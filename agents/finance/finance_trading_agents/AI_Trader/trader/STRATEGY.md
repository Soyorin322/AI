# AI-Trader — Claude Auto Paper-Trading Agent (Operating Spec)

**Account:** `claude-trader` (agent_id 2) on the LOCAL instance `localhost:8000`.
**This is paper trading — simulated $100,000, no real money, no real brokerage.**
All trade notifications + P&L go to the configured Discord webhook.

---

## Every wake (the control page is the on/off switch)

The engine is **this Claude Code session**, woken on a schedule. The control page
(`http://localhost:8787`) flips the `loop_on` flag; it does not trade itself.

Each wake, FIRST run:
```
.venv/Scripts/python.exe trader/engine.py poll
```
It updates the heartbeat (so the page shows the engine "online") and returns
`{loop_on, due, ...}`.
- `loop_on=false` → do nothing else this wake (engine is paused). Stop.
- `loop_on=true` and `due=false` → already traded recently; just stop.
- `loop_on=true` and `due=true` → run the full cycle below, then finish with
  `.venv/Scripts/python.exe trader/engine.py record`.

Then **always reschedule the next wake (~30 min)** so the loop continues.

## The trading cycle (only when due+on)

1. **Read the market + account snapshot** (one command, emits JSON):
   ```
   .venv/Scripts/python.exe trader/snapshot.py
   ```
   It includes: cash, equity, real-time P&L, open positions (live-marked),
   live quotes for the universe, market-open flags, risk limits, recent news,
   and the recent journal. `us_market_open=false` → **do not** trade us-stock
   this cycle (the server will reject it anyway).

2. **Decide** (this is the Claude judgment step — see Strategy below). Pick zero
   or more actions. Doing nothing is a valid, common outcome.

3. **Place each trade** (one command per order; risk is enforced inside, and a
   Discord card is sent on success):
   ```
   .venv/Scripts/python.exe trader/execute.py --action buy  --market crypto   --symbol BTC --notional 8000 --reason "<short rationale>"
   .venv/Scripts/python.exe trader/execute.py --action sell --market crypto   --symbol BTC --pct 100        --reason "<short rationale>"
   .venv/Scripts/python.exe trader/execute.py --action buy  --market us-stock --symbol NVDA --notional 6000 --reason "<short rationale>"
   ```
   - buy/short: size with `--notional <dollars>`.
   - sell/cover: close with `--pct <percent>` (default 100) or `--qty <n>`.
   - A `--reason` is required; it appears in Discord and the journal.
   - If a trade is rejected (risk or market-closed), the JSON shows `ok:false`
     with a reason — note it and move on, do not retry blindly.

4. **Push the P&L card** to Discord:
   ```
   .venv/Scripts/python.exe trader/report.py
   ```

Run all commands from the repo root `E:\data\finance\AI-Trader`. Append `2>/dev/null`
to keep stdout clean JSON.

---

## Strategy (discretionary, rule-bounded)

Not a fixed formula. Each cycle weigh:
- **Trend / momentum** of each quote vs the position's entry and recent journal.
- **Market intel** in the snapshot (news/macro) — lean with clear catalysts,
  stand aside on noise.
- **Position management first:** before opening anything, check open positions
  against the **stop-loss** and take-profit logic below.
- **Conviction sizing:** stronger setups → closer to the 15% per-trade ceiling;
  weak/uncertain → smaller or skip.
- **Diversify:** avoid concentrating the book in one name or one direction.
- Prefer **fewer, higher-quality** trades. The daily cap is 20 but a typical
  cycle places 0–2 orders.

### Hard exits (do these first, every cycle)
- **Stop-loss:** any position with P&L ≤ **−15%** → close it.
- **Take-profit (guideline):** trim/close winners ≥ **+20%** unless momentum is
  clearly continuing.

---

## Risk guardrails (also enforced in code by `risk.py`)

| Rule | Value |
|------|-------|
| Single position max | 20% of equity |
| Max concurrent positions | 6 |
| Cash reserve (never spend below) | 15% of equity |
| Suggested per-trade size | 5%–15% of equity |
| Stop-loss | −15% from entry |
| Daily trade limit | 20 executed trades / local day (Vancouver) |
| Universe | crypto: BTC, ETH, SOL · us-stock: AAPL, NVDA, MSFT, TSLA, AMZN |

`execute.py` will clamp an oversized order down to the limit (and say so) or
reject it. Trust those rejections.

---

## Markets & hours (trader is in Vancouver / Pacific)
- **Crypto:** 24/7 (Hyperliquid). Always tradable.
- **US stocks:** only 09:30–16:00 ET = **06:30–13:00 PT**, Mon–Fri. Outside that
  window snapshot omits stock quotes and the server rejects stock orders.

## Cadence
- US market open hours: ~every **30 min** (crypto + stocks).
- Off-hours / weekends: ~every **60–90 min** (crypto only).

## Notes
- Config & secrets: `trader/secrets.json` (gitignored — token, webhook, AV key).
- Tunables (universe, risk %, limits): `trader/config.py`.
- Trade history / daily counter: `trader/journal.jsonl`.
- To pause: stop the loop. To reset the account: delete the SQLite DB and
  re-register. Backend + worker must be running (`main.py`, `worker.py`).
