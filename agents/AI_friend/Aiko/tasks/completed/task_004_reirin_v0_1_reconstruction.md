# Task 004 — Build Reirin v0.1 from Volume 1–2

Status: Ready

## Objective

Use the Character Reconstruction foundation completed in Task 003 to create the first real reconstructed AI Friend instance:

```text
character_data/Reirin
        ↓
Aiko Character Reconstruction
        ↓
agents/AI_friend/Reirin
```

Task 004 uses **Volume 1 and Volume 2 only** as the reconstruction corpus.

The goal is not to summarize the novels into a character card. The goal is to create an evidence-grounded, provenance-preserving first reconstruction of Reirin that conforms to Aiko-owned contracts.

Volume 3 is deliberately excluded from this task and must remain unread and unused until Task 004 has been completed and reviewed.

---

# 1. Required Reading

Before making changes:

1. Read `agents/AI_friend/Aiko/AGENTS.md` completely.
2. Read the latest architecture under `agents/AI_friend/Aiko/docs/architecture/`, currently `character_create_v0.0.7.txt`.
3. Read `agents/AI_friend/Aiko/docs/reconstruction.md`.
4. Read `agents/AI_friend/Aiko/docs/schemas/reconstruction.md`.
5. Inspect the Task 003 implementation under `agents/AI_friend/Aiko/src/ai_friend/reconstruction/`.
6. Inspect the current `character_data/Reirin/README.md` only for source-side ownership rules.
7. Inspect the current `agents/AI_friend/` layout and preserve the dependency direction defined in `AGENTS.md`.

Task 004 must use Aiko as the reusable framework. It must not turn Aiko into Reirin.

---

# 2. Frozen Reconstruction Corpus

The only canonical reconstruction sources permitted in Task 004 are:

```text
character_data/Reirin/sources/raw/novel/惡女不才_第一卷_speaker重校.md
character_data/Reirin/sources/raw/novel/惡女不才_第二卷_speaker重校.md
```

At the time Task 004 is authored, their Git blob SHAs are:

```text
Volume 1: 4a6109af0305c9d12c14f81862df15c18bb92c67
Volume 2: 8fcfebd854639c8ec4d42b98ff17810d69d907fe
```

These two speaker-rechecked files are the user-approved reconstruction raw inputs for this experiment.

Some embedded header text may still describe them as an earlier draft or recommend preserving another original file. For Task 004, follow the current repository/task ownership decision: the speaker-rechecked Volume 1–2 files above are the authoritative reconstruction inputs.

Do not rewrite the novel source files merely to update their old header wording.

If either source blob SHA differs before reconstruction begins, report the difference in the completion report and record the actual SHA used in the manifest.

---

# 3. Volume 3 Hard Isolation Rule

Task 004 must NOT read, parse, summarize, search, inspect, import, compare against, or otherwise use:

```text
character_data/Reirin/sources/raw/novel/惡女不才_第三卷_speaker重校.md
```

Current blob SHA for the excluded file:

```text
eee247343ae40966f8e5161ad3ed8dc8bdad931b
```

Volume 3 is reserved for the next stage after Task 004 review.

This is a hard anti-leakage rule.

Do not use Volume 3 to:

- validate claims;
- choose better interpretations;
- fill missing background;
- correct relationships;
- infer future character development;
- decide which Volume 1–2 evidence is important;
- improve Reirin v0.1 after seeing later canon.

Task 004 should leave enough metadata that a later task can prove Reirin v0.1 was constructed from Volume 1–2 only.

---

# 4. Ownership and Dependency Direction

Preserve the repository rule:

```text
Aiko
 ↑
 │ uses
Reirin instance
```

Meaning:

```text
agents/AI_friend/Reirin
```

may depend on Aiko-owned contracts, while:

```text
agents/AI_friend/Aiko
```

must not import, depend on, or hard-code Reirin-specific code/data/paths.

The intended data flow is:

```text
character_data/Reirin
        ↓ source material
Aiko reconstruction contracts
        ↓
agents/AI_friend/Reirin
```

Do not store Reirin-specific reconstruction results inside Aiko.

Do not use `character_data/Reirin/data/` as the canonical Reirin instance output. That directory is not the reconstructed AI Friend instance.

---

# 5. Create `agents/AI_friend/Reirin/`

Create the first Reirin instance under:

```text
agents/AI_friend/Reirin/
```

Use a small, inspectable structure. A recommended starting layout is:

```text
agents/AI_friend/Reirin/
├── README.md
├── reconstruction/
│   ├── manifest.json
│   ├── bundle_v0.1.json
│   └── reconstruction_report.md
└── tests/
    └── ...
```

You may add a minimal loader/validator module if needed to map the committed JSON representation into Aiko Task 003 dataclasses.

Do not create a large independent framework inside Reirin.

Do not duplicate Aiko subsystem implementations.

Do not create Reirin-specific replacements for Memory, Runtime, Knowledge, LLM, Perception, or Skills merely to make the directory look complete.

Task 004 is primarily a reconstruction-instance task.

---

# 6. Reconstruction Manifest

Create a machine-readable manifest that freezes the experiment boundary.

At minimum it must record:

```text
character_id
character_name
reconstruction_version
Aiko architecture / reconstruction contract version or commit reference
included source paths
included source blob SHAs
excluded Volume 3 path / status
construction timestamp if appropriate
source language / work metadata where useful
notes about speaker verification status
```

The manifest must make it unambiguous that:

```text
Reirin v0.1 = Volume 1 + Volume 2 only
```

Do not place psychological claims in the manifest.

---

# 7. Preserve Identity vs Body State

This work contains body swapping. Reconstruction must distinguish **character identity** from **current body / surface identity**.

When source text labels:

```text
玲琳（身體：朱慧月）
```

this remains evidence about the person Reirin / 玲琳 while explicitly recording that the current body is Keigetsu / 朱慧月.

Do not accidentally reconstruct two different people merely because the body changed.

Likewise do not attribute Keigetsu's behavior to Reirin merely because Keigetsu is in Reirin's body.

Use generic source metadata / event metadata where needed to preserve this distinction without changing Aiko's generic reconstruction schema.

---

# 8. Source Unit Strategy

Do not treat the entire novel volume as one SourceUnit.

Do not mechanically create one CharacterClaim per dialogue line.

Create addressable source units at a granularity that preserves local context and provenance.

Preferred approach:

```text
Volume
  ↓
Chapter / section
  ↓
Scene / narrative unit
  ↓
addressable source units
```

A SourceUnit may represent a dialogue passage, narration passage, or compact scene-local block when that is the smallest useful evidence context.

Requirements:

- preserve source file identity;
- preserve a stable locator back to the novel source;
- preserve enough surrounding context to interpret the unit;
- do not strip speaker labels that are relevant to attribution;
- do not convert interpretation into source text;
- do not depend on brittle absolute line numbers alone if a more stable locator can also be recorded.

The task does not require every sentence in both novels to become its own source unit. Prefer meaningful, traceable coverage over maximal fragmentation.

---

# 9. Event Reconstruction

Volume 1–2 together form the first complete major story event used for Reirin reconstruction.

Segment them into objective narrative events / subevents before generating character claims.

Each `EventRecord` should describe what occurred without silently embedding Reirin's inferred psychology.

Prefer:

```text
objective / observable event
participants
relevant source lineage
temporal / scene scope
```

Avoid objective event descriptions such as:

```text
Reirin bravely decides...
Reirin compassionately helps...
Reirin proves that she values...
```

when `bravely`, `compassionately`, or `proves that she values` is already interpretation.

Keep:

```text
Event
!=
Character interpretation
!=
Character claim
```

Do not implement the final Event Interpretation / appraisal engine in this task.

---

# 10. Observation and Evidence Extraction

Use observations to record what the source supports directly or near-directly.

Evidence must remain traceable to source material through Task 003 lineage rules.

Evidence may include, for example:

```text
observable behavior
explicit dialogue
explicitly stated thought
explicit narrator statement
repeated response pattern
relationship behavior
choice under conflict
response under hardship
```

Do not present inferred internal motives as observations unless the source explicitly states them.

If the text supports multiple plausible interpretations, preserve ambiguity rather than selecting one merely because it sounds psychologically coherent.

---

# 11. Claim Reconstruction

Create a first set of evidence-grounded CharacterClaims for Reirin.

Claims should describe character-relevant reconstructed state such as candidate or supported:

```text
personality tendencies
values
beliefs
motivations / priorities
coping tendencies
interpersonal tendencies
relationship-specific tendencies
important conflicts
relevant background effects
repeated behavioral patterns
```

Do not force every v0.0.7 conceptual domain to contain data.

Do not invent a final eight-domain Persona schema.

Do not produce a static prose biography and call it the Character Core.

Each important claim must preserve:

```text
claim
status
supporting evidence lineage
contradicting evidence lineage when present
temporal scope when relevant
```

Use Task 003 maturity states honestly:

```text
candidate
supported
contradicted
unresolved
consolidated
```

Plausibility is not enough for consolidation.

---

# 12. Consolidation Policy for Reirin v0.1

Task 004 may consolidate claims only when Volume 1–2 provide sufficiently clear support.

The consolidation decision must be auditable.

For each consolidated claim:

- preserve the supporting evidence IDs;
- preserve counterevidence or exceptions when materially relevant;
- record an explicit `supported -> consolidated` transition;
- do not use the claim itself to generate new evidence for itself;
- do not use another claim as evidence;
- do not use Volume 3.

If a psychologically attractive explanation lacks enough evidence, keep it `candidate` or `unresolved`.

A smaller reliable v0.1 is preferred over a larger speculative personality model.

---

# 13. Contradictions and Exceptions

Do not flatten Reirin into one-dimensional traits.

When Volume 1–2 show apparently conflicting behavior:

1. preserve both observations;
2. examine event / relationship / temporal context;
3. record contradicting evidence where appropriate;
4. refine the claim if the source supports a contextual distinction;
5. otherwise leave the claim unresolved.

Do not resolve contradictions by inventing hidden motives.

Do not treat one exception as automatically disproving a general tendency, and do not ignore exceptions to protect an attractive trait hypothesis.

---

# 14. Temporal Reconstruction

Use `TemporalScope` where Volume 1–2 support meaningful time/period distinctions.

The character at the beginning of Volume 1 and at the end of Volume 2 need not be represented as identical static state.

However, do not finalize a speculative personality-evolution algorithm.

Task 004 should preserve enough temporal information to later reconstruct:

```text
point-in-time Reirin state
```

without forcing all character development into unrelated Persona Cards.

At minimum, the final snapshot should explicitly represent the reconstruction boundary:

```text
Reirin v0.1
point in time: end of Volume 2
source knowledge boundary: Volume 1–2 only
```

---

# 15. Build Reirin v0.1 Snapshot

Produce at least one validated `CharacterStateSnapshot` representing the first consolidated Reirin reconstruction at the end of Volume 2.

The snapshot must depend only on consolidated claims.

Do not invent a final runtime `CharacterProfile` schema merely because Task 003 snapshots are intentionally thin.

Task 004 should treat the snapshot plus its consolidated claims and lineage as the canonical v0.1 reconstruction result.

Runtime compilation can remain a later step unless a minimal adapter is strictly required to validate the instance.

---

# 16. Machine-Readable Bundle

Persist the Reirin reconstruction in a deterministic, inspectable machine-readable representation under `agents/AI_friend/Reirin/reconstruction/`.

Preferred format:

```text
bundle_v0.1.json
```

It should map cleanly to the Aiko Task 003 dataclasses:

```text
SourceReference
SourceUnit
ObservationRecord
EventRecord
EvidenceRecord
CharacterClaim
CharacterStateSnapshot
ReconstructionBundle
Lineage
TemporalScope
StatusTransition
```

Do not invent an unrelated Reirin-only schema when the Aiko contract is sufficient.

If serialization helpers are needed, keep them minimal and reusable where appropriate.

Do not introduce a database.

---

# 17. Human-Readable Reconstruction Report

Create a concise report, for example:

```text
agents/AI_friend/Reirin/reconstruction/reconstruction_report.md
```

The report should summarize:

- source boundary used;
- event / source-unit segmentation strategy;
- number of source units, events, evidence records, claims, and snapshots;
- consolidated vs candidate/unresolved/contradicted claim counts;
- major reconstructed dimensions actually supported by Volume 1–2;
- important contradictions / uncertainty retained;
- known limitations of Reirin v0.1;
- confirmation that Volume 3 was not used.

Do not copy large portions of the novel into the report.

---

# 18. No Character-Style Circularity

Do not use a partially reconstructed Reirin personality to decide who spoke a line, what a source passage says, or whether an observation occurred.

Speaker attribution for Task 004 comes from the user-approved speaker-rechecked source files.

The direction must remain:

```text
Source
↓
Observation / Event
↓
Evidence
↓
Claim
```

Never:

```text
Claim
↓
"this sounds like Reirin"
↓
new evidence for the same claim
```

---

# 19. Aiko Modification Rule

Task 004 should primarily add the Reirin instance.

Do not modify Aiko just because a Reirin-specific convenience would be useful.

If Task 004 discovers a genuine generic blocker in the Task 003 reconstruction foundation:

1. confirm that the missing capability is character-agnostic;
2. make the smallest reusable change in Aiko;
3. add/update Aiko synthetic tests;
4. do not introduce Reirin imports or paths into Aiko;
5. report the generic framework change separately in the completion report.

Do not hide framework fixes inside `agents/AI_friend/Reirin/`.

---

# 20. Tests and Validation

Add tests sufficient to verify the committed Reirin reconstruction can be loaded and validated against Aiko Task 003 contracts.

At minimum verify:

### Corpus boundary

- manifest includes Volume 1 and Volume 2;
- manifest does not include Volume 3 as a reconstruction source;
- no Reirin v0.1 artifact lineage references Volume 3.

### Provenance

- consolidated claims trace to evidence and permitted sources;
- evidence traces to Volume 1–2 source units.

### Identity/body distinction

- body-swap metadata does not change Reirin identity.

### Integrity

- `validate_bundle()` accepts the final bundle;
- no claim-as-evidence or snapshot-as-evidence circularity exists;
- all snapshot claim parents are consolidated.

### Serialization

- committed machine-readable artifacts load deterministically into Aiko-owned contracts.

### Aiko isolation

- Aiko does not import Reirin-specific modules/data.

When applicable run:

```powershell
python -m pytest
python -m ai_friend
```

Also run any Reirin-specific validation command introduced by this task.

---

# 21. Explicit Non-Goals

Do NOT implement in Task 004:

- Volume 3 analysis;
- Volume 3 validation;
- Volume 3 holdout prediction;
- Sakiko;
- a production conversational Reirin runtime;
- a final Character Core / Persona schema;
- a final relationship schema;
- a final emotion model;
- a final appraisal / Event Interpretation engine;
- automatic personality evolution;
- live memory consolidation;
- embeddings;
- RAG;
- vector database;
- graph database;
- production database;
- external LLM API integration;
- local LLM inference runtime;
- TTS;
- voice cloning;
- vision;
- screen capture;
- MIDI;
- piano skills;
- autonomous behavior;
- multi-agent behavior.

Do not expand Task 004 into the complete final Reirin system.

The output is **Reirin Reconstruction v0.1**, not the final runtime character.

---

# 22. Acceptance Criteria

Task 004 is complete only when:

- [ ] `agents/AI_friend/Reirin/` exists as a character-specific instance directory.
- [ ] Reirin depends on Aiko contracts; Aiko does not depend on Reirin.
- [ ] The reconstruction manifest freezes Volume 1–2 as the only construction corpus.
- [ ] Volume 3 was not read or used.
- [ ] Source units are addressable and traceable to Volume 1–2.
- [ ] Objective events are separated from psychological interpretation.
- [ ] Observations are separated from claims.
- [ ] Evidence is separated from claims and has source lineage.
- [ ] Claims preserve uncertainty and contradictory evidence where needed.
- [ ] Consolidated claims have explicit supported-to-consolidated transitions.
- [ ] Reirin identity remains distinct from body state during swaps.
- [ ] At least one end-of-Volume-2 Reirin v0.1 snapshot exists.
- [ ] The snapshot references only consolidated claims.
- [ ] The final machine-readable bundle passes Aiko `validate_bundle()`.
- [ ] The reconstruction artifacts can be loaded deterministically.
- [ ] A human-readable reconstruction report exists.
- [ ] No final speculative Persona schema was invented.
- [ ] No production storage / LLM / RAG dependency was introduced.
- [ ] Existing Aiko tests still pass.
- [ ] Reirin-specific validation tests pass.

---

# 23. Completion Report

When finished, report:

- source files and exact blob SHAs actually used;
- confirmation that Volume 3 was not read or used;
- Reirin directory structure created;
- segmentation strategy;
- artifact counts by type;
- claim status counts;
- final snapshot id/version/time boundary;
- important uncertainty and contradictions retained;
- generic Aiko changes, if any, and why they were necessary;
- tests and validation commands executed with results;
- known limitations of Reirin v0.1;
- any deviations from this task and why.

After Task 004 is complete, stop.

Do not begin using Volume 3 until Task 004 has been reviewed and explicitly accepted.
