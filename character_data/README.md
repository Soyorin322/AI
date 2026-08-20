# Character Data

This directory stores persistent character-owned data separately from agent/framework implementations.

## Principles

- `agents/` contains reusable agent/framework code.
- `character_data/` contains real character-specific source material, derived character data, and character-owned skills.
- Framework tests must not depend on real character corpora.
- Aiko should access character data through explicit configuration/contracts rather than hard-coded character paths.
- Character-specific data must not be treated as framework defaults.
- Raw/archived source material, derived character data, and skill knowledge should remain distinguishable so provenance can be preserved.

## Standard character structure

```text
<Character>/
├── README.md
├── sources/
│   ├── raw/
│   │   ├── anime/
│   │   ├── game/
│   │   ├── novel/
│   │   ├── music/
│   │   └── official/
│   └── curated/
│       ├── background/
│       ├── timeline/
│       └── reference_notes/
├── data/
└── skills/
```

### `sources/`

Stores source material and source-oriented organization.

- `sources/raw/` should stay as close as practical to original source material and source metadata.
- Web pages may be archived as Markdown when practical, but the Markdown file must preserve the original URL, retrieval date, and source identity.
- Converting a web page to Markdown does not make its claims canonical; source authority must still be tracked separately.
- `sources/curated/` may reorganize source material for reconstruction, but should not silently convert interpretation into canonical character facts.
- Provenance from curated material back to raw/official source material should be preserved.

### `data/`

Stores character-specific data derived or compiled from sources, such as structured background records, events, evidence, claims, timelines, relationships, or reconstructed state.

Derived data should preserve provenance back to the source material that supports it. Personality, beliefs, values, traits, and other reconstructed claims should not be written into `sources/` as if they were source material.

### `skills/`

Stores character-owned skill knowledge and skill-specific material used to let a character perform or reason about learned abilities.

Examples include historical etiquette, tea ceremony, dance, music, language, or other domain instruction. Skill teaching material should be kept separate from canonical character evidence: knowing how a skill works is not itself evidence that a character canonically possesses that skill.

A skill can therefore contain its own instructional/reference material while the character model separately records whether, when, and to what degree the character possesses that skill.

## Current characters

- `Sakiko/`
- `Reirin/`

The detailed schemas and reconstruction contracts for evidence, claims, reconstructed character state, and skill state remain subject to Aiko research and future tasks.
