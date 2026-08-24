# Character Reconstruction

Task 003 added the evidence-grounded base. Task 005 hardens it into explicit
stage ownership and validates the v0.0.8 longitudinal path.

Character Reconstruction now assumes a character-perspective pre-analysis stage
between story-level Event preparation and character interpretation. The purpose
of this gate is to preserve full Event context while distinguishing story truth
from information available to the target character.

```text
SourceReference -> exact SourceUnit -> ObservationRecord -> EventRecord
-> CharacterPerspectivePreAnalysis
   -> Accessible / Inaccessible / Uncertain
   -> Known / Believed / Suspected / Misunderstood
-> PeriodAssignment -> PeriodCharacterState -> DevelopmentRecord
-> CompiledCharacterState
```

The perspective stage is a precondition for character analysis, not a personality
analysis stage. It should determine the world the character can reason from before
downstream interpretation asks what that world means to the character.

The complete Event may remain available to the LLM for contextual comprehension.
Information judged inaccessible must not be attributed to the target character.
Uncertain cases remain representable and must not be forced into a binary result.

A first implementation may use two analysis passes:

```text
Pass 1: Complete Event -> Accessible / Inaccessible / Uncertain
Pass 2: Event + Pass 1 + relevant validated character context
        -> Known / Believed / Suspected / Misunderstood
```

This separation reduces the risk of mixing direct information access with
character-dependent inference. Personality, appraisal, trait hypotheses, and
Period Character State updates occur only after this gate.

Each completed perspective-analysis batch should also support a generated
human-readable Markdown review projection, for example:

```text
reirin_perspective_review_volume1.md
```

The review projection is used to check access-boundary errors, private-thought
leakage, future-knowledge leakage, uncertainty handling, and incorrect promotion
of belief or suspicion into knowledge. It is not canonical storage and must remain
regenerable from structured perspective-analysis data.

See:

```text
docs/research/event/character_perspective_preanalysis_v0.0.1.md
```

for the initial research / implementation contract and review format.

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
Perspective / knowledge-boundary, Period, Development, Memory, Skill, and
Compiled State stage gates. Validation is structural; it does not score
psychology, infer confidence, derive change resistance, resolve contradictions,
or decide whether an LLM perspective judgment is semantically correct.

`ReconstructionRepository` remains the replaceable persistence contract and the
in-memory implementation preserves immutable bundle revisions.
`ReconstructionPipeline` validates and saves caller-produced artifacts. Automatic
source extraction, appraisal, consolidation policy, LLM processors, vector
databases, and production memory remain deferred unless introduced by a later
implementation task.

`to_portable_json()` provides deterministic JSON envelopes with explicit schema
and artifact versions. Human-review Markdown is a projection, not a second
canonical schema.

See `folder_ownership.md` for mandatory routing and `docs/schemas/` for field
semantics. No real character instance or corpus is part of the framework
implementation unless an explicit character-data task introduces one; tests
should continue to prefer small invented fixtures.
