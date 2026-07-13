# drift-detect.ps1 — 编码后检测契约/文档漂移（V5.0 新增）
# PostToolUse Hook: 编码后强制检测漂移

$contractsDir = "docs/specs/changes"
$driftFound = $false
$driftReport = @()

# 简化版漂移检测：检查 contracts/ 中的接口是否在代码中有实现
if (Test-Path $contractsDir) {
    Get-ChildItem -Path $contractsDir -Recurse -Filter "api-contracts.md" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        # 提取接口路径（简化版，实际可用正则）
        $paths = [regex]::Matches($content, '##\s+(GET|POST|PUT|PATCH|DELETE)\s+(/\S+)')
        foreach ($path in $paths) {
            $method = $path.Groups[1].Value
            $route = $path.Groups[2].Value
            # 在 src/ 下搜索对应路由实现（简化版）
            $routePattern = $route -replace ":\w+", "[^/]+"
            $codeMatch = Get-ChildItem -Path "src" -Recurse -Include "*.ts","*.tsx" -ErrorAction SilentlyContinue |
                Select-String -Pattern $routePattern -SimpleMatch:$false -ErrorAction SilentlyContinue
            if (-not $codeMatch) {
                $driftFound = $true
                $driftReport += "🔴 契约漂移: $method $route 在代码中未找到实现"
            }
        }
    }
}

if ($driftFound) {
    Write-Host "📊 DRIFT DETECT: 发现契约漂移"
    $driftReport | ForEach-Object { Write-Host "   $_" }
    Write-Host "   详见 references/feedback-loop.md"
    # 不阻断，但警告（reviewer 会强制检查）
    exit 0
} else {
    Write-Host "✅ DRIFT DETECT: 无契约漂移"
    exit 0
}
