# Character state contracts

`ai_friend.character.reconstruction` owns historical and compiled character
representation. It never owns raw Event or Memory records.

## Period Character State

`PeriodCharacterState` is the minimum character-analysis unit. It references one
`PeriodDefinition`, a temporal scope, a `KnowledgeBoundary`, supporting Event and
Evidence IDs, and exactly one `PeriodDomains` value with these eight slots:

`Personality / Physical / Motivation / Backstory / Emotion / Relationships /
Growth / Conflict`.

Each `DomainEntry` is either `observed`, `bounded_inference`, `unknown`,
`unchanged`, `insufficient_evidence`, or `not_applicable`. Abstaining entries
cannot contain fabricated statements or evidence. Evidence-bearing entries must
reference Event or Evidence IDs. Earlier states cannot reference an Event assigned
to a later period.

## Development

`DevelopmentRecord` is cross-period and therefore requires at least two Period
State IDs. It may represent qualitative `ChangeResistance`,
`HistoricalAdaptation`, `CausalHypothesis`, `AccessibilityProfile`, and
`HabitualProcessingPattern`. These are development dimensions, not extra Trait
Domains.

`confidence` describes evidential support. `change_resistance` describes expected
pattern stability. They are separate fields and no formula connects them. A
causal hypothesis retains supporting evidence, uncertainty, and alternative
hypotheses or counterevidence. No consolidation threshold is defined.

## Character skill and compiled state

`CharacterSkillProfile` records canonical or post-canon acquired proficiency and
must reference `SkillEvidence`; it does not describe executable tooling.
`CompiledCharacterState` has explicit schema/character versions and every compiled
entry references Period State, with optional Development/Evidence links. It is a
derived runtime-friendly view, never source evidence for itself.

Relationship data currently appears only as a Period domain entry and through
experience references. Permanent Relationship subsystem ownership is unresolved.
