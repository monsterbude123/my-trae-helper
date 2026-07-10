---
name: comfyui-inventory
description: 探查并缓存已安装的 ComfyUI 模型、自定义节点、系统能力。支持在线（接口查询）和离线（目录扫描）。在生成工作流前用于核对可用资源。
user-invocable: true
metadata: {"openclaw":{"emoji":"📦","os":["darwin","linux","win32"],"requires":{"bins":["pwsh"]},"primaryEnv":"COMFYUI_PATH"}}
---

# ComfyUI 库存技能

探查 ComfyUI 实例中已装内容并缓存结果，用于工作流校验。

## 用途

**每个**工作流生成前**必须**先查库存。这能避免：

- 引用未下载的模型
- 使用未安装的节点
- 超出显存上限

## 两种探查模式

### 在线模式（ComfyUI 接口运行中）

查询实时服务获取权威信息。

**1. 系统信息**：

```bash
curl {{COMFYUI_URL}}/system_stats
```

提取：GPU 名称、总显存、剩余显存、ComfyUI 版本。

**2. 已装节点**：

```bash
curl {{COMFYUI_URL}}/object_info
```

返回所有已注册节点类及其输入/输出规格。

**3. 已装模型（按类型）**：

```bash
curl {{COMFYUI_URL}}/models/checkpoints
curl {{COMFYUI_URL}}/models/loras
curl {{COMFYUI_URL}}/models/vae
curl {{COMFYUI_URL}}/models/controlnet
curl {{COMFYUI_URL}}/models/clip
curl {{COMFYUI_URL}}/models/clip_vision
curl {{COMFYUI_URL}}/models/upscale_models
curl {{COMFYUI_URL}}/models/diffusion_models
```

### 离线模式（目录扫描）

当 ComfyUI 未运行时，直接扫描文件系统。

**需要**：ComfyUI 安装路径（`{{COMFYUI_INSTALL_DIR}}`，默认 `C:\ComfyUI`）

**扫描目录**：

```
{ComfyUI}/models/checkpoints/        → .safetensors、.ckpt
{ComfyUI}/models/loras/              → .safetensors
{ComfyUI}/models/vae/                → .safetensors、.pt
{ComfyUI}/models/controlnet/         → .safetensors、.pth
{ComfyUI}/models/clip/               → .safetensors
{ComfyUI}/models/clip_vision/        → .safetensors
{ComfyUI}/models/upscale_models/     → .pth、.safetensors
{ComfyUI}/models/diffusion_models/   → .safetensors
{ComfyUI}/models/ipadapter/          → .safetensors、.bin
{ComfyUI}/models/instantid/          → .bin
{ComfyUI}/models/insightface/        → .onnx + 文件夹
{ComfyUI}/models/facerestore_models/ → .pth
{ComfyUI}/models/ultralytics/bbox/   → .pt
{ComfyUI}/custom_nodes/              → 文件夹名 = 节点包
```

**自定义节点识别**：列出 `custom_nodes/` 下各目录，每个目录名即一个节点包（如 `ComfyUI_IPAdapter_plus`、`ComfyUI-Impact-Pack`）。

## 缓存格式

结果存到 `state/inventory.json`：

```json
{
  "last_updated": "2026-02-06T12:00:00Z",
  "mode": "online",
  "comfyui_version": "0.3.10",
  "system": {
    "gpu": "NVIDIA RTX 5090",
    "vram_total_gb": 32,
    "vram_free_gb": 28
  },
  "models": {
    "checkpoints": ["flux1-dev.safetensors", "RealVisXL_V5.0.safetensors"],
    "loras": ["sage_character.safetensors"],
    "vae": ["ae.safetensors", "wan_2.1_vae.safetensors"],
    "controlnet": ["instantid_controlnet.safetensors"],
    "clip": ["t5xxl_fp16.safetensors", "clip_l.safetensors"],
    "clip_vision": ["CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"],
    "upscale_models": ["4x-UltraSharp.pth"],
    "diffusion_models": ["wan2.1_i2v_720p_14b_bf16.safetensors"],
    "ipadapter": ["ip-adapter-faceid-plusv2_sd15.bin"],
    "instantid": ["ip-adapter.bin"],
    "insightface": ["inswapper_128.onnx"],
    "facerestore": ["codeformer.pth"],
    "detection": ["face_yolov8m.pt"]
  },
  "custom_nodes": [
    "ComfyUI-Manager",
    "ComfyUI_IPAdapter_plus",
    "ComfyUI_InstantID",
    "ComfyUI-Impact-Pack",
    "ComfyUI-AnimateDiff-Evolved",
    "ComfyUI-VideoHelperSuite"
  ]
}
```

## 工作流校验

拿到工作流 JSON 后，对照库存校验：

```
对每个节点：
  1. 比对 class_type 与已知节点类
  2. 若缺失：识别提供该类的自定义节点包
  3. 建议安装："通过 ComfyUI-Manager 安装：{package_name}"

对每个模型引用：
  1. 比对文件名与该类型的库存
  2. 若缺失：从 references/模型清单.md 查下载链接
  3. 报告："缺失：{filename} - 从 {url} 下载 → {path}"
```

## 常见节点-包映射

| 节点类 | 包名 |
|--------|------|
| ApplyInstantID | ComfyUI_InstantID |
| IPAdapterUnifiedLoader | ComfyUI_IPAdapter_plus |
| FaceDetailer | ComfyUI-Impact-Pack |
| ReactorFaceSwap | ComfyUI-ReActor |
| AnimateDiffLoaderWithContext | ComfyUI-AnimateDiff-Evolved |
| VideoHelper* | ComfyUI-VideoHelperSuite |
| ControlNetApply* | comfyui_controlnet_aux |
| UltimateSDUpscale | ComfyUI_UltimateSDUpscale |
| VHS_* | ComfyUI-VideoHelperSuite |
| RIFE* | ComfyUI-Frame-Interpolation |

## 缓存有效期

- 缓存有效期 **1 小时**（活跃会话内）
- 用户安装新模型/节点时作废
- 强制刷新：`扫描清单.ps1` 或重新查询接口

## 集成

- `comfyui-workflow-builder` 生成工作流前调用
- `comfyui-character-gen`（通过智能体包装）做模型选择时调用
- `comfyui-troubleshooter` 诊断缺失模型错误时调用
- 结果存于 `state/inventory.json` 供所有 skill 引用
