#!/usr/bin/env python
"""
auto-buy-alert · fund tracker -> #funds-manager Discord channel.

Cathie Wood / ARK  : downloads the 6 ARK ETF holdings CSVs daily and diffs vs the
                     stored previous day -> exact buys/sells + current holdings.
Leopold Aschenbrenner / Situational Awareness LP (CIK 0002045724):
                     monitors SEC EDGAR for new 13F-HR filings (quarterly, ~45-day
                     lag — the legal max for a hedge fund) and diffs each new filing
                     vs the prior quarter -> new buys/sells.

Pure Python (no Claude). Pushes via notify.py to DISCORD_WEBHOOK_FUNDS.
Run: python fund_tracker.py
"""
import csv
import datetime
import io
import json
import subprocess
import sys
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path

warnings.filterwarnings("ignore")
import requests

HERE = Path(__file__).resolve().parent
STATE = HERE / "fund_state"
STATE.mkdir(exist_ok=True)

UA_SEC = {"User-Agent": "auto-buy-alert wanhongyu411@gmail.com"}
UA_WEB = {"User-Agent": "Mozilla/5.0"}
SA_CIK = "0002045724"
ARK_BASE = "https://assets.ark-funds.com/fund-documents/funds-etf-csv/"
ARK_FUNDS = {
    "ARKK": "ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv",
    "ARKW": "ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS.csv",
    "ARKG": "ARK_GENOMIC_REVOLUTION_ETF_ARKG_HOLDINGS.csv",
    "ARKQ": "ARK_AUTONOMOUS_TECH._&_ROBOTICS_ETF_ARKQ_HOLDINGS.csv",
    "ARKF": "ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS.csv",
    "ARKX": "ARK_SPACE_EXPLORATION_&_INNOVATION_ETF_ARKX_HOLDINGS.csv",
}


def log(msg):
    line = f"{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')} [funds] {msg}"
    print(line)
    try:
        with (HERE / "run.log").open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def num(s):
    s = str(s).replace(",", "").replace("$", "").strip()
    try:
        return float(s)
    except Exception:
        return 0.0


def fmt_sh(x):
    x = abs(x)
    if x >= 1e6:
        return f"{x/1e6:.2f}M"
    if x >= 1e3:
        return f"{x/1e3:.0f}k"
    return f"{x:.0f}"


def fmt_usd(x):
    if x >= 1e9:
        return f"${x/1e9:.2f}B"
    if x >= 1e6:
        return f"${x/1e6:.1f}M"
    return f"${x:,.0f}"


def load_state(name):
    p = STATE / name
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def save_state(name, obj):
    (STATE / name).write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


# ----------------------- ARK / Cathie Wood -----------------------
def fetch_ark(fund):
    r = requests.get(ARK_BASE + ARK_FUNDS[fund], headers=UA_WEB, timeout=25)
    r.raise_for_status()
    holdings, date = {}, None
    for row in csv.DictReader(io.StringIO(r.text)):
        tk = (row.get("ticker") or "").strip()
        if not tk or tk.upper() in ("", "CASH"):
            continue
        date = (row.get("date") or date)
        holdings[tk] = {
            "company": (row.get("company") or "").strip(),
            "shares": num(row.get("shares")),
            "weight": (row.get("weight (%)") or "").strip(),
        }
    return date, holdings


def diff_holdings(prev, cur):
    buys, sells = [], []
    for tk, info in cur.items():
        if tk not in prev:
            buys.append((tk, "新建仓", info["shares"]))
        else:
            d = info["shares"] - prev[tk]["shares"]
            if d > 1:
                buys.append((tk, "增持", d))
            elif d < -1:
                sells.append((tk, "减持", d))
    for tk, info in prev.items():
        if tk not in cur:
            sells.append((tk, "清仓", -info["shares"]))
    return buys, sells


def track_ark():
    any_change = False
    baseline = False
    lines = []
    counts = []
    holdings_cards = []
    for fund in ARK_FUNDS:
        try:
            date, cur = fetch_ark(fund)
        except Exception as e:
            lines.append(f"**{fund}** 取数失败: {str(e)[:50]}")
            continue
        counts.append(f"{fund} {len(cur)}")
        items = sorted(cur.items(), key=lambda kv: num(kv[1].get("weight")), reverse=True)
        line = " | ".join(f"{tk} {info.get('weight','')}" for tk, info in items)
        holdings_cards.append({"title": f"📊 ARK {fund} · 全部持仓 {len(cur)}", "summary": line[:3800]})
        prev_state = load_state(f"ark_{fund}.json")
        save_state(f"ark_{fund}.json", {"date": date, "holdings": cur})
        if not prev_state:
            baseline = True
            continue
        buys, sells = diff_holdings(prev_state.get("holdings", {}), cur)
        if not buys and not sells:
            continue
        any_change = True
        parts = []
        if buys:
            parts.append("🟢买 " + ", ".join(f"{tk}({lbl} {fmt_sh(d)})" for tk, lbl, d in buys[:10]))
        if sells:
            parts.append("🔴卖 " + ", ".join(f"{tk}({lbl} {fmt_sh(d)})" for tk, lbl, d in sells[:10]))
        lines.append(f"**{fund}**  " + "  ".join(parts))

    if baseline:
        summary = ("首次运行,已建立基线(" + " / ".join(counts) + ")。"
                   "从下个交易日起报告 Cathie Wood / ARK 的每日买卖。")
    elif any_change:
        summary = "\n".join(lines)
    else:
        summary = "今日 6 只 ARK ETF 无持仓变动(完整持仓见下)。"
    return {"summary": summary, "changed": any_change, "holdings_cards": holdings_cards}


# -------------- Leopold Aschenbrenner / Situational Awareness 13F --------------
def latest_13f():
    sub = requests.get(f"https://data.sec.gov/submissions/CIK{SA_CIK}.json",
                       headers=UA_SEC, timeout=25).json()
    rec = sub["filings"]["recent"]
    for i in range(len(rec["form"])):
        if rec["form"][i].startswith("13F"):
            return rec["accessionNumber"][i], rec["filingDate"][i], sub.get("name")
    return None, None, sub.get("name")


def fetch_13f_holdings(accession):
    a = accession.replace("-", "")
    cik = int(SA_CIK)
    idx = requests.get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{a}/index.json",
                       headers=UA_SEC, timeout=25).json()
    docs = [d["name"] for d in idx["directory"]["item"]]
    info = [d for d in docs if d.lower().endswith(".xml") and d.lower() != "primary_doc.xml"]
    if not info:
        return {}
    xml = requests.get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{a}/{info[0]}",
                       headers=UA_SEC, timeout=25).text
    root = ET.fromstring(xml)
    ln = lambda t: t.split("}")[-1]
    holdings = {}
    for it in root.iter():
        if ln(it.tag) != "infoTable":
            continue
        d = {}
        for ch in it.iter():
            tag = ln(ch.tag)
            if tag in ("nameOfIssuer", "cusip", "value", "sshPrnamt"):
                d[tag] = (ch.text or "").strip()
        key = d.get("cusip") or d.get("nameOfIssuer")
        if not key:
            continue
        if key in holdings:
            holdings[key]["value"] += num(d.get("value"))
            holdings[key]["shares"] += num(d.get("sshPrnamt"))
        else:
            holdings[key] = {"name": d.get("nameOfIssuer", ""),
                             "value": num(d.get("value")), "shares": num(d.get("sshPrnamt"))}
    return holdings


def top_holdings_str(holdings, n=5):
    top = sorted(holdings.values(), key=lambda x: x["value"], reverse=True)[:n]
    return "; ".join(f"{h['name']}({fmt_usd(h['value'])})" for h in top)


def sa_holdings_card(holdings):
    items = sorted(holdings.values(), key=lambda h: h.get("value", 0), reverse=True)
    line = " | ".join(f"{h.get('name','')[:16]} {fmt_usd(h.get('value',0))}" for h in items)
    return {"title": f"📊 Situational Awareness · 13F 全部持仓 {len(holdings)}", "summary": line[:3800]}


def track_13f():
    try:
        acc, date, entity = latest_13f()
    except Exception as e:
        return {"summary": f"13F 查询失败: {str(e)[:60]}", "changed": False}
    if not acc:
        return {"summary": "未找到 13F 备案。", "changed": False}

    prev = load_state("sa_13f.json")
    if prev and prev.get("accession") == acc:
        cur = prev.get("holdings", {})
        return {"summary": (f"无新 13F。最新备案 {prev.get('date')}(季度披露,约每 3 个月、滞后 45 天)。\n"
                            f"当前前5持仓:{top_holdings_str(cur)}"),
                "changed": False, "holdings_card": sa_holdings_card(cur)}

    holdings = fetch_13f_holdings(acc)
    save_state("sa_13f.json", {"accession": acc, "date": date, "holdings": holdings})

    if not prev:
        return {"summary": (f"首次记录最新 13F({date}):共 {len(holdings)} 个持仓。\n"
                            f"前5:{top_holdings_str(holdings)}\n下次出新 13F 时报告变动。"),
                "changed": True, "holdings_card": sa_holdings_card(holdings)}

    p = prev.get("holdings", {})
    buys, sells = [], []
    for k, h in holdings.items():
        if k not in p:
            buys.append((h["name"], "新建仓", h["shares"]))
        else:
            d = h["shares"] - p[k]["shares"]
            if d > 1:
                buys.append((h["name"], "增持", d))
            elif d < -1:
                sells.append((h["name"], "减持", d))
    for k, h in p.items():
        if k not in holdings:
            sells.append((h["name"], "清仓", -h["shares"]))
    parts = [f"🆕 **新 13F**({date} 备案)"]
    if buys:
        parts.append("🟢 " + ", ".join(f"{nm}({lbl} {fmt_sh(s)}股)" for nm, lbl, s in buys[:12]))
    if sells:
        parts.append("🔴 " + ", ".join(f"{nm}({lbl} {fmt_sh(s)}股)" for nm, lbl, s in sells[:12]))
    parts.append(f"当前前5:{top_holdings_str(holdings)}")
    return {"summary": "\n".join(parts), "changed": True, "holdings_card": sa_holdings_card(holdings)}


def main():
    today = datetime.date.today().isoformat()
    ark = track_ark()
    sa = track_13f()
    cards = [
        {"title": f"🧭 Cathie Wood · ARK 每日交易 · {today}", "summary": ark["summary"][:4000]},
        {"title": "🧭 Leopold Aschenbrenner · Situational Awareness LP(13F)", "summary": sa["summary"][:4000]},
    ]
    # full current holdings (per user request)
    cards += ark.get("holdings_cards", [])
    if sa.get("holdings_card"):
        cards.append(sa["holdings_card"])
    cards_path = HERE / "_funds_cards.json"
    cards_path.write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")

    # funds channel never @everyone (per user preference)
    args = [sys.executable, str(HERE / "notify.py"), "--file", str(cards_path),
            "--webhook-key", "DISCORD_WEBHOOK_FUNDS"]
    r = subprocess.run(args, capture_output=True, text=True, timeout=60,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    log(f"ARK changed={ark['changed']} SA changed={sa['changed']} -> notify: {r.stdout.strip()} {r.stderr.strip()}")


if __name__ == "__main__":
    main()
