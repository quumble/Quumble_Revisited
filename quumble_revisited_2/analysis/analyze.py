#!/usr/bin/env python3
"""
analyze.py — turn analysis/feature_matrix.csv into convergence summaries.

Outputs (all human-readable CSV/Markdown, nothing hidden):
  analysis/convergence_by_cell.csv   per (word,wording,model,temp,feature): k, n, rate, 95% Wilson CI
  analysis/contrasts.md              the pre-registered comparisons in prose+tables

Pre-registered contrasts (see docs/PREREGISTRATION.md):
  C1 target vs controls   : does quumble converge where distant controls do not?
  C2 phonetic gradient    : near control (glummble) vs distant (zikrath/spinkletta)
  C3 temperature          : t=0 (modal) vs t=1 (sampled) convergence
  C4 vendor x size (2x2)  : is convergence cross-architecture, or size-driven?
  C5 wording robustness   : W1 vs W2 on the target (does framing change the creature?)
"""
import os, csv, math
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
MATRIX = os.path.join(HERE, "feature_matrix.csv")
HIGH = ["round_body","soft_texture","lavender_purple","six_legs","humming_vocal",
        "bioluminescence","large_eyes","spiral_tail","object_collecting","mood_color","waddle_gait"]
LOW = ["shy_gentle","curious","name_from_sound"]
FEATS = HIGH + LOW
META = ["trial_id","word","word_kind","phon","wording","model","vendor","tier","temperature"]


def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (p, max(0.0, c-h), min(1.0, c+h))


def load():
    return list(csv.DictReader(open(MATRIX, encoding="utf-8")))


def rate_block(rows, feats=FEATS):
    """sum k and n per feature over a set of rows."""
    n = len(rows); out = {}
    for f in feats:
        k = sum(int(r[f]) for r in rows)
        out[f] = (k, n) + wilson(k, n)[1:]  # (k,n,lo,hi); rate=k/n
    return n, out


def main():
    rows = load()
    # ---- per-cell convergence CSV ----
    cells = defaultdict(list)
    for r in rows:
        cells[(r["word"], r["wording"], r["model"], r["temperature"])].append(r)
    with open(os.path.join(HERE, "convergence_by_cell.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["word","wording","model","temperature","feature","k","n","rate","ci_lo","ci_hi"])
        for (word,wd,model,temp), rs in sorted(cells.items()):
            n = len(rs)
            for f in FEATS:
                k = sum(int(x[f]) for x in rs)
                p, lo, hi = wilson(k, n)
                w.writerow([word,wd,model,temp,f,k,n,f"{p:.3f}",f"{lo:.3f}",f"{hi:.3f}"])

    def sel(**kw):
        out = rows
        for key, val in kw.items():
            out = [r for r in out if r[key] == str(val)]
        return out

    lines = ["# qr2 Convergence Contrasts\n",
             f"_Generated from {len(rows)} coded trials._\n",
             "Rates are mean feature-presence with 95% Wilson CIs. High-confidence",
             "features only in headline contrasts; semantic (low) features need the",
             "blinded human pass before they support claims.\n"]

    # C1 target vs controls (t=1, W1, pooled across models)
    lines.append("\n## C1 — Target vs controls (t=1, W1, pooled models)\n")
    lines.append("| feature | quumble | glummble (near) | zikrath (distant) | spinkletta (distant) |")
    lines.append("|---|---|---|---|---|")
    grp = {wname: sel(word=wname, wording="W1", temperature=1.0) for wname in
           ("quumble","glummble","zikrath","spinkletta")}
    for f in HIGH:
        cells_txt = []
        for wname in ("quumble","glummble","zikrath","spinkletta"):
            rs = grp[wname]; n=len(rs); k=sum(int(r[f]) for r in rs)
            p,lo,hi = wilson(k,n)
            cells_txt.append(f"{p:.2f} [{lo:.2f}–{hi:.2f}]" if n else "—")
        lines.append(f"| {f} | " + " | ".join(cells_txt) + " |")

    # C3 temperature on target
    lines.append("\n## C3 — Temperature: target quumble, W1, pooled models\n")
    lines.append("| feature | t=1 (sampled) | t=0 (modal) |")
    lines.append("|---|---|---|")
    t1 = sel(word="quumble", wording="W1", temperature=1.0)
    t0 = sel(word="quumble", wording="W1", temperature=0.0)
    for f in HIGH:
        a=wilson(sum(int(r[f]) for r in t1), len(t1))
        b=wilson(sum(int(r[f]) for r in t0), len(t0))
        lines.append(f"| {f} | {a[0]:.2f} [{a[1]:.2f}–{a[2]:.2f}] | {b[0]:.2f} [{b[1]:.2f}–{b[2]:.2f}] |")

    # C4 vendor x size on target
    lines.append("\n## C4 — Vendor × size 2×2: target quumble, W1, t=1\n")
    lines.append("| feature | anthropic·mid | anthropic·small | openai·mid | openai·small |")
    lines.append("|---|---|---|---|---|")
    quad = {(v,t): sel(word="quumble", wording="W1", temperature=1.0, vendor=v, tier=t)
            for v in ("anthropic","openai") for t in ("mid","small")}
    for f in HIGH:
        c=[]
        for v in ("anthropic","openai"):
            for t in ("mid","small"):
                rs=quad[(v,t)]; n=len(rs); k=sum(int(r[f]) for r in rs)
                p,lo,hi=wilson(k,n); c.append(f"{p:.2f}" if n else "—")
        lines.append(f"| {f} | " + " | ".join(c) + " |")

    # C5 wording robustness on target
    lines.append("\n## C5 — Wording robustness: quumble t=1, pooled models\n")
    lines.append("| feature | W1 | W2 |")
    lines.append("|---|---|---|")
    w1=sel(word="quumble", wording="W1", temperature=1.0)
    w2=sel(word="quumble", wording="W2", temperature=1.0)
    for f in HIGH:
        a=wilson(sum(int(r[f]) for r in w1), len(w1))
        b=wilson(sum(int(r[f]) for r in w2), len(w2))
        lines.append(f"| {f} | {a[0]:.2f} [{a[1]:.2f}–{a[2]:.2f}] | {b[0]:.2f} [{b[1]:.2f}–{b[2]:.2f}] |")

    open(os.path.join(HERE, "contrasts.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("Wrote analysis/convergence_by_cell.csv and analysis/contrasts.md")


if __name__ == "__main__":
    main()
