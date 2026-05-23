#!/usr/bin/env python3
"""
extract_features.py — deterministic feature extractor for qr2 data.

Same philosophy as pass 1: fixed regex patterns applied identically to every
trial. CHANGES FROM PASS 1 (documented, deliberate):
  * large_eyes pattern FIXED. Pass 1 required the size word adjacent to "eyes",
    so it missed "large, luminous eyes" / "two enormous amber eyes that..." and
    reported large_eyes as ~absent when it is actually near-universal. The
    second-coder validation (kappa, whole corpus) caught this. Fixed here.
  * Paraphrase handling widened for mood_color, round_body, waddle_gait,
    object_collecting to reduce systematic under-counting found in validation.
  * name_from_sound widened (still 'low' confidence; needs human pass).

Confidence is still marked per feature. 'low' features are semantic and should
be confirmed by the blinded human coder before supporting headline claims.

Reads qr2 per-trial JSON from ../data/raw/, writes feature_matrix.csv to ../analysis/.
"""
import re, os, json, csv, glob, sys
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.environ.get("QR2_RAW") or os.path.normpath(os.path.join(HERE, "..", "data", "raw"))
OUT = os.environ.get("QR2_OUT") or os.path.normpath(os.path.join(HERE, "..", "analysis"))

FEATURES = OrderedDict([
    ("round_body",        dict(conf="high", pats=[r"\bround(ed|ish)?\b", r"\brotund\b", r"\bspherical\b",
        r"\bplump\b", r"\bglobular\b", r"\borb-?like\b", r"\bsphere\b", r"\bcantaloupe\b",
        r"\bball-?(shaped|like)\b"])),
    ("soft_texture",      dict(conf="high", pats=[r"\bsoft\b", r"\bvelvety\b", r"\bvelvet\b", r"\bfluffy\b",
        r"\bfuzzy\b", r"\bmoss-?like\b", r"\bplush\b", r"\bdowny\b", r"\bsilky\b"])),
    ("lavender_purple",   dict(conf="high", pats=[r"\blavender\b", r"\bpurple\b", r"\bviolet\b",
        r"\blilac\b", r"\bmauve\b", r"\bamethyst\b", r"\bindigo\b"])),
    ("six_legs",          dict(conf="high", pats=[r"\bsix\b[^.]{0,20}\blegs?\b", r"\b6\s+legs?\b", r"\bsix-?legged\b"])),
    ("humming_vocal",     dict(conf="high", pats=[r"\bhum(s|ming|med)?\b", r"\bthrum(s|ming|med)?\b",
        r"\bquum-?quum\b", r"\bquuu+m+\b", r"\bresonant\b[^.]{0,15}(hum|tone|sound|purr)",
        r"vibrat\w+[^.]{0,25}(hum|sound|tone)", r"(deep|low|resonant)[^.]{0,20}\bpurr"])),
    ("bioluminescence",   dict(conf="high", pats=[r"\bbioluminescen(t|ce)\b", r"\bglow(s|ing|ed)?\b",
        r"\bluminous\b", r"\bluminescen(t|ce)\b", r"\blight(s)? up\b"])),
    # FIXED: allow intervening adjective(s) between size word and "eyes"
    ("large_eyes",        dict(conf="high", pats=[
        r"\b(large|big|enormous|huge|oversized|wide|giant)\b[^.]{0,25}\beyes?\b",
        r"\beyes?\b[^.]{0,25}\b(take up|third of|dominate)"])),
    ("spiral_tail",       dict(conf="high", pats=[
        r"\b(spiral|curled|curly|coiled|coiling|spiraling|curling)\b[^.]{0,15}\btail\b",
        r"\btail\b[^.]{0,15}\b(spiral|curl|coil)"])),
    ("object_collecting", dict(conf="high", pats=[
        r"\b(collect|hoard|gather|stash|store)\w*\b[^.]{0,40}\b(object|pebble|trinket|shiny|button|treasure|bauble|stone|glass|coin|item)",
        r"\bhoard(s|ing|ed)?\b"])),
    ("mood_color",        dict(conf="high", pats=[
        r"(color|colour|fur|skin|hue|scale|coat)[^.]{0,45}(mood|emotion|feeling)",
        r"(mood|emotion|feeling)[^.]{0,45}(color|colour|shift|change|hue)",
        r"\bchanges?\s+colou?r\b", r"\bcolou?r-?shift",
        r"\bshifts?\b[^.]{0,40}\bdepending on\b[^.]{0,20}\bmood"])),
    ("waddle_gait",       dict(conf="high", pats=[r"\bwaddl(e|es|ing|ed)\b", r"\bbounc(e|es|ing|ed)\b",
        r"\bhop(s|ping|ped)?\b", r"\brolling gait\b", r"\bwobbl(e|es|ing|y)\b[^.]{0,15}(gait|walk|roll|motion)",
        r"\brocking motion\b"])),
    # ---- low-confidence / semantic ----
    ("shy_gentle",        dict(conf="low",  pats=[r"\bshy\b", r"\bgentle\b", r"\btimid\b", r"\bmeek\b",
        r"\bbashful\b", r"\bdocile\b", r"\bskittish\b", r"\bharmless\b"])),
    ("curious",           dict(conf="low",  pats=[r"\bcurious\b", r"\binquisitive\b", r"\bcuriosity\b"])),
    ("name_from_sound",   dict(conf="low",  pats=[
        r"(hence|which is how|that.s how|giving|gives?)\b[^.]{0,30}\b(its |the )?name",
        r"\bname\b[^.]{0,40}\b(sound|hum|noise|call|quum)",
        r"\b(sound|hum|noise|call|quum)\b[^.]{0,40}\bname\b"])),
])


def code_text(text):
    t = (text or "").lower()
    return {f: (1 if any(re.search(p, t) for p in spec["pats"]) else 0)
            for f, spec in FEATURES.items()}


def load_trials(raw_dir):
    out = []
    for fp in sorted(glob.glob(os.path.join(raw_dir, "*.json"))):
        d = json.load(open(fp, encoding="utf-8"))
        if d.get("status") != "ok":
            continue
        out.append(d)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    trials = load_trials(RAW)
    if not trials:
        print(f"No OK trials found in {RAW}. Run the collection (or --mock) first.")
        return
    rows = []
    counts = defaultdict(lambda: defaultdict(int))
    cell_n = defaultdict(int)
    for d in trials:
        feats = code_text(d.get("quumble_response", ""))
        cell = (d["word"], d["wording"], d["model"], d["temperature"])
        cell_n[cell] += 1
        for f, v in feats.items():
            counts[cell][f] += v
        rows.append(dict(trial_id=d["trial_id"], word=d["word"], word_kind=d["word_kind"],
                         phon=d["phon"], wording=d["wording"], model=d["model"],
                         vendor=d["vendor"], tier=d["tier"], temperature=d["temperature"],
                         **feats))
    meta = ["trial_id","word","word_kind","phon","wording","model","vendor","tier","temperature"]
    with open(os.path.join(OUT, "feature_matrix.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(meta + list(FEATURES))
        for r in rows:
            w.writerow([r[m] for m in meta] + [r[f] for f in FEATURES])
    print(f"Coded {len(rows)} OK trials across {len(cell_n)} cells -> analysis/feature_matrix.csv")
    print("Per-cell n (sample):")
    for cell in list(sorted(cell_n))[:6]:
        print(f"  {cell}: n={cell_n[cell]}")


if __name__ == "__main__":
    main()
