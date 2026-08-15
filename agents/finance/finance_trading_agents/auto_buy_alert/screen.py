#!/usr/bin/env python
"""
auto-buy-alert · technical screener (deterministic stage 1).

Usage:
    python screen.py --session {close|preopen|catchup}

Reads watchlist.txt (one ticker per line), pulls ~1y daily data via yfinance,
and applies a "pullback-in-uptrend / oversold-but-stabilizing" rule set.
Prints a JSON report to stdout for the orchestrator (Claude) to do the news
confirmation step. Output is intentionally English/ASCII so it travels cleanly
through any console encoding; the human-facing Discord card is composed later.
"""
import argparse
import json
import sys
import warnings
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

warnings.filterwarnings("ignore")

import yfinance as yf

from indicators import rsi, sma, sma_value_and_slope

HERE = Path(__file__).resolve().parent
ET = ZoneInfo("America/New_York")

# --- tunable thresholds (kept conservative for "stable, few false positives") ---
NEAR_SUPPORT_LOW = -0.01     # allow price slightly below a rising MA
NEAR_SUPPORT_HIGH = 0.03     # ...up to 3% above it (pullback to support)
OVERSOLD_RSI = 35.0
VOL_SPIKE_MULT = 2.5         # down-day volume blowout => likely breakdown, skip
RECENT_RSI_DAYS = 3


def load_watchlists():
    """Return (unique_tickers_in_order, ticker_to_lists, lists_dict).

    Prefers watchlists.json ({"Charles": [...], ...}); falls back to the legacy
    flat watchlist.txt as a single list named 'default'.
    """
    lists = {}
    wl = HERE / "watchlists.json"
    if wl.exists():
        try:
            raw = json.loads(wl.read_text(encoding="utf-8-sig"))
            for name, arr in raw.items():
                lists[name] = [str(t).strip().upper() for t in arr if str(t).strip()]
        except Exception:
            lists = {}
    if not lists:
        txt = HERE / "watchlist.txt"
        if txt.exists():
            arr = [ln.strip().upper() for ln in txt.read_text(encoding="utf-8").splitlines()
                   if ln.strip() and not ln.strip().startswith("#")]
            lists = {"default": arr}

    ticker_lists, order = {}, []
    for name, arr in lists.items():
        for t in arr:
            if t not in ticker_lists:
                ticker_lists[t] = []
                order.append(t)
            if name not in ticker_lists[t]:
                ticker_lists[t].append(name)
    return order, ticker_lists, lists


def trend_window(n):
    if n >= 200:
        return 200
    if n >= 50:
        return 50
    if n >= 20:
        return 20
    return None


def fetch_daily(ticker):
    df = yf.Ticker(ticker).history(period="1y", interval="1d", auto_adjust=True)
    if df is None or df.empty:
        return None
    return df.dropna(subset=["Close"])


def fetch_premarket(ticker, prev_close):
    """Best-effort latest/pre-market price + gap% vs prev close."""
    last = None
    try:
        intr = yf.Ticker(ticker).history(period="1d", interval="1m", prepost=True)
        if intr is not None and not intr.empty:
            last = float(intr["Close"].dropna().iloc[-1])
    except Exception:
        last = None
    if last is None:
        try:
            last = float(yf.Ticker(ticker).fast_info["lastPrice"])
        except Exception:
            last = None
    if last is None or not prev_close:
        return last, None
    gap = round((last - prev_close) / prev_close * 100.0, 2)
    return round(last, 4), gap


def analyze(ticker, session):
    """Return (candidate_dict_or_None, skip_dict_or_None, last_date, is_crypto)."""
    is_crypto = ticker.endswith("-USD")
    df = fetch_daily(ticker)
    if df is None:
        return None, {"ticker": ticker, "reason": "no_data"}, None, is_crypto

    n = len(df)
    last_date = df.index[-1].date()
    if n < 20:
        return None, {"ticker": ticker, "reason": "insufficient_history", "bars": n}, last_date, is_crypto

    close, openp, vol = df["Close"], df["Open"], df["Volume"]
    rsi_series = rsi(close, 14)
    if rsi_series.dropna().shape[0] < 2:
        return None, {"ticker": ticker, "reason": "insufficient_history_rsi", "bars": n}, last_date, is_crypto

    tw = trend_window(n)
    c = float(close.iloc[-1])
    o = float(openp.iloc[-1])
    prev_c = float(close.iloc[-2])
    v = float(vol.iloc[-1])
    avgv20 = float(vol.rolling(20).mean().iloc[-1]) if n >= 20 else float(vol.mean())
    rsi_now = float(rsi_series.iloc[-1])
    rsi_prev = float(rsi_series.iloc[-2])
    rsi_min3 = float(rsi_series.iloc[-RECENT_RSI_DAYS:].min())

    sma_trend, _ = sma_value_and_slope(close, tw) if tw else (None, None)
    trend_ok = sma_trend is not None and c > sma_trend

    oversold_turn = (rsi_min3 <= OVERSOLD_RSI) and (rsi_now > rsi_prev)
    pull_support = False
    support_ma = None
    for w in (20, 60):
        val, rising = sma_value_and_slope(close, w)
        if val and rising:
            dist = (c - val) / val
            if NEAR_SUPPORT_LOW <= dist <= NEAR_SUPPORT_HIGH:
                pull_support = True
                support_ma = w
    pullback = oversold_turn or pull_support

    stabilize = (c > o) or (c > prev_c)
    volume_ok = not ((c < prev_c) and (v > VOL_SPIKE_MULT * avgv20))

    is_candidate = bool(trend_ok and pullback and stabilize and volume_ok)

    # score 0..100 for ranking (more oversold + at support + green => higher)
    score = 0.0
    score += max(0.0, OVERSOLD_RSI - min(rsi_now, OVERSOLD_RSI)) * 2.0
    score += 20.0 if pull_support else 0.0
    score += 20.0 if oversold_turn else 0.0
    score += 10.0 if c > o else 0.0
    score = round(min(score, 100.0), 1)

    flags = {
        "close": round(c, 4),
        "prev_close": round(prev_c, 4),
        "chg_pct": round((c - prev_c) / prev_c * 100.0, 2),
        "rsi14": round(rsi_now, 2),
        "rsi_min_3d": round(rsi_min3, 2),
        "trend_ma_window": tw,
        "above_trend_ma": trend_ok,
        "oversold_turn": oversold_turn,
        "pullback_to_support_ma": support_ma,
        "green_candle": c > o,
        "volume_ok": volume_ok,
        "bars": n,
        "last_bar": str(last_date),
    }

    if session in ("preopen", "catchup"):
        pm, gap = fetch_premarket(ticker, c)
        flags["premarket_price"] = pm
        flags["gap_pct"] = gap

    bits = []
    bits.append(f"RSI(14)={rsi_now:.1f}" + (" turning up" if rsi_now > rsi_prev else ""))
    if support_ma:
        bits.append(f"pullback to rising SMA{support_ma}")
    if oversold_turn:
        bits.append("oversold bounce")
    bits.append("green candle" if c > o else "vs prev close up" if c > prev_c else "weak")
    bits.append(f"above SMA{tw}" if trend_ok else f"below SMA{tw}")
    if not volume_ok:
        bits.append("HIGH down-volume")
    reason = "; ".join(bits)

    rec = {"ticker": ticker, "is_crypto": is_crypto, "candidate": is_candidate,
           "score": score, "flags": flags, "reason": reason}
    if is_candidate:
        return rec, None, last_date, is_crypto
    return None, {"ticker": ticker, "reason": "no_setup", "score": score,
                  "rsi14": round(rsi_now, 2), "above_trend_ma": trend_ok}, last_date, is_crypto


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", choices=["close", "preopen", "catchup"], default="close")
    args = ap.parse_args()

    tickers, ticker_lists, lists = load_watchlists()
    candidates, skipped = [], []
    equity_last_dates = []

    for t in tickers:
        try:
            cand, skip, last_date, is_crypto = analyze(t, args.session)
        except Exception as e:
            skipped.append({"ticker": t, "lists": ticker_lists.get(t, []),
                            "reason": f"error: {type(e).__name__}: {e}"[:160]})
            continue
        if cand:
            cand["lists"] = ticker_lists.get(t, [])
            candidates.append(cand)
        elif skip:
            skip["lists"] = ticker_lists.get(t, [])
            skipped.append(skip)
        if last_date is not None and not is_crypto:
            equity_last_dates.append(last_date)

    candidates.sort(key=lambda x: x["score"], reverse=True)

    # session-aware staleness: for the close run, today's bar should exist.
    stale = False
    now_et = datetime.now(ET)
    if args.session == "close" and equity_last_dates:
        if max(equity_last_dates) < now_et.date():
            stale = True

    report = {
        "session": args.session,
        "generated_at": now_et.isoformat(timespec="seconds"),
        "stale": stale,
        "watchlist_size": len(tickers),
        "watchlists": lists,
        "n_candidates": len(candidates),
        "candidates": candidates,
        "skipped": skipped,
    }
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
