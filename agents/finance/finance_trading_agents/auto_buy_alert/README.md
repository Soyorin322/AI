# auto-buy-alert · 操作手册

自动调研美股买点 + 盘中热门10,推送到 Discord(@everyone)。只做美股,数据走 yfinance,
研报推理用本机 headless Claude。**不下单、不碰钱,仅供参考、非投资建议。**

设计文档见 `../docs/superpowers/specs/2026-06-21-auto-buy-alert-design.md`。

## 每天会发生什么(美国西部 PT 时间,周一~周五)

| 时间 | 任务 | 内容 |
|---|---|---|
| 06:00 | PreOpen 盘前 | 自选股买点(叠加隔夜新闻/盘前价),开盘前最终确认 |
| 10:00 | Hot 盘中热门 | 当日最热门 10 只美股 + 逐只"为什么热 + 研判" |
| 13:15 | Close 盘后 | 基于当日收盘的买点候选 |
| 17:00 | Funds 基金追踪 | Cathie Wood/ARK 每日买卖 + Aschenbrenner 13F(季度)→ **funds 频道** |
| 开机+2min | Catchup 补跑 | 若关机错过了某次,开机后补跑最近一次(仅买点/热门) |

- 真实买点提醒 + 热门10 会 **@everyone** 提醒你;"今日无信号"简讯不 @。
- 买点提醒只在**有候选**时才唤起 Claude(省 token);没信号的日子由脚本直接发简讯。

## 基金追踪(funds 频道)

`fund_tracker.py`(纯 Python,不用 Claude),每交易日 17:00 PT 跑,推送到独立的 funds 频道:

- **Cathie Wood / ARK**:每天下载 6 只 ARK ETF 持仓 CSV,与昨日比对 → 精确的**每日买入/卖出**(新建仓/增持/减持/清仓)。
- **Leopold Aschenbrenner / Situational Awareness LP**(CIK 0002045724):监控 SEC EDGAR 的 **13F** 备案;每出一份新 13F(**季度披露、滞后约 45 天**,对冲基金的法定上限)就与上一季比对 → 买卖变动。无新备案的日子只报"无变动 + 当前前5"。
- 状态存 `fund_state/`;**funds 频道不 @everyone**(安静推送)。看板"基金追踪"区显示最新 13F 日期/持仓数/前5 与 ARK 数据日期。
- 注:**不可能做到对 Aschenbrenner 的"每日"追踪** —— 对冲基金不披露日内交易,13F 季度披露是公开数据的极限。

## 前提
- 到点时**电脑要开机并已登录**(睡眠可被唤醒;**关机**则等下次开机由 Catchup 补跑)。
- 能联网(访问 Yahoo Finance + Discord + Claude)。

## 状态看板(查引擎在不在线)

本地仪表盘,显示 4 个任务是否在岗、最近运行结果/下次运行、今日各时段是否已跑,
以及一键「现在实测」连通性(Claude / Yahoo / Discord,只探测、不发消息、不花 token)。

- **地址**:http://127.0.0.1:8642 (仅本机可见)
- 看板还显示:**监视清单**(Charles 等,改 `watchlists.json` 可加新清单)、**贪婪指数**(美股+BTC)
- **打开**:双击 `open-dashboard.bat`(没启动会自动拉起服务再打开)
- **自启**:`AutoBuyAlert-Dashboard` 任务在你**登录时自动启动**服务,平时直接开浏览器访问即可
- 服务端 `status_server.py`,页面 `dashboard.html`(想改样式直接编辑)

## 常用操作

**手动跑一次(测试):**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File E:\data\finance\auto-buy-alert\run_alert.ps1 -Session hot
# -Session 可选 close | preopen | hot | catchup
```
或在「任务计划程序」里右键对应任务 → 运行。

**改自选股:** 编辑 `watchlist.txt`(每行一个代码;比特币用 `BTC-USD`)。

**改时间:** 任务计划程序里改对应任务的触发器;或重新运行注册脚本。

**改 Discord 频道:** 编辑 `.env` 里的 `DISCORD_WEBHOOK_URL`。

**看日志:** `run.log`(每次运行的记录)。中间产物:`_screen.json` / `_hot.json`。
去重/补跑状态:`state.json`(信号去重)、`last_run.json`(每日各 session 是否已跑)。

**临时关闭 / 重新开启:**
```powershell
Get-ScheduledTask AutoBuyAlert-* | Disable-ScheduledTask
Get-ScheduledTask AutoBuyAlert-* | Enable-ScheduledTask
```

**彻底删除:**
```powershell
Get-ScheduledTask AutoBuyAlert-* | Unregister-ScheduledTask -Confirm:$false
```

## 文件
| 文件 | 作用 |
|---|---|
| `screen.py` | 技术面买点初筛(确定性:趋势/RSI/均线回踩/量能) |
| `hot_list.py` | 盘中热门10综合榜(成交活跃 + 涨跌异动) |
| `indicators.py` | RSI / SMA 指标 |
| `notify.py` | 发 Discord(`--mention` 即 @everyone;`--dry-run` 只打印不发) |
| `run_routine.md` | Claude 每次运行照做的例程指令 |
| `run_alert.ps1` | 计划任务调用的总控(补跑/幂等/省token/调 Claude) |
| `watchlist.txt` / `.env` | 自选股 / 密钥 |

## 调参(在 `screen.py` 顶部)
- `OVERSOLD_RSI`(默认 35)：RSI 超跌阈值,调高=更宽松、更多信号。
- `NEAR_SUPPORT_HIGH`(默认 0.03)：回踩均线的容差(3%)。
- `VOL_SPIKE_MULT`(默认 2.5)：放量破位的过滤倍数。
- 每次 Claude 调用成本上限:`run_alert.ps1` 里 `$MaxBudgetUsd`(默认 $2.0/次)。

## 已知限制
- **美股节假日**:休市日数据不新鲜;盘后会自动判 `stale` 跳过,盘前/热门可能基于上一交易日数据(无害)。
- **yfinance** 偶发限流;如频繁失败可换数据源(stooq / Alpha Vantage),只需改 `screen.py`/`hot_list.py` 取数层。
- 不构成投资建议;请自行判断与风控。
