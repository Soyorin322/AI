# Aiko Evidence-Grounded Character Reconstruction Research v0.0.1

Status: Research Foundation

Suggested location:

```text
docs/research/reconstruction/evidence_grounded_reconstruction_v0.0.1.md
```

---

# 0. Purpose

This research line studies how Aiko can reconstruct a character from source material without allowing plausible but weakly supported psychological interpretations to silently become canonical character data.

Core problem:

```text
Canon / Source Material
        ↓
LLM Interpretation
        ↓
Plausible Psychological Claim
```

is not sufficient.

Aiko needs:

```text
Canon / Source Material
        ↓
Source-supported Observation
        ↓
Candidate Interpretation
        ↓
Psychological Hypothesis
        ↓
Evidence / Counterevidence / Alternatives
        ↓
Validation
        ↓
Possible Consolidated Character Claim
```

Core principle:

> Plausibility is not canon.

---

# 1. Research Boundary

This research does not define the final Persona schema.

It defines the epistemic process by which claims may become eligible for Character Reconstruction.

It should remain separate from:

```text
Event Interpretation
Memory storage implementation
Persona schema
LLM provider
database technology
```

It may produce contracts used by all of them.

---

# 2. Research Topic A — Claim Types and Epistemic Separation

Aiko must distinguish:

```text
Source Fact
Observation
Character Perception
Interpretation
Assumption
Inference
Hypothesis
Evaluation
Consolidated Character Claim
```

Research questions:

1. Which categories are necessary?
2. Which can coexist without being collapsed?
3. Which categories can be canonical?
4. Which should always retain uncertainty?
5. How should derived causal claims be distinguished from explicitly stated canon?

Possible output:

```text
Aiko Character Claim Model
```

---

# 3. Research Topic B — Provenance and Attribution

Every important psychological claim should be traceable to evidence.

Possible representation:

```text
Claim
├── claim_id
├── content
├── claim_type
├── temporal_scope
├── supporting_evidence[]
├── contradicting_evidence[]
├── source_provenance[]
├── alternative_hypotheses[]
├── confidence
└── status
```

Possible statuses:

```text
observed
candidate
supported
contested
uncertain
consolidated
rejected
superseded
```

Research questions:

1. How much evidence must be retained?
2. Should evidence be stored as links or copied excerpts?
3. How should multiple media sources be merged?
4. How should source reliability differ?
5. How should later canon override earlier inference?

---

# 4. Research Topic C — Circularity Prevention

Primary failure mode:

```text
Behavior B
→ infer Trait T
→ use Trait T to explain Behavior B
→ treat that explanation as additional evidence for T
```

This produces self-confirming reconstruction.

Aiko should investigate rules such as:

```text
Evidence used to generate a hypothesis
≠
independent validation evidence
```

and:

```text
Explanation
≠
Verification
```

Research questions:

1. When can the same event legitimately support both extraction and validation?
2. What counts as independent counterfactual or held-out evidence?
3. How should a hypothesis be tested against events not used to create it?
4. How should contradictory behavior affect confidence?
5. How can multiple hypotheses remain alive without premature consolidation?

Possible outputs:

```text
Aiko Circularity Guard
Aiko Hypothesis Validation Contract
```

---

# 5. Research Topic D — Alternative Hypotheses

Aiko should not force one psychological explanation when several remain possible.

Example:

```text
Observation:
The character refuses help.

Hypothesis A:
self-reliance

Hypothesis B:
fear of burdening others

Hypothesis C:
distrust

Hypothesis D:
temporary situational constraint
```

Research should determine when to:

```text
select one
rank several
retain several
defer judgment
```

Core principle:

> Unresolved ambiguity is valid character data.

---

# 6. Research Topic E — Confidence, Uncertainty, and Abstention

Aiko should be allowed to say internally:

```text
insufficient evidence
uncertain
period-specific only
context-specific only
conflicting canon
cannot distinguish between hypotheses
```

Confidence should not become false numerical precision.

Research questions:

1. categorical vs continuous confidence?
2. evidence count vs evidence diversity?
3. effect of source quality?
4. effect of counterevidence?
5. when should consolidation abstain?

---

# 7. Research Topic F — Generate / Verify Separation

Candidate workflow:

```text
Source Material
↓
Candidate Extraction
↓
Evidence Retrieval
↓
Counterevidence Search
↓
Alternative Hypothesis Generation
↓
Verification
↓
Revision / Abstention / Consolidation
```

This workflow is a research candidate, not an approved architecture.

Questions:

1. Should generator and verifier be separate model calls?
2. Should they use different prompts or models?
3. How much verification is needed for low-impact claims?
4. Can verification be deferred to reconstruction/consolidation time?
5. How should cost scale with claim importance?

---

# 8. Research Topic G — Held-Out Canon Validation

Character Reconstruction should eventually be testable.

Possible strategy:

```text
Reconstruction Evidence
        ↓
Character Hypothesis
        ↓
Held-out Canon Event
        ↓
Prediction / Interpretation
        ↓
Compare with Canon
```

Candidate baselines:

```text
A. simple character prompt
B. retrieved canon only
C. reconstructed character
D. reconstructed character + event appraisal
```

Possible evaluation targets:

```text
interpretation fidelity
behavior consistency
knowledge boundary
relationship fidelity
temporal fidelity
calibration / uncertainty
contradiction handling
```

---

# 9. Integration with Event Research

Event research may produce:

```text
candidate interpretation
candidate belief consequence
candidate trait evidence
candidate causal explanation
```

but should not directly promote them into persistent Character Core.

Preferred boundary:

```text
Event Interpretation
        ↓
Evidence / Candidate Claims
        ↓
Evidence-Grounded Reconstruction
        ↓
Consolidation Decision
        ↓
Character Core
```

---

# 10. Research Guardrails

Do not assume:

```text
LLM confidence = evidence confidence
plausibility = canon
one event = one explanation
explanation = evidence
repetition of same evidence = independent support
absence of contradiction = proof
```

Always preserve:

```text
provenance
uncertainty
counterevidence
alternatives
temporal scope
validation status
```

---

# 11. Core Research Question

> How can Aiko infer a deep character model from incomplete narrative evidence while remaining traceable, revisable, uncertain when necessary, and resistant to self-confirming psychological stories?
