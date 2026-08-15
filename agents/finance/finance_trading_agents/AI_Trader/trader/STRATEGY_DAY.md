# AI-Trader — Day-Trade Mode (Operating Spec) · 完全动态选股 / 高度激进

**Separate account:** `claude-daytrader` (agent_id 3), its own $100,000, its own
Discord channel. Fully independent of the swing book. **Paper trading only.**

**Run every command with the `TRADER_MODE=day` prefix** so it uses the day
account/config/state/journal:
```
TRADER_MODE=day .venv/Scripts/python.exe trader/snapshot.py
TRADER_MODE=day .venv/Scripts/python.exe trader/execute.py --action buy --market us-stock --symbol SMCI --notional 18000 --reason "..."
TRADER_MODE=day .venv/Scripts/python.exe trader/report.py
TRADER_MODE=day .venv/Scripts/python.exe trader/engine.py poll | record
```

---

## 追热点 — the universe is DYNAMIC
- **No fixed list.** Each cycle `snapshot.py` refreshes a live movers board from
  yfinance (`hotscan.py`: `day_gainers` + `most_actives`, free/unlimited) and
  returns it as **`hot_movers`** — ticker, intraday `chg_pct`, price, volume, cap.
- Liquidity guardrails are already applied (price ≥ $10, mkt-cap ≥ $2B, vol ≥ 1M
  shares & ≥ $50M traded) so the board is tradeable, not penny pumps.
- The tradeable universe (`config.UNIVERSE`) = that board ∪ a liquid core fallback
  (NVDA/TSLA/AAPL/AMZN/META/AMD), refreshed into `day_universe.json`. **Buys are
  gated to this set; exits are always allowed** (a name that drops off the board
  can still be closed for stop-loss).
- **Long-only for now.** Chase strength; shorting `day_losers` is deferred.

## When it trades
- **US stocks ONLY**, and **only during market hours**: 09:30–16:00 ET = **06:30–13:00 PT**, Mon–Fri.
- `snapshot.py` reports `us_market_open`. If false → **do nothing** (board is empty, server rejects orders).
- Cadence: **~5 minutes** per cycle while the market is open.

## Each cycle (only when US open + due)
1. `snapshot.py` → read `positions`, `hot_movers`, P&L (live-marked).
2. **Manage open positions FIRST:**
   - **Stop-loss:** any position with P&L ≤ **−6%** → close immediately.
   - **Take-profit:** P&L ≥ **+10%** → close (or trim and trail if momentum is
     clearly still accelerating; don't give back a big gain).
   - **Rotate:** if a holding has stalled/rolled over while fresher, stronger
     names lead the board, cut it and redeploy.
   - **End-of-day flat:** after **~12:50 PT** (≈15:50 ET), **close ALL positions** — nothing overnight.
3. **New entries — chase the strongest momentum on `hot_movers`:**
   - Favor strong, *still-working* moves with real volume. **Don't blindly buy the
     #1 parabolic spike** (e.g. a +50% biotic pop already exhausted) — prefer names
     breaking out with room (think SMCI/MU/MARA-type liquid momentum over a thin
     halt-risk pop).
   - Be **decisive and aggressive**: size 8–20% of equity, up to 7 concurrent.
   - Many trades expected (cap 80/day). Quality over forcing, but be active —
     sitting in cash through a trending session is a miss, not discipline.
4. `report.py` → push P&L card (after a trade, or roughly hourly). Then `engine.py record`.

## Strategy
Aggressive **intraday momentum / breakout** on whatever is hot today:
- Enter on confirmed intraday strength with volume; exit on the +10% / −6% brackets or a momentum break.
- No overnight risk — flat by close.

## Risk guardrails (enforced by `risk.py`)
| Rule | Value |
|------|-------|
| Single position max | **25%** of equity |
| Max concurrent positions | **7** |
| Cash reserve | ≥ **10%** |
| Suggested per-trade size | **8%–20%** |
| Stop-loss | **−6%** |
| Take-profit | **+10%** (trail strong winners) |
| Daily trade cap | **80** |
| Universe | DYNAMIC — yfinance movers board ∪ core fallback |

## Notes
- Hot board: `hotscan.py` (yfinance screeners). Cache: `day_universe.json` (≤45 min).
- US-stock prices come from the board / yfinance (Alpha Vantage free key is 25/day
  and already rate-limited — it is NOT relied on for the day book).
- Tunables in `trader/config.py` → `MODES["day"]` and `hotscan.py` constants.
  State: `state_day.json`. Journal: `journal_day.jsonl`.
- Control panel (localhost:8799 / public): the **日内 Day-Trade** card has its own 启动/停止 toggle.
