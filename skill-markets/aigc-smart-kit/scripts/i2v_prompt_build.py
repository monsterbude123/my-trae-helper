"""i2v_prompt_build.py — 跨平台 I2V 影视级 prompt 构造器 CLI。

读取 i2v-image-analyzer 产出的 image-report.json (image-schema v1.0)
+ 可选 user-keywords,输出三平台特化 prompt:
  - h3       : MiniMax H3 三段式 (description + soundscape + non_diegetic_music)
  - seedance : ByteDance Seedance 2.5 四拍弧线 (opening/progression/turn/resolution)
  - kling    : Kling 3.0 I2V 三段式 (subject+action / camera+style / constraints)

依赖: Python stdlib only (json / argparse / pathlib / copy)。
平台: Windows / macOS / Linux。

使用:
    python scripts/i2v_prompt_build.py \\
        --report out/image-report.json --platform h3 \\
        --duration 5 --keywords "温暖 电影感 推近" --out out/prompt-h3.txt

可灵 (kling) 子 skill 尚未沉淀,采用 Kling 3.0 I2V 通用公式兜底。
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

UNKNOWN = "unknown"
REQUIRED_TOP = ("subject", "scene", "cinematography", "aesthetic", "dynamic")
DEFAULT_SEGMENTS = {"h3": 3, "seedance": 4, "kling": 3}

def _get(d: Any, *keys: str, default: Any = None) -> Any:
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur

def _non_unknown(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() == UNKNOWN:
        return None
    if isinstance(value, (list, tuple, dict)) and len(value) == 0:
        return None
    return value

def _str_field(value: Any) -> str:
    """List/tuple → ', ' join → strip. Str → strip. None/'unknown' → ''."""
    v = _non_unknown(value)
    if v is None:
        return ""
    if isinstance(v, (list, tuple)):
        return ", ".join(str(x).strip() for x in v if x and str(x).strip())
    return str(v).strip()

def _join(parts: list, sep: str = ", ") -> str:
    return sep.join(p.strip() for p in parts if p and str(p).strip())

def _compact(value: Any) -> str:
    """精简 amplitude/speed 字段:含括号说明只取首段。"""
    if not value:
        return ""
    s = str(value).strip().split("(")[0].strip().rstrip(",").strip()
    return s


def _seg_split(duration: float, n: int = 3) -> list[tuple[str, str]]:
    """时间段切片:duration → [(start,end), ...]。例 8s,n=3 → 00:00-00:02 / 00:02-00:06 / 00:06-00:08。"""
    if duration <= 0 or n < 1:
        return []
    boundaries = [0.0, duration * 0.25, duration * 0.75, duration]
    if n >= 4:
        boundaries = [duration * i / n for i in range(n + 1)]

    def _fmt(t: float) -> str:
        if t < 0:
            t = 0.0
        m = int(t // 60)
        s = t - m * 60
        if abs(s - round(s)) < 0.01:
            return f"{m:02d}:{round(s):02d}"
        return f"{m:02d}:{s:04.1f}"

    pairs = []
    for i in range(n):
        pairs.append((_fmt(boundaries[i]), _fmt(boundaries[i + 1])))
    return pairs

def _validate(report: dict) -> None:
    missing = [k for k in REQUIRED_TOP if k not in report]
    if missing:
        raise ValueError(
            f"image-report.json 缺必填顶层字段: {', '.join(missing)} "
            f"(image-schema v1.0 §0)"
        )

_KW_LEX: dict[str, list[str]] = {
    "camera": ["推近", "拉远", "推", "拉", "摇", "移", "环绕", "固定", "跟拍",
               "推镜头", "zoom", "dolly", "pan", "tilt", "orbit", "tracking", "static", "lock"],
    "style":  ["电影感", "胶片", "写实", "二次元", "动漫", "3d", "油画", "极简", "复古", "黑白",
               "anime", "cinematic", "film", "realistic", "3d-render", "painting", "minimal"],
    "mood":   ["温暖", "紧张", "平静", "史诗", "孤独", "浪漫", "忧郁", "宁静", "激动", "悲伤",
               "温馨", "warm", "tense", "calm", "epic", "romantic", "melancholy", "peaceful"],
    "action": ["转头", "跑步", "风吹", "微笑", "走动", "回眸", "舞", "跳跃",
               "turn", "run", "wind", "smile", "walk", "dance", "jump"],
    "audio":  ["安静", "城市喧嚣", "海浪", "雨声", "风声",
               "quiet", "city noise", "ocean", "rain", "wind sound"],
}

def _extract_common(report: dict) -> dict:
    """从 image-report 集中提取所有 builder 共享的字段。返回 dict,字段名为短键。"""
    sub, scene, cine, aes, dyn = (report[k] for k in REQUIRED_TOP)
    cons = report.get("constraints", {}) or {}
    _normalize_motion(report, dyn)
    dyn = report["dynamic"]
    motion = dyn.get("recommended_camera_motion", {}) or {}
    duration_raw = dyn.get("recommended_duration", 5)
    try:
        duration = float(duration_raw)
    except (TypeError, ValueError):
        duration = 5.0
    return {"subj_name": _non_unknown(sub.get("name")) or "subject", "subj_count": sub.get("count", 1), "identity": _non_unknown(sub.get("pose")) or _non_unknown(sub.get("expression")), "pose": _non_unknown(sub.get("pose")) or "", "expr": _non_unknown(sub.get("expression")) or "", "cues": sub.get("identity_cues", []) or [], "secondary": sub.get("secondary_subjects", []) or [], "position": _non_unknown(sub.get("position")) or "center-frame", "scene_type": _non_unknown(scene.get("type")) or "scene", "scene_sub": _non_unknown(scene.get("subtype")) or _non_unknown(scene.get("type")) or "scene", "elems": scene.get("key_elements", []) or [], "weather": _non_unknown(scene.get("weather")), "tod": _non_unknown(scene.get("time_of_day")), "framing": _non_unknown(cine.get("framing")) or "medium shot", "angle": _non_unknown(cine.get("angle")) or "eye level", "style": _str_field(aes.get("style")) or "cinematic", "art": _non_unknown(aes.get("art_style")) or "", "grade": _non_unknown(aes.get("color_grade")) or "", "lighting": _non_unknown(aes.get("lighting")) or "", "texture": _non_unknown(aes.get("texture")) or "", "mood": _str_field(aes.get("mood")) or "neutral", "motion": motion, "m_type": _non_unknown(motion.get("type")) or "static", "amp": _non_unknown(motion.get("amplitude")) or "", "spd": _non_unknown(motion.get("speed")) or "", "movable": dyn.get("movable_subjects", []) or [], "rhythm": _non_unknown(dyn.get("recommended_rhythm")) or "normal", "duration": duration, "must_not": cons.get("must_not_change", []) or cons.get("must_keep", []) or [], "high_risk": cons.get("high_risk_motion", []) or []}

def _safe_str(v: Any) -> str:
    """vision 输出 mood/style 可能是 list/tuple/None — 统一为字符串,避免 AttributeError。"""
    if isinstance(v, (list, tuple)):
        return ", ".join(str(x) for x in v)
    return str(v) if v else ""

def _apply_keywords(report: dict, kws: list[str]) -> dict:
    """关键词合并: 优先级高于 vision 默认 (analyzer §3)。"""
    out = copy.deepcopy(report)
    if not kws:
        return out
    cls = {k: [] for k in _KW_LEX}
    for kw in kws:
        s = kw.strip()
        if not s:
            continue
        sl = s.lower()
        hit = next((c for c, ws in _KW_LEX.items() if any(w.lower() in sl for w in ws)), None)
        cls[hit or "mood"].append(s)
    if cls["camera"]:
        cam = _get(out, "dynamic", "recommended_camera_motion", default={}) or {}
        cam["type"] = _join(cls["camera"])
        cam["user_keyword"] = True
        out.setdefault("dynamic", {})["recommended_camera_motion"] = cam
    if cls["style"]:
        cur_s = _safe_str(out.setdefault("aesthetic", {}).get("style", "")).lower()
        out["aesthetic"]["style"] = (_join(cls["style"]) if cur_s == UNKNOWN
                                     else f"{_join(cls['style'])}, {cur_s} (用户强化)")
    if cls["mood"]:
        cur_str = _safe_str(out.setdefault("aesthetic", {}).get("mood", ""))
        if cur_str.lower() == UNKNOWN or not cur_str:
            out["aesthetic"]["mood"] = _join(cls["mood"])
        else:
            ex = [m for m in cur_str.split(",") if m.strip()]
            out["aesthetic"]["mood"] = _join(cls["mood"] + [m for m in ex if m not in cls["mood"]])
    if cls["action"]:
        d = out.setdefault("dynamic", {})
        m = d.get("movable_subjects", []) or []
        m.extend(f"user action: {a}" for a in cls["action"])
        d["movable_subjects"] = m
    ov = out.setdefault("user_overrides", {})
    ov["raw_keywords"] = kws
    ov["classified"] = cls
    return out

_CAM_TYPE_EN: dict[str, str] = {
    "推近": "pushes in", "推": "pushes in", "拉远": "pulls out", "拉": "pulls out",
    "摇": "pans", "移": "tracks", "环绕": "arcs around", "固定": "holds a static shot",
    "跟拍": "tracks",
    "push in": "pushes in", "push": "pushes in",
    "pull out": "pulls out", "pull": "pulls out",
    "pan": "pans", "tilt": "tilts", "orbit": "arcs around",
    "arc-orbit": "arcs around", "arc orbit": "arcs around", "arc": "arcs around",
    "spiral": "arcs around", "twirl": "arcs around",
    "static": "holds a static shot", "tracking": "tracks",
}

_CAM_TYPE_ZH: dict[str, str] = {
    "推近": "向前推近", "推": "向前推近", "拉远": "向后拉远", "拉": "向后拉远",
    "摇": "横向摇移", "移": "横向移动", "环绕": "环绕主体", "固定": "保持固定机位",
    "跟拍": "跟随主体移动",
    "push in": "向前推近", "push": "向前推近",
    "pull out": "向后拉远", "pull": "向后拉远",
    "pan": "横向摇移", "tilt": "竖向摇移", "orbit": "环绕主体",
    "arc-orbit": "环绕主体", "arc orbit": "环绕主体", "arc": "环绕主体",
    "spiral": "螺旋环绕", "twirl": "环绕旋转",
    "static": "保持固定机位", "tracking": "跟随主体移动",
}

_ZH_FIELD_MAP: dict[str, str] = {
    "integrated_multimodal_description": "综合多模态描述",
    "overall_soundscape": "整体声音景观",
    "non_diegetic_music": "非剧情音乐",
    "shot": "镜头",
    "shot_at": "镜头切点",
    "overall_requirement": "整体要求",
}
_ZH_KW_MAP: dict[str, str] = {
    "joyful": "俏皮", "warm": "温暖", "romantic": "浪漫",
    "bright": "明亮", "soft": "柔和", "tense": "紧张",
    "calm": "平静", "epic": "史诗", "melancholy": "忧郁",
    "peaceful": "宁静", "neutral": "中性",
}
_ZH_MUSIC_MAP: dict[str, str] = {
    "warm": "温暖的原声吉他旋律,慢速节奏",
    "tense": "低沉持续的低音,营造紧张氛围",
    "calm": "极简环境音,点缀稀疏的钢琴",
    "epic": "完整管弦乐渐强,加入打击乐",
    "romantic": "柔和的钢琴主旋律,辅以轻柔弦乐",
    "melancholy": "缓慢的钢琴动机,暗含大提琴低吟",
    "peaceful": "轻柔环境音垫底,远处有风铃",
}
_MUSIC_EN_MAP: dict[str, str] = {
    "warm": "a warm soft acoustic guitar motif at a slow tempo",
    "tense": "a low sustained drone building tension",
    "calm": "minimal ambient pad with sparse piano notes",
    "epic": "a full orchestral swell with percussion",
    "romantic": "a gentle piano melody with soft strings",
    "melancholy": "a slow piano motif with subtle cello undertone",
    "peaceful": "soft ambient pad and distant wind chimes",
}

def _normalize_motion(report: dict, dyn: dict) -> None:
    """原地归一化 report 顶层平铺字段 → report.dynamic(兼容 image-schema/vision_call/平铺 3 种变体)。"""
    for k in ("recommended_camera_motion", "recommended_duration", "recommended_rhythm"):
        if k in report and k not in dyn:
            dyn[k] = report[k]
    if "recommended_camera_motion" not in dyn and "type" in dyn and "amplitude" in dyn:
        dyn["recommended_camera_motion"] = {
            kk: dyn[kk] for kk in ("type", "amplitude", "speed") if kk in dyn
        }

def _cam_clause_h3(motion: dict, lang: str = "en") -> str:
    """H3 镜头从句: 'The camera <type> [with <amp> amplitude] [at <spd> speed]'。"""
    if not isinstance(motion, dict):
        return "The camera holds a static shot" if lang == "en" else "镜头保持固定机位"
    t = _non_unknown(motion.get("type")) or "static shot"
    mapping = _CAM_TYPE_ZH if lang == "zh" else _CAM_TYPE_EN
    en = mapping.get(t.lower(), t)
    dyn = motion.get("_dyn_flat", {}) if "_dyn_flat" in motion else {}
    amp = _non_unknown(motion.get("amplitude")) or _non_unknown(dyn.get("amplitude"))
    spd = _non_unknown(motion.get("speed")) or _non_unknown(dyn.get("speed"))
    amp_c = _compact(amp)
    spd_c = _compact(spd)
    if lang == "zh":
        amp_map = {"small": "小幅", "medium": "中等", "large": "大幅"}
        spd_map = {"slow": "慢速", "slow-to-medium": "慢到中速", "medium": "中速", "fast": "快速"}
        amp_p = f",{amp_map.get(amp_c.lower(), amp_c + '幅度')}" if amp_c else ""
        spd_p = f",{spd_map.get(spd_c.lower(), spd_c + '速度')}" if spd_c else ""
        return f"镜头{en}{amp_p}{spd_p}"
    amp_map = {"small": " with small amplitude", "large": " with large amplitude"}
    amp_p = amp_map.get(amp_c.lower(), f" with {amp_c} amplitude" if amp_c else "")
    spd_p = {"slow": " at slow speed", "fast": " at fast speed"}.get(
        spd_c.lower(), f" at {spd_c} speed" if spd_c else "")
    return f"The camera {en}{amp_p}{spd_p}"

def build_h3_prompt(report: dict, lang: str = "en", time_segments: int = 3) -> str:
    """H3 三段式 builder。lang='en' 英文 H3 / 'zh' 中文笔记法(主角锁定+时段切片+整体要求)。"""
    if lang == "zh":
        return _build_h3_zh(report, time_segments)
    c = _extract_common(report)
    subj_name, subj_count, identity, cues = c["subj_name"], c["subj_count"], c["identity"], c["cues"]
    framing, angle, style, mood = c["framing"], c["angle"], c["style"], c["mood"]
    grade = _join([c["grade"], c["texture"], c["lighting"]])
    motion, duration, movable, must_not = c["motion"], c["duration"], c["movable"], c["must_not"]
    env = _join([c["scene_sub"], "with " + _join(c["elems"][:3]) if c["elems"] else ""])
    main = f"{subj_count} {subj_name}{'' if subj_count == 1 else 's'}"
    if identity:
        main += f" ({identity})"
    elif cues:
        main += f" (with {_join(cues[:3])})"
    actions = _join(movable[:3], "; ")
    cam = _cam_clause_h3(motion)
    grade_p = f", in {grade}" if grade else ""
    shot1 = (f"[Shot 1] {style.capitalize()}, {framing}, {angle}, {main}"
             + (f" in a {env}" if env else "") + f"{grade_p}. {cam}"
             + (f" as {actions}" if actions else "") + f". Mood: {mood}.")
    multi = _non_unknown(report["dynamic"].get("multi_shot_potential"))
    if multi and multi.lower().startswith("high"):
        shot2 = (f"[Shot 2] At 00:05.000, the camera cuts to a close-up of "
                 f"{subj_name}'s face, the {mood.split(',')[0].strip()} expression "
                 f"held for the remainder of the {duration}s.")
        desc = shot1 + "\n" + shot2
    else:
        desc = shot1
    sfx = []
    if c["weather"] and c["weather"] != "clear":
        sfx.append(f"ambient {c['weather']} atmosphere")
    if c["tod"]:
        sfx.append(f"{c['tod']} ambient tone")
    sfx.extend(f"subtle sound of {_compact(m)}" for m in movable[:2])
    if not sfx:
        sfx.append(f"ambient room tone matching the {mood} mood")
    soundscape = _join(sfx, ". ").capitalize() + "."
    music = (_MUSIC_EN_MAP.get(mood.split(",")[0].strip().lower(),
             f"a subtle musical underscore matching the {mood} mood") + ", fading gently at the end.")
    cons_part = ("\n\n# constraints (must_not_change)\n"
                 f"Preserve exactly: {'; '.join(must_not)}." if must_not else "")
    return (f"# integrated_multimodal_description\n{desc}\n\n"
            f"# overall_soundscape\n{soundscape}\n\n"
            f"# non_diegetic_music\n{music}{cons_part}").strip() + "\n"

def _build_h3_zh(report: dict, time_segments: int) -> str:
    """中文笔记法 — 时间段切片 + 主角锁定 + 整体要求。"""
    c = _extract_common(report)
    subj_name, cues, secondary = c["subj_name"], c["cues"], c["secondary"]
    framing, angle, style = c["framing"], c["angle"], c["style"] or "电影感"
    motion, movable, mood = c["motion"], c["movable"], c["mood"]
    duration, position = c["duration"], c["position"]
    must_not, high_risk = c["must_not"], c["high_risk"]
    segs = _seg_split(duration, time_segments)
    n = len(segs)
    mood_first = mood.split(",")[0].strip()
    mood_zh = _ZH_KW_MAP.get(mood_first.lower(), mood_first)
    cues_s = _join(cues[:3]) if cues else (c["identity"] or "")
    main_zh = f"{subj_name}({cues_s})" if cues_s else subj_name
    movs = movable or ["主体保持姿态"]
    per_seg = max(1, len(movs) // n) if n else 1
    s0 = secondary[0] if secondary else None
    sn = s0.get("name", "") if isinstance(s0, dict) else (str(s0) if s0 else "")
    sec_snip = f"背景配角色:{sn}作为背景元素,简短出现。" if sn else ""
    cam = _cam_clause_h3(motion, "zh")
    shot_lines = []
    for i, (t0, t1) in enumerate(segs):
        chunk = movs[i * per_seg:(i + 1) * per_seg]
        action = _join(chunk, "、")
        pos_p = position if i == 0 else "主体位置不变"
        line = (f"[{_ZH_FIELD_MAP['shot']} {i+1}] {t0}-{t1},{framing},{angle},{style},"
                f"{main_zh},{pos_p},{action}。{cam}。整体氛围:{mood_zh}。")
        if i == 0 and sec_snip:
            line += " " + sec_snip
        shot_lines.append(line)
    desc = "\n".join(shot_lines)
    must_str = f",{_join(must_not, ',')}" if must_not else ""
    desc += (f"\n整体要求:全程面部清晰可见{must_str}必须保持不变;动作连贯自然不突兀。"
             + (f"\n高风险动作(需避免):{_join(high_risk, '; ')}。" if high_risk else ""))
    sfx_parts = []
    if c["weather"] and c["weather"] != "clear":
        sfx_parts.append(f"{c['weather']}的环境氛围音")
    if c["tod"]:
        sfx_parts.append(f"{c['tod']}时段的环境底噪")
    if movable:
        sfx_parts.extend(f"细微的{_compact(m)}声" for m in movable[:2])
    if not sfx_parts:
        sfx_parts.append(f"与{mood_zh}情绪匹配的空间底噪")
    soundscape = _join(sfx_parts, "、") + "。"
    music = (_ZH_MUSIC_MAP.get(mood_first.lower(),
             f"细小的音乐垫底,匹配{mood_zh}情绪") + ",在结尾处轻柔淡出。")
    return (f"# {_ZH_FIELD_MAP['integrated_multimodal_description']}\n{desc}\n\n"
            f"# {_ZH_FIELD_MAP['overall_soundscape']}\n{soundscape}\n\n"
            f"# {_ZH_FIELD_MAP['non_diegetic_music']}\n{music}").strip() + "\n"

_CAM_SEEDANCE = {
    "push in": "slow dolly in", "push": "slow dolly in",
    "pull out": "pull back", "pan": "handheld pan",
    "static": "locked-off", "orbit": "slow arc",
    "tracking": "low tracking shot",
}

def _build_seedance_zh(duration, subj_name, cues, scene_type, elems, style,
                         mood, rhythm, movable, must_not, time_segments) -> str:
    """Seedance 中文笔记法 — 时段切分 + 主角锁定 + 整体要求(紧凑实现)。"""
    segs = _seg_split(duration, time_segments)
    movs = movable or ["主体保持姿态"]
    per_seg = max(1, len(movs) // len(segs)) if segs else 1
    mood_zh = _ZH_KW_MAP.get(mood.split(",")[0].strip().lower(), mood.split(",")[0].strip())
    cues_s = _join(cues[:3]) if cues else ""
    ident_zh = f"{subj_name}({cues_s})" if cues_s else subj_name
    labels = ["开场", "推进", "转折", "收尾"]
    lines_zh = [f"overall: 一段{duration:.0f}秒的{mood_zh}叙事弧 — {ident_zh} 在 {scene_type}({_join(elems[:2])}),{style}", ""]
    for i, (t0, t1) in enumerate(segs):
        chunk = movs[i * per_seg:(i + 1) * per_seg] if segs else movs[:1]
        action = _join(chunk, "、")
        label = labels[i] if i < len(labels) else f"段{i+1}"
        lines_zh.append(f"{label}({t0}-{t1}):")
        lines_zh.append(f"  主体:{ident_zh};动作:{action}。")
        lines_zh.append("")
    lines_zh.append("references: @Image1 主体身份 / @Image2 场景+色调"
                    + (f" / @Image3 服装细节({_join(cues[:2])})" if cues else ""))
    must_not_str = f",{_join(must_not, ',')}" if must_not else ""
    lines_zh += ["", "audio: BGM 每拍垫底;SFX 由主体动作触发。",
                 f"整体要求:全程面部清晰可见{must_not_str}必须保持不变,动作连贯自然不突兀。"]
    return "\n".join(lines_zh).strip() + "\n"

def build_seedance_prompt(report: dict, lang: str = "en", time_segments: int = 4) -> str:
    """Seedance 四拍 builder(opening/progression/turn/resolution)。lang='zh' 中文笔记法切 4 段。"""
    c = _extract_common(report)
    if lang == "zh":
        return _build_seedance_zh(c["duration"], c["subj_name"], c["cues"], c["scene_type"],
                                   c["elems"], c["style"], c["mood"], c["rhythm"], c["movable"],
                                   c["must_not"], time_segments)
    subj_name, cues, scene_type, elems = c["subj_name"], c["cues"], c["scene_type"], c["elems"]
    framing, angle, style, mood = c["framing"], c["angle"], c["style"], c["mood"]
    grade, lighting = c["grade"], c["lighting"]
    m_type, rhythm, movable = c["m_type"], c["rhythm"], c["movable"]
    duration, must_not = c["duration"], c["must_not"]
    cam = _CAM_SEEDANCE.get(m_type.lower(), m_type).capitalize()
    ident = _join(cues[:3]) if cues else subj_name
    env = _join([scene_type, _join(elems[:3])])
    style_str = _join([style, grade, lighting])
    mood_s = mood.split(",")[0].strip()
    overall = f"a {duration}-second {mood_s} narrative arc — {subj_name} ({ident}) in {env}, {style_str}"
    opening = (f"  Establish the space and the {subj_name}. {framing}, {angle}. "
               f"The first 6 seconds settle into {mood_s} mood. {cam}.")
    if movable:
        progression = (f"  The {subj_name} begins to act. Movement reference: "
                       f"{_join(movable[:3], '; ')}. Pace lifts from {rhythm} rhythm. "
                       f"Hold the same camera language.")
    else:
        progression = f"  The scene develops at a {rhythm} rhythm. Hold the same camera language."
    turn = (f"  A shift occurs — the {grade or 'grade'} warms (or cools), the {mood_s} "
            f"mood turns, and the camera reveals something new about the {subj_name}.")
    resolution = (f"  Land on a wide or locked-off frame. Hold the final two seconds "
                  f"to let the {mood_s} breathe. The {subj_name} resolves in place.")
    refs = ["  @Image1  ← 主体身份锁定 (subject identity lock)", "  @Image2  ← 场景 / 色调 (scene + grade)"]
    if cues:
        refs.append(f"  @Image3  ← 道具 / 服装细节 (cues: {_join(cues[:2])})")
    out = [f"overall: {overall}", "", "opening (0s to 6s):", opening, "",
           "progression (6s to 16s):", progression, "", "turn (16s to 24s):", turn, "",
           "resolution (24s to 30s):", resolution, "", "references:", *refs, "",
           "audio: BGM underscores each beat; SFX triggered by subject motion."]
    if must_not:
        out += ["", f"constraints: do not change — {'; '.join(must_not)}."]
    return "\n".join(out).strip() + "\n"

_CAM_KLING = {
    "push in": "camera slowly pushes in", "push": "camera slowly pushes in",
    "pull out": "camera pulls back", "pan": "camera pans", "tilt": "camera tilts",
    "orbit": "camera arcs around the subject",
    "static": "camera stays locked off",
    "tracking": "camera tracks the subject",
}

def build_kling_prompt(report: dict, lang: str = "en", time_segments: int = 3) -> str:
    """Kling 3.0 三段式 builder。lang='zh' 中文版 + 时段切片(简化为 constraints 一段)。"""
    c = _extract_common(report)
    subj_name, cues = c["subj_name"], c["cues"]
    pose, expr = c["pose"], c["expr"]
    scene_sub, elems = c["scene_sub"], c["elems"]
    framing, angle, style, mood = c["framing"], c["angle"], c["style"], c["mood"]
    art, grade, lighting, texture = c["art"], c["grade"], c["lighting"], c["texture"]
    m_type, amp, spd, movable = c["m_type"], c["amp"], c["spd"], c["movable"]
    duration, must_not, high_risk = c["duration"], c["must_not"], c["high_risk"]
    cam = _CAM_KLING.get(m_type.lower(), f"camera moves {m_type}")
    if amp: cam += f" with {_compact(amp)} amplitude"
    if spd: cam += f" at {_compact(spd)} speed"
    visual = _join([style, art, grade, lighting, texture])
    env = _join([scene_sub, _join(elems[:3])])
    L = ("zh" if lang == "zh" else "en")
    cue_sep, action_label = (("(", ")") if L == "zh" else (" with ", ""))
    subj_phrase = subj_name + (f"{cue_sep[0]}{_join(cues[:3] if L=='en' else cues[:3])}{cue_sep[1]}" if cues else "")
    if pose: subj_phrase += ("," if L == "zh" else ", ") + pose
    if expr: subj_phrase += ("," if L == "zh" else ", ") + expr
    action_phrase = (f"主体动作:{_join(movable[:3], '; ')}。" if L == "zh"
                     else f"Main motion: {_join(movable[:3], '; ')}.") if movable else ""
    section1 = (f"[1] 主体:{subj_phrase}。{action_phrase}" if L == "zh"
                else f"[1] Subject: {subj_phrase}. {action_phrase}").strip()
    if L == "zh":
        s2 = [f"景别:{framing},{angle}。", f"环境:{env}。" if env else "", f"视觉风格:{visual}。" if visual else "", f"运镜:{cam}。", f"情绪:{mood}。"]
    else:
        s2 = [f"Framing: {framing}, {angle}.", f"Environment: {env}." if env else "", f"Visual style: {visual}." if visual else "", f"Motion: {cam}.", f"Mood: {mood}."]
    section2 = "[2] " + " ".join(p for p in s2 if p)
    if L == "zh":
        cons_lines = [f"必须保持:{', '.join(must_not)}。" if must_not else "", f"避免:{', '.join(high_risk)}。" if high_risk else "", "保持场景与原图稳定一致。" if not (must_not or high_risk) else ""]
        segs = _seg_split(duration, time_segments)
        seg_line = "/".join(f"{t0}-{t1}" for t0, t1 in segs)
        section3 = (f"[3] 约束:" + " ".join(p for p in cons_lines if p)
                    + f" 整段时长:{duration:.0f}s,切为{len(segs)}段(时间段:{seg_line});"
                    + "全程面部清晰可见,动作连贯自然不突兀。")
    else:
        constraints = ["Preserve exactly: " + ", ".join(must_not) + "." if must_not else "", "Avoid: " + ", ".join(high_risk) + "." if high_risk else "", "Keep the scene stable and consistent with the source image." if not (must_not or high_risk) else ""]
        section3 = "[3] Constraints: " + " ".join(p for p in constraints if p)
    return "\n".join([section1, section2, section3]).strip() + "\n"

BUILDERS = {"h3": build_h3_prompt, "seedance": build_seedance_prompt, "kling": build_kling_prompt}

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="i2v_prompt_build",
        description="i2v-prompt 跨平台构造器 — 读取 image-report.json (image-schema v1.0) + 可选关键词,输出三平台影视级 prompt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=("示例:\n"
                "  python scripts/i2v_prompt_build.py --report out/image-report.json --platform h3 "
                "--duration 5 --keywords \"温暖 电影感 推近\" --out out/prompt.txt\n"
                "  python scripts/i2v_prompt_build.py --report out/image-report.json --platform h3 "
                "--language zh --time-segments 3 --duration 8 --keywords \"元气满满 转圈\"\n"),
    )
    p.add_argument("--report", required=True, help="image-report.json 路径 (image-schema v1.0)")
    p.add_argument("--platform", required=True, choices=sorted(BUILDERS), help="目标平台: h3 / seedance / kling")
    p.add_argument("--duration", type=int, default=None, help="视频时长(秒); 默认取 report.dynamic.recommended_duration")
    p.add_argument("--keywords", default="", help="用户关键词,空格分隔; 走 i2v-image-analyzer §3 合并协议")
    p.add_argument("--language", choices=["en", "zh"], default="en",
                   help="输出语言: en (默认,英文 H3 三段式) / zh (中文笔记法 — 时间段切片 + 主角锁定 + 整体要求)")
    p.add_argument("--time-segments", type=int, default=None,
                   help="时间段切片数(默认 h3=3 / seedance=4 / kling=3,中文模式生效,等分 25%/50%/25% 或均分)")
    p.add_argument("--out", default=None, help="输出文件路径; 默认 stdout")
    return p

def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    rp = Path(args.report)
    if not rp.is_file():
        print(f"[ERROR] report 文件不存在: {rp}", file=sys.stderr)
        return 2
    try:
        report = json.loads(rp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"[ERROR] 解析/读取失败: {e}", file=sys.stderr)
        return 2
    if not isinstance(report, dict):
        print("[ERROR] image-report.json 顶层必须是 object", file=sys.stderr)
        return 2
    try:
        _validate(report)
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2

    kws = [k for k in args.keywords.split(" ") if k.strip()]
    if kws:
        report = _apply_keywords(report, kws)
    if args.duration is not None:
        report.setdefault("dynamic", {})["recommended_duration"] = args.duration

    ts = args.time_segments if args.time_segments is not None else DEFAULT_SEGMENTS[args.platform]
    try:
        prompt = BUILDERS[args.platform](report, args.language, ts)
    except Exception as e:
        print(f"[ERROR] prompt 构造失败 ({args.platform}): {e}", file=sys.stderr)
        return 3

    if args.out:
        op = Path(args.out)
        op.parent.mkdir(parents=True, exist_ok=True)
        op.write_text(prompt, encoding="utf-8")
        print(f"[OK] prompt 已写入: {op}", file=sys.stderr)
    else:
        sys.stdout.write(prompt)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())