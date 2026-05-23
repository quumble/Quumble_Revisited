#!/usr/bin/env python3
"""
protocol.py — LOCKED study definition for Quumble Revisited, Pass 2.

This file is the single source of truth. Every constant that defines the
experiment lives here so the design is auditable in one place and cannot
drift between the runner, the extractor, and the writeup.

DO NOT edit these values mid-collection. If you must change anything, bump
PROTOCOL_VERSION and start a new data directory — never silently mix.

Design (pre-registered; see docs/PREREGISTRATION.md):
  Factors
    - word        : quumble (target) + 3 controls on a phonetic gradient
    - wording     : two prompt phrasings (target only; controls use W1)
    - model       : 2x2 vendor x size  (Anthropic Sonnet/Haiku, OpenAI mini/nano)
    - temperature : 1.0 and 0.0  (asymmetric N — see N_PLAN)
  Each trial is an INDEPENDENT, STATELESS, single-user-turn API call.
  No system prompt. No conversation history. Contamination is structurally
  impossible because no state crosses calls.
"""

PROTOCOL_VERSION = "qr2-1.0.0"

# ---- Stimulus words --------------------------------------------------------
# kind: 'target' | 'control'
# phon: phonetic relationship to "quumble" — the variable H0 (phonetic priming)
#       predicts should matter. 'self' for the target.
WORDS = {
    "quumble":    dict(kind="target",  phon="self",
                       note="Target token."),
    "glummble":   dict(kind="control", phon="near",
                       note="Near neighbor: shares the -umble hum-coda + rounded vowel; "
                            "harder gl- onset. Tests whether the rime drives convergence."),
    "zikrath":    dict(kind="control", phon="distant",
                       note="Distant: hard consonants, sharp vowels. REUSED from pass 1 — "
                            "NOT blind (outputs previously seen). Labeled as a known-divergent anchor."),
    "spinkletta": dict(kind="control", phon="distant",
                       note="Distant, different flavor: light -ink-, diminutive -etta ending. "
                            "Distinct failure mode from zikrath."),
}

# ---- Prompt wordings (EXACT strings — do not alter whitespace) -------------
WORDINGS = {
    "W1": "Imagine a {word}. It is an imaginary creature. Describe it.",
    "W2": "please describe a {word}. it is an imaginary creature.",
}
# Which wordings each word kind receives.
TARGET_WORDINGS  = ["W1", "W2"]   # target gets both (within-study wording variable)
CONTROL_WORDINGS = ["W1"]         # controls get primary wording only

# ---- Models (2x2 vendor x size). Verified current as of May 2026. ----------
# vendor x tier lets us separate "architecture" from "model size".
MODELS = {
    "claude-sonnet-4-6":          dict(vendor="anthropic", tier="mid",   supports_temperature=True),
    "claude-haiku-4-5":           dict(vendor="anthropic", tier="small", supports_temperature=True),
    "gpt-5.4-mini":               dict(vendor="openai",    tier="mid",   supports_temperature=True),
    "gpt-5.4-nano":               dict(vendor="openai",    tier="small", supports_temperature=True),
}

# ---- Temperatures + asymmetric N -------------------------------------------
# t=1.0 : spread is the point -> larger N.
# t=0.0 : near-deterministic mode -> small N (catches the peak + any flips;
#         NOTE: t=0 is "near-deterministic", NOT bit-identical on these APIs,
#         so a few trials still capture real—if narrow—variation).
TEMPERATURES = [1.0, 0.0]
N_PLAN = {
    ("target",  1.0): 100,
    ("target",  0.0): 30,
    ("control", 1.0): 50,
    ("control", 0.0): 30,
}

MAX_TOKENS = 600
SLEEP_BETWEEN_CALLS_S = 0.0   # set >0 if you hit rate limits

# ---- Trial plan generator --------------------------------------------------
def build_plan():
    """Return the full ordered list of trial specs. Deterministic given this file.

    Each spec is a dict with a stable `trial_id` so the runner can resume by
    skipping ids that already have an output file. trial_id encodes every factor
    so two specs can never collide and provenance is readable from the filename.
    """
    plan = []
    for word, wmeta in WORDS.items():
        kind = wmeta["kind"]
        wordings = TARGET_WORDINGS if kind == "target" else CONTROL_WORDINGS
        for wording in wordings:
            for model in MODELS:
                for temp in TEMPERATURES:
                    n = N_PLAN[(kind, temp)]
                    tlabel = f"t{int(temp) if temp in (0,1) else temp}"  # t1 / t0
                    for rep in range(1, n + 1):
                        trial_id = f"{word}__{wording}__{model}__{tlabel}__r{rep:03d}"
                        plan.append(dict(
                            trial_id=trial_id,
                            protocol_version=PROTOCOL_VERSION,
                            word=word, word_kind=kind, phon=wmeta["phon"],
                            wording=wording,
                            prompt=WORDINGS[wording].format(word=word),
                            model=model,
                            vendor=MODELS[model]["vendor"],
                            tier=MODELS[model]["tier"],
                            temperature=temp,
                            rep=rep,
                        ))
    return plan


def plan_summary(plan):
    from collections import Counter
    by_cell = Counter((p["word"], p["wording"], p["model"], p["temperature"]) for p in plan)
    by_model = Counter(p["model"] for p in plan)
    return dict(total=len(plan), cells=len(by_cell), by_model=dict(by_model))


if __name__ == "__main__":
    import json
    plan = build_plan()
    s = plan_summary(plan)
    print(f"PROTOCOL_VERSION = {PROTOCOL_VERSION}")
    print(f"total trials     = {s['total']}")
    print(f"distinct cells   = {s['cells']}")
    print("per-model totals :")
    for m, c in s["by_model"].items():
        print(f"  {m:32s} {c}")
    print("\nfirst 3 trial specs:")
    for p in plan[:3]:
        print(" ", json.dumps({k: p[k] for k in ('trial_id','prompt','temperature')}))
