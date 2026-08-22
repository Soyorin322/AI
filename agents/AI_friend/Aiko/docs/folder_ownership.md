# Folder ownership and artifact routing

This document is the implementation routing contract for Aiko. If an artifact
does not fit this matrix, document the ownership gap before adding a folder or
persisting data. Real character instances live beside Aiko under
`agents/AI_friend/<Character>/`; they never live inside Aiko.

## Folder ownership matrix

| Path | Owner responsibility | Allowed data | Forbidden data | Reads from | Referenced by | Persistent? | Character-specific? |
|---|---|---|---|---|---|---|---|
| `Aiko/` | Generic framework root | Framework configuration and navigation | Real character canon or instance state | Architecture | Developers | Yes | No |
| `Aiko/characters/` | Templates and synthetic examples | Minimal generic fixtures | Real character instances | Generic contracts | Tests/examples | Optional | Synthetic only |
| `Aiko/docs/` | Architecture, research, schema, workflow | Human-readable design records | Runtime state | Project sources | Developers | Yes | No |
| `Aiko/reference/` | Generic framework research references | Papers and framework notes | Character canon or evidence | External research | Architecture research | Yes | No |
| `Aiko/skills/` | Reusable skill resource packs | `SKILL.md`, scripts, generic assets | Character proficiency/history | Generic resources | Skill loaders | Yes | No |
| `Aiko/tasks/` | Implementation instructions/history | Scoped task specifications | Runtime/canonical data | Architecture | Coding agents | Yes | No |
| `Aiko/tests/` | Framework verification | Synthetic fixtures and contract tests | Real-character corpora | Public contracts | Test runner | Yes | Synthetic only |
| `src/ai_friend/core/` | Truly cross-cutting primitives | IDs, time/version helpers | Domain artifacts | None | All packages | Code | No |
| `src/ai_friend/reconstruction/` | Source-grounded reconstruction stages | Source, exact units, observations, events, evidence, periods, provenance, workflow validation | Runtime context, memories, final capability implementations | Core | Character/memory extraction and repositories | Contracts | No |
| `src/ai_friend/character/` | Historical and compiled character representation | Eight-domain period state, development, compiled state, character skill profile | Raw events, memory records, LLM calls | Core and typed reconstruction IDs/scopes | Runtime | Contracts | No |
| `src/ai_friend/memory/` | Retained subjective experience | Event-referencing memory records, formation decisions, retrieval metadata | Duplicate event objects, world lore, traits | Typed event IDs | Runtime | Contracts/store | No |
| `src/ai_friend/knowledge/` | Character-accessible information | World/technical knowledge contracts and stores | Memories, traits, capability policy | Core | Runtime | Contracts/store | No |
| `src/ai_friend/skills/` | Programmatic capability boundary | Capability protocols, discovery, availability | Canonical character proficiency | Root skill packs and character skill-profile IDs | Runtime | Code/metadata | No |
| `src/ai_friend/perception/` | Runtime input typing | Perception observations/events | Direct character mutation | External input | Runtime | Usually ephemeral | No |
| `src/ai_friend/runtime/` | Coordination and context selection | Ephemeral composed context | Canonical persistent state | Character, knowledge, memory, skills, perception | LLM adapter | No | No |
| `src/ai_friend/llm/` | Replaceable inference adapters | Provider-neutral request/response boundaries | Persistent character/memory/skill state | Runtime context | Runtime | No | No |

Relationship ownership remains unresolved. Relationship domain entries may live
inside a period state and relationship-forming experiences may be referenced by
memory, but Task 005 does not create a permanent relationship subsystem.

## Artifact routing

| Artifact | Generic contract owner | Future character-instance storage |
|---|---|---|
| Source reference / exact SourceUnit / Observation | `reconstruction/` | `reconstruction/manifests/` and source-unit/observation data |
| Event | `reconstruction/` | `reconstruction/events/` (stored once) |
| Evidence | `reconstruction/` | `reconstruction/evidence/` |
| Period definition and assignment | `reconstruction/` | `reconstruction/periods/` |
| Period Character State | `character/` | `reconstruction/periods/` |
| Cross-period Development | `character/` | `reconstruction/development/` |
| Memory record/index | `memory/` | `memory/records/`, `memory/index/` |
| Character Skill Profile | `character/` | `character/skill_profile/` |
| Capability Skill | root `skills/` resources plus Python `skills/` contracts | Reusable, not character canon |
| Compiled Character State | `character/` | `character/compiled/` |
| Runtime context | `runtime/` | Ephemeral only |
| World/technical knowledge | `knowledge/` | Character knowledge package/store |
| Perception event | `perception/` | Runtime ingestion; not canon automatically |
| LLM adapter | `llm/` | Framework only |

## Mandatory stage gates

Persistent reconstruction follows:

```text
approved Source -> exact SourceUnit -> Observation -> Event
-> explicit Period Assignment -> Period Character State
-> cross-period Development -> Compiled Character State
```

Memory and skill extraction branch from the single Event record. Reference notes
may locate an approved span but cannot be a canonical source. Missing domain
evidence remains explicit. Runtime and external capabilities cannot rewrite
canonical proficiency or historical state.
