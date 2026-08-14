---
name: tts-synthesizer
description: 配音合成执行子技能。消费三引擎注音剧本，调用 CosyVoice / Qwen3-TTS / OmniVoice 服务（HTTP + Gradio）实际合成音频，并生成时间轴、声音地图、对照报告。触发词：配音合成、TTS 引擎、Gradio、API、合成、HTTP、timeline、voice map、comparison。
---

# TTS Synthesizer 配音合成子技能

## 职责

消费 `annotated/*.json` 三引擎注音剧本，调用真实 TTS 服务生成音频 WAV 文件，输出 `audio/{cosyvoice,omnivoice}/*.wav` + `project/{timeline,voice-map,comparison}.json`。

> QwenTTS 走 DashScope 商业 API 或本地化服务，本技能包默认聚焦 CosyVoice + OmniVoice 两个本地化引擎（详见 `references/DECISIONS.md`）。

## 关键类与函数

| 类 / 函数 | 位置 | 作用 |
|-----------|------|------|
| `CosyVoiceAdapter` | `scripts/vaslib/synthesizer/cosyvoice_adapter.py` | CosyVoice Gradio 客户端 |
| `OmniVoiceAdapter` | `scripts/vaslib/synthesizer/omnivoice_adapter.py` | OmniVoice 客户端 |
| `Adapter.health_check()` | 同上 | 健康检查：`GET /` 或 `GET /health` |
| `Adapter.synthesize_batch(batch)` | 同上 | 批量合成一个 Batch |
| `build_timeline(annotations, audio_dir)` | `scripts/vaslib/synthesizer/project_generator.py` | 生成 `project/timeline.json`（按毫秒对齐） |
| `build_voice_map(analysis, audio_dir)` | 同上 | 生成 `project/voice-map.json`（角色→音色→音频） |
| `build_comparison_report(...)` | 同上 | 生成 `project/comparison.json`（双引擎同一台词并排） |

## 默认服务地址

| 引擎 | 默认 URL | 启动命令参考 |
|------|----------|---------------|
| CosyVoice | `http://127.0.0.1:50000` | `python cosyvoice/webui.py --port 50000` |
| OmniVoice | `http://localhost:7860` | Gradio 默认端口 |

环境变量覆盖：

```bash
export COSYVOICE_URL=http://127.0.0.1:50000
export OMNIVOICE_URL=http://localhost:7860
```

## CosyVoice 适配器

- **传输协议**：HTTP POST JSON，**SSE 流式响应**
- **请求体**（`instruct` 模式）：

```json
{
  "tts_text": "银行[yín háng]行长[háng zhǎng]处理了这件事",
  "spk_id": "dylan_sft",
  "instruct_text": "用低沉男声，语速稍慢",
  "stream": true
}
```

- **响应**：SSE 事件流，base64 WAV 块拼接
- **错误处理**：HTTP 4xx 重试 3 次，5xx 报错并停止当前批

## OmniVoice 适配器

- **传输协议**：HTTP POST multipart，含参考音频 + 文本
- **请求体**：

```json
{
  "text": "行长",
  "language": "zh",
  "pinyin_overrides": {"行长": "hang2 zhang3"},
  "instruct": "[breath] 嗯哼"
}
```

- **响应**：完整 WAV 文件一次性返回
- **副语言标签**（`[laughter]` `[sigh]` `[breath]`）在 `instruct` 字段中传递

## 合成流程

```
annotated/cosyvoice.json
    │
    ▼ CosyVoiceAdapter.synthesize_batch(batch)
    │   逐 line 调 HTTP API
    │   流式接收 → 落盘 WAV
    ▼
audio/cosyvoice/{batchId}_{lineId}.wav
    │
    ▼ build_timeline / build_voice_map / build_comparison_report
    │
project/{timeline,voice-map,comparison}.json
```

## 健康检查

合成前**必须**调用 `adapter.health_check()`：

- 200 OK → 通过
- 连接拒绝 / 超时 → 报错并提示用户启动对应服务（给出启动命令）
- 4xx → 检查 API 路径是否正确

## 批量与重试

- 单批 ≤ 20 行时一次性 POST；> 20 行自动分片
- 网络错误：指数退避重试 3 次（1s / 2s / 4s）
- 合成失败行写入 `project/comparison.json` 的 `failures` 字段，不中断整批

## 输入 / 输出

- **输入**：
  - `output/annotated/cosyvoice.json` + `omnivoice.json`
  - `output/analyzed/script-analysis.json`
- **输出**：
  - `output/audio/cosyvoice/*.wav`
  - `output/audio/omnivoice/*.wav`
  - `output/project/timeline.json`
  - `output/project/voice-map.json`
  - `output/project/comparison.json`

## CLI 用法

```bash
# 启动 CosyVoice 后执行合成
vas synthesize \
  -o output \
  --cosyvoice-url http://127.0.0.1:50000 \
  --omnivoice-url http://localhost:7860 \
  --engines cosyvoice,omnivoice
```

## 关联技能

- 上游：`annotation-generator`
- 下游：（终端产物，音频文件可直接用于剪辑）

## 详细参考

- 决策日志：`references/DECISIONS.md`（为何先聚焦 CosyVoice + OmniVoice）
- 实施计划：`references/superpowers/plans/2026-05-05-phase1-script-annotation.md`
- 类型定义：`scripts/vaslib/types/synthesis.py`（`SynthesisResult`, `Timeline`, `ComparisonReport`）
