---
name: annotation-generator
description: 注音规则生成子技能。把批次化剧本转换为 QwenTTS / CosyVoice / OmniVoice 三引擎专属的注音规则剧本（JSON + Markdown 审核报告）。触发词：注音、QwenTTS 情感标签、CosyVoice 指令、OmniVoice 拼音、annotation、polyphone、emotion tag。
---

# Annotation Generator 注音规则生成子技能

## 职责

消费 `analyzed/batch-plan.json` + `analyzed/script-analysis.json`，**并行**生成三引擎的注音规则剧本，输出 `annotated/{qwen-tts,cosyvoice,omnivoice}.json + .md` + 并排审核报告 `annotated/all-engines.md`。

## 关键函数

| 函数 | 位置 | 作用 |
|------|------|------|
| `generate_all(batch_plan, analysis)` | `scripts/vaslib/annotator/annotation_generator.py` | 入口：三引擎并行生成 |
| `generate_qwen_tts(batch, line, voice)` | 同上 | QwenTTS 注音（情感标签 + speed） |
| `generate_cosy_voice(batch, line, voice)` | 同上 | CosyVoice 注音（拼音 + instruct） |
| `generate_omni_voice(batch, line, voice)` | 同上 | OmniVoice 注音（pinyinOverrides + 副语言标签） |
| `format_*_markdown(...)` | `scripts/vaslib/annotator/markdown_formatter.py` | 渲染为可读 Markdown |
| `format_all_markdown(annotations)` | 同上 | 产出三引擎并排审核报告 |

## 三引擎注音格式速查

| 引擎 | 情感表达方式 | 消歧方式 |
|------|-------------|---------|
| QwenTTS | `<\|emotion-{angry\|happy\|sad\|whisper\|terrified\|affectionate}\|>...<\|emotion-end\|>` | 不支持 |
| CosyVoice | `instructText` 自然语言指令 | `银行[yín háng]` 拼音标注 |
| OmniVoice | `instruct` 中副语言标签 | `pinyinOverrides` Dict |

## 多音字词典

`scripts/vaslib/config/voices.py` 的 `POLYPHONE_DICT`（81 词）：

- 工具函数：`resolve_polyphones(text)` → 字符串（含拼音标注）
- 工具函数：`get_pinyin_overrides(text)` → `Dict[str, str]`（给 OmniVoice 用）

> 81 词分组清单（金融/生活/人名/成语）、消歧规则、完整映射 → `references/modules/annotation-generator.md`

## 输入 / 输出

- **输入**：
  - `output/analyzed/batch-plan.json`
  - `output/analyzed/script-analysis.json`
- **输出**：
  - `output/annotated/qwen-tts.{json,md}`
  - `output/annotated/cosyvoice.{json,md}`
  - `output/annotated/omnivoice.{json,md}`
  - `output/annotated/all-engines.md`（4 区块审核报告：元信息/角色音色/批次并排/异常清单）

## 关联技能

- 上游：`script-parser`、`voice-assigner`、`batch-manager`
- 下游：`tts-synthesizer`（消费三引擎 JSON 调 API）

## 详细参考

- 模块详解（含完整 JSON 输出示例 + 情感→标签映射表）：`references/modules/annotation-generator.md`
- 类型定义：`scripts/vaslib/types/annotation.py`
- 配置：`scripts/vaslib/config/voices.py`（`POLYPHONE_DICT` 81 词）
