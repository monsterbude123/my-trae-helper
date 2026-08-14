[CmdletBinding()]
param(
    [switch]$Uninstall
)

# trae-prompt-logger.install.ps1 — 一键把 UserPromptSubmit Hook 注册到 TRAE 全局配置
#
# 行为:
#   1. 备份现有 %userprofile%/.trae-cn/hooks.json(若存在)
#   2. 合并写入 UserPromptSubmit 事件,command 指向本仓库 scripts/trae-prompt-logger.mjs
#   3. 若已存在 trae-prompt-logger,先移除再追加(避免重复)
#   4. 修复已损坏的 hooks.json(旧版本安装残留的对象/数组嵌套污染)
#
# 运行(管理员或普通用户均可,只写当前用户配置):
#   powershell -ExecutionPolicy Bypass -File scripts/trae-prompt-logger.install.ps1
#
# 卸载:
#   powershell -ExecutionPolicy Bypass -File scripts/trae-prompt-logger.install.ps1 -Uninstall
#
# 注意:
#   - 此文件需 UTF-8 BOM(PowerShell 5.1 -File 模式识别 UTF-8 的唯一方式)
#   - 变量名避开 PowerShell 自动变量($script / $global 等)避免解析歧义
#   - [CmdletBinding()] 必须在 param 块前且紧跟 BOM(不能有注释行)
#   - JSON 操作委托给 Node 脚本(避免 PowerShell 5 的 ConvertFrom-Json/ConvertTo-Json 单元素数组降级陷阱)

$ErrorActionPreference = 'Stop'

# ─── 路径 ─────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LoggerScript = Join-Path $ScriptDir 'trae-prompt-logger.mjs'
$LoggerScript = (Resolve-Path $LoggerScript).Path

# 委托给 Node 处理 JSON(零依赖、稳健)
$JsonHelper = Join-Path $ScriptDir 'trae-prompt-logger.install.mjs'

$traeDir = Join-Path $env:USERPROFILE '.trae-cn'
$hookFile = Join-Path $traeDir 'hooks.json'

# 标记: 我们的钩子通过 command 路径前缀识别
$MARKER = 'trae-prompt-logger'

# ─── 工具 ─────────────────────────────────────────────

# 调用 Node JSON helper 读取并改写 hooks.json
# 操作类型: 'install' | 'uninstall'
function Invoke-JsonHelper {
    param(
        [string]$Operation  # 'install' or 'uninstall'
    )
    $args = @(
        $JsonHelper,
        '--op', $Operation,
        '--file', $hookFile,
        '--script', $LoggerScript,
        '--marker', $MARKER
    )
    $output = & node @args 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Node helper 失败: $output"
    }
    return $output
}

# ─── 1. 校验前置 ─────────────────────────────────────

# 校验 Node 可用
$nodeCheck = & node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ 未检测到 Node.js,请先安装 Node 18+ 后再运行"
    exit 1
}
Write-Host "✅ Node: $nodeCheck"

if (-not (Test-Path -LiteralPath $LoggerScript)) {
    Write-Error "❌ 找不到脚本: $LoggerScript"
    exit 1
}
Write-Host "✅ Logger 脚本: $LoggerScript"

if (-not (Test-Path -LiteralPath $JsonHelper)) {
    Write-Error "❌ 找不到 JSON helper: $JsonHelper"
    exit 1
}
Write-Host "✅ JSON helper: $JsonHelper"

# 确保 ~/.trae-cn 目录
if (-not (Test-Path -LiteralPath $traeDir)) {
    New-Item -ItemType Directory -Path $traeDir -Force | Out-Null
    Write-Host "✅ 创建目录: $traeDir"
}

# 备份现有 hooks.json(若存在)
if (Test-Path -LiteralPath $hookFile) {
    $backup = "$hookFile.bak.$(Get-Date -Format 'yyyyMMddHHmmss')"
    Copy-Item -LiteralPath $hookFile -Destination $backup
    Write-Host "✅ 备份现有配置: $backup"
}

# ─── 2. 执行操作 ─────────────────────────────────────

if ($Uninstall) {
    $output = Invoke-JsonHelper -Operation 'uninstall'
    Write-Host $output
    Write-Host "✅ 已卸载 trae-prompt-logger Hook" -ForegroundColor Green
} else {
    $output = Invoke-JsonHelper -Operation 'install'
    Write-Host $output
    Write-Host "✅ 已注册 UserPromptSubmit Hook" -ForegroundColor Green
    Write-Host "   配置: $hookFile"
    Write-Host "   命令: node `"$LoggerScript`""
    Write-Host ""
    Write-Host "📁 落盘路径(每个项目内):"
    Write-Host "   <项目根>/.trae/prompt-logs/sessions/<session_id>/prompts.ndjson"
    Write-Host "   <项目根>/.trae/prompt-logs/index.ndjson"
    Write-Host ""
    Write-Host "🧪 验证: 在 TraeCode 中发送任意消息,检查目标项目的 .trae/prompt-logs/ 目录"
    Write-Host "🗑️  卸载: powershell -File $PSCommandPath -Uninstall"
}
