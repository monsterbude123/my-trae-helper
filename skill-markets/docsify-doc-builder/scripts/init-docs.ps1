<#
.SYNOPSIS
  初始化 docsify 文档目录结构和配置。

.DESCRIPTION
  在项目根目录创建 docs/ 文件夹，从技能模板复制所有必要的文件：
    - index.html（docsify 核心配置 + 插件）
    - README.md（首页/项目简介）
    - _sidebar.md（侧边栏导航）
    - _navbar.md（顶部导航栏）
    - custom.css（自定义样式）
    - logo.svg（项目 Logo）

  模板中的 {{PROJECT_NAME}} 和 {{PROJECT_DESCRIPTION}} 会被替换为实际值。

.PARAMETER ProjectName
  项目名称（必填）。可通过 $env:PROJECT_NAME 传入。
  优先级：参数 > 环境变量

.PARAMETER ProjectDescription
  项目描述（可选）。可通过 $env:PROJECT_DESCRIPTION 传入。
  优先级：参数 > 环境变量

.EXAMPLE
  $env:PROJECT_NAME="DeerFlow"; .trae/skills/docsify-doc-builder/scripts/init-docs.ps1

.EXAMPLE
  .trae/skills/docsify-doc-builder/scripts/init-docs.ps1 -ProjectName "MyApp"
#>

param(
    [string]$ProjectName = "",
    [string]$ProjectDescription = ""
)

$ErrorActionPreference = "Stop"

# ── 获取项目名称 ──
if (-not $ProjectName) {
    $ProjectName = $env:PROJECT_NAME
}
if (-not $ProjectName) {
    $ProjectName = Split-Path -Leaf (Get-Location)
    Write-Host "  ℹ️ 未指定项目名，使用当前目录名: $ProjectName" -ForegroundColor Yellow
}

# ── 获取项目描述 ──
if (-not $ProjectDescription) {
    $ProjectDescription = $env:PROJECT_DESCRIPTION
}
if (-not $ProjectDescription) {
    $ProjectDescription = ""
}

# ── 路径配置 ──
$skillRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$templatesDir = Join-Path $skillRoot "templates"
$docsDir = Join-Path (Get-Location) "docs"

Write-Host "`n[文档初始化] 开始..." -ForegroundColor Cyan
Write-Host "  项目: $ProjectName" -ForegroundColor White
Write-Host "  输出: $docsDir" -ForegroundColor White

# ── 创建 docs 目录 ──
if (Test-Path $docsDir) {
    Write-Host "  ℹ️ docs/ 目录已存在，将覆盖同名文件" -ForegroundColor Yellow
}
else {
    New-Item -ItemType Directory -Path $docsDir -Force | Out-Null
    Write-Host "  ✅ 创建 docs/ 目录" -ForegroundColor Green
}

# ── 创建子目录结构 ──
$subDirs = @("基础篇", "进阶篇", "附录")
foreach ($dir in $subDirs) {
    $dirPath = Join-Path $docsDir $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
    }
}
Write-Host "  ✅ 创建文档子目录: $($subDirs -join ', ')" -ForegroundColor Green

# ── 复制模板文件并替换变量 ──
$templateFiles = @(
    "index.html",
    "README.md",
    "_sidebar.md",
    "_navbar.md",
    "custom.css",
    "logo.svg"
)

$fileCount = 0
foreach ($file in $templateFiles) {
    $src = Join-Path $templatesDir $file
    $dst = Join-Path $docsDir $file

    if (Test-Path $src) {
        $content = Get-Content $src -Raw -Encoding UTF8
        $content = $content.Replace("{{PROJECT_NAME}}", $ProjectName)
        $content = $content.Replace("{{PROJECT_DESCRIPTION}}", $ProjectDescription)
        [System.IO.File]::WriteAllText($dst, $content, [System.Text.UTF8Encoding]::new($false))
        $fileCount++
    }
}

Write-Host "  ✅ 复制 $fileCount 个模板文件" -ForegroundColor Green

# ── 创建示例文档 ──
$sampleFiles = @{
    "基础篇/快速开始.md" = @"
# 快速开始

## 安装

```bash
# 安装命令
```

## 使用

```bash
# 使用命令
```
"@
    "基础篇/核心概念.md" = @"
# 核心概念

## 概念一

...

## 概念二

...
"@
    "进阶篇/配置详解.md" = @"
# 配置详解

## 配置项

...
"@
    "基础篇/安装指南.md" = @"
# 安装指南

## 环境要求

- 要求一
- 要求二

## 安装步骤

1. 步骤一
2. 步骤二
"@
    "进阶篇/API参考.md" = @"
# API 参考

## 接口一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/ | 接口说明 |

## 请求示例

```bash
curl https://api.example.com/v1/
```
"@
    "附录/常见问题.md" = @"
# 常见问题 (FAQ)

## Q1: 常见问题一

...

## Q2: 常见问题二

...
"@
    "附录/更新日志.md" = @"
# 更新日志

## v0.1.0 (2024-01-01)

### ✨ 新增
- 初始版本

### 🐛 修复
- 无
"@
    "附录/贡献指南.md" = @"
# 贡献指南

## 如何参与

1. Fork 本仓库
2. 创建特性分支
3. 提交变更
4. 发起 Pull Request
"@
}

foreach ($relPath in $sampleFiles.Keys) {
    $fullPath = Join-Path $docsDir $relPath
    $dir = Split-Path $fullPath -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    if (-not (Test-Path $fullPath)) {
        $sampleFiles[$relPath] | Out-File -FilePath $fullPath -Encoding UTF8
    }
}

Write-Host "  ✅ 创建示例文档文件" -ForegroundColor Green
Write-Host "`n[文档初始化] 完成！" -ForegroundColor Green
Write-Host ""
Write-Host "  下一步操作：" -ForegroundColor Cyan
Write-Host "  1. 编辑 docs/ 下的 Markdown 文件完善文档内容" -ForegroundColor White
Write-Host "  2. 运行 generate-sidebar.ps1 生成侧边栏" -ForegroundColor White
Write-Host "  3. 运行 serve.ps1 启动预览服务器" -ForegroundColor White
Write-Host "  4. 访问 http://localhost:3000 查看效果" -ForegroundColor White
