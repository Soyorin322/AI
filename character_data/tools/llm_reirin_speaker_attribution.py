from __future__ import annotations

import json
import os
import re
from collections import defaultdict, deque
from pathlib import Path

from huggingface_hub import hf_hub_download
from llama_cpp import Llama

ROOT = Path(__file__).resolve().parents[2]
NOVEL = ROOT / "character_data" / "Reirin" / "sources" / "raw" / "novel"
GOLD = NOVEL / "惡女不才_第一卷_speaker重校.md"
REPORT = ROOT / "character_data" / "Reirin" / "speaker_attribution_llm_validation.md"

RAW = {
    1: NOVEL / "惡女不才，請多關照！～雛宮蝶鼠換身傳～ [第一卷] [中村颯希].txt",
    2: NOVEL / "惡女不才，請多關照！～雛宮蝶鼠換身傳～ [第二卷] [中村颯希].txt",
    3: NOVEL / "惡女不才，請多關照！～雛宮蝶鼠換身傳～ [第三卷] [中村颯希].txt",
}
OUT = {
    2: NOVEL / "惡女不才_第二卷_speaker重校.md",
    3: NOVEL / "惡女不才_第三卷_speaker重校.md",
}

ALIASES = {
    "黃玲琳":"玲琳","玲琳":"玲琳","朱慧月":"慧月","慧月":"慧月",
    "冬雪":"冬雪","莉莉":"莉莉","堯明":"堯明","皇太子":"堯明",
    "辰宇":"辰宇","鷲官長":"辰宇","絹秀":"絹秀","黃絹秀":"絹秀","皇后":"絹秀",
    "雅媚":"雅媚","朱雅媚":"雅媚","朱貴妃":"雅媚","清佳":"清佳","金清佳":"清佳",
    "芳春":"芳春","藍芳春":"芳春","歌吹":"歌吹","玄歌吹":"歌吹",
    "景行":"景行","黃景行":"景行","景彰":"景彰","黃景彰":"景彰",
    "文昴":"文昴","弦耀":"弦耀","琥珀":"琥珀","依依":"依依","安安":"安安",
    "雲嵐":"雲嵐","豪龍":"豪龍","杏婆":"杏婆","江德勝":"江德勝","江氏":"江德勝",
    "林熙":"林熙","藍林熙":"林熙","泰龍":"泰龍","俱理須益":"俱理須益",
    "女官":"女官","藤黃":"藤黃女官","銀硃":"銀硃女官","鄉民":"鄉民","邑民":"邑民",
    "女人":"女人","男人":"男人","少年":"少年","老婦人":"老婦人","侍童":"侍童","護衛":"護衛",
}
CANONICAL = set(ALIASES.values()) | {"unknown"}
QUOTE_RE = re.compile(r"^[\s　]*[「『]")
SCENE_RE = re.compile(r"^[\s　]*(?:▶︎▶︎【|【第|【序|【尾聲|【後記|【附錄|【特典SS|＊＊＊|\*\*\*)")


def norm_quote(s: str) -> str:
    s=re.sub(r"^[^:\n]{1,50}:\s*(?=[「『])","",s.strip())
    return re.sub(r"\s+","",s)


def canon(s: str) -> str:
    s=s.strip().strip("`*'\" ")
    s=re.sub(r"（身體：[^）]+）","",s)
    if s in ALIASES: return ALIASES[s]
    for a,c in sorted(ALIASES.items(), key=lambda x:len(x[0]), reverse=True):
        if a in s and len(s)<=len(a)+8: return c
    if any(x in s.lower() for x in ("unknown","不確定","無法判斷","未知")): return "unknown"
    return s if s in CANONICAL else "unknown"


def gold_queue():
    q=defaultdict(deque)
    for line in GOLD.read_text(encoding="utf-8").splitlines():
        m=re.match(r"^([^:\n]{1,50}):\s*([「『].*)$", line)
        if m:
            q[norm_quote(m.group(2))].append(canon(m.group(1)))
    return q


def body_states(volume:int, lines:list[str])->list[str]:
    state="swapped" if volume==2 else "normal"
    out=[]
    for s in lines:
        if volume==2:
            if "恢複了原本的模樣" in s or "恢復了原本的模樣" in s: state="normal"
            if "【尾聲】" in s: state="swapped"
            if "【特別篇 弓箭比賽】" in s or "【附錄 俱理須益的回憶】" in s: state="normal"
        elif volume==3:
            if "本該釋放出攻擊性火焰的「朱慧月」" in s or "看來我們又替換了" in s: state="swapped"
            if "【特典SS 雖然只是悄悄流傳的傳聞】" in s or "【特典SS 因為想靠近】" in s: state="normal"
            if "【特典SS 怪談】" in s: state="swapped"
        out.append(state)
    return out


def render(speaker:str,state:str)->str:
    if speaker=="玲琳" and state=="swapped": return "玲琳（身體：朱慧月）"
    if speaker=="慧月" and state=="swapped": return "慧月（身體：黃玲琳）"
    return speaker


def scenes(lines:list[str])->list[tuple[int,int]]:
    starts=[0]
    for i,s in enumerate(lines):
        if i and (SCENE_RE.match(s.strip()) or s.strip()=="＊＊＊"):
            starts.append(i)
    starts.append(len(lines))
    return [(starts[i],starts[i+1]) for i in range(len(starts)-1)]


def candidate_names(text:str)->list[str]:
    found=[]
    masked=text
    for a,c in sorted(ALIASES.items(), key=lambda x:len(x[0]), reverse=True):
        if a in masked and c not in found:
            found.append(c)
            masked=masked.replace(a," "*len(a))
    # Always permit the two body-swap protagonists and anonymous classes only if present in context.
    for x in ("玲琳","慧月"):
        if x not in found: found.append(x)
    return found


def build_windows(lines:list[str], max_core:int=72, context:int=12):
    windows=[]
    for ss,se in scenes(lines):
        p=ss
        while p<se:
            core_end=min(se,p+max_core)
            # Avoid cutting immediately before a direct quote when possible.
            while core_end<se and core_end-p<max_core+10 and QUOTE_RE.match(lines[core_end].lstrip()):
                core_end+=1
            lo=max(ss,p-context); hi=min(se,core_end+context)
            targets=[i for i in range(p,core_end) if QUOTE_RE.match(lines[i])]
            if targets: windows.append((lo,hi,targets))
            p=core_end
    return windows


def ask_model(llm:Llama, lines:list[str], lo:int, hi:int, targets:list[int])->dict[int,str]:
    id_by_line={line_no:n for n,line_no in enumerate(targets)}
    shown=[]
    for i in range(lo,hi):
        prefix=f"[Q{id_by_line[i]}] " if i in id_by_line else ""
        shown.append(prefix+lines[i])
    text="\n".join(shown)
    cands=candidate_names(text)
    prompt=f"""你正在做中文小說 speaker attribution。請判斷下列每個 [Qn] 直接台詞是誰說的。

規則：
1. 先理解整個場景與對話輪替，不要逐句盲猜。
2. 敘事中的「X說／回答／問／喊／嘟囔」、人物動作、受話者與前後輪替是主要證據。
3. 不要把旁白中被談論的人誤當 speaker，例如「跟堯明訴說」的 speaker 不是堯明。
4. 這部作品只有玲琳和慧月會交換身體。speaker 要標真正的人格，不要依外表／身體判斷。此步只輸出「玲琳」或「慧月」，身體標籤由後處理加入。
5. 回憶、夢境、炎術傳話等要依該段真正發聲者判斷。
6. 群眾若只能確定類別，可用「女官」「鄉民」「邑民」「女人」「男人」「少年」等；若真的無法可靠判斷才輸出 unknown。
7. 不要用角色個性作唯一證據。
8. 每個 Q 必須恰好輸出一次。

本段可見候選人物／類別：{', '.join(cands)}

只回傳 JSON，不要解釋：
{{"labels":[{{"id":0,"speaker":"角色名"}}, ...]}}

文本：
{text}
/no_think"""
    result=llm.create_chat_completion(
        messages=[
            {"role":"system","content":"你是高精度小說對話說話者標註器。只依文本證據輸出 JSON。"},
            {"role":"user","content":prompt},
        ],
        temperature=0.0,
        max_tokens=max(256,len(targets)*18),
        response_format={"type":"json_object"},
    )
    content=result["choices"][0]["message"]["content"]
    try:
        obj=json.loads(content)
    except Exception:
        m=re.search(r"\{.*\}",content,re.S)
        obj=json.loads(m.group(0)) if m else {"labels":[]}
    labels={}
    for item in obj.get("labels",[]):
        try: qid=int(item.get("id"))
        except Exception: continue
        if 0<=qid<len(targets): labels[targets[qid]]=canon(str(item.get("speaker","unknown")))
    for line_no in targets: labels.setdefault(line_no,"unknown")
    return labels


def annotate(llm:Llama, volume:int)->tuple[list[str],dict[int,str]]:
    lines=RAW[volume].read_text(encoding="utf-8-sig").splitlines()
    labels={}
    wins=build_windows(lines)
    print(f"Volume {volume}: {len(wins)} context windows")
    for k,(lo,hi,targets) in enumerate(wins,1):
        labels.update(ask_model(llm,lines,lo,hi,targets))
        if k%10==0: print(f"  {k}/{len(wins)}")
    return lines,labels


def validate_volume1(lines:list[str],labels:dict[int,str]):
    gq=gold_queue(); correct=wrong=unknown=matched=0; errors=[]
    for i,s in enumerate(lines):
        if not QUOTE_RE.match(s): continue
        key=norm_quote(s)
        if not gq[key]: continue
        gold=gq[key].popleft(); pred=labels.get(i,"unknown")
        matched+=1
        if pred=="unknown": unknown+=1
        elif pred==gold: correct+=1
        else:
            wrong+=1
            if len(errors)<30: errors.append((i+1,pred,gold,s[:100]))
    known=correct+wrong
    precision=correct/known if known else 0
    coverage=known/matched if matched else 0
    return precision,coverage,matched,correct,wrong,unknown,errors


def write_output(volume:int,lines:list[str],labels:dict[int,str]):
    states=body_states(volume,lines)
    out=[
        "《惡女不才，請多關照！～雛宮蝶鼠換身傳～》",
        f"第{volume}卷 Speaker 重校版（context-model + scene-aware）",
        "依 character_data/speaker_attribution_guidelines.md，並以第一卷人工完整修正版作 gold validation。",
        "原始小說文字保留；僅直接台詞加入 speaker。旁白不加入 speaker。",
        "換身期間依人格標註並另顯示身體：玲琳（身體：朱慧月）／慧月（身體：黃玲琳）。",
        "",
    ]
    unknown=0; total=0
    for i,s in enumerate(lines):
        if QUOTE_RE.match(s):
            total+=1; sp=labels.get(i,"unknown")
            if sp=="unknown": unknown+=1; out.append(f"【speaker 不確定】: {s}")
            else: out.append(f"{render(sp,states[i])}: {s}")
        else: out.append(s)
    OUT[volume].write_text("\n".join(out)+"\n",encoding="utf-8")
    return total,unknown


def main():
    repo=os.environ.get("QWEN_REPO","ggml-org/Qwen3-4B-GGUF")
    filename=os.environ.get("QWEN_FILE","Qwen3-4B-Q4_K_M.gguf")
    model=hf_hub_download(repo_id=repo,filename=filename)
    llm=Llama(model_path=model,n_ctx=8192,n_threads=max(2,os.cpu_count() or 4),n_batch=1024,verbose=False)

    v1_lines,v1_labels=annotate(llm,1)
    precision,coverage,matched,correct,wrong,unknown,errors=validate_volume1(v1_lines,v1_labels)
    print(f"Gold validation: precision={precision:.3%}, coverage={coverage:.3%}, matched={matched}, wrong={wrong}")

    report=[
        "# Reirin Speaker Attribution — Context Model Validation",
        "",
        f"Model: `{repo}` / `{filename}`",
        "",
        "Volume 1 is the user-corrected gold reference.",
        "",
        f"- Gold quotes matched: **{matched}**",
        f"- Non-unknown precision: **{precision:.2%}**",
        f"- Automatic coverage: **{coverage:.2%}**",
        f"- Correct: **{correct}**",
        f"- Wrong: **{wrong}**",
        f"- Unknown: **{unknown}**",
        "",
        "## First errors",
        "",
    ]
    report += [f"- raw line {ln}: predicted `{p}`, gold `{g}` — `{q}`" for ln,p,g,q in errors] or ["- None"]

    # Do not overwrite Volume 2/3 unless the model substantially exceeds the failed heuristic baseline.
    if precision < 0.90 or coverage < 0.75:
        report += ["", "**Generation aborted:** validation threshold not met; existing Volume 2/3 files were not replaced.", ""]
        REPORT.write_text("\n".join(report),encoding="utf-8")
        raise SystemExit(2)

    stats=[]
    for v in (2,3):
        lines,labels=annotate(llm,v)
        stats.append((v,*write_output(v,lines,labels)))
    report += ["", "## Generated volumes", ""]
    for v,total,u in stats:
        report.append(f"- Volume {v}: {total} quotes; {u} unknown ({u/total:.2%}).")
    report.append("")
    REPORT.write_text("\n".join(report),encoding="utf-8")

if __name__=="__main__":
    main()
