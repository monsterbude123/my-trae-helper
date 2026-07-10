# TTS 配音集成

> 引擎无关的 TTS 配音方法论。引擎特定注入细节见各引擎的脚本技能。

## 铁律

1. **TTS 是后期增强，不能阻塞主流程。** 先完成图像/音频素材 + 脚本 + 构建，确认可玩后再做 TTS。
2. **写 voices.json 之前必须加载 `voice-character-design`。** 不调起就写 = 100% 返工。

## 工作流

TTS 使用 `tts_qwen.json`（从 `comfyui-api-skills/cache/workflows/` 复制）：

| 节点 | 字段 | 用途 |
|------|------|------|
| 1 `FB_Qwen3TTSVoiceDesign` | `text` | 要朗读的中文文本（必填） |
| 1 | `instruct` | 声音指令（描述音色、情绪、语速） |
| 1 | `model_choice` | `1.7B`（更高质量）或 `0.6B`（更快） |
| 1 | `language` | `Chinese`（必须显式指定） |
| 1 | `seed` | 每条独立 seed（`time.time()*1000 + i*7919`） |
| 2 `SaveAudio` | `filename_prefix` | 文件名前缀 `tts_<key>_<idx>` |

**输出格式**：FLAC，后缀自动加 `_00001.flac` 序号。

## Speaker 配置

> **必须按 `voice-character-design` 技能走完整方法论**：
> 1. 加载 `voice-character-design`
> 2. 读五维声学特征 + 音域物理
> 3. 读数值参数（temperature/top_p/repetition_penalty/max_new_tokens）
> 4. 用角色配置卡模板填每个 speaker
> 5. 跨角色区分度验证 + BGM 协调
> 6. 复制配置卡到 `{game_key}/voice/voices.json`

每个 speaker 必须有**独立的 instruct 描述**。

**禁止**：
- 5-20 词短 prompt
- 多个角色用同一段 prompt 改 temperature 凑数
- instruct 写 `Chinese female`（要写 `Chinese **Mandarin** female`）
- 不填数值参数就提交

## TTS 静音问题

| 根因 | 现象 | 修复 |
|------|------|------|
| `max_new_tokens` 过大 | 短文本前导 0.7s 静音后开始读 | 按字符数分级设置 |
| instruct 含"懒散"信号词 | 语速偏慢、拖音 | 用"crisp/focused/forward-moving/never dragging" |
| `repetition_penalty` 过低 | 偶发复读拖节奏 | 1.05 → 1.10 |
| infill 参数未设置 | 模型不知道在哪停 | 确保标点规范（，。？！等） |

**max_new_tokens 分级**：
- ≤6 字符 → 256
- ≤12 字符 → 320
- ≤25 字符 → 512
- ≤50 字符 → 768
- >50 字符 → 1024

## 音色确认流程

1. 为每个角色设计 **3 个候选变体**（不同 instruct focus）
2. 生成 18 个样本（6 角色 × 3 变体）→ 供用户试听
3. 用户听完后选编号（如"邱苏晚=v2"）
4. 将选中变体的 instruct + 数值参数写回 `voices.json`
5. 锁定 `seed`（跨角色间隔 1-5，确保各角色不同）
6. 全量生成时用锁定的 seed，确保跨场景音色稳定

## 避坑汇总

| # | 坑 | 现象 | 修复 |
|---|----|------|------|
| 1 | 节点 1 字段名错 | 写入 prompt 不生效 | 字段名是 `text` |
| 2 | 节点 2 字段名错 | 写入 prefix 不生效 | 字段名是 `filename_prefix` |
| 3 | seed 固定 | 多个 prompt 输出雷同 | 用 `int(time.time()*1000) + i*7919` |
| 4 | 所有 speaker 用同一 instruct | 听起来像一个人在演所有角色 | 每 speaker 独立 instruct |
| 5 | 模型显存 OOM | 1.7B 占 ~4GB | 改 0.6B 或设 `precision=fp16` |
| 6 | 输出格式不匹配 | 期望 mp3 实际 flac | flac 改后缀即可 |

## voice-acting-skill 桥接管线

> 使用 `voice-acting-skill` 的 TTS 适配器。BGM/SFX/AMB/FX 仍走 ComfyUI 管线。

**适用场景**：需要更高音色区分度、或 ComfyUI TTS 节点不稳定时。

**支持的引擎**：

| 引擎 | 说明 |
|------|------|
| `qwen` | 默认，支持本地 Gradio 或 DashScope 云端 |
| `cosy` | 需要本地 CosyVoice Gradio 服务 + prompt wav |
| `comfy` | 回退到 ComfyUI 管线（不推荐） |

**与 ComfyUI 路线的差异**：

| 维度 | ComfyUI 管线 | voice-acting-skill 管线 |
|------|-------------|----------------------|
| TTS 引擎 | ComfyUI Qwen3 TTS 节点 | 独立 TTS 适配器（QwenTTS/CosyVoice） |
| 音色控制 | instruct prompt + seed | voice_id + instruct（区分度更高） |
| 显存占用 | 额外 ~4GB（1.7B 模型） | 无（独立服务） |
| 服务依赖 | ComfyUI 已运行 | 额外 TTS 服务（可远端） |
| 方言支持 | 无 | CosyVoice 支持方言音色 |
