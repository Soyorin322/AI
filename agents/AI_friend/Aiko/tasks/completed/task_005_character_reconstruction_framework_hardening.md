# Task 005 — Aiko Character Reconstruction Framework Hardening

Status: Proposed implementation task  
Target: `agents/AI_friend/Aiko/`  
Primary architecture source: `docs/architecture/character_create_v0.0.8.txt`  
Character-specific input: **Forbidden for this task**  
Reirin reconstruction: **Out of scope**

---

# 0. Task Purpose

Task 005 must turn the current Aiko project from a coarse module skeleton into a framework with explicit:

- folder ownership;
- data ownership;
- schema / contract boundaries;
- dependency direction;
- cross-module reference rules;
- validation rules;
- serialization expectations;
- synthetic end-to-end tests.

The purpose is **not** to reconstruct Reirin or any other real character.

The purpose is to make it difficult for a future Codex task to freely invent where data belongs or to skip directly from source text to a final persona.

The required reconstruction direction is:

```text
Canonical Source
    ↓
Source Unit / Observation
    ↓
Event
    ↓
Period Assignment
    ↓
Period Character State
    ↓
Cross-period Development Analysis
    ↓
Compiled Character State
```

Memory and Skills are related but separate:

```text
Event
  ├──→ Memory Formation
  ├──→ Period State Evidence
  └──→ Skill Evidence

Memory
= what the character retains / remembers about experience

Period Character State
= who the character is during a historical period

Character Skill Profile
= what the character is canonically demonstrated to be able to do
```

Task 005 must encode these distinctions into code, documentation, validation, and tests.

---

# 1. Non-goals

Task 005 MUST NOT:

1. read or reconstruct Reirin source material;
2. create `agents/AI_friend/Reirin/`;
3. create any Sakiko / Reirin / other character-specific data under Aiko;
4. invent a final personality scoring formula;
5. invent numeric rules such as `3 observations = high resistance`;
6. turn research hypotheses into mandatory runtime algorithms;
7. implement a full appraisal engine;
8. implement a production vector database;
9. implement a production LLM pipeline;
10. implement actual piano / etiquette / web-search capability packs;
11. create a permanent independent Relationship subsystem while ownership is still unresolved;
12. collapse Event, Memory, Period State, Evidence, Claim, or Compiled State into one object;
13. use reference notes as canonical evidence;
14. introduce a new Character Core dimension beyond the accepted model.

---

# 2. Authoritative Architectural Rules

Task 005 must treat the following as hard constraints.

## 2.1 Framework ≠ Character Data

`agents/AI_friend/Aiko/` contains the generic reusable framework.

It must not contain canonical data for a specific reconstructed character.

Character-specific reconstruction output belongs under:

```text
agents/AI_friend/<Character>/
```

Character source material belongs under:

```text
character_data/<Character>/
```

Dependency direction:

```text
Aiko framework
      ↑ used by
Character instance
```

Aiko MUST NOT depend on a character instance.

---

## 2.2 Single source of truth

The same semantic artifact must not be copied into multiple subsystem folders.

Example:

```text
Event 0042
```

must exist once as an Event record.

Personality, Emotion, Relationship, Growth, Memory, and Skill records may reference `event_0042`, but must not each contain independent copies of the complete Event.

---

## 2.3 Event ≠ Memory ≠ Period Character State

```text
Event
= What happened?

Memory
= What does the character retain / remember / subjectively carry from it?

Period Character State
= Who is the character during this historical period?
```

These objects must use different contracts.

---

## 2.4 Period Character State is the minimum character-analysis unit

A Period State contains the eight Trait Domains:

```text
PeriodCharacterState
├── Personality
├── Physical
├── Motivation
├── Backstory
├── Emotion
├── Relationships
├── Growth
└── Conflict
```

A Period is not automatically a chapter, scene, line range, or fixed token range.

A Period represents a historically coherent interval in which the character state is relatively consistent.

A Period may include many Events.

---

## 2.5 Missing evidence must remain missing

Codex must never fill a domain only because the schema contains that field.

Allowed explicit states must include equivalents of:

```text
unknown
unchanged
insufficient_evidence
not_applicable
```

Exact representation may be selected during implementation, but absence / uncertainty must be machine-readable.

---

## 2.6 Cross-period analysis happens only after Period States exist

Long-term character analysis must be derived from multiple Period States and their evidence.

Development analysis includes representation for:

```text
Trait Change Resistance
Temporal / Historical Context
Historical Accumulation
Causal Formation
Chronic Accessibility
Habitual Processing
Evidence / Provenance
```

These are NOT extra Trait Domains.

They answer:

```text
How and why did the character move from one Period State to another?
```

---

## 2.7 Representation before algorithm

Task 005 may define data structures for:

- change resistance;
- historical accumulation;
- causal hypotheses;
- chronic accessibility;
- habitual processing;
- competing explanations;
- counterevidence.

Task 005 MUST NOT invent a final algorithm that determines these values from arbitrary counts or LLM confidence.

---

## 2.8 Confidence ≠ Change Resistance

The contracts must allow these concepts to remain separate:

```text
confidence
= how strongly the evidence supports the statement

change_resistance
= how resistant the represented character pattern is expected to be to change
```

Validation / documentation must explicitly prohibit using confidence as a substitute for change resistance.

---

## 2.9 Provenance is mandatory for derived character claims

Required logical trace:

```text
Development / Character Claim
        ↓
Period State entry
        ↓
Event / Observation
        ↓
Source Unit
        ↓
Approved Source
```

Reference notes may assist navigation but do not occupy the final canonical evidence position in this chain.

---

## 2.10 Character knowledge is time-bounded

Earlier Period States must not receive:

- future canon knowledge;
- other characters' private knowledge;
- author-only explanations;
- current-state knowledge copied backward.

Contracts must support point-in-time / temporal scope and knowledge boundary metadata.

---

# 3. Repository Ownership Map

Task 005 must document the responsibility of **every existing top-level Aiko folder** and the important package folders under `src/ai_friend/`.

The implementation may add files or narrowly scoped subfolders, but MUST preserve these ownership rules.

---

# 3.1 `agents/AI_friend/Aiko/`

Purpose:

Generic, character-agnostic AI Friend framework, research documentation, contracts, reference material, tests, and reusable capabilities.

MUST contain:

- framework code;
- generic schemas;
- generic interfaces;
- generic validation;
- research / architecture documentation;
- reusable skill definitions;
- synthetic fixtures and tests.

MUST NOT contain:

- Reirin canonical character state;
- Sakiko canonical character state;
- novel-derived character claims;
- character-specific persistent memories;
- character-specific Period files.

---

# 3.2 `Aiko/AGENTS.md`

Purpose:

Instructions and constraints for coding agents working inside Aiko.

Task 005 MUST update this file if required so future Codex runs understand:

- Aiko is character-agnostic;
- source → event → period → development is mandatory;
- character data does not belong in Aiko;
- folder ownership rules;
- no direct source → final persona shortcut;
- no inferred data promotion without evidence;
- no future knowledge leakage;
- no automatic schema filling;
- no external capability knowledge rewriting canon.

`AGENTS.md` is an agent-operation contract, not canonical architecture documentation.

---

# 3.3 `Aiko/README.md`

Purpose:

Human-facing project entry point.

It should briefly state:

- what Aiko is;
- major subsystem boundaries;
- where architecture docs live;
- where reconstruction contracts live;
- how to run tests;
- that real character instances are outside Aiko.

Do not turn README into a duplicate of `character_create_v0.0.8`.

---

# 3.4 `Aiko/pyproject.toml`

Purpose:

Python package metadata, supported Python version, dependencies, test configuration, packaging configuration.

Task 005 should add dependencies only if necessary.

Do not add heavy production dependencies merely to implement schemas.

Prefer standard library / existing project dependencies unless there is a strong reason.

---

# 3.5 `Aiko/characters/`

Purpose:

Generic examples / templates / compatibility fixtures only.

Task 005 MUST explicitly document that this directory is **not the canonical location for real character instances**.

Allowed:

- minimal example character configuration;
- synthetic fixture;
- templates demonstrating framework usage.

Forbidden:

- Reirin reconstruction output;
- Sakiko reconstruction output;
- persistent real character databases.

If the current directory has no active purpose, retain it only as a documented example/template location; do not silently repurpose it.

---

# 3.6 `Aiko/docs/`

Purpose:

Human-readable architecture, research, schema, workflow, and implementation documentation.

Recommended responsibility:

```text
docs/
├── architecture/
│   └── accepted architecture decisions
├── research/
│   └── unresolved / experimental research
├── schemas/
│   └── implementation-facing data contracts
└── reconstruction.md or equivalent
    └── reconstruction workflow overview
```

## `docs/architecture/`

Contains accepted architecture.

Examples:

- `character_create_v0.0.8.txt`
- accepted module boundaries;
- accepted dependency direction;
- accepted Character Model.

MUST NOT present unresolved research hypotheses as final algorithms.

## `docs/research/`

Contains open research questions and candidate models.

Examples:

- evidence-grounded reconstruction;
- temporal character development;
- adaptive reasoning;
- event interpretation research.

Research files may propose models that are not implemented.

## `docs/schemas/`

Purpose:

Precise implementation-facing contract documentation.

Task 005 SHOULD create/update schema documentation for at least:

```text
source / source unit
observation
event
evidence
period
period character state
development
memory
character skill profile
compiled character state
provenance / lineage
```

Schema docs must state:

- field meaning;
- required vs optional;
- allowed reference directions;
- forbidden content;
- temporal semantics;
- uncertainty semantics.

Schema docs are not a storage location for character data.

---

# 3.7 `Aiko/reference/`

Purpose:

Research/reference material used to design Aiko itself.

Allowed:

- papers;
- external framework notes;
- research references;
- citations / summaries used for generic architecture research.

Forbidden:

- character-specific canon;
- Reirin novel excerpts;
- character reconstruction output;
- runtime character database.

A paper in `reference/` informs Aiko design; it does not become a character memory or character evidence record.

---

# 3.8 `Aiko/skills/`

Purpose:

Reusable human-readable skill packages / Agent Skill resources.

This folder is for capability resources such as:

```text
skills/
└── <skill-name>/
    ├── SKILL.md
    ├── references/
    ├── scripts/
    └── assets/
```

Allowed:

- generic piano capability pack;
- etiquette capability pack;
- anime-watching capability pack;
- reusable role-execution instructions if explicitly generic.

Forbidden:

- canonical skill proficiency of a specific character;
- character-specific skill history;
- character-specific acquired proficiency state.

Important distinction:

```text
Aiko/skills/
= capability implementation/resources

CharacterSkillProfile
= character-specific record saying what that character can canonically or later demonstrably do
```

---

# 3.9 `Aiko/tasks/`

Purpose:

Codex implementation tasks and completed task history.

Rules:

- active task files live here according to existing project convention;
- completed tasks move to the existing completed-task location if that convention exists;
- task documents must reference architecture rather than duplicate it unnecessarily;
- Task 005 itself belongs here.

This folder contains work instructions, not runtime data.

---

# 3.10 `Aiko/tests/`

Purpose:

Framework-level tests.

Task 005 MUST add tests covering:

- schema construction;
- reference integrity;
- prohibited reference directions;
- event single-source-of-truth principle;
- period state validation;
- domain uncertainty / missing evidence;
- memory/event separation;
- temporal knowledge boundary;
- development provenance;
- skill canonical/runtime separation;
- synthetic end-to-end reconstruction.

Tests MUST NOT require Reirin source data.

Use a synthetic test character.

---

# 4. Python Package Ownership

Target package:

```text
Aiko/src/ai_friend/
```

Existing package modules must receive explicit ownership.

---

# 4.1 `src/ai_friend/core/`

Purpose:

Small, truly cross-cutting primitives that cannot cleanly belong to one subsystem.

Allowed examples:

- common IDs / identifier helpers;
- immutable shared base types;
- time / version primitives;
- generic result / error primitives.

Do NOT turn `core/` into a dumping ground.

Forbidden:

- personality models;
- Event models;
- Memory models;
- Skill profiles;
- LLM vendor code.

If a type clearly belongs to `character`, `memory`, `reconstruction`, etc., keep it there.

---

# 4.2 `src/ai_friend/reconstruction/`

Purpose:

Generic source-grounded Character Reconstruction pipeline and provenance layer.

It owns the transformation from approved source material into source-grounded intermediate artifacts and period-building inputs.

It SHOULD own or expose contracts for:

```text
SourceReference
SourceUnit
ObservationRecord
EventRecord
EvidenceRecord
Lineage / Provenance
TemporalScope
PeriodAssignment
ReconstructionBundle / Workspace
Reconstruction validation
Reconstruction workflow orchestration
```

Existing Task 003 provenance/evidence foundations should be reused where semantically correct rather than discarded.

## Required responsibilities

### A. Source contract

Represents approved source identity and immutable provenance.

Must support:

- source ID;
- source type;
- path / locator;
- version / blob hash when available;
- approved boundary metadata.

### B. SourceUnit contract

Represents the exact approved source span or an immutable reference to that exact span.

Important:

`SourceUnit` MUST NOT silently become an LLM-generated summary.

If normalized/derived text is useful, it must be explicitly labeled derived.

Preferred semantics:

```text
SourceUnit
├── source_id
├── exact locator
├── verbatim / exact span OR immutable exact-span reference
├── temporal metadata
└── source integrity metadata
```

### C. Observation contract

First derived layer.

Contains source-supported observations.

Must distinguish:

- explicit statement;
- observed action;
- narrator-supported fact;
- uncertainty.

Must not contain final stable personality conclusions.

### D. Event contract

Single source-of-truth experience record.

Should be able to express:

```text
event_id
temporal_scope
participants
objective / observed facts
character-accessible information
explicit statements
observed behavior
outcome
source / observation refs
uncertainty
```

Event is NOT a final trait.

Event must be stored once.

### E. Evidence contract

Links observations/events to bounded hypotheses or state entries.

Must support:

- support / contradiction;
- evidence type;
- source lineage;
- temporal scope;
- uncertainty.

### F. Period assignment contract

Represents which events contribute to which Period and why a boundary exists.

Must allow uncertain / candidate boundaries.

Must not equate Period with chapter automatically.

### G. Reconstruction validation

Must validate:

- reference existence;
- lineage integrity;
- no self-reference;
- no invalid stage skipping where prohibited;
- no future-period dependency into earlier Period State;
- no reference-note promotion as canonical source evidence;
- no character-claim-as-self-evidence circularity.

## `reconstruction/` MUST NOT own

- final runtime context;
- character-specific storage files;
- production memory engine;
- final Capability Skill implementation;
- LLM provider;
- final relationship subsystem;
- fixed psychological scoring formulas.

---

# 4.3 `src/ai_friend/character/`

Purpose:

Generic representation of reconstructed Character State and its longitudinal development.

This folder is the owner of:

```text
Eight Trait Domain definitions
Period Character State
Development representations
Compiled Character State
Character Skill Profile interface/model
Character-state validation
```

## A. Domain definitions

Define the accepted eight domains:

```text
Personality
Physical
Motivation
Backstory
Emotion
Relationships
Growth
Conflict
```

Do not create separate storage folders for each domain.

Domains are typed sections / entries within a `PeriodCharacterState`.

## B. Period Character State

Must represent:

```text
period_id
temporal_scope
supporting_event_ids
knowledge_boundary
8 domains
state-entry provenance
uncertainty / evidence status
```

Each domain entry must be capable of pointing back to evidence / event lineage.

A Period State must support empty / unresolved domains.

## C. Development representation

Must represent cross-period analysis without pretending the analysis algorithm is solved.

At minimum, provide explicit types/interfaces for concepts such as:

```text
TraitHistory / CharacterPattern
ChangeResistance
HistoricalAdaptation
CausalHypothesis
AccessibilityProfile
HabitualProcessingPattern
DevelopmentEvidenceLink
```

Exact class names may differ if justified.

Requirements:

- provenance;
- supporting periods;
- supporting evidence;
- contradicting evidence;
- uncertainty;
- alternative hypotheses where appropriate;
- temporal validity.

No numeric automatic consolidation formula is required.

## D. Compiled Character State

Represents a runtime-friendly consolidated view.

It may include:

```text
current / persistent traits
current period
active beliefs / values / goals
relationship summaries
chronic accessibility
habitual processing
unresolved conflicts
long-term motivations
expression profile references
supporting evidence links
```

It MUST remain traceable to historical Period States.

Compiled State is derived, not new canonical source truth.

## E. Character Skill Profile

Generic character-specific skill-state contract.

Must support:

```text
skill_id
temporal_scope / period
canonical_proficiency
demonstrated behaviors
explicit training/background
limitations
uncertainty
evidence refs
acquisition origin
```

Must distinguish at least conceptually:

```text
canon-supported skill
post-canon learned skill
runtime capability
underlying LLM hidden knowledge
```

## `character/` MUST NOT own

- raw Events;
- complete Memory records;
- world lore database;
- capability-pack implementation;
- LLM API calls;
- perception input;
- character-specific serialized Reirin files inside Aiko.

---

# 4.4 `src/ai_friend/memory/`

Purpose:

Generic Memory subsystem contracts and formation/retrieval interfaces.

Memory answers:

```text
What does the character retain, remember, infer, or carry from experience?
```

It does not own the Event itself.

Task 005 must establish a minimal Memory contract, not a production memory database.

## A. Memory Formation

Represent:

```text
Event
↓
Memory Formation Decision
├── no persistent memory
└── persistent memory
```

No final memory-retention algorithm is required.

Provide an interface / decision result that future implementations can replace.

## B. Memory Record

Minimum semantic content should support:

```text
memory_id
character_id or owner context
event_refs
period_id / temporal scope
remembered_content
subjective_meaning
emotion / affective trace
salience / importance
confidence / uncertainty
retrieval metadata
```

Memory MUST reference Event by ID.

Memory MUST NOT copy the complete objective Event as a second canonical Event object.

## C. Memory Index / retrieval metadata

Support future retrieval by fields such as:

```text
entities
topics
period
importance
time
relationship relevance
```

Do not require a vector DB.

## D. Knowledge boundary

Memory cannot include facts the character did not have access to.

Validation should be able to reject or flag invalid temporal / knowledge references when enough metadata is available.

## E. Retrieval depth

Document the preferred conceptual chain:

```text
Memory Index
↓
Memory Record
↓
Event Record
↓
Source Evidence
```

## `memory/` MUST NOT own

- raw source;
- duplicate Event objects;
- final persistent Character Trait;
- world knowledge packages;
- Capability Skill implementation.

---

# 4.5 `src/ai_friend/knowledge/`

Purpose:

Generic interfaces/contracts for information available to the character.

Knowledge answers:

```text
What information can this character know / access at this point?
```

Examples of future content:

- world lore;
- people / organizations;
- canonical background knowledge;
- imported real-world knowledge;
- technical knowledge packages.

Task 005 only needs to maintain/clarify interfaces and temporal knowledge-boundary compatibility required by reconstruction.

Do not build a production RAG database.

Knowledge ≠ Memory.

Knowledge ≠ Character Core.

Knowledge ≠ Capability Skill.

---

# 4.6 `src/ai_friend/skills/`

Purpose:

Programmatic Skill contracts, registry, profile/capability coordination, and runtime-facing interfaces.

This differs from root `Aiko/skills/`.

```text
Aiko/skills/
= skill resource packages / SKILL.md / scripts / references

src/ai_friend/skills/
= Python interfaces, registry, loading / policy contracts
```

Task 005 should define the boundary between:

```text
CharacterSkillProfile
CapabilitySkill
RuntimeCapability
```

This package may own:

- SkillRegistry interface;
- CapabilitySkill protocol;
- skill availability / policy checks;
- loading metadata.

CharacterSkillProfile itself may live in `character/` because it is persistent character-specific state; if an existing code structure strongly favors another location, document the dependency carefully and avoid duplicate models.

`src/ai_friend/skills/` MUST NOT infer canonical proficiency from the presence of a capability pack.

---

# 4.7 `src/ai_friend/perception/`

Purpose:

Convert real-world / runtime input into typed observations/events.

Examples:

- text;
- audio;
- speech;
- screen;
- image;
- video;
- MIDI;
- system events.

Task 005 does not need to implement multimodal perception.

It must preserve the rule:

```text
Perception
→ typed observation/event
→ Runtime / interpretation
```

Perception MUST NOT directly modify Character State.

---

# 4.8 `src/ai_friend/runtime/`

Purpose:

Coordinator / orchestrator.

Runtime composes the current context from independent subsystems.

It must respect:

```text
Character ──────┐
Knowledge ──────┤
Memory ─────────┤
Skills ─────────┼── Runtime ──> LLM
Perception ─────┘
```

Runtime may select / retrieve / compose.

Runtime must not become the owner of canonical Character, Memory, Knowledge, or Skill data.

Task 005 may define/update context-facing interfaces required to consume `CompiledCharacterState`, but full runtime behavior is out of scope.

---

# 4.9 `src/ai_friend/llm/`

Purpose:

Replaceable LLM provider interfaces/adapters.

Must remain independent from persistent character data.

LLM provider may reason over provided context.

It must not:

- own Character State;
- silently persist Memory;
- infer Skill availability from model knowledge;
- become required by reconstruction schema validation.

Task 005 should avoid vendor-specific expansion unless required for existing tests.

---

# 4.10 `src/ai_friend/bootstrap.py`

Purpose:

Framework composition/bootstrap.

It may wire implementations to interfaces.

It MUST NOT contain character-specific canonical state or hard-coded Reirin/Sakiko configuration.

---

# 4.11 `src/ai_friend/__main__.py`

Purpose:

Minimal CLI / entry point if already used by the project.

Do not turn it into reconstruction business logic.

Business logic belongs in subsystem packages.

---

# 4.12 `src/ai_friend/__init__.py`

Purpose:

Package-level public exports only.

Avoid large implementation logic.

---

# 5. Character Instance Storage Contract

Task 005 must document, but not instantiate, the expected shape for a future character instance.

Recommended:

```text
agents/AI_friend/<Character>/
├── README.md
├── reconstruction/
│   ├── events/
│   ├── periods/
│   ├── development/
│   ├── evidence/
│   └── manifests/
├── memory/
│   ├── records/
│   └── index/
├── character/
│   ├── compiled/
│   └── skill_profile/
└── runtime/
    └── character-specific runtime configuration only if needed
```

Important:

This is a **logical storage recommendation**, not permission to create a Reirin instance in Task 005.

Do not create eight folders under every Period.

Preferred:

```text
period_001.json
{
  "domains": {
    "personality": ...,
    "physical": ...,
    "motivation": ...,
    "backstory": ...,
    "emotion": ...,
    "relationships": ...,
    "growth": ...,
    "conflict": ...
  }
}
```

---

# 6. Source Material vs Character Instance Boundary

Future source data:

```text
character_data/<Character>/
```

Expected conceptual ownership:

```text
sources/raw/
= approved source material

sources/curated/
= source-side transformed / annotated material

sources/curated/reference_notes/
= navigation aid / candidate clue notes; non-canonical as evidence unless revalidated against approved source
```

Future reconstruction must:

```text
reference note
↓ locate
approved source span
↓ verify
SourceUnit
↓ Observation
↓ Event / Evidence
```

Forbidden:

```text
reference note
↓
final Character State
```

---

# 7. Required Data Contracts

Task 005 must implement or refine generic contracts sufficient for the following pipeline.

Exact Python organization may differ if it improves cohesion, but semantics must remain.

## 7.1 Provenance / Source layer

Required concepts:

- `SourceReference`
- `SourceUnit`
- `TemporalScope`
- `Lineage` / provenance reference

Must preserve exact-source traceability.

---

## 7.2 Observation layer

Required concept:

- `ObservationRecord`

Must represent source-supported surface-level observations.

No final trait claims.

---

## 7.3 Event layer

Required concept:

- `EventRecord`

Must represent one source-of-truth event.

Must support character-accessible information separately from story-level/objective information when possible.

---

## 7.4 Evidence layer

Required concept:

- `EvidenceRecord`

Must distinguish at least:

- supports;
- contradicts.

Must carry lineage.

---

## 7.5 Period layer

Required concepts:

- `PeriodDefinition` or equivalent;
- `PeriodBoundary` / candidate boundary representation;
- `PeriodCharacterState`;
- eight Domain sections / typed entries.

Must support:

- source/event refs;
- period order;
- temporal scope;
- knowledge boundary;
- uncertainty;
- incomplete domains.

---

## 7.6 Development layer

Required concepts or equivalent representations:

- character pattern / trait history;
- change resistance;
- historical adaptation;
- causal hypothesis;
- chronic accessibility profile;
- habitual processing pattern;
- supporting / contradicting evidence;
- alternative hypothesis;
- temporal validity.

These contracts must be extensible.

No final psychological scoring algorithm is required.

---

## 7.7 Memory layer

Required concepts:

- `MemoryFormationDecision` or interface;
- `MemoryRecord`;
- memory retrieval/index metadata.

Memory Record must reference Event IDs.

---

## 7.8 Skill layer

Required concepts:

- `CharacterSkillProfile`;
- `SkillEvidence`;
- `CapabilitySkill` interface / protocol;
- `SkillRegistry` or equivalent if compatible with current project design.

Must maintain:

```text
canonical proficiency
≠ runtime capability
≠ underlying LLM knowledge
```

---

## 7.9 Compiled state layer

Required concept:

- `CompiledCharacterState`

Must be derived from Period / Development state.

Must contain evidence links sufficient to trace important compiled elements.

Must not flatten away all historical identity.

---

# 8. Required Reference Direction

Allowed primary direction:

```text
Source
  ↑
SourceUnit
  ↑
Observation
  ↑
Event
  ↑
Evidence / Period state entry
  ↑
Development analysis
  ↑
Compiled Character State
```

Memory:

```text
MemoryRecord
→ Event
→ Observation / SourceUnit
```

Skill:

```text
CharacterSkillProfile
→ Skill evidence
→ Event / source evidence
```

Forbidden circularity examples:

```text
Trait X
→ used to create Evidence X
→ Evidence X proves Trait X
```

```text
Compiled Character State
→ used as canonical evidence for itself
```

A Period State may provide context to interpret a later Event, but that later interpretation must not be retroactively treated as independent evidence for the earlier Period State unless supported by separate evidence.

---

# 9. Validation Rules

Task 005 must implement automated validation where practical.

At minimum:

## IDs / references

- unique artifact IDs;
- referenced artifact exists;
- source unit references approved source;
- no self-reference;
- no impossible parent type.

## Provenance

- derived artifacts have traceable lineage;
- a final / compiled claim cannot exist without lower-level evidence links;
- reference notes cannot masquerade as canonical SourceReference.

## Event

- one Event object per event ID;
- Event cannot directly declare a persistent trait as canonical fact;
- Event temporal scope must be valid.

## Period

- Period IDs / ordering valid;
- Period State references valid events/evidence;
- a Period State can be incomplete;
- earlier Period cannot depend on later-period-only knowledge;
- domain values must distinguish observation / bounded inference where applicable.

## Development

- development claims reference at least one Period;
- causal hypotheses have evidence/provenance;
- causal hypothesis supports alternatives/uncertainty;
- change resistance field must not be auto-derived from confidence by validator/business rule.

## Memory

- Memory references valid Event;
- Memory does not own a second duplicate Event object;
- Memory temporal scope is compatible with Event / acquisition time;
- character-inaccessible facts can be flagged when explicit knowledge-boundary metadata proves conflict.

## Skills

- canonical proficiency requires evidence;
- runtime capability does not automatically increase canonical proficiency;
- underlying LLM capability does not imply CharacterSkillProfile proficiency;
- post-canon learning is distinguishable from canon.

## Stage promotion

If the existing ArtifactStatus / transition model is retained:

- explicit transitions required;
- no implicit candidate → consolidated promotion;
- unresolved remains representable;
- contradiction remains representable.

---

# 10. Serialization Rules

Task 005 must define deterministic, portable serialization for persistent Aiko-owned data.

Requirements:

- JSON support is sufficient for Task 005;
- YAML may be documented as human-editable optional format but must not create a second incompatible canonical schema;
- deterministic key/order behavior where practical for reproducible diffs;
- explicit schema version;
- explicit character/reconstruction version where character-specific later;
- no Python-object-only persistence;
- no third-party framework object as canonical persistent data.

Persistent data must survive replacement of:

- LLM vendor;
- memory engine;
- vector DB;
- capability implementation.

---

# 11. Documentation Deliverables

Task 005 must create/update documentation so a future Codex can locate responsibility without guessing.

At minimum:

```text
docs/
├── architecture/
│   └── keep character_create_v0.0.8 authoritative
├── schemas/
│   ├── reconstruction.md
│   ├── character_state.md
│   ├── memory.md
│   └── skills.md
└── reconstruction.md
```

Exact filenames may follow existing conventions.

Documentation must contain a Folder Ownership Matrix.

Recommended table columns:

```text
Path
Owner responsibility
Allowed data
Forbidden data
Reads from
Referenced by
Persistent?
Character-specific?
```

---

# 12. Synthetic Test Character

Task 005 MUST NOT validate the pipeline using Reirin.

Create a tiny synthetic fixture only under tests / examples.

Required scenario:

```text
Source A
↓
Event 001
Event 002
↓
Period 01

Event 003
↓
candidate boundary
↓
Period 02

Event 002
→ persistent memory

Event 001 + Event 002 + Event 003
→ evidence-linked Period entries

Period 01 + Period 02
→ one development hypothesis

one demonstrated skill
→ CharacterSkillProfile

CompiledCharacterState
→ references Period / development evidence
```

The synthetic data should be intentionally small and artificial.

It must demonstrate:

1. one Event influences multiple Domains without being copied;
2. one Event forms a Memory, another does not;
3. one Domain remains `insufficient_evidence`;
4. a Period boundary is represented;
5. cross-period change is represented without an automatic scoring formula;
6. a causal hypothesis retains uncertainty;
7. canonical skill proficiency remains separate from runtime capability;
8. provenance can be traversed back to Source.

---

# 13. Tests Required

Add tests for at least:

```text
test_source_unit_preserves_source_grounding
test_event_is_single_source_of_truth
test_period_state_has_eight_domain_slots
test_period_allows_missing_domain_evidence
test_period_cannot_use_future_knowledge
test_development_claim_requires_period_or_evidence_links
test_causal_hypothesis_preserves_uncertainty
test_confidence_is_not_change_resistance
test_memory_references_event_without_copying_event
test_memory_can_be_absent_for_event
test_skill_profile_requires_evidence
test_runtime_capability_does_not_rewrite_canonical_skill
test_compiled_state_traces_to_period_state
test_reference_note_is_not_canonical_evidence
test_end_to_end_synthetic_reconstruction
```

Names may vary, but semantic coverage must remain.

Existing Task 003 tests must continue to pass unless a documented contract correction intentionally changes them.

If changed:

- explain why;
- update docs;
- add replacement tests.

---

# 14. Migration / Compatibility with Task 003

Task 003 generic reconstruction work is not automatically invalid.

Task 005 must first inspect existing:

```text
src/ai_friend/reconstruction/
docs/schemas/
docs/reconstruction.md
tests/test_reconstruction.py
```

Reuse where semantically compatible:

- `TemporalScope`
- `SourceReference`
- `SourceUnit`
- `ObservationRecord`
- `EventRecord`
- `EvidenceRecord`
- `Lineage`
- status / transition validation
- provenance validation
- repository / pipeline abstractions

Correct known contract ambiguity:

```text
SourceUnit.content
```

must no longer be semantically free to mean either exact source text or an LLM summary without labeling.

Task 005 must document and enforce a clearer source-grounding contract.

Do not delete Task 003 provenance protections merely because new layers are added.

---

# 15. Dependency Rules

Required high-level dependency direction:

```text
core
↑
reconstruction ──→ character contracts as needed
      │
      ├──→ memory interfaces
      └──→ skill-profile extraction interface

character
memory
knowledge
skills
perception
      ↓
runtime
      ↓
llm
```

Exact Python imports should avoid cycles.

Rules:

- `character` must not call Memory database implementation directly;
- `memory` must not call LLM provider directly;
- `skills` must not write Memory directly;
- `perception` must not modify Character State directly;
- `llm` must not own persistent state;
- `runtime` coordinates subsystem interactions.

Where cross-subsystem data is needed, use typed IDs, immutable value objects, or interfaces rather than direct storage ownership leaks.

---

# 16. Folder Ownership Matrix Required in Codebase

Task 005 completion MUST include a committed matrix covering at least:

```text
Aiko/
Aiko/characters/
Aiko/docs/
Aiko/reference/
Aiko/skills/
Aiko/tasks/
Aiko/tests/

src/ai_friend/core/
src/ai_friend/reconstruction/
src/ai_friend/character/
src/ai_friend/memory/
src/ai_friend/knowledge/
src/ai_friend/skills/
src/ai_friend/perception/
src/ai_friend/runtime/
src/ai_friend/llm/
```

A future Codex should be able to answer:

```text
"I have artifact X. Which folder owns it?"
```

without inventing a new location.

---

# 17. Explicit Artifact Routing Table

Future reconstruction agents must follow this routing.

| Artifact | Generic contract owner | Future character-instance storage |
|---|---|---|
| Source reference | `reconstruction/` | reconstruction manifest / refs |
| Source unit | `reconstruction/` | reconstruction source-unit data if persisted |
| Observation | `reconstruction/` | reconstruction observations |
| Event | `reconstruction/` | `reconstruction/events/` |
| Evidence | `reconstruction/` | `reconstruction/evidence/` |
| Period definition | `reconstruction/` / `character/` boundary | `reconstruction/periods/` |
| Period Character State | `character/` | `reconstruction/periods/` or documented state location |
| Development analysis | `character/` | `reconstruction/development/` |
| Memory record | `memory/` | `memory/records/` |
| Memory index metadata | `memory/` | `memory/index/` |
| Character Skill Profile | `character/` + skill interface | `character/skill_profile/` |
| Capability Skill | `src/ai_friend/skills/` + root skill pack | reusable `Aiko/skills/<skill>/` |
| Compiled Character State | `character/` | `character/compiled/` |
| Runtime context | `runtime/` | ephemeral / runtime cache, not canonical source |
| World / technical knowledge | `knowledge/` | knowledge package/store |
| Perception event | `perception/` | runtime/event ingestion, not canonical source automatically |
| LLM adapter | `llm/` | framework only |

If a future artifact does not fit this table, Codex must not invent a folder silently. It must document the ownership gap first.

---

# 18. Character Reconstruction Stage Gates

Future Codex workflows must be capable of enforcing the following conceptual gates.

## Gate 1 — Source Grounding

Before Observation:

```text
approved source
+
exact source unit / immutable locator
```

## Gate 2 — Event Grounding

Before Event:

```text
source-supported observation
```

## Gate 3 — Period State

Before a Period Domain entry:

```text
Event / Evidence reference
+
temporal compatibility
```

## Gate 4 — Development

Before long-term character conclusion:

```text
Period State evidence
+
historical comparison
+
counterevidence / uncertainty support
```

A single Event may support a bounded Period observation but must not automatically create a stable cross-period trait.

## Gate 5 — Compiled State

Before inclusion in Compiled Character State:

```text
valid Period / Development lineage
+
current temporal validity
```

## Gate 6 — Runtime

Runtime receives a selected view.

Runtime does not redefine canonical history.

---

# 19. Required Guardrails for Future Codex Tasks

Add these rules to implementation docs / agent instructions where appropriate:

1. Reference notes may locate scenes but are not canonical evidence.
2. Return to approved raw / curated canonical source spans before creating evidence.
3. Store an Event once.
4. Do not create one file per Trait Domain per Event.
5. Do not fill missing Domain fields without evidence.
6. Do not infer a persistent trait from one event.
7. Do not confuse evidence confidence with change resistance.
8. Do not declare causal formation without provenance and alternatives.
9. Do not use later-period knowledge in earlier Period reconstruction.
10. Do not promote character skill level beyond demonstrated evidence.
11. Do not allow external technical skill knowledge to rewrite canonical proficiency.
12. Do not make underlying LLM knowledge equal character knowledge.
13. Do not make underlying LLM capability equal character capability.
14. Do not make Memory a duplicate Event store.
15. Do not make Period State a chronological event log.
16. Do not make Character Core a complete world-lore database.
17. Do not make Runtime the owner of persistent character data.
18. Do not add a permanent Relationship subsystem until architecture research resolves ownership.
19. Do not convert research hypotheses into mandatory algorithms without explicit architecture promotion.
20. Preserve unresolved / abstain states instead of fabricating certainty.

---

# 20. Implementation Order

Codex should execute Task 005 in this order.

## Step 1 — Inspect existing implementation

Read:

```text
AGENTS.md
README.md
docs/architecture/character_create_v0.0.8.txt
docs/reconstruction.md
docs/schemas/
src/ai_friend/reconstruction/
src/ai_friend/character/
src/ai_friend/memory/
src/ai_friend/skills/
tests/
```

Identify what Task 003 already implements.

Do not rewrite working provenance code without reason.

## Step 2 — Write ownership documentation first

Before major code changes:

- create/update folder ownership documentation;
- define artifact routing;
- define dependency rules.

This documentation becomes the constraint for implementation.

## Step 3 — Harden reconstruction contracts

Fix SourceUnit semantics.

Extend Event / Evidence / Period assignment contracts.

Preserve provenance validation.

## Step 4 — Implement Period Character State

Add eight-domain state representation.

Add temporal / knowledge boundary fields.

Add incomplete/unknown support.

## Step 5 — Add development representations

Implement extensible data types for:

- trait history;
- resistance;
- historical adaptation;
- causal hypotheses;
- accessibility;
- habitual processing.

No automatic scoring.

## Step 6 — Add Memory contract

Event-ref based MemoryRecord.

Minimal formation decision interface.

Minimal index metadata.

## Step 7 — Add Character Skill Profile contract

Add canonical / post-canon / runtime separation.

Do not implement real skill packs.

## Step 8 — Add Compiled Character State

Derived runtime-facing character representation.

Maintain lineage.

## Step 9 — Add validators

Implement required guardrails.

## Step 10 — Add synthetic fixture and end-to-end tests

No real character data.

## Step 11 — Update README / AGENTS / schema docs

Ensure future Codex runs cannot miss these rules.

---

# 21. Expected Deliverables

Task 005 should result in changes broadly equivalent to:

```text
agents/AI_friend/Aiko/
├── AGENTS.md                         # updated agent constraints
├── README.md                         # updated navigation
├── docs/
│   ├── architecture/
│   │   └── character_create_v0.0.8.txt
│   ├── schemas/
│   │   ├── reconstruction.md
│   │   ├── character_state.md
│   │   ├── memory.md
│   │   └── skills.md
│   └── reconstruction.md
│
├── src/ai_friend/
│   ├── reconstruction/
│   │   └── hardened source/event/evidence/period/provenance contracts
│   ├── character/
│   │   └── domains/period/development/compiled/skill-profile contracts
│   ├── memory/
│   │   └── memory record/formation/index contracts
│   ├── skills/
│   │   └── capability registry/interfaces
│   └── runtime/
│       └── compiled-state consumption interfaces if required
│
└── tests/
    └── synthetic reconstruction contract tests
```

This tree is a responsibility target, not a demand to create one file for every noun.

Prefer cohesive modules over unnecessary file fragmentation.

---

# 22. Acceptance Criteria

Task 005 is complete only when all of the following are true.

### Architecture

- [ ] Every important Aiko folder has documented ownership.
- [ ] Framework data and character-instance data are separated.
- [ ] Root `Aiko/skills/` and Python `src/ai_friend/skills/` have distinct roles.
- [ ] `characters/` is explicitly non-canonical for real character instances.
- [ ] Relationship ownership remains unresolved / non-forced as specified by architecture.

### Reconstruction

- [ ] SourceUnit cannot ambiguously masquerade as an unlabeled LLM summary.
- [ ] Observation, Event, Evidence remain distinct.
- [ ] Event is a single source of truth.
- [ ] Period assignment is explicit.
- [ ] Period State is the minimum character-analysis unit.
- [ ] Eight Domains are represented inside Period State.
- [ ] Missing evidence can remain missing.

### Development

- [ ] Cross-period development types exist.
- [ ] Confidence is separate from change resistance.
- [ ] Causal hypothesis supports uncertainty / alternatives.
- [ ] No arbitrary scoring formula is introduced.
- [ ] Provenance reaches back to source-level records.

### Memory

- [ ] MemoryRecord references Event.
- [ ] Memory is not a duplicate Event store.
- [ ] Memory formation may return no persistent memory.
- [ ] Character-accessible knowledge boundary is represented/documented.

### Skills

- [ ] CharacterSkillProfile exists.
- [ ] canonical proficiency requires evidence.
- [ ] canon skill, post-canon learned skill, runtime capability, and LLM hidden knowledge are distinguishable.
- [ ] capability pack cannot rewrite canonical proficiency.

### Runtime / portability

- [ ] CompiledCharacterState is derived and traceable.
- [ ] Persistent data remains Aiko-owned and vendor-neutral.
- [ ] Runtime coordinates but does not own subsystem data.

### Tests

- [ ] Synthetic end-to-end fixture passes.
- [ ] Existing valid Task 003 tests continue to pass or documented replacements exist.
- [ ] No test requires Reirin/Sakiko data.
- [ ] invalid reference / circularity cases are tested.
- [ ] future-knowledge leakage guard is tested where representable.

---

# 23. Required Final Report from Codex

At completion, Codex must report:

1. exact files added;
2. exact files modified;
3. folder ownership decisions;
4. contracts added/changed;
5. Task 003 contracts reused;
6. Task 003 contracts intentionally changed and why;
7. validators added;
8. tests added;
9. test results;
10. unresolved architecture questions deliberately left unresolved;
11. confirmation that no real character reconstruction was performed;
12. confirmation that no Reirin source material was read or used.

---

# 24. Final Constraint

The success condition is not "more code".

The success condition is:

```text
A future Codex receives source material
        ↓
it cannot reasonably confuse:
Source
Event
Memory
Period State
Development
Skill Profile
Compiled State
        ↓
because Aiko now gives each artifact
one explicit owner,
one explicit contract,
and one validated reference path.
```

Task 005 should make Aiko a **character reconstruction framework**, not merely a collection of folders.

Only after Task 005 is reviewed and accepted should a later task perform the first valid Reirin reconstruction.
