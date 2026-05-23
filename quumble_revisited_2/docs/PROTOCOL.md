# Operational Protocol — Quumble Revisited, Pass 2

This describes exactly how each trial is collected, so the run is reproducible by
anyone with API access. The machine-readable version is `harness/protocol.py`;
this file is the prose companion.

## One trial = one independent call

Each trial is a single HTTP request to the vendor's chat endpoint:
- exactly **one user message** (the prompt), no system prompt, no prior turns,
- `temperature` set to the trial's level (1.0 or 0.0),
- `max_tokens = 600`,
- the model string for that trial.

No state is shared between trials. The runner never sends a model its own or any
other model's prior output. This makes the multi-turn contamination that affected
pass 1 structurally impossible.

## Prompts (exact)

- **W1:** `Imagine a {word}. It is an imaginary creature. Describe it.`
- **W2:** `please describe a {word}. it is an imaginary creature.`

`{word}` ∈ {quumble, glummble, zikrath, spinkletta}. Target (quumble) is run under
both wordings; controls under W1 only. Whitespace and capitalization are part of
the stimulus and must not be altered.

## Models (verified May 2026)

| key | vendor | tier | temperature settable |
|---|---|---|---|
| `claude-sonnet-4-6` | anthropic | mid | yes |
| `claude-haiku-4-5-20251001` | anthropic | small | yes |
| `gpt-5.4-mini` | openai | mid | yes |
| `gpt-5.4-nano` | openai | small | yes |

Re-verify these strings on each vendor's docs before a live run; vendors deprecate
strings (pass 1 was bitten by exactly this). The flagship `gpt-5.5` and Anthropic
`opus-4.7` are intentionally excluded: opus-4.7 removes the temperature parameter
(adaptive thinking only), which would break the temperature factor, and adding an
unpaired flagship would confound the clean vendor×size 2×2.

## Sampling counts (asymmetric)

| word kind | t=1.0 | t=0.0 |
|---|---|---|
| target (per wording × model) | 100 | 30 |
| control (per model, W1) | 50 | 30 |

t=1 carries the convergence-spread question, so it gets the larger N. t=0 is
near-deterministic, so a small N suffices to capture the modal creature and detect
any mode flips. **Total 2,000 trials, 500 per model.**

## Output

One JSON file per trial in `data/raw/`, named by `trial_id`
(`{word}__{wording}__{model}__{t1|t0}__r{NNN}.json`), recording: the pass-1-style
`condition`/`model`/`conversation`/`quumble_response` surface plus full provenance
(protocol version, all factor levels, timestamp, temperature, max_tokens,
response id, token usage, and the raw provider JSON). A `manifest.json` records the
locked protocol and per-invocation counts.

## Failures

A failed call writes a record with `status: "error"` and the error message; it does
**not** halt the run. Re-running re-attempts only missing trials (a failed trial
has a file, so it is *not* auto-retried — delete its JSON to retry it).

## Cost

~450 output tokens/trial × 2,000 trials on small/mid tiers, 600-token cap.
Typically well under USD $15 total. Confirm current per-token pricing on your
dashboards before running; `run_collection.py --estimate` prints the plan size.
