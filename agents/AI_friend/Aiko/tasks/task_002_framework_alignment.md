# Task 002 — Align Existing Framework with Current Aiko Architecture

Status: Ready

## Objective

Review the existing Aiko framework created by Task 001 and align it with the current repository rules and the latest accepted Aiko architecture.

This is an **alignment task**, not a second bootstrap task.

Preserve working code and existing subsystem boundaries wherever they already satisfy the architecture.

Do not rebuild the framework from scratch.

The goal is to ensure that the current executable skeleton accurately reflects the stable outer architecture described by:

```text
AGENTS.md
+
docs/architecture/latest character_create_v*.txt or .md
```

while leaving unresolved research-stage semantics behind replaceable interfaces and extension points.

---

## Required reading

Before making changes:

1. Read the root `AGENTS.md`.
2. Follow its source-of-truth rules.
3. Read the highest-versioned `character_create_v*.txt` or `.md` under `docs/architecture/`.
4. Inspect the current repository structure and existing Task 001 implementation.
5. Read `docs/architecture.md`, `README.md`, existing tests, and public subsystem interfaces.

Do not use completed task specifications as the current architecture source of truth.

Treat:

```text
AGENTS.md
= persistent development policy

docs/architecture/
= accepted architecture and current design direction

docs/schemas/
= implementation-facing contracts when present

tasks/
= current implementation scope

src/
= current implementation
```

If the current task conflicts with `AGENTS.md` or the latest accepted architecture, follow `AGENTS.md` and the latest architecture and report the conflict.

---

# 1. Core Alignment Target

The existing framework should preserve this stable subsystem structure:

```text
Aiko
├── Character Core
├── Knowledge
├── Memory
├── Perception
├── Skills
├── LLM / Reasoning Engine
└── Runtime / Orchestrator
```

The implementation may use equivalent package names already present in the repository.

Do not restructure working code merely to reproduce this diagram literally.

The stable dependency direction is:

```text
Character ──────┐
Knowledge ──────┤
Memory ─────────┤
Skills ─────────┼──> Runtime / Orchestrator ──> LLM
Perception ─────┘
```

Runtime is responsible for coordination.

Subsystems must not secretly orchestrate each other.

---

# 2. Verify Framework / Implementation / Character Data Separation

Inspect the current code and confirm that the following three layers remain conceptually distinct:

```text
Framework
≠
Module Implementation
≠
Character Data
```

## Framework

Owns:

```text
Runtime
Interfaces / Contracts
Module boundaries
Data flow
Dependency rules
```

## Module implementations

May provide replaceable implementations behind Aiko interfaces.

Examples include current mock or in-memory implementations.

## Character Data

Must remain framework-independent and Aiko-owned.

Do not migrate canonical character data into vendor-specific or framework-specific objects.

If the current implementation already satisfies this rule, leave it unchanged.

---

# 3. Persistent Character Data vs Runtime Context

The architecture must preserve the distinction:

```text
Persistent Character Database
        ≠
Runtime Character Context
        ≠
Static Character Card
```

Task 002 does **not** need to implement a real persistent character database.

It should only ensure that the current architecture leaves a clean boundary between:

```text
persistent / canonical character-facing data
```

and:

```text
temporary RuntimeContext supplied to the LLM
```

Inspect `RuntimeContext` and surrounding code.

If necessary, make the minimum changes required so RuntimeContext is clearly a temporary runtime composition rather than the canonical character store.

Do not implement persistence, retrieval, RAG, or databases in this task.

---

# 4. Character Context Builder / Context Composition Boundary

The current architecture specifies an important stable outer flow:

```text
Character Core ─────┐
Knowledge ──────────┤
Memory ─────────────┤
Role Skill ─────────┤
Capability Skills ──┤
Runtime State ──────┤
Perception ─────────┘
          ↓
Character Context Builder / Context Composer
          ↓
Dynamic Runtime Character Context
          ↓
LLMProvider
```

Task 002 should ensure this responsibility has a clear architectural home.

Do **not** implement advanced retrieval or a final context-selection algorithm.

Acceptable implementations include:

- a small `ContextBuilder` / `ContextComposer` abstraction;
- a focused runtime method or module with one clear responsibility;
- retaining the existing implementation if context construction is already explicit and centralized.

Requirements:

- context composition must not be scattered across Character, Memory, Knowledge, Skills, and LLM modules;
- LLM providers should receive a composed request/context rather than directly reaching into subsystem stores;
- Runtime remains the orchestrator;
- the design must allow future retrieval/context-selection logic to be inserted without rewriting all subsystems.

Do not add abstraction merely for naming if the existing architecture already provides a clean single context-composition boundary.

---

# 5. Stable Replaceable Interfaces

Inspect the current public contracts.

The framework should expose equivalent abstractions for:

```text
CharacterProvider
KnowledgeStore
MemoryStore
SkillRegistry
PerceptionSource
LLMProvider
```

Exact class names may differ if the current implementation is already clear and consistent.

Verify that:

- Runtime depends on abstractions rather than vendor-specific implementations;
- current mock/in-memory implementations remain replaceable;
- external SDK types do not leak into domain contracts;
- replacing an implementation should not require changing canonical Character Data;
- subsystem concrete implementations are not directly coupled to each other.

Do not redesign interfaces that already satisfy these requirements.

---

# 6. Character Core Boundary

Character Core answers:

> Who is this character?

Knowledge answers:

> What information is available to this character?

Memory answers:

> What did this character experience, remember, infer, or learn?

Task 002 should verify that current generic models do not collapse these responsibilities into one object.

However, **do not implement the final Character Core schema in this task**.

The accepted architecture currently anticipates concepts such as:

```text
8 Trait Domains
Trait Change Resistance
Multiple Character Periods
Historical Accumulation
Causal Formation
Expression separation
Dynamic State separation
```

These concepts must remain possible future extensions.

Task 002 may create or preserve appropriate extension points, but must not encode a speculative detailed Persona model merely because these concepts exist in the architecture document.

In particular, do not implement:

- automatic trait extraction;
- Persona consolidation;
- personality evolution;
- fixed change-resistance formulas;
- Sakiko-specific data;
- CharacterGPT-specific storage objects.

---

# 7. Event / Memory / Persona Boundary

Preserve the architectural rule:

```text
Event
    ↓
Memory / interpreted experience / evidence
    ↓
possible later Persona consolidation
```

Never implement:

```text
Event -> direct Persona mutation
```

Task 002 should verify that the current perception/event path does not directly rewrite persistent Character state.

The architecture should remain compatible with a future flow such as:

```text
Objective Event
      ↓
Character Context
      ↓
Subjective Interpretation
      ↓
Emotion / Behavior / Outcome
      ↓
Memory
      ↓
possible Trait Evidence
      ↓
possible controlled Persona Consolidation
```

But this task must **not** implement the final Event Schema, Event Interpretation Pipeline, DREAM-style Event Graph, cognition model, emotion model, or Persona update algorithm.

Those remain later research/implementation tasks.

---

# 8. Knowledge Boundary

Verify that Knowledge remains independent from Memory.

Knowledge represents information available to the character.

Memory represents experiences/history.

Keep the current simple implementation if it already respects this distinction.

Do not implement:

```text
RAG
embeddings
vector retrieval
graph retrieval
hybrid retrieval
external knowledge services
```

No final Knowledge Schema is required in Task 002.

---

# 9. Memory Boundary

Verify that Memory remains a replaceable subsystem and does not invoke the LLM provider directly.

Current simple memory records and in-memory storage may remain unchanged if they satisfy the interface.

Do not implement:

```text
working / episodic / semantic taxonomy as permanent architecture
relationship memory
persona-conditioned insight
memory consolidation
summarization
forgetting
importance scoring
temporal reasoning engine
event graph
Mem0
Letta / MemGPT
TeleMem
DualMem / RoleMemo
```

These are research candidates or later implementation work.

---

# 10. Skills Boundary

The current architecture distinguishes:

```text
Skills
├── Role / Character Execution Skill
└── Capability Skills
```

Task 002 should ensure the generic Skill system does not prevent this distinction.

Do not implement a real character role skill or real capability skill yet.

The existing filesystem `SKILL.md` discovery may remain simple.

Verify that:

- Skills remain separate from Character Core;
- Skills do not directly write Memory;
- the framework can later represent both role-execution instructions and capabilities;
- Skill metadata does not become canonical Persona storage.

Do not implement automatic tool execution, autonomous skill creation, or skill proficiency algorithms.

---

# 11. Perception Boundary

Perception should produce typed observations/events for Runtime.

Conceptually:

```text
Audio / Video / Text / MIDI / System Event
                ↓
            Perception
                ↓
       Typed Observation / Event
                ↓
             Runtime
```

Verify that current `PerceptionEvent` or equivalent:

- is generic;
- supports future modality extension;
- does not depend on a specific recognition provider;
- does not directly mutate persistent Character state.

Do not implement microphone, speech recognition, screen capture, image/video understanding, or MIDI processing.

---

# 12. LLM Boundary

The LLM remains a replaceable reasoning engine, not the character itself.

Verify:

```text
LLM replacement != Character replacement
```

Runtime/domain code should depend on the `LLMProvider` abstraction or equivalent.

The deterministic mock provider may remain unchanged.

Do not integrate any production or local LLM provider in this task.

Do not place canonical Persona, Memory, Knowledge, Relationship, or Skill Profile data inside provider-specific state.

---

# 13. Repository Documentation Alignment

Update documentation only where it is stale or inconsistent with the current accepted architecture.

At minimum inspect:

```text
README.md
docs/architecture.md
docs/character.md
docs/knowledge.md
docs/memory.md
docs/skills.md
docs/perception.md
```

Do not duplicate the full `character_create` document.

`docs/architecture.md` should accurately describe the implemented outer framework, including:

- current subsystem boundaries;
- Runtime as orchestrator;
- replaceable implementations;
- Knowledge vs Memory;
- canonical data vs runtime context;
- context composition boundary;
- current mocks/in-memory implementations;
- explicitly deferred research-stage features.

Keep subsystem documents short if their detailed design has not yet matured.

---

# 14. Tests

Preserve existing tests.

Add or modify tests only where needed to validate alignment changes.

At minimum verify:

### Runtime orchestration

Text input can flow through the existing Runtime to the configured LLM provider.

### Replaceability

At least one provider/store implementation can be replaced without changing Runtime code.

### Context boundary

Runtime context is constructed centrally and passed to the LLM layer without the LLM directly querying subsystem stores.

### Knowledge / Memory separation

Knowledge and Memory remain distinct contracts and stores.

### Perception safety

A perception event can enter Runtime without directly mutating persistent Character state.

### Skills

Skill discovery continues to work.

Do not add tests for deferred research algorithms.

---

# 15. No-op Rule

Do not modify code merely to produce a diff.

If an existing component already satisfies the current architecture, leave it unchanged.

A valid outcome may include:

- no implementation changes;
- documentation-only changes;
- test-only changes;
- a small focused alignment patch.

Avoid large refactors unless a concrete architectural violation requires them.

Do not rename or relocate public modules solely for cosmetic consistency.

---

# 16. Explicit Non-Goals

Do NOT implement in Task 002:

- a real fictional character;
- Sakiko-specific data or behavior;
- final Character Core / Persona schema;
- Persona reconstruction pipeline;
- automatic Persona evolution;
- automatic Persona consolidation;
- Event → Persona mutation;
- final Event Schema;
- final Event Interpretation Pipeline;
- DREAM Event-Aware Memory Graph;
- belief/value/motivation update algorithms;
- emotional appraisal model;
- final relationship model;
- final memory taxonomy;
- long-term memory algorithms;
- embeddings;
- RAG;
- vector databases;
- graph databases;
- persistence database;
- memory consolidation;
- external Persona frameworks;
- external Memory frameworks;
- real LLM APIs;
- local LLM inference;
- speech recognition;
- TTS / voice cloning;
- microphone capture;
- screen capture;
- computer vision;
- video understanding;
- MIDI interpretation;
- piano analysis;
- autonomous agents;
- multi-agent architecture;
- GUI;
- web server;
- mobile application;
- cloud infrastructure.

Do not add third-party frameworks simply because they appear in `character_create` as research candidates.

---

# 17. Acceptance Criteria

Task 002 is complete when:

- [ ] Existing Task 001 functionality remains working.
- [ ] Existing project structure is preserved unless a real architectural issue requires change.
- [ ] Character, Knowledge, Memory, Skills, Perception, LLM, and Runtime remain separate responsibilities.
- [ ] Runtime is the only central orchestrator.
- [ ] Runtime depends on replaceable subsystem contracts.
- [ ] Canonical character-facing data remains independent of vendor/framework-specific schemas.
- [ ] Persistent/canonical data and RuntimeContext remain conceptually separate.
- [ ] Context construction/composition has one clear architectural responsibility.
- [ ] Knowledge and Memory remain distinct.
- [ ] Perception does not directly mutate persistent Character state.
- [ ] Skills do not directly write Memory.
- [ ] Memory does not directly invoke the LLM provider.
- [ ] LLM remains replaceable and is not treated as the character itself.
- [ ] Existing mocks/in-memory implementations remain replaceable.
- [ ] Research-stage Persona/Event/Memory/Relationship semantics were not silently finalized.
- [ ] Documentation accurately reflects the current implementation.
- [ ] Relevant tests pass.
- [ ] No unnecessary external framework or database was introduced.
- [ ] No character-specific assumptions were added.

---

# 18. Validation Before Finishing

Follow the current validation instructions in `AGENTS.md`, `README.md`, `pyproject.toml`, and this task.

At minimum, when applicable:

```powershell
python -m pytest
python -m ai_friend
```

Before declaring completion:

1. Inspect the final repository tree.
2. Run all configured tests.
3. Run the executable smoke test.
4. Review imports around Runtime and subsystem interfaces.
5. Confirm no subsystem reaches into another subsystem's concrete implementation.
6. Confirm context composition remains centralized.
7. Confirm no research candidate was accidentally promoted into permanent architecture.
8. Review dependencies for unnecessary additions.
9. Update documentation if implementation and documentation differ.

If a validation step cannot run, explain exactly why.

---

# 19. Final Response

When finished, report:

- what was inspected;
- actual architectural mismatches found;
- code changes made;
- documentation changes made;
- tests added or changed;
- validation commands executed and results;
- components intentionally left unchanged because they already satisfied the architecture;
- deferred research-stage work;
- any deviations from this task and why.

Do not claim implementation work was necessary if the repository already satisfied a requirement.

Do not claim Task 002 is complete unless the acceptance criteria are actually satisfied.
