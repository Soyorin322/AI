# Architecture

## Overview

Aiko uses a `src` layout and dependency inversion. Public subsystem boundaries
are abstract base classes, while immutable `dataclasses` carry typed data between
them. Dataclasses were chosen because the current schema is small and needs no
runtime validation framework, keeping dependencies minimal.

```text
Character ─────┐
Knowledge ─────┤
Memory ────────┤
Skills ────────┼──> Runtime Orchestrator
Perception ────┘             │
                   Context composition boundary
                             │
                             v
                  temporary RuntimeContext ──> LLMProvider ──> Response
```

## Responsibilities and dependencies

- **Character** supplies generic identity, description, and state.
- **Knowledge** stores information available to the agent.
- **Memory** stores records originating in experiences or interactions.
- **Skills** discovers independently loadable resources; it does not execute them.
- **Perception** defines typed events and replaceable event sources.
- **LLM** defines typed generation requests and responses.
- **Runtime** is the sole coordinator and constructs one explicit context per turn.

Domain modules depend only on their own models and shared core primitives.
Runtime may depend on each subsystem's interface and models. The composition root
(`bootstrap.py`) alone chooses concrete in-memory/mock adapters. Subsystems never
reach into one another's implementation.

## Runtime flow

Text or a perception event enters the orchestrator. Its focused context-composition
method requests the current character, searches knowledge and memory, discovers
skills, and builds a `RuntimeContext`. The selected `LLMProvider` receives only a
composed `LLMRequest`; it does not query subsystem stores. After a response,
Runtime records the interaction through the `MemoryStore` interface.

`RuntimeContext` is a temporary, per-turn projection. It is neither canonical
character storage nor a static character card. A future persistent character
database must use Aiko-owned schemas behind subsystem interfaces; selection and
retrieval can then evolve at this centralized composition boundary.

## Framework, implementations, and character data

The framework owns contracts, data flow, and orchestration. Current in-memory and
mock classes are replaceable module implementations chosen only in `bootstrap.py`.
Character-facing data uses small Aiko-owned dataclasses and the sample YAML; no
vendor object is canonical. Replacing an LLM or store therefore does not redefine
the character.

## Knowledge versus Memory

Knowledge is reference information the agent can retrieve. Memory is evidence of
what it experienced. Separate models and stores prevent accidental mixing and let
each subsystem evolve independently.

## Extension points

- Add an LLM provider by implementing `LLMProvider`, then inject it at composition.
- Add a perception source by implementing `PerceptionSource`; Runtime accepts its
  `PerceptionEvent` without knowing the device or modality.
- Add a skill by creating a directory containing `SKILL.md`. Later registries may
  load richer metadata while preserving `SkillRegistry`. The future distinction
  between role-execution and capability skills remains open and is not Persona
  storage.

## Why mocks

Deterministic mocks prove control flow and replaceability without vendor coupling,
credentials, network access, or premature operational choices.

## Deferred features

Final Persona, event, relationship, skill-profile, and memory taxonomies and their
update/consolidation algorithms remain research-stage. Real characters; production
LLMs; embeddings, RAG, databases, consolidation and forgetting; automatic
skill/tool execution; audio, speech, screen, vision, video, MIDI; GUI/web/mobile
interfaces; cloud infrastructure; and multi-agent behavior are also deferred.
