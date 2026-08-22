# Reconstruction contracts

This document records the Task 003 foundation as hardened by Task 005. Python
dataclasses in `ai_friend.reconstruction.models` are authoritative.

| Contract | Responsibility |
|---|---|
| `SourceReference` | Explicitly approved, format-neutral source identity and locator |
| `SourceUnit` | Exact approved source span or immutable exact-span reference |
| `ObservationRecord` | First derived, source-supported observation |
| `EventRecord` | Single source-of-truth event; never a persistent trait |
| `EvidenceRecord` | Supporting or contradicting bounded evidence |
| `PeriodDefinition` | Historically coherent interval and knowledge boundary |
| `PeriodAssignment` | Explicit Event-to-Period assignment and rationale |
| `CharacterClaim` | Explicitly uncertain Task 003 hypothesis |
| `CharacterStateSnapshot` | Versioned Task 003 consolidated view |
| `ReconstructionBundle` | Immutable repository revision |
| `Lineage` | Source, source-unit, and derived-parent references |
| `TemporalScope` | Format-neutral point/interval metadata |

## Source grounding gate

`SourceUnit.grounding` is mandatory at validation time:

- `exact_text` requires exact content, an exact locator, and an integrity hash;
- `immutable_exact_span_reference` requires a locator and integrity hash and
  must not carry generated summary prose.

Summaries and interpretations belong in `ObservationRecord`, not `SourceUnit`.
A source must set `approved=true`; an unapproved source cannot ground the graph.
A `SourceReference` marked `source_role=reference_note` is rejected. Reference
notes may locate a scene but cannot become canonical evidence.

## Event and period gates

An Event references an Observation and has temporal scope. Objective facts,
character-accessible information, statements, behavior, outcome, and uncertainty
are distinct optional fields. No Event may declare a persistent trait. Store the
Event once and reference it from domains, memory, and skill evidence.

`PeriodDefinition` is ordered and carries explicit boundary status and rationale.
`PeriodAssignment` assigns an Event explicitly; chapters do not create periods
automatically. See `character_state.md` for later stages.

## Provenance and maturity

Only claims explicitly transitioned from `supported` to `consolidated` may be
included as consolidated snapshot inputs. This is a structural safety rule, not
a psychological confidence algorithm. Task 005 retains all Task 003 circularity,
status-transition, repository, and provenance protections.

Final appraisal, expression, and permanent Relationship ownership remain
deferred. Task 005 adds representations and structural gates, not scoring or
automatic psychological algorithms.
