# 模型搜索指南

## 搜索策略

魔搭模型库有 10 万+模型，按以下维度筛选：

| 筛选维度 | 选项 |
|----------|------|
| 任务类型 | NLP / CV / 语音 / 多模态 / 科学智能 |
| 框架 | PyTorch / TensorFlow / MindSpore |
| 许可证 | Apache-2.0 / MIT / CC / 自定义 |
| 是否支持推理 API | 是/否 |

## 热门模型速查

### 大语言模型

| 模型 | 模型 ID | 亮点 |
|------|---------|------|
| Qwen3-235B | `Qwen/Qwen3-235B-A22B` | MoE，1M 上下文 |
| DeepSeek-V3 | `deepseek-ai/DeepSeek-V3` | MoE，极致推理效率 |
| GLM-4-9B | `THUDM/glm-4-9b-chat` | 中英文均衡 |
| MiniMax-Text-01 | `MiniMax/MiniMax-Text-01` | 高效生成 |

### 视觉模型

| 模型 | 模型 ID | 亮点 |
|------|---------|------|
| Qwen-Image | `Qwen/Qwen-Image` | 文生图/编辑 |
| Z Image Turbo | `Tongyi-MAI/Z-Image-Turbo` | 极速人像生成 |
| YOLOv8 | `damo/cv_yolov8_object-detection` | 目标检测 |
| Stable Diffusion | 社区 Fork 多版本 | 文生图 |

### 语音模型

| 模型 | 模型 ID | 亮点 |
|------|---------|------|
| Paraformer | `damo/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch` | ASR 中文 |
| CosyVoice | `FunAudioLLM/CosyVoice-300M` | TTS/克隆 |
| SenseVoice | `FunAudioLLM/SenseVoiceSmall` | 多语言 ASR |

## 搜索入口

- 网页：https://modelscope.cn/models
- SDK：`from modelscope.hub.api import HubApi`
