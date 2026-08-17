# Aiko Event Research Guide v0.0.2

Status: Research Foundation

Suggested location:

```text
docs/research/event/event_research_v0.0.2.md
```

---

# 0. Purpose

This document defines the research foundation for how events affect a persistent virtual character.

This research is intentionally **character-agnostic**.

The goal is not to encode how one specific character reacts to one specific event.

Instead, the goal is to define a reusable mechanism in which:

```text
Event
+
Current Character State
+
Beliefs / Values / Motivation
+
Relationship Context
+
Relevant Prior Experience
        ↓
Subjective Interpretation
        ↓
Emotion / Decision / Behavior
        ↓
Outcome
        ↓
Memory / Belief Update / Evidence
        ↓
Possible Long-Term Character Change
```

The same event may therefore produce different results for:

- different characters;
- the same character at different life periods;
- the same character with different prior memories;
- the same character under different relationship or psychological states.

Core principle:

> Events do not directly change personality.

Instead:

> Events are interpreted through the existing character. Their interpreted consequences may create memories, update beliefs, alter relationships, generate trait evidence, and only later contribute to persistent Persona change.

The central reasoning question is therefore not:

> What would a normal person feel?

or even only:

> What would this character do?

It is:

> Given what this character currently knows, believes, remembers, values, fears, wants, and feels, what does this event mean to this character?

The Event system should help a general-purpose LLM reason from the character's point of view rather than merely imitate a static character description.

---

# 1. Research Boundary

Event research should remain separate from the final implementation of:

```text
Character Core
Memory
Knowledge
Relationship
Emotion
Skills
Perception
```

Event research defines the **transformation process between an occurrence and its effects on those systems**.

Conceptually:

```text
External / Narrative Reality
        ↓
Event Processing
        ↓
Character-specific consequences
        ↓
Subsystem updates
```

Therefore Event research should answer:

> What happened?

> What did the character perceive?

> What did the character think it meant?

> What did the character feel and do?

> What changed because of it?

It should not permanently own all resulting data.

---

# 2. Research Topic A — Event Identification and Segmentation

## Core Question

> What counts as one meaningful event?

Source material may contain:

```text
novel paragraphs
dialogue
anime scenes
real-world conversation
screen activity
audio
MIDI
system events
```

These streams do not naturally arrive as clean event records.

Research should determine how to identify:

```text
event start
event end
participants
actions
objects
location
time
outcome
sub-events
```

Important questions:

1. When should multiple actions be treated as one event?
2. When should one scene be split into several events?
3. How should nested events be represented?
4. How should dialogue turns be grouped into a meaningful interaction?
5. How should incomplete or uncertain events be represented?
6. How should events from different modalities be merged?

Possible output:

```text
Aiko Event Boundary Model
```

This topic should eventually support:

```text
Raw Source
    ↓
Event Segmentation
    ↓
Objective Event Record
```

---

# 3. Research Topic B — Objective Event Representation

## Core Question

> What objectively happened, independent of any character's interpretation?

The system needs a neutral event layer before subjective interpretation.

Possible information:

```text
Event
├── event_id
├── timestamp / period
├── participants
├── actions
├── objects
├── location
├── statements
├── observed outcome
├── temporal links
├── causal links
├── source / provenance
└── uncertainty
```

Important distinction:

```text
Objective Event
≠
Character Perception
≠
Character Memory
```

Example:

```text
Objective:
Person B did not reply for two days.

Character A interpretation:
"B is avoiding me."

Possible actual reason:
B was afraid to reply.
```

Research questions:

1. Which fields belong in a universal event representation?
2. How should uncertainty and conflicting sources be represented?
3. How should temporal order be represented?
4. How should causal relationships be represented?
5. How much information belongs in the Event itself versus Knowledge or Memory?
6. How should provenance link back to source material?

Possible output:

```text
Aiko Objective Event Schema v1
```

---

# 4. Research Topic C — Character Perception and Subjective Interpretation

## Core Question

> How does an objective event become this character's subjective experience?

This is the central bridge between Event and Character.

Conceptually:

```text
Objective Event
        +
Current Persona
        +
Beliefs / Values
        +
Motivation
        +
Relationship State
        +
Relevant Prior Memory
        +
Current Psychological State
        ↓
Subjective Cognition / Interpretation
```

The interpretation should be able to differ across characters and time periods.

This research should explicitly model the difference between a static persona descriptor and a character-grounded reasoning state.

A static description may say:

```text
proud
responsible
guarded
cares about friends
```

but this alone does not explain a response. The system must recover the causal perspective active at that moment:

```text
What does the character know?
What does the character not know?
What is the character trying to protect or achieve?
Which memories are activated?
Which beliefs and values are relevant?
What relationship history matters?
What outcomes does the character expect?
What options feel possible or impossible?
```

Only after these questions should it infer the event's meaning.

A useful conceptual form is:

```text
Interpretation(t)
=
f(Perceived Event(t), Point-in-Time Character State(t))
```

where Character State(t) includes only information available to the character at that time.

### Perspective / Knowledge Constraint

The character must not reason from omniscient story knowledge.

Exclude unless actually available to the character:

```text
future canon knowledge
other characters' private thoughts
author-level explanations
information learned only in later periods
```

Core rule:

> Character truth is bounded by character access, not by everything the system knows.

### Analysis Heuristic

For research and future runtime prompting, prefer this order:

```text
1. What objectively / perceptually happened?
2. What did this character actually have access to?
3. Which memories and prior experiences became relevant?
4. Which beliefs / values / goals / relationships / conflicts were touched?
5. What consequences would the character expect?
6. What does the event therefore mean from this character's perspective?
7. What competing interpretations remain possible?
8. With what confidence?
```

This reasoning trace should be treated as inferred character cognition, not automatically as canonical fact.

Research should distinguish at least:

```text
Observation
Interpretation
Assumption
Inference
Expectation
Evaluation
Meaning
```

Important questions:

1. What information was actually visible to the character?
2. What did the character already believe?
3. Which prior experiences were activated?
4. How did relationship context bias interpretation?
5. How should misunderstanding be preserved?
6. How should confidence in an interpretation be represented?
7. Can multiple competing interpretations coexist?

Possible output:

```text
Aiko Event Interpretation Model
Aiko Character Perspective Contract
```

Core principle:

> Story truth is not automatically character truth.

---

# 5. Research Topic D — Emotion, Decision, and Behavior

## Core Question

> Given a subjective interpretation, how does the character respond?

Avoid a fixed rule such as:

```text
Event X
→ Emotion Y
```

Prefer:

```text
Subjective Interpretation
+
Goals
+
Values
+
Relationship
+
Current State
+
Coping / Defense Tendencies
        ↓
Appraisal
        ↓
Emotion
        ↓
Intention / Decision
        ↓
Behavior
```

### Appraisal as the Character-Specific Bridge

Appraisal should be studied as the mechanism that evaluates what an interpreted event means for the character's concerns.

Candidate dimensions include, without locking the schema prematurely:

```text
relevance / importance
goal congruence or obstruction
agency / responsibility
coping potential
expected future consequences
compatibility with values / identity
relationship implications
uncertainty
```

The important point is not to hard-code a universal emotion table. It is to ask how the same event receives different evaluations because Character State differs.

```text
Same Event
+ Character State A
→ Appraisal A
→ Emotion / Behavior A

Same Event
+ Character State B
→ Appraisal B
→ Emotion / Behavior B
```

This is the main mechanism by which identical external reality becomes different subjective experience.

Research questions:

1. How should emotion arise from appraisal rather than event labels?
2. How should multiple simultaneous emotions be represented?
3. How should motivation and conflict affect decisions?
4. How should defense tendencies or coping strategies influence behavior?
5. How should a character choose between competing goals?
6. How should internal reaction and visible behavior differ?
7. How should temporary psychological state influence behavior without rewriting Persona?

Possible outputs:

```text
Aiko Appraisal / Emotion Contract
Aiko Decision / Behavior Contract
```

This research does not require a final psychological simulator.

The first goal is to define the information flow and responsibilities.

---

# 6. Research Topic E — Event Consequences and Memory Formation

## Core Question

> What should be retained after an event?

Not every observation should become a permanent memory.

Possible consequences include:

```text
Event Consequences
├── no persistent change
├── temporary runtime state
├── factual memory
├── subjective memory
├── learned knowledge
├── relationship change
├── belief update
├── unresolved conflict
├── skill experience
└── trait evidence
```

Research questions:

1. Which events deserve persistent memory?
2. What information should be stored as objective fact?
3. What should be stored as subjective interpretation?
4. Should the character remember emotion separately from factual content?
5. How are contradictions handled?
6. How does an event update relationship state?
7. When does experience become learned knowledge?
8. How should importance, novelty, repetition, and recency affect retention?
9. How should forgetting or consolidation work later?

Possible outputs:

```text
Aiko Event → Memory Contract
Aiko Experience Record Model
```

Important principle:

> One event is not necessarily one memory.

One event may create multiple records across different systems.

---

# 7. Research Topic F — Evidence Accumulation and Long-Term Character Change

## Core Question

> When does experience become persistent character change?

This topic connects Event research back to Character Core.

The system should avoid:

```text
single event
→ permanent trait
```

Prefer:

```text
Event
    ↓
Trait / Belief / Relationship Evidence
    ↓
Accumulation
    ↓
Counterevidence
    ↓
Change Evaluation
    ↓
Possible Persistent Update
```

Research questions:

1. What qualifies as Trait Evidence?
2. How should repeated events accumulate?
3. How should counterevidence weaken a hypothesis?
4. How should evidence interact with Trait Change Resistance?
5. How should major one-time events differ from repeated minor experiences?
6. How should changes be assigned to life periods?
7. How should causal links to past events be preserved?
8. When should an update affect:
   - current state only;
   - relationship state;
   - belief;
   - motivation;
   - conflict;
   - Growth;
   - persistent Persona?

Possible outputs:

```text
Aiko Event → Persona Evidence Contract
Aiko Evidence Accumulation Model
Aiko Persona Consolidation Trigger Model
```

This topic should not directly implement Persona Consolidation until Character Core and Event research agree on a stable contract.

---

# 8. Integrated Research Pipeline

The six topics should eventually connect into:

```text
Raw Source / Real-world Input
        ↓
[A] Event Identification
        ↓
[B] Objective Event
        ↓
[C] Character Perspective / Interpretation
        ↓
[D] Emotion / Decision / Behavior
        ↓
Outcome
        ↓
[E] Memory / Relationship / Knowledge consequences
        ↓
[F] Evidence accumulation
        ↓
Possible controlled long-term Character change
```

A more detailed view:

```text
Objective Event
      ↓
Character-accessible Perception
      ↓
Point-in-Time Character Context
├── Current Persona
├── Beliefs / Values / Motivation
├── Relationship State
├── Relevant Prior Memory
├── Dynamic State
└── Knowledge Boundary
      ↓
Subjective Cognition / Interpretation
      ↓
Appraisal
      ↓
Emotion
      ↓
Intention / Decision / Behavior
      ↓
Outcome
      ↓
Experience Encoding
├── Memory
├── Knowledge
├── Relationship
├── Runtime State
├── Belief
└── Skill Experience
      ↓
Evidence
      ↓
Possible Persona Consolidation
```

---

# 9. Recommended Research Order

Research these topics in the following order:

```text
1. Event Identification / Segmentation
2. Objective Event Representation
3. Character Perspective / Subjective Cognition
4. Emotion / Appraisal / Decision
5. Memory Formation / Event Consequences
6. Evidence Accumulation / Long-Term Character Change
```

Reason:

```text
You cannot study:
"How does an event change personality?"

until you first define:

"What is the event?"
"What did the character perceive?"
"What did the character think happened?"
"What consequence was retained?"
```

The highest-priority conceptual research is therefore:

```text
Objective Event
        ↓
Subjective Character Interpretation
```

because this is the point where identical external reality becomes different character experience.

---

# 10. Research Outputs

This research line should eventually produce:

```text
docs/research/event/
├── event_research_v0.0.1.md
├── event_segmentation.md
├── objective_event_representation.md
├── subjective_interpretation.md
├── emotion_and_behavior.md
├── memory_formation.md
└── evidence_and_character_change.md
```

After research matures, accepted results can be promoted into:

```text
docs/architecture/
```

Then implementation-facing contracts can be defined in:

```text
docs/schemas/
```

Possible mature deliverables:

```text
Aiko Event Schema v1
Aiko Character Perspective Contract
Aiko Event Interpretation Pipeline
Aiko Event → Memory Contract
Aiko Event → Persona Evidence Contract
Aiko Evidence Accumulation Model
```

Only after these are stable should a future Codex task implement them.

---

# 11. Research Guardrails

Do not assume:

```text
Event = Memory
Event = Emotion
Event = Trait change
Objective truth = Character belief
LLM interpretation = Canonical truth
One observation = Stable Persona evidence
```

Always preserve the distinction:

```text
Reality
↓
Perception
↓
Interpretation
↓
Response
↓
Memory
↓
Evidence
↓
Possible long-term change
```

Prefer mechanisms that preserve:

```text
uncertainty
subjectivity
contradiction
history
counterevidence
causal provenance
different time periods
```

Avoid mechanisms that prematurely collapse them into one summary.

---

# 12. Core Research Principle

The central Event research hypothesis for Aiko is:

> A character is not changed directly by events. A character changes through the way events are perceived, interpreted, remembered, and accumulated over time.

Therefore the long-term research target is not merely:

```text
Event → Persona
```

but:

```text
Event
× Existing Character
× Prior Experience
× Relationship Context
× Current State
        ↓
Subjective Experience
        ↓
Memory / Learning / Evidence
        ↓
Gradual Character Formation
```

This Event research layer should remain reusable across different characters.

A specific character supplies the state through which the event is interpreted; the Event framework itself should not contain that character's personality.

The long-term objective is therefore not only faithful reenactment of canon reactions. Canon reconstructs the character's historical starting state; after that point, new experiences can continue to be processed through the same mechanism:

```text
Canon History
    ↓
Reconstructed Character State(t0)
    ↓ new event
Interpretation / Appraisal
    ↓
Experience / Memory / Evidence
    ↓
Character State(t1)
    ↓ new event
...
```

This is the conceptual transition from a character-aware chatbot to a persistent character capable of longitudinal development.
