# voice-assigner 模块

**对应源码**: `scripts/vaslib/analyzer/voice_assigner.py`

## 职责

将 `ParsedScript` 中的角色属性（性别、年龄、性格、方言）分别映射为 QwenTTS / CosyVoice / OmniVoice 三个引擎的音色配置。

## 关键函数

### assign_voices(parsed: ParsedScript) -> ScriptAnalysis

**主入口**。遍历每个角色，调用三个 `match_*` 函数。

### match_qwen_voice(character) -> QwenTtsVoiceConfig

方言 → QwenTTS 音色 ID。

| 方言 | 音色 ID |
|---|---|
| 渝普/川渝 | Sunny |
| 东北口音 | Ethan |
| 沪普 | Jada |
| 北京口音 | Dylan |
| 天津口音 | Dylan |
| (默认) | Cherry |

### match_cosy_voice(character) -> CosyVoiceVoiceConfig

方言 → CosyVoice instruct 模板。

所有方言都使用同一个 speaker ID `longxiaochun`（默认 CosyVoice 中文女声），通过 instruct 区分方言。

模板格式：`用{方言}口音说话，{性格}，{emotion}`

### match_omni_voice(character) -> OmniVoiceVoiceConfig

组合音色设计描述：`男/女，中年/老年/...，方言`。

例：`貔貅` → `男，中年，四川话`
例：`凤` → `女，中年，上海话`

## 输入输出

```
ParsedScript
  └── characters[i] (Character)
       ├── id, name, gender, age
       ├── personality
       └── dialect_hint  ← 关键输入
            ↓
       match_qwen_voice  →  QwenTtsVoiceConfig(voice_id="Sunny", language_type="Chinese")
       match_cosy_voice  →  CosyVoiceVoiceConfig(voice_id="longxiaochun", instruct_template="用川渝口音说话...")
       match_omni_voice  →  OmniVoiceVoiceConfig(voice_design="男, 中年, 四川话", phoneme_overrides={})
            ↓
       VoiceAssignment
```

## 配置单一真相源

**所有方言相关配置都在 `scripts/vaslib/config/voices.py`**。

如需新增方言：
1. 在 `DIALECT_MAPPINGS` 添加条目
2. 在 `QWEN_TTS_LANGUAGE_MAP` 添加映射
3. 在 `OMNIVOICE_DIALECT_MAP` 添加映射
4. **不要** 在 voice_assigner.py 中硬编码

## 测试

`scripts/tests/test_core.py::TestAssignVoices` - 6 个测试用例。
