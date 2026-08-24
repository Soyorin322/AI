# Character Perspective Pre-Analysis v0.0.1

Status: Initial implementation contract / research stage

Location:

```text
agents/AI_friend/Aiko/docs/research/event/character_perspective_preanalysis_v0.0.1.md
```

---

# 0. Purpose

This stage is executed **after source-side Event preparation and before character interpretation**.

Its purpose is to prevent story-level truth from being silently treated as character-level knowledge while preserving the **complete Event** for analysis.

It answers two different questions in sequence:

```text
1. What information in this complete Event is available, unavailable, or uncertain from the target character's perspective?
2. Given the complete Event, that perspective analysis, and relevant validated character context, what does the character know, believe, suspect, or misunderstand?
```

It does **not** answer:

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
Speaker / Thinker Attribution
↓
Event segmentation
↓
Complete Event
├── event_id
├── source_ranges / source locator
├── source-supported participants when useful
├── narrative_order
└── story_chronology when needed


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

# 2. Complete Event Is Always the Analysis Source

The canonical analysis material for this stage is the **complete Event**, not a character-filtered replacement text.

```text
Complete Event
+
Perspective analysis / prompt guidance
```

The Event remains linked to its original Canon source through deterministic locators:

```text
Perspective result
↓
event_id
↓
Event.source_ranges
↓
original source passage
```

`Accessible`, `Inaccessible`, and `Uncertain` are **analysis guidance / perspective judgments**. They do not delete, hide, rewrite, or replace source material.

Therefore:

```text
Context available to the analysis model
≠
Knowledge available to the target character
```

The analysis model may read the complete Event for scene comprehension, causal continuity, subjects, observable actions, and conversational structure. It must use the perspective result as a constraint on what may be attributed to the target character.

The previous line-level hard-filter approach could produce sparse character-only text such as:

```text
34-35
38-41
55-57
67
69
71
76-77
```

That approach can remove subjects, causal links, conversational context, action continuity, and narrator structure. It is therefore not the current design.

This design is motivated by work such as PICTURE (ACL 2026), which explores explicit representation of what a character does and does not know rather than relying only on event hiding.

Because full context can still create leakage risk, perspective judgments remain reviewable and uncertain cases must not be forced into definite classes.

---

# 3. Perspective Results Are Not a Source Mask

The three perspective classes mean:

```text
Accessible
= analysis suggests this information was available to the target character

Inaccessible
= analysis suggests this information was not available to the target character

Uncertain
= source/context does not justify a reliable access judgment
```

They are not instructions to physically construct three separate source files or to remove inaccessible passages from the Event.

Wrong interpretation:

```text
Complete Event
↓
remove Inaccessible
↓
character-only Event
↓
analysis
```

Current interpretation:

```text
Complete Event
+
Accessible / Inaccessible / Uncertain guidance
↓
character-perspective reasoning
```

A downstream prompt or structured reasoning adapter may present these classes as explicit constraints, but the complete Event remains available and source-addressable.

---

# 4. Stage A — Perspective Pass

The Perspective Pass should be as independent from personality interpretation as possible.

Primary inputs:

```text
complete Event context
speaker / thinker identity
source-supported participants / presence cues
explicit information transmission
story chronology
prior validated knowledge only when required
```

It should avoid using personality claims unless strictly required.

## 4.1 Accessible

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

## 4.2 Inaccessible

Information present in the complete Event but not available to the target character.

Typical examples:

```text
another character's private thought
private conversation while target character is absent
narrator-only omniscient explanation
future revelation
hidden motive not externally revealed
information learned only later
```

## 4.3 Uncertain

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

# 5. Stage B — Character Inference

Perspective access and character inference are different stages.

```text
Accessible Information
≠
What the character concludes from that information
```

Character Inference may use:

```text
complete Event
+
Perspective Pass result
+
validated prior Character State
+
relevant prior knowledge / memory
+
relationship history when needed
```

The complete Event remains present for contextual understanding. Information marked `Inaccessible` must not be promoted into target-character knowledge merely because the model can see it.

Current output classes:

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

The objective is character fidelity, not omniscient correctness.

---

# 6. Separation From Character Interpretation

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

This separation reduces circular reasoning.

---

# 7. Two-Pass Execution

The initial implementation may use two LLM analysis passes.

## Pass 1 — Perspective / Information Access

Input:

```text
Complete Event
+ target character
+ source metadata / locator
+ previous validated knowledge only when required
```

Output:

```text
Accessible
Inaccessible
Uncertain
```

The output should reference Event/source locations when useful for review, but it does not become replacement source text.

Pass 1 should not infer stable personality.

## Pass 2 — Character Knowledge / Inference

Input:

```text
Complete Event
+ Pass 1 result as perspective guidance
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

The complete Event remains available in Pass 2 for contextual comprehension.

The two-pass design is intentional. The main risk is error propagation from Pass 1 into Pass 2, not the presence of inaccessible source text itself.

Therefore Pass 1 results should remain reviewable and preserve uncertainty rather than pretending to be ground truth.

---

# 8. Prompt Semantics

A perspective-aware analysis prompt should make the following distinction explicit:

```text
You are given the complete Event for analysis.
Some information in the Event may not be available to the target character.
Use the Perspective Pass to distinguish story context from target-character knowledge.
Do not attribute Inaccessible information to the target character.
Do not treat Uncertain information as definitely known or definitely unknown.
The complete Event remains authoritative context and must retain its source lineage.
```

The purpose of `Accessible / Inaccessible / Uncertain` is therefore to guide reasoning, not to reduce the input corpus.

---

# 9. Provenance Requirement

Every perspective-analysis result must remain traceable to the complete Event and original source.

Minimum conceptual lineage:

```text
perspective_analysis_id
↓
target_character
↓
event_id
↓
Event.source_ranges
↓
original source
```

If individual judgments cite a proposition or source fragment, those references are review aids. They do not change the canonical source ownership of the Event.

A model-written perspective summary alone is never sufficient provenance.

---

# 10. Error Propagation Guardrails

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
2. Keep provenance back to Event IDs and original source locators.
3. Do not transform Pass 1 output into permanent personality evidence directly.
4. Allow later Events to contradict or revise prior knowledge-state inference.
5. Keep story truth, character knowledge, and character belief distinct.
6. Prefer human review for representative / high-impact Events before downstream consolidation.
7. Never construct a character-only replacement Event by deleting `Inaccessible` source lines.

---

# 11. Human Review Markdown

Every completed perspective pre-analysis batch should be able to produce a human-readable `.md` projection.

This Markdown file is **not canonical storage**. It is a review artifact generated from structured perspective-analysis data.

Suggested filename:

```text
<character>_perspective_review_<source-or-batch>.md
```

Example:

```text
reirin_perspective_review_volume1.md
```

Suggested structure:

```markdown
# Character Perspective Review

Character: 玲琳
Source: Volume 1

## V01-E-0001

### Complete Event Source
- Event ID: V01-E-0001
- Source locator: lines 32-79

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
- [ ] Complete Event still retrievable
- [ ] No private-thought leakage into character knowledge
- [ ] No future-knowledge leakage
- [ ] Known vs believed/suspected checked
- [ ] Uncertain cases reviewed

Reviewer notes:
```

The review file may quote or reference source fragments for checking, but must not become a second source-of-truth database.

---

# 12. Validation Strategy

The mechanism should first be tested on manually reviewed samples rather than assumed reliable across the full corpus.

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

source-detachment:
  perspective result cannot be traced back to the complete Event / original source
```

---

# 13. Research Questions

### RQ1 — Full context vs hard filtering

Does full Event context improve scene coherence compared with sparse character-only source ranges?

### RQ2 — Information inhibition

Can the LLM reliably avoid attributing inaccessible information to the target character even though that information remains visible in the complete Event?

### RQ3 — Character-state dependence

Which knowledge-state decisions require only source structure, and which legitimately require prior Character State / Memory / Relationship context?

### RQ4 — Error propagation

How often does an incorrect Perspective Pass produce a downstream Character Interpretation error?

### RQ5 — Human review efficiency

Can generated Markdown make manual correction faster than reviewing raw structured output or the complete novel directly?

### RQ6 — Provenance usability

Can every perspective judgment be reviewed efficiently while retaining direct access to the complete original Event passage?

---

# 14. Scope Guardrail

Do not expand this stage into another complete Character Reconstruction engine.

This stage owns only:

```text
Complete Event
↓
Perspective guidance
  Accessible / Inaccessible / Uncertain
↓
Character knowledge / belief-state inference
  Known / Believed / Suspected / Misunderstood
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

> Determine what world the character can reason from before asking what that world means to the character, while preserving the complete Event as the analysis source and retaining direct provenance to the original Canon.
