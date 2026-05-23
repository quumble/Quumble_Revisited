#!/usr/bin/env python3
"""
agreement.py — inter-rater reliability between a human coding pass and the
deterministic extractor, computed on the blinded subset.

Inputs:
  analysis/human_codes.csv     blind_id + 14 feature 0/1 cols (from the coding tool)
  analysis/blinded_KEY.csv     blind_id -> trial_id
  analysis/feature_matrix.csv  the deterministic script's per-trial codes

Outputs to stdout: per-feature agreement + Cohen's kappa, pooled, and split by
high/low confidence. This is the number that licenses (or doesn't) treating the
deterministic counts as trustworthy without a human in the loop.
"""
import os, csv
HERE = os.path.dirname(os.path.abspath(__file__))
FEATS = ["round_body","soft_texture","lavender_purple","six_legs","humming_vocal",
         "bioluminescence","large_eyes","spiral_tail","object_collecting","mood_color",
         "waddle_gait","shy_gentle","curious","name_from_sound"]
LOW = {"shy_gentle","curious","name_from_sound"}


def kappa(pairs):
    n = len(pairs)
    if n == 0: return None, None
    agree = sum(1 for a, b in pairs if a == b) / n
    a1 = sum(a for a, _ in pairs)/n; b1 = sum(b for _, b in pairs)/n
    pe = a1*b1 + (1-a1)*(1-b1)
    return agree, (1.0 if pe == 1 else (agree - pe)/(1 - pe))


def main():
    hp = os.path.join(HERE, "human_codes.csv")
    if not os.path.exists(hp):
        print("No analysis/human_codes.csv yet. Code the blinded worksheet first "
              "(e.g. with the coding bench HTML tool), export here, then re-run.")
        return
    human = {r["blind_id"]: r for r in csv.DictReader(open(hp))}
    key = {r["blind_id"]: r["trial_id"] for r in csv.DictReader(open(os.path.join(HERE, "blinded_KEY.csv")))}
    det = {r["trial_id"]: r for r in csv.DictReader(open(os.path.join(HERE, "feature_matrix.csv")))}

    pairs_all, by_feat = [], {f: [] for f in FEATS}
    for bid, hrow in human.items():
        tid = key.get(bid); drow = det.get(tid)
        if not drow: continue
        for f in FEATS:
            pair = (int(hrow[f]), int(drow[f]))
            pairs_all.append(pair); by_feat[f].append(pair)

    a, k = kappa(pairs_all)
    print(f"WHOLE-SUBSET human-vs-script: cells={len(pairs_all)}  agreement={a*100:.1f}%  kappa={k:.3f}")
    hi = [p for f in FEATS if f not in LOW for p in by_feat[f]]
    lo = [p for f in LOW for p in by_feat[f]]
    if hi: ah, kh = kappa(hi); print(f"  high-conf: agreement={ah*100:.1f}%  kappa={kh:.3f}  (n={len(hi)})")
    if lo: al, kl = kappa(lo); print(f"  low-conf : agreement={al*100:.1f}%  kappa={kl:.3f}  (n={len(lo)})")
    print(f"\n{'feature':18}{'agree%':>8}{'kappa':>8}{'human':>7}{'script':>7}")
    for f in FEATS:
        fr = by_feat[f]
        if not fr: continue
        af, kf = kappa(fr)
        ht = sum(h for h, _ in fr); st = sum(s for _, s in fr)
        print(f"{f:18}{af*100:7.1f}{kf:8.2f}{ht:7d}{st:7d}{'  *LOW' if f in LOW else ''}")


if __name__ == "__main__":
    main()
