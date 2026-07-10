import re

from vaslib.types.script import Line
from vaslib.types.analysis import ScriptAnalysis
from vaslib.types.batch import BatchPlan, Batch, TiltCorrection

CHARS_PER_SECOND = 4
TARGET_BATCH_SECONDS = 15
BATCH_MARGIN_SECONDS = 2
MAX_BATCH_SECONDS = TARGET_BATCH_SECONDS - BATCH_MARGIN_SECONDS  # 13
TILT_TOLERANCE = 0.2


def estimate_line_duration(line: Line) -> float:
    """估算单句台词的配音时长（秒）。"""
    if line.type == "action" or not line.text:
        return 0.0

    text = line.text
    char_count = len(re.sub(r"[^\u4e00-\u9fff\w]", "", text))
    duration = char_count / CHARS_PER_SECOND

    punctuation_pauses = len(re.findall(r"[。！？]", text)) * 0.5
    comma_pauses = len(re.findall(r"[，、；]", text)) * 0.2
    duration += punctuation_pauses + comma_pauses

    duration += line.pause_before + line.pause_after
    return duration


def correct_tilt(estimated_duration: float, target_duration: float) -> TiltCorrection | None:
    """检测并修正批次时长倾斜。"""
    ratio = estimated_duration / target_duration

    if (1 - TILT_TOLERANCE) <= ratio <= (1 + TILT_TOLERANCE):
        return None

    speed_adjustment = round(target_duration / estimated_duration, 2)

    if ratio > 1 + TILT_TOLERANCE:
        reason = (
            f"配音过长: 估算{estimated_duration:.1f}s > "
            f"目标{target_duration:.1f}s，需加速"
        )
    else:
        reason = (
            f"配音过短: 估算{estimated_duration:.1f}s < "
            f"目标{target_duration:.1f}s，需减速"
        )

    return TiltCorrection(
        original_estimate=estimated_duration,
        target_duration=target_duration,
        speed_adjustment=speed_adjustment,
        reason=reason,
    )


def create_batch_plan(analysis: ScriptAnalysis) -> BatchPlan:
    """将剧本台词按 15 秒限制切分为批次，并提供倾斜修正。"""
    batches: list[Batch] = []

    for scene in analysis.scenes:
        speakable_lines = [l for l in scene.lines if l.type != "action"]
        if not speakable_lines:
            continue

        current_batch_lines: list[Line] = []
        current_duration = 0.0
        batch_counter = len(batches) + 1

        for line in speakable_lines:
            line_duration = estimate_line_duration(line)

            if current_duration + line_duration > MAX_BATCH_SECONDS and current_batch_lines:
                batch_id = f"batch-{batch_counter}"
                tilt_correction = correct_tilt(current_duration, MAX_BATCH_SECONDS)

                batches.append(Batch(
                    id=batch_id,
                    scene_id=scene.id,
                    lines=list(current_batch_lines),
                    estimated_duration_seconds=round(current_duration, 2),
                    target_duration_seconds=float(MAX_BATCH_SECONDS),
                    tilt_correction=tilt_correction,
                ))

                batch_counter += 1
                current_batch_lines = []
                current_duration = 0.0

            current_batch_lines.append(line)
            current_duration += line_duration

        if current_batch_lines:
            batch_id = f"batch-{batch_counter}"
            tilt_correction = correct_tilt(current_duration, MAX_BATCH_SECONDS)

            batches.append(Batch(
                id=batch_id,
                scene_id=scene.id,
                lines=current_batch_lines,
                estimated_duration_seconds=round(current_duration, 2),
                target_duration_seconds=float(MAX_BATCH_SECONDS),
                tilt_correction=tilt_correction,
            ))

    total_lines = sum(len(b.lines) for b in batches)
    avg_lines = round(total_lines / len(batches), 1) if batches else 0.0

    return BatchPlan(
        batches=batches,
        total_batches=len(batches),
        average_lines_per_batch=avg_lines,
        overflow_strategy="split_line",
    )
