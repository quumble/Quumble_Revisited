# Quumble Revisited — Pass 2 (`quumble_revisited_2`)

A clean, pre-registered, uniform-protocol replication of the Quumble Convergence
study. Where pass 1 (`quumble_revisited_1`) consolidated a fragmented, partly
**contaminated** set of hand-captured transcripts, pass 2 collects a fresh corpus
under a single locked protocol so the headline convergence numbers rest on
auditable, reproducible data.

> **Scientific question (unchanged):** given a novel nonsense token and asked to
> describe an imaginary creature, do independent cold instances of different
> language models converge on specific descriptions — and is that convergence
> better explained by phonetic priming (H0), latent-space attractors (H1), or
> navigable conceptual structure (H2)?

## Why a pass 2 (read this first)

Pass 1's two hand-captured datasets (Claude protocol, zikrath control) were saved
**chat sessions**, not isolated single-turn calls. Auditing found:
- multi-turn contamination (a user-supplied SVG fed back into one session; a
  leading question — "how many legs?" — eliciting "no legs" in another),
- a **protocol asymmetry**: hand-captured sets used different, looser capture than
  the API-collected sets, confounding "architecture" with "collection method,"
- a deterministic-extractor bug (`large_eyes`) that hid a near-universal feature.

Pass 2 fixes all three by construction: every trial is an **independent, stateless,
single-turn API call**, the same way for every model; the extractor bug is fixed;
and the design is pre-registered before collection.

## Design at a glance

| Factor | Levels |
|---|---|
| Word | **quumble** (target) · **glummble** (near-phonetic control) · **zikrath** (distant; *reused from pass 1, NOT blind*) · **spinkletta** (distant) |
| Wording | W1 "Imagine a {w}. It is an imaginary creature. Describe it." · W2 "please describe a {w}. it is an imaginary creature." (target gets both; controls W1 only) |
| Model (2×2 vendor × size) | anthropic: `claude-sonnet-4-6` (mid), `claude-haiku-4-5-20251001` (small) · openai: `gpt-5.4-mini` (mid), `gpt-5.4-nano` (small) |
| Temperature | 1.0 (sampled — larger N) · 0.0 (near-modal — small N) |

**N (asymmetric):** target 100@t1 / 30@t0 per (wording×model); controls 50@t1 /
30@t0 per model. **Total = 2,000 trials**, 500 per model. Model strings verified
current as of May 2026. The full locked spec lives in
[`harness/protocol.py`](harness/protocol.py) — the single source of truth.

## Repo layout

```
quumble_revisited_2/
├── README.md                     ← you are here
├── harness/
│   ├── protocol.py               LOCKED study definition + trial-plan generator
│   ├── providers.py              transparent Anthropic/OpenAI REST clients + MOCK
│   ├── run_collection.py         stateless, resume-safe runner -> per-trial JSON
│   └── test_harness.py           end-to-end mock test (no keys, no spend)
├── analysis/
│   ├── extract_features.py       deterministic coder (large_eyes FIXED vs pass 1)
│   ├── analyze.py                convergence rates + Wilson CIs + 5 contrasts
│   ├── make_blinded_worksheet.py shuffle + strip identity -> human coding instrument
│   └── agreement.py              human-vs-script kappa on the blinded subset
├── data/
│   ├── raw/                      one JSON per trial lands here (gitignored by default)
│   └── manifest.json             auto-written run record
└── docs/
    ├── PREREGISTRATION.md        hypotheses + analysis plan, fixed before collection
    ├── PROTOCOL.md               operational capture protocol
    └── CODEBOOK.md               feature definitions for the human coder
```

## Quickstart

```bash
# 0. inspect the locked plan (no calls)
python harness/protocol.py
python harness/run_collection.py --estimate

# 1. prove the pipeline works offline (no keys, no spend)
python harness/test_harness.py
python harness/run_collection.py --mock --limit 20      # writes fake trials to data/raw/

# 2. LIVE collection (real calls, real spend) — needs keys
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
python harness/run_collection.py                        # resume-safe; re-run to continue

# 3. analyze
python analysis/extract_features.py                     # -> analysis/feature_matrix.csv
python analysis/analyze.py                              # -> convergence_by_cell.csv + contrasts.md

# 4. human coding pass (the inter-rater step pass 1 lacked at scale)
python analysis/make_blinded_worksheet.py               # -> blinded_worksheet.csv + blinded_KEY.csv
#    code blinded_worksheet.csv (e.g. with the coding-bench HTML tool), save as
#    analysis/human_codes.csv, then:
python analysis/agreement.py                            # -> human-vs-script kappa
```

## What pass 2 can answer that pass 1 could not

- **C1 target vs controls** — does quumble converge where distant controls don't?
- **C2 phonetic gradient** — does the *near* control (glummble) converge more than
  the distant ones? This is the direct test of H0 (phonetic priming).
- **C3 temperature** — is convergence present at the *mode* (t=0), not just on
  average (t=1)?
- **C4 vendor × size** — is convergence cross-architecture, or just an artifact of
  model size? (The 2×2 separates them.)
- **C5 wording robustness** — does the creature survive a change in prompt phrasing?

## Status

Harness + analysis are written and **pass an end-to-end mock test**. No live data
collected yet — that requires running `run_collection.py` with your own API keys.
Model strings current as of May 2026; re-verify before a live run, as vendors
deprecate strings (see pass-1 lessons).

## Note on the `zikrath` control

`zikrath` is reused from pass 1, where its outputs were already observed by the
author. It is therefore **not blind** and is included only as a known-divergent
anchor, flagged as such in `protocol.py` and the manifest. `glummble` and
`spinkletta` are freshly coined and were checked for non-existence before use.
