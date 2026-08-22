# Character

The current contract defines only generic identity, description, and opaque state
attributes in Aiko-owned dataclasses. It is independent of vendor storage and is
not a final persistent Character Core schema. Persona periods, trait resistance,
expression, dynamic-state separation, evidence, relationship, and consolidation
semantics remain deferred; perception never mutates this profile directly.

Reconstruction artifacts and snapshots now provide a separate persistent-data
boundary. A future compiler/provider adapter may create a runtime-facing
`CharacterProfile` from validated reconstruction state, but Task 003 deliberately
does not define that compilation or turn `CharacterProfile` into canonical storage.
