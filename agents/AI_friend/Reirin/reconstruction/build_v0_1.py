"""Build Reirin v0.1 bottom-up from the single Task 006 approved source."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from ai_friend.character.reconstruction import (
    CausalHypothesis,
    CharacterSkillProfile,
    ChangeResistance,
    CompiledCharacterState,
    CompiledStateEntry,
    DevelopmentRecord,
    DomainEntry,
    DomainEvidenceState,
    HistoricalAdaptation,
    KnowledgeBoundary,
    PeriodCharacterState,
    PeriodDomains,
    SkillAcquisitionOrigin,
    SkillEvidence,
)
from ai_friend.memory.models import (
    MemoryFormationDecision,
    MemoryFormationOutcome,
    MemoryIndexMetadata,
    MemoryRecord,
)
from ai_friend.reconstruction.hardening import ReconstructionGraph, validate_reconstruction_graph
from ai_friend.reconstruction.models import (
    ArtifactStatus,
    BoundaryStatus,
    EventRecord,
    EvidenceRecord,
    EvidenceStance,
    ObservationRecord,
    PeriodAssignment,
    PeriodDefinition,
    ReconstructionBundle,
    SourceReference,
    SourceUnit,
    SourceUnitGrounding,
    TemporalScope,
)
from ai_friend.reconstruction.provenance import Lineage
from ai_friend.reconstruction.serialization import to_portable_json


INSTANCE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = INSTANCE_ROOT.parents[2]
SOURCE_PATH = WORKSPACE_ROOT / "character_data" / "Reirin" / "sources" / "raw" / "novel" / "惡女不才_第一卷_前三章.md"
SOURCE_RELATIVE = "character_data/Reirin/sources/raw/novel/惡女不才_第一卷_前三章.md"
SCHEMA_VERSION = "0.0.8"
ARTIFACT_VERSION = "Reirin-v0.1"
CREATED_AT = datetime(2026, 8, 22, tzinfo=timezone.utc)


def _scope(label: str, order: int) -> TemporalScope:
    return TemporalScope(label=label, metadata={"period_order": order, "source_scope": "first-three-chapters-only"})


def _exact_unit(lines: list[str], artifact_id: str, start: int, end: int, label: str, order: int) -> SourceUnit:
    content = "\n".join(lines[start - 1:end])
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return SourceUnit(
        artifact_id, "source-v1-first-three", content,
        f"{SOURCE_RELATIVE};lines={start}-{end};anchor={label}", _scope(label, order),
        {"character_identity": "黃玲琳 / Reirin", "speaker_annotation_is_derived": True},
        SourceUnitGrounding.EXACT_TEXT, f"sha256:{digest}",
    )


def _obs(artifact_id: str, content: str, unit_id: str, scope: TemporalScope, **metadata: object) -> ObservationRecord:
    return ObservationRecord(artifact_id, content, Lineage(source_unit_ids=(unit_id,)), scope, metadata)


def _event(
    artifact_id: str, description: str, observation_ids: tuple[str, ...], scope: TemporalScope,
    participants: tuple[str, ...], facts: tuple[str, ...], accessible: tuple[str, ...],
    statements: tuple[str, ...] = (), behaviors: tuple[str, ...] = (), outcome: str | None = None,
    uncertainty: str | None = None,
) -> EventRecord:
    return EventRecord(
        artifact_id, description, Lineage(parent_artifact_ids=observation_ids), scope,
        {"character_identity": "黃玲琳 / Reirin", "body_identity": "黃玲琳" if scope.metadata["period_order"] == 1 else "朱慧月"},
        participants, facts, accessible, statements, behaviors, outcome, uncertainty,
    )


def _evidence(
    artifact_id: str, content: str, stance: EvidenceStance, parents: tuple[str, ...], scope: TemporalScope,
    evidence_type: str,
) -> EvidenceRecord:
    return EvidenceRecord(
        artifact_id, content, stance, Lineage(parent_artifact_ids=parents), scope,
        {"evidence_type": evidence_type, "scope_limit": "first-three-chapters-only"},
    )


def build_graph() -> tuple[ReconstructionGraph, tuple[MemoryIndexMetadata, ...]]:
    raw = SOURCE_PATH.read_text(encoding="utf-8")
    lines = raw.splitlines()
    if len(lines) != 853:
        raise ValueError(f"approved source line count changed: {len(lines)}")
    source_sha256 = hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest()
    if source_sha256 != "c4ebb0d72546fa79ef6c6371cda65f9916a097e62576adda20e523934e050c03":
        raise ValueError("approved source SHA-256 changed")

    p1_scope = _scope("pre-swap protected life through tower fall", 1)
    p2_scope = _scope("post-swap confinement and beast-seeking adjudication", 2)
    p3_scope = _scope("post-acquittal warehouse relocation and initial self-sufficient living", 3)

    source = SourceReference(
        "source-v1-first-three", "惡女不才 第一卷前三章 Speaker 標註版", SOURCE_RELATIVE, "text/markdown",
        {
            "source_role": "approved_reconstruction_input", "content_basis": "novel_text",
            "speaker_annotation": "derived", "speaker_annotation_confidence": "not_guaranteed",
            "approval_scope": "Task 006 only", "sha256": source_sha256,
            "git_blob": "5dae00c1fd63de0566c7dbf19e00689ef3d63bc6",
        }, True,
    )
    units = (
        _exact_unit(lines, "su-001", 36, 56, "pre-swap public position health and demonstrated embroidery", 1),
        _exact_unit(lines, "su-002", 87, 107, "tower fall and immediate awakening", 2),
        _exact_unit(lines, "su-003", 113, 174, "body discrepancy failed identity proof and false diary claim", 2),
        _exact_unit(lines, "su-004", 197, 236, "swap disclosure coercion and Reirin response", 2),
        _exact_unit(lines, "su-005", 238, 261, "health comparison original-body history and narrator endurance statement", 2),
        _exact_unit(lines, "su-006", 331, 355, "calm response during beast-seeking danger", 2),
        _exact_unit(lines, "su-007", 365, 418, "poisoned mouse lion death and accepted responsibility", 2),
        _exact_unit(lines, "su-008", 420, 457, "acquittal warning prayer and renewed action", 2),
        _exact_unit(lines, "su-009", 485, 518, "Lily hostility and disclosure of prior mistreatment", 3),
        _exact_unit(lines, "su-010", 524, 589, "warehouse exile freedom and released expression", 3),
        _exact_unit(lines, "su-011", 625, 689, "warehouse labor and request for minimal supplies", 3),
        _exact_unit(lines, "su-012", 716, 765, "Lily accepts outside inducement unknown to Reirin", 3),
        _exact_unit(lines, "su-013", 794, 840, "cultivation cooking shared food and bounded identity hint", 3),
    )
    observations = (
        _obs("obs-001", "Narration identifies Reirin as fifteen, physically frail, socially favored, and the maker of the leading embroidery; some praise is reported through other speakers.", "su-001", p1_scope, observation_type="narrator_fact_plus_reported_speech", speaker_uncertainty="reported praise is not treated as Reirin self-report"),
        _obs("obs-002", "Reirin falls from the tower after an attributed hostile line from Keigetsu and later awakens in a body with unfamiliar voice, hands, and clothing.", "su-002", p2_scope, observation_type="observed_action_and_first_person_sensation", speaker_uncertainty="hostile speaker label is derived but consistent with nearby action"),
        _obs("obs-003", "Reirin infers a body exchange, cannot express her identity or the exchange, and attempts to identify herself through private facts known to Dongxue.", "su-003", p2_scope, observation_type="explicit_inference_and_action"),
        _obs("obs-004", "Keigetsu, appearing through flame in Reirin's original body, states that she caused the exchange and blocked disclosure; Reirin hears this and initially offers health advice despite the threat.", "su-004", p2_scope, observation_type="accessible_statement_and_response", speaker_uncertainty="speaker labels remain derived annotations; identity is additionally supported by dialogue content"),
        _obs("obs-005", "Reirin checks the current body, explicitly calls it healthy, recalls her original body's extreme recurrent illness and self-management, and reminds herself of responsibility toward her original body.", "su-005", p2_scope, observation_type="explicit_statement_narrator_fact_and_inner_reasoning"),
        _obs("obs-006", "During the beast-seeking rite Reirin remains behaviorally calm, says she is accustomed to proximity to death, and explains that anticipating pain would consume strength.", "su-006", p2_scope, observation_type="observed_behavior_and_explicit_statement"),
        _obs("obs-007", "Reirin had kept a mouse's body for burial after it consumed poison she dropped; when the lion dies after eating it, she says she bears responsibility and apologizes.", "su-007", p2_scope, observation_type="narrated_action_and_explicit_statement"),
        _obs("obs-008", "After acquittal Reirin accepts the imposed public identity label, prays for the dead animals, and tells herself to do what she can.", "su-008", p2_scope, observation_type="observed_behavior_and_explicit_statement"),
        _obs("obs-009", "Lily tells Reirin that the former body-owner mistreated her and refuses to provide care; Reirin recognizes Lily as a socially vulnerable attendant and hears the hostility directly.", "su-009", p3_scope, observation_type="accessible_relationship_statement"),
        _obs("obs-010", "On seeing the warehouse and grounds, Reirin explicitly expresses joy at soil, physical activity, privacy, freedom, and no longer suppressing her voice; narration links prior suppression to illness and others' worry.", "su-010", p3_scope, observation_type="explicit_emotion_action_and_narrator_context"),
        _obs("obs-011", "Reirin performs substantial clearing work, declines broad rescue, and asks Chenyu only for salt; she remains polite toward Chenyu and Weng Ang.", "su-011", p3_scope, observation_type="observed_work_and_explicit_request"),
        _obs("obs-012", "Outside Reirin's presence, Lily accepts food and a promised promotion in exchange for reporting mistreatment of the person believed to be Keigetsu.", "su-012", p3_scope, observation_type="story_level_event_not_character_accessible"),
        _obs("obs-013", "Reirin identifies edible plants, reorganizes cultivation beds, cooks and shares food, calls applying book knowledge joyful, and gives Lily only a constrained hint that she changed after the festival.", "su-013", p3_scope, observation_type="demonstrated_ability_explicit_statement_and_relationship_action"),
    )
    events = (
        _event("event-001", "Reirin participates in the festival as a frail, publicly favored candidate with demonstrated embroidery.", ("obs-001",), p1_scope, ("黃玲琳", "堯明", "雛宮女官"), ("Reirin's embroidery is displayed and judged best among the displayed works.", "Narration describes recurrent frailty and close family protection."), ("Reirin is present for the festival and knows her own physical condition and embroidery work.",), outcome="The protected pre-swap situation is established.", uncertainty="Other women's broad praise is reported opinion, not direct access to Reirin's cognition."),
        _event("event-002", "Reirin falls from the tower and awakens in confinement in Keigetsu's body.", ("obs-002",), p2_scope, ("黃玲琳", "朱慧月", "堯明", "冬雪"), ("Reirin falls and later awakens in a body with unfamiliar features in a cell.",), ("Reirin remembers the fall, perceives the unfamiliar body, and recognizes the cell.",), outcome="Character identity remains 黃玲琳 while current body identity becomes 朱慧月.", uncertainty="The source's speaker attribution is derived; the swap is subsequently corroborated in accessible dialogue."),
        _event("event-003", "Reirin attempts and fails to prove her identity to Dongxue under a disclosure restriction.", ("obs-003",), p2_scope, ("黃玲琳", "冬雪"), ("Speech and writing about the exchange are blocked; Dongxue rejects private identifying facts because of a false diary explanation.",), ("Reirin knows her identity, infers the exchange, and learns that Dongxue believes a diary was stolen.",), behaviors=("Offers private biographical facts to establish identity.",), outcome="The identity proof fails and Reirin remains treated as Keigetsu."),
        _event("event-004", "Keigetsu tells Reirin that the exchange and disclosure block were intentional.", ("obs-004",), p2_scope, ("黃玲琳", "朱慧月"), ("The person in Reirin's original body claims responsibility for the exchange and threatens Reirin with execution.",), ("Reirin hears the stated motive, method, disclosure constraint, and threat.",), statements=("Reirin asks why and offers advice for treating her original body's fever.",), outcome="Reirin's accessible knowledge now includes an asserted intentional exchange.", uncertainty="The other party's causal account is a statement by an adversarial participant, not independent narrator verification."),
        _event("event-005", "Reirin evaluates the healthy borrowed body against her severely frail original body.", ("obs-005",), p2_scope, ("黃玲琳",), ("The borrowed body has stable pulse and movement while narration describes the original body's recurrent severe illness.",), ("Reirin directly tests the current body, recalls her illness-management history, envies the health, and recalls duty toward her original body.",), outcome="She understands a sharp body/health contrast without changing character identity."),
        _event("event-006", "Reirin faces the beast-seeking rite and remains behaviorally calm before the lion.", ("obs-006",), p2_scope, ("黃玲琳", "辰宇", "堯明"), ("Reirin is placed with a hungry lion and remains standing as it approaches.",), ("She knows the danger and explains her learned strategy of not anticipating pain.",), behaviors=("Maintains composure before attack.",), uncertainty="Calm behavior is bounded to this danger context and must not alone establish lifelong fearlessness."),
        _event("event-007", "The lion dies after consuming the poisoned mouse remains kept by Reirin.", ("obs-007",), p2_scope, ("黃玲琳", "辰宇"), ("The lion consumes poisoned remains and dies; Reirin survives.",), ("Reirin knows how the mouse encountered the poison and treats both deaths as her responsibility.",), behaviors=("Warns the lion, explains the accident, apologizes, and intends burial/prayer."), outcome="The rite ends without Reirin's death."),
        _event("event-008", "Reirin is declared innocent of the tower attack and resolves to act within her constrained public identity.", ("obs-008",), p2_scope, ("黃玲琳", "辰宇", "堯明"), ("The rite formally declares the person publicly identified as Keigetsu innocent of the attack.",), ("Reirin hears the acquittal, the continued threat against identity-like behavior, and knows she cannot disclose the swap.",), behaviors=("Prays for the animals and verbally rallies herself."), outcome="Execution danger ends, but identity concealment and social hostility continue."),
        _event("event-009", "Lily escorts Reirin to a derelict warehouse and directly refuses service while describing prior abuse.", ("obs-009",), p3_scope, ("黃玲琳", "莉莉"), ("Reirin is relocated and Lily states that she will not provide household care.",), ("Reirin learns Lily's name, vulnerable status, claimed mistreatment, and present refusal.",), outcome="Reirin enters a new environment with a hostile attendant relationship."),
        _event("event-010", "Reirin welcomes warehouse isolation as an opportunity for physical activity, autonomy, and open expression.", ("obs-010",), p3_scope, ("黃玲琳",), ("Reirin is left at the warehouse with overgrown grounds and no immediate supervision.",), ("She knows she is isolated, inhabits a healthy body, and explicitly experiences joy and freedom while remembering the wrongful exchange.",), behaviors=("Runs into the grass, touches the soil, jumps, and speaks loudly."), outcome="Her active goals shift toward self-sufficient living while the exchange remains unresolved."),
        _event("event-011", "Reirin begins clearing the grounds and requests only basic supplies when Chenyu offers help.", ("obs-011",), p3_scope, ("黃玲琳", "辰宇", "文昴"), ("Reirin clears vegetation; Chenyu offers intervention or supplies; she asks for salt and receives basic provisions.",), ("Reirin participates in the conversation and knows what support is offered and accepted.",), behaviors=("Performs manual work, declines broad intervention, and makes a limited practical request."), outcome="Initial self-sufficient settlement receives minimal material support."),
        _event("event-012", "Lily privately accepts an inducement to report on mistreatment of the person believed to be Keigetsu.", ("obs-012",), p3_scope, ("莉莉", "雅容"), ("Lily accepts rice and a promised promotion for future reports.",), (), outcome="An undisclosed pressure enters Lily's relationship context.", uncertainty="This story-level event is inaccessible to Reirin in the allowed source window and is excluded from her Memory and Period domain claims."),
        _event("event-013", "Reirin cultivates recovered plants, cooks, shares food with Lily, and gives a constrained identity hint.", ("obs-013",), p3_scope, ("黃玲琳", "莉莉"), ("Reirin has cleared and organized part of the grounds, identified edible plants, cooked food, and shared it.",), ("Reirin knows her own work, book-derived knowledge, enjoyment, and the limited hint she gives Lily; she does not know Lily's private agreement.",), behaviors=("Cultivates, cooks, offers food, and avoids falsely claiming use of magic."), outcome="Lily encounters behavior inconsistent with her prior model of Keigetsu, but Reirin's identity remains undisclosed."),
    )
    evidence = (
        _evidence("evidence-001", "The displayed embroidery and narrator comparison support demonstrated embroidery ability, without importing every bystander's praise as fact.", EvidenceStance.SUPPORTS, ("event-001",), p1_scope, "demonstrated_skill"),
        _evidence("evidence-002", "Narration supports severe recurrent original-body frailty and extensive family protection before the swap.", EvidenceStance.SUPPORTS, ("event-001",), p1_scope, "narrator_supported_state"),
        _evidence("evidence-003", "Direct bodily perception, failed disclosure, and later dialogue support identity/body separation after the fall.", EvidenceStance.SUPPORTS, ("event-002", "event-003", "event-004"), p2_scope, "identity_and_knowledge"),
        _evidence("evidence-004", "Reirin's health checks and explicit duty reminder support the borrowed-body health contrast and continued identification with her original body.", EvidenceStance.SUPPORTS, ("event-005",), p2_scope, "explicit_reasoning"),
        _evidence("evidence-005", "Behavior and explicit statements during the rite support context-bounded composure under anticipated physical danger.", EvidenceStance.SUPPORTS, ("event-006",), p2_scope, "observed_behavior_plus_statement"),
        _evidence("evidence-006", "Her apology and ownership of the animal deaths support responsibility-taking in this concrete incident.", EvidenceStance.SUPPORTS, ("event-007", "event-008"), p2_scope, "observed_behavior_plus_statement"),
        _evidence("evidence-007", "Reirin's tears and near-faint response to intense personal hatred limit any broad claim that she is emotionally unaffected by threat or rejection.", EvidenceStance.CONTRADICTS, ("event-004",), p2_scope, "counterevidence"),
        _evidence("evidence-008", "Lily's direct account establishes present hostility and claimed prior abuse by the former body-owner, not acts attributable to Reirin's identity.", EvidenceStance.SUPPORTS, ("event-009",), p3_scope, "relationship_context"),
        _evidence("evidence-009", "Reirin's explicit joy and narrator context support health- and privacy-enabled release of previously restrained emotional expression.", EvidenceStance.SUPPORTS, ("event-010",), p3_scope, "explicit_emotion_plus_narrator_context"),
        _evidence("evidence-010", "Manual clearing and a narrowly scoped supply request support self-directed practical action in the warehouse context.", EvidenceStance.SUPPORTS, ("event-011",), p3_scope, "demonstrated_action"),
        _evidence("evidence-011", "Pre-swap dependence on intensive protection limits any claim that visible independence was already broadly demonstrated in all contexts.", EvidenceStance.CONTRADICTS, ("event-001",), p1_scope, "contextual_counterevidence"),
        _evidence("evidence-012", "Lily's private agreement is story-level relationship context but cannot support Reirin-accessible knowledge or memory in this period.", EvidenceStance.CONTRADICTS, ("event-012",), p3_scope, "knowledge_boundary_guard"),
        _evidence("evidence-013", "Cultivation, plant identification, food preparation, and sharing are directly demonstrated in the warehouse scene.", EvidenceStance.SUPPORTS, ("event-013",), p3_scope, "demonstrated_skill_and_behavior"),
        _evidence("evidence-014", "Reirin explicitly remembers the wrongful motive for the swap while enjoying the warehouse, supporting a concurrent freedom-versus-duty tension.", EvidenceStance.SUPPORTS, ("event-010", "event-013"), p3_scope, "explicit_conflict"),
        _evidence("evidence-015", "The source window ends shortly after relocation, so persistence of the new expression and autonomy pattern is not established.", EvidenceStance.CONTRADICTS, ("event-010", "event-011", "event-013"), p3_scope, "scope_counterevidence"),
    )
    periods = (
        PeriodDefinition("period-001", 1, p1_scope, BoundaryStatus.CONFIRMED, "Baseline body, protected environment, public identity, and knowledge state precede the tower fall and exchange.", 1),
        PeriodDefinition("period-002", 2, p2_scope, BoundaryStatus.CONFIRMED, "Awakening in Keigetsu's body changes body identity, environment, public identity, accessible knowledge, immediate goal, and execution risk.", 2),
        PeriodDefinition("period-003", 3, p3_scope, BoundaryStatus.CANDIDATE, "Acquittal ends immediate execution risk and relocation changes environment, available autonomy, relationships, and active goals; the source window is too short to confirm lasting coherence.", 3),
    )
    assignments = tuple(
        PeriodAssignment(f"assignment-{index:03d}", f"event-{index:03d}", "period-001" if index == 1 else "period-002" if index <= 8 else "period-003", "Assigned from body/environment/knowledge/goal state active during the event.", BoundaryStatus.CONFIRMED if index <= 8 else BoundaryStatus.CANDIDATE)
        for index in range(1, 14)
    )

    abstain = lambda state=DomainEvidenceState.INSUFFICIENT_EVIDENCE: DomainEntry(state)
    states = (
        PeriodCharacterState(
            "period-state-001", "period-001", p1_scope, KnowledgeBoundary(1, ("fact-own-identity", "fact-original-body-frailty", "fact-public-role")),
            PeriodDomains(
                personality=DomainEntry(DomainEvidenceState.BOUNDED_INFERENCE, ("Within the public pre-swap setting, Reirin is presented as polite and socially esteemed; direct behavioral coverage is limited.",), ("event-001",), ("evidence-001", "evidence-002"), "Some praise originates in bystander speech."),
                physical=DomainEntry(DomainEvidenceState.OBSERVED, ("Character identity and body identity are both 黃玲琳; the original body is severely and recurrently frail.",), ("event-001",), ("evidence-002",)),
                motivation=abstain(),
                backstory=DomainEntry(DomainEvidenceState.OBSERVED, ("Her mother died near her birth and her family responds to her frailty with intensive protection.",), ("event-001",), ("evidence-002",)),
                emotion=abstain(),
                relationships=DomainEntry(DomainEvidenceState.OBSERVED, ("Narration places her in a close, protective family network and as Yaoming's favored future partner; her private interpretation is not established.",), ("event-001",), ("evidence-002",), "Relationship description is narrator-level, not a complete subjective relationship model."),
                growth=abstain(DomainEvidenceState.NOT_APPLICABLE),
                conflict=abstain(),
            ), ("event-001",), ("evidence-001", "evidence-002"), ArtifactStatus.CANDIDATE,
            "Only one pre-swap event unit is directly represented.",
        ),
        PeriodCharacterState(
            "period-state-002", "period-002", p2_scope, KnowledgeBoundary(2, ("fact-own-identity", "fact-body-swapped", "fact-disclosure-blocked", "fact-keigetsu-claimed-intent")),
            PeriodDomains(
                personality=DomainEntry(DomainEvidenceState.BOUNDED_INFERENCE, ("Across confinement and the rite, Reirin uses deliberate action and remains composed under physical danger while taking responsibility for concrete harm.",), ("event-003", "event-006", "event-007", "event-008"), ("evidence-005", "evidence-006", "evidence-007"), "This does not establish universal fearlessness or emotional invulnerability."),
                physical=DomainEntry(DomainEvidenceState.OBSERVED, ("Character identity remains 黃玲琳 while current body identity is 朱慧月; she experiences the current body as markedly healthy while her original body is fever-prone.",), ("event-002", "event-005"), ("evidence-003", "evidence-004")),
                motivation=DomainEntry(DomainEvidenceState.OBSERVED, ("She attempts to communicate her identity, survive the imposed process, and preserve responsibility toward her original body and harmed animals.",), ("event-003", "event-005", "event-007", "event-008"), ("evidence-004", "evidence-006")),
                backstory=DomainEntry(DomainEvidenceState.OBSERVED, ("She recalls frequent severe illness and sustained self-management before the exchange.",), ("event-005",), ("evidence-004",)),
                emotion=DomainEntry(DomainEvidenceState.OBSERVED, ("She expresses distress and tears at intense hatred, surprise and envy at health, and subdued remorse over animal deaths.",), ("event-004", "event-005", "event-007"), ("evidence-004", "evidence-006", "evidence-007")),
                relationships=DomainEntry(DomainEvidenceState.OBSERVED, ("Dongxue and Yaoming reject her identity claim; Keigetsu is an adversarial exchange partner; Chenyu begins reassessing the person publicly identified as Keigetsu.",), ("event-003", "event-004", "event-006", "event-008"), ("evidence-003",), "Chenyu's private thoughts are story-level and not included as Reirin knowledge."),
                growth=DomainEntry(DomainEvidenceState.BOUNDED_INFERENCE, ("Within this emergency period she adapts from failed identity proof to acting within the imposed public identity.",), ("event-003", "event-008"), ("evidence-003", "evidence-006"), "Persistence beyond the immediate constraint is unknown."),
                conflict=DomainEntry(DomainEvidenceState.OBSERVED, ("She is drawn to the borrowed body's health while explicitly maintaining duty to her original body and identity.",), ("event-005",), ("evidence-004",)),
            ), tuple(f"event-{i:03d}" for i in range(2, 9)), tuple(f"evidence-{i:03d}" for i in range(3, 8)), ArtifactStatus.CANDIDATE,
            "Adversarial testimony and derived speaker labels are retained with bounded certainty.",
        ),
        PeriodCharacterState(
            "period-state-003", "period-003", p3_scope, KnowledgeBoundary(3, ("fact-own-identity", "fact-body-swapped", "fact-warehouse-exile", "fact-lily-hostility", "fact-basic-supplies"), ("fact-lily-private-inducement",)),
            PeriodDomains(
                personality=DomainEntry(DomainEvidenceState.BOUNDED_INFERENCE, ("In the warehouse context Reirin acts politely, practically, and with marked self-direction.",), ("event-009", "event-011", "event-013"), ("evidence-008", "evidence-010", "evidence-013", "evidence-015"), "The short period cannot establish a stable lifetime trait."),
                physical=DomainEntry(DomainEvidenceState.OBSERVED, ("Character identity remains 黃玲琳 in 朱慧月's healthy body, enabling sustained movement, eating, and manual work not available in her original body.",), ("event-010", "event-011", "event-013"), ("evidence-009", "evidence-010", "evidence-013")),
                motivation=DomainEntry(DomainEvidenceState.OBSERVED, ("She pursues self-sufficient living, practical cultivation, food preparation, and limited rather than comprehensive outside aid.",), ("event-010", "event-011", "event-013"), ("evidence-010", "evidence-013",)),
                backstory=abstain(DomainEvidenceState.UNCHANGED),
                emotion=DomainEntry(DomainEvidenceState.OBSERVED, ("She explicitly expresses joy, excitement, and relief at freedom, privacy, food, and bodily capacity.",), ("event-010", "event-013"), ("evidence-009",)),
                relationships=DomainEntry(DomainEvidenceState.OBSERVED, ("Lily is openly hostile and reports prior abuse by the former body-owner; Reirin responds with attention, food sharing, and a constrained identity hint. Chenyu supplies basic necessities after her limited request.",), ("event-009", "event-011", "event-013"), ("evidence-008", "evidence-010", "evidence-013"), "Lily's private inducement remains excluded from Reirin-accessible state."),
                growth=DomainEntry(DomainEvidenceState.BOUNDED_INFERENCE, ("Relative to the protected pre-swap baseline, visible expression and independent activity expand under the healthy body and unsupervised environment.",), ("event-001", "event-010", "event-011", "event-013"), ("evidence-009", "evidence-010", "evidence-011", "evidence-015"), "Health, privacy, novelty, and situational necessity are competing explanations."),
                conflict=DomainEntry(DomainEvidenceState.OBSERVED, ("She enjoys the bodily freedom and warehouse life while remembering that the exchange arose from another person's hatred and remains unresolved.",), ("event-010", "event-013"), ("evidence-014",)),
            ), tuple(f"event-{i:03d}" for i in range(9, 14)), tuple(f"evidence-{i:03d}" for i in range(8, 16)), ArtifactStatus.CANDIDATE,
            "This candidate period covers only the initial relocation interval.",
        ),
    )

    decisions = (
        MemoryFormationDecision("event-001", MemoryFormationOutcome.DO_NOT_PERSIST, "The source supplies baseline state but no evidence of a distinct retained episode."),
        MemoryFormationDecision("event-002", MemoryFormationOutcome.PERSIST, "Identity/body transition is directly experienced and remains active.", "memory-002"),
        MemoryFormationDecision("event-003", MemoryFormationOutcome.PERSIST, "Failed identity proof directly shapes her current constraint.", "memory-003"),
        MemoryFormationDecision("event-004", MemoryFormationOutcome.PERSIST, "The asserted motive and disclosure restriction become accessible knowledge.", "memory-004"),
        MemoryFormationDecision("event-005", MemoryFormationOutcome.PERSIST, "She explicitly compares body states and recalls responsibility.", "memory-005"),
        MemoryFormationDecision("event-006", MemoryFormationOutcome.DO_NOT_PERSIST, "No later recall is shown within scope; its state evidence remains in Event/Evidence."),
        MemoryFormationDecision("event-007", MemoryFormationOutcome.PERSIST, "She explicitly assumes responsibility for deaths and later prays.", "memory-007"),
        MemoryFormationDecision("event-008", MemoryFormationOutcome.PERSIST, "Acquittal and continued identity restriction determine subsequent action.", "memory-008"),
        MemoryFormationDecision("event-009", MemoryFormationOutcome.PERSIST, "Lily's direct account is accessible and defines the current relationship constraint.", "memory-009"),
        MemoryFormationDecision("event-010", MemoryFormationOutcome.PERSIST, "Reirin explicitly reflects on freedom, expression, and the exchange.", "memory-010"),
        MemoryFormationDecision("event-011", MemoryFormationOutcome.DO_NOT_PERSIST, "Routine supply acquisition is retained as Event but no durable subjective meaning is shown."),
        MemoryFormationDecision("event-012", MemoryFormationOutcome.DO_NOT_PERSIST, "The event is inaccessible to Reirin in this source window."),
        MemoryFormationDecision("event-013", MemoryFormationOutcome.PERSIST, "She explicitly names the joy of applying learned knowledge and engages Lily.", "memory-013"),
    )
    memory_specs = {
        "memory-002": ("event-002", "period-002", "I woke in an unfamiliar body in a cell.", "My identity and current body no longer matched.", "confusion and alarm"),
        "memory-003": ("event-003", "period-002", "I could not state the exchange and Dongxue rejected private facts.", "Direct identity proof was blocked.", "frustration and shock"),
        "memory-004": ("event-004", "period-002", "The person in my original body claimed the exchange was intentional.", "The exchange partner asserted hostility and a disclosure restriction.", "distress with concern for the fevered body"),
        "memory-005": ("event-005", "period-002", "The borrowed body moved without my familiar illness symptoms.", "Health was deeply attractive, but my original body remained my responsibility.", "wonder and conflicted envy"),
        "memory-007": ("event-007", "period-002", "The mouse and lion died after the poison accident.", "I treated the deaths as consequences requiring apology and prayer.", "remorse"),
        "memory-008": ("event-008", "period-002", "The rite ended in acquittal but I remained unable to disclose identity.", "I had to act within the imposed public identity for now.", "relief constrained by unresolved identity"),
        "memory-009": ("event-009", "period-003", "Lily said the former body-owner abused her and refused service.", "Her hostility concerned acts attached to this body and public identity.", "concern and uncertainty"),
        "memory-010": ("event-010", "period-003", "The warehouse gave me room to move, work, and speak freely.", "Health and privacy made previously constrained activity possible.", "joy with unresolved duty"),
        "memory-013": ("event-013", "period-003", "I applied book knowledge to plants and shared cooked food with Lily.", "Practical experimentation and food sharing were possible here.", "joy and engagement"),
    }
    memories = tuple(
        MemoryRecord(mid, remembered, CREATED_AT, {"character_id": "Reirin", "event_copy": False}, (eid,), pid, remembered, meaning, affect, "Retained meaning is bounded to explicit source-supported awareness.", ())
        for mid, (eid, pid, remembered, meaning, affect) in memory_specs.items()
    )
    memory_index = tuple(
        MemoryIndexMetadata(memory.id, ("黃玲琳",), ("identity", "body", "experience"), memory.period_id, "source-window-significant")
        for memory in memories
    )

    skill_evidence = (
        SkillEvidence("skill-evidence-001", ("event-001",), ("evidence-001",), ("Produces the embroidery judged best among displayed festival works.",), ()),
        SkillEvidence("skill-evidence-002", ("event-013",), ("evidence-013",), ("Identifies edible growth, reorganizes beds, cultivates plants, and prepares food.",), ("States that relevant knowledge was learned from books.",)),
    )
    skill_profiles = (
        CharacterSkillProfile("skill-profile-001", "embroidery", SkillAcquisitionOrigin.CANON_SUPPORTED, "high-quality demonstrated work within the festival comparison", ("skill-evidence-001",), "period-001", ("No broader textile curriculum or professional standard is established.",), "Bystander superlatives are not treated as a formal proficiency scale."),
        CharacterSkillProfile("skill-profile-002", "practical-cultivation-and-food-preparation", SkillAcquisitionOrigin.CANON_SUPPORTED, "multiple basic tasks demonstrated successfully in one warehouse interval", ("skill-evidence-002",), "period-003", ("Short observation window; no expert agronomy or culinary level is established.",), "Demonstration combines book-derived knowledge with one observed implementation context."),
    )

    developments = (
        DevelopmentRecord(
            "development-001", "Visible emotional expression and independent physical activity increase after the body and environment changes.",
            ("period-state-001", "period-state-002", "period-state-003"), Lineage(parent_artifact_ids=("evidence-002", "evidence-004", "evidence-009", "evidence-010", "evidence-011", "evidence-015")),
            "supported as a bounded source-window contrast", ChangeResistance("unresolved", "The source window is too short to infer resistance to change.", "Confidence in the contrast does not determine persistence."),
            (HistoricalAdaptation("The post-swap healthy body and warehouse privacy coincide with broader expression and activity.", ("period-001", "period-002", "period-003"), ("evidence-004", "evidence-009", "evidence-010", "evidence-011", "evidence-015"), "Persistence beyond the initial warehouse interval is unknown."),),
            (CausalHypothesis("Reduced physical constraint and reduced observation may enable expression and autonomy previously suppressed by illness and protection.", ("evidence-002", "evidence-004", "evidence-009", "evidence-010"), ("evidence-011", "evidence-015"), ("Novelty of the environment or immediate survival necessity may explain part of the change.",), "The source supports correlation and Reirin's own contrast, not a finalized causal model."),),
            temporal_scope=TemporalScope(start="period-001", end="period-003", label="first-three-chapters-development"), status=ArtifactStatus.UNRESOLVED,
        ),
        DevelopmentRecord(
            "development-002", "Responsibility-directed action appears in both the adjudication and warehouse periods, but its breadth and durability remain unresolved.",
            ("period-state-002", "period-state-003"), Lineage(parent_artifact_ids=("evidence-004", "evidence-006", "evidence-010", "evidence-013", "evidence-015")),
            "limited cross-period support", ChangeResistance("unresolved", "Two short adjacent periods cannot establish change resistance."),
            causal_hypotheses=(CausalHypothesis("Prior illness-management experience may contribute to deliberate action under constraint.", ("evidence-004", "evidence-005", "evidence-010"), ("evidence-007", "evidence-015"), ("Immediate situational demands and the healthy borrowed body may sufficiently explain the actions.",), "Causal formation is provisional and not consolidated."),),
            temporal_scope=TemporalScope(start="period-002", end="period-003", label="first-three-chapters-development"), status=ArtifactStatus.UNRESOLVED,
        ),
    )
    compiled = (
        CompiledCharacterState(
            "compiled-reirin-v0.1", SCHEMA_VERSION, ARTIFACT_VERSION, "period-state-003",
            ("period-state-001", "period-state-002", "period-state-003"),
            (
                CompiledStateEntry("Current character identity is 黃玲琳 / Reirin while current body identity is 朱慧月 within this source window.", ("period-state-002", "period-state-003"), (), ("evidence-003", "evidence-004")),
                CompiledStateEntry("Current warehouse-period state includes explicit joy in bodily capacity, privacy, practical work, and applying learned knowledge.", ("period-state-003",), ("development-001",), ("evidence-009", "evidence-010", "evidence-013")),
                CompiledStateEntry("Composure and responsibility-taking are supported only as bounded patterns in the observed danger and settlement contexts.", ("period-state-002", "period-state-003"), ("development-002",), ("evidence-005", "evidence-006", "evidence-007", "evidence-015")),
                CompiledStateEntry("The current relationship with Lily begins under hostility attached to the former body-owner and includes Reirin's food sharing; Lily's private inducement is not accessible to Reirin.", ("period-state-003",), (), ("evidence-008", "evidence-012", "evidence-013")),
            ), ("development-001", "development-002"),
            (
                "Period 003 boundary remains candidate because only its opening interval is present.",
                "Long-term trait stability and change resistance are unresolved.",
                "Speaker attribution is derived and not treated as infallible.",
                "No knowledge after the first three chapters is included.",
                "Relationship ownership remains the Aiko architecture's unresolved issue.",
            ),
        ),
    )
    bundle = ReconstructionBundle(
        "reirin-reconstruction", 1, (source,), units, observations, events, evidence, (), (), None,
        {"schema_version": SCHEMA_VERSION, "character_id": "Reirin", "reconstruction_version": "0.1", "source_scope": "first-three-chapters-only"},
        periods, assignments,
    )
    graph = ReconstructionGraph(bundle, states, developments, memories, decisions, skill_evidence, skill_profiles, compiled)
    report = validate_reconstruction_graph(graph)
    report.raise_for_errors()
    return graph, memory_index


def _write(path: Path, artifact: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_portable_json(artifact, schema_version=SCHEMA_VERSION, artifact_version=ARTIFACT_VERSION), encoding="utf-8")


def persist(graph: ReconstructionGraph, memory_index: tuple[MemoryIndexMetadata, ...]) -> None:
    bundle = graph.bundle
    _write(INSTANCE_ROOT / "reconstruction/source_units/source_units_v0.1.json", bundle.source_units)
    _write(INSTANCE_ROOT / "reconstruction/observations/observations_v0.1.json", bundle.observations)
    _write(INSTANCE_ROOT / "reconstruction/events/events_v0.1.json", bundle.events)
    _write(INSTANCE_ROOT / "reconstruction/evidence/evidence_v0.1.json", bundle.evidence)
    _write(INSTANCE_ROOT / "reconstruction/periods/period_definitions_v0.1.json", bundle.period_definitions)
    _write(INSTANCE_ROOT / "reconstruction/periods/period_assignments_v0.1.json", bundle.period_assignments)
    _write(INSTANCE_ROOT / "reconstruction/periods/period_states_v0.1.json", graph.period_states)
    _write(INSTANCE_ROOT / "reconstruction/development/development_v0.1.json", graph.developments)
    _write(INSTANCE_ROOT / "memory/records/memory_decisions_v0.1.json", graph.memory_decisions)
    _write(INSTANCE_ROOT / "memory/records/memories_v0.1.json", graph.memories)
    _write(INSTANCE_ROOT / "memory/index/memory_index_v0.1.json", memory_index)
    _write(INSTANCE_ROOT / "character/skill_profile/skill_evidence_v0.1.json", graph.skill_evidence)
    _write(INSTANCE_ROOT / "character/skill_profile/skill_profile_v0.1.json", graph.skill_profiles)
    _write(INSTANCE_ROOT / "character/compiled/compiled_character_state_v0.1.json", graph.compiled_states)
    manifest = {
        "architecture_version": "character_create_v0.0.8", "artifact_counts": {
            "source_references": len(bundle.sources), "source_units": len(bundle.source_units),
            "observations": len(bundle.observations), "events": len(bundle.events), "evidence_records": len(bundle.evidence),
            "periods": len(bundle.period_definitions), "period_assignments": len(bundle.period_assignments),
            "period_character_states": len(graph.period_states), "memory_decisions": len(graph.memory_decisions),
            "memory_records": len(graph.memories), "skill_evidence": len(graph.skill_evidence),
            "character_skill_profiles": len(graph.skill_profiles), "development_records": len(graph.developments),
            "compiled_character_states": len(graph.compiled_states),
        },
        "character_id": "Reirin", "framework": "Aiko", "reconstruction_version": "0.1",
        "source_path": SOURCE_RELATIVE, "source_role": "approved_reconstruction_input",
        "source_annotation_status": "speaker attribution is derived and not guaranteed",
        "source_hash": {"sha256": bundle.sources[0].metadata["sha256"], "git_blob": bundle.sources[0].metadata["git_blob"]},
        "source_scope": "Volume 1 selected prologue/first three chapters file only",
        "source_reference": json.loads(to_portable_json(bundle.sources[0], schema_version=SCHEMA_VERSION, artifact_version=ARTIFACT_VERSION))["artifact"],
        "periods": [{"id": p.id, "order": p.order, "status": p.boundary_status.value, "reason": p.boundary_reason} for p in bundle.period_definitions],
        "validation_status": "pending persisted reload validation",
        "known_limitations": ["short source window", "derived speaker annotation", "candidate final period boundary", "no later-source knowledge"],
        "unresolved_items": list(graph.compiled_states[0].unresolved_items),
    }
    path = INSTANCE_ROOT / "reconstruction/manifests/reconstruction_v0.1_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    built_graph, built_index = build_graph()
    persist(built_graph, built_index)
