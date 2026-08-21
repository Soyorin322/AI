# Speaker Attribution Guidelines

This document defines shared data-preparation principles for attributing dialogue speakers in character source material stored under `character_data/`.

It is intended for novels, subtitles, scripts, transcripts, and other narrative sources where the speaker is not explicitly labeled for every utterance.

The purpose of speaker attribution is to prepare reliable source material for later evidence extraction and character reconstruction. Speaker labels are therefore part of source preprocessing, not part of the character model itself.

---

## 1. Core principle

Speaker attribution must be performed at the level of the **current narrative scene / narrative unit**, not as isolated sentence-by-sentence guessing.

A quote should be attributed only after considering:

1. explicit narrative attribution;
2. active participants in the current scene;
3. dialogue-turn structure;
4. addressee and interaction structure;
5. nearby pronouns and character mentions;
6. local linguistic cues;
7. character speaking style only as a weak tie-breaker.

The preferred decision order is:

```text
explicit narrative attribution
        ↓
scene participant constraints
        ↓
dialogue turn / response structure
        ↓
addressee relation
        ↓
coreference / local linguistic cues
        ↓
character style as weak evidence
```

Character style must never be used as the sole reason to assign a quote to a character.

---

## 2. Scene-first attribution

Before assigning speakers, identify the current narrative scene or narrative unit.

A scene should track at minimum:

```yaml
scene_id: ...
participants:
  - character_a
  - character_b
location: ...
time_context: ...
body_state: ...
```

Speaker candidates should normally be restricted to characters who are actually present or otherwise able to speak in that scene.

When the scene changes, speaker state must be reset.

Do not let a speaker assumption from the previous scene leak into the next scene.

---

## 3. Explicit narrative attribution has highest priority

Narration such as the following should override dialogue-pattern guesses:

```text
「住口！」堯明怒斥。
```

Result:

```text
堯明: 「住口！」
```

Other strong cues include:

- `X說`
- `X回答`
- `X喊道`
- `X呢喃`
- `X問道`
- `X打斷`
- `X笑著說`
- equivalent grammatical constructions in the source language

If a nearby narration explicitly identifies the speaker, do not override it merely because a dialogue alternation pattern suggests another character.

---

## 4. Distinguish narration from dialogue

A major observed failure mode is assigning speaker labels to narration.

Only text that is actually direct speech, transmitted speech, quoted internal speech, or another explicitly defined speech type should receive a speaker label.

Narrative prose must remain unlabeled.

Incorrect:

```text
冬雪: 雛女們，只有在白天才會在雛宮研習……
```

Correct:

```text
雛女們，只有在白天才會在雛宮研習……
```

Do not inherit a speaker label merely because narration follows that character's dialogue.

---

## 5. Use dialogue-turn structure, but do not propagate blindly

In a stable two-person exchange, turn alternation can be strong evidence:

```text
A: ...
B: ...
A: ...
B: ...
```

However, turn alternation is only valid while the participant set remains stable and narration does not introduce another speaker.

The system must not assume:

```text
previous speaker = A
therefore next speaker = B
```

without checking the scene.

A single wrong assignment must not be allowed to determine the rest of the conversation.

---

## 6. Reset after uncertainty

Do not propagate an uncertain speaker into subsequent lines.

If one utterance cannot be confidently identified:

```text
【speaker 不確定】: 「……」
```

or, when useful:

```text
【speaker 不確定（朱家女官）】: 「……」
```

The next utterance must be evaluated again from scene evidence rather than assuming the unknown quote consumed one turn in an alternating pattern.

Precision is more important than forcing complete coverage.

---

## 7. Candidate restriction

Before using an LLM or heuristic scoring, construct a reasonable candidate set.

Example:

```yaml
participants:
  - Reirin
  - Keigetsu
  - Tousetsu

speaker_candidates:
  - Reirin
  - Keigetsu
  - Tousetsu
```

Do not ask a model to freely choose from every named character in the book when only three characters are present.

Possible candidate evidence includes:

- physically present characters;
- remote communication participants;
- characters identified in a flashback;
- narratively introduced off-screen voices;
- quoted remembered speech where explicitly signaled.

---

## 8. Coreference and local mentions

Pronouns and descriptive references should be resolved when possible.

Example:

```text
「住口！」他怒斥。
```

If `他` clearly refers to 堯明:

```text
堯明: 「住口！」
```

Speaker attribution should conceptually separate:

```text
quote
  ↓
local speaker mention
  ↓
character identity
```

This is safer than mapping every quote directly to a global character identity.

---

## 9. Body-swap and identity-state tracking

When a story contains body swaps, possession, disguise, avatars, remote projections, or similar identity complications, **speaker identity and surface/body identity must be tracked separately**.

For *Though I Am an Inept Villainess*, only Reirin and Keigetsu exchange bodies.

Preferred rendered labels during the exchange:

```text
玲琳（身體：朱慧月）: 「……」
慧月（身體：黃玲琳）: 「……」
```

Before the exchange or in a flashback before the exchange:

```text
玲琳: 「……」
慧月: 「……」
```

The semantic representation should preserve both identity and body state separately when structured data is available:

```yaml
speaker: Reirin
body: Keigetsu
```

Do not infer speaker from visible body identity alone.

---

## 10. Flashbacks and temporal state

Speaker state must follow the time represented by the scene, not the chronological position of the chapter.

If a later chapter contains a flashback to a time before a body swap, the speaker label should reflect the earlier state.

Example:

```text
玲琳: 「……」
```

not:

```text
玲琳（身體：朱慧月）: 「……」
```

Temporal transitions must therefore trigger a re-evaluation of identity state.

---

## 11. Speaking style is weak evidence only

A character's vocabulary, politeness level, sentence endings, rhetorical style, emotional tendencies, or habitual phrases may be used to break a tie between already plausible candidates.

They must not be used as primary evidence.

Unsafe loop:

```text
assume this sounds like Reirin
        ↓
label it Reirin
        ↓
use the quote to strengthen Reirin's style model
        ↓
future quotes appear even more Reirin-like
```

This creates circular evidence contamination.

Character style evidence must never validate itself.

---

## 12. Confidence and abstention

Speaker attribution should support uncertainty explicitly.

Suggested levels:

```text
high
- explicit narration identifies the speaker
- unambiguous coreference
- uniquely constrained scene context

medium
- strong dialogue-turn and participant evidence
- no conflicting narrative cue

low
- multiple candidates remain plausible
- attribution depends mainly on style or weak context
```

When confidence is low, prefer abstention over an unsupported label.

Example structured form:

```yaml
speaker: unknown
candidates:
  - character_a
  - character_b
confidence: low
```

---

## 13. Store attribution evidence when practical

For derived structured datasets, preserve why a speaker was assigned.

Example:

```yaml
utterance_id: vol01_ch03_0042
speaker: Reirin
body: Keigetsu
confidence: high
attribution:
  methods:
    - explicit_narrative_cue
    - scene_participant_constraint
  evidence:
    - "玲琳開口道"
```

This allows later correction of the speaker layer without rebuilding the entire character database.

---

## 14. Separate raw source from attributed source

Never overwrite the original raw source simply to add speakers.

Recommended conceptual separation:

```text
raw source
    ↓
speaker-attributed / curated source
    ↓
verified source units
    ↓
evidence extraction
    ↓
character reconstruction
```

The original source should remain available for comparison and reprocessing.

Speaker attribution is a derived annotation layer.

---

## 15. Failure mode observed during Reirin Volume 1 processing

The first automatic pass of Volume 1 revealed a recurring failure pattern:

```text
one speaker is assigned incorrectly
        ↓
next line is inferred by dialogue alternation
        ↓
incorrect conversation state is propagated
        ↓
large sections receive systematically wrong speakers
```

A second pass that reconstructed each scene's participant set before assigning dialogue produced substantially more reliable results.

The practical lesson is:

> The main failure was not simply lack of character knowledge. It was uncontrolled propagation of an incorrect conversation state.

Therefore:

- reset at scene boundaries;
- reconstruct participants before attribution;
- do not inherit uncertain state;
- re-check narration after every dialogue turn;
- do not treat conversation alternation as a global rule.

---

## 16. Recommended processing workflow

```text
Raw source
   ↓
Quote detection
   ↓
Narrative-unit / scene segmentation
   ↓
Participant detection
   ↓
Character mention + coreference resolution
   ↓
Explicit attribution rules
   ↓
Dialogue-turn reasoning
   ↓
Constrained LLM attribution when needed
   ↓
Confidence / abstention
   ↓
Human review for uncertain or high-impact cases
   ↓
Verified speaker-attributed source
```

The LLM should preferably choose among constrained candidates rather than freely generate a character name.

---

## 17. Evaluation principle

Do not evaluate a new attribution method only by subjective impression.

Maintain a manually corrected subset as a gold corpus.

Suggested categories:

- explicit attribution;
- implicit attribution;
- pronoun/coreference attribution;
- two-person dialogue;
- multi-party dialogue;
- body-swap dialogue;
- flashback dialogue;
- internal thought;
- remote / magical transmitted speech;
- anonymous group speech.

For each new method, compare against the same gold subset and record accuracy/error categories.

Human-corrected material must remain distinguishable from automatically generated labels.

---

## 18. Relationship to Evidence-Grounded Reconstruction

Speaker attribution occurs **before** evidence extraction.

An incorrect speaker can contaminate:

- personality evidence;
- beliefs and values;
- relationship evidence;
- emotional behavior;
- dialogue style;
- memory reconstruction;
- event interpretation.

Therefore speaker labels should never silently enter high-confidence character evidence unless the attribution itself is sufficiently reliable.

Conceptually:

```text
source text
  ↓
speaker attribution
  ↓
verified source unit
  ↓
evidence
  ↓
claim
  ↓
character model
```

Speaker attribution is part of evidence preparation, not evidence generation.

---

## 19. Current status

These principles are based partly on general speaker-attribution methodology and partly on concrete failure analysis from the first-volume Reirin annotation experiment.

They should be treated as shared data-processing guidance for `character_data/` and refined as more manually verified corpora become available.
