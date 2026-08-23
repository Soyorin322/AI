from __future__ import annotations

import json
import os
import re
from collections import defaultdict, deque
from pathlib import Path

from huggingface_hub import hf_hub_download
from llama_cpp import Llama

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "data_processing" / "text" / "Though I Am an Inept Villainess Tale of the Butterfly-Rat Body Swap in the Maiden Court"
PROCESSED = WORK / "processed"
GOLD = WORK / "惡女不才_volume3.md"

PARTS = {
    5: ["惡女不才_volume5_part1.md", "惡女不才_volume5_part2.md", "惡女不才_volume5_part3.md"],
    6: ["惡女不才_volume6_part1.md", "惡女不才_volume6_part2.md", "惡女不才_volume6_part3.md"],
    7: ["惡女不才_volume7_part1.md", "惡女不才_volume7_part2.md"],
    8: ["惡女不才_volume8_part1.md", "惡女不才_volume8_part2.md"],
    9: ["惡女不才_volume9_part1.md", "惡女不才_volume9_part2.md", "惡女不才_volume9_part3.md"],
}

ALIASES = {
    "黃玲琳":"玲琳","玲琳":"玲琳","朱慧月":"慧月","慧月":"慧月",
    "冬雪":"冬雪","莉莉":"莉莉","堯明":"堯明","皇太子":"堯明",
    "辰宇":"辰宇","鷲官長":"辰宇","絹秀":"絹秀","黃絹秀":"絹秀","皇后":"絹秀",
    "雅媚":"雅媚","朱雅媚":"雅媚","清佳":"清佳","金清佳":"清佳",
    "芳春":"芳春","藍芳春":"芳春","歌吹":"歌吹","玄歌吹":"歌吹",
    "景行":"景行","黃景行":"景行","景彰":"景彰","黃景彰":"景彰",
    "文昴":"文昴","弦耀":"弦耀","琥珀":"琥珀","依依":"依依","安安":"安安",
    "雲嵐":"雲嵐","豪龍":"豪龍","杏婆":"杏婆","江德勝":"江德勝","江氏":"江德勝",
    "林熙":"林熙","藍林熙":"林熙","泰龍":"泰龍","俱理須益":"俱理須益",
    "藤黃":"藤黃女官","銀硃":"銀硃女官","女官":"女官","侍女":"侍女",
    "鄉民":"鄉民","邑民":"邑民","百姓":"百姓","女人":"女人","男人":"男人",
    "少年":"少年","少女":"少女","老婦人":"老婦人","侍童":"侍童","護衛":"護衛",
    "武官":"武官","官吏":"官吏","眾人":"眾人","孩子":"孩子",
}

TARGET_RE = re.compile(r"^[\s　]*[「（]")
QUOTE_RE = re.compile(r"^[\s　]*「")
THOUGHT_RE = re.compile(r"^[\s　]*（.*）[\s　]*$")
PREFIX_RE = re.compile(r"^([^:\n]{1,80}):\s*(?=[「（])")
SCENE_RE = re.compile(r"^[\s　]*(?:# |▶︎▶︎【|【第|【序|【尾聲|【後記|【附錄|【特典|＊＊＊|\*\*\*)")
SPEECH_VERBS = "說|問|答|回答|喊|叫|嘟囔|低語|喃喃|開口|搭話|反駁|補充|宣布|命令|提醒|勸|抱怨|怒吼|叫嚷|說道|說著|問道|答道|回應|解釋|追問|斥責|笑道|感嘆"
THOUGHT_VERBS = "心想|暗想|想到|覺得|認為|意識到|在心裡|內心|默念|暗自|思忖|腦海"


def clean_label(s: str) -> str:
    s = s.strip().strip("`*'\" ")
    if s.startswith("【") and ("不確定" in s or "unknown" in s.lower()): return "unknown"
    s = re.sub(r"（身體：[^）]+）", "", s)
    for a,c in sorted(ALIASES.items(), key=lambda x:len(x[0]), reverse=True):
        if s == a or (a in s and len(s) <= len(a)+8): return c
    if s in set(ALIASES.values()): return s
    return "unknown"


def strip_prefix(line: str) -> str:
    return PREFIX_RE.sub("", line, count=1)


def candidate_names(text: str) -> list[str]:
    out=[]
    for a,c in sorted(ALIASES.items(), key=lambda x:len(x[0]), reverse=True):
        if a in text and c not in out: out.append(c)
    for x in ("玲琳","慧月"):
        if x not in out: out.append(x)
    return out[:24]


def nearest_explicit(lines: list[str], i: int, thought: bool=False) -> str | None:
    verbs = THOUGHT_VERBS if thought else SPEECH_VERBS
    # Strongest evidence: immediately adjacent narration naming a character + attribution verb.
    for j in (i-1, i+1, i+2, i-2):
        if not (0 <= j < len(lines)): continue
        s=strip_prefix(lines[j])
        for a,c in sorted(ALIASES.items(), key=lambda x:len(x[0]), reverse=True):
            if a in s and re.search(verbs, s): return c
    return None


def scene_bounds(lines:list[str]) -> list[tuple[int,int]]:
    starts=[0]
    for i,s in enumerate(lines):
        if i and (SCENE_RE.match(s.strip()) or s.strip()=="＊＊＊"): starts.append(i)
    starts.append(len(lines))
    return [(starts[k],starts[k+1]) for k in range(len(starts)-1)]


def build_windows(lines:list[str], core=56, ctx=14):
    result=[]
    for ss,se in scene_bounds(lines):
        p=ss
        while p<se:
            ce=min(se,p+core)
            targets=[i for i in range(p,ce) if TARGET_RE.match(strip_prefix(lines[i])) and "bilibili.com" not in lines[i] and "（插畫）" not in lines[i]]
            if targets: result.append((max(ss,p-ctx),min(se,ce+ctx),targets))
            p=ce
    return result


def ask(llm:Llama, lines:list[str], lo:int, hi:int, targets:list[int], pre:dict[int,str]) -> dict[int,str]:
    unresolved=[i for i in targets if pre.get(i,"unknown")=="unknown"]
    if not unresolved: return {}
    qid={idx:n for n,idx in enumerate(unresolved)}
    shown=[]
    for i in range(lo,hi):
        raw=strip_prefix(lines[i])
        if i in qid: shown.append(f"[Q{qid[i]}] {raw}")
        else: shown.append(raw)
    block="\n".join(shown)
    cands=candidate_names(block)
    prompt=f"""你是中文小說 speaker/thinker attribution 標註器。這部作品有身體交換，但此步只判斷真正的人格；body identity 之後再處理。

請判斷每個 [Qn]：
- 以「」開始：誰真正說了這句話。
- 以（）包圍：這是誰的內心話／心理想法。

必須遵守：
1. 只依文本證據：明示的『X說／問／回答／想』、前後動作、受話者、對話輪替、場景 POV。
2. 不能因角色個性或你對故事的印象強猜。
3. 轉述、回憶中引用、信件內容若不是當下角色直接發言，應依文本真正來源判斷；若只是在旁白中被引用而非獨立話語，可輸出 unknown。
4. 玲琳和慧月交換身體時仍以人格判斷：玲琳就是玲琳，慧月就是慧月。
5. 多人齊聲或群眾只能確定類別時，可用『女官／百姓／男人／女人／眾人』等。
6. 無充分證據必須輸出 unknown，不可補猜。
7. 每個 Q 恰好一次，只回 JSON。

可見候選：{', '.join(cands)}
格式：{{"labels":[{{"id":0,"speaker":"玲琳"}},{{"id":1,"speaker":"unknown"}}]}}

文本：
{block}
/no_think"""
    r=llm.create_chat_completion(
        messages=[{"role":"system","content":"只依小說文本證據做高精度 attribution，寧缺勿猜。"},{"role":"user","content":prompt}],
        temperature=0.0,max_tokens=max(256,len(unresolved)*18),response_format={"type":"json_object"},
    )
    content=r["choices"][0]["message"]["content"]
    try: obj=json.loads(content)
    except Exception:
        m=re.search(r"\{.*\}",content,re.S); obj=json.loads(m.group(0)) if m else {"labels":[]}
    out={}
    for item in obj.get("labels",[]):
        try: q=int(item["id"])
        except Exception: continue
        if 0<=q<len(unresolved): out[unresolved[q]]=clean_label(str(item.get("speaker","unknown")))
    for i in unresolved: out.setdefault(i,"unknown")
    return out


def annotate_file(llm:Llama,path:Path) -> tuple[list[str],dict[int,str]]:
    lines=path.read_text(encoding="utf-8-sig").splitlines()
    labels={}
    for i,s in enumerate(lines):
        raw=strip_prefix(s)
        if not TARGET_RE.match(raw) or "bilibili.com" in raw or raw.strip()=="（插畫）": continue
        thought=bool(THOUGHT_RE.match(raw))
        labels[i]=nearest_explicit(lines,i,thought) or "unknown"
    wins=build_windows(lines)
    for k,(lo,hi,targets) in enumerate(wins,1):
        labels.update(ask(llm,lines,lo,hi,targets,labels))
        if k%10==0: print(path.name,k,"/",len(wins),flush=True)
    return lines,labels


def gold_labels(path:Path):
    q=defaultdict(deque)
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        m=PREFIX_RE.match(line)
        if not m: continue
        raw=strip_prefix(line)
        if not TARGET_RE.match(raw): continue
        key=re.sub(r"\s+","",raw)
        q[key].append(clean_label(m.group(1)))
    return q


def validate_gold(llm:Llama):
    lines,labels=annotate_file(llm,GOLD)
    gold=gold_labels(GOLD)
    matched=correct=wrong=unknown=0
    errors=[]
    for i,line in enumerate(lines):
        raw=strip_prefix(line)
        key=re.sub(r"\s+","",raw)
        if not gold[key]: continue
        g=gold[key].popleft(); p=labels.get(i,"unknown")
        if g=="unknown": continue
        matched+=1
        if p=="unknown": unknown+=1
        elif p==g: correct+=1
        else:
            wrong+=1
            if len(errors)<30: errors.append((i+1,p,g,raw[:120]))
    known=correct+wrong
    precision=correct/known if known else 0
    coverage=known/matched if matched else 0
    return precision,coverage,matched,correct,wrong,unknown,errors


def detect_swap_labels(lines:list[str],labels:dict[int,str],llm:Llama) -> dict[int,str]:
    # Body identity is intentionally conservative. Ask only for protagonist targets, with local context.
    out={}
    protagonists=[i for i,s in labels.items() if s in ("玲琳","慧月")]
    for start in range(0,len(protagonists),40):
        ids=protagonists[start:start+40]
        if not ids: continue
        lo=max(0,min(ids)-25); hi=min(len(lines),max(ids)+26)
        numbered=[]
        qmap={idx:n for n,idx in enumerate(ids)}
        for i in range(lo,hi):
            raw=strip_prefix(lines[i])
            numbered.append((f"[Q{qmap[i]}] " if i in qmap else "")+raw)
        prompt="""判斷下列標成玲琳或慧月的人格，在該句發生時身體是否交換。只依文本。輸出每個 Q 的 body：normal 或 swapped。swapped 表示玲琳在朱慧月身體、慧月在黃玲琳身體。不確定輸出 unknown。只回 JSON：{\"states\":[{\"id\":0,\"body\":\"normal\"}]}\n\n"""+"\n".join(numbered)+"\n/no_think"
        r=llm.create_chat_completion(messages=[{"role":"system","content":"只依文本追蹤身體交換狀態。"},{"role":"user","content":prompt}],temperature=0,max_tokens=max(180,len(ids)*12),response_format={"type":"json_object"})
        try: obj=json.loads(r["choices"][0]["message"]["content"])
        except Exception: obj={"states":[]}
        for item in obj.get("states",[]):
            try:q=int(item["id"])
            except Exception:continue
            if 0<=q<len(ids): out[ids[q]]=str(item.get("body","unknown"))
    return out


def render(sp:str,state:str)->str:
    if sp=="unknown": return "【speaker 不確定】"
    if sp=="玲琳" and state=="swapped": return "玲琳（身體：朱慧月）"
    if sp=="慧月" and state=="swapped": return "慧月（身體：黃玲琳）"
    return sp


def write_output(volume:int,part_name:str,lines:list[str],labels:dict[int,str],states:dict[int,str]):
    out=[]; total=unknown=0
    for i,line in enumerate(lines):
        raw=strip_prefix(line)
        if i in labels:
            total+=1; sp=labels[i]
            if sp=="unknown": unknown+=1
            out.append(f"{render(sp,states.get(i,'normal'))}: {raw}")
        else: out.append(line)
    d=PROCESSED/f"volume_{volume:02d}"; d.mkdir(parents=True,exist_ok=True)
    target=d/part_name.replace(".md","_speaker標註.md")
    target.write_text("\n".join(out)+"\n",encoding="utf-8")
    return target,total,unknown


def main():
    repo=os.environ.get("QWEN_REPO","Qwen/Qwen3-8B-GGUF")
    filename=os.environ.get("QWEN_FILE","Qwen3-8B-Q4_K_M.gguf")
    model=hf_hub_download(repo_id=repo,filename=filename)
    llm=Llama(model_path=model,n_ctx=8192,n_threads=max(2,os.cpu_count() or 4),n_batch=1024,verbose=False)

    precision,coverage,matched,correct,wrong,unknown,errors=validate_gold(llm)
    report=["# Volume 5–9 Stage 1 validation","",f"Gold: `{GOLD.name}`",f"Model: `{repo}/{filename}`","",f"- matched: {matched}",f"- precision (non-unknown): {precision:.2%}",f"- coverage: {coverage:.2%}",f"- correct: {correct}",f"- wrong: {wrong}",f"- unknown: {unknown}","","## First errors"]
    report += [f"- line {n}: predicted `{p}`, gold `{g}` — `{t}`" for n,p,g,t in errors]
    (PROCESSED/"speaker_stage1_v5_v9_validation.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    print(f"VALIDATION precision={precision:.3%} coverage={coverage:.3%}",flush=True)
    if precision < 0.80:
        raise SystemExit("Validation precision below 80%; refusing to generate V5–V9")

    summary=[]
    for vol,parts in PARTS.items():
        for name in parts:
            path=WORK/name
            lines,labels=annotate_file(llm,path)
            states=detect_swap_labels(lines,labels,llm)
            target,total,unk=write_output(vol,name,lines,labels,states)
            summary.append((str(target.relative_to(ROOT)),total,unk))
            print(target,total,unk,flush=True)
    with (PROCESSED/"speaker_stage1_v5_v9_summary.json").open("w",encoding="utf-8") as f:
        json.dump({"validation":{"precision":precision,"coverage":coverage},"outputs":[{"path":p,"targets":t,"unknown":u} for p,t,u in summary]},f,ensure_ascii=False,indent=2)

if __name__=="__main__": main()
