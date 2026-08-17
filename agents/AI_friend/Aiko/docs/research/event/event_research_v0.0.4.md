# Aiko Event Research Guide v0.0.4

Status: Research Foundation

Suggested location:

```text
docs/research/event/event_research_v0.0.4.md
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


## 0.1 Runtime Complexity Principle

Aiko 應保留完整 Event / Appraisal representation，但不應在每次 interaction 中全量推理。

核心原則：

> Dense representation, sparse activation.

> Deep psychology does not require deep reasoning on every interaction.

因此：

```text
Complete Appraisal Representation
        ↓
Event Screening
        ↓
Salience / Relevance / Ambiguity / Conflict
        ↓
Reasoning Depth Selection
        ↓
Event-specific Active Structures
        ↓
Selective Appraisal
        ↓
Escalate / Stop
```

新的心理學研究成果應先判斷它屬於：

```text
representation
activation condition
processing disposition
runtime state
evidence
consolidated state
```

而不是直接變成「每次 Event 多做一個推理步驟」。

Runtime 應另外研究：

```text
when reasoning is unnecessary
when lightweight appraisal is enough
when deeper retrieval is necessary
when competing interpretations require verification
when processing should stop
```

因此：

> Appraisal depth is a runtime decision, not a fixed property of the appraisal schema.

此問題與：

```text
docs/research/runtime/adaptive_reasoning_control_v0.0.1.md
```

共同研究。

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

## 1.1 Cross-Research Dependency — Evidence Integrity

Event Interpretation 不應把 LLM 產生的心理推論自動視為 canonical truth。

必須維持：

```text
Objective / Source Evidence
        ↓
Observation
        ↓
Character Perception
        ↓
Interpretation
        ↓
Hypothesis / Subjective Meaning
```

其中：

```text
Observation
≠ Interpretation
≠ Psychological Hypothesis
≠ Persistent Character Claim
```

Event research 可以產生：

```text
candidate interpretation
candidate belief update
candidate trait evidence
candidate causal explanation
```

但是否可進入 consolidated Character State，應由 Character Reconstruction / Consolidation 的 evidence rules 決定。

特別需要避免：

```text
Event behavior
→ infer trait X
→ use trait X to explain the same event
→ treat explanation as new proof of trait X
```

因此 Event records 應盡可能保存：

```text
source / provenance
observation
character-accessible information
interpretation
alternative interpretation
confidence
uncertainty
supporting evidence
contradicting evidence
```

具體 validation / attribution / circularity prevention 由：

```text
docs/research/reconstruction/evidence_grounded_reconstruction_v0.0.1.md
```

進一步研究。

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
Source-supported Observation
≠
Derived Causal Interpretation
≠
Objective Event
≠
Character Perception
≠
Character Memory
```

「Objective」不代表 LLM 可以自由補齊缺失的因果關係。

如果來源只支持：

```text
Person B did not reply for two days.
```

則：

```text
B intentionally avoided A.
```

仍然是 inference，而不是 objective event fact。

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

# 4. Research Topic C — Character Perspective and Character-dependent Processing

## Core Question

> How does an objective event become this character's subjective experience?

概念：

```text
Objective Event
        +
Point-in-Time Character State
        ↓
Character-dependent Processing
        ↓
Selective Appraisal
        ↓
Subjective Meaning
```

Character State(t) 至少可能包含：

```text
Current Persona
Beliefs / Values
Goals / Motivation
Relationship State
Relevant Prior Memory
Dynamic State
Knowledge Boundary
Conflicts
Chronic Accessibility
Habitual Processing
```

### Perspective / Knowledge Constraint

角色不可使用：

```text
future canon knowledge
other characters' private thoughts
author-level explanations
information learned only in later periods
```

核心原則：

> Story truth is not automatically character truth.

---

## 4.1 Desires / Goals

角色想要什麼，會影響：

```text
Goal Relevance
Goal Conduciveness
Urgency
Expected Consequence
```

同一 Event 因角色目標不同，可形成不同 Appraisal。

---

## 4.2 Chronic Accessibility

Chronic Accessibility 表示：

> 某些 appraisal-relevant cognitive structures、schemas 或 memories 因長期經驗，在特定角色與時期更容易被喚起。

例如：

```text
Period 1
├── trust_schema: high
├── abandonment_schema: low
└── self_reliance_schema: medium

Period 3
├── trust_schema: low
├── abandonment_schema: high
└── self_reliance_schema: high
```

這允許角色成長表現為：

```text
same event
+
different accessible schemas
=
different interpretation
```

而不必把所有變化都壓成 Trait replacement。

Chronic Accessibility 應與 Point-in-Time Character State 綁定。

---

## 4.3 Habitual Processing

Habitual Processing 表示：

> 角色長期形成的注意、選擇、解釋與資訊組織習慣。

例如：

```text
遇到失敗
→ 優先檢查自己的責任

遇到失約
→ 優先注意承諾是否被尊重
```

Habitual Processing 通常具有較高 change resistance，但不是 immutable。

它與 Trait 有關，但不是 Trait 的同義詞。

```text
Trait:
重視責任

Habitual Processing:
遇到失敗時，習慣先檢查自己的責任。
```

---

## 4.4 Analysis Order

研究與未來 prompting 建議順序：

```text
1. What objectively / perceptually happened?
2. What did this character have access to?
3. Which memories / schemas became accessible?
4. Which goals / beliefs / values / relationships were touched?
5. Which habitual processing tendencies bias attention?
6. Which appraisal dimensions are salient?
7. What does the event mean to this character?
8. What competing interpretations remain possible?
9. With what confidence?
```

輸出應區分：

```text
Observation
Interpretation
Assumption
Inference
Expectation
Evaluation
Meaning
```

Possible outputs:

```text
Aiko Character Perspective Contract
Aiko Character-dependent Processing Model
```

---

# 5. Research Topic D — Selective Appraisal, Emotion, Decision, and Behavior

## Core Question

> Given this character's interpretation, which psychological evaluations are relevant, and how do they shape emotion and behavior?

不要：

```text
Event X → Emotion Y
```

採用：

```text
Subjective Event Meaning
+
Character State
        ↓
Selective Appraisal
        ↓
Emotion / Action Tendency
        ↓
Decision / Behavior
```

---

## 5.1 Multi-dimensional Appraisal

目前 Appraisal representation 採用四大類：

```text
Appraisal
├── 1. Relevance
├── 2. Implications
├── 3. Coping Potential
└── 4. Normative Significance
```

### Relevance

```text
Novelty
Intrinsic Pleasantness
Goal Relevance
```

### Implications

```text
Agency / Cause
Predictability
Expectation Discrepancy
Goal Conduciveness
Urgency
```

### Coping Potential

```text
Control
Power
Adjustment
```

### Normative Significance

```text
Internal Standards
External Standards
Fairness
```

這些維度應視為完整 representational space，而不是每次 interaction 的 mandatory questionnaire。

---

## 5.2 Salience Gate

Event 在進入深度 Appraisal 前，先判斷：

```text
Which character domains matter?
Which appraisal dimensions matter?
Which memories matter?
How important is this event?
```

概念：

```text
Event
↓
Salience / Relevance Gate
↓
Selective Activation
↓
Selective Appraisal
```

事件可暫分：

```text
Level 0 — Trivial
Level 1 — Lightweight
Level 2 — Contextually Important
Level 3 — Character-forming
```

### Level 0

```text
minimal interpretation
no persistent analysis
```

### Level 1

可能只啟動：

```text
Relevance
Pleasantness
Relationship Context
```

### Level 2

可能啟動：

```text
Implications
Expectation Discrepancy
Fairness
Relationship
Relevant Memory
```

### Level 3

啟動：

```text
broad / deep appraisal
deep memory retrieval
causal analysis
conflict analysis
relationship update
possible trait evidence
possible persona consolidation
```

---

## 5.3 Evidence-driven Escalation

先做 lightweight pass。

若發現：

```text
high conflict
high emotion
persona contradiction
relationship criticality
identity / value relevance
unexpected behavior
major consequence
```

才升級：

```text
Deep Appraisal
+
Causal Retrieval
+
Memory Analysis
```

因此：

> Important events receive deep reasoning; ordinary events do not pay the same cost.

---

## 5.4 Adaptive Appraisal Depth

Salience Gate 之外，仍需要一個獨立問題：

> How much reasoning does this event actually require?

候選判斷因素：

```text
salience
ambiguity
prediction error
relationship criticality
identity / value relevance
persona contradiction
emotional intensity
consequence magnitude
uncertainty
need for causal explanation
```

概念上：

```text
Event Screening
        ↓
Low ambiguity + low importance
        → minimal processing

Moderate relevance
        → selective appraisal

High ambiguity / conflict / consequence
        → deeper retrieval + competing hypotheses + verification
```

重要原則：

> More appraisal dimensions in representation must not imply more mandatory runtime steps.

> Deep processing should be triggered by evidence of need, not by schema size.

> The system should be able to stop early when additional reasoning is unlikely to change the interpretation or response.

具體 activation / escalation / stopping policy 屬於：

```text
docs/research/runtime/adaptive_reasoning_control_v0.0.1.md
```

---

## 5.5 Subjective Meaning

Appraisal 不應只輸出 emotion label。

可表示：

```text
Subjective Meaning
├── interpretation
├── expectation
├── evaluation
├── perceived threat / opportunity
├── relationship implication
├── value implication
├── uncertainty
└── confidence
```

允許 competing interpretations coexist。

---

## 5.6 Emotion / Intention / Behavior

```text
Subjective Meaning
+
Current State
+
Motivation
+
Conflict
+
Coping / Defense Tendencies
        ↓
Emotion
        ↓
Action Tendency
        ↓
Decision / Behavior
```

內在反應與外顯 behavior 應分開。

Possible outputs:

```text
Aiko Salience Gate
Aiko Appraisal Contract
Aiko Decision / Behavior Contract
```

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


# 6.1 Processing Disposition Updates

## Chronic Accessibility Update

不是每個 Event 都改變 accessibility。

候選因素：

```text
repetition
high emotional intensity
major relationship event
identity / value relevance
strong prediction error
long-term reinforcement
```

理想流程：

```text
Memory History
↓
Reconstruction / Offline Consolidation
↓
Accessibility Profile(period_t)
```

Runtime 不應每次從全部 Memory 重新估算。

## Habitual Processing Update

Habitual Processing 通常具有較高 change resistance。

更新應考慮：

```text
Repeated behavior
Repeated appraisal pattern
Major one-time event
Contradictory evidence
Long-term period transition
```

避免：

```text
one event
→ permanent processing habit
```

Possible outputs:

```text
Aiko Accessibility Update Contract
Aiko Habitual Processing Update Contract
```

---


# 6.2 Temporal Consequence Layers

Event consequences should not be forced directly into a single Persona timeline.

A working research distinction is:

```text
Event
↓
Immediate Dynamic State
↓
Repeated / meaningful consequences
↓
Historical Adaptation
↓
Possible Persistent Character Structure
```

This is not yet a finalized schema.

Important distinction:

```text
Past Period Memory
≠
Historical Adaptation
≠
Current Persistent Structure
```

Historical periods should preserve what happened and what was active at the time, while long-term character structure should represent only sufficiently consolidated patterns.

Research questions:

1. What separates temporary state from medium-term adaptation?
2. How much repetition or duration is required?
3. Can one highly significant event create a medium-term adaptation without immediately changing persistent structure?
4. How does context-specific learning become generalized?
5. How should counterevidence reverse or narrow an adaptation?
6. How should a past Character State(t) be reconstructed without storing a complete independent Persona Card?
7. Which temporal effects belong to Memory / Timeline versus Character Core?

This topic is coordinated with:

```text
docs/research/character/temporal_character_development_v0.0.1.md
```

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

```text
Raw Source / Real-world Input
        ↓
[A] Event Identification
        ↓
[B] Objective Event
        ↓
[C] Character Perspective
        ↓
Salience Gate
        ↓
Character-dependent Processing
├── Desires / Goals
├── Chronic Accessibility
└── Habitual Processing
        ↓
Selective Appraisal
├── Relevance
├── Implications
├── Coping Potential
└── Normative Significance
        ↓
Subjective Meaning
        ↓
Emotion / Intention / Behavior
        ↓
Outcome
        ↓
Memory / Relationship / Belief Consequences
        ↓
Evidence Accumulation
        ↓
Optional Persistent Character Update
```

---

## 8.1 Three-Layer Runtime Model

```text
Layer 1 — Event Screening
├── What happened?
├── Is it important?
├── Which Character domains matter?
├── Which memories matter?
└── Which appraisal dimensions may matter?

Layer 2 — Selective Appraisal
├── Relevant Character Context
├── Relevant Memory
├── Desires / Goals
├── Chronic Accessibility
├── Habitual Processing
└── Salient Appraisal Dimensions
        ↓
Subjective Meaning

Layer 3 — Consolidation
├── transient only?
├── episodic memory?
├── subjective insight?
├── relationship update?
├── belief update?
├── trait evidence?
├── chronic accessibility update?
├── habitual processing update?
└── persona consolidation?
```

---

## 8.2 Reconstruction-time vs Runtime

### Reconstruction / Consolidation Time

允許昂貴：

```text
full event analysis
multi-dimensional appraisal
cross-period comparison
causal reasoning
trait consolidation
accessibility update
habitual processing extraction
relationship history analysis
```

### Runtime

優先：

```text
event screening
compiled character retrieval
relevant memory retrieval
selective appraisal
response generation
```

因此：

> Deep psychology can be compiled into character state and retrieved on demand.

---

## 8.3 Compiled Character State Interface

Event Runtime 不應每次讀取所有歷史 Event。

優先使用：

```text
Compiled Character State
├── current traits
├── active beliefs
├── values / goals
├── relationship summary
├── chronic accessibility
├── habitual processing
├── unresolved conflicts
├── dynamic state
└── supporting evidence links
```

需要 deeper reasoning 時，再回溯 evidence。

---

# 9. Recommended Research Order

目前 Event research 優先順序更新為：

```text
1. Event Identification / Segmentation
2. Objective Event Representation + Evidence Separation
3. Character Perspective / Knowledge Boundary
4. Character-dependent Processing
   ├── Desires / Goals
   ├── Chronic Accessibility
   └── Habitual Processing
5. Appraisal Representation
6. Salience Gate / Selective Activation
7. Adaptive Reasoning Depth / Escalation / Stopping
8. Subjective Meaning + Competing Interpretations
9. Emotion / Intention / Behavior
10. Memory Formation
11. Temporal Consequence Layers
12. Processing Disposition Updates
13. Evidence Accumulation / Long-Term Change
```

其中最高優先級仍是：

```text
Objective Event
        ↓
Point-in-Time Character Perspective
        ↓
Subjective Meaning
```

但實作上必須同時研究：

```text
How much reasoning is necessary for this event?
```

以避免 Event framework 隨理論增加而變成每次 interaction 的全量心理學模擬。

---

## 9.1 Integration with Character Reconstruction

Event Research 同時服務 Character Reconstruction。

推薦流程：

```text
Seed Character
        ↓
Representative Event Set
        ↓
Deep Event Analysis
        ↓
Trait / Belief / Relationship Evidence
        ↓
Appraisal Pattern Extraction
        ↓
Chronic Accessibility Extraction
        ↓
Habitual Processing Extraction
        ↓
Character Consolidation
        ↓
More Events
        ↓
Validation / Refinement
```

因此可以先以少量高資訊場景建立初步角色，再逐步加入更多 Event。

---

# 10. Research Outputs

This research line should eventually produce:

```text
docs/research/event/
├── event_research_v0.0.1.md
├── event_segmentation.md
├── objective_event_representation.md
├── character_perspective.md
├── appraisal_model.md
├── salience_and_activation.md
├── emotion_and_behavior.md
├── memory_formation.md
├── accessibility_and_habits.md
└── evidence_and_character_change.md

Cross-cutting research dependencies:

docs/research/reconstruction/
└── evidence_grounded_reconstruction_v0.0.1.md

docs/research/character/
└── temporal_character_development_v0.0.1.md

docs/research/runtime/
└── adaptive_reasoning_control_v0.0.1.md
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
Aiko Salience Gate
Aiko Appraisal Contract
Aiko Event → Memory Contract
Aiko Event → Persona Evidence Contract
Aiko Accessibility Update Contract
Aiko Habitual Processing Update Contract
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
Full Appraisal = Mandatory every turn
More psychological dimensions = More runtime steps
LLM inference = Source evidence
Plausible explanation = Canonical explanation
Historical period = Independent permanent Persona Card
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


新增目前階段的 Event Runtime 原則：

> Appraisal should be multi-dimensional in representation but selectively activated at runtime.

> Chronic Accessibility is period-dependent and can encode character growth without requiring every change to become a trait change.

> Habitual Processing represents relatively stable attention and interpretation tendencies and should normally change slowly.

> Important events should trigger evidence-driven escalation rather than forcing deep analysis for all events.

> Dense representation, sparse activation.

> Deep psychology does not require deep reasoning on every interaction.


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
