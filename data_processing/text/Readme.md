# Text Data Processing

`data_processing/text/` is the text-specific preprocessing and **story reconstruction** layer for novels, prose, subtitles, transcripts, webpages converted to text, and other textual source material.

Its responsibility is to determine, as faithfully and audibly as possible:

```text
What does the source say?
What happened in the story?
Who participated?
Who could know which parts?
```

It is deliberately separated from Aiko's character reconstruction responsibility.

The core boundary is:

> `data_processing/text/` determines **what happened and who could know it**.  
> Aiko determines **what those experiences mean for a particular character**.

---

# Core Pipeline

The intended long-term text-processing pipeline is:

```text
Raw Text
↓
Source Normalization
↓
Speaker Attribution
↓
Scene / Source-Span Segmentation
↓
Observation Extraction
↓
Event Segmentation
↓
Event Participants
↓
Objective Facts
↓
Timeline
↓
Perspective / Accessibility Mapping
↓
Story-level structured output
```

The resulting story-level output is then consumed by character reconstruction:

```text
StoryEvent
+
PerspectiveReference(<Character>)
+
Evidence
↓
Aiko Character Reconstruction
↓
Period Character State
Memory
Development
Character Skill Profile
Compiled Character State
```

This separation is intentional.

Aiko should not need to repeatedly answer:

```text
"What happened in this chapter?"
```

for every character.

Instead, the story-processing layer should establish a shared story representation once, and Aiko should consume the perspective relevant to the target character.

---

# Ownership Boundary

## `data_processing/text/` owns

Source-side and story-level artifacts such as:

```text
Source normalization
Speaker attribution
Scene / span segmentation
Source-grounded observations
Story Event segmentation
Event participants
Objective story facts
Story timeline
Perspective / accessibility mapping
Story-level evidence/provenance
```

## Aiko / Character Reconstruction owns

Character-specific derived state such as:

```text
Period Character State
Character-specific subjective interpretation
Memory
Development
Character Skill Profile
Compiled Character State
Runtime-facing character context
```

## Explicit non-ownership

`data_processing/text/` must NOT directly decide:

```text
final personality traits
persistent character disposition
long-term psychological development
what the character remembers permanently
compiled persona
runtime behavior
```

Those belong downstream.

---

# Story Truth vs Character Experience

A central design principle is:

```text
Story Truth
≠ Character-Accessible Truth
≠ Character Interpretation
```

Example:

```text
Story Truth:
Lily privately accepts an inducement.

Reirin-accessible truth:
Lily behaves with hostility toward Reirin.

Possible Reirin inference:
Lily dislikes the person she believes to be Zhu Huiyue.
```

The first fact may exist in the global story graph without being available to Reirin.

Therefore:

> Facts may be global; access to facts is contextual.

---

# Speaker Attribution Rules

Speaker attribution is a **derived annotation**, not part of the original canonical text unless the source explicitly identifies the speaker.

The annotated output must preserve:

```text
original text
≠ speaker annotation
```

## 1. Preserve the original source

Never overwrite or replace the original source with a speaker-attributed derivative.

Preferred flow:

```text
raw source
↓
speaker-attributed derivative
```

Both must remain independently recoverable.

## 2. Do not alter original wording

Adding speaker labels must not silently rewrite, summarize, translate, reorder, or normalize the underlying prose/dialogue unless that transformation is explicitly another processing stage.

A speaker-attributed derivative should ideally preserve the original text and add only annotation metadata or prefixes.

## 3. Attribution provenance

Each speaker annotation should eventually be distinguishable as one of the following conceptual classes:

```text
EXPLICIT
    Source directly identifies the speaker.

CONTEXT_INFERRED
    Speaker is inferred from nearby narrative/dialogue context.

RULE_INFERRED
    Speaker is assigned by a deterministic annotation rule.

UNCERTAIN
    Available context is insufficient for reliable attribution.
```

Exact schema names may change, but the distinction should remain machine-readable.

## 4. Never force an uncertain speaker

If the context is insufficient, preserve uncertainty instead of guessing.

Example textual convention:

```text
【speaker 不確定】「……」
```

A downstream model must be able to distinguish unresolved attribution from confirmed attribution.

## 5. Context is evidence, not proof by default

Useful attribution signals include:

- explicit speech verbs / names;
- turn-taking structure;
- nearby narration;
- vocatives / forms of address;
- scene participation;
- first-person self-reference;
- character-specific knowledge;
- body / identity state in body-swap, disguise, possession, or transformation scenarios.

These signals may support attribution, but inferred attribution must not silently become canonical fact.

## 6. Character identity and body identity must remain separate

For stories involving body swaps, possession, disguise, transformation, aliases, or identity concealment, preserve both identities when relevant.

Example:

```text
character_identity: Reirin / 黃玲琳
body_identity: 朱慧月
```

Do not infer identity only from the visible/current body.

## 7. Speaker annotation is not direct personality evidence

Preferred downstream flow:

```text
speaker annotation
↓
exact source/context
↓
Observation
↓
Story Event / Evidence
↓
Character Reconstruction
```

A derived speaker tag alone must not become a high-confidence personality, relationship, Memory, or knowledge claim.

## 8. Corrections must be auditable

If an attribution is corrected later, preserve enough provenance to determine:

- which source span changed;
- previous attribution;
- new attribution;
- reason for correction;
- downstream artifacts that may require invalidation or rebuild.

Long-term structured annotation should therefore prefer stable source-span IDs.

---

# Scene / Source-Span Segmentation

Scene or span segmentation should create stable textual units that can be referenced by later story artifacts.

It should NOT automatically assume:

```text
chapter = scene
a paragraph = event
one dialogue line = event
```

Segmentation exists to provide recoverable source context, not to predetermine narrative meaning.

A source span should preserve:

```text
source identity
exact locator
exact text or immutable exact-span reference
annotation provenance
```

---

# Observation Extraction

Observation is the first derived statement from source text.

It should answer:

```text
What does this source span directly support?
```

Examples:

```text
X said Y.
X moved from A to B.
X was visibly injured.
X explicitly stated a goal.
```

Observation must remain narrower than interpretation.

Do not turn:

```text
"X apologizes for causing harm"
```

into:

```text
"X is fundamentally responsible"
```

at this layer.

---

# Event Segmentation

The text-processing layer should identify story-level Events from observations.

An Event answers:

```text
What happened?
```

not:

```text
What permanent trait does this prove?
```

Event segmentation should be based on meaningful changes such as:

- action / decision;
- participants;
- objective situation;
- location;
- goal or conflict;
- outcome;
- knowledge state;
- identity/body state;
- consequential causal transition.

Avoid both extremes:

```text
one Event per sentence
```

and:

```text
one Event for an entire chapter
```

---

# Event Single Source of Truth

The same objective Event should exist once in the shared story representation.

Preferred:

```text
Event X
├── objective facts
├── participants
├── source lineage
└── perspective/accessibility references
```

and:

```text
Event X
├── Reirin perspective
├── Lily perspective
├── Chenyu perspective
└── Keigetsu perspective
```

rather than duplicating:

```text
Event X for Reirin
Event X for Lily
Event X for Chenyu
...
```

This is important for consistency, provenance, and multi-character reconstruction.

---

# Event Participants

Participants should represent who was actually involved in or present for an Event.

Participation does NOT automatically imply full knowledge.

A participant may:

```text
observe only part of an Event
misunderstand the Event
arrive late
leave early
hear only dialogue
observe consequences but not cause
```

Therefore:

```text
participant
≠ complete knower
```

---

# Objective Facts

Event processing may extract story-level objective facts where the source supports them.

These should remain separate from:

```text
what a character perceived
what a character inferred
what a character believed
```

For example:

```text
Objective fact:
A private agreement occurred.

Character perception:
Reirin did not witness it.

Character inference:
Reirin may infer only from later behavior.
```

Do not flatten these layers.

---

# Timeline

Timeline processing should establish story chronology independently from character Periods.

```text
Story Timeline
≠ Character Period State
```

The story timeline answers:

```text
When did Event A occur relative to Event B?
```

Aiko Period reconstruction answers:

```text
When did the character enter a meaningfully different historical state?
```

A chapter or date may help chronology without defining a Character Period.

---

# Perspective / Accessibility Mapping

This layer records who could access what information at a given time.

A future perspective representation may distinguish concepts such as:

```text
DIRECTLY_OBSERVED
DIRECTLY_TOLD
CHARACTER_INFERRED
PARTIALLY_ACCESSIBLE
STORY_ONLY
UNKNOWN
```

The exact schema is not yet permanently fixed.

## Prefer fact-level accessibility when needed

Whole-Event accessibility may be too coarse.

An Event may contain multiple facts:

```text
Event X
├── fact-01
├── fact-02
└── fact-03
```

A character may know only some of them.

Example:

```text
Event:
Lily accepts an inducement and later behaves hostilely.

Reirin:
├── hostile behavior → accessible
└── private inducement → story-only
```

Therefore long-term perspective mapping should be capable of representing partial knowledge rather than only:

```text
knows_event = true / false
```

## Perspective is contextual

The same global fact may have different accessibility for different characters:

```text
fact-X
├── Reirin  → STORY_ONLY
├── Lily    → CHARACTER_ACCESSIBLE
├── Chenyu  → UNKNOWN
└── Keigetsu→ CHARACTER_ACCESSIBLE
```

This enables the same story graph to support multiple character reconstructions without duplicating Events.

---

# Output Contract Toward Aiko

The intended handoff from text processing to Aiko is conceptually:

```text
StoryEvent
+
PerspectiveReference(target_character)
+
Evidence / Source Lineage
```

Aiko then answers:

```text
What did this character experience?
What did they know at that point?
What did they retain as Memory?
What did the experience mean to them?
How did their Period Character State change?
What patterns emerge across Periods?
```

This means Aiko should increasingly consume story-level structured data rather than repeatedly re-parse raw novel text for every character.

---

# Multi-Character Reuse

The story-processing layer should be reusable across multiple target characters.

Example:

```text
Shared Story Graph
        ↓
PerspectiveReference(Reirin)
        ↓
Reirin Character Reconstruction

Shared Story Graph
        ↓
PerspectiveReference(Lily)
        ↓
Lily Character Reconstruction
```

The story layer is shared.

Character reconstruction remains character-specific.

---

# Upstream Correction and Dependency Invalidation

Because Speaker → Observation → Event → Perspective forms a dependency chain, upstream corrections may invalidate downstream artifacts.

Example:

```text
speaker attribution corrected
↓
Observation may change
↓
Event participant / statement attribution may change
↓
Perspective mapping may change
↓
Character reconstruction may need rebuild
```

Future tooling should preserve dependency/provenance links so these rebuilds can be targeted rather than manual and global.

---

# Design Principles

1. Preserve exact-source provenance.
2. Raw text and derived annotation are separate artifacts.
3. Speaker attribution uncertainty must remain visible.
4. Do not use schema completeness as permission to guess.
5. Observation ≠ interpretation.
6. Event segmentation should be evidence-driven, not mechanically sentence- or chapter-based.
7. Story Event ≠ Character subjective interpretation.
8. Store each objective Event once.
9. Reuse one story graph for multiple characters.
10. Participants do not automatically know the complete Event.
11. Prefer fact-level accessibility when Event-level accessibility is too coarse.
12. Story chronology ≠ Character Period segmentation.
13. Character accessibility is contextual and time-dependent.
14. Upstream annotation corrections must be traceable to downstream dependent artifacts.
15. Formats should remain portable and independent of any specific LLM provider.
16. `data_processing/text/` determines **what happened and who could know it**.
17. Aiko determines **what those experiences mean for the target character**.
