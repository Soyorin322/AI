# Task 006 — First Aiko-Compliant Reirin Reconstruction

Status: Proposed implementation/reconstruction task  
Target framework: `agents/AI_friend/Aiko/`  
Target character instance: `agents/AI_friend/Reirin/`  
Primary source: `character_data/Reirin/sources/raw/novel/惡女不才_第一卷_前三章.md`  
Primary architecture authority: `agents/AI_friend/Aiko/docs/architecture/character_create_v0.0.8.txt`  
Framework contract authority: Task 005 outputs under `Aiko/docs/` and `Aiko/src/ai_friend/`

---

# 0. Task Purpose

Task 006 is the first real-character integration test of the Aiko Character Reconstruction framework.

The goal is NOT to "read the first three chapters and summarize Reirin's personality."

The goal is to prove that a real character source can be transformed through the exact Aiko reconstruction stages:

```text
Approved Source
    ↓
Exact SourceUnit
    ↓
Observation
    ↓
Event
    ↓
Explicit Period Assignment
    ↓
Period Character State
    ↓
Cross-period Development
    ↓
Compiled Character State
```

with side branches:

```text
Event
├──→ Memory Formation Decision → MemoryRecord
└──→ SkillEvidence → CharacterSkillProfile
```

The resulting persistent character data must be written under:

```text
agents/AI_friend/Reirin/
```

and must conform to Aiko-owned contracts implemented by Task 005.

This is the first valid Reirin reconstruction attempt using the hardened Aiko framework.

---

# 1. Source Scope — HARD LIMIT

Use exactly this file:

```text
character_data/Reirin/sources/raw/novel/惡女不才_第一卷_前三章.md
```

Do NOT read or use:

- later chapters from Volume 1;
- Volume 2;
- Volume 3;
- wiki;
- web sources;
- previous Reirin reconstructions;
- Task 004 Reirin outputs;
- reference notes;
- summaries from other files;
- character descriptions from external websites.

The reconstruction source boundary for Task 006 is only this one file.

If information required by a schema is not supported by this file:

```text
preserve uncertainty / abstain
```

Do NOT fill gaps from model knowledge.

---

# 2. Source Trust / Annotation Status

The selected file is a speaker-annotated derivative of the novel text.

Its header explicitly states that speaker attribution was produced by contextual inference / rule assistance and may require later human correction.

Therefore Task 006 must distinguish:

```text
novel text content
= reconstruction evidence

speaker attribution labels
= derived annotation / useful metadata
```

Do NOT treat every speaker tag as infallible canonical truth.

The SourceReference metadata must record that:

```text
source_role: approved_reconstruction_input
content_basis: novel_text
speaker_annotation: derived
speaker_annotation_confidence: not_guaranteed
```

or an equivalent Aiko-compatible representation.

The file MAY be marked `approved=true` for this controlled reconstruction experiment, but the approval means:

> approved input for Task 006

not:

> every derived speaker label is canonical fact.

If a speaker attribution is uncertain or conflicts with nearby narrative context:

- preserve uncertainty;
- do not create a confident character claim from that line alone.

---

# 3. Character Scope

Primary reconstruction subject:

```text
Character: 黃玲琳 / Reirin
Character instance ID: Reirin
```

Other characters may appear in Event participants and relationship evidence, including but not limited to:

- 朱慧月;
- 冬雪;
- 堯明;
- 辰宇;
- other named participants.

However Task 006 MUST NOT reconstruct full independent Character States for those characters.

They exist only as:

```text
participants
relationship targets
story context
sources of statements/actions
```

needed to reconstruct Reirin.

---

# 4. Read Before Execution

Before changing any character data, Codex MUST read:

```text
agents/AI_friend/Aiko/AGENTS.md
agents/AI_friend/Aiko/README.md
agents/AI_friend/Aiko/docs/architecture/character_create_v0.0.8.txt
agents/AI_friend/Aiko/docs/folder_ownership.md
agents/AI_friend/Aiko/docs/reconstruction.md
agents/AI_friend/Aiko/docs/schemas/reconstruction.md
agents/AI_friend/Aiko/docs/schemas/character_state.md
agents/AI_friend/Aiko/docs/schemas/memory.md
agents/AI_friend/Aiko/docs/schemas/skills.md
```

and inspect the authoritative Task 005 implementations:

```text
agents/AI_friend/Aiko/src/ai_friend/reconstruction/models.py
agents/AI_friend/Aiko/src/ai_friend/reconstruction/provenance.py
agents/AI_friend/Aiko/src/ai_friend/reconstruction/validation.py
agents/AI_friend/Aiko/src/ai_friend/reconstruction/hardening.py
agents/AI_friend/Aiko/src/ai_friend/reconstruction/serialization.py

agents/AI_friend/Aiko/src/ai_friend/character/reconstruction.py

agents/AI_friend/Aiko/src/ai_friend/memory/models.py
agents/AI_friend/Aiko/src/ai_friend/memory/interfaces.py

agents/AI_friend/Aiko/src/ai_friend/skills/models.py
agents/AI_friend/Aiko/src/ai_friend/skills/interfaces.py
```

Also inspect:

```text
agents/AI_friend/Aiko/tests/test_reconstruction_hardening.py
```

to understand the intended end-to-end contract usage.

Do not create a parallel private schema for Reirin if Aiko already defines the concept.

---

# 5. Existing `agents/AI_friend/Reirin/`

At the start of Task 006, inspect:

```text
agents/AI_friend/Reirin/
```

Do not assume it is empty.

If only placeholder files exist, initialize the character instance according to this task.

If unexpected reconstruction data already exists:

- do not silently overwrite it;
- report it;
- isolate Task 006 output using explicit reconstruction versioning.

Task 006 must not delete unrelated user data.

---

# 6. Required Character Instance Structure

Task 006 must create a clear character-instance layout under:

```text
agents/AI_friend/Reirin/
```

Use the following ownership structure unless the current Aiko contracts require a narrowly justified variation:

```text
agents/AI_friend/Reirin/
├── README.md
│
├── reconstruction/
│   ├── manifests/
│   │   └── reconstruction_v0.1_manifest.json
│   │
│   ├── source_units/
│   │   └── source_units_v0.1.json
│   │
│   ├── observations/
│   │   └── observations_v0.1.json
│   │
│   ├── events/
│   │   └── events_v0.1.json
│   │
│   ├── evidence/
│   │   └── evidence_v0.1.json
│   │
│   ├── periods/
│   │   ├── period_definitions_v0.1.json
│   │   ├── period_assignments_v0.1.json
│   │   └── period_states_v0.1.json
│   │
│   └── development/
│       └── development_v0.1.json
│
├── memory/
│   ├── records/
│   │   └── memories_v0.1.json
│   └── index/
│       └── memory_index_v0.1.json
│
└── character/
    ├── skill_profile/
    │   └── skill_profile_v0.1.json
    └── compiled/
        └── compiled_character_state_v0.1.json
```

The exact number of files may be adjusted if Aiko's deterministic serialization layer makes another representation clearly safer, but the logical ownership MUST remain identical.

Do NOT create:

```text
personality/
emotion/
relationship/
growth/
```

as separate Event-copy folders.

The eight Domains live inside each `PeriodCharacterState`.

---

# 7. Version

This controlled reconstruction is:

```text
Reirin reconstruction version: v0.1
```

Meaning:

> first Aiko-compliant reconstruction from the first three chapters only.

It does NOT mean:

> complete or final Reirin personality.

All manifests and compiled state must clearly identify:

```text
character_id: Reirin
reconstruction_version: 0.1
source_scope: first volume, selected prologue/first three chapter source file only
```

Use the exact source filename in the manifest.

---

# 8. Required Stage 1 — SourceReference

Create one approved `SourceReference` representing:

```text
character_data/Reirin/sources/raw/novel/惡女不才_第一卷_前三章.md
```

Record sufficient metadata to identify:

- file/path;
- title;
- media type;
- controlled Task 006 source boundary;
- annotation status;
- source role;
- exact source version/hash if practical.

The source reference MUST NOT point to Task 004 or reference notes.

---

# 9. Required Stage 2 — Exact SourceUnits

Codex must read the entire allowed source file before finalizing event segmentation.

Do not select only a few scenes based on pre-existing assumptions about Reirin.

Create SourceUnits for source spans that actually ground later Observations / Events.

A SourceUnit must use Aiko's exact-source semantics:

```text
SourceUnitGrounding.EXACT_TEXT
```

or:

```text
IMMUTABLE_EXACT_SPAN_REFERENCE
```

if exact text is intentionally not duplicated.

Each SourceUnit must have:

- stable ID;
- source ID;
- exact locator;
- exact text or exact immutable span reference according to contract;
- integrity hash;
- temporal metadata where useful.

The locator must be sufficiently precise to return to the original source.

Examples of acceptable locator strategy:

```text
heading + line range
```

or equivalent deterministic source position.

Do not use:

```text
"early chapter"
"near body swap"
"somewhere in chapter 2"
```

as the only locator.

---

# 10. Required Stage 3 — Observation Extraction

For each relevant SourceUnit, create one or more `ObservationRecord`.

Observation answers:

```text
What does the source directly support?
```

Allowed observation content includes:

- explicit character statement;
- narrator-supported fact;
- directly observed behavior;
- explicit physical state;
- explicit relationship behavior;
- explicit goal or decision;
- direct result of an action.

Observation MUST NOT be a stable personality conclusion.

Forbidden Observation examples:

```text
Reirin is fundamentally altruistic.
Reirin has high resilience.
Reirin always protects others.
```

unless the source itself explicitly makes such a statement, and even then it remains an observed source statement, not automatically a consolidated trait.

Prefer narrow statements.

---

# 11. Required Stage 4 — Event Segmentation

From Observations, identify distinct `EventRecord` nodes.

The Event must be the single source of truth for what happened.

Each Event should include where supported:

```text
id
description
lineage
temporal_scope
participants
objective_facts
character_accessible_information
explicit_statements
observed_behaviors
outcome
uncertainty
```

## 11.1 Do not pre-impose Event count

Task 006 does not specify a fixed number of Events.

Codex must segment based on meaningful event boundaries.

Avoid both extremes:

```text
one Event per sentence
```

and:

```text
one Event for an entire chapter
```

Use a new Event where there is a meaningful shift in:

- objective situation;
- action/decision;
- participants;
- goal/conflict;
- consequence;
- knowledge state;
- identity/body state;
- environment;
- relationship interaction.

## 11.2 Event description must not become trait analysis

Bad:

```text
event_007:
Reirin demonstrates her permanently fearless personality.
```

Good:

```text
event_007:
Reirin remains behaviorally calm while facing the beast-seeking execution and explicitly explains that she is accustomed to being near death.
```

The second may later support bounded Period or Development analysis.

---

# 12. Character-Accessible Information

This field is mandatory to consider for all psychologically important Events.

Separate:

```text
story-level truth
```

from:

```text
what Reirin could know at that time
```

Examples of forbidden leakage:

- narrator-only facts unknown to Reirin;
- another character's private thoughts;
- later chapter information;
- future period explanations.

If a story fact is real but unavailable to Reirin:

- it may remain an objective/narrative fact;
- it must NOT enter Reirin's `character_accessible_information`;
- it must NOT enter her Memory as known fact.

---

# 13. Required Stage 5 — Evidence Records

Create bounded `EvidenceRecord` objects where Event/Observation material supports or contradicts a Period State or later Development hypothesis.

Use:

```text
SUPPORTS
CONTRADICTS
```

appropriately.

Evidence should be narrow enough that later analyses can distinguish:

```text
observed behavior
```

from:

```text
interpretation of behavior
```

and:

```text
long-term conclusion
```

Do not manufacture counterevidence.

If none exists within the source scope, preserve that fact.

---

# 14. Required Stage 6 — Period Discovery

Do NOT use chapter numbers as automatic Periods.

The first three chapters contain major candidate state transitions, but Task 006 must derive Period boundaries from character-state evidence.

Candidate boundary signals include:

- body / identity transition;
- major environment transition;
- knowledge-state transition;
- major relationship-state transition;
- major goal transition;
- major life situation transition;
- major psychological turning point.

Codex must first analyze Events, then propose `PeriodDefinition`.

Each Period must have:

```text
id
order
temporal_scope
boundary_status
boundary_reason
knowledge_boundary_order
```

Possible `boundary_status`:

```text
confirmed
candidate
unresolved
```

Task 006 must explain each proposed boundary.

No Period may exist solely because:

```text
chapter changed
```

---

# 15. Required Stage 7 — Period Assignment

Every Event used for character-state reconstruction must receive an explicit `PeriodAssignment`.

Assignment must include:

```text
event_id
period_id
reason
status
```

An Event must not be duplicated into another Period to express multiple Domain effects.

One Event:

```text
event_001
```

may support:

```text
Personality
Physical
Motivation
Relationships
...
```

through references from the same Period State.

---

# 16. Required Stage 8 — Period Character State

Create one `PeriodCharacterState` per accepted/candidate historical Period.

Each Period State contains exactly the Aiko eight Domain slots:

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

Use only these `DomainEvidenceState` semantics:

```text
observed
bounded_inference
unknown
unchanged
insufficient_evidence
not_applicable
```

Do NOT invent additional confidence labels as substitute Domain states.

## 16.1 Domain rule

Every non-abstaining DomainEntry must reference:

```text
event_ids
and/or
evidence_ids
```

and must contain only claims valid for that Period.

## 16.2 No forced filling

If the source does not support a Domain:

```text
insufficient_evidence
```

is a correct answer.

Task 006 is NOT judged by how full all eight Domains are.

It is judged by fidelity and traceability.

## 16.3 Bounded inference

Use `bounded_inference` for statements such as:

```text
Within this Period and the observed situations, Reirin appears to...
```

Do not silently convert bounded inference into life-long personality.

---

# 17. Physical / Body Identity Must Be Explicitly Period-Aware

Because this source includes a body swap, Task 006 must handle:

```text
character identity
≠ current body identity
```

without confusing them.

For Reirin:

```text
person/character identity:
黃玲琳 / Reirin
```

may coexist with:

```text
current body:
朱慧月's body
```

in later Period(s).

Do not rename Reirin as 慧月 merely because the body changes.

Where relevant, Period Physical state should preserve:

- original body condition;
- current body identity;
- health differences;
- character's awareness of the change;
- uncertainty where applicable.

This is a critical Task 006 integration test.

---

# 18. Required Stage 9 — Memory Formation

For each psychologically or narratively relevant Event, explicitly consider a `MemoryFormationDecision`.

The decision may be:

```text
persist
```

or:

```text
do_not_persist
```

Task 006 does NOT require every Event to create Memory.

If `persist`:

create a `MemoryRecord`.

Memory must reference the Event ID.

Memory may contain:

- remembered content;
- subjective meaning;
- affective trace;
- uncertainty;
- period;
- accessible fact IDs;
- retrieval metadata.

Memory MUST NOT duplicate the Event's full objective structure.

Forbidden:

```text
MemoryRecord.metadata.objective_facts = complete Event copy
```

Preferred retrieval relation:

```text
MemoryIndex
→ MemoryRecord
→ Event
→ Observation
→ SourceUnit
```

---

# 19. Memory Subjectivity Guard

Memory may include a bounded subjective interpretation only if the text supports that Reirin formed or plausibly retained that subjective understanding.

Do NOT inject analyst conclusions into Memory.

For example:

Bad:

```text
Reirin remembers that this event permanently made her resilient.
```

unless the source supports that exact retrospective meaning.

Memory is:

```text
how Reirin remembers/carries the experience
```

not:

```text
the researcher's final psychological model.
```

---

# 20. Required Stage 10 — Skill Evidence / Character Skill Profile

Scan the source for canon-supported demonstrated abilities.

Create `SkillEvidence` only where behavior/statement actually supports a skill.

Possible categories must emerge from evidence rather than a preset desired profile.

Canonical proficiency must remain bounded.

Forbidden:

```text
one successful act
→ expert
```

For every `CharacterSkillProfile`, preserve:

```text
skill_id
origin = canon_supported
canonical_proficiency
skill_evidence_ids
period_id if applicable
limitations
uncertainty
```

Do NOT create `RuntimeCapability` simply because a Canon skill exists.

Do NOT add technical skill packs to Aiko in this task.

---

# 21. Required Stage 11 — Cross-Period Development

Only create a `DevelopmentRecord` if at least two Period Character States legitimately exist.

Development analysis must be based on cross-period comparison.

Potential representation may include:

```text
ChangeResistance
HistoricalAdaptation
CausalHypothesis
AccessibilityProfile
HabitualProcessingPattern
```

Do NOT require every dimension to be populated.

## 21.1 Change Resistance

Do not assign:

```text
high
medium
low
```

merely because a statement appears convincing.

If evidence is not sufficient to judge resistance:

```text
unresolved
```

or equivalent qualitative representation is preferred.

Confidence does not determine resistance.

## 21.2 Historical Accumulation

Ask:

```text
Does a pattern persist or change across the Periods visible in this source?
```

Do not assume one Event creates a permanent trait.

## 21.3 Causal Formation

A causal statement must remain a `CausalHypothesis`.

It must include:

- supporting evidence;
- uncertainty;
- counterevidence if present;
- alternative hypothesis if appropriate.

Do not promote narrative correlation into confirmed psychological causality.

## 21.4 Chronic Accessibility / Habitual Processing

Only create these if multiple events/periods support a recognizable repeated processing tendency.

Do not create them because the schema exists.

---

# 22. Important Special Case — Narrator-Level Character Summary

The novel may contain narrator statements that explicitly summarize Reirin, for example statements describing long-term physical frailty or unusually strong mental endurance.

These are valuable evidence.

However they must still pass through:

```text
SourceUnit
→ Observation
→ Event / Evidence
→ Period / Development
```

Do not bypass the graph and paste narrator summaries directly into Compiled Character State.

If the narrator explicitly states a generalized trait, record that as strong source evidence, but still:

- preserve temporal scope;
- preserve source lineage;
- compare with observed behavior;
- retain contradictions if later found.

---

# 23. Required Stage 12 — Compiled Character State

Produce a `CompiledCharacterState` only after Period States and any legitimate Development records have been created.

For this first source window, the compiled state should be deliberately conservative.

It may contain:

- current Period State reference;
- historical Period State IDs;
- evidence-supported current/persistent entries;
- relevant Development IDs;
- unresolved items.

Every compiled entry must be traceable to Period State.

Do NOT include:

- unsupported final personality;
- future-volume knowledge;
- complete-world knowledge;
- technical abilities not demonstrated;
- analyst speculation presented as canon.

The compiled state is:

```text
Reirin v0.1 based on the first three chapters only
```

not the final Reirin.

---

# 24. Legacy Task 003 Objects

`CharacterClaim` and `CharacterStateSnapshot` still exist for Task 003 compatibility.

Task 006 MUST NOT use them as an alternative shortcut:

```text
Event
→ CharacterClaim
→ CharacterStateSnapshot
→ done
```

The primary Task 006 character path is:

```text
Event
→ PeriodCharacterState
→ DevelopmentRecord
→ CompiledCharacterState
```

Legacy objects may only be used if required by existing Aiko infrastructure and must not replace Period-based reconstruction.

If used, explain their exact purpose in the final report.

---

# 25. No Direct Persona Summary Pass

Codex MUST NOT perform this hidden workflow:

```text
read all chapters
↓
write mental summary of Reirin
↓
retrofit Events / Evidence to justify that summary
```

Required workflow is bottom-up.

Codex must construct lower-level artifacts before finalizing upper-level artifacts.

Implementation process should be auditable in this sequence:

```text
Phase 1: SourceUnits
Phase 2: Observations
Phase 3: Events
Phase 4: Evidence
Phase 5: Period discovery/assignment
Phase 6: Period States
Phase 7: Memory / Skill branch
Phase 8: Cross-period Development
Phase 9: Compiled State
Phase 10: Validation
```

If later stages reveal an error, revise lower-level artifacts explicitly rather than silently changing conclusions.

---

# 26. Coverage Requirement

The entire allowed source file must be read before Task 006 is complete.

However not every paragraph needs to become a SourceUnit or Event.

Codex must document:

```text
covered source scope
selected character-relevant spans
non-selected sections
reason non-selected sections do not materially affect Reirin reconstruction
```

The purpose is to prevent cherry-picking only famous/obvious scenes.

Do not omit contradictory or mundane Reirin behavior merely because it does not fit an emerging pattern.

---

# 27. Evidence Integrity Rules

Hard rules:

1. Plausibility is not canon.
2. Observation ≠ interpretation.
3. Interpretation ≠ persistent trait.
4. Hypothesis ≠ evidence.
5. One Event cannot become its own independent validation through a derived claim.
6. Supporting and contradicting evidence must remain distinguishable.
7. Unknown is valid.
8. Unresolved is valid.
9. Later knowledge cannot validate an earlier state if the earlier character did not have it.
10. Codex's own previous reconstruction text is never source evidence.

---

# 28. Counterevidence Requirement

When creating a Development statement, actively search within the permitted source for:

```text
exceptions
contradictions
context-specific behavior
alternative explanation
```

Do not search outside the permitted file.

If counterevidence exists:

- record it;
- narrow the Development claim if necessary.

If no counterevidence is found:

- say `no counterevidence identified within Task 006 source scope`;
- do not say `no counterevidence exists`.

---

# 29. Temporal Reconstruction Rule

For each Period State ask:

```text
What did Reirin know by this point?
What had Reirin experienced by this point?
Which body was she inhabiting?
Which relationships were active?
Which goals/conflicts were active?
```

Never reconstruct Period 1 using discoveries from Period 2 unless the information was already available in Period 1.

---

# 30. Serialization Requirements

Use Aiko-owned deterministic JSON serialization semantics.

Where practical, use:

```text
ai_friend.reconstruction.serialization.to_portable_json()
```

with explicit:

```text
schema_version
artifact_version
```

Persistent files must be:

- UTF-8;
- portable JSON;
- deterministic enough for useful Git diffs;
- Aiko-schema based;
- independent of an LLM vendor.

Do not serialize arbitrary Python reprs or third-party framework objects.

If multiple artifacts are saved in one JSON file, use a documented Aiko-owned envelope.

---

# 31. Reconstruction Manifest

Create:

```text
agents/AI_friend/Reirin/reconstruction/manifests/reconstruction_v0.1_manifest.json
```

It must summarize at minimum:

```text
character_id
reconstruction_version
framework
architecture_version
source_path
source_role
source_annotation_status
source_hash/version if practical
source_scope
created artifact counts
period IDs/order
validation status
known limitations
unresolved items
```

It must NOT contain an untraceable prose personality summary.

---

# 32. Reirin README

Create/update:

```text
agents/AI_friend/Reirin/README.md
```

It should state:

- this is a character instance generated with Aiko;
- v0.1 source scope;
- current reconstruction status;
- folder ownership;
- how provenance flows;
- that this is incomplete and first-three-chapter-only;
- that Aiko framework lives next to it, not inside Reirin;
- that future source expansion must create a new reconstruction version rather than silently overwriting history.

---

# 33. Validation — MANDATORY

After constructing the complete in-memory reconstruction graph, Codex MUST run:

```python
validate_reconstruction_graph(...)
```

from the Task 005 hardened Aiko framework.

Task 006 is not complete if the graph contains validation errors.

If the generated persisted files cannot be reconstructed into the Aiko dataclasses and validated, the task is incomplete.

Required validation flow:

```text
persistent Reirin files
↓
load / reconstruct Aiko contract objects
↓
ReconstructionGraph
↓
validate_reconstruction_graph()
↓
0 validation errors
```

Do not merely validate a separate synthetic in-memory object while writing unrelated JSON to disk.

The validated graph and the persisted character data must represent the same reconstruction.

---

# 34. Add Character-Instance Validation Test

Add a narrowly scoped test or validation script that verifies Reirin v0.1 files can be loaded into Aiko contracts and pass validation.

Location may follow project convention, for example:

```text
agents/AI_friend/Aiko/tests/
```

or a validation entry point under Reirin if framework tests should remain synthetic-only.

Do NOT put the novel text itself into Aiko tests.

The test may read the Reirin instance files by repository path.

It should check at least:

- source approved;
- SourceUnit grounding valid;
- Event → Observation lineage;
- Period assignment;
- eight Domain slots;
- future-knowledge guard;
- Memory Event references;
- Development cross-period rule;
- skill evidence;
- compiled-state lineage;
- zero hard validation issues.

---

# 35. Do Not Modify Aiko Architecture to Fit the Character

Task 006 is an integration test of Task 005.

Therefore:

```text
Reirin must fit Aiko contracts
```

not:

```text
Aiko contracts are freely changed until Reirin fits.
```

If a real-source case reveals a genuine framework deficiency:

1. document it;
2. make the smallest generic fix;
3. add framework test;
4. explain why it is generic;
5. do not add a Reirin-specific exception to Aiko.

Any Aiko framework modification in Task 006 must be called out prominently in the final report.

---

# 36. Forbidden Reirin-Specific Framework Code

Do NOT add:

```python
if character == "Reirin":
    ...
```

to Aiko.

Do NOT add Reirin-specific constants, event names, speaker names, or source assumptions to generic Aiko package code.

Character-specific content belongs only under:

```text
agents/AI_friend/Reirin/
```

and the approved source remains under:

```text
character_data/Reirin/
```

---

# 37. What NOT to Infer from the First Three Chapters

Task 006 must not claim to establish:

- complete lifetime personality;
- complete relationship graph;
- final stable persona;
- final change resistance;
- complete skill set;
- final speech style;
- post-canon behavior;
- events from later volumes;
- future relationship outcomes.

A strong narrator statement may support a strong bounded claim, but source scope remains explicit.

---

# 38. Expected First-Pass Analytical Questions

The following are prompts for disciplined analysis, NOT pre-decided conclusions:

## Event layer

- What major experiences does Reirin undergo?
- Which experiences materially change her situation, knowledge, body, goal, or relationship state?
- Which observations are directly supported?

## Period layer

- Is the pre-swap state meaningfully distinct from post-swap state?
- Are later transitions within the allowed chapters large enough to justify additional Periods?
- Which boundaries are confirmed vs candidate?

## Character layer

For each Period:

- Personality: what behavior/tendencies are actually supported here?
- Physical: what body/health state is active?
- Motivation: what does she currently want / prioritize?
- Backstory: what past facts are directly relevant to current character formation?
- Emotion: what is explicit vs inferred?
- Relationships: how does she currently treat/understand important others?
- Growth: what has changed relative to a previous Period?
- Conflict: what competing goals/values/tensions are active?

## Development layer

Only across Periods:

- Which patterns persist?
- Which change?
- What historical experience may explain them?
- What alternative explanation exists?
- What remains unresolved?

These questions must not be answered beyond source support.

---

# 39. Acceptance Criteria — Source Layer

Task 006 passes Source-layer acceptance only if:

- [ ] only the approved first-three-chapter file is used;
- [ ] entire allowed file is read;
- [ ] source annotation status is documented;
- [ ] SourceReference is approved for this task;
- [ ] SourceUnits use exact grounding;
- [ ] SourceUnits have deterministic locators;
- [ ] SourceUnits have integrity hashes;
- [ ] no Task 004/reference-note evidence enters the graph.

---

# 40. Acceptance Criteria — Observation / Event

- [ ] Observations are source-supported and narrow.
- [ ] Events derive from Observations.
- [ ] Event segmentation is not mechanically chapter-based.
- [ ] Event count is evidence-driven.
- [ ] Event is stored once.
- [ ] Event does not declare stable personality directly.
- [ ] character-accessible information is distinguished from story-level truth.
- [ ] important uncertainty is retained.

---

# 41. Acceptance Criteria — Period

- [ ] Period boundaries are explicitly reasoned.
- [ ] chapter != Period by default.
- [ ] each Event used in character state has a PeriodAssignment.
- [ ] Period order is valid.
- [ ] candidate/unresolved boundary states are allowed.
- [ ] KnowledgeBoundary is represented.
- [ ] earlier Periods do not use later Events/knowledge.

---

# 42. Acceptance Criteria — Eight Domains

For every Period:

- [ ] Personality exists as a Domain slot.
- [ ] Physical exists.
- [ ] Motivation exists.
- [ ] Backstory exists.
- [ ] Emotion exists.
- [ ] Relationships exists.
- [ ] Growth exists.
- [ ] Conflict exists.
- [ ] unsupported domains explicitly abstain.
- [ ] supported domains reference Event/Evidence.
- [ ] bounded inference is not promoted to permanent trait automatically.
- [ ] body identity and character identity remain distinct.

---

# 43. Acceptance Criteria — Memory

- [ ] relevant Events receive explicit MemoryFormationDecision.
- [ ] persistent decisions have matching MemoryRecord.
- [ ] Memory references Event.
- [ ] Memory does not duplicate Event.
- [ ] inaccessible story facts are excluded.
- [ ] Memory subjective meaning is source-bounded.
- [ ] index metadata is generated for persistent memories.
- [ ] `do_not_persist` is used only when justified, not fabricated to satisfy testing.

---

# 44. Acceptance Criteria — Skills

- [ ] demonstrated skills are evidence-linked.
- [ ] canonical proficiency is conservative.
- [ ] no skill is promoted solely from model knowledge.
- [ ] no runtime capability pack is created.
- [ ] limitations/uncertainty are preserved.
- [ ] skill may be Period-scoped.

---

# 45. Acceptance Criteria — Development

If 2+ valid Period States exist:

- [ ] legitimate cross-period patterns are evaluated.
- [ ] no DevelopmentRecord is based on only one Period.
- [ ] counterevidence is actively checked.
- [ ] confidence and change resistance remain separate.
- [ ] causal claims remain hypotheses.
- [ ] alternative/counterevidence is preserved where applicable.
- [ ] chronic accessibility/habitual processing are omitted if unsupported.

If fewer than 2 legitimate Period States exist:

- [ ] no fake DevelopmentRecord is created merely to satisfy the task.
- [ ] the manifest explains that cross-period analysis is deferred.

---

# 46. Acceptance Criteria — Compiled State

- [ ] CompiledCharacterState exists.
- [ ] current Period State is explicit.
- [ ] historical states are retained.
- [ ] every compiled entry references Period State.
- [ ] Development references are used where relevant.
- [ ] unresolved items are retained.
- [ ] source scope limitation is explicit.
- [ ] compiled state contains no future-volume knowledge.
- [ ] compiled state is not source evidence for itself.

---

# 47. Acceptance Criteria — Filesystem

- [ ] character data lives under `agents/AI_friend/Reirin/`.
- [ ] source remains under `character_data/Reirin/`.
- [ ] no Reirin canon is stored inside `Aiko/`.
- [ ] no eight-domain Event duplication folders are created.
- [ ] directory ownership matches `Aiko/docs/folder_ownership.md`.
- [ ] `.gitkeep` may be removed only when the directory now contains real files.

---

# 48. Acceptance Criteria — Validation / Tests

- [ ] complete Reirin graph passes `validate_reconstruction_graph`.
- [ ] persisted JSON corresponds to validated objects.
- [ ] Aiko framework tests still pass.
- [ ] Reirin instance validation test/script passes.
- [ ] `git diff --check` passes.
- [ ] no generic Aiko regression is introduced.
- [ ] any generic framework fix is documented.

---

# 49. Required Reconstruction Review Report

Create a human-readable report under Reirin, recommended:

```text
agents/AI_friend/Reirin/reconstruction/reconstruction_v0.1_report.md
```

The report must summarize the PROCESS and RESULT without becoming a second canonical character database.

Include:

1. source used;
2. source trust/annotation note;
3. source coverage;
4. SourceUnit count;
5. Observation count;
6. Event count;
7. Event list with one-line descriptions;
8. Period definitions and boundary rationale;
9. Period → Event assignment summary;
10. each Period's 8-Domain coverage status;
11. Memory decisions/counts;
12. skill profiles found;
13. Development records created;
14. Compiled State entry summary;
15. contradictions/counterevidence found;
16. unresolved items;
17. validation result;
18. known limitations;
19. exact source scope warning;
20. any Aiko framework changes.

This report is for human audit.

Canonical machine-readable data remains the Aiko contract files.

---

# 50. Required Final Codex Report

When Task 006 is complete, Codex must report:

## Files

1. all files added under `agents/AI_friend/Reirin/`;
2. all Aiko files modified, if any;
3. tests/scripts added.

## Reconstruction counts

4. SourceReferences;
5. SourceUnits;
6. Observations;
7. Events;
8. EvidenceRecords;
9. Periods;
10. PeriodAssignments;
11. PeriodCharacterStates;
12. Memory decisions;
13. MemoryRecords;
14. SkillEvidence;
15. CharacterSkillProfiles;
16. DevelopmentRecords;
17. CompiledCharacterStates.

## Reasoning controls

18. Period boundary rationale;
19. examples of intentionally abstained Domain fields;
20. examples where an inference was kept bounded rather than promoted;
21. counterevidence/alternative hypotheses retained;
22. future-knowledge leakage checks;
23. source speaker-annotation uncertainty handling.

## Validation

24. `validate_reconstruction_graph()` result;
25. full test results;
26. `git diff --check`;
27. whether persisted files were reloaded and validated.

## Scope confirmation

28. confirmation no later chapters/volumes/wiki/web/Task004 evidence was used;
29. confirmation Aiko contains no Reirin-specific canonical data;
30. confirmation this is only `Reirin v0.1 — first three chapters`.

---

# 51. Failure Conditions

Task 006 must be considered FAILED if any of the following occurs:

```text
source text
→ direct personality summary
```

without Event/Period lineage;

or:

```text
chapter
→ automatically Period
```

without state-based rationale;

or:

```text
Event
→ duplicated into multiple Domain event records
```

or:

```text
one Event
→ permanent trait
```

without cross-period support / explicit strong source statement handled with provenance;

or:

```text
Memory
= duplicate Event
```

or:

```text
future knowledge
→ earlier Period
```

or:

```text
speaker annotation
= blindly treated as infallible canon
```

or:

```text
canonical skill
= runtime capability
```

or:

```text
LLM knowledge
= Reirin knowledge
```

or:

```text
Task 004 output
→ evidence
```

or:

```text
Reirin-specific logic
→ Aiko generic package
```

or:

```text
generated JSON
≠ graph that was actually validated
```

---

# 52. Recommended Execution Sequence

Codex should execute in this order:

```text
Step 1
Read Aiko architecture/contracts/tests.

Step 2
Inspect current Reirin directory.

Step 3
Read the entire approved source file.

Step 4
Register SourceReference.

Step 5
Extract exact SourceUnits.

Step 6
Create Observations.

Step 7
Build Event segmentation.

Step 8
Review Event coverage against entire source.

Step 9
Create Evidence records.

Step 10
Infer candidate Period boundaries from Events.

Step 11
Create PeriodDefinitions + PeriodAssignments.

Step 12
Construct 8-domain PeriodCharacterStates.

Step 13
Create MemoryFormationDecisions + MemoryRecords/index.

Step 14
Extract SkillEvidence + CharacterSkillProfile.

Step 15
Only now perform cross-period Development analysis.

Step 16
Create conservative CompiledCharacterState.

Step 17
Serialize all persistent artifacts.

Step 18
Reload persisted artifacts.

Step 19
Build ReconstructionGraph from persisted data.

Step 20
Run validate_reconstruction_graph().

Step 21
Run Aiko tests / Reirin validation.

Step 22
Create human audit report.

Step 23
Report exact results and unresolved issues.
```

Do not reorder the workflow into a top-down persona-first analysis.

---

# 53. Final Principle

Task 006 should demonstrate:

```text
We did not ask Codex:

"Who is Reirin?"

We asked:

"What exactly does the source show happened?"
        ↓
"What state was Reirin in during each historical period?"
        ↓
"What patterns are actually supported across those periods?"
        ↓
"What conservative character state can Aiko compile from that evidence?"
```

The objective is not maximum personality detail.

The objective is:

```text
maximum traceability
+
temporal correctness
+
evidence discipline
+
minimum unsupported inference
```

If uncertainty remains, preserve uncertainty.

If a Domain lacks evidence, abstain.

If a pattern has only one Event, keep it local.

If the source does not support a conclusion, do not create it.

Only after this first reconstruction passes review should later tasks expand Reirin to more chapters or volumes.
