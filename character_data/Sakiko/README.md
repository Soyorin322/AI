# Sakiko Character Data

This directory is the character-specific data root for Sakiko.

It is intentionally kept outside `agents/AI_friend/Aiko/` so that Aiko remains character-agnostic.

Planned structure:

```text
Sakiko/
├── README.md
└── sources/
    ├── raw/
    │   ├── anime/
    │   ├── game/
    │   ├── novel/
    │   ├── music/
    │   └── official/
    └── curated/
        ├── background/
        ├── timeline/
        └── reference_notes/
```

Rules:

- `sources/raw/` should stay as close as practical to original source material and source metadata.
- `sources/curated/` may reorganize source material for reconstruction, but should not silently convert interpretation into canonical character facts.
- Personality, beliefs, values, traits, and other reconstructed claims should not be written into `sources/` as if they were source material.
- Provenance from curated material back to raw/official source material should be preserved.
- Aiko framework tests should use synthetic fixtures, not Sakiko data.

Final schemas for source metadata, evidence, claims, and reconstructed character state are intentionally deferred to the Aiko research → architecture → schema → task maturity process.
