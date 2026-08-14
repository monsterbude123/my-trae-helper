---
name: voice-assigner
description: 角色音色分配子技能。根据角色属性（性别、年龄、方言）将每个角色映射到 QwenTTS / CosyVoice / OmniVoice 三引擎的具体音色。触发词：音色、角色映射、方言、QwenTTS 音色、CosyVoice 音色、OmniVoice 音色、voice assignment、dialect mapping。
---

# Voice Assigner 音色分配子技能

## 职责

消费 `parsed/script.json`，为每个角色生成三引擎的音色配置（`voice_id` + `speed` + `instruct`），输出 `analyzed/script-analysis.json`。

## 关键函数

| 函数 | 位置 | 作用 |
|------|------|------|
| `assign_voices(parsed, overrides?)` | `scripts/vaslib/analyzer/voice_assigner.py` | 入口：为所有角色分配三引擎音色 |
| `match_qwen_voice(char)` | 同上 | QwenTTS 音色匹配（按方言 + 性别） |
| `match_cosy_voice(char)` | 同上 | CosyVoice spk_id 匹配 |
| `match_omni_voice(char)` | 同上 | OmniVoice voice prompt 匹配 |

## 方言→音色映射

| 方言 | 引擎音色 | 备注 |
|------|----------|------|
| 渝普 / 川渝 | **Sunny** | 适用于 CosyVoice / OmniVoice，QwenTTS 需映射到对应方言音色 |
| 东北口音 | **Ethan** | |
| 沪普 | **Jada** | |
| 北京口音 | **Dylan** | |
| 天津口音 | **Dylan** | 同北京口音 |
| 普通话（无方言） | **默认女声 Cherry / 默认男声 Ryan** | 由性别二选一 |

> 完整映射表（含所有方言）、三引擎命名约定 → `references/modules/voice-assigner.md`

## 匹配优先级

```
1. 手动指定（用户在 assets/configs/*.yaml 中覆盖）
2. 方言 hint（角色元信息里的方言描述）
3. 性别 + 年龄（无方言时按默认女声/男声/童声）
4. 角色类型（旁白 → 统一音色，不分性别）
```

> 手动覆盖示例、匹配失败兜底、完整代码示例 → `references/modules/voice-assigner.md`

## 多音字词典

`scripts/vaslib/config/voices.py` 的 `POLYPHONE_DICT`（**81 词**），提供 `resolve_polyphones(text)` 和 `get_pinyin_overrides(text)` 两个工具函数，被 `annotation-generator` 复用。

> 81 词分组（金融/生活/人名/成语）、具体词条列表 → `references/modules/voice-assigner.md`

## 输入 / 输出

- **输入**：`output/parsed/script.json`
- **输出**：`output/analyzed/script-analysis.json`（含 `voice_map` 字段）

## 关联技能

- 上游：`script-parser`
- 下游：`annotation-generator`（消费 voice_map）、`tts-synthesizer`（直接消费 voice_map 调 API）

## 详细参考

- 模块详解（含完整代码示例、三引擎命名约定、兜底策略）→ `references/modules/voice-assigner.md`
- 音色配置：`scripts/vaslib/config/voices.py`
- 类型定义：`scripts/vaslib/types/analysis.py`（`VoiceAssignment`, `VoiceMap`）
- 决策记录：`references/DECISIONS.md` 中"音色分配优先级"决策
- 铁律：`references/CONSTRAINTS.md` 中"方言口音必须为每个角色明确指定"铁律
