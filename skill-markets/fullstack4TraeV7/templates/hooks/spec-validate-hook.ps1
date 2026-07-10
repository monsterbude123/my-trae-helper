# fullstack Spec Validate Hook
# 写 spec.md 后自动校验格式（WHEN-THEN-AND + SHALL + L0-L4 编号）
# 从 PostToolUse 触发，仅处理 spec.md 文件

param(
    [string]$file_path = $env:TRAE_FILE_PATH
)

# 只处理 spec.md 文件
if ($file_path -notmatch 'specs/.*/spec\.md$') {
    exit 0
}

if (-not (Test-Path $file_path)) {
    Write-Output "[Fullstack Spec Validate] File not found: $file_path"
    exit 1
}

$content = Get-Content $file_path -Raw
$issues = @()

# 1. 检查 L0-L4 编号
if ($content -notmatch '>\s*L[0-4]-\d{3}') {
    $issues += "缺少 L0-L4 段位编号（如 > L0-051）"
}

# 2. 检查 WHEN 关键字
if ($content -notmatch '\*\*WHEN\b') {
    $issues += "缺少 **WHEN** 关键字"
}

# 3. 检查 THEN 关键字
if ($content -notmatch '\*\*THEN\b') {
    $issues += "缺少 **THEN** 关键字"
}

# 4. 检查 SHALL 契约
if ($content -notmatch '\bSHALL\b') {
    $issues += "未使用 SHALL 表达契约（用 SHALL / SHALL NOT 替代模糊的'应该''可以'）"
}

# 5. 检查 Requirement
if ($content -notmatch '### Requirement:') {
    $issues += "缺少 Requirement 定义"
}

if ($issues.Count -gt 0) {
    Write-Output "[Fullstack Spec Validate] FAILED for $file_path :"
    foreach ($issue in $issues) {
        Write-Output "  - $issue"
    }
    exit 1
}

# 6. Prototypes/ 存在性校验（V10 NEW — 涉及 UI 的 spec 必须有原型）
#    spec 路径: docs/specs/changes/{change}/specs/{capability}/spec.md
#    prototypes 路径: docs/specs/changes/{change}/prototypes/
$uiKeywords = @('页面', '界面', 'UI', '前端', '按钮', '表单', '组件', 'component', 'page', 'screen', '视图', '对话框', '弹窗', 'Panel', 'Modal', 'Table', 'Form', 'Dashboard')
$hasUI = $false
foreach ($kw in $uiKeywords) {
    if ($content -match $kw) {
        $hasUI = $true
        break
    }
}

if ($hasUI) {
    # 从 spec 路径提取 change 目录: docs/specs/changes/{change}/
    if ($file_path -match 'docs/specs/changes/([^/]+)/') {
        $changeName = $matches[1]
        $prototypesDir = "docs/specs/changes/$changeName/prototypes"
        
        if (-not (Test-Path $prototypesDir)) {
            Write-Output "[Fullstack Spec Validate] 🛑 FAILED: spec 涉及 UI 但 prototypes/ 目录不存在"
            Write-Output "   Change: $changeName"
            Write-Output "   Expected: $prototypesDir/"
            Write-Output "   铁律: 涉及 UI 的 spec 必须产出 prototypes/（V5.1）"
            Write-Output "   Action: spec-writer 执行步骤 3.7 产出原型文档"
            exit 1
        }
        
        # 检查 prototypes/ 是否为空目录
        $protoFiles = Get-ChildItem -Path $prototypesDir -File -ErrorAction SilentlyContinue
        if (-not $protoFiles -or $protoFiles.Count -eq 0) {
            Write-Output "[Fullstack Spec Validate] 🛑 FAILED: prototypes/ 目录存在但为空"
            Write-Output "   Path: $prototypesDir/"
            Write-Output "   至少需要一个原型文件 + README.md 索引"
            exit 1
        }
        
        # 检查是否有 README.md 索引
        $readmePath = Join-Path $prototypesDir "README.md"
        if (-not (Test-Path $readmePath)) {
            Write-Output "[Fullstack Spec Validate] ⚠️ WARNING: prototypes/ 缺少 README.md 索引"
            Write-Output "   Expected: $readmePath"
            Write-Output "   建议补上 prototypes/README.md"
            # 不阻断，但记录 warning
        }
    }
}

Write-Output "[Fullstack Spec Validate] PASSED for $file_path"
exit 0
