from __future__ import annotations

import re
from collections import Counter, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOVEL_DIR = ROOT / "character_data" / "Reirin" / "sources" / "raw" / "novel"

VOLUMES = {
    2: (
        NOVEL_DIR / "惡女不才，請多關照！～雛宮蝶鼠換身傳～ [第二卷] [中村颯希].txt",
        NOVEL_DIR / "惡女不才_第二卷_speaker重校.md",
    ),
    3: (
        NOVEL_DIR / "惡女不才，請多關照！～雛宮蝶鼠換身傳～ [第三卷] [中村颯希].txt",
        NOVEL_DIR / "惡女不才_第三卷_speaker重校.md",
    ),
}

GOLD = NOVEL_DIR / "惡女不才_第一卷_speaker重校.md"

# Canonical identity names.  Visible body/role aliases are normalized separately.
BASE_CHARACTERS = [
    "玲琳", "慧月", "冬雪", "莉莉", "堯明", "辰宇", "絹秀", "雅媚",
    "清佳", "芳春", "歌吹", "景行", "景彰", "文昴", "弦耀",
    "琥珀", "依依", "安安", "雲嵐", "豪龍", "杏婆", "江德勝",
    "林熙", "泰龍", "林", "俱理須益",
]

ALIASES = {
    "黃玲琳": "玲琳", "玲琳": "玲琳",
    "朱慧月": "慧月", "慧月": "慧月",
    "冬雪": "冬雪", "莉莉": "莉莉",
    "皇太子堯明": "堯明", "堯明": "堯明", "皇太子": "堯明",
    "鷲官長辰宇": "辰宇", "辰宇": "辰宇", "鷲官長": "辰宇",
    "皇后絹秀": "絹秀", "絹秀": "絹秀",
    "朱貴妃雅媚": "雅媚", "朱雅媚": "雅媚", "雅媚": "雅媚", "朱貴妃": "雅媚",
    "金清佳": "清佳", "清佳": "清佳",
    "藍芳春": "芳春", "芳春": "芳春",
    "玄歌吹": "歌吹", "歌吹": "歌吹",
    "黃景行": "景行", "景行": "景行",
    "黃景彰": "景彰", "景彰": "景彰",
    "文昴": "文昴", "弦耀": "弦耀",
    "琥珀": "琥珀", "依依": "依依", "安安": "安安",
    "雲嵐": "雲嵐", "豪龍": "豪龍", "杏婆": "杏婆",
    "江德勝": "江德勝", "江氏": "江德勝",
    "藍林熙": "林熙", "林熙": "林熙",
    "泰龍": "泰龍",
}

# Generic speakers are used only when the text itself makes the class explicit.
GENERIC = ["女官", "藤黃女官", "銀硃女官", "鄉民", "女人", "男人", "少年", "老婦人", "小姓", "鷲官", "侍童", "護衛", "邑民"]

SPEECH_CUES = (
    "說", "說道", "問", "問道", "回答", "答道", "回應", "喊", "叫", "叫道",
    "嘟囔", "喃喃", "呢喃", "開口", "反駁", "補充", "打斷", "責備", "斥責",
    "怒吼", "低聲", "輕聲", "高聲", "大聲", "小聲", "宣告", "詢問", "附和",
    "吐槽", "感嘆", "勸", "命令", "催促", "提醒", "笑道", "哭喊", "驚呼",
    "接著說", "繼續說", "這麼說", "這麼問", "搭話", "回嘴", "應道", "答應",
)

QUOTE_RE = re.compile(r"^[\s　]*[「『]")
HEADING_RE = re.compile(r"^[\s　]*(?:▶︎▶︎【|【第|【序|【尾聲|【後記|【附錄|【特典SS|\*\*\*|＊＊＊)")


def strip_existing_label(line: str) -> str:
    # Source TXT should be unlabelled, but this makes reruns idempotent if used on an annotated file.
    return re.sub(r"^(?:[^：:\n]{1,40}: )(?=[「『])", "", line)


def gold_speakers() -> list[str]:
    names = []
    if not GOLD.exists():
        return BASE_CHARACTERS
    for line in GOLD.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([^:\n]{1,40}):\s*[「『]", line)
        if not m:
            continue
        label = re.sub(r"（身體：[^）]+）", "", m.group(1))
        if "speaker 不確定" not in label and label not in names:
            names.append(label)
    return names + [x for x in BASE_CHARACTERS if x not in names]


def names_in(text: str) -> list[str]:
    found = []
    # Long aliases first so 黃玲琳 is not double counted as 玲琳.
    for alias in sorted(ALIASES, key=len, reverse=True):
        if alias in text:
            canon = ALIASES[alias]
            if canon not in found:
                found.append(canon)
    return found


def generic_from_narration(text: str) -> str | None:
    # Only accept explicit grammatical subjects, never infer an anonymous class from the scene alone.
    pats = [
        ("女官", r"(?:一名|幾名|那些|旁邊的|身著[^，。]{0,12}的)?女官[^，。]{0,14}(?:說|喊|叫|問|嘟囔|喃喃|開口|回答|附和)"),
        ("鄉民", r"(?:一名|幾名|那些)?鄉民[^，。]{0,14}(?:說|喊|叫|問|嘟囔|喃喃|開口|回答|附和)"),
        ("女人", r"(?:一個|一名|那個|旁邊的)?女人[^，。]{0,14}(?:說|喊|叫|問|嘟囔|喃喃|開口|回答|附和)"),
        ("男人", r"(?:一個|一名|那個|旁邊的)?男人[^，。]{0,14}(?:說|喊|叫|問|嘟囔|喃喃|開口|回答|附和)"),
        ("少年", r"(?:一個|一名|那個)?少年[^，。]{0,14}(?:說|喊|叫|問|嘟囔|喃喃|開口|回答|附和)"),
        ("老婦人", r"(?:一個|一名|那個)?老婦人[^，。]{0,14}(?:說|喊|叫|問|嘟囔|喃喃|開口|回答|附和)"),
    ]
    for label, pat in pats:
        if re.search(pat, text):
            return label
    return None


def explicit_speaker(context: str) -> str | None:
    # Strong forms such as「說話的是絹秀」「X回答道」.
    m = re.search(r"說話的(?:人|聲音主人)?是(?:個[^，。]{0,10})?([\u4e00-\u9fff]{1,8})", context)
    if m:
        for alias, canon in sorted(ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
            if alias in m.group(0):
                return canon

    candidates = []
    for alias, canon in sorted(ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
        for mo in re.finditer(re.escape(alias), context):
            tail = context[mo.end():mo.end() + 32]
            # Avoid "聽到X說" style cases where X is inside another character's perception only if
            # there is no direct speech cue immediately attached to X.
            cue_pos = min((tail.find(c) for c in SPEECH_CUES if c in tail), default=-1)
            if 0 <= cue_pos <= 18:
                candidates.append((mo.start(), canon))
    if candidates:
        return candidates[-1][1]
    return generic_from_narration(context)


def body_state_for(volume: int, lines: list[str]) -> list[str]:
    state = "normal"
    out = []
    for line in lines:
        if volume == 2:
            if not out:
                state = "swapped"
            if "恢複了原本的模樣" in line or "恢復了原本的模樣" in line:
                state = "normal"
            if "【尾聲】" in line:
                state = "swapped"
            if "【特別篇 弓箭比賽】" in line or "【附錄 俱理須益的回憶】" in line:
                state = "normal"
        elif volume == 3:
            if not out:
                state = "normal"
            # The accidental swap occurs immediately before this explicit description.
            if "本該釋放出攻擊性火焰的「朱慧月」" in line or "看來我們又替換了" in line:
                state = "swapped"
            # The published third volume ends its main story while the swap is still active.
            # Stand-alone post-story SS reset unless the SS explicitly states Reirin is visiting after swapping.
            if "【特典SS 雖然只是悄悄流傳的傳聞】" in line or "【特典SS 因為想靠近】" in line:
                state = "normal"
            if "【特典SS 怪談】" in line:
                state = "swapped"
        out.append(state)
    return out


def render_label(speaker: str, state: str) -> str:
    if speaker == "玲琳" and state == "swapped":
        return "玲琳（身體：朱慧月）"
    if speaker == "慧月" and state == "swapped":
        return "慧月（身體：黃玲琳）"
    return speaker


def scene_ids(lines: list[str]) -> list[int]:
    sid = 0
    ids = []
    for line in lines:
        if HEADING_RE.match(line.strip()) or line.strip() == "＊＊＊":
            sid += 1
        ids.append(sid)
    return ids


def nearest_context(lines: list[str], i: int, before: int, after: int) -> str:
    lo = max(0, i - before)
    hi = min(len(lines), i + after + 1)
    return "\n".join(lines[lo:hi])


def strong_pass(lines: list[str], scenes: list[int]) -> dict[int, str]:
    assigned: dict[int, str] = {}
    for i, raw in enumerate(lines):
        line = strip_existing_label(raw)
        if not QUOTE_RE.match(line):
            continue

        # 1) Same-line tail after closing quote.
        close = max(line.rfind("」"), line.rfind("』"))
        if close >= 0 and close + 1 < len(line):
            sp = explicit_speaker(line[close + 1:])
            if sp:
                assigned[i] = sp
                continue

        # 2) Immediately following narration is most reliable in Chinese/Japanese translated prose.
        for j in (i + 1, i + 2):
            if j >= len(lines) or scenes[j] != scenes[i]:
                continue
            if QUOTE_RE.match(strip_existing_label(lines[j])):
                break
            sp = explicit_speaker(lines[j])
            if sp:
                assigned[i] = sp
                break
        if i in assigned:
            continue

        # 3) Immediately preceding narration.
        for j in (i - 1, i - 2):
            if j < 0 or scenes[j] != scenes[i]:
                continue
            if QUOTE_RE.match(strip_existing_label(lines[j])):
                break
            sp = explicit_speaker(lines[j])
            if sp:
                assigned[i] = sp
                break
    return assigned


def dialogue_groups(lines: list[str], scenes: list[int]) -> list[list[int]]:
    q = [i for i, line in enumerate(lines) if QUOTE_RE.match(strip_existing_label(line))]
    groups: list[list[int]] = []
    cur: list[int] = []
    for i in q:
        if not cur:
            cur = [i]
            continue
        prev = cur[-1]
        # A group may contain short narration between turns, but not a scene transition or a long prose passage.
        gap = i - prev
        if scenes[i] == scenes[prev] and gap <= 5:
            cur.append(i)
        else:
            groups.append(cur)
            cur = [i]
    if cur:
        groups.append(cur)
    return groups


def local_candidates(lines: list[str], group: list[int], scenes: list[int]) -> list[str]:
    lo = max(0, group[0] - 5)
    hi = min(len(lines), group[-1] + 6)
    text = "\n".join(lines[lo:hi])
    c = names_in(text)
    # Remove characters that are merely being addressed/mentioned in quoted dialogue when there is no narrative mention.
    narrative_text = "\n".join(lines[j] for j in range(lo, hi) if not QUOTE_RE.match(strip_existing_label(lines[j])))
    narrative_names = set(names_in(narrative_text))
    if narrative_names:
        c = [x for x in c if x in narrative_names]
    return c


def fill_groups(lines: list[str], scenes: list[int], assigned: dict[int, str]) -> None:
    for group in dialogue_groups(lines, scenes):
        anchors = [(pos, assigned[pos]) for pos in group if pos in assigned]
        candidates = local_candidates(lines, group, scenes)
        anchored_names = []
        for _, s in anchors:
            if s not in GENERIC and s not in anchored_names:
                anchored_names.append(s)
        for s in anchored_names:
            if s not in candidates:
                candidates.append(s)

        # Stable two-person conversation: fill by parity from each anchor, but never override explicit anchors.
        if len(candidates) == 2 and anchors:
            a, b = candidates
            for anchor_pos, anchor_sp in anchors:
                if anchor_sp not in (a, b):
                    continue
                anchor_idx = group.index(anchor_pos)
                for k, line_no in enumerate(group):
                    if line_no in assigned:
                        continue
                    expected = anchor_sp if (k - anchor_idx) % 2 == 0 else (b if anchor_sp == a else a)
                    assigned[line_no] = expected
            continue

        # No explicit anchor, but exactly two narratively present participants: use the nearest named narration
        # to seed the first turn, then alternate.  If no seed exists, abstain.
        if len(candidates) == 2 and not anchors:
            first = group[0]
            seed = None
            for j in range(first - 1, max(-1, first - 5), -1):
                if j < 0 or scenes[j] != scenes[first]:
                    break
                ns = names_in(lines[j])
                if len(ns) == 1 and ns[0] in candidates:
                    seed = ns[0]
                    break
            if seed:
                a, b = candidates
                for k, line_no in enumerate(group):
                    assigned[line_no] = seed if k % 2 == 0 else (b if seed == a else a)
            continue

        # Multi-party groups: only fill a quote if the local +/-2-line narration names exactly one candidate.
        for line_no in group:
            if line_no in assigned:
                continue
            ctx = nearest_context(lines, line_no, 2, 2)
            narr = "\n".join(x for x in ctx.splitlines() if not QUOTE_RE.match(strip_existing_label(x)))
            ns = [x for x in names_in(narr) if not candidates or x in candidates]
            if len(set(ns)) == 1:
                assigned[line_no] = ns[0]


def second_pass(lines: list[str], scenes: list[int], assigned: dict[int, str]) -> None:
    # Dialogue continuity with strict guardrails.  Only use recent *known* speakers in the same scene.
    recent_by_scene: dict[int, deque[str]] = {}
    last_quote_by_scene: dict[int, int] = {}
    for i, raw in enumerate(lines):
        if not QUOTE_RE.match(strip_existing_label(raw)):
            continue
        sid = scenes[i]
        recent = recent_by_scene.setdefault(sid, deque(maxlen=6))
        if i in assigned:
            if assigned[i] not in GENERIC:
                recent.append(assigned[i])
            last_quote_by_scene[sid] = i
            continue

        prev_q = last_quote_by_scene.get(sid)
        if prev_q is None or i - prev_q > 4:
            last_quote_by_scene[sid] = i
            continue

        uniq = []
        for s in recent:
            if s not in uniq:
                uniq.append(s)
        if len(uniq) == 2 and recent:
            last = recent[-1]
            assigned[i] = uniq[1] if last == uniq[0] else uniq[0]
            recent.append(assigned[i])
        last_quote_by_scene[sid] = i


def annotate(volume: int, src: Path, dst: Path) -> tuple[int, int]:
    raw_lines = src.read_text(encoding="utf-8-sig").splitlines()
    lines = [strip_existing_label(x) for x in raw_lines]
    scenes = scene_ids(lines)
    states = body_state_for(volume, lines)

    assigned = strong_pass(lines, scenes)
    fill_groups(lines, scenes, assigned)
    second_pass(lines, scenes, assigned)

    out = [
        "《惡女不才，請多關照！～雛宮蝶鼠換身傳～》",
        f"第{volume}卷 Speaker 重校版",
        "依 character_data/speaker_attribution_guidelines.md 與第一卷人工完整修正版進行 scene-aware speaker attribution。",
        "原始小說文字保留；僅直接台詞加上 speaker。旁白不加 speaker。",
        "換身時依人格標註：玲琳（身體：朱慧月）／慧月（身體：黃玲琳）；時間或身體狀態切換時重新判定。",
        "低信心處保留【speaker 不確定】，不以錯誤 conversation state 強行向後傳播。",
        "",
    ]

    total = unknown = 0
    for i, line in enumerate(lines):
        if QUOTE_RE.match(line):
            total += 1
            speaker = assigned.get(i)
            if speaker:
                out.append(f"{render_label(speaker, states[i])}: {line}")
            else:
                unknown += 1
                out.append(f"【speaker 不確定】: {line}")
        else:
            out.append(line)

    dst.write_text("\n".join(out) + "\n", encoding="utf-8")
    return total, unknown


def main() -> None:
    print("Gold reference:", GOLD)
    print("Gold speaker labels:", ", ".join(gold_speakers()))
    for volume, (src, dst) in VOLUMES.items():
        total, unknown = annotate(volume, src, dst)
        print(f"Vol{volume}: {total} dialogue lines, {unknown} abstained -> {dst}")


if __name__ == "__main__":
    main()
