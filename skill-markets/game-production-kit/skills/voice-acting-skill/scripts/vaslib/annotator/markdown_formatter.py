"""
将三引擎注音数据格式化为人类可读的 Markdown 报告。
"""

from __future__ import annotations

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


def _total_lines(batches: list) -> int:
    """统计所有 batch 中的总行数。"""
    return sum(len(b.lines) for b in batches)


# ---------------------------------------------------------------------------
# Qwen TTS
# ---------------------------------------------------------------------------


def _format_qwen_line(line: QwenTtsLine) -> str:
    """格式化单行 Qwen TTS 台词为 Markdown 表格行。"""
    rows = [
        "| **音色** | `{}` |".format(line.voice),
        "| **语速** | `{}` |".format(line.speed),
        "| **语言** | `{}` |".format(line.language_type),
        "| **情感** | `{}` |".format(
            "有标签" if line.annotated_text != line.text else "无",
        ),
    ]
    rows.append("")
    rows.append("**原文**:")
    rows.append("")
    rows.append(line.text)
    rows.append("")
    rows.append("**注音文本**:")
    rows.append("")
    rows.append(f"```\n{line.annotated_text}\n```")
    return "\n".join(rows)


def _format_qwen_batch(batch: QwenTtsBatch) -> str:
    """格式化单个 Qwen TTS batch。"""
    parts = [f"## Batch: {batch.batch_id}", ""]
    for i, line in enumerate(batch.lines, 1):
        parts.append(f"### {i}. {line.line_id}")
        parts.append("")
        parts.append(_format_qwen_line(line))
        parts.append("---")
        parts.append("")
    return "\n".join(parts)


def format_qwen_tts_markdown(annotation: QwenTtsAnnotation) -> str:
    """将 QwenTtsAnnotation 格式化为 Markdown 字符串。"""
    total = _total_lines(annotation.batches)
    lines = [
        "# Qwen TTS 注音剧本",
        "",
        "## 引擎信息",
        "",
        "| 属性 | 值 |",
        "|------|-----|",
        "| **引擎** | `{}` |".format(annotation.engine),
        "| **模型** | `{}` |".format(annotation.model),
        "| **总批次** | `{}` |".format(len(annotation.batches)),
        "| **总句数** | `{}` |".format(total),
        "",
    ]
    for batch in annotation.batches:
        lines.append(_format_qwen_batch(batch))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CosyVoice
# ---------------------------------------------------------------------------


def _format_cosy_line(line: CosyVoiceLine) -> str:
    """格式化单行 CosyVoice 台词。"""
    ref_audio = line.ref_audio_path if line.ref_audio_path else "无"
    ref_text_display = line.ref_text if line.ref_text else "无"
    rows = [
        "| **音色** | `{}` |".format(line.spk_id),
        "| **语速** | `{}` |".format(line.speed),
        "| **参考音频** | `{}` |".format(ref_audio),
        "| **流式** | `{}` |".format(line.stream),
        "| **指令** | `{}` |".format(line.instruct_text),
    ]
    rows.append("")
    rows.append("**拼音文本**:")
    rows.append("")
    rows.append(f"```\n{line.tts_text}\n```")
    if ref_text_display != "无":
        rows.append("")
        rows.append("**参考文本**:")
        rows.append(ref_text_display)
    return "\n".join(rows)


def _format_cosy_batch(batch: CosyVoiceBatch) -> str:
    """格式化单个 CosyVoice batch。"""
    parts = [f"## Batch: {batch.batch_id}", ""]
    for i, line in enumerate(batch.lines, 1):
        parts.append(f"### {i}. {line.line_id}")
        parts.append("")
        parts.append(_format_cosy_line(line))
        parts.append("---")
        parts.append("")
    return "\n".join(parts)


def format_cosy_voice_markdown(annotation: CosyVoiceAnnotation) -> str:
    """将 CosyVoiceAnnotation 格式化为 Markdown 字符串。"""
    total = _total_lines(annotation.batches)
    lines = [
        "# CosyVoice 注音剧本",
        "",
        "## 引擎信息",
        "",
        "| 属性 | 值 |",
        "|------|-----|",
        "| **引擎** | `{}` |".format(annotation.engine),
        "| **模型** | `{}` |".format(annotation.model),
        "| **模式** | `{}` |".format(annotation.mode),
        "| **总批次** | `{}` |".format(len(annotation.batches)),
        "| **总句数** | `{}` |".format(total),
        "",
    ]
    for batch in annotation.batches:
        lines.append(_format_cosy_batch(batch))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# OmniVoice
# ---------------------------------------------------------------------------


def _format_omni_line(line: OmniVoiceLine) -> str:
    """格式化单行 OmniVoice 台词。"""
    ref_audio = line.ref_audio_path if line.ref_audio_path else "无"
    ref_text_display = line.ref_text if line.ref_text else "无"
    pinyin_items = "、".join(
        f"{k}[{v}]" for k, v in line.pinyin_overrides.items()
    ) if line.pinyin_overrides else "无"
    rows = [
        "| **语言** | `{}` |".format(line.language),
        "| **音色设计** | `{}` |".format(line.instruct),
        "| **副语言标签** | `{}` |".format(
            "有" if any(tag in line.text for tag in ["[anger]", "[laughter]", "[sigh]", "[surprise-ah]", "[breath]"]) else "无",
        ),
        "| **拼音覆盖** | `{}` |".format(pinyin_items),
    ]
    rows.append("")
    rows.append("**原文**:")
    rows.append("")
    rows.append(line.text)
    if ref_text_display != "无":
        rows.append("")
        rows.append("**参考文本**:")
        rows.append(ref_text_display)
    if ref_audio != "无":
        rows.append("")
        rows.append("**参考音频**: `{}`".format(ref_audio))
    return "\n".join(rows)


def _format_omni_batch(batch: OmniVoiceBatch) -> str:
    """格式化单个 OmniVoice batch。"""
    parts = [f"## Batch: {batch.batch_id}", ""]
    for i, line in enumerate(batch.lines, 1):
        parts.append(f"### {i}. {line.line_id}")
        parts.append("")
        parts.append(_format_omni_line(line))
        parts.append("---")
        parts.append("")
    return "\n".join(parts)


def format_omni_voice_markdown(annotation: OmniVoiceAnnotation) -> str:
    """将 OmniVoiceAnnotation 格式化为 Markdown 字符串。"""
    total = _total_lines(annotation.batches)
    lines = [
        "# OmniVoice 注音剧本",
        "",
        "## 引擎信息",
        "",
        "| 属性 | 值 |",
        "|------|-----|",
        "| **引擎** | `{}` |".format(annotation.engine),
        "| **模型** | `{}` |".format(annotation.model),
        "| **总批次** | `{}` |".format(len(annotation.batches)),
        "| **总句数** | `{}` |".format(total),
        "",
    ]
    for batch in annotation.batches:
        lines.append(_format_omni_batch(batch))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 三合一报告
# ---------------------------------------------------------------------------


def format_all_markdown(
    qwen: QwenTtsAnnotation,
    cosy: CosyVoiceAnnotation,
    omni: OmniVoiceAnnotation,
) -> str:
    """生成三引擎注音 Markdown 报告，用 --- 分隔。"""
    parts = [
        format_qwen_tts_markdown(qwen),
        "---",
        format_cosy_voice_markdown(cosy),
        "---",
        format_omni_voice_markdown(omni),
    ]
    return "\n\n".join(parts)
