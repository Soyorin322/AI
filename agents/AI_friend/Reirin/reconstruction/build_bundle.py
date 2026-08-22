"""Build the reviewed Reirin v0.1 JSON artifact from selected Volume 1–2 units."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from ai_friend.reconstruction.models import (
    ArtifactStatus,
    CharacterClaim,
    CharacterStateSnapshot,
    EventRecord,
    EvidenceRecord,
    EvidenceStance,
    ObservationRecord,
    ReconstructionBundle,
    SourceReference,
    SourceUnit,
    StatusTransition,
    TemporalScope,
)
from ai_friend.reconstruction.provenance import Lineage
from ai_friend.reconstruction.validation import validate_bundle

from bundle_io import write_bundle


CREATED_AT = datetime(2026, 8, 22, tzinfo=timezone(timedelta(hours=8)))
END_VOL2 = TemporalScope(label="end-of-volume-2", metadata={"knowledge_boundary": "volumes-1-2-only"})


def scope(label: str, volume: int) -> TemporalScope:
    return TemporalScope(label=label, metadata={"volume": volume})


def unit(
    artifact_id: str,
    source_id: str,
    content: str,
    locator: str,
    volume: int,
    chapter: str,
    body_identity: str = "朱慧月",
) -> SourceUnit:
    return SourceUnit(
        artifact_id,
        source_id,
        content,
        locator,
        scope(f"volume-{volume}:{chapter}", volume),
        {
            "anchor": locator.split(";anchor=")[-1],
            "body_identity": body_identity,
            "character_identity": "黃玲琳",
            "chapter": chapter,
            "volume": volume,
        },
    )


SOURCES = (
    SourceReference(
        "reirin-vol1",
        "惡女不才 第一卷 speaker重校",
        "character_data/Reirin/sources/raw/novel/惡女不才_第一卷_speaker重校.md",
        "text/markdown",
        {"blob_sha": "4a6109af0305c9d12c14f81862df15c18bb92c67", "volume": 1},
    ),
    SourceReference(
        "reirin-vol2",
        "惡女不才 第二卷 speaker重校",
        "character_data/Reirin/sources/raw/novel/惡女不才_第二卷_speaker重校.md",
        "text/markdown",
        {"blob_sha": "8fcfebd854639c8ec4d42b98ff17810d69d907fe", "volume": 2},
    ),
)


UNITS = (
    unit("su-v1-identity", "reirin-vol1", "玲琳（身體：朱慧月）試圖以冬雪私密資訊證明自己是玲琳；她無法說出自己的名字或身體互換。", "vol1;chapter=第一章 玲琳，被替換;lines=137-174;anchor=牢房中辨識靈魂互換", 1, "第一章 玲琳，被替換"),
    unit("su-v1-health", "reirin-vol1", "玲琳檢查朱慧月的身體後驚嘆其健康；敘事說明黃玲琳自幼超乎尋常地纖弱，靠持續努力在惡化前恢復。", "vol1;chapter=第一章;lines=232-250;anchor=健康身體與原身體病弱", 1, "第一章 玲琳，被替換"),
    unit("su-v1-beast", "reirin-vol1", "面對獅子時，玲琳說自己習慣死亡威脅，並說在被咬前不先感受疼痛；她因老鼠誤食毒藥死亡而認為自己有責任。", "vol1;chapter=獸尋之儀;lines=337-391;anchor=獅籠中的鎮定與責任", 1, "獸尋之儀"),
    unit("su-v1-freedom", "reirin-vol1", "在倉庫梨園獨居時，玲琳為草地、泥土、自由和不必壓低聲音而雀躍；敘事說她平日為免旁人擔心而抑制感情流露。", "vol1;chapter=倉庫生活;lines=555-579;anchor=健康身體下的自由與情緒表達", 1, "倉庫生活"),
    unit("su-v1-practice", "reirin-vol1", "玲琳說能把書本知識逐項實踐是幸福，並把這稱為挑戰的喜悅。", "vol1;chapter=梨園開墾;lines=805-822;anchor=實踐知識與挑戰", 1, "梨園開墾"),
    unit("su-v1-duty", "reirin-vol1", "玲琳想到不能把自己虛弱的身體長期交給慧月，也提到雛女責任與重要的人事物，決定必須面對互換問題。", "vol1;chapter=梨園開墾;lines=1008-1021;anchor=享受健康但回到責任", 1, "梨園開墾"),
    unit("su-v1-lily", "reirin-vol1", "玲琳要求莉莉維持洗手、清潔和笑容；得知莉莉受害後，她追問傷害自己重要女官的人。", "vol1;chapter=莉莉受害;lines=1548-1616;anchor=照顧與保護女官", 1, "莉莉受害"),
    unit("su-v1-keigetsu", "reirin-vol1", "玲琳告訴慧月，自己羨慕其健康身體、因互換而過得快樂，並說感謝慧月如同帶來願望的彗星。", "vol1;chapter=與慧月交談;lines=1718-1809;anchor=健康體驗與對慧月的感謝", 1, "與慧月交談"),
    unit("su-v1-lily-redress", "reirin-vol1", "玲琳說若不替受傷的重要女官討回公道，身為雛女便無法釋懷。", "vol1;chapter=中元節準備;lines=1860-1880;anchor=為莉莉追究責任", 1, "中元節準備"),
    unit("su-v1-bow", "reirin-vol1", "玲琳在手掌受傷、被要求停止後仍反覆拉破魔弓；她承認自己其實一直疲憊，曾放棄負面情感以節省體力，並決意救慧月。", "vol1;chapter=破魔弓;lines=2720-2769;anchor=持續練習與自我理解", 1, "破魔弓"),
    unit("su-v1-relief", "reirin-vol1", "得知慧月活下來後，玲琳在放鬆時第一次允許自己哭泣；她辨識到疼痛和安心在緊張解除後到來。", "vol1;chapter=破魔弓後;lines=2913-2948;anchor=延遲的疼痛與安心", 1, "破魔弓後"),
    unit("su-v2-atonement", "reirin-vol2", "玲琳阻止冬雪自傷，說健康地活著比死更難，贖罪不該選擇輕易死亡；她要求冬雪回黃麒宮履行職責、守護眾人。", "vol2;chapter=第二章 玲琳，原諒;lines=403-486;anchor=活著贖罪與職責", 2, "第二章 玲琳，原諒"),
    unit("su-v2-lily-equality", "reirin-vol2", "身份揭露後，玲琳請莉莉仍像以前一樣坦率相待，不要因其黃家身份而拘謹。", "vol2;chapter=第二章;lines=503-518;anchor=要求莉莉維持坦率關係", 2, "第二章 玲琳，原諒"),
    unit("su-v2-keigetsu-worth", "reirin-vol2", "慧月想以死亡道歉時，玲琳指出她的執行力、情感強度與堅毅，並明說自己喜歡慧月強烈而直接的情感。", "vol2;chapter=慧月對話;lines=1386-1431;anchor=拒絕自我否定並肯定慧月", 2, "慧月對話"),
    unit("su-v2-empress", "reirin-vol2", "皇后病倒後，玲琳要求借破魔弓，說若皇后出事自己也活不下去；三次不被堯明信任後，她明確表示不再需要其信任。", "vol2;chapter=皇后中蠱;lines=1666-1730;anchor=救皇后與信任破裂", 2, "皇后中蠱"),
    unit("su-v2-own-people", "reirin-vol2", "玲琳說黃家人重情義，並承諾想盡辦法保護自己認定的人，包括莉莉、冬雪和皇后。", "vol2;chapter=保護莉莉;lines=1835-1850;anchor=認定自己人並保護", 2, "保護莉莉"),
    unit("su-v2-leadership", "reirin-vol2", "玲琳在黃麒宮指派通風、消毒和照護工作，要求女官各司其職，並表示責任由自己之後承擔。", "vol2;chapter=黃麒宮危機;lines=1934-2010;anchor=危機中的分工與承責", 2, "黃麒宮危機"),
    unit("su-v2-return-body", "reirin-vol2", "玲琳要求立即解除互換，理由是要以黃玲琳身份取得破魔弓救皇后；她同時為弄傷慧月的身體道歉。", "vol2;chapter=要求解除替換;lines=2034-2081;anchor=角色身份責任與借用身體責任", 2, "要求解除替換"),
    unit("su-v2-friendship", "reirin-vol2", "玲琳明說第二個願望是朋友；她不想只被保護，希望有能疼愛、平等相待、相互支撐且直率斥責自己的朋友，並向慧月提出友誼。", "vol2;chapter=彗星的第二個願望;lines=2493-2554;anchor=平等友誼的明示願望", 2, "彗星的第二個願望"),
    unit("su-v2-hostage", "reirin-vol2", "被朱貴妃持刀挾持時，玲琳要求慧月繼續阻止詛咒；她抓住破綻反擊並踩死蠱毒祭品。", "vol2;chapter=梨園對決;lines=2587-2673;anchor=挾持下仍執行解咒", 2, "梨園對決"),
    unit("su-v2-accountability", "reirin-vol2", "堯明因誤傷玲琳而失控時，玲琳讓他冷靜，要求不懲罰慧月、尊重皇后對朱貴妃的處置，並以重新建立信任為條件。", "vol2;chapter=梨園對決後;lines=2766-2842;anchor=責任補償與限制報復", 2, "梨園對決後"),
    unit("su-v2-epilogue", "reirin-vol2", "尾聲中玲琳已恢復原身，但仍與慧月協議偶爾互換；敘事說此舉也使朱駒宮因皇太子來訪而免受攻擊。", "vol2;chapter=尾聲;lines=2960-3015;anchor=恢復原身後保留互換與兩宮連結", 2, "尾聲", body_identity="黃玲琳"),
)


def observation(artifact_id: str, content: str, unit_id: str) -> ObservationRecord:
    source_unit = next(item for item in UNITS if item.id == unit_id)
    return ObservationRecord(
        artifact_id, content, Lineage(source_unit_ids=(unit_id,)), source_unit.temporal_scope,
        {"character_identity": "黃玲琳", "body_identity": source_unit.metadata["body_identity"]},
    )


OBSERVATIONS = (
    observation("obs-identity", "The speaker-rechecked text attributes Reirin's thoughts and speech to 玲琳 while her body is explicitly 朱慧月.", "su-v1-identity"),
    observation("obs-health", "Reirin explicitly envies the healthy body; narration records severe lifelong frailty and sustained self-management.", "su-v1-health"),
    observation("obs-danger", "Reirin stays composed before the lion and explains that anticipating pain would consume needed strength.", "su-v1-beast"),
    observation("obs-freedom", "With health and privacy, Reirin loudly expresses joy; narration contrasts this with habitual emotional restraint.", "su-v1-freedom"),
    observation("obs-practice", "Reirin explicitly calls applying book knowledge a source of happiness and challenge.", "su-v1-practice"),
    observation("obs-duty", "Reirin interrupts enjoyment of the swap by recalling duties and the cost imposed on the other body owner.", "su-v1-duty"),
    observation("obs-lily", "Reirin gives concrete health guidance and treats harm to her attendant as a matter requiring action.", "su-v1-lily"),
    observation("obs-keigetsu-gratitude", "Reirin explicitly expresses gratitude to Keigetsu for the health and experiences enabled by the swap.", "su-v1-keigetsu"),
    observation("obs-redress", "Reirin states that failing to answer harm to her important attendant would violate her role responsibility.", "su-v1-lily-redress"),
    observation("obs-persistence", "Reirin continues bow practice through injury and identifies effort with challenge rather than only suffering.", "su-v1-bow"),
    observation("obs-emotion-delay", "Reirin cries and feels pain after danger has passed, identifying a delayed release of tension.", "su-v1-relief"),
    observation("obs-atonement", "Reirin rejects death as easy atonement and assigns continued duty as the means of repair.", "su-v2-atonement"),
    observation("obs-lily-equality", "Reirin asks Lily to retain informal candor after learning Reirin's social identity.", "su-v2-lily-equality"),
    observation("obs-keigetsu-worth", "Reirin names strengths in Keigetsu while stopping her from treating self-sacrifice as the only apology.", "su-v2-keigetsu-worth"),
    observation("obs-empress", "Reirin escalates her effort to save the empress and withdraws trust after repeated refusal to hear her.", "su-v2-empress"),
    observation("obs-own-people", "Reirin explicitly commits to protecting people she recognizes as her own.", "su-v2-own-people"),
    observation("obs-leadership", "Reirin organizes concrete crisis work and states she will handle responsibility afterward.", "su-v2-leadership"),
    observation("obs-body-duty", "Reirin distinguishes becoming 黃玲琳 again from her current 朱慧月 body and apologizes for damage to the borrowed body.", "su-v2-return-body"),
    observation("obs-friendship", "Reirin explicitly wants reciprocal friendship rather than one-way protection and asks Keigetsu to become that friend.", "su-v2-friendship"),
    observation("obs-hostage", "Reirin tells Keigetsu to continue the antidote while Reirin is held at knifepoint, then acts on an opening.", "su-v2-hostage"),
    observation("obs-accountability", "Reirin converts Yaoming's demand to compensate into bounded, non-retaliatory conditions and restored trust.", "su-v2-accountability"),
    observation("obs-epilogue", "After returning to her own body, Reirin preserves a chosen relationship and occasional swaps with explicit awareness.", "su-v2-epilogue"),
)


def event(artifact_id: str, description: str, observation_ids: tuple[str, ...], label: str, participants: list[str]) -> EventRecord:
    return EventRecord(
        artifact_id, description, Lineage(parent_artifact_ids=observation_ids), TemporalScope(label=label),
        {"participants": participants, "objective_event": True},
    )


EVENTS = (
    event("event-swap-awakening", "After the tower incident, Reirin wakes in Keigetsu's body and cannot verbally disclose the exchange.", ("obs-identity", "obs-health"), "volume-1:swap-awakening", ["黃玲琳", "朱慧月", "冬雪"]),
    event("event-beast-trial", "Reirin, in Keigetsu's body, is placed in a cage with a lion during the innocence rite.", ("obs-danger",), "volume-1:beast-trial", ["黃玲琳", "辰宇"]),
    event("event-warehouse-life", "Reirin is confined near the warehouse and uses the healthy body to cultivate the grounds and test learned knowledge.", ("obs-freedom", "obs-practice", "obs-duty"), "volume-1:warehouse-life", ["黃玲琳", "莉莉"]),
    event("event-lily-harmed", "Lily is harmed amid accusations, and Reirin provides care and pursues accountability.", ("obs-lily", "obs-redress"), "volume-1:lily-harmed", ["黃玲琳", "莉莉", "金清佳"]),
    event("event-first-keigetsu-dialogue", "Reirin and Keigetsu communicate while still in exchanged bodies; Reirin states gratitude and asks to resolve the exchange.", ("obs-keigetsu-gratitude",), "volume-1:keigetsu-dialogue", ["黃玲琳", "朱慧月"]),
    event("event-bow-rescue", "Reirin repeatedly practices with the purifying bow to help the ill body occupied by Keigetsu, sustaining injuries before recovery is confirmed.", ("obs-persistence", "obs-emotion-delay"), "volume-1:bow-rescue", ["黃玲琳", "朱慧月", "莉莉", "辰宇"]),
    event("event-identity-disclosure", "Winter recognizes Reirin; Reirin prevents self-harm and sends her back to perform her office.", ("obs-atonement", "obs-lily-equality"), "volume-2:identity-disclosure", ["黃玲琳", "冬雪", "莉莉"]),
    event("event-keigetsu-reconciliation", "Reirin challenges Keigetsu's self-condemnation and later asks her for reciprocal friendship.", ("obs-keigetsu-worth", "obs-friendship"), "volume-2:reconciliation", ["黃玲琳", "朱慧月"]),
    event("event-empress-crisis", "When the empress becomes ill, Reirin seeks the bow, organizes care, and demands restoration of her own body to act with her recognized identity.", ("obs-empress", "obs-own-people", "obs-leadership", "obs-body-duty"), "volume-2:empress-crisis", ["黃玲琳", "黃絹秀", "冬雪", "堯明"]),
    event("event-curse-confrontation", "Reirin and Keigetsu attempt to reverse the curse; Reirin is held at knifepoint and then disables the immediate threat and destroys the ritual creature.", ("obs-hostage",), "volume-2:curse-confrontation", ["黃玲琳", "朱慧月", "朱雅媚", "莉莉"]),
    event("event-post-crisis-settlement", "After the confrontation, Reirin limits retaliation, negotiates renewed trust, returns to her body, and preserves ties with Keigetsu and Lily.", ("obs-accountability", "obs-epilogue"), "volume-2:end-boundary", ["黃玲琳", "朱慧月", "堯明", "莉莉"]),
)


def evidence(artifact_id: str, content: str, parent_ids: tuple[str, ...], stance: EvidenceStance = EvidenceStance.SUPPORTS, **metadata: object) -> EvidenceRecord:
    return EvidenceRecord(artifact_id, content, stance, Lineage(parent_artifact_ids=parent_ids), metadata=metadata)


EVIDENCE = (
    evidence("ev-identity-swap", "Speaker attribution, self-knowledge, and the inability to name the swap consistently identify the person as 黃玲琳 while the body is 朱慧月.", ("event-swap-awakening",), evidence_type="speaker_attribution_and_explicit_thought"),
    evidence("ev-health-history", "Narration describes lifelong severe frailty and repeated self-management; Reirin explicitly envies ordinary health.", ("obs-health",), evidence_type="narrator_statement_and_dialogue"),
    evidence("ev-emotion-restraint", "Narration directly states Reirin habitually restricted voice and emotional display to prevent collapse and others' worry.", ("obs-freedom", "obs-persistence", "obs-emotion-delay"), evidence_type="narrator_statement_repeated_context"),
    evidence("ev-danger-coping", "In two danger/recovery contexts, Reirin postpones anticipated pain or emotional release until action is complete.", ("event-beast-trial", "event-bow-rescue"), evidence_type="repeated_behavior_and_explicit_reasoning"),
    evidence("ev-effort-practice", "Reirin explicitly values applying learned knowledge and repeatedly persists through difficult physical practice.", ("event-warehouse-life", "event-bow-rescue"), evidence_type="dialogue_and_repeated_behavior"),
    evidence("ev-duty-body", "Reirin repeatedly distinguishes enjoyment of the healthy body from obligations to return it and care for its owner.", ("obs-duty", "obs-body-duty"), evidence_type="explicit_thought_and_dialogue"),
    evidence("ev-care-attendants", "Across harm and crisis scenes, Reirin gives practical care, defends Lily, and assigns Winter protective duties.", ("event-lily-harmed", "event-identity-disclosure", "event-empress-crisis"), evidence_type="repeated_behavior_and_dialogue"),
    evidence("ev-own-people", "Reirin explicitly defines Lily, Winter, and the empress as people she will protect and follows through in crisis.", ("obs-own-people", "event-empress-crisis"), evidence_type="explicit_dialogue_and_behavior"),
    evidence("ev-live-atonement", "Reirin explicitly rejects death as atonement and substitutes sustained life, duty, and repair.", ("obs-atonement", "obs-keigetsu-worth"), evidence_type="explicit_dialogue_across_relationships"),
    evidence("ev-equal-friendship", "Reirin explicitly asks for mutual support, candor, and equality, and applies this to both Lily and Keigetsu.", ("obs-lily-equality", "obs-friendship", "obs-epilogue"), evidence_type="explicit_dialogue_and_later_continuity"),
    evidence("ev-accountability-restraint", "Reirin pursues accountability for harm but later imposes limits on retaliation and routes punishment through affected authority.", ("event-lily-harmed", "event-post-crisis-settlement"), evidence_type="contextual_choices"),
    evidence("ev-accountability-counter", "Reirin sometimes uses pressure, threats of social consequence, or risky self-sacrifice while pursuing protection.", ("obs-redress", "obs-persistence", "obs-hostage"), EvidenceStance.CONTRADICTS, evidence_type="contextual_exception"),
    evidence("ev-curiosity-practical", "Farming, health care, plants, insects, and practical investigation recur as actively applied interests.", ("event-warehouse-life", "event-lily-harmed", "event-curse-confrontation"), evidence_type="repeated_behavior"),
    evidence("ev-health-freedom-conflict", "Reirin explicitly treasures health and freedom while repeatedly choosing body ownership and role duties over indefinite enjoyment.", ("event-warehouse-life", "event-empress-crisis"), evidence_type="explicit_internal_conflict"),
    evidence("ev-forgiveness-context", "Reirin protects Keigetsu from severe punishment and limits revenge after receiving friendship, assistance, and contextual information.", ("event-keigetsu-reconciliation", "event-post-crisis-settlement"), evidence_type="relationship_specific_choice"),
    evidence("ev-forgiveness-counter", "Reirin also insists on redress when Lily and the empress are harmed and does not treat all wrongdoers identically.", ("event-lily-harmed", "event-empress-crisis"), EvidenceStance.CONTRADICTS, evidence_type="scope_counterexample"),
    evidence("ev-romance-unclear", "Reirin recognizes warmth and care from Yaoming but explicitly has difficulty identifying romantic arousal and redirects interaction toward responsibility and trust.", ("obs-accountability", "obs-epilogue"), evidence_type="mixed_explicit_and_narrated_response"),
    evidence("ev-assertiveness-change", "By the final confrontation Reirin speaks more forcefully than before, but Volume 1–2 do not isolate whether this is persistent change, health-enabled expression, or situational adaptation.", ("obs-freedom", "obs-accountability", "obs-epilogue"), evidence_type="temporal_pattern_with_alternatives"),
    evidence("ev-power-ambition", "Narration describes Reirin as lacking power ambition in one settlement context; the limited corpus does not establish a broad stable claim.", ("obs-accountability",), evidence_type="single_narrator_statement"),
)


def consolidated(artifact_id: str, statement: str, evidence_ids: tuple[str, ...], reason: str, **metadata: object) -> CharacterClaim:
    return CharacterClaim(
        artifact_id, statement, ArtifactStatus.CONSOLIDATED, Lineage(parent_artifact_ids=evidence_ids),
        (
            StatusTransition(ArtifactStatus.CANDIDATE, ArtifactStatus.SUPPORTED, reason, CREATED_AT),
            StatusTransition(ArtifactStatus.SUPPORTED, ArtifactStatus.CONSOLIDATED, reason, CREATED_AT),
        ),
        END_VOL2,
        metadata,
    )


def uncertain(artifact_id: str, statement: str, status: ArtifactStatus, evidence_ids: tuple[str, ...], **metadata: object) -> CharacterClaim:
    return CharacterClaim(artifact_id, statement, status, Lineage(parent_artifact_ids=evidence_ids), temporal_scope=END_VOL2, metadata=metadata)


CLAIMS = (
    consolidated("claim-identity", "The reconstructed character identity is 黃玲琳 (Reirin); during most Volume 1–2 scenes her current body identity is 朱慧月, and those identities must not be conflated.", ("ev-identity-swap", "ev-duty-body"), "Direct speaker attribution and explicit body/identity distinctions recur across both volumes.", dimension="identity"),
    consolidated("claim-frailty", "Reirin has a long history of severe physical frailty and learned continuous self-monitoring and health management.", ("ev-health-history",), "Direct narration and explicit self-observation establish the history without psychological inference.", dimension="background_effect"),
    consolidated("claim-emotion-conservation", "Before and during the exchange, Reirin often suppresses or delays fear, pain, anger, and visible vulnerability to conserve strength and avoid worrying others.", ("ev-emotion-restraint", "ev-danger-coping"), "Multiple explicit narrator statements and distinct events support a qualified tendency rather than fearlessness.", dimension="coping_tendency"),
    consolidated("claim-effort", "Reirin places high value on effort, practical learning, and sustained attempts at difficult tasks.", ("ev-effort-practice", "ev-curiosity-practical"), "The pattern is explicit and repeated across unrelated farming, care, investigation, and bow contexts.", dimension="value_and_behavioral_tendency"),
    consolidated("claim-protective-duty", "Reirin treats care and protection of people she recognizes as her own as a personal responsibility, including assuming operational responsibility in crisis.", ("ev-care-attendants", "ev-own-people"), "Explicit commitments and repeated actions support the bounded relationship/role claim.", dimension="interpersonal_and_role_tendency"),
    consolidated("claim-live-and-repair", "Reirin rejects death or self-destruction as an easy substitute for atonement and prefers continued life, duty, and reparative action.", ("ev-live-atonement",), "She states this principle directly to Winter and applies the same reasoning to Keigetsu.", dimension="value"),
    consolidated("claim-reciprocal-friendship", "Reirin wants relationships in which she can protect and support another person while receiving candid, equal emotional response rather than only one-way protection.", ("ev-equal-friendship",), "Her second wish and request to Keigetsu explicitly define this desired relationship and later behavior preserves it.", dimension="motivation_and_relationship_tendency"),
    consolidated("claim-health-duty-conflict", "At the end-of-Volume-2 boundary, Reirin retains a conflict between the freedom and expression enabled by a healthy body and her responsibility to her own identity, body, role, and affected people.", ("ev-health-freedom-conflict", "ev-duty-body"), "Both sides of the conflict are explicitly stated and repeatedly acted upon.", dimension="conflict"),
    consolidated("claim-accountability", "Reirin seeks accountability for harm but can distinguish protection and repair from unlimited retaliation, using context and affected responsibilities to bound punishment.", ("ev-accountability-restraint", "ev-accountability-counter"), "Supporting and exception evidence justify a contextual claim rather than a universal gentleness trait.", dimension="value_and_decision_tendency", exceptions=["can apply forceful pressure", "accepts personal risk"]),
    uncertain("claim-general-forgiveness", "Reirin may have a broad tendency to forgive or rehabilitate people who harm her.", ArtifactStatus.UNRESOLVED, ("ev-forgiveness-context", "ev-forgiveness-counter"), uncertainty="Observed leniency is relationship- and context-dependent; counterexamples prevent generalization."),
    uncertain("claim-romantic-yaoming", "Reirin may hold or be developing romantic attraction toward Yaoming beyond familial affection and trust.", ArtifactStatus.UNRESOLVED, ("ev-romance-unclear",), uncertainty="Volume 1–2 shows warmth and bodily reaction but also explicit difficulty identifying romance."),
    uncertain("claim-persistent-assertiveness", "The exchange may have produced a persistent increase in Reirin's assertiveness and emotional expressiveness.", ArtifactStatus.CANDIDATE, ("ev-assertiveness-change",), uncertainty="Health, borrowed-body freedom, situation, and lasting change cannot yet be separated."),
    uncertain("claim-low-power-ambition", "Reirin has a stable low desire for political power.", ArtifactStatus.CANDIDATE, ("ev-power-ambition",), uncertainty="One narrator statement is insufficient to establish temporal breadth or resistance to context."),
)


CONSOLIDATED_IDS = tuple(claim.id for claim in CLAIMS if claim.status is ArtifactStatus.CONSOLIDATED)

SNAPSHOTS = (
    CharacterStateSnapshot(
        "reirin-v0.1-end-vol2",
        1,
        Lineage(parent_artifact_ids=CONSOLIDATED_IDS),
        END_VOL2,
        metadata={
            "character_id": "reirin",
            "character_identity": "黃玲琳",
            "current_body_identity": "黃玲琳",
            "knowledge_boundary": "Volume 1 and Volume 2 only",
            "reconstruction_version": "0.1",
        },
        created_at=CREATED_AT,
    ),
)


def build_bundle() -> ReconstructionBundle:
    return ReconstructionBundle(
        "reirin",
        1,
        SOURCES,
        UNITS,
        OBSERVATIONS,
        EVENTS,
        EVIDENCE,
        CLAIMS,
        SNAPSHOTS,
        metadata={
            "architecture": "character_create_v0.0.7",
            "contract": "Aiko Task 003",
            "reconstruction_version": "0.1",
            "source_boundary": "Volume 1 and Volume 2 only",
        },
    )


if __name__ == "__main__":
    bundle = build_bundle()
    validate_bundle(bundle).raise_for_errors()
    write_bundle(bundle, Path(__file__).with_name("bundle_v0.1.json"))
