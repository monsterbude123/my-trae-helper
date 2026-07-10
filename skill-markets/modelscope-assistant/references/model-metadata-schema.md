# 模型元数据 Schema

每个模型条目记录以下字段。Registry 文件放在仓库根目录 `model-registry.yaml`。

## 为什么需要元数据

文件系统只能提供"文件在哪、多大"，无法回答"这个模型能做什么、质量如何"。元数据层解决的是 AI 助手做模型推荐的**知识缺口**——当你问"我想生成写实人像"，助手必须知道哪个模型 `recommended_for: ["写实人像"]` 才能给出答案。

## Schema

```yaml
models:
  - id: "sd_xl_base_1.0"           # 全局唯一 ID（kebab-case）
    name: "SDXL Base 1.0"           # 人类可读名称
    type: checkpoint                # checkpoint | lora | vae | controlnet | diffusion_model | text_encoder | upscaler | llm | tts
    family: sdxl                    # 模型家族（sdxl, flux, wan, qwen, llama...）
    task: text-to-image             # 主任务
    file:
      path: "checkpoints/sdxl/sd_xl_base_1.0.safetensors"
      size_gb: 6.94
      sha256: "abc123..."
    source:
      url: "https://modelscope.cn/models/xxx"
      license: "OpenRAIL++-M"
    capabilities:                   # 模型能做什么
      - text-to-image
      - image-to-image
    quality:                        # 1-10 评分
      realism: 8
      style_flexibility: 7
      speed: 6
    recommended_for:                # 推荐用途（中文），AI 做语义匹配的核心字段
      - "写实风格人像"
      - "通用图像生成"
    dependencies:                   # 配套模型（同仓库内查询）
      - type: text_encoder
        family: clip_l
      - type: vae
        family: sdxl_vae
    tags: [写实, 人像, 通用]
    notes: "SDXL 官方基座，社区使用最广"
    status: active                  # active | archived | deprecated
```

## 字段说明

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `id` | 是 | string | 全局唯一，kebab-case，用作查询 key |
| `name` | 是 | string | 展示名 |
| `type` | 是 | enum | 模型文件类型 |
| `family` | 是 | string | 模型家族，用于关联同家族的 checkpoint/lora/vae |
| `task` | 是 | enum | 主任务类型 |
| `file.path` | 是 | string | 相对于仓库根目录的路径 |
| `file.size_gb` | 否 | float | 文件大小 |
| `file.sha256` | 否 | string | SHA256 哈希，用于去重和完整性校验 |
| `source.url` | 否 | url | 下载来源 |
| `source.license` | 否 | string | 开源协议 |
| `capabilities` | 是 | list | 能力列表，枚举值见下方 |
| `quality.*` | 否 | int(1-10) | 主观质量评分，维度因 type 不同而异 |
| `recommended_for` | 是 | list | **核心字段**：推荐用途（中文短语），AI 做语义匹配的依据 |
| `dependencies` | 否 | list | 配套模型，在同 registry 内查询 |
| `tags` | 否 | list | 自由标签 |
| `notes` | 否 | string | 备注 |
| `status` | 是 | enum | active / archived / deprecated |

## 能力枚举（capabilities）

| 领域 | 枚举值 |
|------|--------|
| 图像 | `text-to-image`, `image-to-image`, `inpainting`, `outpainting`, `image-editing`, `super-resolution`, `face-restoration` |
| 视频 | `text-to-video`, `image-to-video`, `video-editing` |
| 语音 | `tts`, `asr`, `voice-clone`, `cross-lingual`, `streaming`, `audio-generation` |
| 语言 | `text-generation`, `code-generation`, `reasoning`, `tool-use`, `translation`, `summarization` |
| 视觉理解 | `image-classification`, `object-detection`, `image-segmentation`, `ocr`, `visual-question-answering` |

## 任务类型枚举（task）

| 值 | 中文 |
|----|------|
| `text-to-image` | 文生图 |
| `image-to-image` | 图生图 |
| `text-to-video` | 文生视频 |
| `image-to-video` | 图生视频 |
| `image-editing` | 图像编辑 |
| `tts` | 语音合成 |
| `asr` | 语音识别 |
| `text-generation` | 文本生成 |

## 维护策略

- **下载新模型** → 手动或脚本追加一条
- **删除模型** → `status: archived`，不删除记录（保留历史）
- **完整性校验** → `file.sha256` 定期校验文件未被替换
- **知识积累** → `notes` 和 `quality` 随着使用持续更新（如"这个模型的 hand 生成不稳定"）
