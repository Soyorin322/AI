# Character Reconstruction

Task 003 adds a character-agnostic, evidence-grounded reconstruction boundary.
It builds persistent reconstruction artifacts from caller-supplied source data;
it does not run as part of ordinary Runtime interaction.

```text
SourceReference
      ↓
SourceUnit
      ↓
ObservationRecord
      ↓
EventRecord
      ↓
EvidenceRecord
      ↓
CharacterClaim
      ↓ explicit maturity transition
CharacterStateSnapshot
```

These are distinct Aiko-owned types. `Lineage` connects derived artifacts to
source identities, source units, and parent artifacts without assuming chapters,
files, transcripts, or any other source format. Claims may remain candidate,
unresolved, supported, or contradicted. A consolidated claim requires an explicit
transition from supported status; plausibility alone never makes it canonical.

`validate_bundle()` reports missing references, missing evidence lineage,
duplicate IDs, self/cyclic ancestry, claims used as evidence, broken status
histories, and snapshots containing non-consolidated claims. It checks structural
integrity only; it does not score psychological truth or resolve contradictions.

`ReconstructionRepository` is the persistence contract. The included in-memory
implementation preserves immutable bundle revisions. No database or filesystem
layout is selected. `ReconstructionPipeline` only validates and saves artifacts;
source extraction, claim proposal, evaluation, consolidation policy, state
compilation into `CharacterProfile`, and LLM-assisted processors are deferred.

Temporal scope is represented by optional format-neutral labels/intervals. This
keeps point-in-time reconstruction possible without finalizing the research
hypothesis that decomposes a character into persistent structure, historical
adaptations, and dynamic state.

No real character instance or character corpus is part of this implementation.

