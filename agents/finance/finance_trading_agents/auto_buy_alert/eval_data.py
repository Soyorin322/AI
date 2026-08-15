#!/usr/bin/env python
"""
auto-buy-alert · /eval data collector.

Gathers the deterministic facts for a "全方位" stock/crypto report and prints JSON:
technicals, fundamentals (stocks), Fear & Greed context, and cross-references
against Cathie Wood / ARK holdings, Aschenbrenner's 13F, and the local watchlists.
The Claude synthesis step (eval_routine.md) turns this + live news into the report.

Usage: python eval_data.py <TICKER>     e.g. INTC, NVDA, BTC, BTC-USD
"""
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import yfinance as yf

from indicators import rsi, sma
from fear_greed import get_fear_greed

HERE = Path(__file__).resolve().parent
ARK_FUNDS = ["ARKK", "ARKW", "ARKG", "ARKQ", "ARKF", "ARKX"]
CRYPTO = {"BTC", "ETH", "SOL", "DOGE", "XRP", "ADA", "AVAX", "LINK", "BNB", "LTC"}


def normalize(t):
    t = t.strip().upper()
    if t.endswith("-USD"):
        return t, True
    if t in CRYPTO:
        return t + "-USD", True
    return t, False


def pct_ret(close, days):
    if len(close) > days:
        return round((close.iloc[-1] / close.iloc[-1 - days] - 1) * 100, 2)
    return None


def technicals(ticker):
    df = yf.Ticker(ticker).history(period="1y", interval="1d", auto_adjust=True)
    if df is None or df.empty:
        return None
    close = df["Close"].dropna()
    n = len(close)
    c = float(close.iloc[-1])
    out = {
        "price": round(c, 4),
        "chg_1d_pct": pct_ret(close, 1),
        "ret_1m_pct": pct_ret(close, 21),
        "ret_3m_pct": pct_ret(close, 63),
        "ret_6m_pct": pct_ret(close, 126),
        "rsi14": round(float(rsi(close, 14).iloc[-1]), 1) if n > 15 else None,
        "bars": n,
    }
    for w in (20, 50, 200):
        if n >= w:
            v = float(sma(close, w).iloc[-1])
            out[f"sma{w}"] = round(v, 2)
            out[f"above_sma{w}"] = bool(c > v)
    hi, lo = float(close.max()), float(close.min())
    out["wk52_high"], out["wk52_low"] = round(hi, 2), round(lo, 2)
    out["pos_in_52w_pct"] = round((c - lo) / (hi - lo) * 100, 1) if hi > lo else None
    return out


def fundamentals(ticker):
    try:
        info = yf.Ticker(ticker).info or {}
    except Exception:
        return {}
    keys = {
        "longName": "name", "sector": "sector", "industry": "industry",
        "marketCap": "market_cap", "trailingPE": "pe_ttm", "forwardPE": "pe_fwd",
        "profitMargins": "profit_margin", "revenueGrowth": "rev_growth",
        "dividendYield": "div_yield", "beta": "beta",
        "targetMeanPrice": "analyst_target", "recommendationKey": "analyst_reco",
        "longBusinessSummary": "summary",
    }
    out = {}
    for k, v in keys.items():
        if info.get(k) is not None:
            out[v] = info[k]
    if out.get("summary"):
        out["summary"] = out["summary"][:600]
    return out


def ark_cross_ref(ticker):
    hits = []
    for f in ARK_FUNDS:
        p = HERE / "fund_state" / f"ark_{f}.json"
        if not p.exists():
            continue
        try:
            h = json.loads(p.read_text(encoding="utf-8")).get("holdings", {})
        except Exception:
            continue
        if ticker in h:
            hits.append({"fund": f, "weight": h[ticker].get("weight"), "shares": h[ticker].get("shares")})
    return hits


def sa13f_cross_ref(company_name):
    p = HERE / "fund_state" / "sa_13f.json"
    if not p.exists() or not company_name:
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    key = company_name.upper().split()[0]  # e.g. "INTEL", "NVIDIA"
    for h in d.get("holdings", {}).values():
        nm = (h.get("name") or "").upper()
        if key and key in nm:
            return {"name": h.get("name"), "value": h.get("value"), "shares": h.get("shares"),
                    "filing_date": d.get("date")}
    return None


def watchlist_cross_ref(ticker):
    p = HERE / "watchlists.json"
    if not p.exists():
        return []
    try:
        wl = json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception:
        return []
    return [name for name, arr in wl.items() if ticker in [str(x).upper() for x in arr]]


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: eval_data.py <TICKER>"}))
        return
    raw = sys.argv[1]
    ticker, is_crypto = normalize(raw)

    tech = technicals(ticker)
    if tech is None:
        print(json.dumps({"error": f"no data for {ticker}", "input": raw}, ensure_ascii=False))
        return

    fund = {} if is_crypto else fundamentals(ticker)
    report = {
        "input": raw,
        "ticker": ticker,
        "asset_type": "crypto" if is_crypto else "stock",
        "technicals": tech,
        "fundamentals": fund,
        "fear_greed": get_fear_greed(),
        "ark_holdings": ark_cross_ref(ticker),
        "aschenbrenner_13f": sa13f_cross_ref(fund.get("name") or ticker),
        "in_watchlists": watchlist_cross_ref(ticker),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
