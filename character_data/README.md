# Character Data

This directory stores persistent character-owned data separately from agent/framework implementations.

Principles:

- `agents/` contains reusable agent/framework code.
- `character_data/` contains real character-specific source material and future reconstructed character data.
- Framework tests must not depend on real character corpora.
- Aiko should access character data through explicit configuration/contracts rather than hard-coded character paths.
- Character-specific data must not be treated as framework defaults.

Current characters:

- `Sakiko/`

The detailed schema and reconstruction contracts remain subject to Aiko research and future tasks.
