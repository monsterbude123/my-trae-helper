<#
.SYNOPSIS
  检查 docsify-cli 环境，按需安装。

.DESCRIPTION
  检测系统中是否已安装 docsify-cli。
  未安装时自动通过 npm 全局安装。
  安装失败时给出明确的修复指引。

.EXAMPLE
  .trae/skills/docsify-doc-builder/scripts/check-env.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "`n[环境检查] 检测 docsify-cli..." -ForegroundColor Cyan

# ── 检测 Node.js ──
try {
    $nodeVer = node --version 2>$null
    if (-not $nodeVer) { throw "node 未返回版本号" }
    Write-Host "  ✅ Node.js: $nodeVer" -ForegroundColor Green
}
catch {
    Write-Host "  ❌ Node.js 未安装！" -ForegroundColor Red
    Write-Host ""
    Write-Host "  ── 安装指引 ──" -ForegroundColor Yellow
    Write-Host "  1. 访问 https://nodejs.org/ 下载 LTS 版本"
    Write-Host "  2. 安装后重新打开终端"
    Write-Host "  3. 重新运行此脚本"
    Write-Host "  ──────────────" -ForegroundColor Yellow
    exit 1
}

# ── 检测 npm ──
try {
    $npmVer = npm --version 2>$null
    if (-not $npmVer) { throw "npm 未返回版本号" }
    Write-Host "  ✅ npm: $npmVer" -ForegroundColor Green
}
catch {
    Write-Host "  ❌ npm 未安装！" -ForegroundColor Red
    exit 1
}

# ── 检测/安装 docsify-cli ──
try {
    $docsifyVer = docsify --version 2>$null
    if ($docsifyVer) {
        Write-Host "  ✅ docsify-cli: $docsifyVer" -ForegroundColor Green
    }
    else {
        throw "未检测到 docsify"
    }
}
catch {
    Write-Host "  ⏳ docsify-cli 未安装，正在通过 npm 全局安装..." -ForegroundColor Yellow
    try {
        npm install -g docsify-cli
        $newVer = docsify --version 2>$null
        if ($newVer) {
            Write-Host "  ✅ docsify-cli 安装成功: $newVer" -ForegroundColor Green
        }
        else {
            throw "安装后仍无法运行"
        }
    }
    catch {
        Write-Host "  ❌ 安装失败！请手动执行:" -ForegroundColor Red
        Write-Host "     npm install -g docsify-cli" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`n[环境检查] 全部通过！" -ForegroundColor Green
