# Aiko

Aiko (AI 子) is the working name for a generic, modular `ai-friend` framework.
It provides replaceable boundaries for Character, Knowledge, Memory, Skills,
Perception, LLM providers, and Runtime orchestration. This first version uses
only deterministic in-memory/mock adapters; it does not implement a fictional
persona or connect to a real AI service.

Runtime centrally composes a temporary `RuntimeContext` for each request. That
context is a selected view for a replaceable reasoning engine, not canonical
character storage or a static character card.

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

See [docs/architecture.md](docs/architecture.md) for design boundaries and
extension points.
