<#
.SYNOPSIS
  启动 docsify 开发服务器。

.DESCRIPTION
  在 docs/ 目录上启动 docsify serve，默认端口 3000。
  支持通过环境变量 DOCSIFY_PORT 自定义端口。
  支持热更新：编辑 docs/ 下的 .md 文件后浏览器自动刷新。

.PARAMETER Port
  服务器端口（可选）。默认 3000。
  优先级：参数 > 环境变量 DOCSIFY_PORT > 默认值

.PARAMETER NoOpen
  不自动打开浏览器。默认自动打开。

.EXAMPLE
  .trae/skills/docsify-doc-builder/scripts/serve.ps1

.EXAMPLE
  $env:DOCSIFY_PORT=4000; .trae/skills/docsify-doc-builder/scripts/serve.ps1

.EXAMPLE
  .trae/skills/docsify-doc-builder/scripts/serve.ps1 -Port 8080 -NoOpen
#>

param(
    [int]$Port = 0,
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

$docsDir = Join-Path (Get-Location) "docs"

# ── 端口配置 ──
if ($Port -le 0) {
    $envPort = [int]($env:DOCSIFY_PORT)
    if ($envPort -gt 0) {
        $Port = $envPort
    }
    else {
        $Port = 3000
    }
}

# ── 检查 docs/ 目录 ──
if (-not (Test-Path $docsDir)) {
    Write-Host "  ❌ docs/ 目录不存在！请先运行 init-docs.ps1" -ForegroundColor Red
    exit 1
}

# ── 检查 docsify-cli ──
try {
    $ver = docsify --version 2>$null
    if (-not $ver) { throw "未检测到 docsify" }
}
catch {
    Write-Host "  ❌ docsify-cli 未安装！请先运行 check-env.ps1" -ForegroundColor Red
    exit 1
}

# ── 启动服务器 ──
Write-Host "`n[文档服务] 启动中..." -ForegroundColor Cyan
Write-Host "  目录: $docsDir" -ForegroundColor White
Write-Host "  端口: $Port" -ForegroundColor White
Write-Host "  热更新: 已启用（编辑 .md 文件后浏览器自动刷新）" -ForegroundColor White
Write-Host ""

# 自动打开浏览器
if (-not $NoOpen) {
    $url = "http://localhost:$Port"
    Start-Process $url
    Write-Host "  🌐 浏览器已自动打开: $url" -ForegroundColor Green
}

Write-Host "  按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

# 启动 docsify serve
docsify serve "$docsDir" --port $Port
