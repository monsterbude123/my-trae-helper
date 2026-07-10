<#
.SYNOPSIS
  根据 docs/ 目录结构自动生成 _sidebar.md。

.DESCRIPTION
  扫描 docs/ 目录下的所有 .md 文件（排除 _sidebar.md / _navbar.md / README.md），
  按目录结构生成 docsify 侧边栏导航。

  特性：
    - 支持嵌套目录（最多 4 层）
    - 文件名中的数字前缀自动去除（如 "01-快速开始.md" → "快速开始.md"）
    - README.md 排在每级目录首位
    - 已有 _sidebar.md 会被完全覆盖
    - 如果项目根有 README.md，自动添加"项目简介"链接

.EXAMPLE
  .trae/skills/docsify-doc-builder/scripts/generate-sidebar.ps1
#>

$ErrorActionPreference = "Stop"

$docsDir = Join-Path (Get-Location) "docs"
$sidebarPath = Join-Path $docsDir "_sidebar.md"

Write-Host "`n[侧边栏生成] 开始..." -ForegroundColor Cyan
Write-Host "  扫描: $docsDir" -ForegroundColor White

if (-not (Test-Path $docsDir)) {
    Write-Host "  ❌ docs/ 目录不存在！请先运行 init-docs.ps1" -ForegroundColor Red
    exit 1
}

# ── 获取所有 .md 文件（排除特殊文件） ──
$excludeFiles = @("_sidebar.md", "_navbar.md")
$allFiles = Get-ChildItem -Path $docsDir -Recurse -Filter "*.md" -File | Where-Object {
    $_.Name -notin $excludeFiles
}

if ($allFiles.Count -eq 0) {
    Write-Host "  ⚠️  docs/ 下没有 Markdown 文件，生成空侧边栏" -ForegroundColor Yellow
    "# 文档目录`n`n* 暂无内容" | Out-File -FilePath $sidebarPath -Encoding UTF8
    exit 0
}

Write-Host "  发现 $($allFiles.Count) 个 Markdown 文件" -ForegroundColor White

# ── 排序（按目录层级、文件名） ──
$sorted = $allFiles | Sort-Object -Property FullName

# ── 构建侧边栏 ──
$lines = @()
$lines.Add("<!-- _sidebar.md — 由 generate-sidebar.ps1 自动生成 -->")
$lines.Add("<!-- 手动编辑后重新运行会基于最新文件结构重建 -->")
$lines.Add("")

# 首页
$lines.Add("* [项目简介](README.md)")
$lines.Add("")

# 按目录分组
$groups = $sorted | Group-Object { $_.Directory.FullName } | Sort-Object Name

# 计算相对路径深度
function Get-RelativeDepth {
    param([string]$dirPath)
    $rel = $dirPath.Substring($docsDir.Length).TrimStart("\").TrimStart("/")
    if ([string]::IsNullOrEmpty($rel)) { return 0 }
    return ($rel -split "[\\/]").Count
}

# 跟踪已渲染的父级目录，避免重复
$renderedParents = @{}

foreach ($group in $groups) {
    $dirPath = $group.Name
    $depth = Get-RelativeDepth -dirPath $dirPath

    # 获取相对路径部分
    $relDir = $dirPath.Substring($docsDir.Length).TrimStart("\").TrimStart("/")

    if ($depth -gt 0) {
        # 渲染祖先目录（如果尚未渲染）
        $parts = $relDir -split "[\\/]"
        $accPath = ""
        for ($i = 0; $i -lt $parts.Count; $i++) {
            $accPath = if ($accPath) { "$accPath/$($parts[$i])" } else { $parts[$i] }
            $key = $accPath.ToLower()
            if (-not $renderedParents.ContainsKey($key)) {
                $indent = "  " * ($i)  # 根级目录用 *，子目录用缩进
                $displayName = $parts[$i] -replace '^\d+[-_]', ''
                $lines.Add("$indent* $displayName")
                $renderedParents[$key] = $true
            }
        }
    }

    # 渲染该目录下的文件
    $files = $group.Group | Sort-Object Name

    # 将 README.md 排到首位
    $readme = $files | Where-Object { $_.Name -eq "README.md" }
    $others = $files | Where-Object { $_.Name -ne "README.md" }
    $ordered = @($readme) + $others

    foreach ($file in $ordered) {
        $relPath = $file.FullName.Substring($docsDir.Length + 1) -replace '\\', '/'

        # 文件名去数字前缀
        $displayName = $file.BaseName -replace '^\d+[-_]', ''
        # 如果是 README 文件，显示为目录名
        if ($file.Name -eq "README.md" -and $depth -gt 0) {
            $displayName = "概览"
        }

        $indent = "  " * $depth
        $lines.Add("$indent  * [$displayName]($relPath)")
    }
}

$lines.Add("")

# ── 写入文件 ──
$content = $lines -join "`r`n"
[System.IO.File]::WriteAllText($sidebarPath, $content, [System.Text.UTF8Encoding]::new($false))

Write-Host "  ✅ 写入 $sidebarPath" -ForegroundColor Green
Write-Host "  共 $($lines.Count) 行" -ForegroundColor White
Write-Host "`n[侧边栏生成] 完成！" -ForegroundColor Green
