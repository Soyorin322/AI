# 打开 auto-buy-alert 状态看板;若本地服务没在跑,先把它拉起来。
$url = "http://127.0.0.1:8642"
$pyw = "C:\Users\hongy\anaconda3\pythonw.exe"
if (-not (Test-Path $pyw)) { $pyw = "C:\Users\hongy\anaconda3\python.exe" }
$srv = "E:\data\finance\auto-buy-alert\status_server.py"

$up = $false
try { Invoke-WebRequest "$url/api/status" -TimeoutSec 2 -UseBasicParsing | Out-Null; $up = $true } catch {}
if (-not $up) {
  Start-Process -FilePath $pyw -ArgumentList $srv -WindowStyle Hidden
  Start-Sleep -Seconds 2
}
Start-Process $url
