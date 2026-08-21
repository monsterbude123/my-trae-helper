"""i2v-image-analyzer / video-input-analyzer — vision 调用实现层。

支持 5 种 input_mode 的多模态版本:
  - i2v: 单图 + 文本(向后兼容,v1.0 schema)
  - t2v: 纯文本(v2.0 schema)
  - v2v: 视频 + 文本(v2.0 schema)
  - ref2v: 多模态 + 文本(v2.0 schema)
  - mm2v: 输入不明确,询问用户(v2.0 schema)

升级自 v1.0(2026-08-19)→ v2.0(2026-08-20):
  - 默认行为保持兼容(单图 → v1.0 schema)
  - 新参数触发 v2.0 schema(input_mode / input_inventory / reference_assignments / video_metadata)
  - 新增 --input-mode / --video / --frame-time / --reference-images / --audio / --text 参数

复用 minimax-multimodal/scripts/_client.py 的共享 HTTP 客户端(同仓已存在):
  - 双区域 + 指数退避 + Key 脱敏
  - .env 自动加载:cwd/.env / 祖先链 / skill 内 .env,先匹配先加载

用法(v1.0 向后兼容):
  python scripts/i2v_vision_call.py --image photo.jpg --keywords "电影感 温暖" --out report.json

用法(v2.0 多模态):
  python scripts/i2v_vision_call.py --image photo.jpg --input-mode i2v --out report.json
  python scripts/i2v_vision_call.py --video prev.mp4 --frame-time 2.0 --out v2v-report.json
  python scripts/i2v_vision_call.py --reference-images "r1.jpg" "r2.jpg" --out ref-report.json
  python scripts/i2v_vision_call.py --text "20 岁少女在走廊转圈" --out t2v-report.json

依赖: requests(项目侧统一依赖,随 minimax-multimodal 引入)。
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 复用 minimax-multimodal 的共享 HTTP 客户端(.env 加载 / Key 管理 / 指数退避)
_AIGC_ROOT = Path(__file__).resolve().parent.parent.parent
_MM_SCRIPTS = _AIGC_ROOT / "minimax-multimodal" / "scripts"
if str(_MM_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_MM_SCRIPTS))

import requests  # noqa: E402

try:
    import _client as mm_client  # type: ignore
except ImportError:  # pragma: no cover
    mm_client = None

LOG = logging.getLogger("i2v_vision")

VISION_MODEL_DEFAULT = "MiniMax-M3"
SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
SUPPORTED_VIDEO_EXTS = {".mp4", ".mov", ".avi", ".webm", ".mkv"}
SUPPORTED_AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
SUPPORTED_INPUT_MODES = ("auto", "i2v", "t2v", "v2v", "ref2v", "mm2v")


def _utcnow_iso() -> str:
    """UTC ISO 8601 — 替代 deprecated datetime.utcnow()。"""
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# -----------------------------------------------------------------------------
# Schema 版本检测
# -----------------------------------------------------------------------------

def _is_v2_request(args: argparse.Namespace) -> bool:
    """检测是否使用 v2.0 多模态请求。

    v2.0 触发条件(任一):
      - --input-mode 显式给出(非 auto)
      - --video 给出
      - --reference-images 给出
      - --audio 给出
      - --text 给出(纯文本 t2v)
    """
    if args.input_mode and args.input_mode != "auto":
        return True
    if args.video:
        return True
    if args.reference_images:
        return True
    if args.audio:
        return True
    if args.text:
        return True
    return False


def _detect_input_mode(
    images: List[str],
    videos: List[str],
    audios: List[str],
    text: str,
    keywords: List[str],
    explicit_mode: str,
) -> str:
    """根据输入组合判定 input_mode。

    优先级:
      1. 显式 --input-mode 优先(若非 auto)
      2. 有视频 → v2v
      3. 多模态(>=2 类)→ ref2v
      4. 单图 → i2v
      5. 纯文本 → t2v
      6. 完全无输入 → mm2v

    详见 skills/video-input-analyzer/references/input-mode-detection.md
    """
    if explicit_mode and explicit_mode != "auto":
        return explicit_mode

    has_img = bool(images)
    has_vid = bool(videos)
    has_aud = bool(audios)
    has_text = bool(text or keywords)

    if has_vid and not has_img:
        return "v2v"
    if has_img and has_vid:
        return "ref2v"
    if has_img and has_aud:
        return "ref2v"
    if has_vid and has_aud:
        return "ref2v"
    if len(images) >= 2:
        return "ref2v"
    if has_img:
        return "i2v"
    if has_text:
        return "t2v"
    return "mm2v"


# -----------------------------------------------------------------------------
# System prompt:内置 schema 字段 + scene-vocabulary 标准词
# -----------------------------------------------------------------------------

SYSTEM_PROMPT_V1 = """你是专业的影视画面分析师。请观察用户提供的图像,按 JSON schema v1.0 输出结构化分析。

## 输出要求(MUST)
1. **仅输出 JSON**,不要包裹 markdown 代码块、不要前缀解释、不要后缀补充。
2. 字段顺序与下面 schema 一致;缺失字段 → 填 "unknown" 或空数组,不省略。
3. 词汇**严格使用** scene-vocabulary.md 标准词表(见附录)。不要自造形容词。
4. recommended_camera_motion 必填 type + amplitude + speed + rationale 四件套。
5. constraints.text_in_image 必填(可空数组)— 列出图中所有可见文字 + 位置。
6. 如果无法识别主体/场景 → 必填字段填 "unknown",并把 analyzer_status 设为 "partial: <原因>"。

## JSON Schema(顶层字段顺序)
```
{
  "version": "1.0",                     // 锁 1.0
  "image_id": "<hash 或 URL>",
  "analyzed_at": "<ISO 8601>",
  "subject": { ... },                   // §1
  "scene": { ... },                     // §2
  "cinematography": { ... },            // §3
  "aesthetic": { ... },                 // §4
  "dynamic": { ... },                   // §5
  "constraints": { ... },               // §6
  "user_overrides": { ... },            // §7
  "analyzer_status": "ok" | "partial: <原因>"
}
```

## scene-vocabulary 标准词(候选值,严格从这里选)
- scene.type: indoor / outdoor / studio / abstract
- cinematography.framing: extreme-wide / wide / medium-wide / medium / medium-close / close-up / extreme-close-up
- cinematography.angle: eye-level / low-angle / high-angle / bird's-eye / dutch-angle / over-the-shoulder
- cinematography.composition: rule-of-thirds / centered / symmetric / diagonal / minimal / frame-within-frame / leading-lines
- aesthetic.lighting: natural-light / golden-hour / blue-hour / studio-light / hard-light / soft-light / volumetric / neon / candlelight / backlight / rim-light
- aesthetic.color_grade: warm / cool / teal-and-orange / high-contrast / low-contrast / desaturated / vintage / modern / monochrome / pastel
- aesthetic.style: cinematic / photographic / illustration / anime / 3D-render / oil-painting / watercolor / minimal / surreal
- aesthetic.mood: 从 calm/warm/tense/joyful/melancholic/epic/mysterious/romantic 八族中选 2-3 个词
- dynamic.movable_subjects: 人(hair/expression/clothing-flap)/ 自然(leaves/clouds/water-flow)/ 物体(fabric-flow/shadow)

## 必填字段 quick check
- subject.name / count / position / pose
- scene.type / key_elements(3-5 个)
- cinematography.framing / angle / composition
- aesthetic.style / lighting / mood
- dynamic.movable_subjects / recommended_camera_motion(type+amplitude+speed+rationale) / recommended_duration / recommended_rhythm

下游 i2v-h3-prompt / i2v-seedance-prompt 会读取这些字段包装 prompt。"unknown" 字段不会被写入 prompt,留 vision 不确定的留白。
"""


SYSTEM_PROMPT_V2 = """你是专业的多模态影视画面分析师。请观察用户提供的输入(图 / 视频 / 音频 / 文本),按 JSON schema v2.0 输出结构化分析。

## 输出要求(MUST)
1. **仅输出 JSON**,不要包裹 markdown 代码块、不要前缀解释、不要后缀补充。
2. 字段顺序与下面 schema 一致;缺失字段 → 填 "unknown" 或空数组,不省略。
3. 词汇**严格使用** multi-modal-vocabulary.md 标准词表(见附录)。不要自造形容词。
4. recommended_camera_motion 必填 type + amplitude + speed + rationale 四件套。
5. constraints.text_in_image 必填(可空数组)— 列出图中所有可见文字 + 位置。
6. 如果无法识别主体/场景 → 必填字段填 "unknown",并把 analyzer_status 设为 "partial: <原因>"。
7. input_mode 必填,且 MUST 是下列之一: i2v / t2v / v2v / ref2v / mm2v
8. input_inventory 必填,列出所有视觉输入(image / video / audio)
9. ref2v 模式时:reference_assignments 必填,每个素材分配唯一角色(见 §3 角色词表)
10. v2v 模式时:video_metadata.key_frames 必填,至少 3 帧(首 / 中 / 末)

## JSON Schema v2.0(顶层字段顺序)
```
{
  "version": "2.0",                              // 锁 2.0
  "input_mode": "i2v|t2v|v2v|ref2v|mm2v",
  "analyzed_at": "<ISO 8601>",
  "input_inventory": {
    "images": [ { "id", "source", "sha1", "size_bytes", "width", "height" } ],
    "videos": [ { "id", "source", "sha1", "duration_s", "fps", "width", "height", "key_frames" } ],
    "audios": [ { "id", "source", "sha1", "duration_s", "transcript" } ],
    "user_text": "<原始文本>"
  },
  "subject": { ... },                            // 同 v1.0
  "scene": { ... },                              // 同 v1.0
  "cinematography": { ... },                     // 同 v1.0
  "aesthetic": { ... },                          // 同 v1.0
  "dynamic": { ... },                            // 同 v1.0
  "constraints": { ... },                        // 同 v1.0
  "reference_assignments": [                     // ref2v 必填
    { "media_id", "role", "rationale" }
  ],
  "video_metadata": {                            // v2v 必填
    "source_video", "duration_s", "fps", "resolution",
    "key_frames": [ { "time_s", "description" } ],
    "last_frame_description", "continuation_intent", "style_anchor"
  },
  "user_overrides": { ... },                     // 同 v1.0
  "analyzer_status": "ok" | "partial: <原因>"
}
```

## 角色词表(reference_assignments.role)
- character_identity: 主体身份(脸部特写 / 产品)
- scene_aesthetic: 场景色调 / 美学
- motion_reference: 镜头运动参考
- rhythm_ambient: 节奏 / 氛围参考
- first_last_frame: 首尾帧补帧(i2v 模式)
- style_transfer: 风格化参考(v2v 风格化)
- extension_prior: 续写前序(v2v 续写)

## multi-modal-vocabulary 标准词(同 v1.0 + 视频 / 音频扩展)
- scene.type / cinematography.* / aesthetic.* :同 v1.0 词表
- 视频关键帧状态:static / pan-left/right / tilt-up/down / zoom-in/out / push-in/pull-out / tracking / handheld / orbit
- 音频节奏:steady-rhythm / syncopated / accelerating / decelerating / silence / ambient-only

下游各 video prompt skill 会按 input_mode 路由读取字段包装 prompt。"unknown" 字段不会被写入 prompt。
"""


# -----------------------------------------------------------------------------
# 媒体预处理:本地 / URL / base64
# -----------------------------------------------------------------------------

def _image_to_data_uri(image: str) -> str:
    """统一转 data URI(本地文件)/ 透传 URL。"""
    if image.startswith(("http://", "https://")):
        return image
    p = Path(image).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"图片文件不存在:{p}")
    ext = p.suffix.lower().lstrip(".")
    mime = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "gif": "image/gif",
    }.get(ext, "application/octet-stream")
    if ext not in SUPPORTED_IMAGE_EXTS:
        LOG.warning("非标准图片格式:%s(支持 jpg/png/webp/gif)", ext)
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _image_id(image: str) -> str:
    """算 image_id:URL 直接用,本地文件 sha1(前 16 位)。"""
    if image.startswith(("http://", "https://")):
        return image
    p = Path(image).expanduser().resolve()
    if not p.exists():
        return image
    h = hashlib.sha1(p.read_bytes()).hexdigest()[:16]
    return f"sha1:{h}"


def _media_id(media: str, prefix: str = "media") -> str:
    """算媒体 ID:sha1(前 16 位) + 前缀。"""
    if media.startswith(("http://", "https://")):
        # URL 不取文件,直接 hash URL
        h = hashlib.sha1(media.encode("utf-8")).hexdigest()[:16]
    else:
        p = Path(media).expanduser().resolve()
        if not p.exists():
            return media
        h = hashlib.sha1(p.read_bytes()).hexdigest()[:16]
    return f"{prefix}-{h[:8]}"


def _media_sha1(media: str) -> str:
    """算 sha1 完整字符串(供 input_inventory 引用)。"""
    if media.startswith(("http://", "https://")):
        return "url:" + hashlib.sha1(media.encode("utf-8")).hexdigest()[:16]
    p = Path(media).expanduser().resolve()
    if not p.exists():
        return "missing"
    return hashlib.sha1(p.read_bytes()).hexdigest()[:32]


def _media_size_bytes(media: str) -> int:
    """算文件大小(URL 时为 0)。"""
    if media.startswith(("http://", "https://")):
        return 0
    p = Path(media).expanduser().resolve()
    if not p.exists():
        return 0
    return p.stat().st_size


def _check_media_ext(media: str, supported: set, media_type: str) -> None:
    """检查媒体扩展名,非标准时 warning(不阻断)。"""
    if media.startswith(("http://", "https://")):
        return
    p = Path(media).expanduser().resolve()
    if not p.exists():
        return
    ext = p.suffix.lower()
    if ext not in supported:
        LOG.warning("非标准 %s 格式:%s(支持 %s)", media_type, ext, sorted(supported))


# -----------------------------------------------------------------------------
# 关键词合并:user-keywords → user_overrides 草稿
# -----------------------------------------------------------------------------

_KEYWORD_RULES = [
    # (匹配关键词子串, 类别, 注入字段路径)
    ("推近", "camera", "cinematography.recommended_camera_motion"),
    ("拉远", "camera", "cinematography.recommended_camera_motion"),
    ("环绕", "camera", "cinematography.recommended_camera_motion"),
    ("固定", "camera", "cinematography.recommended_camera_motion"),
    ("电影", "style", "aesthetic.style"),
    ("胶片", "style", "aesthetic.style"),
    ("写实", "style", "aesthetic.style"),
    ("二次元", "style", "aesthetic.style"),
    ("温暖", "mood", "aesthetic.mood"),
    ("紧张", "mood", "aesthetic.mood"),
    ("平静", "mood", "aesthetic.mood"),
    ("史诗", "mood", "aesthetic.mood"),
    ("转头", "action", "dynamic.suggested_action"),
    ("跑步", "action", "dynamic.suggested_action"),
    ("风吹", "action", "dynamic.suggested_action"),
    ("微笑", "action", "dynamic.suggested_action"),
    # v2.0 扩展
    ("续写", "continuation", "video_metadata.continuation_intent"),
    ("风格化", "continuation", "video_metadata.continuation_intent"),
    ("restyle", "continuation", "video_metadata.continuation_intent"),
    ("循环", "continuation", "video_metadata.continuation_intent"),
    ("主体身份", "role", "reference_assignments[0].role"),
    ("场景色调", "role", "reference_assignments[1].role"),
    ("镜头参考", "role", "reference_assignments[2].role"),
]


def _classify_keywords(keywords: List[str]) -> Dict[str, Any]:
    """把用户关键词分类 + 标注 merge 目标字段。返回 user_overrides 草稿。"""
    classified: Dict[str, List[str]] = {
        "camera": [], "style": [], "mood": [], "action": [],
        "continuation": [], "role": [],
    }
    merged_into: Dict[str, str] = {}
    for kw in keywords:
        kw_lower = kw.lower()
        hit = False
        for needle, category, field in _KEYWORD_RULES:
            if needle in kw or needle in kw_lower:
                classified[category].append(kw)
                merged_into[field] = f"{kw} (用户强化)"
                hit = True
                break
        if not hit:
            # 未识别关键词归 "other",不强行注入,留 vision 决定
            classified.setdefault("other", []).append(kw)
    return {
        "raw_keywords": keywords,
        "classified": {k: v for k, v in classified.items() if v},
        "merged_into": merged_into,
    }


# -----------------------------------------------------------------------------
# Vision 调用
# -----------------------------------------------------------------------------

def _build_user_message(
    image_uris: List[str],
    keywords: List[str],
    text: str = "",
) -> Dict[str, Any]:
    """构建 vision 调用的 user message(支持多图)。"""
    text_parts = ["请分析这些输入。"]
    if text:
        text_parts.append(f"\n用户文本需求: {text}")
    if keywords:
        text_parts.append(
            f"\n用户额外关键词(供参考,优先级高于 vision 默认建议):{' / '.join(keywords)}"
        )
    text_combined = "".join(text_parts)

    content: List[Dict[str, Any]] = [{"type": "text", "text": text_combined}]
    for uri in image_uris:
        content.append({"type": "image_url", "image_url": {"url": uri}})
    return {"role": "user", "content": content}


def _call_vision(
    messages: List[Dict[str, Any]],
    *,
    model: str,
    max_tokens: int,
    cred: Dict[str, Any],
) -> str:
    """调 /v1/text/chatcompletion_v2,返回 content 字符串。"""
    url = f"{cred['base_url']}/v1/text/chatcompletion_v2"
    headers = {
        "Authorization": f"Bearer {cred['api_key']}",
        "api-key": cred["api_key"],
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.4,  # vision 偏结构化,温度低
    }
    LOG.info("调 vision 模型:%s (max_tokens=%d)", model, max_tokens)
    if mm_client is not None:
        data = mm_client.request(
            "POST", url, headers=headers, json_body=body,
            timeout=cred.get("timeout", 60),
        )
    else:
        # fallback:无 mm_client 时直接 requests
        resp = requests.post(url, headers=headers, json=body, timeout=cred.get("timeout", 60))
        resp.raise_for_status()
        data = resp.json()
    # 解析 content
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"vision 响应解析失败:{e};raw={json.dumps(data, ensure_ascii=False)[:300]}")


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """从模型输出里抠 JSON。兼容 markdown ```json 包裹 / 前缀说明。"""
    text = text.strip()
    # 1) 整体就是 JSON
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    # 2) ```json ... ``` 包裹
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # 3) 抓首个 { 到末尾 }
    start = text.find("{")
    if start >= 0:
        try:
            return json.loads(text[start:])
        except json.JSONDecodeError:
            pass
    return None


# -----------------------------------------------------------------------------
# Schema 校验 + 降级
# -----------------------------------------------------------------------------

REQUIRED_TOP_FIELDS_V1 = [
    "version", "image_id", "analyzed_at",
    "subject", "scene", "cinematography", "aesthetic", "dynamic",
]

REQUIRED_TOP_FIELDS_V2 = [
    "version", "input_mode", "analyzed_at", "input_inventory",
    "subject", "scene", "cinematography", "aesthetic", "dynamic",
]


def _build_input_inventory(
    images: List[str],
    videos: List[str],
    audios: List[str],
    text: str,
) -> Dict[str, Any]:
    """构建 input_inventory 字段(v2.0 必填)。"""
    inv_images = []
    for i, img in enumerate(images, 1):
        _check_media_ext(img, SUPPORTED_IMAGE_EXTS, "image")
        inv_images.append({
            "id": f"img-{i}",
            "source": img,
            "sha1": _media_sha1(img),
            "size_bytes": _media_size_bytes(img),
        })
    inv_videos = []
    for i, vid in enumerate(videos, 1):
        _check_media_ext(vid, SUPPORTED_VIDEO_EXTS, "video")
        # 注:duration_s / fps / key_frames 由 vision 模型填充,本地只填 source
        inv_videos.append({
            "id": f"vid-{i}",
            "source": vid,
            "sha1": _media_sha1(vid),
            "size_bytes": _media_size_bytes(vid),
        })
    inv_audios = []
    for i, aud in enumerate(audios, 1):
        _check_media_ext(aud, SUPPORTED_AUDIO_EXTS, "audio")
        inv_audios.append({
            "id": f"aud-{i}",
            "source": aud,
            "sha1": _media_sha1(aud),
            "size_bytes": _media_size_bytes(aud),
        })
    return {
        "images": inv_images,
        "videos": inv_videos,
        "audios": inv_audios,
        "user_text": text,
    }


def _normalize_report_v1(
    raw: Dict[str, Any], *, image: str, keywords: List[str]
) -> Dict[str, Any]:
    """v1.0 兜底:补齐必填字段 / version / analyzed_at / image_id / user_overrides。"""
    report = dict(raw)  # 浅拷贝
    report["version"] = "1.0"
    report["image_id"] = report.get("image_id") or _image_id(image)
    report["analyzed_at"] = report.get("analyzed_at") or _utcnow_iso()

    # user_overrides:模型可能没填 → 用关键词分类结果补
    if not report.get("user_overrides") and keywords:
        report["user_overrides"] = _classify_keywords(keywords)
    elif keywords:
        # 模型填了 user_overrides,但 raw_keywords 不全 → 补 raw_keywords
        existing = report["user_overrides"].get("raw_keywords") or []
        if set(existing) != set(keywords):
            report["user_overrides"]["raw_keywords"] = keywords

    # 必填顶层兜底
    for f in REQUIRED_TOP_FIELDS_V1:
        report.setdefault(f, "unknown" if f != "subject" else {"name": "unknown"})

    if not report.get("analyzer_status"):
        report["analyzer_status"] = "ok"
    return report


def _normalize_report_v2(
    raw: Dict[str, Any],
    *,
    images: List[str],
    videos: List[str],
    audios: List[str],
    text: str,
    keywords: List[str],
    input_mode: str,
) -> Dict[str, Any]:
    """v2.0 兜底:补齐必填字段 / version / analyzed_at / input_mode / input_inventory。"""
    report = dict(raw)
    report["version"] = "2.0"
    report["input_mode"] = report.get("input_mode") or input_mode
    report["analyzed_at"] = report.get("analyzed_at") or _utcnow_iso()

    # input_inventory 兜底
    if not report.get("input_inventory"):
        report["input_inventory"] = _build_input_inventory(images, videos, audios, text)

    # user_overrides(扩展 v2.0:含 user_text)
    if not report.get("user_overrides"):
        report["user_overrides"] = _classify_keywords(keywords)
        if text:
            report["user_overrides"]["user_text"] = text
    elif keywords or text:
        # 模型填了 user_overrides,但 raw_keywords / user_text 不全 → 补
        existing = report["user_overrides"].get("raw_keywords") or []
        if keywords and set(existing) != set(keywords):
            report["user_overrides"]["raw_keywords"] = keywords
        if text and "user_text" not in report["user_overrides"]:
            report["user_overrides"]["user_text"] = text

    # 必填顶层兜底
    for f in REQUIRED_TOP_FIELDS_V2:
        if f == "subject":
            report.setdefault(f, {"name": "unknown"})
        else:
            report.setdefault(f, "unknown")

    # ref2v 模式:reference_assignments 兜底(空数组,标 unknown)
    if input_mode == "ref2v" and not report.get("reference_assignments"):
        report["reference_assignments"] = []

    # v2v 模式:video_metadata 兜底
    if input_mode == "v2v" and not report.get("video_metadata"):
        report["video_metadata"] = {
            "source_video": videos[0] if videos else "unknown",
            "duration_s": 0,
            "key_frames": [],
            "last_frame_description": "unknown",
            "continuation_intent": "extend",
        }

    if not report.get("analyzer_status"):
        report["analyzer_status"] = "ok"
    return report


def _fallback_report_v1(image: str, reason: str, keywords: List[str]) -> Dict[str, Any]:
    """v1.0 vision 完全失败时的 partial schema(参考 image-schema.md §8)。"""
    report = {
        "version": "1.0",
        "image_id": _image_id(image),
        "analyzed_at": _utcnow_iso(),
        "subject": {"name": "unknown", "count": 0, "position": "unknown", "pose": "unknown"},
        "scene": {"type": "unknown", "key_elements": []},
        "cinematography": {"framing": "unknown", "angle": "unknown", "composition": "unknown"},
        "aesthetic": {"style": "unknown", "lighting": "unknown", "mood": "neutral"},
        "dynamic": {
            "movable_subjects": [],
            "recommended_camera_motion": {
                "type": "static",
                "amplitude": "medium",
                "speed": "normal",
                "rationale": f"无法识别主体,使用保守默认值(reason={reason})",
            },
            "recommended_duration": 5,
            "recommended_rhythm": "normal",
        },
        "constraints": {"must_not_change": [], "high_risk_motion": []},
        "analyzer_status": f"partial: {reason}",
    }
    if keywords:
        report["user_overrides"] = _classify_keywords(keywords)
    return report


def _fallback_report_v2(
    reason: str,
    images: List[str],
    videos: List[str],
    audios: List[str],
    text: str,
    keywords: List[str],
    input_mode: str,
) -> Dict[str, Any]:
    """v2.0 vision 完全失败时的 partial schema(参考 input-schema.md §6)。"""
    report = {
        "version": "2.0",
        "input_mode": input_mode,
        "analyzed_at": _utcnow_iso(),
        "input_inventory": _build_input_inventory(images, videos, audios, text),
        "subject": {"name": "unknown", "count": 0, "position": "unknown", "pose": "unknown"},
        "scene": {"type": "unknown", "key_elements": []},
        "cinematography": {"framing": "unknown", "angle": "unknown", "composition": "unknown"},
        "aesthetic": {"style": "unknown", "lighting": "unknown", "mood": "neutral"},
        "dynamic": {
            "movable_subjects": [],
            "recommended_camera_motion": {
                "type": "static",
                "amplitude": "medium",
                "speed": "normal",
                "rationale": f"无法识别主体,使用保守默认值(reason={reason})",
            },
            "recommended_duration": 5,
            "recommended_rhythm": "normal",
        },
        "constraints": {"must_not_change": [], "high_risk_motion": []},
        "analyzer_status": f"partial: {reason}",
    }
    if keywords or text:
        overrides = _classify_keywords(keywords)
        if text:
            overrides["user_text"] = text
        report["user_overrides"] = overrides
    if input_mode == "ref2v":
        report["reference_assignments"] = []
    if input_mode == "v2v" and videos:
        report["video_metadata"] = {
            "source_video": videos[0],
            "duration_s": 0,
            "key_frames": [],
            "last_frame_description": "unknown",
            "continuation_intent": "extend",
        }
    return report


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def _get_credentials() -> Dict[str, Any]:
    """优先用 minimax-multimodal 的 get_credentials,失败再降级。"""
    if mm_client is not None:
        return mm_client.get_credentials()
    # fallback:直读环境变量
    key = os.environ.get("MINIMAX_API_KEY", "").strip()
    base = os.environ.get("MINIMAX_BASE_URL", "").strip() or "https://api.minimaxi.com"
    if not key:
        raise RuntimeError(
            "未找到 API Key。请设置以下任一环境变量:\n"
            "  - MINIMAX_API_KEY(国内)\n"
            "  - MINIMAX_GLOBAL_API_KEY(国际)\n"
            "  - 或在项目根目录 .env 配置"
        )
    return {
        "region": "cn" if "minimaxi.com" in base else "global",
        "base_url": base.rstrip("/"),
        "api_key": key,
        "timeout": int(os.environ.get("MINIMAX_TIMEOUT", "60")),
    }


def run_analyze(
    image: Optional[str] = None,
    *,
    keywords: Optional[List[str]] = None,
    model: str = VISION_MODEL_DEFAULT,
    max_tokens: int = 2048,
    # v2.0 多模态参数(可选,None 表示不启用)
    input_mode: str = "auto",
    video: Optional[str] = None,
    frame_time: float = 0.0,
    reference_images: Optional[List[str]] = None,
    audio: Optional[str] = None,
    text: Optional[str] = None,
) -> Dict[str, Any]:
    """主入口:多模态输入 → input-report.json v2.0 / image-report.json v1.0(dict)。

    向后兼容:
      - 仅传 image → v1.0 schema(老接口不变)
      - 传 v2.0 参数 → v2.0 schema
    """
    keywords = keywords or []
    reference_images = reference_images or []

    # 检测请求版本
    use_v2 = bool(
        input_mode != "auto" or video or reference_images or audio or text
    )

    # 收集输入
    images: List[str] = []
    if image:
        images.append(image)
    images.extend(reference_images)

    videos: List[str] = []
    if video:
        videos.append(video)

    audios: List[str] = []
    if audio:
        audios.append(audio)

    text_str = text or ""

    # 判定 input_mode
    detected_mode = _detect_input_mode(
        images, videos, audios, text_str, keywords, input_mode
    )

    # --- v1.0 路径(向后兼容,单图无其他模态) ---
    if not use_v2:
        # 单图处理
        if not image:
            return _fallback_report_v1(
                image="<no image>",
                reason="v1.0 requires --image",
                keywords=keywords,
            )
        try:
            image_uri = _image_to_data_uri(image)
        except FileNotFoundError as e:
            return _fallback_report_v1(image, f"image not found: {e}", keywords)

        try:
            cred = _get_credentials()
        except RuntimeError as e:
            LOG.error("[FATAL] %s", e)
            return _fallback_report_v1(image, f"credentials missing: {e}", keywords)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT_V1},
            _build_user_message([image_uri], keywords),
        ]

        try:
            content = _call_vision(messages, model=model, max_tokens=max_tokens, cred=cred)
        except Exception as e:
            LOG.warning("vision 调用失败:%s;降级 partial schema", e)
            return _fallback_report_v1(image, f"vision error: {e}", keywords)

        raw = _extract_json(content)
        if raw is None:
            LOG.warning("模型输出非 JSON,降级 partial schema。raw[:200]=%s", content[:200])
            return _fallback_report_v1(image, "vision returned non-JSON", keywords)

        report = _normalize_report_v1(raw, image=image, keywords=keywords)
        LOG.info(
            "vision OK (v1.0):subject=%s",
            report["subject"].get("name"),
        )
        return report

    # --- v2.0 路径(多模态) ---
    # 预处理图片(本地 → data URI)
    image_uris: List[str] = []
    for img in images:
        try:
            image_uris.append(_image_to_data_uri(img))
        except FileNotFoundError as e:
            LOG.warning("图片跳过:%s", e)

    if not image_uris and not videos and not audios and not text_str and not keywords:
        return _fallback_report_v2(
            "no valid input",
            images, videos, audios, text_str, keywords, detected_mode,
        )

    try:
        cred = _get_credentials()
    except RuntimeError as e:
        LOG.error("[FATAL] %s", e)
        return _fallback_report_v2(
            f"credentials missing: {e}",
            images, videos, audios, text_str, keywords, detected_mode,
        )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_V2},
        _build_user_message(image_uris, keywords, text_str),
    ]

    try:
        content = _call_vision(messages, model=model, max_tokens=max_tokens, cred=cred)
    except Exception as e:
        LOG.warning("vision 调用失败:%s;降级 partial schema", e)
        return _fallback_report_v2(
            f"vision error: {e}",
            images, videos, audios, text_str, keywords, detected_mode,
        )

    raw = _extract_json(content)
    if raw is None:
        LOG.warning("模型输出非 JSON,降级 partial schema。raw[:200]=%s", content[:200])
        return _fallback_report_v2(
            "vision returned non-JSON",
            images, videos, audios, text_str, keywords, detected_mode,
        )

    report = _normalize_report_v2(
        raw,
        images=images,
        videos=videos,
        audios=audios,
        text=text_str,
        keywords=keywords,
        input_mode=detected_mode,
    )
    LOG.info(
        "vision OK (v2.0):input_mode=%s,subject=%s",
        report["input_mode"],
        report["subject"].get("name"),
    )
    return report


def _parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "i2v-image-analyzer / video-input-analyzer:vision 调用实现层\n"
            "  v1.0 兼容: --image <path> --keywords <str> --out <path>\n"
            "  v2.0 多模态: --input-mode {auto,i2v,t2v,v2v,ref2v,mm2v} "
            "--video / --reference-images / --audio / --text"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # v1.0 兼容参数
    p.add_argument("--image", help="图片路径或 HTTP(S) URL(v1.0 必填,v2.0 可选)")
    p.add_argument("--keywords", default="", help="空格分隔的用户关键词,可选")
    p.add_argument("--out", default="-", help="输出文件路径,默认 stdout")
    p.add_argument("--model", default=VISION_MODEL_DEFAULT, help=f"vision 模型(默认 {VISION_MODEL_DEFAULT})")
    p.add_argument("--max-tokens", type=int, default=2048, help="最大输出 token")
    p.add_argument("--log-level", default="INFO", help="日志级别")

    # v2.0 多模态参数
    p.add_argument(
        "--input-mode",
        default="auto",
        choices=SUPPORTED_INPUT_MODES,
        help="输入模式(默认 auto 自动判定)",
    )
    p.add_argument("--video", help="视频文件路径(v2v 模式)")
    p.add_argument(
        "--frame-time",
        type=float,
        default=0.0,
        help="视频关键帧时间点(秒,默认 0 = 首帧)",
    )
    p.add_argument(
        "--reference-images",
        nargs="+",
        default=[],
        help="多张参考图(ref2v 模式,空格分隔)",
    )
    p.add_argument("--audio", help="音频文件路径(ref2v 模式)")
    p.add_argument("--text", help="用户文本(t2v 模式 / 一般需求描述)")

    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    _setup_logging(args.log_level)
    keywords = [k for k in args.keywords.split() if k]

    report = run_analyze(
        image=args.image,
        keywords=keywords,
        model=args.model,
        max_tokens=args.max_tokens,
        input_mode=args.input_mode,
        video=args.video,
        frame_time=args.frame_time,
        reference_images=args.reference_images,
        audio=args.audio,
        text=args.text,
    )
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out == "-":
        sys.stdout.write(payload + "\n")
    else:
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload, encoding="utf-8")
        LOG.info("已写入:%s (version=%s)", out_path, report.get("version"))
    # 降级态退出码非零,方便 pipeline 监控
    status = report.get("analyzer_status", "ok")
    return 0 if status == "ok" else 2


if __name__ == "__main__":
    sys.exit(main())
