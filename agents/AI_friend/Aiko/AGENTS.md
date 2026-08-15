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

Before making architectural changes, read the latest `character_create_v*.txt` document available in the repository.

Treat that document as the current architecture and research specification.

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
Interpretation
        ↓
Evidence / subsystem updates
        ↓
Optional controlled consolidation
```

Do not hard-code a specific personality-update algorithm unless explicitly requested.

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

From this directory, run the existing project validation commands when applicable:

```powershell
python -m pytest
"Hello`nexit" | python -m ai_friend
```

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
