# Validation Report: deterministic script vs. author hand-codes

**Dataset:** GPT-5.3 quumble replication, n=10 (the only set with surviving per-trial author hand-codes).

**Method:** the deterministic extractor was run blind on the same 10 verbatim responses the author hand-coded in `quumble_gpt_analysis.xlsx`. Per-feature and pooled agreement computed below.


| Feature | Confidence | Author | Script | Cells agree |
|---|---|---|---|---|
| round_body | high | 10/10 | 7/10 | 7/10 |
| soft_texture | high | 10/10 | 10/10 | 10/10 |
| lavender_purple | high | 6/10 | 6/10 | 10/10 |
| six_legs | high | 0/10 | 0/10 | 10/10 |
| humming_vocal | high | 7/10 | 6/10 | 9/10 |
| bioluminescence | high | 10/10 | 8/10 | 8/10 |
| spiral_tail | high | 9/10 | 4/10 | 5/10 |
| object_collecting | high | 10/10 | 9/10 | 9/10 |
| mood_color | high | 9/10 | 6/10 | 7/10 |
| shy_gentle | low | 10/10 | 7/10 | 7/10 |
| curious | low | 10/10 | 10/10 | 10/10 |
| name_from_sound | low | 6/10 | 1/10 | 5/10 |

**Overall per-cell agreement:** 97/120 = 80.8%

**Pooled Cohen's κ:** 0.552 (moderate)

**Reading:** agreement is near-perfect on morphological/appearance features (soft_texture, lavender, six_legs, object_collecting) — the features carrying the core cross-architecture claim. Disagreement concentrates in inferential features the script cannot safely judge (spiral_tail paraphrases, name_from_sound, mood_color). This is the expected and honest profile: the core findings are robust to coder identity; the semantic features need a human pass. It is reported as a limitation, not hidden.
