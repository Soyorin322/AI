# Character Reconstruction

Task 003 added the evidence-grounded base. Task 005 hardens it into explicit
stage ownership and validates the v0.0.8 longitudinal path:

```text
SourceReference -> exact SourceUnit -> ObservationRecord -> EventRecord
-> PeriodAssignment -> PeriodCharacterState -> DevelopmentRecord
-> CompiledCharacterState
```

Event also branches by ID into `MemoryFormationDecision -> MemoryRecord` and
`SkillEvidence -> CharacterSkillProfile`. Neither branch owns another Event copy.

These are distinct Aiko-owned types. `Lineage` connects derived artifacts to
source identities, source units, and parents. Candidate, unresolved, supported,
contradicted, and explicitly consolidated states remain representable.
Plausibility alone never makes an inference canonical.

`validate_bundle()` reports invalid exact-source grounding, reference notes used
as canonical sources, missing references, broken source lineage, duplicate IDs,
self/cyclic ancestry, claims used as evidence, broken status histories, and unsafe
snapshots. `validate_reconstruction_graph()` additionally enforces Event,
Period, knowledge-boundary, Development, Memory, Skill, and Compiled State stage
gates. Validation is structural; it does not score psychology, infer confidence,
derive change resistance, or resolve contradictions.

`ReconstructionRepository` remains the replaceable persistence contract and the
in-memory implementation preserves immutable bundle revisions.
`ReconstructionPipeline` validates and saves caller-produced artifacts. Automatic
source extraction, appraisal, consolidation policy, LLM processors, vector
databases, and production memory are deferred.

`to_portable_json()` provides deterministic JSON envelopes with explicit schema
and artifact versions. YAML may be a human-editable projection later, but is not
a second canonical schema.

See `folder_ownership.md` for mandatory routing and `docs/schemas/` for field
semantics. No real character instance or corpus is part of this implementation;
tests use only a tiny invented fixture.
