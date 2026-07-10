from __future__ import annotations

import time


def build_timeline(
    batch_plan: dict,
    analysis: dict,
    cosyvoice_results: dict,
    omnivoice_merged_path: str | None,
) -> dict:
    """Build a project timeline with tracks for each TTS engine.

    Parameters are plain dicts (not pydantic models).

    Returns: ProjectTimeline-compatible dict
    """
    # Build character id → name map
    meta = analysis.get("meta") or {}
    char_name_map: dict[str, str] = {}
    for char in meta.get("characters", []):
        char_name_map[char["id"]] = char.get("name", char["id"])

    # Get cosyvoice results by line_id
    cosy_results_map: dict[str, dict] = {}
    if isinstance(cosyvoice_results, dict):
        raw_results = cosyvoice_results.get("results", [])
        if isinstance(raw_results, list):
            for r in raw_results:
                lid = r.get("line_id", r.get("lineId", ""))
                if lid:
                    cosy_results_map[lid] = r

    cosyvoice_clips: list[dict] = []
    omnivoice_clips: list[dict] = []
    cosy_time = 0.0
    omni_time = 0.0

    batches = batch_plan.get("batches", [])
    for batch in batches:
        batch_id = batch.get("id", "")
        scene_id = batch.get("scene_id", batch.get("sceneId", ""))
        for line in batch.get("lines", []):
            if line.get("type") == "action":
                continue

            line_id = line.get("id", "")
            char_id = line.get("characterId") or line.get("character_id", "")
            text = line.get("text", "")

            cosy_result = cosy_results_map.get(line_id)
            if cosy_result and cosy_result.get("status") == "success":
                cosyvoice_clips.append({
                    "lineId": line_id,
                    "batchId": batch_id,
                    "sceneId": scene_id,
                    "characterId": char_id,
                    "text": text,
                    "audioPath": cosy_result.get("audio_path", cosy_result.get("audioPath", "")),
                    "startTimeSeconds": cosy_time,
                    "durationSeconds": cosy_result.get("duration_seconds", cosy_result.get("durationSeconds", 0)),
                    "fadeInSeconds": 0.05,
                    "fadeOutSeconds": 0.05,
                })
                cosy_time += cosy_result.get("duration_seconds", cosy_result.get("durationSeconds", 0)) + 0.1

            omnivoice_clips.append({
                "lineId": line_id,
                "batchId": batch_id,
                "sceneId": scene_id,
                "characterId": char_id,
                "text": text,
                "audioPath": omnivoice_merged_path or "",
                "startTimeSeconds": omni_time,
                "durationSeconds": 0,
                "fadeInSeconds": 0.05,
                "fadeOutSeconds": 0.05,
            })
            omni_time += 2.0

    return {
        "projectId": f"project-{int(time.time() * 1000)}",
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        "totalDurationSeconds": max(cosy_time, omni_time),
        "tracks": [
            {"engine": "cosyvoice", "clips": cosyvoice_clips},
            {"engine": "omnivoice", "clips": omnivoice_clips},
        ],
    }


def build_voice_map(
    analysis: dict,
    batch_plan: dict,
    cosyvoice_annotation: dict | None = None,
) -> dict:
    """Build a voice mapping table from analysis and batch plan.

    Returns: VoiceMap-compatible dict
    """
    meta = analysis.get("meta") or {}
    voice_assignments = analysis.get("voice_assignments", analysis.get("voiceAssignments", []))

    # Build line_ids per character
    line_ids_by_char: dict[str, list[str]] = {}
    for batch in batch_plan.get("batches", []):
        for line in batch.get("lines", []):
            char_id = line.get("characterId") or line.get("character_id")
            if not char_id:
                continue
            if char_id not in line_ids_by_char:
                line_ids_by_char[char_id] = []
            line_ids_by_char[char_id].append(line.get("id", ""))

    characters: list[dict] = []
    for va in voice_assignments:
        char_id = va.get("character_id", va.get("characterId", ""))
        char = next(
            (c for c in meta.get("characters", []) if c.get("id", "") == char_id),
            None,
        )
        cosyvoice_config = va.get("cosyvoice", {})
        omnivoice_config = va.get("omnivoice", {})

        characters.append({
            "characterId": char_id,
            "characterName": char.get("name", char_id) if char else char_id,
            "cosyvoice": {
                "voiceId": cosyvoice_config.get("voice_id", cosyvoice_config.get("voiceId", "")),
                "instructTemplate": cosyvoice_config.get(
                    "instruct_template",
                    cosyvoice_config.get("instructTemplate", ""),
                ),
                "audioSample": "",
            },
            "omnivoice": {
                "voiceDesign": omnivoice_config.get(
                    "voice_design",
                    omnivoice_config.get("voiceDesign", ""),
                ),
                "audioSample": "",
            },
            "lineIds": line_ids_by_char.get(char_id, []),
        })

    return {"characters": characters}


def build_comparison_report(
    batch_plan: dict,
    analysis: dict,
    cosyvoice_results: dict,
    omnivoice_results: dict,
) -> dict:
    """Build a comparison report between CosyVoice and OmniVoice engines.

    Returns: ComparisonReport-compatible dict
    """
    meta = analysis.get("meta") or {}
    char_name_map: dict[str, str] = {}
    for char in meta.get("characters", []):
        char_name_map[char["id"]] = char.get("name", char["id"])

    # Flatten all non-action lines
    all_lines: list[dict] = []
    for batch in batch_plan.get("batches", []):
        for line in batch.get("lines", []):
            if line.get("type") != "action":
                all_lines.append(line)

    # Build cosyvoice results map by line_id
    cosy_map: dict[str, dict] = {}
    if isinstance(cosyvoice_results, dict):
        for r in cosyvoice_results.get("results", []):
            lid = r.get("line_id", r.get("lineId", ""))
            if lid:
                cosy_map[lid] = r

    omnivoice_status = omnivoice_results.get("status", "failed")
    omnivoice_merged_path = omnivoice_results.get("merged_audio_path", omnivoice_results.get("mergedAudioPath"))

    line_comparisons: list[dict] = []
    for line in all_lines:
        line_id = line.get("id", "")
        char_id = line.get("characterId") or line.get("character_id", "")
        char_name = char_name_map.get(char_id, "旁白") if char_id else "旁白"
        text = line.get("text", "")

        cosy = cosy_map.get(line_id, {})
        cosy_status = cosy.get("status", "failed")

        engines = {
            "cosyvoice": {
                "audioPath": cosy.get("audio_path", cosy.get("audioPath", "")),
                "durationSeconds": cosy.get("duration_seconds", cosy.get("durationSeconds", 0)),
                "latencyMs": cosy.get("latency_ms", cosy.get("latencyMs", 0)),
                "status": cosy_status if cosy_status == "success" else "failed",
                "error": cosy.get("error", None),
            },
            "omnivoice": {
                "audioPath": omnivoice_merged_path or "",
                "durationSeconds": 0,
                "latencyMs": 0,
                "status": "success" if omnivoice_status == "success" else "failed",
                "error": omnivoice_results.get("error", None),
            },
        }

        best_match = "cosyvoice" if cosy.get("status") == "success" else "omnivoice"

        line_comparisons.append({
            "lineId": line_id,
            "text": text,
            "characterName": char_name,
            "engines": engines,
            "bestMatch": best_match,
            "bestMatchReason": "",
        })

    # Count successes
    cosy_success_count = sum(
        1 for r in cosy_map.values() if r.get("status") == "success"
    )
    omni_success_count = len(all_lines) if omnivoice_results.get("status") == "success" else 0
    total_lines = len(all_lines)

    engine_summaries = [
        {
            "engine": "cosyvoice",
            "successRate": cosy_success_count / total_lines if total_lines > 0 else 0,
            "averageDurationSeconds": 0,
            "averageLatencyMs": 0,
            "totalCost": 0,
        },
        {
            "engine": "omnivoice",
            "successRate": omni_success_count / total_lines if total_lines > 0 else 0,
            "averageDurationSeconds": 0,
            "averageLatencyMs": 0,
            "totalCost": 0,
        },
    ]

    # Per-character success scores
    char_engine_map: dict[str, dict[str, int]] = {}
    for lc in line_comparisons:
        char_name = lc.get("characterName", "")
        if not char_name:
            continue
        if char_name not in char_engine_map:
            char_engine_map[char_name] = {"cosyvoice": 0, "omnivoice": 0}
        for engine_key, data in lc.get("engines", {}).items():
            if data.get("status") == "success":
                char_engine_map[char_name][engine_key] = (
                    char_engine_map[char_name].get(engine_key, 0) + 1
                )

    recommendations: list[dict] = []
    for char_name, scores in char_engine_map.items():
        best_engine = "cosyvoice"
        best_score = 0
        for engine_key, score in scores.items():
            if score > best_score:
                best_score = score
                best_engine = engine_key
        char_id = next(
            (c.get("id", "") for c in meta.get("characters", []) if c.get("name") == char_name),
            "",
        )
        recommendations.append({
            "characterId": char_id,
            "characterName": char_name,
            "recommendedEngine": best_engine,
            "reason": f"成功率最高: {best_score}/{scores.get(best_engine, 0)}",
        })

    return {
        "projectId": f"project-{int(time.time() * 1000)}",
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        "summary": {
            "totalLines": total_lines,
            "totalDurationSeconds": 0,
            "engines": engine_summaries,
        },
        "lineComparisons": line_comparisons,
        "recommendations": recommendations,
    }
