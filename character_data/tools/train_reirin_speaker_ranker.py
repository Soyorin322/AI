from __future__ import annotations

import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path

import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[2]
NOVEL = ROOT / "character_data" / "Reirin" / "sources" / "raw" / "novel"
GOLD = NOVEL / "惡女不才_第一卷_speaker重校.md"
REPORT = ROOT / "character_data" / "Reirin" / "speaker_attribution_ranker_validation.md"
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
    "林":"林熙",
    "女官":"女官","藤黃":"藤黃女官","銀硃":"銀硃女官","鄉民":"鄉民","邑民":"邑民",
    "女人":"女人","男人":"男人","少年":"少年","老婦人":"老婦人","侍童":"侍童","護衛":"護衛",
}
ALIASES_SORTED = sorted(ALIASES, key=len, reverse=True)
GENERIC={"女官","藤黃女官","銀硃女官","鄉民","邑民","女人","男人","少年","老婦人","侍童","護衛"}
QUOTE_RE=re.compile(r"^[\s　]*[「『]")
SCENE_RE=re.compile(r"^[\s　]*(?:▶︎▶︎【|【第|【序|【尾聲|【後記|【附錄|【特典SS|＊＊＊|\*\*\*)")
SPEECH_CUES=r"說(?:道)?|問(?:道)?|回答|答道|回應|喊(?:道)?|叫(?:道)?|嘟囔|喃喃|呢喃|開口|反駁|補充|打斷|斥責|怒吼|宣告|附和|吐槽|感嘆|命令|催促|提醒|搭話|回嘴|應道"
ACTION_CUES=r"笑|皺|點頭|搖頭|抬頭|低頭|轉身|伸手|握|嘆|瞪|睜|閉|探身|聳肩|行禮|跪|站|走|看|望"
RECIPIENT_MARKERS=("跟","向","對","給","替","為","問","叫住","看著","望著","瞪著")


def canon(s:str)->str:
    s=re.sub(r"（身體：[^）]+）","",s.strip())
    return ALIASES.get(s,s)


def norm_quote(s:str)->str:
    s=re.sub(r"^[^:\n]{1,50}:\s*(?=[「『])","",s.strip())
    return re.sub(r"\s+","",s)


def mentions(text:str)->list[str]:
    found=[]; masked=text
    for a in ALIASES_SORTED:
        if a in masked:
            c=ALIASES[a]
            if c not in found: found.append(c)
            masked=masked.replace(a," "*len(a))
    return found


def mention_count(text:str,cand:str)->int:
    return sum(text.count(a) for a,c in ALIASES.items() if c==cand)


def starts_as_actor(text:str,cand:str)->int:
    t=text.strip()[:32]
    for a,c in ALIASES.items():
        if c!=cand: continue
        m=re.search(re.escape(a),t)
        if m and m.start()<=10:
            pre=t[max(0,m.start()-4):m.start()]
            if not any(pre.endswith(x) for x in RECIPIENT_MARKERS): return 1
    return 0


def speech_subject(text:str,cand:str)->int:
    t=text.strip()
    for a,c in ALIASES.items():
        if c!=cand: continue
        for m in re.finditer(re.escape(a),t):
            pre=t[max(0,m.start()-4):m.start()]
            if any(pre.endswith(x) for x in RECIPIENT_MARKERS): continue
            tail=t[m.end():m.end()+25]
            if re.search(rf"^[^，。！？；:]{{0,10}}(?:{SPEECH_CUES})",tail): return 1
    return 0


def recipient_mention(text:str,cand:str)->int:
    for a,c in ALIASES.items():
        if c!=cand: continue
        for marker in RECIPIENT_MARKERS:
            if marker+a in text: return 1
    return 0


def actor_action(text:str,cand:str)->int:
    if not starts_as_actor(text,cand): return 0
    for a,c in ALIASES.items():
        if c!=cand: continue
        m=re.search(re.escape(a),text[:35])
        if m and re.search(rf"^[^，。！？]{{0,14}}(?:{ACTION_CUES})",text[m.end():m.end()+25]): return 1
    return 0


def scene_ids(lines:list[str])->list[int]:
    sid=0; out=[]
    for s in lines:
        if SCENE_RE.match(s.strip()) or s.strip()=="＊＊＊": sid+=1
        out.append(sid)
    return out


def scene_participants(lines:list[str],sids:list[int])->dict[int,list[str]]:
    counts=defaultdict(Counter)
    for i,s in enumerate(lines):
        if QUOTE_RE.match(s): continue
        for c in mentions(s): counts[sids[i]][c]+=1
    return {sid:[c for c,_ in cnt.most_common()] for sid,cnt in counts.items()}


def gold_map_for_raw(lines:list[str])->dict[int,str]:
    queues=defaultdict(deque)
    for s in GOLD.read_text(encoding="utf-8").splitlines():
        m=re.match(r"^([^:\n]{1,50}):\s*([「『].*)$",s)
        if m: queues[norm_quote(m.group(2))].append(canon(m.group(1)))
    out={}
    for i,s in enumerate(lines):
        if not QUOTE_RE.match(s): continue
        q=queues[norm_quote(s)]
        if q: out[i]=q.popleft()
    return out


def local_candidates(lines:list[str],i:int,sid:int,sids:list[int],parts:dict[int,list[str]],prev:list[str]|None=None)->list[str]:
    c=[]
    for radius in (3,8,20):
        lo=max(0,i-radius); hi=min(len(lines),i+radius+1)
        for j in range(lo,hi):
            if sids[j]!=sid: continue
            for n in mentions(lines[j]):
                if n not in c: c.append(n)
        if len(c)>=2: break
    if prev:
        for n in reversed(prev[-3:]):
            if n not in c and n!="unknown": c.append(n)
    for n in parts.get(sid,[])[:4]:
        if n not in c: c.append(n)
    return c[:10]


def feat(lines:list[str],i:int,cand:str,sids:list[int],parts:dict[int,list[str]],prev_speaker:str|None,prev2_speaker:str|None)->dict[str,float]:
    f={}
    sid=sids[i]
    for off in (-4,-3,-2,-1,1,2,3,4):
        j=i+off
        if j<0 or j>=len(lines) or sids[j]!=sid: continue
        t=lines[j]
        kind="q" if QUOTE_RE.match(t) else "n"
        key=f"{off:+d}_{kind}"
        f[key+"_mention"]=float(mention_count(t,cand)>0)
        f[key+"_count"]=min(3,mention_count(t,cand))
        if kind=="n":
            f[key+"_actor"]=starts_as_actor(t,cand)
            f[key+"_speechsubj"]=speech_subject(t,cand)
            f[key+"_action"]=actor_action(t,cand)
            f[key+"_recipient"]=recipient_mention(t,cand)
    quote=lines[i]
    f["in_quote"]=float(mention_count(quote,cand)>0)
    f["recipient_in_quote"]=recipient_mention(quote,cand)
    f["is_generic"]=float(cand in GENERIC)
    f["prev_same"]=float(prev_speaker==cand)
    f["prev2_same"]=float(prev2_speaker==cand)
    f["scene_rank0"]=float(parts.get(sid,[None])[0:1]==[cand])
    f["scene_top3"]=float(cand in parts.get(sid,[])[:3])
    local=[]
    for j in range(max(0,i-4),min(len(lines),i+5)):
        if sids[j]==sid and not QUOTE_RE.match(lines[j]):
            for n in mentions(lines[j]):
                if n not in local: local.append(n)
    f["only_local_name"]=float(local==[cand])
    # Nearest named narrative actor before/after.
    for direction,name in ((-1,"before"),(1,"after")):
        nearest=None
        for d in range(1,7):
            j=i+direction*d
            if j<0 or j>=len(lines) or sids[j]!=sid: break
            if QUOTE_RE.match(lines[j]): continue
            ns=mentions(lines[j])
            if ns:
                nearest=ns[0]; break
        f[f"nearest_{name}"]=float(nearest==cand)
    return f


def make_pair_dataset(lines:list[str],gold:dict[int,str],indices:list[int]):
    sids=scene_ids(lines); parts=scene_participants(lines,sids)
    X=[]; y=[]
    prev_by_scene=defaultdict(list)
    for i in indices:
        if i not in gold: continue
        sid=sids[i]; history=prev_by_scene[sid]
        prev=history[-1] if history else None; prev2=history[-2] if len(history)>1 else None
        cands=local_candidates(lines,i,sid,sids,parts,history)
        if gold[i] not in cands: cands.append(gold[i])
        for c in cands:
            X.append(feat(lines,i,c,sids,parts,prev,prev2)); y.append(int(c==gold[i]))
        history.append(gold[i])
    return X,np.array(y)


def fit_model(lines:list[str],gold:dict[int,str],train_indices:list[int]):
    X,y=make_pair_dataset(lines,gold,train_indices)
    vec=DictVectorizer(sparse=True)
    Xm=vec.fit_transform(X)
    clf=LogisticRegression(max_iter=1500,class_weight="balanced",C=1.2,solver="liblinear")
    clf.fit(Xm,y)
    return vec,clf


def rank_predict(lines:list[str],quote_indices:list[int],vec,clf,threshold:float,margin:float):
    sids=scene_ids(lines); parts=scene_participants(lines,sids)
    pred={}; scores={}; hist=defaultdict(list)
    for i in quote_indices:
        sid=sids[i]; history=hist[sid]
        prev=history[-1] if history else None; prev2=history[-2] if len(history)>1 else None
        cands=local_candidates(lines,i,sid,sids,parts,history)
        if not cands:
            pred[i]="unknown"; hist[sid].append("unknown"); continue
        X=[feat(lines,i,c,sids,parts,prev,prev2) for c in cands]
        ps=clf.predict_proba(vec.transform(X))[:,1]
        order=np.argsort(-ps)
        top=int(order[0]); p1=float(ps[top]); p2=float(ps[order[1]]) if len(order)>1 else 0.0
        scores[i]=(cands[top],p1,p2)
        sp=cands[top] if p1>=threshold and p1-p2>=margin else "unknown"
        pred[i]=sp; hist[sid].append(sp)
    return pred,scores


def evaluate(gold:dict[int,str],pred:dict[int,str],indices:list[int]):
    correct=wrong=unknown=0; errs=[]
    for i in indices:
        if i not in gold: continue
        p=pred.get(i,"unknown"); g=gold[i]
        if p=="unknown": unknown+=1
        elif p==g: correct+=1
        else:
            wrong+=1
            if len(errs)<25: errs.append((i+1,p,g))
    known=correct+wrong; total=known+unknown
    return (correct/known if known else 0,known/total if total else 0,correct,wrong,unknown,errs)


def choose_threshold(lines,gold,train_idx,val_idx):
    vec,clf=fit_model(lines,gold,train_idx)
    best=None
    for th in np.arange(0.35,0.91,0.05):
        for mg in (0.0,0.05,0.10,0.15,0.20,0.25):
            pred,_=rank_predict(lines,val_idx,vec,clf,float(th),float(mg))
            ev=evaluate(gold,pred,val_idx)
            precision,coverage=ev[0],ev[1]
            target=precision>=0.95
            key=(int(target),coverage,precision)
            if best is None or key>best[0]: best=(key,float(th),float(mg),ev)
    return best,vec,clf


def body_states(volume:int,lines:list[str])->list[str]:
    state="swapped" if volume==2 else "normal"; out=[]
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


def render(sp,state):
    if state=="swapped" and sp=="玲琳": return "玲琳（身體：朱慧月）"
    if state=="swapped" and sp=="慧月": return "慧月（身體：黃玲琳）"
    return sp


def write_volume(v,vec,clf,th,mg):
    lines=RAW[v].read_text(encoding="utf-8-sig").splitlines()
    qs=[i for i,s in enumerate(lines) if QUOTE_RE.match(s)]
    pred,scores=rank_predict(lines,qs,vec,clf,th,mg)
    states=body_states(v,lines)
    out=[
        "《惡女不才，請多關照！～雛宮蝶鼠換身傳～》",
        f"第{v}卷 Speaker 重校版（gold-trained structural ranker）",
        "依 character_data/speaker_attribution_guidelines.md，以第一卷人工完整校正版學習敘事結構特徵。",
        "原始小說保留；只對直接台詞加 speaker。低信心保留【speaker 不確定】。",
        "換身期間依人格標註：玲琳（身體：朱慧月）／慧月（身體：黃玲琳）。",
        "",
    ]
    unknown=0
    for i,s in enumerate(lines):
        if QUOTE_RE.match(s):
            p=pred.get(i,"unknown")
            if p=="unknown": unknown+=1; out.append(f"【speaker 不確定】: {s}")
            else: out.append(f"{render(p,states[i])}: {s}")
        else: out.append(s)
    OUT[v].write_text("\n".join(out)+"\n",encoding="utf-8")
    return len(qs),unknown


def main():
    lines=RAW[1].read_text(encoding="utf-8-sig").splitlines()
    gold=gold_map_for_raw(lines)
    qs=[i for i,s in enumerate(lines) if QUOTE_RE.match(s)]
    aligned=[i for i in qs if i in gold]
    split=int(len(aligned)*0.72)
    train_idx=aligned[:split]; val_idx=aligned[split:]
    best,_,_=choose_threshold(lines,gold,train_idx,val_idx)
    _,th,mg,val=best
    precision,coverage,correct,wrong,unknown,errs=val

    # Retrain on all aligned gold quotes after threshold selection.
    vec,clf=fit_model(lines,gold,aligned)
    stats=[(v,*write_volume(v,vec,clf,th,mg)) for v in (2,3)]

    report=[
        "# Reirin Speaker Attribution — Gold-trained Structural Ranker",
        "",
        f"- Raw Volume 1 direct quotes: **{len(qs)}**",
        f"- Quotes aligned to user-corrected gold: **{len(aligned)}** ({len(aligned)/len(qs):.2%})",
        f"- Validation split: first {len(train_idx)} aligned quotes train / last {len(val_idx)} validation",
        f"- Selected probability threshold: **{th:.2f}**",
        f"- Selected top1-top2 margin: **{mg:.2f}**",
        f"- Validation precision (non-unknown): **{precision:.2%}**",
        f"- Validation coverage: **{coverage:.2%}**",
        f"- Correct / wrong / unknown: **{correct} / {wrong} / {unknown}**",
        "",
        "## Generated volumes",
        "",
    ]
    for v,total,u in stats:
        report.append(f"- Volume {v}: {total} direct quote lines; {u} unknown ({u/total:.2%}).")
    report += ["", "## Validation error examples", ""]
    report += [f"- raw line {ln}: predicted `{p}`, gold `{g}`" for ln,p,g in errs] or ["- None"]
    report += ["", "This ranker deliberately uses structural/context features rather than character identity/style features, so it can generalize to later-volume characters without circular style contamination.", ""]
    REPORT.write_text("\n".join(report),encoding="utf-8")
    print("\n".join(report[:14]))

if __name__=="__main__": main()
