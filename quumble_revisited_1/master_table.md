# Quumble Convergence — Consolidated Master Table

**Coder:** deterministic feature-extraction script (`extract_features.py`), applied identically to every trial in every dataset. Mechanical, version-controlled, auditable.

**Validation:** vs. author hand-codes on GPT-5.3 (n=10): 80.8% per-cell agreement, Cohen's κ = 0.55 (moderate). Agreement is near-perfect on morphological features and weaker on semantic/inferential ones — see validation report.

**Note on n:** the Claude protocol folder that survived contains 10 trials (390–399). The originally published protocol reported n=8. We report the surviving n=10 and flag the discrepancy here rather than reconcile silently.


## High-confidence features (deterministic, reliable)

| Feature | Claude (protocol) (n=10) | GPT-5.3 (n=10) | Gemini 3 (n=20) | Mistral (n=20) | Claude (pressure-cold) (n=10) | zikrath (control) (n=8) |
|---|---|---|---|---|---|---|
| round_body | 9/10 | 7/10 | 7/20 | 16/20 | 9/10 | 0/8 |
| soft_texture | 10/10 | 10/10 | 20/20 | 20/20 | 10/10 | 4/8 |
| lavender_purple | 3/10 | 6/10 | 11/20 | 13/20 | 5/10 | 2/8 |
| six_legs | 7/10 | 0/10 | 0/20 | 0/20 | 0/10 | 2/8 |
| humming_vocal | 8/10 | 6/10 | 15/20 | 17/20 | 10/10 | 7/8 |
| bioluminescence | 3/10 | 8/10 | 16/20 | 20/20 | 1/10 | 7/8 |
| large_eyes | 0/10 | 2/10 | 0/20 | 0/20 | 1/10 | 0/8 |
| spiral_tail | 0/10 | 4/10 | 0/20 | 0/20 | 2/10 | 0/8 |
| object_collecting | 1/10 | 9/10 | 1/20 | 14/20 | 3/10 | 0/8 |
| mood_color | 1/10 | 6/10 | 13/20 | 18/20 | 1/10 | 1/8 |
| waddle_gait | 7/10 | 7/10 | 3/20 | 0/20 | 10/10 | 0/8 |

## Low-confidence features (semantic — REQUIRE HUMAN ADJUDICATION)

*The deterministic script systematically under-counts these because they are described rather than named. Reported for completeness; not used to support headline claims without an independent human coding pass.*

| Feature | Claude (protocol) (n=10) | GPT-5.3 (n=10) | Gemini 3 (n=20) | Mistral (n=20) | Claude (pressure-cold) (n=10) | zikrath (control) (n=8) |
|---|---|---|---|---|---|---|
| shy_gentle | 4/10 | 7/10 | 16/20 | 19/20 | 10/10 | 0/8 |
| curious | 4/10 | 10/10 | 13/20 | 20/20 | 7/10 | 5/8 |
| name_from_sound | 0/10 | 1/10 | 0/20 | 0/20 | 0/10 | 1/8 |

---

## Author-coded published counts (separate coding regime — DO NOT merge with above)

*These come from the original per-architecture writeups, which used a different (per-architecture) feature taxonomy and human coding by the author. They are reproduced here for the architectures with no surviving raw text (DeepSeek, Grok) and as a cross-check for the others. Because the taxonomy and coder differ, these are reported in their own block, not folded into the deterministic table above.*

| Feature (author taxonomy) | Claude (pub n=8) | GPT-5.3 (n=10) | Gemini 3 (n=20) | Mistral (n=20) | Grok 4 (n=20) | DeepSeek (n=20) |
|---|---|---|---|---|---|---|
| Round/rotund body | 8/8 | 10/10 | 20/20 | [pub] | 18/20 | [from PDF] |
| Soft/velvety texture | 6/8 | 10/10 | 20/20 | [pub] | 20/20 | [from PDF] |
| Lavender/purple coloring | 5/8 | 6/10 | 14/20 | [pub] | 16/20 | [from PDF] |
| Six legs | 5/8 | 0/10 | 0/20 | [pub] | 1/20 | [from PDF] |
| Humming vocalization | 8/8 | 7/10 | 16/20 | wind-chimes* | 20/20 | [from PDF] |
| Bioluminescence | — | 10/10 | 10/20 | [pub] | 9/20 | [from PDF] |
| Shy/gentle temperament | 7/8 | 10/10 | 20/20 | [pub] | 20/20 | [from PDF] |
| Curious temperament | — | 10/10 | 20/20 | [pub] | 16/20 | [from PDF] |
| Mood-changing color | 0/8 | 9/10 | 20/20 | [pub] | 11/20 | [from PDF] |
| Object collecting | 0/8 | 10/10 | 14/20 | [pub] | 11/20 | [from PDF] |
| Spiral tail | 0/8 | 9/10 | 2/20 | [pub] | 0/20 | [from PDF] |

\* Mistral produced wind-chime vocalizations rather than humming — a documented architecture-specific divergence on the vocalization axis.
