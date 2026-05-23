# Quumble Revisited — Consolidation Pass 1 (`quumble_revisited_1`)

This folder consolidates a previously fragmented research line — the Quumble Convergence
work, originally spread across ~8 separate deposits — into a single auditable dataset and
analysis pipeline, as a step toward a peer-reviewable paper.

The scientific question is unchanged from the original work: **given a novel nonsense token
and asked to describe an imaginary creature, do independent cold instances of language models
converge on specific descriptions, and is that convergence better explained by phonetic
priming (H0), latent-space attractors (H1), or navigable conceptual structure (H2)?**

What is new here is *methodological*, not empirical. The original writeups were coded by the
author (or by a model in the same family as the subjects). This pass introduces a
**deterministic, reproducible feature extractor** and a **blinded human-coding instrument** so
that the headline convergence numbers no longer rest on the author's hand-coding alone.

## What's in this folder

| File | What it is |
|---|---|
| `master_table.md` | Consolidated feature-convergence table across six datasets. Three separated blocks: high-confidence deterministic features, low-confidence semantic features (flagged for human adjudication), and the original author-coded published counts (kept separate — different taxonomy/coder, **not** merged). |
| `validation_report.md` | Agreement check between the deterministic script and the author's original GPT-5.3 hand-codes (n=10): 80.8% per-cell agreement, Cohen's κ = 0.55. |
| `feature_matrix_deterministic.csv` | Per-trial, per-feature 0/1 matrix produced by the extractor. Full audit trail. |
| `blinded_coding_worksheet.csv` | All trial responses, shuffled and stripped of model identity, with empty feature columns — the instrument for an independent human coding pass. |
| `blinded_coding_KEY.csv` | Held-out answer key mapping `blind_id` → dataset/trial. Do not consult while coding the worksheet. |
| `extract_features.py` | The deterministic feature extractor. Fixed regex patterns applied identically to every trial. |
| `build_outputs.py` | Regenerates every file above from the raw trial data. |

## Method, briefly

- **Datasets pooled:** Claude protocol (n=10, trials 390–399), GPT-5.3 (n=10), Gemini 3 (n=20),
  Mistral (n=20), Claude pressure-cold (n=10), and the zikrath control word (n=8). Author-coded
  Grok 4 and DeepSeek counts are carried from the original writeups (no raw text survived for them).
- **Coding regimes are kept distinct.** The deterministic script uses one fixed feature taxonomy
  across all architectures. The original per-architecture writeups used per-architecture
  taxonomies and human coding. These are reported in separate blocks and never silently combined.
- **Confidence is marked per feature.** Morphological/appearance features (round body, soft
  texture, lavender, six legs, object-collecting) are reliably regex-codeable. Semantic/inferential
  features (temperament, name-derived-from-sound, mood-color) are systematically under-counted by
  the script and are flagged as requiring human adjudication.

## Known limitations (read before citing any number)

- **The deterministic extractor is literal.** It under-counts paraphrased features. Several cells
  (e.g. Gemini `round_body`, Claude `lavender`) are likely low due to paraphrase misses, not true
  absence. The blinded worksheet exists precisely to resolve these.
- **No full-corpus inter-rater reliability yet.** The κ = 0.55 figure is script-vs-author on one
  architecture (GPT-5.3), not an independent human second-coder pass on the whole corpus. Closing
  that gap is the top priority for the next revision.
- **`n` discrepancy:** the surviving Claude protocol folder has 10 trials; the originally published
  protocol reported 8. We report the surviving n=10 and flag the discrepancy rather than reconcile
  silently.
- **DeepSeek columns are incomplete** pending re-entry from the original DeepSeek writeup.
- **Capture method varies by architecture** (API vs. copy-paste from chat), and free-tier model
  version identifiers may not map exactly to API versions. Documented per dataset.

## Reproducing

```
python3 extract_features.py     # prints the master count table from raw trials
python3 build_outputs.py        # regenerates all files in this folder
```

Both scripts expect the raw trial files in the layout used during this pass (see
`build_outputs.py` loaders for exact paths).

## Status

This is a **consolidation pass, not a finished paper.** It assembles the auditable dataset and
the reproducible pipeline. Still to do: an independent human coding pass via the blinded
worksheet, completion of the DeepSeek column, and the consolidated prose write-up.
