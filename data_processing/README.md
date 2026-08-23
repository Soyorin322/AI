# Data Processing

`data_processing/` is the source-side preprocessing layer that prepares canonical source material for downstream use by Aiko.

Its purpose is deliberately narrow:

> transform heterogeneous source media into structured, traceable, minimally interpreted source data that `agents/AI_friend/Aiko` can consume safely.

`data_processing/` is **not** a second Character Reconstruction system. It should not grow character models, personality hypotheses, runtime logic, memory models, appraisal logic, or other Aiko-internal reasoning structures.

## Responsibility boundary

`data_processing/` owns source-side work such as:

- source normalization;
- speaker / dialogue annotation;
- scene and Event segmentation;
- source provenance and stable locators;
- participant / observer metadata when directly supported by the source;
- narrative ordering;
- story chronology metadata when needed to recover historical order;
- media-specific extraction / alignment needed before Aiko consumes the material.

It does **not** own:

- final character state;
- Period Character State;
- character Memory;
- Character Skill Profile;
- character-specific observations / evidence claims;
- personality, belief, relationship, or psychological conclusions;
- appraisal / subjective interpretation;
- runtime context;
- Aiko framework internals.

The intended flow is:

```text
Raw / collected source material
        ↓
data_processing/
        ↓
structured, traceable Canon artifacts
        ↓
agents/AI_friend/Aiko
        ↓
Character Reconstruction / Runtime / Event Interpretation
```

## Event data

Event data in `data_processing/` is a story-level source index, not a replacement for the original text and not a character model.

An Event should primarily help downstream systems answer:

```text
Where is this scene in the Canon?
What source span belongs to it?
Who participates in it?
In what order is it presented?
Where does it belong in story chronology?
```

The Event layer should remain minimal. Character-specific psychological analysis belongs downstream in Aiko.

### `narrative_order`

`narrative_order` records the order in which Events are presented in the source material.

```text
narrative_order
= source / reader presentation order
```

It is useful for:

- source navigation;
- reconstructing the original narrative sequence;
- preserving reveal / disclosure order.

It does **not** imply that the Event occurred at that position in the character's life.

### Story chronology

Story chronology records the estimated historical ordering of Events inside the story world.

```text
story chronology
= order in which the represented events actually occurred
```

This is distinct from `narrative_order` because novels frequently contain flashbacks, recollections, retrospective chapters, and other non-linear narration.

Example:

```text
Narrative order:
E01 → E02 → E36 (flashback) → E37

Story chronology:
E36 → E01 → E02 → E37
```

Story chronology exists only to preserve enough historical structure for downstream reconstruction. It should not grow into a complete temporal-reasoning system unless a concrete source-processing requirement demonstrates that it is necessary.

## Character perspective / access

Character perspective is an important source-processing problem because:

> story truth is not automatically character knowledge.

However, the current line-level allow-list approach can fragment the source context too aggressively. A character-only view assembled from isolated permitted lines may lose subjects, causal context, action continuity, and conversational meaning.

Therefore the following remains an explicit research item rather than a finalized schema:

### Research item — Complete Event Context + Perspective / Access Mask

Research whether downstream analysis can reliably use:

```text
complete Event context
+
character perspective / access constraint
```

instead of physically reducing the Event into a sparse set of readable source lines.

The goal is to preserve complete narrative context while still preventing leakage of:

- another character's private thoughts;
- narrator-only omniscient information;
- future revelations;
- information learned only at a later time;
- other information not available to the target character at that point in the story.

This mechanism must be evaluated before becoming a stable data contract. In particular, research must test whether an LLM can respect the access boundary without incorrectly treating inaccessible context as character knowledge.

Until that mechanism is validated, perspective metadata should remain conservative and should not be treated as a character-specific replacement text.

## Planned media areas

The exact structure remains intentionally minimal until each media workflow is researched. Possible areas include:

```text
data_processing/
├── text/
├── video/
├── image/
├── web/
├── common/
└── docs/
```

Folders should only be added when their ownership and data contract are clear.

## Design principles

1. Preserve provenance back to the original source.
2. Keep raw source separate from derived annotations.
3. Do not silently convert uncertain annotations into canonical facts.
4. Keep Event records story-level and avoid character-specific duplication.
5. Keep source processing separate from Character Reconstruction.
6. Preserve both narrative presentation order and story chronology when they differ.
7. Treat character access as a perspective constraint, not automatically as replacement text.
8. Avoid introducing psychological or runtime concepts into `data_processing/` unless they are strictly required for source preprocessing.
9. Prefer the smallest schema that preserves information Aiko actually needs.
10. Keep data formats portable and independent of any specific LLM provider.

## Complexity guardrail

Before adding a new field, annotation layer, or preprocessing stage, ask:

```text
Does Aiko need this information from the source layer?

Can Aiko derive it later during Character Reconstruction without losing provenance or source fidelity?
```

If the second answer is yes, prefer deriving it downstream instead of permanently expanding `data_processing/`.

`data_processing/` should remain a clean bridge from Canon to Aiko, not become another copy of Aiko itself.
