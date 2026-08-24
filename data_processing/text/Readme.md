# Text Data Processing

`data_processing/text/` is the text-specific source-processing layer for novels, prose, subtitles, transcripts, webpages converted to text, and other textual Canon material.

Its responsibility is deliberately narrow:

```text
1. Ground who is speaking / thinking in the source text.
2. Segment the source into traceable story-level Events.
```

The core boundary is:

> `data_processing/text/` prepares complete, traceable source material and Event boundaries.  
> `agents/AI_friend/Aiko` owns character perspective, knowledge-state reasoning, and character analysis.

`data_processing/text/` must not decide what a target character knows, believes, suspects, misunderstands, remembers, or psychologically infers from an Event.

---

# Current Official Workflow

```text
Raw novel / text source
↓
Stage 1 — Speaker / Thinker Attribution
↓
Human Review
↓
Speaker-grounded source
↓
Stage 2 — Event Segmentation / Indexing
↓
events.json
↓
Aiko Character Perspective Pre-Analysis
↓
Aiko Character Reconstruction
```

The previous hard-filter design is no longer part of the current workflow:

```text
Event
↓
character_access line allow-list
↓
remove inaccessible lines
↓
Aiko
```

This approach could fragment subjects, causal links, conversational context, observable actions, and narrator structure. The current pipeline therefore preserves the complete Event and lets Aiko reason about perspective while keeping story truth distinct from character knowledge.

Mandatory intermediate Observation / Fact / separate Perspective files are not required by `data_processing/text/`.

---

# Stage 1 — Speaker / Thinker Attribution

Stage 1 creates a speaker-grounded derivative of the original source.

Its job is only to determine who is responsible for dialogue or inner thought.

It does not create Events, personality conclusions, Memory, Development, perspective judgments, or character knowledge states.

## Preserve the original source

Never overwrite the original novel/source file.

Preferred flow:

```text
original source
↓
automatically speaker-attributed derivative
↓
human-reviewed speaker-grounded source
```

The human-reviewed version is the preferred input for Stage 2.

## Dialogue must receive speaker attribution

Every actual spoken utterance that can be attributed should be marked with its speaker.

Example:

```text
慧月（身體：黃玲琳）: 「我知道。」
```

If the work contains body swaps, possession, disguise, transformation, aliases, or similar identity changes, preserve character identity separately from body / visible identity.

Example:

```text
慧月（身體：黃玲琳）: 「……」
玲琳（身體：朱慧月）: 「……」
```

Do not infer the actual speaker only from the visible body.

## Inner thoughts must also receive attribution

Inner monologue written as `（...）` or equivalent private thought must be attributed to the thinker when supported.

Example:

```text
慧月（身體：黃玲琳）:（我，要死了嗎……？）
```

Speaker / thinker labels are source annotations. They help Aiko later distinguish dialogue from private thought, but Stage 1 itself does not decide another character's knowledge state.

## Narration is not dialogue

Ordinary narration remains narration.

```text
慧月默默地抬起手臂，凝視著掌心。
```

Do not convert it into a speaker-labelled line merely because the scene follows a character.

## Quoted material is not automatically current dialogue

Quotation marks may contain remembered speech, quoted documents, hypothetical statements, imitation, phrases mentioned as words, or embedded dialogue. Attribution must follow the source context.

## Uncertainty must remain explicit

Do not force attribution when the source does not support a reliable answer.

```text
【speaker 不確定（候選：A / B）】: 「……」
```

Human review should resolve uncertain cases where possible before Stage 2.

## Source text integrity

Speaker attribution is derived annotation:

```text
original text
≠ speaker annotation
```

Adding attribution must not silently rewrite, summarize, translate, reorder, or otherwise alter the underlying source text.

---

# Stage 2 — Event Segmentation / Indexing

Stage 2 operates on the human-reviewed speaker-grounded source and creates a story-level Event index.

Its purpose is not to summarize the novel and not to create a character-specific view.

The central rule is:

> **Event = complete source index, not replacement text.**

Each Event must be able to deterministically retrieve the complete source passage from which it was identified.

Conceptual minimal record:

```json
{
  "event_id": "V04-E-0017",
  "label": "navigation-only label",
  "source_ranges": [
    {
      "file": "惡女不才_第四卷_speaker重校.md",
      "start_line": 341,
      "end_line": 389
    }
  ],
  "narrative_order": 17,
  "story_chronology": null
}
```

The exact locator may use stable span IDs, line ranges, byte offsets, or another deterministic mechanism. The invariant is always:

```text
event_id
↓
source locator
↓
complete original Event passage
```

A short `label` may be stored for navigation, but it is never character-analysis evidence.

## Optional source-supported Event metadata

If useful for indexing or validation, Event records may contain minimal story-level metadata that is directly supported by the source, for example participants or scene/location identifiers.

Such metadata must remain descriptive of the Event itself. It must not become a character-perspective or knowledge-state model.

Do not store in `data_processing`:

```text
character_access allow-lists
Accessible / Inaccessible judgments
Known / Believed / Suspected / Misunderstood
character-specific interpretation
personality / appraisal conclusions
Memory / Development / Period Character State
```

Those belong to Aiko.

---

# Event Boundaries

An Event is a meaningful story occurrence, not a mechanical text unit.

Do not assume:

```text
one sentence = one Event
one paragraph = one Event
one chapter = one Event
```

Potential boundary signals include meaningful changes in:

- action / decision;
- objective situation;
- participant set;
- location;
- conflict / goal;
- result / consequence;
- identity / body state;
- causal transition;
- temporal transition.

One Event may use multiple explicitly traceable source ranges when the narrative interrupts and later resumes the same occurrence.

---

# Ordering

## `narrative_order`

Records source / reader presentation order.

```text
narrative_order
= order presented in the source
```

## `story_chronology`

When needed, records the estimated historical order inside the story world.

```text
story_chronology
= order in which represented Events actually occurred
```

This distinction is necessary for flashbacks, recollections, retrospective chapters, and other non-linear narration.

`data_processing` should preserve only enough chronology for downstream reconstruction; it should not grow into a complete temporal-reasoning engine unless a concrete need appears.

---

# Contract Toward Aiko

The output of `data_processing/text/` is a complete Event, not a character-filtered Event.

```text
event_id
+
complete source_ranges
+
source-grounded speaker / thinker annotations
+
minimal story-level metadata
+
ordering / chronology when needed
↓
Aiko
```

Aiko may read the complete Event while separately reasoning about what the target character can or cannot know.

Therefore:

```text
Context available to the analysis model
≠
Knowledge available to the target character
```

`data_processing` must not physically delete inaccessible lines to create a character-only replacement source.

---

# Relationship to Aiko

```text
data_processing/text/
────────────────────
Who spoke / thought this?
Where does the Event begin and end?
How can the complete Event be retrieved from Canon?
What is its source / narrative / chronological position?

Aiko
────────────────────
What information was available to the target character?
What did the character know, believe, suspect, or misunderstand?
What did the Event mean to that character?
How did it contribute to Memory, Evidence, Period State, or Development?
```

The Aiko stage begins with `Character Perspective Pre-Analysis` before personality or psychological interpretation.

---

# Correction and Rebuild Principle

A speaker / thinker correction can invalidate Event metadata or downstream Aiko analysis.

```text
speaker correction
↓
Event re-check when affected
↓
Aiko Perspective Pre-Analysis may become stale
↓
Character Reconstruction may require rebuild
```

The original source remains immutable.

---

# Design Principles

1. Preserve the original source unchanged.
2. Speaker / thinker attribution is derived annotation.
3. Human review of Stage 1 should precede Stage 2 whenever possible.
4. Preserve character identity separately from body / disguise / performed identity.
5. Never force unresolved attribution.
6. `Event = complete source index, not replacement text`.
7. Every Event must deterministically retrieve its complete original passage.
8. Keep Event data story-level and character-agnostic.
9. Do not hard-filter Event source by target character in `data_processing`.
10. Perspective and knowledge-state reasoning belong to Aiko.
11. Preserve narrative order and story chronology when they differ.
12. Prefer the smallest schema that preserves information Aiko actually needs.
13. Do not reintroduce Observation / Fact / Perspective layers unless a demonstrated requirement justifies them.
