# Text Data Processing

`data_processing/text/` is the text-specific preprocessing and story-indexing layer for novels, prose, subtitles, transcripts, webpages converted to text, and other textual source material.

Its current responsibility is intentionally narrow:

```text
1. Ground who is speaking / thinking in the source text.
2. Build Event indexes that always trace back to the original text.
3. Record which parts of an Event each character could actually know.
```

The core boundary is:

> `data_processing/text/` determines **what happened, where it is in the source, and which source content each character could access**.  
> Aiko determines **what those experiences mean for the target character**.

This directory must not perform final personality reconstruction, Memory consolidation, Development analysis, or runtime persona compilation.

---

# Current Official Workflow

The current implementation is deliberately divided into **two stages**.

```text
Raw novel / text source
↓
Stage 1 — Speaker / Thinker Attribution
↓
Human Review
↓
Speaker-grounded source
↓
Stage 2 — Event Indexing
↓
events.json
↓
Aiko Character Reconstruction
```

The previous, more granular design involving mandatory intermediate Observation / Fact artifacts is **not part of the required first implementation**.

Those layers may be introduced later only if a concrete need appears. The current priority is to make four things reliable first:

```text
source grounding
speaker correctness
event indexing
knowledge boundary
```

---

# Stage 1 — Speaker / Thinker Attribution

Stage 1 creates a speaker-grounded derivative of the original source.

Its job is only to determine who is responsible for dialogue or inner thought.

It does NOT create Events, personality conclusions, Memory, Development, or other character interpretation.

## 1. Preserve the original source

Never overwrite the original novel/source file.

Preferred structure:

```text
original source
↓
automatically speaker-attributed derivative
↓
human-reviewed speaker-grounded source
```

The human-reviewed version becomes the preferred input for Stage 2.

## 2. Dialogue must receive speaker attribution

Every actual spoken utterance that can be attributed should be marked with its speaker.

Example:

```text
慧月（身體：黃玲琳）: 「我知道。」
```

If the work contains body swaps, possession, disguise, transformation, aliases, or similar identity changes, preserve the distinction between character identity and body identity.

Example:

```text
慧月（身體：黃玲琳）: 「……」
玲琳（身體：朱慧月）: 「……」
```

Do not infer the actual speaker only from the visible body.

## 3. Inner thoughts in parentheses must also receive attribution

Inner monologue written as `（...）` or equivalent private thought must be attributed to the thinker.

Example, following the established reviewed-volume style:

```text
慧月（身體：黃玲琳）:（我，要死了嗎……？）
```

This is important because private thoughts must later remain inaccessible to other characters unless the source explicitly shows that they were communicated.

A bare inner thought such as:

```text
（我還活著……）
```

should therefore become, when attribution is supported:

```text
慧月（身體：黃玲琳）:（我還活著……）
```

## 4. Narration is not dialogue

Ordinary narration must not be given a speaker label merely because the current scene follows a character.

Example:

```text
慧月默默地抬起手臂，凝視著掌心。
```

This remains narration.

Do not convert it into:

```text
慧月: 慧月默默地抬起手臂，凝視著掌心。
```

## 5. Quoted material is not automatically dialogue

Text inside quotation marks may represent:

- remembered speech;
- quoted documents;
- hypothetical statements;
- phrases mentioned as words;
- imitation / performed voice;
- embedded dialogue.

Do not assign a current-scene speaker solely because quotation marks are present.

## 6. Uncertainty must remain explicit

Do not force a speaker when the source does not support a reliable attribution.

Use a visible unresolved label such as:

```text
【speaker 不確定（候選：A / B）】: 「……」
```

or equivalent.

Human review should resolve these where possible before Stage 2.

## 7. Speaker attribution is derived annotation

The speaker label is not part of the original canonical text unless explicitly present in the source.

Therefore:

```text
original text
≠ speaker annotation
```

Adding labels must not silently rewrite, summarize, translate, reorder, or otherwise alter the underlying novel text.

## 8. Attribution should follow source context, not character stereotypes

Useful evidence includes:

- explicit speech verbs / names;
- dialogue turn-taking;
- nearby narration;
- vocatives / forms of address;
- scene participation;
- first-person self-reference;
- character-specific knowledge;
- body-swap state;
- disguise / performed voice state.

Do not assign speakers based merely on what “sounds like” a character.

## 9. Human review is mandatory before Stage 2

Stage 1 may be produced automatically, but Stage 2 should consume the **human-reviewed** speaker-grounded source whenever available.

The purpose of human review is to prevent attribution errors from propagating into Event participants and character knowledge boundaries.

Potential error chain:

```text
wrong speaker
↓
wrong Event participant
↓
wrong accessible information
↓
wrong character reconstruction
```

---

# Stage 2 — Event Indexing

Stage 2 operates on the human-reviewed speaker-grounded source and creates `events.json`.

Its purpose is not to summarize the novel.

Its purpose is to build a reliable index between:

```text
Character
↔ Event
↔ Exact source text
```

with an explicit knowledge boundary for each character.

The central rule is:

> **Event = index, not replacement text.**

An Event must always be able to return to the complete source passage from which it was identified.

---

# Event Requirements

Each Event should support the following three downstream guarantees.

## Guarantee 1 — Find all Events relevant to a character

The system must be able to query a character and retrieve all Events in which that character:

- actively participates;
- directly observes relevant content;
- directly receives information;
- otherwise has source-supported access to part of the Event.

Do not equate participation with knowledge.

```text
participant
≠ observer
≠ information recipient
≠ complete knower
```

A character may know an Event without being an active participant, and a participant may know only part of an Event.

## Guarantee 2 — Every Event must retrieve the complete original passage

Each Event must preserve a deterministic reference to the full source passage that defines it.

Preferred conceptual form:

```json
{
  "event_id": "V04-E-0017",
  "source_ranges": [
    {
      "file": "惡女不才_第四卷_speaker重校.md",
      "start_span_id": "V04-C02-S0341",
      "end_span_id": "V04-C02-S0389"
    }
  ]
}
```

A future implementation may use stable span IDs, line ranges, byte offsets, or another deterministic locator, but it must satisfy the same invariant:

```text
event_id
↓
source range
↓
complete source passage
```

Do not rely only on:

- an Event summary;
- a chapter name;
- one anchor sentence;
- a paraphrase.

The Event source range should include enough contiguous context to reconstruct the Event without requiring the model to guess missing material.

## Guarantee 3 — Prevent characters from receiving inaccessible information

The complete Event source passage may contain information that not every character could know.

Examples include:

- another character's inner thoughts;
- private conversations;
- actions occurring outside the character's presence;
- narrator-only revelations;
- causes that are hidden while consequences are visible;
- information revealed only at a later time.

Therefore each Event must record which source portions are accessible to which characters.

The preferred rule is:

> Do not summarize “what the character knows” when the source itself can be indexed directly.

Prefer:

```text
character
→ accessible source spans
```

over:

```text
character
→ model-written summary of what they know
```

This keeps character knowledge grounded in original text rather than model interpretation.

---

# Recommended `events.json` Structure

The first implementation should remain minimal.

A conceptual Event record may contain:

```json
{
  "event_id": "V04-E-0017",
  "label": "景彰以聲音模仿協助堯明秘密離開",

  "source_ranges": [
    {
      "file": "惡女不才_第四卷_speaker重校.md",
      "start_span_id": "V04-C02-S0341",
      "end_span_id": "V04-C02-S0389"
    }
  ],

  "participants": [
    "詠堯明",
    "黃景彰",
    "朱慧月"
  ],

  "observers": [
    "冬雪",
    "莉莉"
  ],

  "character_access": {
    "詠堯明": [
      "V04-C02-S0341:V04-C02-S0389"
    ],
    "黃景彰": [
      "V04-C02-S0341:V04-C02-S0389"
    ],
    "朱慧月": [
      "V04-C02-S0341:V04-C02-S0389"
    ],
    "江氏": []
  },

  "order": 17
}
```

The exact schema may evolve, but the following responsibilities should remain stable:

```text
event_id
source_ranges
participants
observers / information recipients where relevant
character_access
ordering / temporal locator
```

## `label` is navigation only

A short human-readable Event label may be included for browsing.

Example:

```text
景彰以聲音模仿協助堯明秘密離開
```

But:

> Event labels must never be treated as character-analysis evidence.

The original source passage remains authoritative.

---

# Character Access Must Be Source-Derived

`character_access` must be derived from the source situation, not from speculative reasoning about what a character “probably understood.”

Safe sources of access include:

```text
character directly heard the dialogue
character directly observed the action
character was explicitly told the information
character is the thinker of the inner monologue
character is the speaker of the utterance
source explicitly establishes later receipt of the information
```

Do not automatically expose information merely because:

```text
the reader knows it
it appears in the same Event
another participant knows it
it seems obvious in hindsight
the model thinks the character could probably infer it
```

Inference may be handled later by Character Reconstruction if needed.

Stage 2 should primarily model **source-supported access**, not speculative belief inference.

---

# Inner Thought and Knowledge Boundary

Inner thoughts are particularly important.

Example source:

```text
芳春: 「沒事的。」
芳春:（太好了，她們全都上當了。）
```

If Reirin heard only the spoken line, the Event may contain both source spans globally, but Reirin's accessible range must exclude the private thought.

Conceptually:

```text
Event source
├── spoken line              → Reirin accessible
└── 芳春 inner thought       → Reirin inaccessible
```

The downstream character system should receive:

```text
Event
↓
filter(character = Reirin)
↓
only accessible source spans
↓
Aiko
```

It should NOT receive the whole Event and then be instructed to “pretend not to know” hidden content.

---

# Event Boundaries

An Event should represent a meaningful story occurrence, not a mechanical text unit.

Do not assume:

```text
one sentence = one Event
one paragraph = one Event
one chapter = one Event
```

Potential Event-boundary signals include meaningful changes in:

- action / decision;
- participants;
- objective situation;
- location;
- conflict / goal;
- result / consequence;
- information availability;
- identity / body state;
- causal transition.

A chapter may contain many Events.

One Event may also require multiple contiguous or clearly linked source ranges if the narrative temporarily interrupts and resumes it. If multiple ranges are used, all ranges must remain explicitly traceable.

---

# Event Storage and Reuse

The same objective Event should be stored once.

Do not create:

```text
Event X for Reirin
Event X for Lily
Event X for Chenyu
```

Instead use:

```text
Event X
├── source_ranges
├── participants
├── observers
└── character_access
    ├── Reirin
    ├── Lily
    ├── Chenyu
    └── ...
```

This allows the same story index to support multiple character reconstructions.

---

# Query Contract Toward Aiko

For a target character, downstream retrieval should conceptually perform:

```text
character = <Target>
↓
find Events where character is:
    participant
    OR observer
    OR information recipient
    OR present in character_access
↓
retrieve Event source_ranges
↓
apply character_access filter
↓
return only source text accessible to that character
↓
Aiko Character Reconstruction
```

This should ensure:

```text
1. A character can find all relevant Events.
2. Every Event can retrieve the complete original passage.
3. A character cannot receive source information they did not have access to.
```

These are mandatory invariants of the current design.

---

# Relationship to Aiko

`data_processing/text/` owns:

```text
speaker / thinker attribution
human-reviewed speaker-grounded source
Event boundaries
Event source ranges
participants
observers / recipients
source-supported character access
story ordering needed for Event lookup
```

Aiko owns:

```text
subjective interpretation
Period Character State
Memory formation / retention
Development
Character Skill Profile
Compiled Character State
runtime-facing character context
```

Therefore:

```text
Text Processing
= What source content did this character have access to?

Aiko
= What did that experience mean to this character?
```

---

# Deferred / Optional Future Layers

The following artifacts are not required in the current two-stage workflow:

```text
Observation records
Fact records
separate Perspective files
separate Timeline files
mandatory semantic summaries
```

They may become useful later for:

- auditability;
- causal analysis;
- belief modeling;
- complex chronology;
- cross-media alignment;
- high-scale dependency invalidation.

But they should not be introduced merely because a schema can support them.

Current rule:

> Keep the semantic core minimal. Add new layers only when they solve a demonstrated problem.

---

# Correction and Rebuild Principle

Because Stage 2 depends on the human-reviewed Stage 1 source, a speaker correction may affect downstream Event metadata.

Example:

```text
speaker correction
↓
participant / observer correction
↓
character_access correction
↓
character reconstruction may need rebuild
```

The original source remains immutable.

Future tooling may add explicit dependency IDs or stale-artifact detection, but the current workflow should at minimum preserve clear source-file and source-range references.

---

# Design Principles

1. Preserve the original source unchanged.
2. Speaker attribution is derived annotation.
3. Dialogue attribution should be complete before Event indexing.
4. Inner thoughts in `（...）` must also be attributed to the thinker when supported.
5. Narration must not be mislabeled as dialogue.
6. Preserve character identity separately from body / disguise / performed identity.
7. Never force unresolved speaker attribution.
8. Human review of Stage 1 is required before Stage 2 whenever possible.
9. `Event = index, not replacement text`.
10. Every Event must deterministically retrieve its complete source passage.
11. Event labels are navigation aids, not evidence.
12. Participation does not imply complete knowledge.
13. Character access should point to original source spans whenever possible.
14. Do not summarize hidden knowledge into a character-access record when direct source indexing is possible.
15. Reader knowledge must not automatically become character knowledge.
16. Private thoughts must remain inaccessible to other characters unless communicated.
17. Store each objective Event once and reuse it for multiple characters.
18. Keep current implementation minimal; add Observation / Fact / other semantic layers only when necessary.
19. `data_processing/text/` determines **what happened, where it is in the source, and what source content each character could access**.
20. Aiko determines **what those experiences mean for the target character**.
