# Preregistration — Quumble Revisited, Pass 2

**Protocol version:** `qr2-1.0.0`
**Status:** registered prior to live data collection.
**Note:** this is an informal author preregistration for a small methods study,
not a registry submission. Its purpose is to fix hypotheses and the analysis plan
*before* seeing the data, so the analysis is confirmatory rather than constructed
post hoc.

## Background

Pass 1 found apparent cross-architecture convergence on a "soft, round, humming,
gentle" creature for the token *quumble*, but rested on a partly contaminated,
non-uniformly-captured corpus and author hand-coding. Pass 2 re-collects under one
locked single-turn API protocol to test whether the effect survives clean data.

## Hypotheses

- **H0 — phonetic priming.** The convergent creature is driven by the *sound* of
  the token (soft "qu-" onset, rounded vowel, nasal "-mble" coda). Prediction:
  the near-phonetic control **glummble** (shared "-umble" rime) should converge
  toward the same creature substantially more than the phonetically distant
  controls **zikrath** / **spinkletta**.
- **H1 — latent-space attractor.** The convergence is specific to the learned
  representation of *quumble*, not its phonology. Prediction: even glummble
  diverges from quumble despite the shared rime; quumble's feature profile is
  distinctly tighter than all controls.
- **H2 — navigable conceptual structure.** Convergence reflects shared structure
  across models that is robust to surface perturbation. Prediction: quumble's
  profile is stable across wording (W1≈W2) and across temperature (t1≈t0), and
  is shared across both vendors and both size tiers.

These are not mutually exclusive; the contrasts are designed to apportion
evidence among them.

## Primary outcome

Per-trial binary presence of 11 high-confidence morphological/appearance
features (see `docs/CODEBOOK.md`), coded by the deterministic extractor. Three
semantic features are coded but treated as secondary pending the human pass.

Convergence for a (word × model × wording × temperature) cell on a feature =
proportion of trials in which the feature is present, reported with a 95% Wilson
score interval.

## Confirmatory contrasts (fixed in `analysis/analyze.py`)

- **C1 Target vs controls** (t=1, W1, pooled models): quumble vs each control,
  per high-confidence feature.
- **C2 Phonetic gradient:** glummble (near) vs zikrath/spinkletta (distant).
  H0 predicts glummble ≫ distant; H1 predicts glummble ≈ distant ≪ quumble.
- **C3 Temperature:** quumble t=1 vs t=0. H2 predicts ≈; a large drop at t=0
  would indicate the t=1 convergence is a sampling-breadth effect.
- **C4 Vendor × size 2×2** (quumble, W1, t=1): main effects of vendor and tier.
  Convergence that holds across all four cells supports cross-architecture H1/H2;
  convergence that tracks tier (mid vs small) regardless of vendor indicates a
  capability/size effect, not architecture.
- **C5 Wording robustness:** quumble W1 vs W2 (t=1). H2 predicts ≈.

## Analysis decisions fixed in advance

- **Inclusion:** only trials with `status == "ok"` and non-empty response text are
  analyzed. Errored trials are reported as a count, not imputed.
- **Coding instrument:** the deterministic extractor is primary for the 11
  high-confidence features. The 3 semantic features require a blinded human pass;
  human-vs-script Cohen's κ is reported (`agreement.py`). High-confidence headline
  claims are not adjusted by the human pass; semantic claims are gated on it.
- **No optional stopping:** the full plan (2,000 trials) is collected before
  confirmatory analysis. Resume-safety is for crash recovery, not peeking.
- **Multiplicity:** with 11 features × several contrasts this is exploratory in the
  statistical sense; CIs are reported rather than a single corrected p-value, and
  effects are read as patterns across features, not single-cell significance.

## Controls and blinding

- **glummble, spinkletta:** freshly coined, checked for non-existence, never
  previously shown to the models by the author → blind.
- **zikrath:** reused from pass 1, outputs previously observed → **not blind**,
  included only as a known-divergent anchor and labeled as such.
- Human coding is done on a shuffled, identity-stripped worksheet; the key is held
  out (`make_blinded_worksheet.py`).

## Known limitations (stated up front)

- t=0 is *near*-deterministic on these APIs, not bit-identical; the small t=0 N
  samples the peak region but cannot prove strict determinism.
- Free-tier vs API model identity and any provider-side prompt wrapping may differ
  from a bare prompt; we use the documented chat endpoints with no system prompt.
- Two vendors and two size tiers is a small grid; "cross-architecture" claims are
  bounded to these four models.
