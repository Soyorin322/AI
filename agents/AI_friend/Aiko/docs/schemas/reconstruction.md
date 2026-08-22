# Reconstruction contracts

This document records the stable Task 003 implementation-facing contracts. The
Python dataclasses in `ai_friend.reconstruction.models` are authoritative.

| Contract | Responsibility |
|---|---|
| `SourceReference` | Format-neutral source identity and locator |
| `SourceUnit` | Addressable raw source content |
| `ObservationRecord` | Observation derived from source content |
| `EventRecord` | Minimal event boundary; not subjective appraisal |
| `EvidenceRecord` | Supporting or contradicting evidence |
| `CharacterClaim` | Explicitly uncertain character hypothesis |
| `CharacterStateSnapshot` | Versioned consolidated reconstruction view |
| `ReconstructionBundle` | Immutable repository revision containing artifacts |
| `Lineage` | Source, source-unit, and derived-parent references |
| `TemporalScope` | Optional format-neutral point/interval metadata |

Only claims explicitly transitioned from `supported` to `consolidated` may be
included as consolidated snapshot inputs. This is a structural safety rule, not
a psychological confidence algorithm. Final Persona, event, temporal-development,
relationship, expression, and appraisal schemas remain deferred.

