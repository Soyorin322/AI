# Text Data Processing

`data_processing/text/` is the text-specific preprocessing layer for novels, prose, subtitles, transcripts, webpages converted to text, and other textual source material.

Its responsibility is to turn source text into structured, auditable artifacts while preserving a strict distinction between original text and derived annotations.

## Intended processing stages

A text workflow may gradually include:

```text
Raw text
↓
Normalization
↓
Speaker attribution / dialogue annotation
↓
Source segmentation
↓
Observation extraction
↓
Event segmentation
↓
Participant / perspective analysis
↓
Story-level structured data
```

Not every source must use every stage.

---

# Speaker Attribution Rules

Speaker attribution is a **derived annotation**, not part of the original canonical text unless the source explicitly names the speaker.

The annotated output must therefore preserve:

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

Both should remain independently recoverable.

## 2. Do not alter the original wording

Adding speaker labels must not silently rewrite, summarize, translate, reorder, or normalize the underlying prose/dialogue unless that transformation is explicitly part of another processing stage.

A speaker-attributed file should ideally preserve the original textual content and add only annotation metadata or prefixes.

## 3. Mark attribution provenance

Each speaker annotation should be distinguishable as one of the following conceptual classes:

```text
EXPLICIT
    The source directly identifies the speaker.

CONTEXT_INFERRED
    The speaker is inferred from local narrative/dialogue context.

RULE_INFERRED
    The speaker is assigned by a deterministic annotation rule.

UNCERTAIN
    Available context is insufficient for reliable attribution.
```

Exact schema names may change later, but the distinction must remain machine-readable when structured annotation is introduced.

## 4. Never force an uncertain speaker

If attribution is not sufficiently supported, preserve uncertainty instead of guessing.

Example textual convention:

```text
【speaker 不確定】「……」
```

A downstream model must be able to tell that this is unresolved.

## 5. Context is evidence, not proof by default

Useful speaker-attribution signals include:

- explicit speech verbs or names;
- turn-taking structure;
- nearby narration;
- vocatives / forms of address;
- character location and scene participation;
- first-person self-reference;
- distinctive knowledge available only to certain participants;
- body/identity state in body-swap or disguise scenarios.

These signals may support attribution, but inferred attribution must not be silently promoted to canonical fact.

## 6. Character identity and body identity must remain separate

For stories involving body swaps, possession, disguise, transformation, aliases, or identity concealment, speaker labels must preserve both conceptual identities when relevant.

Example:

```text
character_identity: Reirin / 黃玲琳
body_identity: 朱慧月
```

Do not assign identity solely from the visible/current body.

## 7. Speaker annotation must not directly become character evidence

Preferred downstream flow:

```text
annotated speaker label
↓
return to exact source/context
↓
Observation / Event
↓
Evidence
```

A derived speaker tag alone must not become a high-confidence personality, relationship, memory, or knowledge claim.

## 8. Corrections must be auditable

If a speaker attribution is corrected later, preserve enough provenance to determine:

- which span changed;
- previous attribution;
- new attribution;
- why it changed;
- whether downstream artifacts need invalidation/rebuild.

Long-term structured annotations should therefore use stable source-span IDs rather than relying only on edited prose files.

---

# Event and Perspective Processing

Text processing may also produce story-level Event segmentation and participant/perspective annotations.

This layer should answer story questions such as:

```text
What happened?
Who participated?
Who directly observed it?
Who was told about it?
Who could know only part of it?
Who was not aware of it?
```

This is different from character reconstruction, which asks what a specific character retained, believed, remembered, or became because of those events.

A long-term preferred architecture is:

```text
Text Source
↓
Story Event
↓
Perspective / Accessibility Mapping
↓
Character Reconstruction
```

## Event single-source-of-truth

The same objective Event should not be duplicated once per character.

Preferred:

```text
Event X
├── Reirin perspective
├── Lily perspective
├── Chenyu perspective
└── Keigetsu perspective
```

rather than:

```text
Event X for Reirin
Event X for Lily
Event X for Chenyu
...
```

## Perspective annotations

A future perspective annotation may distinguish concepts such as:

```text
DIRECTLY_OBSERVED
DIRECTLY_TOLD
CHARACTER_INFERRED
PARTIALLY_ACCESSIBLE
STORY_ONLY
UNKNOWN
```

The exact schema is intentionally not fixed yet.

Important principle:

> Facts may be global; access to facts is contextual.

Therefore an Event can exist in the story graph without being knowledge available to every character.

---

# Boundary with Aiko

`data_processing/text/` should primarily own source-side and story-level processing:

```text
speaker attribution
source spans
story events
participants
perspective/accessibility annotations
```

Aiko / character reconstruction should own character-side interpretation:

```text
Period Character State
Memory
Development
Character Skill Profile
Compiled Character State
```

Do not store final personality conclusions in this text-processing layer.

---

# Design Principles

1. Preserve exact-source provenance.
2. Raw text and derived annotation are separate artifacts.
3. Speaker attribution uncertainty must remain visible.
4. Do not use schema completeness as permission to guess.
5. Event segmentation should be evidence-driven, not mechanically one sentence or one chapter per Event.
6. Story Event and character subjective interpretation must remain distinct.
7. One Event should be stored once and referenced by multiple perspectives.
8. Character accessibility is contextual and time-dependent.
9. Corrections to upstream annotations should be traceable to downstream dependent artifacts.
10. Formats should remain portable and independent of any specific LLM provider.
