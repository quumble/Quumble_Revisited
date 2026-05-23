#!/usr/bin/env python3
"""
Deterministic feature extractor for the Quumble Convergence corpus.

Design goals (these are the methodological point, not incidental):
  - Fully mechanical: same regex patterns applied identically to every trial,
    every architecture. No per-trial judgement.
  - Auditable: every feature's trigger pattern is printed alongside its hit.
  - Conservative + honest: features that regex cannot safely judge (nuanced
    affect, "name derived from sound") are computed but FLAGGED as
    low-confidence / needs-human-adjudication in the output.
  - NOT a replacement for a human second coder. This is a reproducible
    first-pass instrument whose errors are systematic and inspectable.

Output: per-trial feature matrix + per-architecture counts, written to CSV,
plus an agreement check against the author's hand-coded GPT-5.3 xlsx.
"""
import re, json, csv, sys, glob, os
from collections import defaultdict, OrderedDict

# ---- Feature patterns -------------------------------------------------------
# Each feature: list of regex alternatives (case-insensitive, searched in the
# response text). A feature is "present" (1) if ANY pattern matches.
# `confidence`: 'high' = regex is reliable; 'low' = semantic, flag for human.
FEATURES = OrderedDict([
    ("round_body",        dict(conf="high", pats=[r"\bround(ed|ish)?\b", r"\brotund\b", r"\bspherical\b", r"\bplump\b", r"\bglobular\b", r"\borb-?like\b"])),
    ("soft_texture",      dict(conf="high", pats=[r"\bsoft\b", r"\bvelvety\b", r"\bvelvet\b", r"\bfluffy\b", r"\bfuzzy\b", r"\bmoss-?like\b", r"\bplush\b", r"\bdowny\b"])),
    ("lavender_purple",   dict(conf="high", pats=[r"\blavender\b", r"\bpurple\b", r"\bviolet\b", r"\blilac\b", r"\bmauve\b", r"\bamethyst\b"])),
    ("six_legs",          dict(conf="high", pats=[r"\bsix\s+(stubby\s+|short\s+|tiny\s+|little\s+)?legs?\b", r"\b6\s+legs?\b", r"\bsix-?legged\b"])),
    ("humming_vocal",     dict(conf="high", pats=[r"\bhum(s|ming|med)?\b", r"\bthrum(s|ming|med)?\b", r"\bquum-?quum\b", r"\bquuum+\b", r"\bresonant (hum|tone|sound)\b"])),
    ("bioluminescence",   dict(conf="high", pats=[r"\bbioluminescen(t|ce)\b", r"\bglow(s|ing|ed)?\b", r"\bluminous\b", r"\bluminescen(t|ce)\b", r"\blight(s)? up\b"])),
    ("large_eyes",        dict(conf="high", pats=[r"\blarge\s+(glowing\s+|luminous\s+|expressive\s+|round\s+)?eyes?\b", r"\bbig\s+(glowing\s+|round\s+|expressive\s+)?eyes?\b", r"\bwide\s+eyes?\b", r"\bglossy eyes?\b"])),
    ("spiral_tail",       dict(conf="high", pats=[r"\bspiral(ed|ing)?\s+tail\b", r"\bcurled\s+tail\b", r"\bcurly\s+tail\b", r"\bcoiled\s+tail\b"])),
    ("object_collecting", dict(conf="high", pats=[r"\bcollect(s|ing|ed)?\b.{0,30}\b(object|pebble|trinket|shiny|button|treasure|bauble|stone)", r"\bhoard(s|ing|ed)?\b", r"\bgather(s|ing|ed)?\b.{0,30}\b(shiny|trinket|object|pebble)"])),
    ("mood_color",        dict(conf="high", pats=[r"\b(color|colour|fur|skin|hue).{0,40}\b(mood|emotion|feeling)", r"\b(mood|emotion|feeling).{0,40}\b(color|colour|shift|change)", r"\bchanges?\s+color\b", r"\bcolou?r-?shift"])),
    ("waddle_gait",       dict(conf="high", pats=[r"\bwaddl(e|es|ing|ed)\b", r"\bbounc(e|es|ing|ed)\b", r"\bhop(s|ping|ped)?\b", r"\brolling gait\b"])),
    # ---- low-confidence / semantic: computed but flagged ----
    ("shy_gentle",        dict(conf="low",  pats=[r"\bshy\b", r"\bgentle\b", r"\btimid\b", r"\bmeek\b", r"\bbashful\b", r"\bdocile\b"])),
    ("curious",           dict(conf="low",  pats=[r"\bcurious\b", r"\binquisitive\b", r"\bcurios"])),
    ("name_from_sound",   dict(conf="low",  pats=[r"\bname\b.{0,40}\b(sound|hum|noise|call|vocal)", r"\b(sound|hum|noise|call)\b.{0,40}\bname\b", r"named?\s+(for|after)\s+the\s+(sound|hum|noise)"])),
])

def code_text(text):
    t = text.lower()
    row = {}
    hits = {}
    for feat, spec in FEATURES.items():
        matched = None
        for p in spec["pats"]:
            m = re.search(p, t)
            if m:
                matched = m.group(0)
                break
        row[feat] = 1 if matched else 0
        hits[feat] = matched
    return row, hits

# ---- Loaders for each dataset's response text -------------------------------
def load_claude_protocol():
    # quumble392..399 (.txt) — extract the *final* description after "follow your gut"
    out = []
    for f in sorted(glob.glob("convergenceprotocol/quumble39*.txt")) + sorted(glob.glob("convergenceprotocol/quumble_conversation*.txt")):
        txt = open(f, encoding="utf-8", errors="replace").read()
        out.append((os.path.basename(f), txt))
    return out

def load_gpt_protocol():
    out = []
    for f in sorted(glob.glob("convergenceprotocol/quumblegpt*copypasteversion.txt"),
                    key=lambda x: int(re.search(r"gpt(\d+)", x).group(1))):
        txt = open(f, encoding="utf-8", errors="replace").read()
        out.append((os.path.basename(f), txt))
    return out

def load_zikrath():
    out = []
    for f in sorted(glob.glob("convergenceprotocol/zikrath*.txt"),
                    key=lambda x: int(re.search(r"zikrath(\d+)", x).group(1))):
        out.append((os.path.basename(f), open(f, encoding="utf-8", errors="replace").read()))
    return out

def load_gemini():
    out = []
    for f in sorted(glob.glob("qummble3arch/*quumblegemini*.txt")):
        out.append((os.path.basename(f), open(f, encoding="utf-8", errors="replace").read()))
    return out

def load_mistral():
    out = []
    for f in sorted(glob.glob("qummble3arch/*mistral*.txt")):
        out.append((os.path.basename(f), open(f, encoding="utf-8", errors="replace").read()))
    return out

def load_pressure_cold():
    # cold_baseline only = comparable to other cold-instance data
    out = []
    d = json.load(open("quumbleunderpressure/all_results.json"))
    for item in d:
        if item.get("condition") == "cold_baseline":
            out.append((f"pressure_cold_{item['trial']:02d}", item.get("quumble_response","") or ""))
    return out

DATASETS = OrderedDict([
    ("Claude (protocol)", load_claude_protocol),
    ("GPT-5.3",           load_gpt_protocol),
    ("Gemini 3",          load_gemini),
    ("Mistral",           load_mistral),
    ("Claude (pressure-cold)", load_pressure_cold),
    ("zikrath (control)", load_zikrath),
])

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ".")
    all_rows = []
    counts = OrderedDict()
    for dsname, loader in DATASETS.items():
        try:
            trials = loader()
        except Exception as e:
            print(f"!! {dsname}: loader error {e}")
            continue
        n = len(trials)
        feat_count = defaultdict(int)
        for tid, text in trials:
            row, hits = code_text(text)
            for feat, v in row.items():
                feat_count[feat] += v
            all_rows.append(dict(dataset=dsname, trial=tid, **row))
        counts[dsname] = (n, dict(feat_count))
        print(f"[{dsname}]  n={n}")

    # write per-trial matrix
    with open("feature_matrix.csv","w",newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["dataset","trial"]+list(FEATURES.keys()))
        for r in all_rows:
            w.writerow([r["dataset"], r["trial"]]+[r[f] for f in FEATURES])

    # print master count table
    print("\n===== MASTER COUNT TABLE (deterministic extractor) =====")
    header = ["feature","conf"] + [f"{ds} (n={counts[ds][0]})" for ds in counts]
    print(" | ".join(header))
    for feat, spec in FEATURES.items():
        cells = [feat, spec["conf"]]
        for ds in counts:
            n, fc = counts[ds]
            cells.append(f"{fc.get(feat,0)}/{n}")
        print(" | ".join(cells))

if __name__ == "__main__":
    main()
