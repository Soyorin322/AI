from __future__ import annotations

import argparse
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
THOUGHT_RE = re.compile(r"^[\s　]*（.*）[\s　]*$")
PREFIX_RE = re.compile(r"^([^:\n]{1,80}):\s*(?=[「（])")
SCENE_RE = re.compile(r"^[\s　]*(?:# |▶︎▶︎【|【第|【序|【尾聲|【後記|【附錄|【特典|＊＊＊|\*\*\*)")
SPEECH_VERBS = "說|問|答|回答|喊|叫|嘟囔|低語|喃喃|開口|搭話|反駁|補充|宣布|命令|提醒|勸|抱怨|怒吼|叫嚷|說道|說著|問道|答道|回應|解釋|追問|斥責|笑道|感嘆"
THOUGHT_VERBS = "心想|暗想|想到|覺得|認為|意識到|在心裡|內心|默念|暗自|思忖|腦海"
SWAP_HINT = re.compile(r"替換|交換|換身|換回|恢復原本|恢複原本|身體.*(?:交換|替換)|靈魂.*(?:交換|替換)|又替換|又交換")


def strip_prefix(line:str)->str:
    return PREFIX_RE.sub("",line,count=1)


def clean_label(s:str)->str:
    s=s.strip().strip("`*'\" ")
    if "不確定" in s or "unknown" in s.lower(): return "unknown"
    s=re.sub(r"（身體：[^）]+）","",s)
    for a,c in sorted(ALIASES.items(),key=lambda x:len(x[0]),reverse=True):
        if s==a or (a in s and len(s)<=len(a)+8): return c
    return s if s in set(ALIASES.values()) else "unknown"


def candidate_names(text:str)->list[str]:
    out=[]
    for a,c in sorted(ALIASES.items(),key=lambda x:len(x[0]),reverse=True):
        if a in text and c not in out: out.append(c)
    for x in ("玲琳","慧月"):
        if x not in out: out.append(x)
    return out[:24]


def nearest_explicit(lines:list[str],i:int,thought:bool=False)->str|None:
    verbs=THOUGHT_VERBS if thought else SPEECH_VERBS
    for j in (i-1,i+1,i+2,i-2):
        if not 0<=j<len(lines): continue
        s=strip_prefix(lines[j])
        matches=[]
        for a,c in sorted(ALIASES.items(),key=lambda x:len(x[0]),reverse=True):
            if a in s and re.search(verbs,s) and c not in matches: matches.append(c)
        if len(matches)==1: return matches[0]
    return None


def scene_bounds(lines:list[str])->list[tuple[int,int]]:
    starts=[0]
    for i,s in enumerate(lines):
        if i and (SCENE_RE.match(s.strip()) or s.strip()=="＊＊＊"): starts.append(i)
    starts.append(len(lines))
    return [(starts[k],starts[k+1]) for k in range(len(starts)-1)]


def build_windows(lines:list[str],core:int=64,ctx:int=16):
    out=[]
    for ss,se in scene_bounds(lines):
        for p in range(ss,se,core):
            ce=min(se,p+core)
            targets=[i for i in range(p,ce) if TARGET_RE.match(strip_prefix(lines[i])) and "bilibili.com" not in lines[i] and strip_prefix(lines[i]).strip()!="（插畫）"]
            if targets: out.append((max(ss,p-ctx),min(se,ce+ctx),targets))
    return out


def load_model()->Llama:
    repo=os.environ.get("QWEN_REPO","Qwen/Qwen3-8B-GGUF")
    filename=os.environ.get("QWEN_FILE","Qwen3-8B-Q4_K_M.gguf")
    model=hf_hub_download(repo_id=repo,filename=filename)
    return Llama(model_path=model,n_ctx=8192,n_threads=max(2,os.cpu_count() or 4),n_batch=1024,verbose=False)


def ask_speakers(llm:Llama,lines:list[str],lo:int,hi:int,targets:list[int],pre:dict[int,str])->dict[int,str]:
    unresolved=[i for i in targets if pre.get(i,"unknown")=="unknown"]
    if not unresolved: return {}
    qid={idx:n for n,idx in enumerate(unresolved)}
    shown=[]
    for i in range(lo,hi):
        raw=strip_prefix(lines[i]); shown.append((f"[Q{qid[i]}] " if i in qid else "")+raw)
    block="\n".join(shown); cands=candidate_names(block)
    prompt=f"""判斷中文小說中每個 [Qn] 的真正 speaker 或 thinker。
- 「」是直接台詞；（）是內心話。
- 只依文本證據：明示說話/思考動詞、相鄰動作、受話者、對話輪替、場景 POV。
- 玲琳與慧月可能交換身體；此處只輸出人格，不依外表判斷。
- 回憶、轉述、引用不可誤當當下 speaker。
- 多人只能確定類別可用女官/百姓/男人/女人/眾人。
- 證據不足必須 unknown，禁止補猜。
候選：{', '.join(cands)}
只回 JSON：{{"labels":[{{"id":0,"speaker":"玲琳"}}]}}
文本：\n{block}\n/no_think"""
    r=llm.create_chat_completion(messages=[{"role":"system","content":"高精度小說 attribution；寧缺勿猜，只回 JSON。"},{"role":"user","content":prompt}],temperature=0,max_tokens=max(220,len(unresolved)*18),response_format={"type":"json_object"})
    content=r["choices"][0]["message"]["content"]
    try: obj=json.loads(content)
    except Exception:
        m=re.search(r"\{.*\}",content,re.S); obj=json.loads(m.group(0)) if m else {"labels":[]}
    out={}
    for item in obj.get("labels",[]):
        try:q=int(item.get("id"))
        except Exception:continue
        if 0<=q<len(unresolved): out[unresolved[q]]=clean_label(str(item.get("speaker","unknown")))
    for i in unresolved: out.setdefault(i,"unknown")
    return out


def annotate_file(llm:Llama,path:Path,validation_windows:int|None=None):
    lines=path.read_text(encoding="utf-8-sig").splitlines(); labels={}
    for i,s in enumerate(lines):
        raw=strip_prefix(s)
        if not TARGET_RE.match(raw) or "bilibili.com" in raw or raw.strip()=="（插畫）": continue
        labels[i]=nearest_explicit(lines,i,bool(THOUGHT_RE.match(raw))) or "unknown"
    wins=build_windows(lines)
    if validation_windows is not None and len(wins)>validation_windows:
        # Evenly sample the whole book, not only the beginning.
        idx=sorted(set(round(i*(len(wins)-1)/(validation_windows-1)) for i in range(validation_windows))) if validation_windows>1 else [0]
        wins=[wins[i] for i in idx]
        allowed={t for _,_,ts in wins for t in ts}
        labels={i:s for i,s in labels.items() if i in allowed}
    for k,(lo,hi,targets) in enumerate(wins,1):
        labels.update(ask_speakers(llm,lines,lo,hi,targets,labels))
        if k%8==0: print(path.name,k,"/",len(wins),flush=True)
    return lines,labels


def gold_labels(path:Path):
    q=defaultdict(deque)
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        m=PREFIX_RE.match(line)
        if not m: continue
        raw=strip_prefix(line)
        if TARGET_RE.match(raw): q[re.sub(r"\s+","",raw)].append(clean_label(m.group(1)))
    return q


def validate_gold(llm:Llama):
    lines,labels=annotate_file(llm,GOLD,validation_windows=20); gold=gold_labels(GOLD)
    matched=correct=wrong=unknown=0; errors=[]
    for i,p in labels.items():
        raw=strip_prefix(lines[i]); key=re.sub(r"\s+","",raw)
        if not gold[key]: continue
        g=gold[key].popleft()
        if g=="unknown": continue
        matched+=1
        if p=="unknown": unknown+=1
        elif p==g: correct+=1
        else:
            wrong+=1
            if len(errors)<30: errors.append((i+1,p,g,raw[:120]))
    known=correct+wrong; precision=correct/known if known else 0; coverage=known/matched if matched else 0
    return precision,coverage,matched,correct,wrong,unknown,errors


def ask_swap_transitions(llm:Llama,lines:list[str],centers:list[int],start_state:str)->list[tuple[int,str]]:
    if not centers: return []
    lo=max(0,min(centers)-24); hi=min(len(lines),max(centers)+25)
    shown=[f"[{i}] {strip_prefix(lines[i])}" for i in range(lo,hi)]
    prompt=f"""追蹤玲琳與慧月的換身狀態。進入這段前 state={start_state}。
normal = 玲琳在黃玲琳身體、慧月在朱慧月身體。
swapped = 玲琳在朱慧月身體、慧月在黃玲琳身體。
請只找文本中真正發生『換身／換回』的狀態轉換，不要把談論、回憶或假設誤認成轉換。
若有轉換，回傳發生後最早可確定新狀態的原始行號與 state_after；沒有則空陣列。
只回 JSON：{{"transitions":[{{"line":123,"state_after":"swapped"}}]}}
文本：\n"""+"\n".join(shown)+"\n/no_think"
    r=llm.create_chat_completion(messages=[{"role":"system","content":"只依文本判斷實際換身狀態轉換。"},{"role":"user","content":prompt}],temperature=0,max_tokens=220,response_format={"type":"json_object"})
    try: obj=json.loads(r["choices"][0]["message"]["content"])
    except Exception: obj={"transitions":[]}
    out=[]
    for x in obj.get("transitions",[]):
        try:n=int(x["line"]); st=str(x["state_after"])
        except Exception:continue
        if lo<=n<hi and st in ("normal","swapped"): out.append((n,st))
    return sorted(set(out))


def swap_timeline(llm:Llama,parts:list[list[str]]):
    # Global volume line space preserves state across part boundaries.
    lines=[]; offsets=[]
    for p in parts:
        offsets.append(len(lines)); lines.extend(p); lines.append("# __PART_BOUNDARY__")
    hints=[i for i,s in enumerate(lines) if SWAP_HINT.search(strip_prefix(s))]
    groups=[]
    for i in hints:
        if not groups or i-groups[-1][-1]>45: groups.append([i])
        else: groups[-1].append(i)
    if not groups: return offsets,{ }
    transitions=[]; state="normal"
    # Include the opening context as a guard against a volume beginning already swapped.
    groups=[[0]]+groups
    seen=set()
    for g in groups:
        key=(min(g),max(g))
        if key in seen: continue
        seen.add(key)
        tr=ask_swap_transitions(llm,lines,g,state)
        for n,st in tr:
            transitions.append((n,st)); state=st
    transitions=sorted(set(transitions))
    state_by_global={}; state="normal"; k=0
    for i in range(len(lines)):
        while k<len(transitions) and transitions[k][0]<=i:
            state=transitions[k][1]; k+=1
        state_by_global[i]=state
    return offsets,state_by_global


def render(sp:str,state:str)->str:
    if sp=="unknown": return "【speaker 不確定】"
    if sp=="玲琳" and state=="swapped": return "玲琳（身體：朱慧月）"
    if sp=="慧月" and state=="swapped": return "慧月（身體：黃玲琳）"
    return sp


def process_volume(llm:Llama,volume:int):
    source_parts=[]; annotations=[]
    for name in PARTS[volume]:
        lines,labels=annotate_file(llm,WORK/name); source_parts.append(lines); annotations.append((name,lines,labels))
    offsets,state_global=swap_timeline(llm,source_parts)
    d=PROCESSED/f"volume_{volume:02d}"; d.mkdir(parents=True,exist_ok=True)
    stats=[]
    for part_i,(name,lines,labels) in enumerate(annotations):
        out=[]; total=unknown=0; off=offsets[part_i]
        for i,line in enumerate(lines):
            raw=strip_prefix(line)
            if i in labels:
                total+=1; sp=labels[i]; unknown+=sp=="unknown"
                out.append(f"{render(sp,state_global.get(off+i,'normal'))}: {raw}")
            else: out.append(line)
        target=d/name.replace(".md","_speaker標註.md"); target.write_text("\n".join(out)+"\n",encoding="utf-8")
        stats.append({"path":str(target.relative_to(ROOT)),"targets":total,"unknown":unknown})
        print(target,total,unknown,flush=True)
    (d/"speaker_stage1_summary.json").write_text(json.dumps({"volume":volume,"outputs":stats},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--validate-only",action="store_true"); ap.add_argument("--volume",type=int,choices=PARTS)
    args=ap.parse_args(); llm=load_model()
    if args.validate_only:
        p,c,m,ok,bad,unk,errors=validate_gold(llm)
        PROCESSED.mkdir(parents=True,exist_ok=True)
        report=["# Volume 5–9 Stage 1 validation","",f"Gold: `{GOLD.name}`","Model: `Qwen3-8B-Q4_K_M`","Validation sample: 20 evenly distributed context windows","",f"- matched: {m}",f"- precision (non-unknown): {p:.2%}",f"- coverage: {c:.2%}",f"- correct: {ok}",f"- wrong: {bad}",f"- unknown: {unk}","","## First errors"]+[f"- line {n}: predicted `{x}`, gold `{g}` — `{t}`" for n,x,g,t in errors]
        (PROCESSED/"speaker_stage1_v5_v9_validation.md").write_text("\n".join(report)+"\n",encoding="utf-8")
        print(f"VALIDATION precision={p:.3%} coverage={c:.3%}",flush=True)
        if p<0.80: raise SystemExit("Validation precision below 80%")
        return
    if args.volume is None: raise SystemExit("Use --validate-only or --volume N")
    process_volume(llm,args.volume)

if __name__=="__main__": main()
