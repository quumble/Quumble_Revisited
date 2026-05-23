#!/usr/bin/env python3
"""
make_blinded_worksheet.py — build the independent human-coding instrument.

Takes the collected qr2 trials, shuffles them, strips model/word identity, and
writes:
  analysis/blinded_worksheet.csv  blind_id, response_text, <empty feature cols>
  analysis/blinded_KEY.csv        blind_id -> trial_id (HELD OUT; do not consult
                                  while coding)

A human (or a second model coder) fills the feature columns from the worksheet
alone, then agreement.py joins on the key and computes human-vs-script kappa —
the inter-rater reliability step that pass 1 was missing at corpus scale.

By default it samples a manageable subset (default 120) so a human can actually
finish; pass --all to blind the entire corpus. Seed is fixed for reproducibility.
"""
import os, csv, json, glob, random, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.environ.get("QR2_RAW") or os.path.normpath(os.path.join(HERE, "..", "data", "raw"))
FEATS = ["round_body","soft_texture","lavender_purple","six_legs","humming_vocal",
         "bioluminescence","large_eyes","spiral_tail","object_collecting","mood_color",
         "waddle_gait","shy_gentle","curious","name_from_sound"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=120, help="how many trials to blind (default 120)")
    ap.add_argument("--all", action="store_true", help="blind every OK trial")
    ap.add_argument("--seed", type=int, default=20260523)
    args = ap.parse_args()

    trials = []
    for fp in sorted(glob.glob(os.path.join(RAW, "*.json"))):
        d = json.load(open(fp, encoding="utf-8"))
        if d.get("status") == "ok" and d.get("quumble_response"):
            trials.append(d)
    if not trials:
        print("No OK trials found; run collection first."); return

    rng = random.Random(args.seed)
    rng.shuffle(trials)
    if not args.all:
        trials = trials[:args.n]

    rows = []
    key = []
    for i, d in enumerate(trials, 1):
        bid = f"Q{i:04d}"
        # strip identity: only the raw text goes in the worksheet
        rows.append([bid, d["quumble_response"]] + [""]*len(FEATS))
        key.append([bid, d["trial_id"], d["word"], d["model"], d["wording"], d["temperature"]])

    with open(os.path.join(HERE, "blinded_worksheet.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["blind_id","response_text"]+FEATS); w.writerows(rows)
    with open(os.path.join(HERE, "blinded_KEY.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["blind_id","trial_id","word","model","wording","temperature"]); w.writerows(key)
    print(f"Blinded {len(rows)} trials -> analysis/blinded_worksheet.csv (+ blinded_KEY.csv held out)")


if __name__ == "__main__":
    main()
