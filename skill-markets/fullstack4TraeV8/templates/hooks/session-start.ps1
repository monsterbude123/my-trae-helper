# fullstack SessionStart Hook: 注入项目上下文
# 会话创建后自动执行，向 AI 注入项目结构、活跃变更、模块文档索引

$projectRoot = Get-Location

Write-Output "[Fullstack Project Context]"
Write-Output "- Project Root: $projectRoot"

# 1. 检测活跃变更
$changesDir = Join-Path $projectRoot "docs/specs/changes"
if (Test-Path $changesDir) {
    $activeChanges = Get-ChildItem -Directory $changesDir -ErrorAction SilentlyContinue
    if ($activeChanges) {
        Write-Output "- Active Changes:"
        foreach ($change in $activeChanges) {
            $proposal = Join-Path $change.FullName "proposal.md"
            $tasks = Join-Path $change.FullName "tasks.md"
            $hasProposal = Test-Path $proposal
            $hasTasks = Test-Path $tasks
            if ($hasProposal -or $hasTasks) {
                # Count completed tasks
                $completed = 0; $total = 0
                if ($hasTasks) {
                    $content = Get-Content $tasks -Raw
                    $total = ([regex]::Matches($content, '- \[[ x]\]')).Count
                    $completed = ([regex]::Matches($content, '- \[x\]')).Count
                }
                $status = if ($hasProposal -and $hasTasks) { "in-progress" } elseif ($hasProposal) { "proposal-only" } else { "unknown" }
                Write-Output "  - $($change.Name): $status ($completed/$total tasks done)"
            }
        }
    } else {
        Write-Output "- Active Changes: none"
    }
} else {
    Write-Output "- Active Changes: none (docs/specs/changes/ not found)"
}

# 2. 检测模块文档
$modulesDir = Join-Path $projectRoot "docs/modules"
if (Test-Path $modulesDir) {
    $modules = Get-ChildItem $modulesDir -Filter "*.md" -ErrorAction SilentlyContinue
    if ($modules) {
        Write-Output "- Module Documents:"
        foreach ($mod in $modules) {
            Write-Output "  - docs/modules/$($mod.Name)"
        }
    } else {
        Write-Output "- Module Documents: none"
    }
} else {
    Write-Output "- Module Documents: none (docs/modules/ not found)"
}

# 3. 检测 CODEMAPS
$codemapsDir = Join-Path $projectRoot "docs/CODEMAPS"
if (Test-Path $codemapsDir) {
    $maps = Get-ChildItem $codemapsDir -Filter "*.md" -ErrorAction SilentlyContinue
    if ($maps) {
        Write-Output "- CODEMAPS: $($maps.Count) files"
    }
}

# 4. 检测配置
$configFile = Join-Path $projectRoot "docs/specs/config.yaml"
if (Test-Path $configFile) {
    Write-Output "- Config: docs/specs/config.yaml (present)"
} else {
    Write-Output "- Config: docs/specs/config.yaml (MISSING - run planner to generate)"
}

# 5. 检测测试框架
$hasJest = Test-Path (Join-Path $projectRoot "jest.config.*")
$hasVitest = Test-Path (Join-Path $projectRoot "vitest.config.*")
$hasPytest = Test-Path (Join-Path $projectRoot "pytest.ini") -or Test-Path (Join-Path $projectRoot "pyproject.toml")
if ($hasJest -or $hasVitest -or $hasPytest) {
    Write-Output "- Test Framework: detected"
}

Write-Output ""

# 6. V7.1 NEW: Render cockpit via Python script
$cockpitScript = Join-Path $projectRoot ".trae/hooks/render-cockpit.py"
if (Test-Path $cockpitScript) {
    python $cockpitScript --project-root $projectRoot
} else {
    $skillScript = Join-Path "$env:USERPROFILE\.trae-cn\skills\fullstack4traev8\templates\scripts" "render-cockpit.py"
    if (Test-Path $skillScript) {
        python $skillScript --project-root $projectRoot
    } else {
        Write-Output "[Cockpit] render-cockpit.py not found. Run 'python env-init.py --fix' to install."
    }
}

Write-Output ""

# 7. V9 NEW: 产出 Hook 执行日志（自证生效）
$logDir = Join-Path $projectRoot ".trae/logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}
$logFile = Join-Path $logDir "hook-session-start-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$sessionSummary = @"
[Hook: session-start] $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Status: EXECUTED
Project: $projectRoot
Active Changes: $($activeChanges.Count)
Modules: $($modules.Count)
Cockpit: $((Test-Path $cockpitScript) ? "RENDERED" : "NOT_FOUND")

"@
$sessionSummary | Out-File -FilePath $logFile -Encoding utf8
Write-Output "[Hook] Log: $logFile"
