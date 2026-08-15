# Task 001 — Bootstrap Generic `ai-friend` Framework

## Objective

Create the initial architecture and executable skeleton for a completely generic, modular, persistent AI character framework named `ai-friend`.

This task is **architecture-first**.

Do **not** implement any real fictional character, production LLM integration, vector database, speech recognition, TTS, vision model, MIDI interpretation, or external API integration yet.

The purpose of this task is to establish a clean foundation that later tasks can extend independently with:

1. Character Core
2. Knowledge
3. Memory
4. Skills
5. Perception
6. LLM providers
7. Runtime orchestration

The framework must not contain assumptions about any specific character, franchise, personality, voice, or application.

---

## Core Design Principles

The architecture must follow these principles:

### 1. Modular boundaries

The following domains must remain independent:

* Character
* Knowledge
* Memory
* Skills
* Perception
* LLM
* Runtime

Modules must communicate through explicit interfaces or typed domain models.

Do not allow one subsystem to directly depend on another subsystem's concrete implementation.

For example:

* Character must not directly access SQLite.
* Memory must not directly invoke an LLM provider.
* Perception must not directly update Character state.
* Skills must not directly modify Memory storage.
* Runtime should coordinate these systems.

---

### 2. Dependency inversion

Use abstractions/interfaces so future implementations can be replaced.

Examples:

```python
MemoryStore
KnowledgeStore
LLMProvider
SkillRegistry
PerceptionSource
CharacterProvider
```

Concrete implementations should be injected into the runtime.

For this task, create only lightweight in-memory/mock implementations.

---

### 3. Typed domain models

Use Python type hints throughout the public API.

Use either:

* `dataclasses`
* or Pydantic

Choose one consistent approach and document the reason in `docs/architecture.md`.

Avoid passing unstructured dictionaries between major subsystems when a domain model is appropriate.

---

## Initial Package Structure

Use a `src` layout.

Target structure:

```text
ai-friend/
├── AGENTS.md
├── README.md
├── pyproject.toml
│
├── src/
│   └── ai_friend/
│       ├── __init__.py
│       ├── __main__.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── interfaces.py
│       │   ├── models.py
│       │   └── events.py
│       │
│       ├── character/
│       │   ├── __init__.py
│       │   ├── interfaces.py
│       │   ├── models.py
│       │   └── mock.py
│       │
│       ├── knowledge/
│       │   ├── __init__.py
│       │   ├── interfaces.py
│       │   ├── models.py
│       │   └── memory_store.py
│       │
│       ├── memory/
│       │   ├── __init__.py
│       │   ├── interfaces.py
│       │   ├── models.py
│       │   └── memory_store.py
│       │
│       ├── skills/
│       │   ├── __init__.py
│       │   ├── interfaces.py
│       │   ├── models.py
│       │   └── registry.py
│       │
│       ├── perception/
│       │   ├── __init__.py
│       │   ├── interfaces.py
│       │   ├── models.py
│       │   └── mock.py
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── interfaces.py
│       │   ├── models.py
│       │   └── mock.py
│       │
│       └── runtime/
│           ├── __init__.py
│           ├── context.py
│           ├── session.py
│           └── orchestrator.py
│
├── characters/
│   └── example/
│       └── character.yaml
│
├── skills/
│   └── example_skill/
│       └── SKILL.md
│
├── tests/
│
└── docs/
    ├── architecture.md
    ├── character.md
    ├── knowledge.md
    ├── memory.md
    ├── skills.md
    └── perception.md
```

Small deviations are acceptable if they materially improve the architecture, but document them.

---

# Domain Requirements

## Character

Create only the minimum generic character representation needed for the framework.

Suggested concepts:

```text
CharacterIdentity
CharacterState
CharacterProfile
```

Do not attempt to design the final personality model yet.

The example character must be generic and exist only to demonstrate that the runtime works.

Do not encode anime-specific or franchise-specific concepts.

---

## Knowledge

Create an abstraction representing information the character can retrieve.

For now implement only an in-memory knowledge store.

Example responsibilities:

```python
add(...)
get(...)
search(...)
```

Keep Knowledge conceptually separate from Memory.

Knowledge represents information available to the agent.

Memory represents information originating from experiences or interactions.

Do not implement embeddings or vector search in this task.

---

## Memory

Create the memory abstraction but do not attempt to solve long-term memory yet.

Define extensible memory types that can later support concepts such as:

```text
working
episodic
semantic
relationship
```

For this task, a generic `MemoryRecord` and in-memory store are sufficient.

Each memory record should at minimum be capable of carrying:

```text
id
timestamp
content
metadata
```

Do not implement:

* embeddings
* memory consolidation
* summarization
* forgetting
* memory importance scoring
* persona-conditioned interpretation

Those belong to later tasks.

---

## Skills

Create a generic Skill abstraction.

Skills must be independently loadable resources.

Reserve the directory structure:

```text
skills/
└── example_skill/
    ├── SKILL.md
    ├── scripts/
    ├── references/
    └── assets/
```

Only `SKILL.md` is required in the example.

A skill should at minimum expose metadata such as:

```text
name
description
path
```

Do not implement automatic tool execution yet.

The Skill Registry should be able to discover available skill directories.

---

## Perception

Create a generic event-based perception interface.

Use a typed model similar to:

```python
class PerceptionEvent:
    id: str
    modality: str
    source: str
    timestamp: datetime
    payload: ...
```

The architecture must leave room for future modalities such as:

```text
text
audio
screen
image
video
MIDI
system events
```

Do not implement actual microphone, screen capture, vision, or MIDI code yet.

A mock perception source is sufficient.

---

## LLM

Define a provider abstraction.

Example conceptual interface:

```python
class LLMProvider:
    def generate(self, request: LLMRequest) -> LLMResponse:
        ...
```

Do not integrate OpenAI, Anthropic, Ollama, llama.cpp, or any real provider yet.

Create a deterministic mock provider.

The rest of the application must depend only on the interface, not the mock implementation.

---

# Runtime Orchestrator

Create a central runtime/orchestrator.

The orchestrator is responsible for coordinating subsystems.

Conceptually:

```text
User input / Perception Event
            ↓
      Runtime Orchestrator
            ↓
    Character state
    Relevant memory
    Relevant knowledge
    Available skills
            ↓
      Runtime Context
            ↓
        LLM Provider
            ↓
          Response
```

Create an explicit `RuntimeContext` model.

Do not allow prompt construction logic to become scattered across modules.

For now, the orchestrator only needs enough functionality to demonstrate the architecture.

---

# Executable Demo

The project must run with:

```bash
python -m ai_friend
```

It should start a minimal terminal conversation loop.

Example:

```text
ai-friend generic runtime
Type "exit" to quit.

You > Hello
Example > Mock response to: Hello

You >
```

No real AI is required.

The important part is that this response flows through:

```text
CLI
→ Orchestrator
→ Character
→ Memory/Knowledge context
→ Mock LLM
→ Response
```

Do not bypass the architecture just to make the demo work.

---

# Configuration

Use a minimal configuration approach.

Do not introduce a complex configuration framework.

The sample character can use:

```text
characters/example/character.yaml
```

Keep it minimal, for example:

```yaml
id: example
name: Example
description: Generic example character used for framework testing.
```

Do not define the final Character Core schema in this task.

---

# AGENTS.md

Create a root `AGENTS.md`.

It should explain persistent development rules for future Codex tasks.

Include at least:

## Project intent

`ai-friend` is a modular framework for persistent AI characters.

The framework must remain character-agnostic.

## Architectural rules

* Maintain strict subsystem boundaries.
* Prefer dependency inversion.
* Do not couple domain logic to vendor APIs.
* Do not introduce global mutable state.
* Do not bypass interfaces for convenience.
* Do not mix Knowledge and Memory concepts.
* Runtime coordinates modules; modules should not orchestrate each other.
* Prefer simple implementations until real requirements justify complexity.

## Coding rules

* Python with type hints.
* Keep modules focused.
* Public interfaces should be documented.
* Avoid unnecessary dependencies.
* Avoid premature optimization.
* Prefer standard library when practical.

## Validation

Document the exact commands Codex should run after modifying the repository, for example:

```bash
pytest
```

and any formatter/type-checker actually configured by the project.

Do not list validation tools that are not installed/configured.

---

# Documentation

Create `docs/architecture.md`.

It must explain:

1. Overall architecture
2. Responsibility of each subsystem
3. Allowed dependency directions
4. How the orchestrator works
5. Difference between Knowledge and Memory
6. How future LLM providers can be added
7. How future perception sources can be added
8. How future Skills can be added
9. Why the current implementation intentionally uses mocks
10. Explicitly deferred features

Include a simple text architecture diagram.

Example:

```text
                ┌─────────────┐
                │ Character   │
                └──────┬──────┘
                       │
Knowledge ─────────────┤
Memory ────────────────┤
Skills ────────────────┤
Perception ────────────┤
                       ▼
                ┌─────────────┐
                │Orchestrator │
                └──────┬──────┘
                       ▼
                ┌─────────────┐
                │ LLMProvider │
                └─────────────┘
```

Also create short placeholder design documents for:

```text
docs/character.md
docs/knowledge.md
docs/memory.md
docs/skills.md
docs/perception.md
```

These documents should clearly state that their real implementations will be designed in later tasks.

Do not invent detailed future architecture prematurely.

---

# Testing Requirements

Use `pytest`.

Tests must verify at minimum:

### Runtime

The orchestrator can process text input using mock components.

### Replaceability

At least one test should demonstrate that a subsystem implementation can be replaced without modifying the orchestrator.

For example:

```text
MockLLMProvider
        ↓ replace with
AlternativeFakeLLMProvider
```

without changing runtime code.

### Knowledge

In-memory knowledge records can be stored and retrieved.

### Memory

In-memory memory records can be stored and retrieved.

### Skills

Skill discovery can find the example `SKILL.md`.

### Perception

A mock perception event can be passed into the runtime.

---

# Dependency Constraints

Keep dependencies minimal.

Preferred initial dependencies:

```text
pytest
PyYAML
```

Only add another dependency if clearly justified.

Do not add:

* LangChain
* LangGraph
* LlamaIndex
* Mem0
* FAISS
* Qdrant
* Chroma
* OpenAI SDK
* Anthropic SDK
* Ollama client
* FastAPI
* SQLAlchemy
* GUI frameworks

Those may be evaluated in later tasks.

---

# Explicit Non-Goals

Do NOT implement any of the following in Task 001:

* real fictional characters
* personality simulation
* emotional model
* relationship model
* long-term memory algorithms
* embeddings
* RAG
* vector databases
* graph databases
* memory consolidation
* autonomous memory writing
* autonomous Skill creation
* real LLM APIs
* local LLM inference
* voice recognition
* speech synthesis
* voice cloning
* microphone capture
* screen capture
* computer vision
* video understanding
* anime watching
* MIDI input
* piano analysis
* GUI
* web server
* mobile app
* cloud infrastructure
* multi-agent architecture

If something is not required to demonstrate the framework boundary, leave it for a later task.

---

# Acceptance Criteria

The task is complete only when all of the following are true:

* [ ] Project uses a clean Python `src` layout.
* [ ] `python -m ai_friend` starts successfully.
* [ ] A terminal text interaction works through the orchestrator.
* [ ] Character, Knowledge, Memory, Skills, Perception, LLM, and Runtime exist as separate modules.
* [ ] Major module boundaries use explicit typed interfaces.
* [ ] Mock implementations exist where required.
* [ ] No production LLM/API/database/perception integrations are present.
* [ ] Knowledge and Memory are architecturally separate.
* [ ] Skills can be discovered from a `SKILL.md` directory.
* [ ] A generic `PerceptionEvent` exists.
* [ ] Runtime context is explicitly modeled.
* [ ] The orchestrator depends on abstractions rather than concrete implementations.
* [ ] Unit tests pass.
* [ ] `AGENTS.md` exists.
* [ ] `docs/architecture.md` explains the architecture.
* [ ] README explains installation, running, and testing.
* [ ] No character-specific assumptions are embedded in the framework.

---

# Before Finishing

Before considering the task complete:

1. Inspect the final project structure.
2. Run all configured tests.
3. Run the application manually with a simple input.
4. Check for unnecessary dependencies or premature abstractions.
5. Confirm no subsystem directly reaches into another subsystem's concrete implementation.
6. Confirm the framework remains completely character-agnostic.
7. Update documentation if implementation decisions differ from this specification.

In the final response, summarize:

* architecture created
* important design decisions
* files/modules added
* tests executed and results
* deliberate non-goals/deferred work
* any deviations from this specification and why
