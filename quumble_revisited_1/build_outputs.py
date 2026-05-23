#!/usr/bin/env python3
"""Generate all consolidation deliverables as local files in ./outputs_consol/"""
import csv, json, re, glob, os, random
from collections import OrderedDict, defaultdict
from extract_features import code_text, FEATURES, DATASETS

OUT = "/mnt/user-data/outputs/quumble_consolidation"
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(OUT, exist_ok=True)

# ============================================================
# 1. Run deterministic extractor, collect per-trial + counts
# ============================================================
all_rows = []
counts = OrderedDict()
trial_texts = []  # (dataset, trial, text) for blinded worksheet
for dsname, loader in DATASETS.items():
    trials = loader()
    n = len(trials)
    fc = defaultdict(int)
    for tid, text in trials:
        row, _ = code_text(text)
        for f, v in row.items():
            fc[f] += v
        all_rows.append(dict(dataset=dsname, trial=tid, **row))
        trial_texts.append((dsname, tid, text))
    counts[dsname] = (n, dict(fc))

# ---- 1a. per-trial feature matrix CSV ----
with open(f"{OUT}/feature_matrix_deterministic.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["dataset", "trial"] + list(FEATURES.keys()))
    for r in all_rows:
        w.writerow([r["dataset"], r["trial"]] + [r[f] for f in FEATURES])

# ============================================================
# 2. Consolidated master table (markdown) — deterministic spine
# ============================================================
HIGH = [f for f, s in FEATURES.items() if s["conf"] == "high"]
LOW = [f for f, s in FEATURES.items() if s["conf"] == "low"]
order = list(counts.keys())

def cell(ds, f):
    n, fc = counts[ds]
    return f"{fc.get(f,0)}/{n}"

md = []
md.append("# Quumble Convergence — Consolidated Master Table\n")
md.append("**Coder:** deterministic feature-extraction script (`extract_features.py`), applied "
          "identically to every trial in every dataset. Mechanical, version-controlled, auditable.\n")
md.append("**Validation:** vs. author hand-codes on GPT-5.3 (n=10): 80.8% per-cell agreement, "
          "Cohen's κ = 0.55 (moderate). Agreement is near-perfect on morphological features and "
          "weaker on semantic/inferential ones — see validation report.\n")
md.append("**Note on n:** the Claude protocol folder that survived contains 10 trials (390–399). "
          "The originally published protocol reported n=8. We report the surviving n=10 and flag the "
          "discrepancy here rather than reconcile silently.\n")

# High-confidence table
md.append("\n## High-confidence features (deterministic, reliable)\n")
md.append("| Feature | " + " | ".join(f"{ds} (n={counts[ds][0]})" for ds in order) + " |")
md.append("|" + "---|" * (len(order) + 1))
for f in HIGH:
    md.append(f"| {f} | " + " | ".join(cell(ds, f) for ds in order) + " |")

# Low-confidence table
md.append("\n## Low-confidence features (semantic — REQUIRE HUMAN ADJUDICATION)\n")
md.append("*The deterministic script systematically under-counts these because they are described "
          "rather than named. Reported for completeness; not used to support headline claims without "
          "an independent human coding pass.*\n")
md.append("| Feature | " + " | ".join(f"{ds} (n={counts[ds][0]})" for ds in order) + " |")
md.append("|" + "---|" * (len(order) + 1))
for f in LOW:
    md.append(f"| {f} | " + " | ".join(cell(ds, f) for ds in order) + " |")

# Author-coded published columns (DIFFERENT taxonomy — kept separate, NOT merged)
md.append("\n---\n\n## Author-coded published counts (separate coding regime — DO NOT merge with above)\n")
md.append("*These come from the original per-architecture writeups, which used a different (per-architecture) "
          "feature taxonomy and human coding by the author. They are reproduced here for the architectures "
          "with no surviving raw text (DeepSeek, Grok) and as a cross-check for the others. Because the "
          "taxonomy and coder differ, these are reported in their own block, not folded into the deterministic "
          "table above.*\n")
md.append("| Feature (author taxonomy) | Claude (pub n=8) | GPT-5.3 (n=10) | Gemini 3 (n=20) | Mistral (n=20) | Grok 4 (n=20) | DeepSeek (n=20) |")
md.append("|---|---|---|---|---|---|---|")
# Hand-entered from the PDFs/xlsx the user supplied. DeepSeek cells left as [from PDF] where not legible in extract.
author = [
    ("Round/rotund body",          "8/8", "10/10", "20/20", "[pub]", "18/20", "[from PDF]"),
    ("Soft/velvety texture",       "6/8", "10/10", "20/20", "[pub]", "20/20", "[from PDF]"),
    ("Lavender/purple coloring",   "5/8", "6/10",  "14/20", "[pub]", "16/20", "[from PDF]"),
    ("Six legs",                   "5/8", "0/10",  "0/20",  "[pub]", "1/20",  "[from PDF]"),
    ("Humming vocalization",       "8/8", "7/10",  "16/20", "wind-chimes*", "20/20", "[from PDF]"),
    ("Bioluminescence",            "—",   "10/10", "10/20", "[pub]", "9/20",  "[from PDF]"),
    ("Shy/gentle temperament",     "7/8", "10/10", "20/20", "[pub]", "20/20", "[from PDF]"),
    ("Curious temperament",        "—",   "10/10", "20/20", "[pub]", "16/20", "[from PDF]"),
    ("Mood-changing color",        "0/8", "9/10",  "20/20", "[pub]", "11/20", "[from PDF]"),
    ("Object collecting",          "0/8", "10/10", "14/20", "[pub]", "11/20", "[from PDF]"),
    ("Spiral tail",                "0/8", "9/10",  "2/20",  "[pub]", "0/20",  "[from PDF]"),
]
for row in author:
    md.append("| " + " | ".join(row) + " |")
md.append("\n\\* Mistral produced wind-chime vocalizations rather than humming — a documented "
          "architecture-specific divergence on the vocalization axis.\n")

with open(f"{OUT}/master_table.md", "w") as fh:
    fh.write("\n".join(md))

# ============================================================
# 3. Validation report (markdown)
# ============================================================
import openpyxl
wb = openpyxl.load_workbook("convergenceprotocol/quumble_gpt_analysis.xlsx", data_only=True)
ws = wb["Feature Coding"]
hand = {}
for r in ws.iter_rows(min_row=5, values_only=True):
    if not r or not r[0]:
        continue
    hand[r[0].strip()] = [(1 if str(c).strip().upper() == "Y" else 0) for c in r[3:13]]
MAP = {
    'round_body':'Round/rotund body','soft_texture':'Soft/velvety/moss-like texture',
    'lavender_purple':'Lavender/purple coloring','six_legs':'Six legs',
    'humming_vocal':'Humming/quum-quum vocalization','bioluminescence':'Bioluminescence/glowing',
    'spiral_tail':'Spiral/curled tail','object_collecting':'Collects shiny objects',
    'mood_color':'Mood-changing fur color','shy_gentle':'Shy/gentle/friendly temperament',
    'curious':'Curious temperament','name_from_sound':'Name derived from sound it makes',
}
files = sorted(glob.glob("convergenceprotocol/quumblegpt*copypasteversion.txt"),
               key=lambda x: int(re.search(r"gpt(\d+)", x).group(1)))
auto = {k: [] for k in MAP}
for f in files:
    row, _ = code_text(open(f, encoding="utf-8", errors="replace").read())
    for k in MAP:
        auto[k].append(row[k])

vr = ["# Validation Report: deterministic script vs. author hand-codes\n",
      "**Dataset:** GPT-5.3 quumble replication, n=10 (the only set with surviving per-trial author hand-codes).\n",
      "**Method:** the deterministic extractor was run blind on the same 10 verbatim responses the author "
      "hand-coded in `quumble_gpt_analysis.xlsx`. Per-feature and pooled agreement computed below.\n",
      "\n| Feature | Confidence | Author | Script | Cells agree |",
      "|---|---|---|---|---|"]
both = []
agree = tot = 0
for k, hk in MAP.items():
    h, a = hand[hk], auto[k]
    ag = sum(1 for x, y in zip(h, a) if x == y)
    agree += ag; tot += 10; both += list(zip(h, a))
    vr.append(f"| {k} | {FEATURES[k]['conf']} | {sum(h)}/10 | {sum(a)}/10 | {ag}/10 |")
n = len(both); po = sum(1 for x, y in both if x == y) / n
ph = sum(x for x, y in both); pa = sum(y for x, y in both)
pe = (ph/n)*(pa/n) + ((n-ph)/n)*((n-pa)/n)
kappa = (po - pe) / (1 - pe)
vr.append(f"\n**Overall per-cell agreement:** {agree}/{tot} = {agree/tot:.1%}")
vr.append(f"\n**Pooled Cohen's κ:** {kappa:.3f} (moderate)")
vr.append("\n**Reading:** agreement is near-perfect on morphological/appearance features "
          "(soft_texture, lavender, six_legs, object_collecting) — the features carrying the core "
          "cross-architecture claim. Disagreement concentrates in inferential features the script "
          "cannot safely judge (spiral_tail paraphrases, name_from_sound, mood_color). This is the "
          "expected and honest profile: the core findings are robust to coder identity; the semantic "
          "features need a human pass. It is reported as a limitation, not hidden.\n")
with open(f"{OUT}/validation_report.md", "w") as fh:
    fh.write("\n".join(vr))

# ============================================================
# 4. Blinded human-coding worksheet (CSV) — shuffled, identity-stripped
# ============================================================
random.seed(42)
blind = trial_texts[:]
random.shuffle(blind)
keymap = []  # answer key: blind_id -> (dataset, original trial)
with open(f"{OUT}/blinded_coding_worksheet.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["blind_id", "response_text"] + [f for f in FEATURES])
    for i, (ds, tid, text) in enumerate(blind, 1):
        bid = f"B{i:03d}"
        keymap.append((bid, ds, tid))
        clean = re.sub(r"\s+", " ", text).strip()[:4000]
        w.writerow([bid, clean] + ["" for _ in FEATURES])
with open(f"{OUT}/blinded_coding_KEY.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["blind_id", "dataset", "original_trial"])
    for row in keymap:
        w.writerow(row)

print("Wrote files to", OUT)
for f in sorted(os.listdir(OUT)):
    print("  ", f, os.path.getsize(os.path.join(OUT, f)), "bytes")
