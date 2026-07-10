# annotation-generator 模块

**对应源码**: `scripts/vaslib/annotator/annotation_generator.py` + `markdown_formatter.py`

## 职责

将 `BatchPlan` 转换为 QwenTTS / CosyVoice / OmniVoice 三个引擎的注音 JSON + Markdown 审核报告。

## 关键函数

### generate_all(batch_plan, analysis) -> dict

**主入口**。调用三个 `generate_*` 函数，返回 `{"qwen": ..., "cosy": ..., "omni": ...}`。

### generate_qwen_tts(batch_plan, analysis) -> QwenTtsAnnotation

为每行台词添加：
- 情感标签 `<|emotion-xxx|>...<|emotion-end|>`
- 音色 voice_id
- 语速 speed
- 语言类型 language_type="Chinese"

**情感标签映射**：

| 剧本情感 | QwenTTS 标签 |
|---|---|
| 愤怒 | `<|emotion-angry|>` |
| 开心 | `<|emotion-happy|>` |
| 悲伤 | `<|emotion-sad|>` |
| 恐惧/惊慌 | `<|emotion-terrified|>` |
| 深情/傲娇 | `<|emotion-affectionate|>` |
| 耳语/淡定/从容 | `<|emotion-whisper|>` |

### generate_cosy_voice(batch_plan, analysis) -> CosyVoiceAnnotation

为每行台词添加：
- speaker id `longxiaochun`
- instruct 文本（方言+情感+性格）
- 多音字注音 `词[拼音]`（来自 POLYPHONE_DICT）
- 参考音频 ref_audio_path
- 参考文本 ref_text
- 流式开关 stream=true

### generate_omni_voice(batch_plan, analysis) -> OmniVoiceAnnotation

为每行台词添加：
- 副语言标签（叹息、笑声、惊讶）
- 拼音覆盖 phoneme_overrides（多音字）
- 音色设计（来自 voice_assigner）

**副语言标签**：

| 剧本情感 | OmniVoice 标签 |
|---|---|
| 愤怒 | `[anger]` |
| 开心/无厘头 | `[laughter]` |
| 悲伤 | `[sigh]` |
| 恐惧/惊慌/夸张 | `[surprise-ah]` |
| 深情/傲娇 | `[breath]` |

## 多音字处理

`POLYPHONE_DICT` 包含 81 个词条（详见 `assets/configs/polyphone-dictionary.md`）。

- 长词优先匹配（`行长` > `银行`）
- `resolve_polyphones(text)` 返回带 `[拼音]` 标记的文本
- `get_pinyin_overrides(text)` 返回 `{词: pinyin_with_tone_number}`

## Markdown 格式化

`markdown_formatter.py` 提供 `format_*_markdown` 函数：

- `format_qwen_tts_markdown(annotation)` → Markdown 表格 + 原文 + 注音文本
- `format_cosy_voice_markdown(annotation)` → 同上 + instruct 展示
- `format_omni_voice_markdown(annotation)` → 同上 + 副语言标签展示
- `format_all_markdown(qwen, cosy, omni)` → 三合一报告（用 `---` 分隔）

## 输出

```
annotated/
├── qwen-tts.json + .md
├── cosyvoice.json + .md
├── omnivoice.json + .md
└── all-engines.md  ← 三引擎合并报告，用于人工审核
```

## 测试

`scripts/tests/test_core.py::TestGenerateAll` - 5 个测试用例。
