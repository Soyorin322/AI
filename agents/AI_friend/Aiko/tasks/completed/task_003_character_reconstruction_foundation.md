# Task 003 — Implement Aiko Character Reconstruction Foundation for `character_create_v0.0.7`

Status: Ready

## Objective

Bring the **Aiko framework implementation** forward so that it reflects the stable, implementation-ready architecture in the latest accepted architecture document:

```text
docs/architecture/character_create_v0.0.7.txt
```

Task 003 is the bridge between the existing Task 001 / Task 002 framework scaffold and the first real character reconstruction experiment planned for Task 004.

This task must make Aiko capable of supporting the architectural flow:

```text
Source Material
    ↓
Character Reconstruction
    ↓
Persistent Character Data / Reconstructed Character State
    ↓
Character Runtime
```

However, **Task 003 must remain character-agnostic**.

Do not create Reirin, Sakiko, or any other real character instance in this task.

Task 004 will instantiate Reirin only after Task 003 has been reviewed and accepted.

---

# 1. Required Reading and Source of Truth

Before changing code:

1. Read `AGENTS.md` completely.
2. Read the highest-versioned architecture document under `docs/architecture/`; currently this is `character_create_v0.0.7.txt`.
3. Inspect the implementation produced by Task 001 and Task 002.
4. Inspect existing public interfaces, runtime flow, tests, and documentation.
5. Inspect `docs/research/` only when needed to understand terminology already accepted by the architecture.

Use the repository maturity rules:

```text
Research
   ↓
Architecture
   ↓
Schema / Contract
   ↓
Task
   ↓
Implementation
```

Do not treat research-stage hypotheses as finalized schema or algorithms.

When `character_create_v0.0.7.txt` explicitly marks a concept as research, candidate, provisional, unresolved, future, or hypothesis, preserve only the smallest compatible extension point.

---

# 2. Scope Boundary

Task 003 implements the **generic reconstruction foundation**.

Conceptually:

```text
Aiko
│
├── provides reconstruction architecture
│
└── remains character-agnostic
```

Future Task 004 will use it as:

```text
Aiko reconstruction architecture
        ↓
character_data/Reirin
        ↓
Character Reconstruction
        ↓
agents/AI_friend/Reirin
```

Task 003 must NOT cross that boundary.

Do not read or depend on:

```text
character_data/Reirin/
character_data/Sakiko/
agents/AI_friend/Reirin/
agents/AI_friend/Sakiko/ character-specific content
```

Synthetic fixtures may be used in tests.

---

# 3. Preserve Existing Stable Outer Architecture

Do not rebuild Task 001 / Task 002 from scratch.

Preserve the existing stable subsystem responsibilities:

```text
Character
Knowledge
Memory
Perception
Skills
LLM
Runtime / Orchestrator
```

Runtime remains the central coordinator.

The new reconstruction capability must not introduce hidden cross-subsystem orchestration.

In particular:

- Reconstruction must not turn Character into a Memory controller.
- Reconstruction must not let Memory call an LLM directly.
- Reconstruction must not let Perception directly mutate persistent Character state.
- Reconstruction must not let Skills write canonical Character state.
- Reconstruction must not collapse Knowledge and Memory.
- Reconstruction must not place vendor-specific objects into canonical Aiko data contracts.

---

# 4. Add a Dedicated Reconstruction Boundary

Introduce a clear generic architectural home for Character Reconstruction.

Preferred conceptual package:

```text
src/ai_friend/reconstruction/
```

Exact files may differ if a simpler structure better matches the current codebase, but responsibilities must remain explicit.

Recommended minimum responsibilities:

```text
reconstruction/
├── models.py        # Aiko-owned reconstruction contracts
├── interfaces.py    # reconstruction-facing provider / processor contracts
├── provenance.py    # source lineage / traceability primitives
├── validation.py    # generic integrity validation
└── pipeline.py      # minimal orchestration boundary, not a final algorithm
```

Do not add files merely to reproduce this tree if fewer files are clearer.

The important requirement is that Character Reconstruction becomes a first-class framework responsibility rather than being hidden inside `character`, `runtime`, or an LLM prompt.

---

# 5. Minimum Aiko-Owned Reconstruction Contracts

Task 003 should define minimal, typed, framework-owned contracts sufficient to support the accepted v0.0.7 evidence-grounded reconstruction direction.

The implementation should be capable of representing the following conceptual stages without collapsing them into one object:

```text
Source Reference
      ↓
Source Unit / Observation
      ↓
Event
      ↓
Evidence
      ↓
Candidate Claim / Hypothesis
      ↓
Validated / Consolidated Character State
```

Names may differ if repository conventions suggest better names.

At minimum the contracts must preserve these distinctions:

```text
Source != Observation
Observation != Interpretation
Evidence != Claim
Claim != Consolidated Character State
Persistent Character Data != Runtime Context
```

Suggested minimal domain concepts:

```text
SourceReference
SourceSpan or SourceUnit
EventRecord
EvidenceRecord
CharacterClaim
CharacterStateSnapshot or equivalent
```

Do not overdesign these records.

Prefer small typed dataclasses / enums / protocols with generic metadata and extension fields where semantics are still under research.

---

# 6. Provenance Is Mandatory

The architecture requires evidence integrity and traceability.

Task 003 must make it possible for any derived reconstruction artifact to retain lineage to its supporting source material.

At minimum, provenance should be able to identify:

```text
source identity
source location / span / record id
parent derived artifact ids when applicable
```

The design must support a chain such as:

```text
Character Claim
    ↓
EvidenceRecord(s)
    ↓
SourceUnit(s)
    ↓
SourceReference
```

Do not require a database.

Do not require a specific filesystem path format.

Do not assume novel chapter/line semantics because future sources may be subtitles, games, web pages, audio transcripts, images, MIDI, or other media.

Use a generic source locator / metadata model.

---

# 7. Evidence Integrity and Circularity Guards

Task 003 must encode the stable safety rules from `character_create_v0.0.7` at the contract / validator level where practical.

The framework must not silently permit:

```text
behavior
→ inferred trait
→ same trait explains same behavior
→ behavior automatically becomes new proof of the trait
```

Provide lightweight validation that can detect obvious lineage problems, for example:

- a claim with no supporting evidence when support is required;
- an evidence record with no source lineage;
- a derived artifact referencing itself;
- duplicate/self-referential parent chains where detectable;
- invalid references to missing ids in an in-memory reconstruction bundle;
- promotion of unresolved/candidate material to a consolidated state without an explicit status transition.

Do not invent a complete epistemic reasoning engine.

Do not attempt automatic contradiction resolution.

Do not assign psychological confidence formulas that are not defined by architecture.

The goal is to make unsafe data flow structurally visible and testable.

---

# 8. Explicit Status / Maturity of Reconstruction Artifacts

The architecture requires uncertainty, alternative hypotheses, confidence, and abstention to remain possible.

Task 003 should provide a minimal generic status model sufficient to distinguish concepts such as:

```text
observation
candidate
supported
contradicted
unresolved
consolidated
```

Exact enum values are an implementation decision only if they remain generic and minimal.

Do not encode a complex psychology-specific lifecycle.

A candidate claim must not become canonical merely because it is plausible.

The framework should make explicit promotion possible rather than implicit.

---

# 9. Temporal Character State Must Remain Possible

`character_create_v0.0.7` requires preserving historical character development and point-in-time state, while explicitly warning against prematurely treating a character as a stack of unrelated Persona Cards.

Task 003 must therefore make the reconstruction model compatible with:

```text
Character(t)
=
Persistent Structure(t)
+
Historical Adaptations(t)
+
Dynamic State(t)
```

but this formula is still a research hypothesis.

Therefore:

- support point-in-time snapshots / temporal references;
- allow evidence and claims to carry temporal scope when known;
- allow future reconstruction of historical state;
- do NOT finalize the internal decomposition into `Persistent Structure`, `Historical Adaptations`, and `Dynamic State` as mandatory permanent schema unless the latest architecture explicitly promotes it beyond research status;
- do NOT implement trait evolution algorithms.

Use extension points rather than speculative permanent fields.

---

# 10. Character Core Compatibility Without Finalizing Persona Schema

The existing Character implementation is intentionally minimal.

Task 003 must not replace it with a giant finalized Persona object merely to match every concept listed in v0.0.7.

The accepted architecture anticipates concepts including:

```text
Personality
Physical
Motivation
Backstory
Emotion
Relationships
Growth
Conflict
Trait Change Resistance
Historical formation
Expression
```

These are architectural coverage requirements / research directions, not permission to invent a rigid storage schema.

Task 003 should create the minimum boundary that allows reconstruction output to later compile into a runtime-facing Character representation.

Conceptually:

```text
Persistent Reconstruction Artifacts
        ↓
Character State Compiler / Character Provider boundary
        ↓
Runtime-facing CharacterProfile / Character State
```

It is acceptable to keep the existing `CharacterProfile` temporarily if it remains a runtime-facing abstraction.

Do not make `CharacterProfile` itself the canonical reconstruction database.

---

# 11. Reconstruction != Runtime

Keep these responsibilities separate:

```text
Character Reconstruction
= build / refine persistent character representation from source evidence

Character Runtime
= activate the relevant view of that representation during interaction

Event Interpretation
= determine what a current event means to the character
```

Task 003 focuses on Character Reconstruction foundation only.

Do not implement the final Event Interpretation pipeline.

Do not implement runtime appraisal.

Do not implement adaptive reasoning control beyond preserving an extension point if current interfaces require it.

Do not modify Runtime to perform reconstruction during normal conversation.

---

# 12. Progressive Reconstruction Support

The architecture defines the following strategy:

```text
Phase A — Seed Character
Phase B — Representative Event Expansion
Phase C — Coverage Expansion
Phase D — Long-tail Validation
```

Task 003 should support this workflow structurally without hard-coding a single experiment.

At minimum it should be possible to:

- build an initial reconstruction bundle;
- append new evidence / events / candidate claims;
- preserve previous artifacts rather than overwriting source lineage;
- produce a new character-state snapshot/version;
- keep evaluation / holdout material separate from construction material at the caller/configuration level.

Do not implement Reirin's Volume 1–2 / Volume 3 split here.

That belongs to Task 004.

---

# 13. Storage / Persistence Boundary

Task 003 must define interfaces/contracts for persistent reconstructed character data but must NOT choose a production storage engine.

Do not introduce:

```text
SQLite
PostgreSQL
vector database
graph database
ORM
embedding store
cloud database
```

A simple in-memory repository or filesystem-neutral mock is acceptable for tests.

The stable requirement is:

```text
Aiko-owned reconstruction schema
        ↓
replaceable storage implementation
```

not a specific database.

The location of a future real character instance is outside this task.

Task 004 will define how the Reirin instance is generated under `agents/AI_friend/Reirin/`.

---

# 14. LLM Boundary

Do not make Character Reconstruction synonymous with one LLM prompt.

If an LLM-assisted reconstruction interface is needed, define it as a replaceable abstraction.

For example, the framework may later support processors such as:

```text
EventExtractor
EvidenceExtractor
ClaimProposer
ClaimValidator
StateCompiler
```

but Task 003 does not need to implement real LLM-based versions of all of them.

Use deterministic / mock implementations where tests need executable behavior.

Do not integrate OpenAI, Anthropic, Ollama, llama.cpp, or another production provider in this task.

---

# 15. Documentation and Schemas

Because Task 003 introduces implementation-facing reconstruction contracts, update documentation accordingly.

At minimum inspect and update as needed:

```text
docs/architecture.md
docs/character.md
README.md
```

Add a concise reconstruction document if useful, for example:

```text
docs/reconstruction.md
```

If concrete stable data contracts are introduced, document them under:

```text
docs/schemas/
```

in accordance with `AGENTS.md`.

Do not duplicate `character_create_v0.0.7.txt`.

Documentation must clearly state:

- what Task 003 actually implements;
- what remains research-stage;
- reconstruction vs runtime responsibility;
- provenance and evidence boundaries;
- persistent reconstruction data vs runtime character context;
- no real character instance exists yet.

---

# 16. Tests

Preserve all existing tests.

Add focused tests for the new reconstruction foundation.

At minimum validate:

### Provenance

A claim can be traced through evidence to a source reference.

### Separation

Evidence and claims are distinct types and cannot silently substitute for one another.

### Integrity

Missing source lineage / self-reference / invalid references are rejected or surfaced by validation.

### Uncertainty

Candidate or unresolved claims remain representable without being treated as consolidated character state.

### Temporal compatibility

Artifacts can carry a point-in-time / temporal scope without requiring a finalized persona-evolution model.

### Replaceability

A reconstruction repository / store implementation can be replaced behind an interface.

### Runtime isolation

Existing runtime smoke tests still work and Runtime does not need to perform reconstruction during an interaction.

### Character agnosticism

Tests use synthetic characters / sources only.

No test may require Reirin or Sakiko data.

---

# 17. Explicit Non-Goals

Do NOT implement in Task 003:

- Reirin;
- Sakiko;
- any real fictional-character data;
- Volume 1 / Volume 2 / Volume 3 corpus selection;
- a final Persona schema;
- a final eight-domain storage schema;
- automatic trait extraction from novels;
- automatic event extraction from real sources;
- automatic claim generation from real sources;
- final psychological confidence scoring;
- automatic contradiction resolution;
- final relationship schema;
- final expression schema;
- final Event Interpretation pipeline;
- appraisal algorithms;
- chronic-accessibility algorithms;
- habitual-processing algorithms;
- personality evolution algorithms;
- Event -> direct Persona mutation;
- production persistence database;
- RAG;
- embeddings;
- vector database;
- graph database;
- real LLM API;
- local LLM inference;
- GUI;
- web server;
- voice;
- vision;
- MIDI;
- autonomous-agent behavior;
- multi-agent behavior.

Do not implement a research idea merely because it is described in `character_create_v0.0.7.txt`.

---

# 18. Acceptance Criteria

Task 003 is complete only when all applicable criteria are satisfied:

- [ ] Task 001 / Task 002 behavior still works.
- [ ] Aiko remains character-agnostic.
- [ ] A dedicated Character Reconstruction architectural boundary exists.
- [ ] Reconstruction is distinct from Character Runtime and Event Interpretation.
- [ ] Aiko-owned typed contracts can represent source lineage, source units/observations, events, evidence, claims, and reconstructed state/snapshots without collapsing them together.
- [ ] Provenance can trace claims back to source material through evidence.
- [ ] Evidence and claims are explicitly distinct.
- [ ] Candidate / unresolved material is not implicitly canonical.
- [ ] Basic circular/self-reference integrity problems are detectable.
- [ ] Temporal scope / point-in-time reconstruction remains possible.
- [ ] No speculative final Persona evolution schema was introduced.
- [ ] Persistent reconstruction data remains separate from RuntimeContext.
- [ ] Storage is behind an Aiko-owned replaceable contract.
- [ ] No production database/framework/vendor dependency is required.
- [ ] Existing Runtime remains the coordinator for runtime interaction.
- [ ] Runtime does not reconstruct personality during normal request handling.
- [ ] Synthetic tests cover provenance, integrity, uncertainty, temporal compatibility, and replaceability.
- [ ] No tests depend on `character_data/Reirin` or another real character corpus.
- [ ] Documentation describes the implemented reconstruction boundary and deferred research areas.
- [ ] `python -m pytest` passes.
- [ ] `python -m ai_friend` smoke test still passes when applicable.

---

# 19. Validation Before Finishing

Before declaring Task 003 complete:

1. Inspect the final repository tree.
2. Run the complete test suite.
3. Run the executable smoke test.
4. Inspect dependency direction around `reconstruction`, `character`, and `runtime`.
5. Confirm no Reirin/Sakiko imports or data paths were added.
6. Confirm no production storage or LLM dependency was introduced.
7. Verify a synthetic trace:

```text
SourceReference
↓
SourceUnit
↓
EvidenceRecord
↓
CharacterClaim
↓
CharacterStateSnapshot / compiled representation
```

8. Verify that removing or changing a mock store does not require changing the domain contracts.
9. Verify research-stage concepts remain documented as deferred rather than silently finalized.
10. Update docs if implementation differs from documentation.

If any validation cannot be executed, state the exact reason.

---

# 20. Completion Report

When Codex finishes, report:

- repository areas inspected;
- architecture mismatches found relative to `character_create_v0.0.7`;
- files added / changed;
- reconstruction contracts added;
- provenance and validation rules implemented;
- documentation / schema updates;
- tests added or modified;
- validation commands and results;
- existing components intentionally left unchanged;
- research-stage concepts intentionally deferred;
- any deviations from this task and why.

Do not claim Task 003 complete unless the acceptance criteria actually pass.

After Task 003 is complete, **stop**.

Do not begin Task 004 and do not create `agents/AI_friend/Reirin/` until Task 003 has been reviewed and explicitly accepted.
