# contract-gate.ps1 — 编码前检查契约文件存在（V5.0 新增）
# PreToolUse Hook: 写代码前强制检查 contracts/ 已 approved

$changeDir = "docs/specs/changes"
$contractsFound = $false

# 查找活跃变更的 contracts 目录
if (Test-Path $changeDir) {
    Get-ChildItem -Path $changeDir -Directory | ForEach-Object {
        $contractPath = Join-Path $_.FullName "contracts"
        if (Test-Path $contractPath) {
            $contractsFound = $true
            # 检查 api-contracts.md 是否存在
            $apiContract = Join-Path $contractPath "api-contracts.md"
            if (-not (Test-Path $apiContract)) {
                Write-Host "🛑 CONTRACT GATE: api-contracts.md 缺失于 $contractPath"
                Write-Host "   协议先行铁律：编码前契约必须 approved"
                exit 1
            }
            # 检查契约状态是否 approved
            $content = Get-Content $apiContract -Raw
            if ($content -match "状态:\s*(draft|review)") {
                Write-Host "🛑 CONTRACT GATE: 契约状态未 approved ($apiContract)"
                exit 1
            }
        }
    }
}

if ($contractsFound) {
    Write-Host "✅ CONTRACT GATE: 契约已 approved，可以编码"
} else {
    Write-Host "🛑 CONTRACT GATE: 未找到 contracts/ 目录"
    Write-Host "   协议先行铁律：编码前契约必须存在并 approved"
    Write-Host "   请走 fullstack-contract-writer 阶段产出 contracts/"
    exit 1
}
