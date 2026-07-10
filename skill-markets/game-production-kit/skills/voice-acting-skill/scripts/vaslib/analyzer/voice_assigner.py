"""
角色属性 → TTS 引擎音色配置映射模块。

将剧本中的角色属性（性别、年龄、性格、方言）分别映射为
QwenTTS / CosyVoice / OmniVoice 三个引擎的音色配置。
"""

from vaslib.types.script import Character, ParsedScript
from vaslib.types.analysis import (
    ScriptAnalysis,
    VoiceAssignment,
    QwenTtsVoiceConfig,
    CosyVoiceVoiceConfig,
    OmniVoiceVoiceConfig,
)
from vaslib.config import (
    DIALECT_MAPPINGS,
    DEFAULT_DIALECT_MAPPING,
    QWEN_TTS_LANGUAGE_MAP,
    COSYVOICE_DEFAULT_VOICE_ID,
    OMNIVOICE_GENDER_MAP,
    OMNIVOICE_AGE_MAP,
    OMNIVOICE_DIALECT_MAP,
)


def match_qwen_voice(character: Character) -> QwenTtsVoiceConfig:
    """匹配 QwenTTS 音色配置。

    根据角色方言提示从 DIALECT_MAPPINGS 中查找 QwenTTS voice_id，
    未匹配时使用 DEFAULT_DIALECT_MAPPING。
    """
    mapping = DIALECT_MAPPINGS.get(character.dialect_hint, DEFAULT_DIALECT_MAPPING)
    return QwenTtsVoiceConfig(
        voice_id=mapping["qwen_tts_voice_id"],
        emotion_style="",
        language_type=QWEN_TTS_LANGUAGE_MAP.get(character.dialect_hint, "Chinese"),
    )


def match_cosy_voice(character: Character) -> CosyVoiceVoiceConfig:
    """匹配 CosyVoice 音色配置。

    从方言映射中获取 instruct 模板，
    将 {personality} 替换为角色性格，{emotion} 替换为空字符串。
    """
    mapping = DIALECT_MAPPINGS.get(character.dialect_hint, DEFAULT_DIALECT_MAPPING)
    instruct_template = (
        mapping["cosyvoice_instruct"]
        .replace("{personality}", character.personality)
        .replace("{emotion}", "")
    )
    return CosyVoiceVoiceConfig(
        voice_id=COSYVOICE_DEFAULT_VOICE_ID,
        instruct_template=instruct_template,
        ref_audio_path=None,
    )


def match_omni_voice(character: Character) -> OmniVoiceVoiceConfig:
    """匹配 OmniVoice 音色配置。

    通过 OMNIVOICE_GENDER_MAP / OMNIVOICE_AGE_MAP 将角色属性映射为中文描述，
    若角色有方言提示则追加方言描述，拼接为 voice_design。
    """
    gender = OMNIVOICE_GENDER_MAP[character.gender]
    age = OMNIVOICE_AGE_MAP[character.age]
    dialect = OMNIVOICE_DIALECT_MAP.get(character.dialect_hint, "")

    parts = [gender, age]
    if dialect:
        parts.append(dialect)
    voice_design = "，".join(parts)

    return OmniVoiceVoiceConfig(
        voice_design=voice_design,
        ref_audio_path=None,
        phoneme_overrides={},
    )


def assign_voices(parsed_script: ParsedScript) -> ScriptAnalysis:
    """为剧本中所有角色分配三引擎音色配置。

    遍历 parsed_script.meta.characters，对每个角色生成 VoiceAssignment，
    包含 QwenTTS / CosyVoice / OmniVoice 三组配置。
    """
    voice_assignments = [
        VoiceAssignment(
            character_id=character.id,
            qwen_tts=match_qwen_voice(character),
            cosyvoice=match_cosy_voice(character),
            omnivoice=match_omni_voice(character),
        )
        for character in parsed_script.meta.characters
    ]
    return ScriptAnalysis(
        meta=parsed_script.meta,
        scenes=parsed_script.scenes,
        voice_assignments=voice_assignments,
    )
