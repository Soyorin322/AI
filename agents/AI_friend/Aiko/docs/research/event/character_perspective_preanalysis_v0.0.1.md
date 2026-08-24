# Character Perspective Pre-Analysis v0.0.1

Status: Initial implementation contract / research stage

Location:

```text
agents/AI_friend/Aiko/docs/research/event/character_perspective_preanalysis_v0.0.1.md
```

---

# 0. Purpose

This stage is executed **after source-side Event preparation and before character analysis**.

Its purpose is to prevent story-level truth from being silently treated as character-level knowledge while still allowing the LLM to read the complete Event context.

The stage answers two different questions in sequence:

```text
1. What information is available to the target character?
2. Given that information and the character's existing state, what does the character know, believe, suspect, or misunderstand?
```

It does **not** yet answer:

```text
What personality trait does this prove?
What long-term Character State should change?
What psychological interpretation is canonical?
```

Those belong to later Character Interpretation / Reconstruction stages.

---

# 1. Pipeline Position

```text
data_processing
────────────────────
Canon
↓
Event segmentation
↓
source_ranges
participants
narrative_order
story_chronology


Aiko
────────────────────
Complete Event
        ↓
Perspective Pass
        ↓
┌──────────────────────┐
│ Accessible           │
│ Inaccessible         │
│ Uncertain            │
└──────────────────────┘
        ↓
Character Inference
        ↓
┌──────────────────────┐
│ Known                │
│ Believed             │
│ Suspected            │
│ Misunderstood        │
└──────────────────────┘
        ↓
Character Interpretation
        ↓
Evidence
        ↓
Period Character State
```

Core boundary:

> `data_processing` prepares complete, traceable Event material. Aiko owns character perspective and knowledge-state reasoning.

---

# 2. Why Full Event Context Is Preserved

The previous line-level access approach can produce a sparse character-only text such as:

```text
34-35
38-41
55-57
67
69
71
76-77
```

Although conservative, this can remove subjects, causal links, conversational context, action continuity, and narrator structure.

Therefore this stage does **not** physically replace the Event with only accessible lines.

Instead:

```text
Full Event Context
+
Character Perspective Constraint
```

The full source remains available to the analysis model for scene comprehension, while inaccessible information must not be attributed to the target character.

Core distinction:

```text
Context available to the analysis model
≠
Knowledge available to the character
```

This design is motivated by work such as PICTURE (ACL 2026), which explores explicit representation of what a character does and does not know instead of relying only on event hiding.

This is still a research-sensitive mechanism: seeing inaccessible information may cause leakage, so the output requires validation and human-review support.

---

# 3. Stage A — Perspective Pass

The Perspective Pass should be as independent from personality interpretation as possible.

It primarily uses:

```text
complete Event context
speaker / thinker identity
participants
presence / absence when source-supported
explicit information transmission
prior validated knowledge state when necessary
story chronology
```

It should avoid using personality claims unless strictly required.

## 3.1 Output classes

### Accessible

Information directly available to the target character at this point.

Typical examples:

```text
own actions
own speech
own explicit thoughts
speech directly heard
observable actions / events
explicitly received information
own bodily experience
public environmental information directly experienced
```

### Inaccessible

Information present in the Event context but not available to the target character.

Typical examples:

```text
another character's private thought
private conversation while target character is absent
narrator-only omniscient explanation
future revelation
hidden motive not externally revealed
information learned only later
```

### Uncertain

Cases where source evidence does not justify a reliable accessible / inaccessible decision.

Examples:

```text
unclear whether the character could hear the exchange
ambiguous observation target
implicit non-verbal cue with uncertain visibility
uncertain chronology / presence
```

`Uncertain` is mandatory as a first-class result. The model must not be forced to convert every ambiguous case into a binary decision.

---

# 4. Stage B — Character Inference

Perspective access and character inference are different stages.

```text
Accessible Information
≠
What the character concludes from that information
```

Character Inference may use validated character state, prior memories, relationship history, beliefs, relevant knowledge, and reasoning tendencies.

Its current output classes are:

### Known

The character has sufficiently direct or established support for the proposition.

### Believed

The character accepts a proposition as true, although the proposition may be objectively false or incompletely supported.

### Suspected

The character considers a proposition plausible but has not committed to it as known or believed.

### Misunderstood

The character forms an incorrect or materially distorted understanding relative to story-level truth.

Important:

> `Misunderstood` is not an error in reconstruction when the source supports that the character misunderstood the situation.

The objective of this stage is character fidelity, not omniscient correctness.

---

# 5. Separation From Character Interpretation

This stage must stop before personality interpretation.

Allowed:

```text
Reirin heard statement X.
Reirin did not hear statement Y.
Reirin suspects that Keigetsu is hiding something.
Reirin believes proposition Z.
```

Not allowed as this stage's final conclusion:

```text
Reirin is compassionate.
Reirin has high responsibility.
This proves a stable defense mechanism.
This Event should permanently update Personality.
```

Those belong downstream:

```text
Perspective / Knowledge State
        ↓
Character Interpretation
        ↓
Evidence Candidate
        ↓
Period Character State
```

This separation is required to reduce circular reasoning.

---

# 6. Two-Pass Execution

The initial implementation may use two LLM analysis passes.

## Pass 1 — Perspective / Information Access

Input:

```text
Complete Event
+ target character
+ source metadata
+ previous validated knowledge only when required
```

Output:

```text
Accessible
Inaccessible
Uncertain
```

Pass 1 should not infer stable personality.

## Pass 2 — Character Knowledge / Inference

Input:

```text
Complete Event
+ Pass 1 result
+ relevant validated Character State
+ relevant prior knowledge / memory
```

Output:

```text
Known
Believed
Suspected
Misunderstood
```

The complete Event remains available in Pass 2 for contextual comprehension, but information marked Inaccessible must not be used as target-character knowledge.

The two-pass design is intentional. The main risk is not the extra pass itself but **error propagation** from Pass 1 into Pass 2.

Therefore Pass 1 results should remain reviewable and should preserve uncertainty rather than pretending to be ground truth.

---

# 7. Error Propagation Guardrails

Major failure mode:

```text
Pass 1 incorrectly marks X as Accessible
        ↓
Pass 2 treats X as Known
        ↓
Character Interpretation explains behavior using X
        ↓
X contaminates Character Evidence
```

Required guardrails:

1. Preserve `Uncertain` instead of forcing binary classification.
2. Keep provenance links back to Event and source ranges.
3. Do not transform Pass 1 output into permanent personality evidence directly.
4. Allow later Events to contradict or revise a prior knowledge-state inference.
5. Keep story truth, character knowledge, and character belief distinct.
6. Prefer human review for representative / high-impact Events before downstream consolidation.

---

# 8. Human Review Markdown

Every completed perspective pre-analysis batch should be able to produce an additional human-readable `.md` projection.

This Markdown file is **not canonical storage**. It is a review artifact generated from the structured result.

Suggested filename:

```text
<character>_perspective_review_<source-or-batch>.md
```

Example:

```text
reirin_perspective_review_volume1.md
```

## 8.1 Review goals

The reviewer should be able to answer quickly:

```text
Did the model incorrectly expose private information?
Did it hide information the character obviously perceived?
Did it confuse story truth with character belief?
Did it treat a suspicion as knowledge?
Did it miss a character misunderstanding?
Did chronology cause future-knowledge leakage?
```

## 8.2 Required review structure

```markdown
# Character Perspective Review

Character: 玲琳
Source: Volume 1

## V01-E-0001

### Event
- Source: lines 32-79
- Narrative order: 1
- Story chronology: ...

### Accessible
- ...

### Inaccessible
- ...

### Uncertain
- ...

### Character Inference

#### Known
- ...

#### Believed
- ...

#### Suspected
- ...

#### Misunderstood
- ...

### Review
- [ ] Access boundary checked
- [ ] No private-thought leakage
- [ ] No future-knowledge leakage
- [ ] Known vs believed/suspected checked
- [ ] Uncertain cases reviewed

Reviewer notes:

---
```

The review file may contain readable source excerpts or source references as needed for checking, but must not become a second source-of-truth database.

---

# 9. Validation Strategy

The mechanism should first be tested on a manually reviewed sample rather than assumed reliable across the full corpus.

Recommended evaluation unit:

```text
Event × target character
```

Suggested error categories:

```text
false-access:
  inaccessible information incorrectly marked accessible

false-inhibition:
  information clearly available to the character marked inaccessible

uncertainty-collapse:
  ambiguous information incorrectly forced to a definite class

knowledge-upgrade:
  suspicion / belief incorrectly promoted to known

temporal-leakage:
  future or later-learned information attributed too early

private-state-leakage:
  another character's private thought attributed to target character
```

A practical initial acceptance threshold may be defined empirically after manual review of representative Events. A lower-than-perfect per-Event accuracy may still be usable when downstream evidence accumulation and contradiction checking prevent isolated errors from becoming consolidated character claims.

---

# 10. Research Questions

The first implementation should explicitly evaluate:

### RQ1 — Full context vs hard filtering

Does full Event context improve scene coherence compared with sparse character-only source ranges?

### RQ2 — Information inhibition

Can the LLM reliably avoid attributing inaccessible information to the target character even though that information remains visible in the prompt?

### RQ3 — Character-state dependence

Which knowledge-state decisions require only source structure, and which legitimately require prior Character State / Memory / Relationship context?

### RQ4 — Error propagation

How often does an incorrect Perspective Pass produce a downstream Character Interpretation error?

### RQ5 — Human review efficiency

Can the generated Markdown review artifact make manual correction faster than reviewing raw structured output or the complete novel directly?

---

# 11. Scope Guardrail

Do not expand this stage into another complete Character Reconstruction engine.

This stage owns only:

```text
Event
↓
Perspective / access state
↓
character knowledge / belief state
```

It does not own:

```text
stable personality
long-term Character State
appraisal conclusion
emotion model
relationship consolidation
memory consolidation
trait confidence
causal personality formation
```

Core principle:

> Determine what world the character can reason from before asking what that world means to the character.
