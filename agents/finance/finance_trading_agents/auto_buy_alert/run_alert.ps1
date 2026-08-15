<#
auto-buy-alert · scheduler wrapper.

Called by Windows Task Scheduler, e.g.:
  powershell -NoProfile -ExecutionPolicy Bypass -File E:\data\finance\auto-buy-alert\run_alert.ps1 -Session close

Flow: run the deterministic Python first; invoke Claude (headless) only when there is
something to analyze (any buy candidate, or the hot session). Idempotent via
last_run.json so a catch-up run never double-sends a session already completed today.

Sessions: close | preopen | hot | catchup
  catchup (boot/logon) resolves to the single most-recent missed session for today.
#>
param(
  [ValidateSet("close", "preopen", "hot", "catchup")]
  [string]$Session = "close"
)

# 'Continue' (not 'Stop'): native tools like claude/python write harmless warnings to
# stderr; under 'Stop' PowerShell would treat those as fatal and abort the run.
$ErrorActionPreference = "Continue"
$Proj = "E:\data\finance"
$Dir  = Join-Path $Proj "auto-buy-alert"
$Log  = Join-Path $Dir  "run.log"
$ClaudeExe = "C:\Users\hongy\.local\bin\claude.exe"
$MaxBudgetUsd = "2.0"   # per-run cost cap for the headless Claude call
Set-Location $Proj

function Log($m) {
  $t = (Get-Date).ToString("s")
  Add-Content -Path $Log -Value "$t [$Session] $m" -Encoding utf8
  Write-Host "$t [$Session] $m"
}
function WriteUtf8($path, $text) {
  [IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding($false)))
}

# --- Eastern Time (Windows tz id auto-handles DST despite the name) ---
function NowET { [System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTime]::UtcNow, 'Eastern Standard Time') }
$et = NowET
$tradeDay  = $et.ToString("yyyy-MM-dd")
$isWeekday = ($et.DayOfWeek -ne 'Saturday' -and $et.DayOfWeek -ne 'Sunday')

# --- last_run.json: per trading-day session completion markers ---
$lastRunPath = Join-Path $Dir "last_run.json"
function LoadLastRun {
  if (Test-Path $lastRunPath) { try { return (Get-Content $lastRunPath -Raw | ConvertFrom-Json) } catch {} }
  return [pscustomobject]@{}
}
function IsDone($lr, $day, $sess) {
  if ($lr.PSObject.Properties.Name -contains $day) {
    $d = $lr.$day
    if ($d.PSObject.Properties.Name -contains $sess) { return ($d.$sess -eq 'done') }
  }
  return $false
}
function MarkDone($day, $sess) {
  $lr = LoadLastRun
  if (-not ($lr.PSObject.Properties.Name -contains $day)) {
    $lr | Add-Member -NotePropertyName $day -NotePropertyValue ([pscustomobject]@{})
  }
  $d = $lr.$day
  if ($d.PSObject.Properties.Name -contains $sess) { $d.$sess = 'done' }
  else { $d | Add-Member -NotePropertyName $sess -NotePropertyValue 'done' }
  $lr | Add-Member -NotePropertyName 'updated_at' -NotePropertyValue ((NowET).ToString("s")) -Force
  WriteUtf8 $lastRunPath ($lr | ConvertTo-Json -Depth 6)
}

# --- wait for network (boot/catch-up may fire before Wi-Fi is up) ---
function WaitNetwork([int]$maxSec = 120) {
  $deadline = (Get-Date).AddSeconds($maxSec)
  while ((Get-Date) -lt $deadline) {
    try {
      $c = New-Object Net.Sockets.TcpClient
      $iar = $c.BeginConnect('1.1.1.1', 443, $null, $null)
      if ($iar.AsyncWaitHandle.WaitOne(3000) -and $c.Connected) { $c.Close(); return $true }
      $c.Close()
    } catch {}
    Start-Sleep -Seconds 3
  }
  return $false
}

# --- resolve effective session ---
$eff = $Session
$catchup = $false
if ($Session -eq 'catchup') {
  if (-not $isWeekday) { Log "weekend - nothing to catch up"; exit 0 }
  $lr = LoadLastRun
  $etH = $et.Hour + $et.Minute / 60.0
  $missed = @()
  if ($etH -ge 9.0   -and -not (IsDone $lr $tradeDay 'preopen')) { $missed += 'preopen' }
  if ($etH -ge 13.0  -and -not (IsDone $lr $tradeDay 'hot'))     { $missed += 'hot' }
  if ($etH -ge 16.25 -and -not (IsDone $lr $tradeDay 'close'))   { $missed += 'close' }
  if ($missed.Count -eq 0) { Log "no missed session for $tradeDay"; exit 0 }
  foreach ($s in @('close', 'hot', 'preopen')) { if ($missed -contains $s) { $eff = $s; break } }
  $catchup = $true
  Log "catch-up resolves to '$eff' (missed: $($missed -join ','))"
}

if (IsDone (LoadLastRun) $tradeDay $eff) { Log "$eff already done for $tradeDay - skip"; exit 0 }

WaitNetwork 120 | Out-Null

$label = switch ($eff) { 'close' { '盘后' } 'preopen' { '盘前' } 'hot' { '盘中' } default { '盘后' } }
if ($catchup) { $label = "$label·补跑" }

# Tools allow-list keeps the headless run from ever pausing on a permission prompt.
function InvokeClaude($sess) {
  $prompt = "Execute the auto-buy-alert routine now, non-interactively. SESSION=$sess. " +
            "SESSION_LABEL=$label. Read auto-buy-alert\run_routine.md and follow it exactly. " +
            "Pre-generated data is in auto-buy-alert\_screen.json (buy) or auto-buy-alert\_hot.json (hot). " +
            "Do not ask questions; complete and send the Discord message."
  Log "invoking claude (SESSION=$sess)"
  # Pipe empty stdin so claude doesn't wait 3s for piped input and warn.
  '' | & $ClaudeExe -p $prompt --permission-mode acceptEdits --max-budget-usd $MaxBudgetUsd `
      --allowedTools "Bash" "WebSearch" "WebFetch" "Read" "Write" "Glob" "Grep" 2>&1 |
    ForEach-Object { Log "claude> $_" }
}

if ($eff -eq 'hot') {
  $json = & python (Join-Path $Dir 'hot_list.py') --top 10 2>$null | Out-String
  WriteUtf8 (Join-Path $Dir '_hot.json') $json
  InvokeClaude 'hot'
  MarkDone $tradeDay 'hot'
  Log "hot session done"
  exit 0
}

# buy sessions: close / preopen
$json = & python (Join-Path $Dir 'screen.py') --session $eff 2>$null | Out-String
WriteUtf8 (Join-Path $Dir '_screen.json') $json
$rep = $null
try { $rep = $json | ConvertFrom-Json } catch {}
if ($null -eq $rep) { Log "screen.py produced no parseable output - abort (no mark-done so catch-up can retry)"; exit 1 }

if ($eff -eq 'close' -and $rep.stale) {
  $card = @{ summary = "数据非最新(可能休市),本次跳过。"; title = "ℹ️ AutoBuyAlert · $label" }
  WriteUtf8 (Join-Path $Dir '_cards.json') ($card | ConvertTo-Json)
  & python (Join-Path $Dir 'notify.py') --file (Join-Path $Dir '_cards.json') | ForEach-Object { Log $_ }
  MarkDone $tradeDay $eff; Log "stale -> summary sent"; exit 0
}

if ([int]$rep.n_candidates -eq 0) {
  $card = @{ summary = "今日无买点信号($label)— 自选股均未满足回调买点。"; title = "ℹ️ AutoBuyAlert · $label" }
  WriteUtf8 (Join-Path $Dir '_cards.json') ($card | ConvertTo-Json)
  & python (Join-Path $Dir 'notify.py') --file (Join-Path $Dir '_cards.json') | ForEach-Object { Log $_ }
  MarkDone $tradeDay $eff; Log "no candidates -> summary sent"; exit 0
}

# candidates exist -> Claude researches news, composes cards, sends
InvokeClaude $eff
MarkDone $tradeDay $eff
Log "buy session done ($($rep.n_candidates) candidates)"
