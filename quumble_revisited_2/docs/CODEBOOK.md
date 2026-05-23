# Human-style semantic codebook (independent second coder)

Coding unit: one model response describing the creature. Code 1 if the feature is
present IN MEANING, regardless of exact wording; 0 otherwise. Coder does not see
model identity or the deterministic script's output while coding.

- round_body: body described as round/rotund/spherical/plump/ball-like/squat-round.
  Cantaloupe/orb/sphere similes count. "Squat" alone does not unless paired w/ round.
- soft_texture: fur/skin/body soft, velvety, fluffy, plush, downy, moss-like, fuzzy.
- lavender_purple: any purple-family color named as a body/fur color (lavender,
  purple, violet, lilac, mauve, amethyst, indigo IF describing the quumble's own body).
- six_legs: explicitly six legs / six-legged / 6 legs. Four legs = 0.
- humming_vocal: vocalization described as a hum/thrum/"quum"/resonant low sound/
  vibration-you-feel. Wind-chime/whistle-only without hum = judge: whistle alone=0,
  but "hum + whistle" =1. Purring that is explicitly a deep hum-like vibration =1.
- bioluminescence: any part of the creature glows / is luminescent / lights up.
- large_eyes: eyes explicitly large/big/enormous/oversized/huge (relative emphasis).
- spiral_tail: tail described as spiral/curled/coiled/curly. A spiraling HORN is not a tail.
- object_collecting: creature collects/hoards/gathers small objects/trinkets/shiny things.
- mood_color: body/fur color changes WITH mood/emotion/feeling (the mechanism, not just
  that it happens to be purple). "shifts ... depending on its mood" =1.
- waddle_gait: moves by waddling/rolling/wobbling/bouncing/hopping gait.
- shy_gentle: temperament shy/timid/gentle/meek/bashful/skittish/docile/harmless-and-retiring.
- curious: temperament curious/inquisitive.
- name_from_sound: text explicitly says the NAME derives from the sound it makes
  ("which is how it got its name", "hence the name", "gives the creature its name").

---
## Note for pass 2

`large_eyes` definition is unchanged in MEANING, but the deterministic extractor's
regex was FIXED for pass 2: pass 1 required the size word adjacent to "eyes" and so
missed "large, luminous eyes" / "two enormous amber eyes that take up...". A human
coder should code large_eyes as PRESENT whenever the eyes are described as
large/big/enormous/oversized/wide/huge, regardless of intervening words.
