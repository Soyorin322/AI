# Data Processing

`data_processing/` is the generic preprocessing and analysis layer for source materials used by the AI project.

Its responsibility is to transform heterogeneous source media into structured, traceable data that downstream systems such as story reconstruction and character reconstruction can consume.

This directory is intentionally media-agnostic. Future inputs may include:

- novels / prose / subtitles / transcripts;
- animation / video;
- images / illustrations / screenshots;
- webpages;
- other structured or unstructured source material.

## Responsibility boundary

`data_processing/` owns source-side processing such as normalization, segmentation, annotation, extraction, alignment, and media-specific preprocessing.

It does **not** own:

- final character state;
- character Memory;
- Character Skill Profile;
- runtime context;
- Aiko framework internals;
- character-specific personality conclusions.

A useful high-level flow is:

```text
Raw / collected source material
        ↓
data_processing/
        ↓
structured source / story-level artifacts
        ↓
Aiko Character Reconstruction
        ↓
agents/AI_friend/<Character>/
```

## Planned media areas

The exact structure remains intentionally minimal until each media workflow is researched. Likely future areas include:

```text
data_processing/
├── text/
├── video/
├── image/
├── web/
├── common/
└── docs/
```

These folders should only be created when their ownership and data contracts are defined.

## Design principles

1. Preserve provenance back to the original source.
2. Keep raw source separate from derived annotations and analysis.
3. Do not silently convert uncertain annotations into canonical facts.
4. Prefer reusable, media-agnostic contracts where possible.
5. Avoid duplicating the same story-level Event for each character.
6. Keep story-level processing separate from character-specific reconstruction.
7. Facts may be global; character access to those facts is contextual.
8. Data formats should remain portable and independent of any specific LLM provider.

This directory is currently a foundation point only. Media-specific schemas and pipelines will be introduced through later research/tasks rather than assumed in advance.
