# Aiko

Aiko (AI 子) is the working name for a generic, modular `ai-friend` framework.
It provides replaceable boundaries for Character, Knowledge, Memory, Skills,
Perception, LLM providers, and Runtime orchestration. This first version uses
only deterministic in-memory/mock adapters; it does not implement a fictional
persona or connect to a real AI service.

Runtime centrally composes a temporary `RuntimeContext` for each request. That
context is a selected view for a replaceable reasoning engine, not canonical
character storage or a static character card.

The framework also includes an evidence-grounded Character Reconstruction
framework. It enforces exact source grounding and keeps observations, single-copy
events, period assignments, eight-domain period states, cross-period development,
memories, skill profiles, and compiled state distinct and traceable. Reconstruction
persistence is replaceable and isolated from conversational Runtime. No real
character instance or automatic extraction pipeline is included.

## Install

Python 3.11 or newer is required.

```powershell
python -m pip install -e ".[dev]"
```

## Run

```powershell
python -m ai_friend
```

## Test

```powershell
python -m pytest
```

See [character_create_v0.0.8](docs/architecture/character_create_v0.0.8.txt) for
the current architecture, [folder ownership](docs/folder_ownership.md) for
mandatory artifact routing, and [reconstruction](docs/reconstruction.md) plus
[schema docs](docs/schemas/) for contracts. Real character sources and instances
belong outside Aiko.
