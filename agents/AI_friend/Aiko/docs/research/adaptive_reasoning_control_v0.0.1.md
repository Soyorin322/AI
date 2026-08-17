# Aiko Adaptive Reasoning Control Research v0.0.1

Status: Research Foundation

Suggested location:

```text
docs/research/runtime/adaptive_reasoning_control_v0.0.1.md
```

---

# 0. Purpose

This research line studies how Aiko can maintain a rich psychological representation without forcing every interaction through the same deep reasoning pipeline.

Core principle:

> Dense representation, sparse activation.

> Deep psychology does not require deep reasoning on every interaction.

Primary risk:

```text
more psychology research
→ more representation dimensions
→ more mandatory runtime steps
→ higher latency / token cost
→ over-engineered behavior
```

Aiko should break that chain.

---

# 1. Research Boundary

This research does not define the final appraisal theory.

It studies:

```text
when to reason
what to activate
how deeply to reason
when to retrieve more evidence
when to escalate
when to stop
```

It coordinates with:

```text
Event Interpretation
Character Runtime
Memory Retrieval
Character Context Builder
LLM Provider
```

---

# 2. Research Topic A — Event Screening

Before deep processing, estimate whether the event requires psychological reasoning.

Candidate signals:

```text
importance
novelty
ambiguity
relationship relevance
identity / value relevance
prediction error
emotional intensity
consequence magnitude
persona contradiction
causal uncertainty
```

Possible outcome:

```text
Trivial
Lightweight
Contextually Important
Character-Critical
```

The level system itself is not yet canonical.

---

# 3. Research Topic B — Selective Activation

A rich representation may contain many structures:

```text
traits
beliefs
values
goals
relationships
memories
chronic accessibility
habitual processing
appraisal dimensions
conflicts
skills
```

Runtime should activate only those likely to change the interpretation or response.

Research questions:

1. How should activation candidates be selected?
2. Retrieval before appraisal or appraisal before retrieval?
3. How should chronic accessibility bias selection without becoming a static prompt?
4. How should relationship context influence activation?
5. How can missing but important context trigger deeper retrieval?

---

# 4. Research Topic C — Adaptive Reasoning Depth

Candidate flow:

```text
Event Screening
↓
Minimal interpretation
↓
if sufficient → respond

otherwise
↓
Selective Appraisal
↓
if sufficient → respond

otherwise
↓
Deep Retrieval
+
Competing Hypotheses
+
Causal / Historical Analysis
↓
respond / consolidate evidence
```

Questions:

1. What makes a lightweight pass sufficient?
2. How should ambiguity trigger depth?
3. Should reasoning depth depend on action consequence?
4. How should latency/token budget constrain depth?
5. Can critical events override budget constraints?

---

# 5. Research Topic D — Escalation Triggers

Candidate escalation triggers:

```text
high conflict
high uncertainty
persona contradiction
relationship criticality
identity / value challenge
unexpected behavior
major consequence
strong prediction error
multiple plausible interpretations
need for historical explanation
```

Important:

> Escalation must be evidence-driven, not schema-driven.

---

# 6. Research Topic E — Early Stopping

Aiko needs a stopping rule.

Additional reasoning should stop when:

```text
interpretation is sufficiently stable
remaining uncertainty does not affect behavior
retrieved evidence is redundant
additional appraisal dimensions are irrelevant
cost exceeds expected decision value
```

Research questions:

1. How can "sufficiently stable" be estimated?
2. How should confidence interact with stopping?
3. When should uncertainty be preserved rather than resolved?
4. How should high-stakes character updates require stricter stopping criteria?

---

# 7. Research Topic F — Reconstruction-Time vs Runtime Cost

Expensive reasoning should move offline when possible.

```text
Reconstruction / Consolidation Time
├── deep cross-event analysis
├── causal comparison
├── evidence validation
├── historical synthesis
└── compiled state generation

Runtime
├── event screening
├── selective retrieval
├── selective appraisal
└── response generation
```

Core question:

> Which psychological work can be compiled into reusable character state?

---

# 8. Research Topic G — Failure Modes

### Underthinking

```text
important event
→ shallow interpretation
→ character-inconsistent response
```

### Overthinking

```text
trivial interaction
→ deep appraisal
→ unnecessary latency
→ unnatural behavior
```

### Schema domination

```text
model answers the psychological checklist
instead of behaving naturally as the character
```

### Retrieval explosion

```text
every weak signal
→ more memories
→ more traits
→ more appraisal
→ context overload
```

Research should explicitly test all four.

---

# 9. Evaluation

Candidate evaluation dimensions:

```text
character fidelity
response naturalness
latency
token usage
retrieval count
reasoning depth
unnecessary escalation rate
missed escalation rate
behavioral consistency
```

Compare:

```text
A. fixed full appraisal
B. no appraisal
C. adaptive appraisal
```

The adaptive mechanism is only valuable if it improves fidelity/cost tradeoffs.

---

# 10. Integration with Event Research

Event Research owns the semantic process:

```text
Event
→ Character Perspective
→ Appraisal
→ Subjective Meaning
```

Adaptive Reasoning Control decides:

```text
how much of that process is active now
```

Therefore:

```text
Appraisal Representation
≠
Runtime Execution Plan
```

---

# 11. Research Guardrails

Do not assume:

```text
more reasoning = better reasoning
more retrieved memory = better character fidelity
all appraisal dimensions matter
all uncertainty must be resolved
every event deserves consolidation
```

Prefer:

```text
selective activation
evidence-driven escalation
early stopping
uncertainty preservation
offline consolidation
measured evaluation
```

---

# 12. Core Research Question

> How can Aiko selectively spend reasoning effort only where it materially improves character-grounded interpretation, while keeping ordinary interaction fast, natural, and inexpensive?
