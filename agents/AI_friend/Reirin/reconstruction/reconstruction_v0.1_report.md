# Reirin v0.1 reconstruction audit report

## Source and trust boundary

This reconstruction uses exactly one approved input:
`character_data/Reirin/sources/raw/novel/惡女不才_第一卷_前三章.md`.
The complete 853-line file was read. Its SHA-256 is
`c4ebb0d72546fa79ef6c6371cda65f9916a097e62576adda20e523934e050c03`.

Novel prose is evidence. Speaker labels are derived, rule-assisted annotations
with non-guaranteed accuracy. No conclusion relies on a disputed speaker tag
alone; identity-relevant attributions are paired with nearby narration, bodily
perception, or accessible dialogue and retain uncertainty.

No later Volume 1 chapter, Volume 2/3 material, wiki, web source, reference note,
old Task 004 reconstruction, prior Reirin summary, or model-held story knowledge
was used.

## Coverage and selection

Thirteen exact spans were selected after reading the entire source. They cover:

- the pre-swap public/body baseline and demonstrated embroidery;
- fall, awakening, identity/body discrepancy, failed identity proof, and the
  adversarial explanation of the exchange;
- the health comparison and original-body illness history;
- the beast-seeking rite, animal deaths, responsibility response, and acquittal;
- relocation, Lily's direct hostility, warehouse freedom, practical settlement,
  Lily's inaccessible private inducement, cultivation, cooking, and food sharing.

Non-selected material consists chiefly of publication/front matter, general
world exposition, extended private narration about other characters, procedural
descriptions not changing Reirin's state, and repeated audience reactions. The
private Lily scene was selected separately because it tests story truth versus
Reirin-accessible knowledge; it never enters Reirin's Memory or subjective state.

## Artifact counts

| Artifact | Count |
|---|---:|
| SourceReference | 1 |
| Exact SourceUnit | 13 |
| ObservationRecord | 13 |
| EventRecord | 13 |
| EvidenceRecord | 15 |
| PeriodDefinition | 3 |
| PeriodAssignment | 13 |
| PeriodCharacterState | 3 |
| MemoryFormationDecision | 13 |
| MemoryRecord | 9 |
| MemoryIndexMetadata | 9 |
| SkillEvidence | 2 |
| CharacterSkillProfile | 2 |
| DevelopmentRecord | 2 |
| CompiledCharacterState | 1 |

## Events

1. `event-001`: festival baseline—frail original body, public position, and displayed embroidery.
2. `event-002`: tower fall and awakening in Keigetsu's body.
3. `event-003`: failed identity proof under the disclosure restriction.
4. `event-004`: adversarial participant states the exchange was intentional.
5. `event-005`: Reirin tests the healthy body and contrasts it with her original illness.
6. `event-006`: beast-seeking danger and context-bounded composure.
7. `event-007`: poisoned mouse remains cause the lion's death; Reirin accepts concrete responsibility.
8. `event-008`: acquittal ends execution risk while identity concealment continues.
9. `event-009`: Lily escorts Reirin to exile and directly describes hostility/prior abuse.
10. `event-010`: Reirin explicitly welcomes bodily capacity, privacy, freedom, and expression.
11. `event-011`: she clears the grounds and requests limited basic supplies.
12. `event-012`: Lily privately accepts an inducement; this remains inaccessible to Reirin.
13. `event-013`: Reirin demonstrates cultivation, cooking, food sharing, and a constrained identity hint.

Each Event exists once. Period domains, Memory, SkillEvidence, Development, and
Compiled State reference those IDs rather than copying Event objects.

## Period discovery and assignment

| Period | Status | Boundary rationale | Events |
|---|---|---|---|
| `period-001` | confirmed | Original body, protected environment, public identity, and pre-fall knowledge form the baseline. | 001 |
| `period-002` | confirmed | Awakening after the fall changes body identity, environment, public identity, knowledge, goal, and execution risk. | 002–008 |
| `period-003` | candidate | Acquittal and warehouse relocation change danger, environment, autonomy, relationships, and goals, but the source ends early in the new interval. | 009–013 |

These boundaries are state-based, not chapter-based. Every Event has exactly one
explicit assignment.

## Eight-domain coverage

| Period | Personality | Physical | Motivation | Backstory | Emotion | Relationships | Growth | Conflict |
|---|---|---|---|---|---|---|---|---|
| 001 | bounded inference | observed | insufficient evidence | observed | insufficient evidence | observed | not applicable | insufficient evidence |
| 002 | bounded inference | observed | observed | observed | observed | observed | bounded inference | observed |
| 003 | bounded inference | observed | observed | unchanged | observed | observed | bounded inference | observed |

Character identity remains `黃玲琳 / Reirin`. Body identity is `黃玲琳` in
Period 001 and `朱慧月` in Periods 002–003.

Examples intentionally kept bounded include composure under physical danger,
responsibility-taking in the animal incident, and practical self-direction in the
warehouse. None is promoted into a universal or lifelong trait.

## Memory and knowledge boundary

All 13 Events receive an explicit formation decision: 9 persist and 4 do not.
Non-persist decisions cover the baseline without a distinct retained episode,
the rite scene without later recall within scope, routine supply acquisition, and
Lily's inaccessible private agreement. Nine index entries point to nine Memory
records, which reference Event IDs without embedding objective Event copies.

`event-012` is story-level truth but has no character-accessible information for
Reirin. It is explicitly excluded by Period 003's knowledge boundary and never
appears in her Memory.

## Skills

- `embroidery`: high-quality work demonstrated in the festival comparison;
  broader professional standards remain unknown.
- `practical-cultivation-and-food-preparation`: several basic tasks demonstrated
  in one warehouse interval; expert agronomy or culinary proficiency is not claimed.

No RuntimeCapability or technical skill pack was created.

## Development and counterevidence

Two unresolved Development records compare multiple Period States:

- greater visible expression and independent activity after body/environment
  changes;
- responsibility-directed action across the adjudication and warehouse periods.

Confidence and change resistance remain separate; both change-resistance values
are `unresolved`. Causal formation remains hypothetical. Alternatives include
novelty, immediate survival demands, privacy, and the healthy body's capacity.
Counterevidence includes pre-swap dependence on protection, strong emotional
distress under personal hatred, and the very short duration of Period 003.

No counterevidence beyond this Task 006 source scope was searched or claimed.

## Compiled state and unresolved items

The single compiled state references all three historical Period States and two
Development records. It contains four conservative entries: identity/body
separation, current warehouse joy/activity, bounded composure/responsibility, and
the current Lily relationship context with inaccessible facts excluded.

Unresolved items include the candidate Period 003 boundary, long-term stability,
change resistance, speaker attribution, later-source knowledge, and permanent
Relationship subsystem ownership.

## Validation and limitations

Persistent JSON was reloaded into Aiko dataclasses, assembled into a
`ReconstructionGraph`, and passed `validate_reconstruction_graph()` with zero
errors. Validation uses the persisted files, not a parallel in-memory builder
result.

This is `Reirin v0.1 — first three chapters only`. It is not a complete lifetime
persona, relationship graph, skill set, speech profile, or final Reirin state.
No Aiko generic framework change was required for Task 006.
