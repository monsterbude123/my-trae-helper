"""
三引擎注音规则生成器。

接收已切分的批次和分析结果，生成每个引擎专用的注音JSON。
"""

from __future__ import annotations

from vaslib.config.voices import (
    COSYVOICE_DEFAULT_VOICE_ID,
    POLYPHONE_DICT,
    OMNIVOICE_GENDER_MAP,
    OMNIVOICE_AGE_MAP,
    OMNIVOICE_DIALECT_MAP,
    OMNIVOICE_INSTRUCT_GENDER,
    OMNIVOICE_INSTRUCT_AGE,
    get_pinyin_overrides,
)
from vaslib.types.analysis import ScriptAnalysis, VoiceAssignment
from vaslib.types.annotation import (
    CosyVoiceAnnotation,
    CosyVoiceBatch,
    CosyVoiceLine,
    OmniVoiceAnnotation,
    OmniVoiceBatch,
    OmniVoiceLine,
    QwenTtsAnnotation,
    QwenTtsBatch,
    QwenTtsLine,
)
from vaslib.types.batch import BatchPlan
from vaslib.types.script import Character, Line, LineType

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

EMOTION_TAG_MAP: dict[str, str] = {
    "愤怒": "<|emotion-angry|>",
    "开心": "<|emotion-happy|>",
    "悲伤": "<|emotion-sad|>",
    "耳语": "<|emotion-whisper|>",
    "恐惧": "<|emotion-terrified|>",
    "惊慌": "<|emotion-terrified|>",
    "深情": "<|emotion-affectionate|>",
    "傲娇": "<|emotion-affectionate|>",
    "反差萌": "<|emotion-happy|>",
    "无厘头": "<|emotion-happy|>",
    "痞气": "<|emotion-angry|>",
    "淡定": "<|emotion-whisper|>",
    "从容": "<|emotion-whisper|>",
    "夸张": "<|emotion-terrified|>",
    "严肃": "<|emotion-angry|>",
}

EMOTION_END_TAG: str = "<|emotion-end|>"

OMNIVOICE_EMOTION_TAGS: dict[str, str] = {
    "愤怒": "[anger]",
    "开心": "[laughter]",
    "悲伤": "[sigh]",
    "恐惧": "[surprise-ah]",
    "惊慌": "[surprise-ah]",
    "深情": "[breath]",
    "傲娇": "[breath]",
    "无厘头": "[laughter]",
    "反差萌": "[laughter]",
    "夸张": "[surprise-ah]",
}


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


def resolve_polyphones(text: str) -> str:
    """
    按 POLYPHONE_DICT 替换文本中的多音字为 `词[拼音]` 格式。

    按词长度排序(长词优先匹配)，用 str.replace 替换。
    """
    sorted_words = sorted(POLYPHONE_DICT.keys(), key=len, reverse=True)
    result = text
    for word in sorted_words:
        pinyin = POLYPHONE_DICT[word]["default"]
        result = result.replace(word, f"{word}[{pinyin}]")
    return result


def find_voice_assignment(
    analysis: ScriptAnalysis,
    character_id: str | None,
) -> VoiceAssignment | None:
    """根据 character_id 查找对应的音色分配，找不到返回 None."""
    if character_id is None:
        return None
    for va in analysis.voice_assignments:
        if va.character_id == character_id:
            return va
    return None


def _find_character(analysis: ScriptAnalysis, character_id: str | None) -> Character | None:
    """根据 character_id 查找角色信息。"""
    if character_id is None:
        return None
    for c in analysis.meta.characters:
        if c.id == character_id:
            return c
    return None


def build_qwen_annotated_text(text: str, emotion_hint: str) -> str:
    """为 Qwen TTS 构建情感标签包裹的注音文本。

    如果 emotion_hint 有匹配的 EMOTION_TAG_MAP，返回 "{tag}{text}{end_tag}"；
    否则返回原 text。emotion_hint 支持逗号分隔的多个情感关键词。
    """
    # 拆分逗号分隔的情感提示，取第一个匹配的标签
    for hint_keyword in emotion_hint.replace("，", ",").split(","):
        hint_keyword = hint_keyword.strip()
        if not hint_keyword:
            continue
        tag = EMOTION_TAG_MAP.get(hint_keyword)
        if tag is not None:
            return f"{tag}{text}{EMOTION_END_TAG}"
    return text


# ---------------------------------------------------------------------------
# Qwen TTS
# ---------------------------------------------------------------------------


def generate_qwen_tts(
    batch_plan: BatchPlan,
    analysis: ScriptAnalysis,
) -> QwenTtsAnnotation:
    """生成 Qwen TTS 引擎注音数据。"""
    batches: list[QwenTtsBatch] = []

    for batch in batch_plan.batches:
        lines: list[QwenTtsLine] = []

        for line in batch.lines:
            # 过滤 action 行
            if line.type == "action":
                continue

            va = find_voice_assignment(analysis, line.character_id)
            voice = (
                va.qwen_tts.voice_id
                if va is not None
                else "Cherry"
            )

            annotated_text = build_qwen_annotated_text(line.text, line.emotion_hint)

            qwen_line = QwenTtsLine(
                line_id=line.id,
                text=line.text,
                annotated_text=annotated_text,
                voice=voice,
                speed=1.0,
                language_type="Chinese",
            )
            lines.append(qwen_line)

        if lines:
            batches.append(QwenTtsBatch(batch_id=batch.id, lines=lines))

    return QwenTtsAnnotation(
        engine="qwen-tts",
        model="qwen3-tts-flash-2025-11-27",
        batches=batches,
    )


# ---------------------------------------------------------------------------
# CosyVoice
# ---------------------------------------------------------------------------


def _build_cosy_instruct_text(
    va: VoiceAssignment | None,
    character: Character | None,
    emotion_hint: str,
) -> str:
    """构建 CosyVoice instructText (voice template + emotion)。"""
    template = (
        va.cosyvoice.instruct_template
        if va is not None
        else "{personality}，{emotion}"
    )
    personality = character.personality if character is not None else ""
    emotion = emotion_hint if emotion_hint else ""
    return template.format(personality=personality, emotion=emotion)


def generate_cosy_voice(
    batch_plan: BatchPlan,
    analysis: ScriptAnalysis,
) -> CosyVoiceAnnotation:
    """生成 CosyVoice 引擎注音数据。"""
    batches: list[CosyVoiceBatch] = []

    for batch in batch_plan.batches:
        lines: list[CosyVoiceLine] = []

        for line in batch.lines:
            if line.type == "action":
                continue

            va = find_voice_assignment(analysis, line.character_id)
            character = _find_character(analysis, line.character_id)

            tts_text = resolve_polyphones(line.text)
            instruct_text = _build_cosy_instruct_text(
                va, character, line.emotion_hint,
            )

            cosy_line = CosyVoiceLine(
                line_id=line.id,
                tts_text=tts_text,
                spk_id=COSYVOICE_DEFAULT_VOICE_ID,
                instruct_text=instruct_text,
                ref_audio_path=va.cosyvoice.ref_audio_path if va is not None else None,
                ref_text=line.text if va is not None else None,
                speed=1.0,
                stream=True,
            )
            lines.append(cosy_line)

        if lines:
            batches.append(CosyVoiceBatch(batch_id=batch.id, lines=lines))

    return CosyVoiceAnnotation(
        engine="cosyvoice",
        model="cosyvoice-v2",
        mode="instruct",
        batches=batches,
    )


# ---------------------------------------------------------------------------
# OmniVoice
# ---------------------------------------------------------------------------


def _build_omni_instruct(
    va: VoiceAssignment | None,
    character: Character | None,
) -> str:
    """构建 OmniVoice instruct (音色设计提示词)。"""
    template = (
        va.omnivoice.voice_design
        if va is not None
        else "{gender}, {age}"
    )
    if character is None:
        return template.format(gender="男", age="青年")
    gender_label = OMNIVOICE_INSTRUCT_GENDER.get(character.gender, "Male / 男")
    age_label = OMNIVOICE_INSTRUCT_AGE.get(character.age, "Young Adult / 青年")
    return template.format(gender=gender_label, age=age_label)


def generate_omni_voice(
    batch_plan: BatchPlan,
    analysis: ScriptAnalysis,
) -> OmniVoiceAnnotation:
    """生成 OmniVoice 引擎注音数据。"""
    batches: list[OmniVoiceBatch] = []

    for batch in batch_plan.batches:
        lines: list[OmniVoiceLine] = []

        for line in batch.lines:
            if line.type == "action":
                continue

            va = find_voice_assignment(analysis, line.character_id)
            character = _find_character(analysis, line.character_id)

            # 添加情感标签到文本前（支持逗号分隔的多个情感）
            emotion_tag = ""
            for hint_keyword in line.emotion_hint.replace("，", ",").split(","):
                hint_keyword = hint_keyword.strip()
                if not hint_keyword:
                    continue
                tag = OMNIVOICE_EMOTION_TAGS.get(hint_keyword)
                if tag:
                    emotion_tag = tag
                    break
            annotated_text = f"{emotion_tag}{line.text}" if emotion_tag else line.text

            # 获取拼音覆盖
            pinyin_overrides = get_pinyin_overrides(line.text)

            # 构建 instruct
            instruct = _build_omni_instruct(va, character)

            # 确定语言
            language = "Chinese"
            if character is not None and character.dialect_hint in OMNIVOICE_DIALECT_MAP:
                language = OMNIVOICE_DIALECT_MAP[character.dialect_hint]

            omni_line = OmniVoiceLine(
                line_id=line.id,
                text=annotated_text,
                language=language,
                pinyin_overrides=pinyin_overrides,
                instruct=instruct,
                ref_audio_path=va.omnivoice.ref_audio_path if va is not None else None,
                ref_text=line.text if va is not None else None,
            )
            lines.append(omni_line)

        if lines:
            batches.append(OmniVoiceBatch(batch_id=batch.id, lines=lines))

    return OmniVoiceAnnotation(
        engine="omnivoice",
        model="k2-fsa/OmniVoice",
        batches=batches,
    )


# ---------------------------------------------------------------------------
# 统一入口
# ---------------------------------------------------------------------------


def generate_all(
    batch_plan: BatchPlan,
    analysis: ScriptAnalysis,
) -> dict[str, QwenTtsAnnotation | CosyVoiceAnnotation | OmniVoiceAnnotation]:
    """生成所有三个引擎的注音数据。

    返回 {"qwen": ..., "cosy": ..., "omni": ...}.
    """
    return {
        "qwen": generate_qwen_tts(batch_plan, analysis),
        "cosy": generate_cosy_voice(batch_plan, analysis),
        "omni": generate_omni_voice(batch_plan, analysis),
    }
