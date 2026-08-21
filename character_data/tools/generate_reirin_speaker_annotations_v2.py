from __future__ import annotations

import re
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOVEL_DIR = ROOT / "character_data" / "Reirin" / "sources" / "raw" / "novel"
REPORT = ROOT / "character_data" / "Reirin" / "speaker_attribution_validation.md"

RAW = {
    1: NOVEL_DIR / "惡女不才，請多關照！～雛宮蝶鼠換身傳～ [第一卷] [中村颯希].txt",
    2: NOVEL_DIR / "惡女不才，請多關照！～雛宮蝶鼠換身傳～ [第二卷] [中村颯希].txt",
    3: NOVEL_DIR / "惡女不才，請多關照！～雛宮蝶鼠換身傳～ [第三卷] [中村颯希].txt",
}
OUT = {
    2: NOVEL_DIR / "惡女不才_第二卷_speaker重校.md",
    3: NOVEL_DIR / "惡女不才_第三卷_speaker重校.md",
}
GOLD = NOVEL_DIR / "惡女不才_第一卷_speaker重校.md"

ALIASES = {
    "黃玲琳": "玲琳", "玲琳": "玲琳",
    "朱慧月": "慧月", "慧月": "慧月",
    "冬雪": "冬雪", "莉莉": "莉莉",
    "皇太子堯明": "堯明", "堯明": "堯明", "皇太子": "堯明",
    "鷲官長辰宇": "辰宇", "辰宇": "辰宇", "鷲官長": "辰宇",
    "皇后絹秀": "絹秀", "黃絹秀": "絹秀", "絹秀": "絹秀", "皇后": "絹秀",
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
    "泰龍": "泰龍", "俱理須益": "俱理須益",
}

GENDER = {
    "玲琳":"F","慧月":"F","冬雪":"F","莉莉":"F","絹秀":"F","雅媚":"F",
    "清佳":"F","芳春":"F","歌吹":"F","琥珀":"F","依依":"F","安安":"F","杏婆":"F",
    "堯明":"M","辰宇":"M","景行":"M","景彰":"M","文昴":"M","弦耀":"M",
    "雲嵐":"M","豪龍":"M","江德勝":"M","林熙":"M","泰龍":"M","俱理須益":"M",
}

GENERIC_PATTERNS = [
    ("女官", r"(?:一名|幾名|那些|旁邊的|身著[^，。！？]{0,12}的)?女官[^，。！？]{0,12}(?:說|喊|叫|問|回答|開口|附和|嘟囔|喃喃)"),
    ("鄉民", r"(?:一名|幾名|那些)?鄉民[^，。！？]{0,12}(?:說|喊|叫|問|回答|開口|附和|嘟囔|喃喃)"),
    ("邑民", r"(?:一名|幾名|那些)?邑民[^，。！？]{0,12}(?:說|喊|叫|問|回答|開口|附和|嘟囔|喃喃)"),
    ("女人", r"(?:一個|一名|那個|旁邊的)?女人[^，。！？]{0,12}(?:說|喊|叫|問|回答|開口|附和|嘟囔|喃喃)"),
    ("男人", r"(?:一個|一名|那個|旁邊的)?男人[^，。！？]{0,12}(?:說|喊|叫|問|回答|開口|附和|嘟囔|喃喃)"),
    ("少年", r"(?:一個|一名|那個)?少年[^，。！？]{0,12}(?:說|喊|叫|問|回答|開口|附和|嘟囔|喃喃)"),
]

CUES = r"說(?:道)?|問(?:道)?|回答|答道|回應|喊(?:道)?|叫(?:道)?|嘟囔|喃喃|呢喃|開口|反駁|補充|打斷|斥責|怒吼|宣告|附和|吐槽|感嘆|命令|催促|提醒|搭話|回嘴|應道"
QUOTE_RE = re.compile(r"^[\s　]*[「『]")
SCENE_RE = re.compile(r"^[\s　]*(?:▶︎▶︎【|【第|【序|【尾聲|【後記|【附錄|【特典SS|＊＊＊|\*\*\*)")


def strip_label(s: str) -> str:
    return re.sub(r"^[^:\n]{1,40}:\s*(?=[「『])", "", s)


def aliases_in(text: str) -> list[str]:
    out=[]
    masked=text
    for alias in sorted(ALIASES, key=len, reverse=True):
        if alias in masked:
            canon=ALIASES[alias]
            if canon not in out:
                out.append(canon)
            masked=masked.replace(alias, " "*len(alias))
    return out


def canonical_label(label: str) -> str:
    label=re.sub(r"（身體：[^）]+）", "", label).strip()
    return ALIASES.get(label, label)


def scene_ids(lines: list[str]) -> list[int]:
    sid=0; out=[]
    for s in lines:
        if SCENE_RE.match(s.strip()) or s.strip()=="＊＊＊":
            sid+=1
        out.append(sid)
    return out


def actor_at_start(text: str) -> str|None:
    t=text.strip()
    # Named grammatical subject near sentence start. Reject recipient markers such as 跟堯明/向堯明/對堯明.
    for alias in sorted(ALIASES, key=len, reverse=True):
        m=re.search(re.escape(alias), t[:28])
        if not m: continue
        prefix=t[max(0,m.start()-2):m.start()]
        if prefix.endswith(("跟","向","對","給","問","替","為","被")):
            continue
        if m.start() <= 10:
            return ALIASES[alias]
    return None


def strict_speech_subject(text: str) -> str|None:
    t=text.strip()
    # Strong copular attribution.
    for alias in sorted(ALIASES, key=len, reverse=True):
        if re.search(rf"(?:說話的|聲音的主人|發出[^，。！？]{{0,8}}聲音的)(?:人)?是[^，。！？]{{0,10}}{re.escape(alias)}", t):
            return ALIASES[alias]
    # Name must function as subject of a speech verb, not recipient/object.
    hits=[]
    for alias in sorted(ALIASES, key=len, reverse=True):
        for m in re.finditer(re.escape(alias), t):
            prefix=t[max(0,m.start()-3):m.start()]
            if prefix.endswith(("跟","向","對","給","問","替","為","被","看著","望著")):
                continue
            tail=t[m.end():m.end()+24]
            cm=re.search(rf"^[^，。！？；:]{{0,10}}(?:{CUES})", tail)
            if cm:
                hits.append((m.start(),ALIASES[alias]))
    if hits:
        return hits[-1][1]
    for label,pat in GENERIC_PATTERNS:
        if re.search(pat,t): return label
    return None


def previous_named_subject(lines:list[str], i:int, scenes:list[int], gender:str|None=None, limit:int=4)->str|None:
    for j in range(i-1,max(-1,i-limit-1),-1):
        if j<0 or scenes[j]!=scenes[i] or QUOTE_RE.match(strip_label(lines[j])): continue
        a=actor_at_start(lines[j])
        if a and (gender is None or GENDER.get(a)==gender):
            return a
    return None


def explicit_pass(lines:list[str], scenes:list[int])->dict[int,str]:
    out={}
    for i,raw in enumerate(lines):
        line=strip_label(raw)
        if not QUOTE_RE.match(line): continue
        close=max(line.rfind("」"),line.rfind("』"))
        if close>=0 and close+1<len(line):
            sp=strict_speech_subject(line[close+1:])
            if sp: out[i]=sp; continue

        # Next line only: either a clear speech subject or an immediately described named actor.
        if i+1<len(lines) and scenes[i+1]==scenes[i] and not QUOTE_RE.match(strip_label(lines[i+1])):
            nxt=lines[i+1]
            sp=strict_speech_subject(nxt)
            if not sp:
                sp=actor_at_start(nxt)
            if sp:
                out[i]=sp; continue
            # Pronoun + explicit speech/action cue: resolve only to a nearby same-gender named subject.
            st=nxt.strip()
            if re.match(r"^(她|他)[^，。！？]{0,16}(?:"+CUES+r"|皺|笑|點|搖|抬|低|轉|伸|握|嘆)",st):
                g="F" if st.startswith("她") else "M"
                sp=previous_named_subject(lines,i,scenes,g,3)
                if sp: out[i]=sp; continue

        # Preceding line: require explicit speech cue or colon-like setup; do not accept mere mention.
        if i>0 and scenes[i-1]==scenes[i] and not QUOTE_RE.match(strip_label(lines[i-1])):
            prv=lines[i-1]
            sp=strict_speech_subject(prv)
            if sp:
                out[i]=sp; continue
            if prv.rstrip().endswith(("：",":")):
                sp=actor_at_start(prv)
                if sp: out[i]=sp; continue
    return out


def quote_groups(lines:list[str], scenes:list[int])->list[list[int]]:
    qs=[i for i,s in enumerate(lines) if QUOTE_RE.match(strip_label(s))]
    groups=[]; cur=[]
    for i in qs:
        if not cur: cur=[i]; continue
        p=cur[-1]
        if scenes[i]==scenes[p] and i-p<=4:
            cur.append(i)
        else:
            groups.append(cur); cur=[i]
    if cur: groups.append(cur)
    return groups


def candidate_narrative_names(lines:list[str], group:list[int])->list[str]:
    lo=max(0,group[0]-4); hi=min(len(lines),group[-1]+5)
    found=[]
    for j in range(lo,hi):
        if QUOTE_RE.match(strip_label(lines[j])): continue
        for n in aliases_in(lines[j]):
            if n not in found: found.append(n)
    return found


def fill_safe_alternation(lines:list[str], scenes:list[int], assigned:dict[int,str])->None:
    for g in quote_groups(lines,scenes):
        anchors=[(k,assigned[q]) for k,q in enumerate(g) if q in assigned and assigned[q] not in {"女官","鄉民","邑民","女人","男人","少年"}]
        if not anchors: continue
        names=[]
        for _,s in anchors:
            if s not in names: names.append(s)
        narr=candidate_narrative_names(lines,g)
        # Only fill when exactly two plausible conversational participants exist.
        cands=[]
        for s in names+narr:
            if s not in cands: cands.append(s)
        if len(cands)!=2: continue
        a,b=cands
        # All anchors must agree with one alternating parity pattern.
        valid=[]
        for first in (a,b):
            ok=True
            for k,s in anchors:
                expected=first if k%2==0 else (b if first==a else a)
                if s!=expected: ok=False; break
            if ok: valid.append(first)
        if len(valid)!=1: continue
        first=valid[0]
        for k,q in enumerate(g):
            if q not in assigned:
                assigned[q]=first if k%2==0 else (b if first==a else a)


def body_states(volume:int, lines:list[str])->list[str]:
    state="swapped" if volume==2 else "normal"
    out=[]
    for s in lines:
        if volume==2:
            if "恢複了原本的模樣" in s or "恢復了原本的模樣" in s:
                state="normal"
            if "【尾聲】" in s:
                state="swapped"
            if "【特別篇 弓箭比賽】" in s or "【附錄 俱理須益的回憶】" in s:
                state="normal"
        elif volume==3:
            if "本該釋放出攻擊性火焰的「朱慧月」" in s or "看來我們又替換了" in s:
                state="swapped"
            if "【特典SS 雖然只是悄悄流傳的傳聞】" in s or "【特典SS 因為想靠近】" in s:
                state="normal"
            if "【特典SS 怪談】" in s:
                state="swapped"
        out.append(state)
    return out


def render(sp:str,state:str)->str:
    if state=="swapped" and sp=="玲琳": return "玲琳（身體：朱慧月）"
    if state=="swapped" and sp=="慧月": return "慧月（身體：黃玲琳）"
    return sp


def predict(lines:list[str], volume:int)->tuple[dict[int,str],list[int],list[str],list[int]]:
    scenes=scene_ids(lines)
    assigned=explicit_pass(lines,scenes)
    fill_safe_alternation(lines,scenes,assigned)
    qs=[i for i,s in enumerate(lines) if QUOTE_RE.match(strip_label(s))]
    return assigned,qs,body_states(volume,lines),scenes


def parse_gold()->list[tuple[str,str]]:
    out=[]
    for s in GOLD.read_text(encoding="utf-8").splitlines():
        m=re.match(r"^([^:\n]{1,40}):\s*([「『].*)$",s)
        if m:
            out.append((canonical_label(m.group(1)),m.group(2)))
    return out


def validate()->tuple[float,float,int,int,list[str]]:
    lines=RAW[1].read_text(encoding="utf-8-sig").splitlines()
    assigned,qs,_,_=predict(lines,1)
    raw_quotes=[strip_label(lines[i]) for i in qs]
    gold=parse_gold()
    # Sequential quote alignment; both files preserve source quote order.
    gidx=0; correct=wrong=covered=0; examples=[]
    for qi,qtext in zip(qs,raw_quotes):
        while gidx<len(gold) and gold[gidx][1]!=qtext:
            gidx+=1
        if gidx>=len(gold): break
        gsp,_=gold[gidx]; gidx+=1
        p=assigned.get(qi)
        if not p: continue
        covered+=1
        if canonical_label(p)==gsp:
            correct+=1
        else:
            wrong+=1
            if len(examples)<20:
                examples.append(f"- predicted `{p}`, gold `{gsp}`: `{qtext[:70]}`")
    precision=correct/covered if covered else 0.0
    coverage=covered/len(raw_quotes) if raw_quotes else 0.0
    return precision,coverage,correct,wrong,examples


def write_volume(volume:int)->tuple[int,int]:
    lines=RAW[volume].read_text(encoding="utf-8-sig").splitlines()
    assigned,qs,states,_=predict(lines,volume)
    header=[
        "《惡女不才，請多關照！～雛宮蝶鼠換身傳～》",
        f"第{volume}卷 Speaker 重校版（scene-aware v2）",
        "依 character_data/speaker_attribution_guidelines.md 與第一卷人工完整修正版進行高精度 speaker attribution。",
        "原始小說文字保留；僅直接台詞加 speaker。旁白不加 speaker。",
        "換身時依人格標註：玲琳（身體：朱慧月）／慧月（身體：黃玲琳）。",
        "無充分證據時保留【speaker 不確定】，不讓不確定狀態向後傳播。",
        "",
    ]
    out=header[:]; unknown=0
    for i,s in enumerate(lines):
        if QUOTE_RE.match(strip_label(s)):
            sp=assigned.get(i)
            if sp:
                out.append(f"{render(sp,states[i])}: {strip_label(s)}")
            else:
                unknown+=1
                out.append(f"【speaker 不確定】: {strip_label(s)}")
        else:
            out.append(s)
    OUT[volume].write_text("\n".join(out)+"\n",encoding="utf-8")
    return len(qs),unknown


def main():
    precision,coverage,correct,wrong,examples=validate()
    stats=[]
    for v in (2,3):
        stats.append((v,*write_volume(v)))
    report=[
        "# Reirin Speaker Attribution Validation",
        "",
        "The manually corrected Volume 1 is used as a gold reference for validating the conservative scene-aware rules before generating Volume 2 and 3.",
        "",
        f"- Volume 1 non-abstained precision: **{precision:.2%}**",
        f"- Volume 1 automatic coverage: **{coverage:.2%}**",
        f"- Correct labelled quotes: **{correct}**",
        f"- Wrong labelled quotes: **{wrong}**",
        "",
        "## Generated volumes",
        "",
    ]
    for v,total,unknown in stats:
        report.append(f"- Volume {v}: {total} quote lines; {unknown} left as `speaker 不確定` ({unknown/total:.2%}).")
    report += ["", "## First validation errors", ""] + (examples or ["- None in aligned evaluated quotes."])
    report += ["", "The objective is precision-first attribution. Unknown labels are preferred to unsupported speaker assignments.", ""]
    REPORT.write_text("\n".join(report),encoding="utf-8")
    print("\n".join(report[:12]))

if __name__=="__main__":
    main()
