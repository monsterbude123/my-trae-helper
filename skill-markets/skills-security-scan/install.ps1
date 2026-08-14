# skills-security-scan install.ps1 — DEPRECATED 2026-08-14
# 已并入 trae-security-review。改用：
#   node $env:MY_TRAE_HELPER\bin\cli.mjs add trae-security-review -a trae-cn

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "[DEPRECATED] skills-security-scan 已并入 trae-security-review。" -ForegroundColor Yellow
Write-Host "请改用：" -ForegroundColor Yellow
Write-Host "  node `$env:MY_TRAE_HELPER\bin\cli.mjs add trae-security-review -a trae-cn" -ForegroundColor Yellow
exit 64