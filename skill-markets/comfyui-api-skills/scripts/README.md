# ComfyUI 工具脚本

> 真正的命令行工具，**不**是给 AI 看的指令文件。
> 零外部依赖（仅用 Python 3.10+ 标准库），跨平台（Windows / macOS / Linux）。

## 4 个脚本

| 脚本 | 作用 | 何时用 |
|------|------|--------|
| `comfy_pipeline.py` | 提交→轮询→下载一条龙 | 最常用，**80% 场景** |
| `comfy_inject.py` | 只改 JSON 不提交 | 想用 GUI 拖入 ComfyUI、批量生成 JSON |
| `comfy_status.py` | 服务状态 + 库存速览 | 调试、确认模型已装 |
| `lib/comfy_client.py` | 公共客户端（被上述调用） | 自己写脚本时 import |

## 安装

把 `scripts/` 目录加到 PATH，或直接 `python scripts/comfy_pipeline.py`。

**前置**：Python 3.10+。**零依赖**。

## 配置

读取 `.env`（在 `scripts/` 上一级）：

```bash
COMFYUI_URL=http://127.0.0.1:8188
COMFYUI_POLL_INTERVAL=5
COMFYUI_POLL_TIMEOUT=600
COMFYUI_CLIENT_ID=comfyui-api-skills
```

CLI 参数 > 环境变量 > `.env` > 默认值。

## 快速开始

### 1. 查服务状态

```bash
python scripts/comfy_status.py
# 输出：ComfyUI 版本 / GPU / 显存 / checkpoint 计数
```

### 2. 一键提交（80% 场景）

```bash
# 用默认 JSON 跑一次
python scripts/comfy_pipeline.py --json example/comfyui-test/api-json/Anima_01.json

# 替换提示词 + 改参数
python scripts/comfy_pipeline.py --json Anima_01.json \
    --positive "1girl, blue hair, sunset" \
    --negative "worst quality, blurry" \
    --seed 12345 --steps 30 --cfg 7 \
    --output-dir ./out --output-prefix TestRun
```

### 3. 只改 JSON 不提交

```bash
python scripts/comfy_inject.py --json Anima_01.json --show
python scripts/comfy_inject.py --json Anima_01.json \
    --positive "..." --seed 999 --out modified.json
```

### 4. 远程 ComfyUI

```bash
python scripts/comfy_pipeline.py --json Anima_01.json \
    --url http://192.168.1.20:8188
```

## 完整参数表（comfy_pipeline.py）

```
必填：
  -j, --json FILE          工作流 JSON 文件

提示词（自动定位 KSampler 正负节点）：
  -p, --positive TEXT      替换正提示词
  -n, --negative TEXT      替换负提示词

采样参数：
  --seed INT               随机种子
  --steps INT              步数
  --cfg FLOAT              CFG 缩放
  --sampler NAME           euler / euler_ancestral / dpmpp_2m / er_sde ...
  --scheduler NAME         normal / karras / exponential / sgm_uniform ...

分辨率与批量：
  --width INT              图像宽度
  --height INT             图像高度
  --batch-size INT         批量

模型与输出：
  --ckpt FILE.safetensors  替换 checkpoint
  --output-prefix STR      替换 SaveImage 文件名前缀

连接：
  --url URL                ComfyUI 地址
  --poll-interval INT      轮询间隔秒数（默认 5）
  --timeout INT            轮询总超时秒数（默认 600）
  --no-download            不下载输出
  --output-dir DIR         输出目录（默认 ./out）

调试：
  --save-json FILE         保存修改后的 JSON
  --dry-run                只生成 JSON 不提交
  --no-health-check        跳过服务检查
```

## 智能识别原理

- **正负提示词节点**：从 `KSampler.inputs.positive` / `negative` 回溯到 `CLIPTextEncode`
- **latent 节点**：从 `KSampler.inputs.latent_image` 回溯到 `EmptyLatentImage`（含 width/height/batch_size）
- **checkpoint 节点**：从 `KSampler.inputs.model` 回溯 `CheckpointLoaderSimple` / `UNETLoader`
- **output prefix**：扫描所有 `SaveImage` / `VHS_VideoCombine` 节点

支持主流采样器节点（KSampler / KSamplerAdvanced / SamplerCustom）。

## 与 skill 包的关系

这些脚本是 `comfyui-api` skill 的**实现层**。skill 文档告诉 AI 怎么用 ComfyUI，
脚本让用户（或 CI）直接执行。两者互补：

- **AI 编排**：用 skill 文档自动决策与排错
- **手动 / 批处理**：用 CLI 脚本
- **CI / 流水线**：直接调 `comfy_pipeline.py` 返回 0/非 0 退出码
