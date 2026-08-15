#!/usr/bin/env python
"""
auto-buy-alert · Fear & Greed indices.

US stocks  : CNN Fear & Greed Index (official). If CNN is unreachable, falls back
             to a VIX-based gauge via yfinance (higher VIX = more fear).
Crypto/BTC : alternative.me Fear & Greed Index.

Prints JSON; importable via get_fear_greed().
"""
import json
import warnings

warnings.filterwarnings("ignore")
import requests

CNN_URL = "https://production.dataviz.cnn.com/index/fearandgreed/graphdata"
CNN_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.cnn.com/markets/fear-and-greed",
}


def _label(v):
    if v < 25: return "Extreme Fear"
    if v < 45: return "Fear"
    if v < 55: return "Neutral"
    if v < 75: return "Greed"
    return "Extreme Greed"


def stocks_fng():
    # 1) official CNN index
    try:
        r = requests.get(CNN_URL, headers=CNN_HEADERS, timeout=10)
        if r.status_code == 200:
            fg = r.json().get("fear_and_greed", {})
            score = int(round(float(fg.get("score"))))
            return {"source": "CNN", "value": score,
                    "rating": fg.get("rating") or _label(score),
                    "detail": "CNN Fear & Greed"}
    except Exception:
        pass
    # 2) fallback: VIX-based gauge (always reachable via yfinance)
    try:
        import yfinance as yf
        vix = float(yf.Ticker("^VIX").history(period="5d")["Close"].dropna().iloc[-1])
        score = max(0, min(100, int(round(120 - vix * 3.5))))
        return {"source": "VIX", "value": score, "rating": _label(score),
                "detail": f"VIX {vix:.1f} (CNN 不可达, 用 VIX 估算)"}
    except Exception as e:
        return {"source": None, "value": None, "rating": "unavailable", "detail": str(e)[:80]}


def crypto_fng():
    try:
        d = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10).json()["data"][0]
        return {"source": "alternative.me", "value": int(d["value"]),
                "rating": d["value_classification"], "detail": "BTC/Crypto Fear & Greed"}
    except Exception as e:
        return {"source": None, "value": None, "rating": "unavailable", "detail": str(e)[:80]}


def get_fear_greed():
    return {"stocks": stocks_fng(), "crypto": crypto_fng()}


if __name__ == "__main__":
    print(json.dumps(get_fear_greed(), ensure_ascii=False, indent=2))
