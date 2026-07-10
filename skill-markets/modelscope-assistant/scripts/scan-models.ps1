<#
.SYNOPSIS
    扫描本地模型仓库，生成 model-registry.yaml 骨架。

.DESCRIPTION
    遍历模型仓库目录，识别 safetensors/ckpt/gguf 文件及目录型模型，
    按 Schema 生成 YAML 条目。自动填充 file 和 type 字段，
    capabilities/recommended_for/quality 标记 TODO。

.PARAMETER RepoPath
    模型仓库根目录路径

.PARAMETER OutputPath
    输出 YAML 文件路径（默认：仓库根目录下 model-registry.yaml）

.EXAMPLE
    .\scan-models.ps1 -RepoPath "D:\ai-models"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoPath,
    [string]$OutputPath = ""
)

if ($OutputPath -eq "") {
    $OutputPath = Join-Path $RepoPath "model-registry.yaml"
}

# 目录名 → type 映射
$dirTypeMap = @{
    "checkpoints"       = "checkpoint"
    "loras"             = "lora"
    "diffusion_models"  = "diffusion_model"
    "text_encoders"     = "text_encoder"
    "vae"               = "vae"
    "controlnet"        = "controlnet"
    "upscale_models"    = "upscaler"
    "clip_vision"       = "clip_vision"
    "audio_encoders"    = "audio_encoder"
    "llm"               = "llm"
    "tts"               = "tts"
}

$scanDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$entries = @()
$errors = @()

Write-Host "Scanning: $RepoPath" -ForegroundColor Cyan

# 对每个子目录扫描文件
foreach ($dir in (Get-ChildItem -Directory $RepoPath -Depth 0)) {
    $dirName = $dir.Name
    if ($dirName -eq "_archive" -or $dirName.StartsWith(".")) { continue }

    $type = $dirTypeMap[$dirName]
    if (-not $type) {
        Write-Host "  SKIP $dirName : unknown type" -ForegroundColor DarkGray
        continue
    }

    Write-Host "  Scanning $dirName (type=$type)..." -ForegroundColor Gray

    # 扫描该目录下的模型文件
    $files = Get-ChildItem $dir.FullName -Recurse -File -Include @("*.safetensors","*.ckpt","*.pt","*.gguf") -EA SilentlyContinue

    foreach ($file in $files) {
        # 跳过 metadata 文件
        if ($file.Name -like "*.metadata-only*") { continue }

        $relativePath = $file.FullName.Replace($RepoPath, "").TrimStart("\", "/")
        $sizeGB = [math]::Round($file.Length / 1GB, 2)
        $sha256 = ""

        # 计算 SHA256（大文件会慢）
        try {
            $sha256 = (Get-FileHash -Path $file.FullName -Algorithm SHA256).Hash
        } catch {
            $errors += "SHA256 failed: $relativePath : $_"
        }

        # 从路径中推断 family（checkpoints/flux/flux1_dev.safetensors → flux）
        $pathParts = $relativePath -split '[\\/]'
        $family = ""
        if ($pathParts.Count -ge 3) {
            $family = $pathParts[1]  # 第二段目录名作为 family
        }

        $id = $file.BaseName -replace '[^a-zA-Z0-9_-]', '_' -replace '_+', '_' -replace '^_|_$', ''

        $entry = @"
  - id: "$id"
    name: "$($file.BaseName)"      # TODO: 人类可读名称
    type: $type
    family: "$family"              # TODO: 确认家族
    task: ""                        # TODO: text-to-image | image-to-video | tts | ...
    file:
      path: "$relativePath"
      size_gb: $sizeGB
      sha256: "$sha256"
    source:
      url: ""                       # TODO
      license: ""                   # TODO
    capabilities: []                # TODO
    quality: {}                     # TODO
    recommended_for: []             # TODO
    dependencies: []                # TODO
    tags: []                        # TODO
    notes: "自动生成于 $scanDate"
    status: active
"@
        $entries += $entry
    }

    # 也检查是否有目录型模型（如 CosyVoice 是整个目录）
    $subDirs = Get-ChildItem $dir.FullName -Directory -Depth 0 -EA SilentlyContinue
    $subDirs = $subDirs | Where-Object {
        $_ -notin $files.DirectoryName -and
        -not (Get-ChildItem $_.FullName -File -Recurse -Include @("*.safetensors","*.ckpt","*.pt","*.gguf") -EA SilentlyContinue) -and
        (Get-ChildItem $_.FullName -File -EA SilentlyContinue | Measure-Object).Count -gt 0
    }

    foreach ($subDir in $subDirs) {
        # 简单的启发式：如果子目录下有 config.json 或 .yaml，可能是目录型模型
        if ((Test-Path (Join-Path $subDir.FullName "config.json")) -or
            (Test-Path (Join-Path $subDir.FullName "*.yaml"))) {
            $relativePath = $subDir.FullName.Replace($RepoPath, "").TrimStart("\", "/")
            $sizeGB = [math]::Round((Get-ChildItem $subDir.FullName -Recurse -File -EA SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
            $id = $subDir.Name -replace '[^a-zA-Z0-9_-]', '_'

            $entry = @"
  - id: "$id"
    name: "$($subDir.Name)"         # TODO
    type: $type
    family: "$($subDir.Name)"
    task: ""                        # TODO
    file:
      path: "$relativePath/"
      size_gb: $sizeGB
      sha256: ""                    # 目录型不计算
    source:
      url: ""                       # TODO
      license: ""                   # TODO
    capabilities: []                # TODO
    quality: {}                     # TODO
    recommended_for: []             # TODO
    dependencies: []                # TODO
    tags: []                        # TODO
    notes: "目录型模型，自动生成于 $scanDate"
    status: active
"@
            $entries += $entry
        }
    }
}

# 输出 YAML
$yaml = @"`
# Model Registry
# 自动生成于: $scanDate
# 仓库路径: $RepoPath
# 总计条目: $($entries.Count)
# 扫描错误: $($errors.Count)
#
# 标记 TODO 的字段请手动填写，尤其是 recommended_for 和 capabilities。

models:
$($entries -join "")

"@

Set-Content -Path $OutputPath -Value $yaml -Encoding UTF8

Write-Host ""
Write-Host "Done! Generated: $OutputPath" -ForegroundColor Green
Write-Host "  Models: $($entries.Count)" -ForegroundColor White
if ($errors.Count -gt 0) {
    Write-Host "  Errors:" -ForegroundColor Yellow
    $errors | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
}
Write-Host ""
Write-Host "Next: 手动填写 TODO 字段，至少补上 capabilities 和 recommended_for" -ForegroundColor Cyan
