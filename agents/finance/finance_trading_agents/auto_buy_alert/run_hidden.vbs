' Hidden launcher for AutoBuyAlert scheduled tasks — runs run_alert.ps1 with
' no console window (window style 0), so the tasks never flash a CMD/PowerShell
' window on the desktop. Usage:  wscript run_hidden.vbs <session>
Option Explicit
Dim sh, session, cmd
Set sh = CreateObject("WScript.Shell")
session = "close"
If WScript.Arguments.Count > 0 Then session = WScript.Arguments(0)
cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File " & _
      """E:\data\finance\auto-buy-alert\run_alert.ps1"" -Session " & session
' 0 = hidden window, False = don't wait for it to finish
sh.Run cmd, 0, False
