#!/usr/bin/env python3
"""
run_collection.py — execute the locked plan from protocol.py.

Key properties (these are the methodological point):
  * STATELESS  : each trial is one independent single-turn call. No history,
                 no system prompt. Contamination across trials is impossible.
  * RESUME-SAFE: a trial whose output JSON already exists is skipped, so you can
                 stop/restart or recover from a crash without double-billing.
  * AUDITABLE  : every output file records the exact prompt, model, temperature,
                 protocol version, timestamp, raw provider response, usage, and
                 the full trial spec. Nothing about the run is hidden.
  * SCHEMA     : compatible with pass-1 pressure-cold JSON (condition/model/
                 conversation fields present) so the existing extractor flows in.

Usage:
  python run_collection.py --mock                 # offline dry run, no keys/spend
  python run_collection.py --mock --limit 20      # just the first 20 trials
  python run_collection.py                        # LIVE (needs env keys)
  python run_collection.py --only-word quumble    # filter
  python run_collection.py --only-model gpt-5.4-nano
  python run_collection.py --estimate             # print plan + rough cost, do nothing

Environment for live runs:
  export ANTHROPIC_API_KEY=...
  export OPENAI_API_KEY=...
"""
import os, sys, json, time, argparse, datetime, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import protocol as P
from providers import get_provider, ProviderError

DEFAULT_OUTDIR = os.path.normpath(os.path.join(HERE, "..", "data", "raw"))


def iso_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def trial_path(outdir, spec):
    return os.path.join(outdir, spec["trial_id"] + ".json")


def record_for(spec, result, status, error=None):
    """Build the on-disk record. Mirrors pass-1 pressure-cold schema where it
    makes sense (condition/model/conversation) and adds full provenance."""
    return {
        # --- pass-1-compatible surface ---
        "condition": f'{spec["word_kind"]}_{("cold" if spec["temperature"]==0.0 else "warm")}',
        "model": spec["model"],
        "timestamp": iso_now(),
        "conversation": [
            {"role": "user", "content": spec["prompt"]},
            {"role": "assistant", "content": result["text"] if result else ""},
        ],
        # the field pass-1's extractor reads as the response text:
        "quumble_response": result["text"] if result else "",
        # --- qr2 full provenance ---
        "trial_id": spec["trial_id"],
        "protocol_version": spec["protocol_version"],
        "word": spec["word"],
        "word_kind": spec["word_kind"],
        "phon": spec["phon"],
        "wording": spec["wording"],
        "prompt": spec["prompt"],
        "vendor": spec["vendor"],
        "tier": spec["tier"],
        "temperature": spec["temperature"],
        "rep": spec["rep"],
        "max_tokens": P.MAX_TOKENS,
        "status": status,                          # "ok" | "error"
        "error": error,
        "response_id": result["response_id"] if result else None,
        "usage": result["usage"] if result else None,
        "provider_raw": result["raw"] if result else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true", help="use offline fake provider (no keys, no spend)")
    ap.add_argument("--outdir", default=DEFAULT_OUTDIR)
    ap.add_argument("--limit", type=int, default=None, help="run at most N (post-filter) trials")
    ap.add_argument("--only-word", default=None)
    ap.add_argument("--only-model", default=None)
    ap.add_argument("--estimate", action="store_true", help="print plan + cost estimate and exit")
    args = ap.parse_args()

    plan = P.build_plan()
    if args.only_word:
        plan = [p for p in plan if p["word"] == args.only_word]
    if args.only_model:
        plan = [p for p in plan if p["model"] == args.only_model]

    if args.estimate:
        s = P.plan_summary(P.build_plan())
        print(json.dumps(s, indent=2))
        # crude cost estimate: ~25 input + 450 output tokens/trial, blended ~ $3/M out
        out_tok = len(P.build_plan()) * 450
        print(f"\n~{out_tok:,} output tokens across all trials")
        print("Rough spend (small/mid tiers, 600-tok cap): typically well under $15.")
        print("Confirm exact pricing on your provider dashboards before a live run.")
        return

    os.makedirs(args.outdir, exist_ok=True)
    done = ran = failed = skipped = 0
    started = iso_now()

    for spec in plan:
        if args.limit is not None and ran >= args.limit:
            break
        path = trial_path(args.outdir, spec)
        if os.path.exists(path):
            skipped += 1
            continue
        provider = get_provider(spec["vendor"], mock=args.mock)
        try:
            result = provider(spec["model"], spec["prompt"], spec["temperature"], P.MAX_TOKENS)
            rec = record_for(spec, result, "ok")
            ran += 1; done += 1
        except ProviderError as e:
            rec = record_for(spec, None, "error", error=str(e))
            ran += 1; failed += 1
        except Exception as e:  # never let one trial kill the run
            rec = record_for(spec, None, "error", error=f"{type(e).__name__}: {e}\n{traceback.format_exc()[:400]}")
            ran += 1; failed += 1
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=2)
        if P.SLEEP_BETWEEN_CALLS_S:
            time.sleep(P.SLEEP_BETWEEN_CALLS_S)
        if ran % 50 == 0:
            print(f"  ... {ran} run ({done} ok, {failed} err), {skipped} pre-existing skipped")

    # write/refresh manifest
    manifest = {
        "protocol_version": P.PROTOCOL_VERSION,
        "run_started_utc": started,
        "run_finished_utc": iso_now(),
        "mock": args.mock,
        "planned_total": len(P.build_plan()),
        "this_invocation": dict(ran=ran, ok=done, errors=failed, skipped_preexisting=skipped),
        "words": P.WORDS,
        "wordings": P.WORDINGS,
        "models": P.MODELS,
        "temperatures": P.TEMPERATURES,
        "n_plan": {f"{k[0]}@t{k[1]}": v for k, v in P.N_PLAN.items()},
        "max_tokens": P.MAX_TOKENS,
    }
    with open(os.path.join(args.outdir, "..", "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)

    print(f"\nDONE. ran={ran} ok={done} errors={failed} skipped={skipped}")
    print(f"output dir: {args.outdir}")
    print("manifest:   ../manifest.json")
    if args.mock:
        print("\n(MOCK run — fabricated text, no API calls were made.)")


if __name__ == "__main__":
    main()
