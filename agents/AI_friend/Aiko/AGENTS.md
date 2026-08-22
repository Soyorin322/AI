# Aiko development rules

## Project intent

Aiko (`ai-friend`) is a modular framework for persistent AI characters.

The framework must remain:

- character-agnostic
- LLM-provider-agnostic
- storage-engine-agnostic
- replaceable at subsystem boundaries
- able to preserve character data across implementation changes

Aiko owns the character. External technologies provide capabilities.

---

## Source of truth

For architectural work, first inspect:

```text
docs/architecture/
```

Use the highest-versioned `character_create_v*.txt` or `character_create_v*.md` in that directory as the current architecture and research specification.

Do not search outside the Aiko project directory for an architecture source unless the task explicitly provides one.

Treat older `character_create` versions as historical references only.

Do not silently convert research ideas, candidate technologies, examples, or future directions into finalized architecture.

If a requirement is described as any of the following:

- research
- candidate
- future
- possible
- provisional
- unresolved
- to be decided
- needs further study

preserve an extension point instead of choosing a permanent implementation.

When the latest architecture document conflicts with older implementation assumptions, prefer the latest architecture document unless the user explicitly requests otherwise.

---

## Architecture maturity rule

Use the following implementation policy.

### Stable architecture — implement

The following principles are considered stable unless the architecture document explicitly changes them:

- Framework != Module Implementation != Character Data
- Persistent Character Database != Runtime Character Context
- Character Data must use Aiko-owned schemas
- Runtime is the coordinator / orchestrator
- Subsystems communicate through explicit contracts
- Implementations must be replaceable behind interfaces
- Knowledge and Memory are separate responsibilities
- Perception produces observations/events but does not directly mutate Character state
- Skills do not directly write Memory
- Memory does not directly call the LLM provider
- Character does not directly manipulate Memory storage
- External frameworks must be isolated behind adapters or migration layers

### Research-stage semantics — interface first

For concepts that are still being researched, prefer:

- `Protocol`
- abstract base classes
- typed contracts
- minimal dataclasses
- placeholders
- mocks
- stubs
- TODO markers linked to the relevant research area

Do not invent a detailed algorithm merely to make the architecture look complete.

Examples of research-stage areas may include:

- final Persona schema
- trait evolution rules
- Event interpretation
- character-specific appraisal / subjective cognition
- perspective / knowledge boundary
- Memory lifecycle
- Relationship model
- Knowledge retrieval strategy
- Skill proficiency model
- belief/value update
- emotion modeling
- causal character formation

### Unspecified implementation choices — do not decide automatically

Do not choose or introduce any of the following unless the task explicitly requires it:

- vector database
- graph database
- ORM
- persistence database
- embedding provider
- LLM vendor
- local model runtime
- persona framework
- memory framework
- agent framework
- workflow framework

If a minimal implementation is required, prefer a simple local or in-memory implementation behind the appropriate interface.


---

## Research → Architecture → Schema → Task maturity flow

Research findings are not automatically approved architecture.

Use the following maturity flow:

```text
docs/research/
    ↓
research evidence, paper notes, experiments, candidate ideas

docs/architecture/
    ↓
accepted architectural decisions and current design direction

docs/schemas/
    ↓
implementation-facing contracts and data definitions

tasks/
    ↓
explicit Codex implementation scope
```

Rules:

- Files under `docs/research/` are evidence and exploration, not implementation authority.
- Do not implement a research paper, GitHub project, or experiment merely because it exists under `docs/research/`.
- A concept should normally move into `docs/architecture/` before it becomes a stable architectural requirement.
- A data structure should normally move into `docs/schemas/` before Codex treats it as an implementation contract.
- `tasks/` defines what should be implemented now; it does not redefine the whole architecture.
- Completed task specifications are implementation history, not the current source of truth.
- If a task requests behavior that has not matured beyond research-stage status, implement only the smallest compatible interface or placeholder unless the user explicitly approves the design.

Prefer:

```text
Research
   ↓
Architecture decision
   ↓
Schema / contract
   ↓
Task
   ↓
Implementation
```

Avoid:

```text
Research paper
   ↓
direct permanent implementation
```

---

## Canonical data ownership

Persistent character data must remain independent of third-party frameworks.

Do not use vendor/framework-specific objects as canonical storage for:

- identity
- persona
- timeline
- relationships
- memories
- knowledge
- expression
- evidence
- skill profile

Third-party integrations must use:

```text
Aiko-owned contract
        ↓
Adapter / migration layer
        ↓
External implementation
```

Removing an external dependency should not require redefining what the character is.

---

## Framework and character-instance dependency direction

Aiko is the reusable, character-agnostic framework and reconstruction architecture. A concrete AI Friend instance may use Aiko-owned contracts and framework capabilities, but Aiko must never depend on that concrete character instance.

The dependency direction must remain:

```text
Aiko
 ↑
 │ uses
Character Instance
```

For example:

```text
Aiko
 ↑
 │ uses
Reirin instance
```

This means the concrete character instance depends on Aiko; Aiko does not import or depend on Reirin-specific code, schemas, paths, data, or assumptions.

Never create a bidirectional dependency such as:

```text
Aiko ↔ Reirin
```

Rules:

- Character-specific code may depend on stable Aiko-owned interfaces and contracts.
- Aiko must not import from `agents/AI_friend/<Character>/`.
- Aiko must not hard-code paths under `character_data/<Character>/`.
- Character-specific fixes must not be added to Aiko unless they represent a genuinely reusable framework requirement.
- Missing generic framework capability should be implemented in Aiko first rather than patched only inside one character instance.
- Reconstruction methods and reusable architecture belong to Aiko; character-specific reconstruction results belong to the concrete character instance.

The intended ownership flow is:

```text
character_data/<Character>
        ↓
Aiko Character Reconstruction
        ↓
agents/AI_friend/<Character>
```

---

## Runtime and dependency direction

Runtime coordinates subsystem interaction.

Preferred direction:

```text
Character ──────┐
Knowledge ──────┤
Memory ─────────┤
Skills ─────────┼──> Runtime / Orchestrator ──> LLM
Perception ─────┘
```

Do not create hidden cross-subsystem orchestration.

In particular:

- Character must not directly operate the Memory database.
- Memory must not directly invoke the LLM provider.
- Perception must not directly mutate persistent Character state.
- Skills must not directly write Memory.
- Knowledge must not become an alias for Memory.
- Adapters must not leak vendor-specific types into domain interfaces.

Dependency inversion is preferred over direct concrete imports.

---

## Event and character-evolution safety

Do not implement the assumption:

```text
Event -> direct Persona mutation
```

The current architectural direction treats events as interpreted experiences that may produce observations, memories, knowledge, relationship effects, emotional state, or Persona evidence.

Persistent Persona change must remain a separate controlled process.

Until the relevant research is finalized, model this with contracts such as:

```text
Event / Observation
        ↓
Character-specific Interpretation / Appraisal
        ↓
Emotion / Intention / Behavior
        ↓
Evidence / subsystem updates
        ↓
Optional controlled consolidation
```

Do not hard-code a specific personality-update algorithm unless explicitly requested.

Do not hard-code generic event-to-reaction rules such as:

```text
Event X -> Emotion Y
Event X -> Behavior Y
```

The same external event may produce different interpretations, emotions, intentions, and behavior for:

- different characters;
- the same character at different life periods;
- the same character with different prior memories;
- the same character under different relationship or psychological states.

Preserve the interpretation / appraisal layer as a research-stage extension point. Do not permanently select a specific appraisal theory, emotion model, or cognitive architecture unless the architecture or task explicitly approves it.

---

## Character-specific cognition and perspective safety

Aiko must not operate a character merely by matching static persona traits to likely dialogue.

The intended reasoning direction is:

```text
Event / Observation
        +
Point-in-Time Character State
├── accessible knowledge
├── relevant prior memory
├── beliefs / values
├── goals / motivation
├── relationship state
├── conflict
└── dynamic psychological state
        ↓
Subjective Interpretation / Appraisal
        ↓
Emotion / Intention / Decision / Behavior
```

The central runtime question should be conceptually closer to:

> Given what this character currently knows, remembers, believes, values, fears, wants, and feels, what does this event mean to this character?

rather than:

> What would a character with these traits probably do?

### Same event, different meaning

Do not assume identical events imply identical subjective experiences.

Conceptually:

```text
Same Event
+
Character State A
        ↓
Interpretation A

Same Event
+
Character State B
        ↓
Interpretation B
```

This also applies to different periods of the same character.

A point-in-time character state is not merely a cosmetic profile selector. It represents a historically accumulated state shaped by prior experiences, beliefs, relationships, conflicts, motivations, and psychological context.

When causal history is available, later character periods should preserve continuity with earlier periods rather than being modeled as unrelated replacement profiles.

### Knowledge boundary / no omniscient leakage

Character reasoning must respect point-in-time information access.

Do not automatically expose the character to:

- future canonical events;
- narrator or author knowledge;
- audience-only information;
- another character's private thoughts or memories;
- hidden world state the character has not perceived or learned;
- later-period knowledge while simulating an earlier period.

Preserve the distinction:

```text
Story / Canon Truth
        ≠
Character-accessible Knowledge
        ≠
Character Belief
        ≠
Character Inference
```

Runtime context selection should prefer only information the current character could reasonably access at that time unless a task explicitly requests an omniscient or analytical mode.

### Canonical evidence vs inferred cognition

Do not silently convert model-generated interpretation into canonical character data.

Preserve provenance distinctions such as:

```text
Canonical Evidence
        ↓
Extracted Character State
        ↓
Inferred Character Cognition / Appraisal
        ↓
Predicted Emotion / Intention / Behavior
```

An inferred cognition may be highly plausible and useful for runtime reasoning while still remaining an inference.

If an interpretation is not directly supported by source material, do not label it as canonical fact merely because the LLM generated it consistently.

Schema and storage design should preserve enough provenance to distinguish:

- directly observed / canonical evidence;
- extracted or consolidated character state;
- inferred subjective interpretation;
- predicted response;
- later confirmed or contradicted interpretation.

### Character Core responsibility

Character Core should provide persistent and point-in-time character state needed for character-specific reasoning.

It should not be reduced to a static checklist such as:

```text
proud
responsible
elegant
stubborn
cares about friends
```

Traits are inputs to interpretation, not complete behavioral rules.

Conceptually:

```text
Character Core + Memory + Relationship + Knowledge Boundary + Dynamic State
        ↓
Interpretation / Appraisal Process
        ↓
Character-specific Meaning
```

Character Core does not need to permanently own the appraisal algorithm.

The appraisal / interpretation process may remain a Runtime or dedicated cognition-layer responsibility as long as subsystem boundaries remain explicit and replaceable.


---

## Framework bootstrap rule

When building an unresolved subsystem for the first time, prefer a working shell over speculative completeness.

A good first implementation usually contains:

- public interface / contract
- simple in-memory or mock implementation
- Runtime integration
- tests for the contract
- clear extension points

For example:

```text
MemoryStore
   ↓
InMemoryMemoryStore
```

is preferred over prematurely introducing a complex memory framework.

The goal is to allow later replacement:

```text
InMemoryMemoryStore
        ↓
FutureMemoryImplementation
```

without rewriting Runtime or canonical Character Data.

---

## External technology evaluation

Before introducing a new paper-derived technique, GitHub project, framework, library, or service, determine:

1. What problem does it solve?
2. Which Aiko subsystem owns that responsibility?
3. Is it a design reference, library, adapter target, or canonical component?
4. Does it force Aiko data into a third-party schema?
5. Can it be replaced later?
6. Which interface isolates it from Runtime?
7. What migration would be required if it were removed?
8. Does it require training a specialized character model?
9. Can its useful ideas be reused without adopting the whole framework?
10. Does it belong to Character Data, Runtime Context, Role Skill, Capability Skill, or infrastructure?

If these questions cannot be answered from the task or existing architecture, do not deeply integrate the technology.

---

## Coding rules

- Use Python with type hints.
- Keep modules focused and responsibilities explicit.
- Document public interfaces and non-obvious architectural constraints.
- Avoid global mutable state.
- Avoid unnecessary dependencies.
- Prefer the Python standard library when practical.
- Prefer composition over tight inheritance hierarchies.
- Keep domain models free of vendor SDK types.
- Avoid premature optimization.
- Avoid speculative abstraction that has no current consumer.
- Preserve backwards-compatible interfaces when practical.
- Keep mocks and simple implementations easy to replace.

---

## Change discipline

For architectural work:

1. Inspect the existing structure before editing.
2. Identify the subsystem and contract affected.
3. Make the smallest coherent change that satisfies the request.
4. Do not expand scope into unresolved research areas.
5. Add or update tests for changed behavior.
6. Report important assumptions or architectural decisions.

Do not perform unrelated refactors merely because they appear cleaner.

Do not rename or relocate public modules without a clear reason.

Do not delete placeholders for planned architecture simply because they are currently unused.

---

## Validation

Use the validation commands currently documented by the project in `README.md`, `pyproject.toml`, or task-specific instructions.

At minimum, when applicable, run:

```powershell
python -m pytest
python -m ai_friend
```

If an executable smoke test requires stdin or other setup, use the method documented by the current project rather than assuming an old command remains valid.

Do not add or claim formatter, linter, type-checker, or test commands that are not actually configured.

If a command cannot run because of the environment, dependency availability, or unfinished research-stage code, report that limitation rather than silently bypassing validation.

---

## Definition of done

A change is complete when:

- it respects subsystem boundaries;
- it does not hard-code unresolved research decisions;
- canonical character data remains Aiko-owned;
- new external dependencies are isolated;
- Runtime remains the coordinator;
- public contracts are typed and understandable;
- relevant tests pass, or failures are clearly explained.

When uncertain between a complex implementation and a minimal replaceable one, choose the minimal replaceable one.

---

## Character reconstruction stage and folder guardrails

Use `docs/folder_ownership.md` as the implementation routing contract. If a new
artifact does not fit its matrix, document the ownership gap before creating a
location. Real character data belongs in `character_data/<Character>/` and
`agents/AI_friend/<Character>/`, never inside Aiko.

The mandatory reconstruction order is:

```text
approved Source -> exact SourceUnit -> Observation -> single-copy Event
-> explicit Period Assignment -> Period Character State
-> cross-period Development -> Compiled Character State
```

Do not skip directly from source or Event to final character state. A SourceUnit
must contain exact approved text or an immutable exact-span reference with an
explicit grounding marker, locator, and integrity hash. LLM summaries belong in
Observation; reference notes may locate scenes but are not canonical evidence.

Period Character State is the minimum character-analysis unit and contains all
eight domain slots: Personality, Physical, Motivation, Backstory, Emotion,
Relationships, Growth, and Conflict. Store the Event once and reference it from
multiple domains. Missing evidence remains `unknown`, `unchanged`,
`insufficient_evidence`, or `not_applicable`; never fill a slot merely because it
exists. Earlier periods must not use later-only knowledge.

Development analysis requires multiple Period States. Keep confidence separate
from change resistance. Causal hypotheses retain provenance, uncertainty,
alternatives, and counterevidence; do not invent scoring rules or consolidation
thresholds.

Memory references Event IDs and never becomes a second Event store. Canonical
skill profile, post-canon learning, runtime capability, and underlying LLM
knowledge are distinct; external capabilities cannot rewrite canonical
proficiency. Relationship ownership remains unresolved, so do not add a permanent
Relationship subsystem without a later architecture decision.
