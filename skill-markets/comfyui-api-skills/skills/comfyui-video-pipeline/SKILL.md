---
name: comfyui-video-pipeline
description: 按需求调度视频生成引擎。覆盖 LTX-2.3（4K 音视频）、Wan 2.6（参考图生视频 + 口型同步 + 原生音频）、Wan 2.2 MoE（电影级）、FramePack（长视频）、HunyuanVideo 1.5（轻量旗舰）、AnimateDiff V3（快速迭代）。含后处理与说话人管线。用于视频生成或动画。
user-invocable: true
metadata: {"openclaw":{"emoji":"🎥","os":["darwin","linux","win32"],"requires":{"anyBins":["ffmpeg"]}}}
---

# ComfyUI 视频管线技能

按需求调度不同视频生成引擎，串联后处理。

## 引擎选择决策表

| 需求 | 推荐引擎 | 显存 |
|------|----------|------|
| 4K 竖屏/横屏生产级 | LTX-2.3 | 24GB+ |
| 参考图生视频 + 原生口型同步 + 原生音频 | Wan 2.6 | 24GB+ |
| 电影级画质 + 首尾帧控制 | Wan 2.2 MoE 14B | 24GB+ |
| 轻量旗舰画质 | HunyuanVideo 1.5 | 24GB |
| 长视频（60 秒+）+ 低显存 | FramePack | 6GB+ |
| 人物为主 + 33 种表情 + 电影感 | SkyReels V1 | 24GB+ |
| 快速迭代 + 动作 LoRA | AnimateDiff V3 | 8GB+ |
| 商业级 + 云服务 | Kling 3.0（合作伙伴节点） | 云端 |

## 各引擎详解

### LTX-2.3

**核心特性**：
- 4K 音视频同步生成
- 竖屏/横屏原生支持
- 提供 GGUF 量化（低显存可用）
- 2026 年 3 月新出，Day-0 ComfyUI 支持

**适用场景**：
- 短剧/竖屏短片
- 4K 生产级镜头
- 需要原生音频

**核心节点**（参考）：`LTXVideoSampler` / `LTXVideoDecode`

**参数建议**：
- 分辨率：1080p / 2160p
- 帧数：97-241
- 步数：30-50

### Wan 2.6

**核心特性**：
- **参考图生视频**（image-to-video）
- **原生音频生成**（场景音效 + 语音）
- **内置口型同步**（无需独立节点）
- 1080p 输出
- 2026 年 1 月新出

**适用场景**：
- 角色动作视频
- 说话人视频（最简方案）
- 音乐可视化

**核心节点**：`WanVideoSampler` / `WanVideoDecode` / `WanVideoAudioEncoder`

**参数建议**：
- 输入：1 张参考图
- 分辨率：720p / 1080p
- 帧数：49-121
- 步数：30-50
- 音频：开启

### Wan 2.2 MoE 14B

**核心特性**：
- A14B 架构（混合专家）
- 电影级画质
- 首尾帧控制（起止构图）
- 14B 参数，原生 FP16

**适用场景**：
- 电影感短片
- 镜头转场
- 概念验证

**核心节点**：`WanVideoSampler` + `FirstLastFrame` 控制

**参数建议**：
- 分辨率：720p
- 帧数：81
- 步数：40-50

### HunyuanVideo 1.5

**核心特性**：
- 8.3B 参数（自 13B 缩减）
- 中文提示词支持好
- 旗舰画质

**适用场景**：
- 中文场景
- 高质量短片
- 资源略紧的生产

**核心节点**：`HunyuanVideoSampler`

### FramePack

**核心特性**：
- **VRAM 不随长度增长**（适合长视频）
- 60 秒+ 视频
- 6GB 即可运行
- SageAttn 提速 30%

**适用场景**：
- 长镜头（演讲、纪录片片段）
- 低显存设备
- 概念验证长视频

**核心节点**：`FramePackSampler`

**参数建议**：
- 帧数：1500+（60 秒+ @ 24fps）
- 步数：30-40

### SkyReels V1

**核心特性**：
- 33 种表情
- 基于 HunyuanVideo
- 人物/电影感优化
- 2026 年 1 月新出

**适用场景**：
- 人物表情视频
- 电影感人物镜头
- 表演捕捉替代

**核心节点**：`SkyReelsSampler` + `ExpressionController`

### AnimateDiff V3

**核心特性**：
- 快速迭代（4-8 步 Lightning）
- 动作 LoRA 生态
- SD1.5 / SDXL 基础

**适用场景**：
- 快速预览
- 动作风格实验
- 低显存

**核心节点**：`AnimateDiffLoaderWithContext` + `KSampler`（带 motion model）

## 后处理

### 帧插值（RIFE）

**用途**：把 24fps 提升到 48/60fps

**节点**：`RIFE VFI`（来自 ComfyUI-Frame-Interpolation）

**参数**：
- 倍率：2x / 4x
- 模型：rife47 / rife49

### 人脸修复

**用途**：放大或低质量素材后修复人脸

**节点**：`FaceDetailer`（来自 ComfyUI-Impact-Pack）或 `ReActorFaceSwap`

**参数**：
- 检测模型：`face_yolov8m.pt`
- 修复模型：`codeformer.pth`（推荐）

### 去闪烁

**用途**：消除视频帧间亮度跳变

**节点**：`Deflicker` 节点

### 色彩校正

**用途**：统一调色

**节点**：`ColorCorrect` 节点组

## 说话人专项管线

参考 `comfyui-voice-pipeline` 生成的音频 → Wan 2.6 视频：

```
角色参考图
  ↓
Wan 2.6 视频生成（开启音频 + 口型同步）
  ↓
输出：带音轨的说话人视频
```

或更复杂的组合：

```
角色参考图 → Wan 2.2 视频生成（无音频）
语音合成 → 独立音频轨
LatentSync 1.6 → 口型对齐
VHS_VideoCombine → 合并
```

## 工作流构建

使用 `comfyui-workflow-builder` 生成各引擎的 JSON：

- 引擎选择后调用对应模式
- 后处理作为附加节点链
- 保存到 `projects/{项目}/工作流/`

## 提交与监控

通过 `comfyui-api` 提交：

```bash
curl -X POST {{COMFYUI_URL}}/prompt \
  -H "Content-Type: application/json" \
  -d @工作流.json
```

**轮询**：每 `{{COMFYUI_POLL_INTERVAL}}` 秒一次，`{{COMFYUI_POLL_TIMEOUT}}` 秒超时告警（视频生成 15-30 分钟正常）。

## 输出

视频生成完成后：

1. 视频文件存到 `projects/{项目}/生成记录/{时间戳}/`
2. 帧插值后版本另存
3. 在 `清单.yaml` 记录有效引擎/参数组合

## 注意事项

- **显存不足时**先用 GGUF 量化版本
- **超长视频**优先用 FramePack
- **音频需求**用 Wan 2.6 一次完成（避免后期合并麻烦）
- **口型同步**优先用 LatentSync 1.6 或 Wan 2.6 原生
- 多次实验后**记录有效组合**到项目档案
