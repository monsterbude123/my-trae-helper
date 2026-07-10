---
name: comfyui-workflow-builder
description: 从自然语言生成 ComfyUI 工作流 JSON。生成前对照库存校验每个模型与节点。支持文生图、身份保持、视频（Wan/AnimateDiff）、放大与局部重绘。包含各组件的显存估算。用于直接构建 ComfyUI 工作流。
user-invocable: true
metadata: {"openclaw":{"emoji":"🔧","os":["darwin","linux","win32"]}}
---

# ComfyUI 工作流构建技能

从自然语言需求生成合规、已校验的 ComfyUI 工作流 JSON。

## 工作流程

### 步骤 1：需求解析

从用户输入中提取：

- **任务类型**：文生图、图生图、放大、局部重绘、视频
- **模型偏好**：FLUX、SDXL、Wan、HunyuanVideo、AnimateDiff
- **身份保持**：是否需要 InstantID、PuLID、IP-Adapter、LoRA
- **参数**：分辨率、步数、CFG、采样器
- **后处理**：放大、人脸修复、帧插值

### 步骤 2：库存校验

**任何**工作流生成前**必须**读取 `state/inventory.json`：

1. 确认所选模型已下载
2. 确认所需自定义节点已安装
3. 估算显存是否在硬件承受范围

库存缺失时：

- 模型：提供 `references/模型清单.md` 中的下载链接
- 节点：建议 `ComfyUI-Manager install {package_name}`

### 步骤 3：节点图设计

按以下顺序构建节点图：

```
1. 模型加载（LoadCheckpoint / LoadDiffusionModel）
2. CLIP 文本编码（CLIPTextEncode × 2）
3. 采样器（KSampler 或对应视频采样器）
4. VAE 解码（VAEDecode）
5. 保存（SaveImage / VHS_VideoCombine）
6. 可选：放大、人脸修复、ControlNet 等
```

### 步骤 4：JSON 格式化

按 ComfyUI 格式输出：

```json
{
  "1": {
    "class_type": "LoadCheckpoint",
    "inputs": { "ckpt_name": "flux1-dev.safetensors" }
  },
  "2": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "Sage 半身像，森林背景，写实人像，50mm 镜头",
      "clip": ["1", 1]
    }
  },
  "3": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "ugly, deformed, blurry, low quality",
      "clip": ["1", 1]
    }
  },
  "4": {
    "class_type": "EmptyLatentImage",
    "inputs": { "width": 1024, "height": 1024, "batch_size": 1 }
  },
  "5": {
    "class_type": "KSampler",
    "inputs": {
      "model": ["1", 0],
      "positive": ["2", 0],
      "negative": ["3", 0],
      "latent_image": ["4", 0],
      "seed": 42,
      "steps": 28,
      "cfg": 3.5,
      "sampler_name": "uni_pc",
      "scheduler": "sgm_uniform",
      "denoise": 1.0
    }
  },
  "6": {
    "class_type": "VAEDecode",
    "inputs": {
      "samples": ["5", 0],
      "vae": ["1", 2]
    }
  },
  "7": {
    "class_type": "SaveImage",
    "inputs": { "filename_prefix": "Sage", "images": ["6", 0] }
  }
}
```

### 步骤 5：保存与执行

1. 保存到 `projects/{项目}/工作流/{名称}.json`
2. 若 ComfyUI 在运行：通过 `comfyui-api` 提交
3. 若未运行：建议用户拖入 ComfyUI

## 工作流模式

### 模式 A：基础文生图

**适用**：FLUX、SDXL、SD1.5

**核心节点**：
- `LoadCheckpoint`
- `CLIPTextEncode` × 2
- `EmptyLatentImage`
- `KSampler`
- `VAEDecode`
- `SaveImage`

**显存估算**：基础 8-16GB（视模型）

### 模式 B：身份保持（InstantID）

**核心节点**：
- `LoadCheckpoint`（SDXL）
- `ApplyInstantID`
- `InstantIDFaceAnalysis`
- `IPAdapterApply`
- 其余同模式 A

**前置条件**：
- SDXL checkpoint
- `ComfyUI_InstantID` 节点包
- `ip-adapter.bin` 模型
- 参考图

**显存估算**：12-16GB

### 模式 C：身份保持（PuLID Flux II）

**核心节点**：
- `LoadCheckpoint`（FLUX）
- `ApplyPuLIDFluxII`
- `PulidFluxModelLoader`
- `PulidFluxEvaClipLoader`
- `FaceAnalysis`（来自 Impact Pack）
- 其余同模式 A

**显存估算**：24-40GB

### 模式 D：放大（Ultimate SD Upscale）

**核心节点**：
- `LoadCheckpoint`
- `CLIPTextEncode`
- `ImageUpscaleWithModel`
- `UltimateSDUpscale`
- `SaveImage`

**显存估算**：12-20GB

### 模式 E：局部重绘（Inpainting）

**核心节点**：
- `LoadCheckpoint`（inpainting 模型）
- `LoadImage`（待编辑图）
- `VAEEncode`
- `SetLatentNoiseMask`
- `KSampler`（denoise < 1.0）
- `VAEDecode`
- `SaveImage`

**关键参数**：`denoise` 0.4-0.6 控制重绘强度

### 模式 F：视频生成（Wan 2.6 图生视频）

**核心节点**：
- `LoadDiffusionModel`（Wan 2.6）
- `CLIPLoader`（T5 + CLIP）
- `VAELoader`（Wan VAE）
- `WanVideoSampler`
- `WanVideoDecode`
- `VHS_VideoCombine`

**显存估算**：24GB+

**参数建议**：
- 分辨率：720p / 1080p
- 帧数：49-81
- 步数：30-50

### 模式 G：视频生成（AnimateDiff）

**核心节点**：
- `LoadCheckpoint`（SD1.5 或 SDXL）
- `AnimateDiffLoaderWithContext`
- `CLIPTextEncode`
- `KSampler`（带 motion model）
- `VHS_VideoCombine`

**显存估算**：8-16GB

## 显存估算规则

| 组件 | 显存占用 |
|------|----------|
| FLUX.1-dev FP16 | 24GB |
| FLUX.1-dev FP8 | 12GB |
| FLUX.1-dev NVFP4 | 8GB |
| SDXL FP16 | 8GB |
| SD1.5 FP16 | 4GB |
| Wan 2.2 14B | 24GB |
| Wan 2.6 14B | 24GB |
| HunyuanVideo 1.5 | 24GB |
| FramePack | 6-12GB |
| InstantID 栈 | +4GB |
| PuLID Flux II | +4-8GB |
| ControlNet | +2-4GB |
| 放大 4x | +4-8GB |

**总显存** = 模型 + LoRA + ControlNet + 后处理 + 1-2GB 缓冲

## 输出

工作流构建完成时交付：

1. **工作流 JSON 文件**（保存到 `projects/{项目}/工作流/`）
2. **节点说明**（每个节点的目的与参数）
3. **显存估算**
4. **执行说明**（在线/离线模式）
5. **预期结果**（分辨率、文件名模式）

## 注意事项

- **不要**在缺失节点/模型时硬提交——先告知用户
- LoRA 强度 0.7-0.9，超过 1.0 会过拟合
- CFG：FLUX 1-5，SDXL 5-9，SD1.5 7-12
- 步数：FLUX 20-35，SDXL 25-35
- 视频步数视模型而定
