# Folder ownership and artifact routing

This document is the implementation routing contract for Aiko.

Real character instances live beside Aiko under `agents/AI_friend/<Character>/`; they never live inside Aiko.

The source-side / character-side boundary is:

```text
Canon
↓
data_processing
  Speaker / Thinker Attribution
  Event Segmentation
  Complete source locators
  Story-level ordering / chronology
↓
Complete Event
↓
Aiko
  Character Perspective Pre-Analysis
  Character Knowledge / Inference
  Character Interpretation
  Evidence / Period State / Memory / Development
```

`data_processing` owns preparation of complete, traceable story-level Events. Aiko does not create a second character-filtered copy of the source Event.

---

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
| `src/ai_friend/reconstruction/` | Character-side reconstruction after prepared Events enter Aiko | Character Perspective Pre-Analysis, knowledge-state inference, evidence, periods, provenance linking, workflow validation | Raw source normalization, speaker annotation, story-level Event segmentation, runtime context, final capability implementations | Complete Events from `data_processing`, core | Character/memory extraction and repositories | Contracts | No |
| `src/ai_friend/character/` | Historical and compiled character representation | Eight-domain period state, development, compiled state, character skill profile | Raw source Events, memory records, LLM calls | Core and typed reconstruction IDs/scopes | Runtime | Contracts | No |
| `src/ai_friend/memory/` | Retained subjective experience | Event-referencing memory records, formation decisions, retrieval metadata | Duplicate story-level Event objects, world lore, traits | Prepared Event IDs and character-perspective results | Runtime | Contracts/store | No |
| `src/ai_friend/knowledge/` | Character-accessible information | World/technical knowledge contracts and stores | Memories, traits, capability policy | Reconstruction / validated character knowledge | Runtime | Contracts/store | No |
| `src/ai_friend/skills/` | Programmatic capability boundary | Capability protocols, discovery, availability | Canonical character proficiency | Root skill packs and character skill-profile IDs | Runtime | Code/metadata | No |
| `src/ai_friend/perception/` | Runtime input typing | Perception observations/events | Direct character mutation | External input | Runtime | Usually ephemeral | No |
| `src/ai_friend/runtime/` | Coordination and context selection | Ephemeral composed context | Canonical persistent state | Character, knowledge, memory, skills, perception | LLM adapter | No | No |
| `src/ai_friend/llm/` | Replaceable inference adapters | Provider-neutral request/response boundaries | Persistent character/memory/skill state | Runtime context | Runtime | No | No |

Relationship ownership remains unresolved. Relationship-domain entries may live inside a period state and relationship-forming experiences may be referenced by memory, but there is no permanent relationship subsystem yet.

---

# Source-side ownership outside Aiko

`data_processing/` owns reusable, character-agnostic source preparation:

```text
speaker / thinker attribution
human-reviewed speaker-grounded source
Event boundaries
complete Event source ranges / locators
minimal source-supported participant metadata when useful
narrative_order
story_chronology
```

It must not own:

```text
Accessible / Inaccessible / Uncertain judgments for a target character
Known / Believed / Suspected / Misunderstood states
character-specific interpretation
personality evidence
Memory consolidation
Period Character State
Development
runtime context
```

The complete Event produced by `data_processing` remains the authoritative story-level source artifact for downstream character analysis.

---

## Artifact routing

| Artifact | Owner | Future character-instance storage |
|---|---|---|
| Raw / normalized source | `data_processing/` | source dataset / processed source tree |
| Speaker / thinker annotation | `data_processing/` | processed source tree |
| Story-level Event index and complete source locator | `data_processing/` | processed source tree, e.g. `processed/volume_XX/events.json` |
| Character Perspective Pre-Analysis | `reconstruction/` | `reconstruction/perspective/` or equivalent character-instance reconstruction storage |
| Character knowledge / belief-state inference | `reconstruction/` / `knowledge/` according to persistence semantics | reconstruction / character knowledge package |
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

---

# Mandatory reconstruction stage gates

The current character-side reconstruction path begins **after** source-side Event preparation:

```text
data_processing
────────────────────
approved source
→ speaker / thinker grounding
→ complete story-level Event

Aiko
────────────────────
Complete Event
→ Character Perspective Pre-Analysis
   → Accessible / Inaccessible / Uncertain
→ Character Knowledge / Inference
   → Known / Believed / Suspected / Misunderstood
→ Character Interpretation / Evidence
→ explicit Period Assignment
→ Period Character State
→ cross-period Development
→ Compiled Character State
```

The complete Event is not replaced by a sparse character-only source artifact.

Perspective results annotate how a target character may reason from the Event; they do not become a second canonical source and they do not remove inaccessible source material from the analysis context.

Memory and skill extraction branch from the single prepared Event / reconstruction lineage. Neither branch owns another Event copy.

---

# Provenance and identity

Aiko-derived artifacts must preserve lineage back to the prepared Event and, through the Event locator, to the original source passage.

Conceptually:

```text
CharacterPerspectiveResult
↓
event_id
↓
Event.source_ranges
↓
original source
```

Character interpretation, evidence, memory, and period-state artifacts must never replace this source lineage with model-written summaries alone.

---

# Ownership guardrails

1. `data_processing` owns source structure; Aiko owns character-relative reasoning.
2. Story-level Events are stored once and remain character-agnostic.
3. Aiko may read the complete Event even when parts are inaccessible to the target character.
4. `Accessible / Inaccessible / Uncertain` is perspective-analysis metadata, not a source deletion mask.
5. `Known / Believed / Suspected / Misunderstood` is character inference, not story truth.
6. No Aiko subsystem may silently copy a prepared Event into a divergent character-specific Event object.
7. Every persistent derived artifact must retain traceability to Event IDs and original source locators.
8. Runtime and external capabilities cannot rewrite canonical historical character state.
