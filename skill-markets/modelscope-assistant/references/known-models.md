# 已知模型目录

> 收录魔搭社区上常见的高质量模型元数据。作为 AI 助手推荐模型的权威知识库。
> 每个条目包含 `capabilities` 和 `recommended_for`，供 AI 做语义匹配。
> 文件路径按统一仓库 `D:\ai-models\` 约定给出。

## Text-to-Image（文生图）

### SDXL 家族

```yaml
- id: sdxl_base_1.0
  name: SDXL Base 1.0
  type: checkpoint
  family: sdxl
  task: text-to-image
  file:
    name: sd_xl_base_1.0.safetensors
    size_gb: 6.94
  source:
    url: https://modelscope.cn/models/AI-ModelScope/stable-diffusion-xl-base-1.0
    license: OpenRAIL++-M
  capabilities: [text-to-image, image-to-image]
  quality: {realism: 8, style_flexibility: 8, speed: 6}
  recommended_for: ["写实人像", "通用图像生成", "风景"]
  dependencies:
    - {type: text_encoder, family: clip_l}
    - {type: text_encoder, family: clip_g}
    - {type: vae, family: sdxl_vae}
  tags: [写实, 人像, 风景, 通用]
  status: active
```

### Flux 家族

```yaml
- id: flux1_dev
  name: Flux.1 Dev
  type: checkpoint
  family: flux
  task: text-to-image
  file:
    name: flux1_dev.safetensors
    size_gb: 23.8
  source:
    url: https://modelscope.cn/models/black-forest-labs/FLUX.1-dev
    license: Flux.1 Dev Non-Commercial
  capabilities: [text-to-image, image-to-image, inpainting]
  quality: {realism: 9, style_flexibility: 9, speed: 4}
  recommended_for: ["超写实人像", "高精度渲染", "商业级出图"]
  dependencies:
    - {type: text_encoder, family: t5}
    - {type: text_encoder, family: clip_l}
    - {type: vae, family: flux_vae}
  tags: [超写实, 人像, 商业, 高端]
  status: active
```

### Wan 家族

```yaml
- id: wan2_2_i2v_720p
  name: Wan 2.2 I2V 720P
  type: diffusion_model
  family: wan
  task: image-to-video
  file:
    name: wan2.2_i2v_720p.safetensors
    size_gb: 15.2
  source:
    url: https://modelscope.cn/models/Wan-AI/Wan2.2-I2V-14B
    license: Apache-2.0
  capabilities: [image-to-video]
  quality: {motion_naturalness: 8, temporal_consistency: 8, speed: 3}
  recommended_for: ["图生视频", "短视频生成", "动态壁纸"]
  dependencies:
    - {type: text_encoder, family: umt5}
    - {type: vae, family: wan_vae}
  tags: [视频, 动态, 短视频]
  status: active
```

## Text-to-Speech（语音合成）

### CosyVoice 家族

```yaml
- id: cosyvoice3_0_5b
  name: Fun-CosyVoice 3.0 0.5B
  type: tts
  family: cosyvoice
  task: tts
  file:
    name: Fun-CosyVoice3-0.5B-2512/  # 目录
    size_gb: 3.2
  source:
    url: https://modelscope.cn/models/FunAudioLLM/Fun-CosyVoice3-0.5B-2512
    license: MIT
  capabilities: [tts, voice-clone, cross-lingual, streaming]
  quality: {content_accuracy: 9, speaker_similarity: 8, naturalness: 9}
  recommended_for: ["语音合成", "声音克隆", "多语言朗读", "方言朗读"]
  tags: [TTS, 声音克隆, 多语言, 中文方言]
  notes: "0.5B 参数，支持 9 语言 18 方言，零样本克隆"
  status: active
```

## Large Language Models（大语言模型）

### Qwen 家族

```yaml
- id: qwen3_235b_a22b
  name: Qwen3 235B-A22B
  type: llm
  family: qwen
  task: text-generation
  file:
    name: Qwen3-235B-A22B-GGUF/  # 目录
    size_gb: 140
  source:
    url: https://modelscope.cn/models/Qwen/Qwen3-235B-A22B
    license: Apache-2.0
  capabilities: [text-generation, tool-use, code-generation, reasoning]
  quality: {reasoning: 9, coding: 9, chinese: 10, speed: 3}
  recommended_for: ["中文对话", "代码生成", "复杂推理", "工具调用"]
  tags: [中文, 推理, 代码, MoE]
  notes: "MoE 架构，1M 上下文，236B 参数"
  status: active

- id: qwen3_0_5b
  name: Qwen3 0.5B
  type: llm
  family: qwen
  task: text-generation
  file:
    name: qwen3-0.5b-instruct-Q4_K_M.gguf
    size_gb: 0.4
  source:
    url: https://modelscope.cn/models/Qwen/Qwen3-0.5B
    license: Apache-2.0
  capabilities: [text-generation]
  quality: {speed: 10, chinese: 7}
  recommended_for: ["轻量对话", "嵌入式设备", "快速测试"]
  tags: [轻量, 中文, 快速]
  status: active
```

### DeepSeek 家族

```yaml
- id: deepseek_v3
  name: DeepSeek-V3
  type: llm
  family: deepseek
  task: text-generation
  file:
    name: DeepSeek-V3-GGUF/
    size_gb: 380
  source:
    url: https://modelscope.cn/models/deepseek-ai/DeepSeek-V3
    license: MIT
  capabilities: [text-generation, code-generation, reasoning, tool-use]
  quality: {reasoning: 10, coding: 10, chinese: 10, speed: 4}
  recommended_for: ["高级编程", "数学推理", "长文档分析"]
  tags: [推理, 代码, 中文, MoE, 旗舰]
  status: active
```

## Image Editing（图像编辑）

### Qwen-Edit 家族

```yaml
- id: qwen_edit_2511
  name: Qwen-Edit 2511
  type: diffusion_model
  family: qwen
  task: image-editing
  file:
    name: Qwen-Edit-2511/
    size_gb: 12.5
  source:
    url: https://modelscope.cn/models/Qwen/Qwen-Edit-2511
    license: Apache-2.0
  capabilities: [image-editing, object-removal, object-addition, style-transfer]
  quality: {precision: 9, semantic_understanding: 9}
  recommended_for: ["一句话P图", "物体增删", "光影修改", "背景替换"]
  tags: [图像编辑, 语义编辑, 无掩码]
  status: active
```

## Automatic Speech Recognition（语音识别）

```yaml
- id: paraformer_large_zh
  name: Paraformer Large 中文
  type: checkpoint
  family: paraformer
  task: asr
  file:
    name: speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch/
    size_gb: 1.2
  source:
    url: https://modelscope.cn/models/damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
    license: Apache-2.0
  capabilities: [asr, punctuation, vad]
  quality: {accuracy: 9, speed: 8}
  recommended_for: ["中文语音转文字", "会议记录", "字幕生成"]
  tags: [ASR, 中文, 快速]
  status: active
```
