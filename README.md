# Quumble_Revisited

A consolidation of early quumble-related nonsense into more cohesive, honest nonsense.

This repository chases one small, stubborn question:

> Given a novel nonsense word (e.g. *quumble*) and asked to describe an imaginary
> creature, do independent, memory-less language-model instances **converge** on the
> same description — and if they do, is that convergence best explained by **phonetic
> priming** (soft-sounding words get soft creatures), by **shared training
> distribution**, or by something more interesting (a stable cross-model "concept")?

The original work was scattered across ~8 deposits and coded informally, often by a
model in the same family as the subjects. This repo is the attempt to redo it
*properly* — controlled, preregistered, blind-codeable, and reproducible by someone
who isn't us.

## Layout

| Folder | What it is |
|---|---|
| [`quumble_revisited_1/`](quumble_revisited_1/) | **Consolidation pass.** Pulls the fragmented original datasets into one auditable table with a deterministic feature extractor and a blinded human-coding instrument. Methodological cleanup of existing data — no new collection. |
| [`quumble_revisited_2/`](quumble_revisited_2/) | **Clean re-run.** A from-scratch, preregistered experiment with a stateless single-turn harness, phonetic-control words, a vendor×size model grid, and temperature/wording robustness checks. This is the part designed to actually answer the question. |

Start with [`quumble_revisited_2/README.md`](quumble_revisited_2/README.md) — it's the
current, self-contained experiment. Pass 1 is useful context for how the question and
the coding methodology evolved.

## Why pass 2 exists

Pass 1's honest limitation was that its numbers leaned on author/in-family hand-coding
and on data captured inconsistently (API vs. copy-paste, mixed model versions). Pass 2
was built to remove the contamination at the source rather than patch it in analysis:

- **Stateless & single-turn** — every trial is an independent cold call, so no instance
  ever sees another's answer. This structurally eliminates the within-session
  contamination that made the original convergence claims unfalsifiable.
- **Controls, not just the target** — alongside *quumble* it collects a near-phonetic
  neighbour (*glummble*) and phonetically distant words. Convergence only means
  something relative to these.
- **A 2×2 of vendor × size** — separates "all models agree" from "models of similar
  size agree" from "one family has a quirk."
- **Temperature and wording variants** — checks whether any apparent creature survives
  going to the modal (t=0) response and a reworded prompt.
- **Reproducible end-to-end** — preregistration, protocol, and codebook are committed;
  the harness resumes safely; raw data is regenerable from code + API keys.

## What it found (short version)

A controlled, mostly-deflationary result — which is the honest kind:

- **The soft-creature effect is real and robust.** Soft-sounding nonsense words reliably
  elicit soft/round creature descriptions across both vendors and both sizes, stable to
  temperature and wording. Clean replication of sound-symbolism in LLMs.
- **It is not *quumble*-specific.** The near-phonetic control (*glummble*) converges just
  as hard on the predictable features — often harder. That directly undercuts the
  original "quumble names a particular thing" framing: the driver is the phonetics, not
  the word.
- **No evidence for a shared latent creature.** Beyond the phonetic vibe, the specific
  ("arbitrary") features fragment by model cell rather than agreeing across them — the
  signature of family-specific training associations, not a navigable shared concept.
- **One small residual.** A few features (humming, bioluminescence) separate *quumble*
  from *glummble* in a way pure phonetics doesn't obviously predict. Worth a future
  probe; not, on this data, evidence of anything grand.

Full numbers and the contrast tables are in
[`quumble_revisited_2/analysis/contrasts.md`](quumble_revisited_2/analysis/contrasts.md).

## Read before citing any number

- **The blinded human-coding pass gates the interesting claims.** The most
  interpretation-heavy features (temperament, "collects objects", mood-colour) are coded
  by regex in the committed outputs and are exactly where a script mis-codes. The
  *quumble*-vs-*glummble* divergence rides on these. Run the blinded pass
  (`make_blinded_worksheet.py` → code → `agreement.py`) before treating those contrasts
  as load-bearing.
- **A response-length confound is present, not hypothetical.** Output was capped at a
  fixed token budget and longer responses mention more features; the t=0 rises in pass 2
  partly track description length, not a "truer" creature. Interpret per-feature rates
  with that in mind.
- **Model strings are unpinned aliases**, current as of May 2026. The run date is the
  provenance anchor; vendors deprecate strings, so re-verify before re-running.
- **Raw per-trial data is not committed** — only the derived feature matrix and
  contrasts. A fresh clone collects its own corpus (see the pass-2 Quickstart).

## Reproducing

Each folder has its own instructions. For the live experiment, see
[`quumble_revisited_2/README.md`](quumble_revisited_2/README.md#quickstart) — it needs
an Anthropic and an OpenAI API key and costs roughly the price of a sandwich to run the
full 2000-trial corpus.

## License

See [`LICENSE`](LICENSE).
