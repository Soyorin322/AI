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
Skills ────────┼──> Runtime Orchestrator ──> LLMProvider ──> Response
Perception ────┘             │
                             └──> RuntimeContext
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

Text or a perception event enters the orchestrator. It requests the current
character, searches knowledge and memory, discovers skills, and builds a
`RuntimeContext`. The selected `LLMProvider` receives that context. After a
response, Runtime records the interaction through the `MemoryStore` interface.
Prompt/context assembly therefore remains centralized.

## Knowledge versus Memory

Knowledge is reference information the agent can retrieve. Memory is evidence of
what it experienced. Separate models and stores prevent accidental mixing and let
each subsystem evolve independently.

## Extension points

- Add an LLM provider by implementing `LLMProvider`, then inject it at composition.
- Add a perception source by implementing `PerceptionSource`; Runtime accepts its
  `PerceptionEvent` without knowing the device or modality.
- Add a skill by creating a directory containing `SKILL.md`. Later registries may
  load richer metadata while preserving `SkillRegistry`.

## Why mocks

Deterministic mocks prove control flow and replaceability without vendor coupling,
credentials, network access, or premature operational choices.

## Deferred features

Real characters and personality/emotion/relationship models; production LLMs;
embeddings, RAG, databases, consolidation and forgetting; automatic skill/tool
execution; audio, speech, screen, vision, video, MIDI; GUI/web/mobile interfaces;
cloud infrastructure; and multi-agent behavior are intentionally deferred.

