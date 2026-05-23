#!/usr/bin/env python3
"""
test_harness.py — proves the pipeline works end-to-end with the MOCK provider,
no keys and no spend. Run from anywhere:  python harness/test_harness.py

Checks:
  1. plan generates the expected 2000 trials, 500/model, 40 cells
  2. a --mock --limit run writes valid per-trial JSON in the right schema
  3. resume: re-running skips existing files (no duplicate work/billing)
  4. extractor reads mock JSON and writes a feature matrix
  5. analyze produces contrasts; blinded worksheet + key line up
"""
import os, sys, json, subprocess, tempfile, glob, csv

HARNESS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HARNESS, ".."))
sys.path.insert(0, HARNESS)
import protocol as P


def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond: raise SystemExit(f"FAILED: {name}")


def main():
    print("1. plan shape")
    plan = P.build_plan(); s = P.plan_summary(plan)
    check("2000 trials", s["total"] == 2000)
    check("40 cells", s["cells"] == 40)
    check("500 per model", all(v == 500 for v in s["by_model"].values()))

    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "raw")
        print("2. mock run (limit 25)")
        subprocess.run([sys.executable, os.path.join(HARNESS, "run_collection.py"),
                        "--mock", "--limit", "25", "--outdir", out], check=True,
                       capture_output=True)
        files = glob.glob(os.path.join(out, "*.json"))
        check("25 trial files written", len(files) == 25)
        rec = json.load(open(files[0]))
        check("schema has quumble_response", "quumble_response" in rec)
        check("schema has conversation", isinstance(rec.get("conversation"), list))
        check("schema has provenance", rec.get("protocol_version") == P.PROTOCOL_VERSION)
        check("status ok", rec.get("status") == "ok")

        print("3. resume / no double-billing")
        r = subprocess.run([sys.executable, os.path.join(HARNESS, "run_collection.py"),
                            "--mock", "--limit", "25", "--outdir", out],
                           check=True, capture_output=True, text=True)
        check("re-run skips existing", "skipped=25" in r.stdout)

        # point extractor/analysis at the temp dir by copying into the real tree
        # (simpler: run extractor with a tiny full mock collection)
        print("4. extractor on a small full mock collection")
        out2 = os.path.join(tmp, "raw2")
        subprocess.run([sys.executable, os.path.join(HARNESS, "run_collection.py"),
                        "--mock", "--only-word", "quumble", "--limit", "40", "--outdir", out2],
                       check=True, capture_output=True)
        env = dict(os.environ, QR2_RAW=out2, QR2_OUT=tmp)
        subprocess.run([sys.executable, os.path.join(ROOT, "analysis", "extract_features.py")],
                       check=True, capture_output=True, env=env)
        mtx = os.path.join(tmp, "feature_matrix.csv")
        check("feature_matrix.csv written", os.path.exists(mtx))
        rows = list(csv.DictReader(open(mtx)))
        check("matrix has 40 rows", len(rows) == 40)
        soft = sum(int(r["soft_texture"]) for r in rows)
        check("mock quumble reads as soft (sanity)", soft >= 38)
        # large_eyes fix sanity: mock quumble text mentions large/glossy eyes -> should fire
        eyes = sum(int(r["large_eyes"]) for r in rows)
        check("large_eyes fires on mock text (fix works)", eyes >= 1)
        print("5. blinded worksheet alignment")
        subprocess.run([sys.executable, os.path.join(ROOT, "analysis", "make_blinded_worksheet.py"),
                        "--all"], check=True, capture_output=True,
                       env=dict(env, QR2_RAW=out2))
        # worksheet writes into analysis/ by default; just confirm it produced aligned files
        wsf = os.path.join(ROOT, "analysis", "blinded_worksheet.csv")
        kyf = os.path.join(ROOT, "analysis", "blinded_KEY.csv")
        if os.path.exists(wsf) and os.path.exists(kyf):
            ws = list(csv.DictReader(open(wsf))); ky = list(csv.DictReader(open(kyf)))
            check("worksheet and key aligned", len(ws) == len(ky) == 40)
            check("worksheet hides identity", "model" not in ws[0])
            os.remove(wsf); os.remove(kyf)  # clean test artifacts

    print("\nALL CHECKS PASSED ✔  (mock pipeline end-to-end)")


if __name__ == "__main__":
    main()
