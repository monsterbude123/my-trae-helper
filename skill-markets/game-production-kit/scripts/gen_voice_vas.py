"""TTS 批量生成（voice-acting-skill 引擎，替代 gen_voice.py 的 ComfyUI 管线）。

使用 voice-acting-skill（Voice-Acting-Script-Skill）的 TTS 适配器进行角色配音，
BGM/SFX/AMB/FX 仍走 ComfyUI 管线（gen_audio.py）。

支持引擎（--engine 参数）：
  qwen    — QwenTTS 适配器（默认，支持本地 Gradio 或 DashScope 云端）
  cosy    — CosyVoice 适配器（需本地 CosyVoice Gradio 服务 + prompt wav）
  comfy   — 保留选项，回退到原 gen_voice.py 的 ComfyUI 管线

输入：{game_key}/scene/*.txt（WebGAL 脚本，通过 --game-key 指定）
输出：{game_key}/voice/*.flac + manifest.json

依赖：
  - voice-acting-skill（位于 ~/.trae-cn/skills/Voice-Acting-Script-Skill/）
  - 至少一个 TTS 服务在运行（见 voice-acting-skill/references/ENVIRONMENT.md）
"""

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# 项目路径（基于脚本位置推导，不硬编码机器路径）
# ---------------------------------------------------------------------------
# 脚本位置: .trae/skills/{skill}/scripts/gen_voice_vas.py  → 上推 4 层为项目根
_SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = _SCRIPT_DIR.parents[3]  # .trae/skills/{skill}/scripts/ → 项目根
GAME_KEY = "webgal_case02"      # 通过 --game-key 覆盖
CASE = ROOT / GAME_KEY
SCENE_DIR = CASE / "scene"
VOICE_DIR = CASE / "voice"
ENGINE_PUBLIC_VOICE = ROOT / "_work" / "webgal-engine" / "public" / "game" / "voice"
MANIFEST_PATH = VOICE_DIR / "manifest.json"

# voice-acting-skill 路径（自动查找，只用环境变量）
_user_home = Path(os.environ.get("USERPROFILE", "")) or Path(os.environ.get("HOME", ""))
_VAS_CANDIDATES = [
    _user_home / ".trae-cn" / "skills" / "Voice-Acting-Script-Skill",
    _user_home / ".trae" / "skills" / "Voice-Acting-Script-Skill",
]
VAS_DIR = None
for p in _VAS_CANDIDATES:
    if (p / "scripts").is_dir():
        VAS_DIR = p
        break

if VAS_DIR is None:
    print("[FATAL] voice-acting-skill 未找到。请确认已安装：")
    print("  路径：~/.trae-cn/skills/Voice-Acting-Script-Skill/")
    sys.exit(1)

sys.path.insert(0, str(VAS_DIR / "scripts"))
sys.path.insert(0, str(VAS_DIR / "scripts" / "vaslib"))

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

# 角色 → QwenTTS voice_id 映射（基于 voice-acting-skill 的 DIALECT_MAPPINGS）
# 标准普通话角色使用默认 voice_id，方言角色使用对应映射
SPEAKER_VOICE_MAP: dict[str, str] = {
    "邱苏晚": "Vivian",       # 年轻女性
    "林之一": "Ethan",        # 年轻男性
    "咖啡馆老板": "Dylan",    # 年长男性
    "旁白": "Cherry",         # 中性默认
    "新闻主播": "Sunny",      # 职业女性
    "主持人": "Dylan",        # 男性主持人（与咖啡馆老板共享）
}

# 6 个有效 speaker（含旁白）
VALID_SPEAKERS = set(SPEAKER_VOICE_MAP.keys())

# speaker → 文件名 token
SPEAKER_TOKEN = {
    "邱苏晚": "qiusuwan",
    "林之一": "linzhiyi",
    "咖啡馆老板": "cafeboss",
    "旁白": "narrator",
    "新闻主播": "newsanchor",
    "主持人": "host",
}

# 命令行关键字（行首不能是这些）
COMMAND_KEYWORDS = {
    "changeBg", "changeFigure", "bgm", "choose", "jumpLabel", "label",
    "setVar", "changeScene", "callScene", "playEffect", "pixiInit",
    "pixiPerform", "if", "unlockCg", "unlockBgm", "filmMode", "miniAvatar",
    "playVideo", "intro", "say", "end", "getUserInput", "showVars",
    "setTextbox", "setAnimation", "setTransform", "applyStyle",
    "setComplexAnimation", "setTempAnimation", "setTransition",
    "playVocal", "wait",
}

# ---------------------------------------------------------------------------
# 解析 WebGAL 脚本
# ---------------------------------------------------------------------------

RE_DIALOGUE = re.compile(r"^([^:\s{][^:\s{]*?):(.+);$")
RE_NARRATOR = re.compile(r"^\s*\{旁白\}:(.+);$")


def safe_name(speaker: str) -> str:
    return SPEAKER_TOKEN.get(speaker, "narrator")


def is_pure_brackets_line(s: str) -> bool:
    return s.startswith("{") and not RE_NARRATOR.match(s)


def parse_dialogues() -> list[dict]:
    """遍历所有 scene/*.txt，提取对话行 + 旁白行。"""
    results = []
    for f in sorted(SCENE_DIR.glob("*.txt")):
        scene = f.stem
        lines = f.read_text(encoding="utf-8").splitlines()
        for i, raw in enumerate(lines, start=1):
            line = raw.strip()
            if not line:
                continue
            if line.startswith(";") or line.startswith("//"):
                continue
            if line.startswith(":"):
                continue

            speaker = None
            text = None
            m_nar = RE_NARRATOR.match(line)
            if m_nar:
                speaker = "旁白"
                text = m_nar.group(1).strip()
            else:
                if is_pure_brackets_line(line):
                    continue
                m = RE_DIALOGUE.match(line)
                if not m:
                    continue
                speaker = m.group(1).strip()
                text = m.group(2).strip()
                if speaker in COMMAND_KEYWORDS:
                    continue
                if not text:
                    continue
                if speaker not in VALID_SPEAKERS:
                    continue
                if not re.match(r"^[\u4e00-\u9fffA-Za-z_]", speaker):
                    continue

            results.append({
                "scene": scene,
                "line": i,
                "speaker": speaker,
                "text": text,
            })
    return results


def clean_text_for_tts(text: str) -> str:
    """TTS 前清理：去掉外层引号、首尾空格"""
    t = text.strip()
    for q in ('"', '"', '"', '\u2018', '\u2019', "'", "'"):
        if t.startswith(q) and t.endswith(q):
            t = t[1:-1].strip()
            break
    return t


# ---------------------------------------------------------------------------
# QwenTTS 合成（voice-acting-skill 适配器）
# ---------------------------------------------------------------------------

def synthesize_with_qwen(dialogues: list[dict], qwen_url: str | None, api_key: str | None) -> list[dict]:
    """使用 voice-acting-skill 的 QwenTtsAdapter 合成所有对话。"""
    from vaslib.synthesizer.qwen_tts_adapter import QwenTtsAdapter

    adapter = QwenTtsAdapter(url=qwen_url, api_key=api_key)
    adapter.connect()

    if not adapter.health_check():
        print(f"[FATAL] QwenTTS 服务不可达: url={qwen_url}, api_key={'***' if api_key else None}")
        sys.exit(1)

    print(f"  QwenTTS 服务 OK (url={qwen_url or 'DashScope云端'})")

    # 按 scene 编号
    by_scene = {}
    for d in dialogues:
        by_scene.setdefault(d["scene"], []).append(d)
    for scene, items in by_scene.items():
        for idx, item in enumerate(items, start=1):
            item["audio"] = f"v_{scene}_{idx:04d}_{safe_name(item['speaker'])}.flac"
            item["line_id"] = f"{scene}-L{item['line']}"

    # 构建适配器输入
    lines_input = []
    for d in dialogues:
        tts_text = clean_text_for_tts(d["text"])
        voice = SPEAKER_VOICE_MAP.get(d["speaker"], "Cherry")
        # 可选：从 voices.json 读取 instruct 提升音色质量
        instruct = ""
        lines_input.append({
            "line_id": d.get("line_id", f"{d['scene']}-L{d['line']}"),
            "text": tts_text,
            "annotated_text": tts_text,
            "voice": voice,
            "instruct": instruct,
            "speed": 1.0,
        })

    # 合成前删除旧文件
    removed = 0
    for target_dir in (VOICE_DIR, ENGINE_PUBLIC_VOICE):
        if target_dir.exists():
            for f in target_dir.glob("v_*.flac"):
                f.unlink()
                removed += 1
    print(f"  删除 {removed} 个旧 flac")

    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    tmp_dir = VOICE_DIR / "_vas_tmp"
    tmp_dir.mkdir(exist_ok=True)

    total = len(lines_input)
    results = []
    ok = fail = 0

    def _on_progress(completed, total_count):
        nonlocal ok, fail
        # 进度由 synthesize_batch 的内部计数决定
        pass

    batch_result = adapter.synthesize_batch(lines_input, str(tmp_dir), on_progress=_on_progress)
    ok = batch_result.get("success_count", 0)
    fail = batch_result.get("failure_count", 0)

    # 转换 wav → flac，复制到 voice/ 目录
    for item, result in zip(dialogues, batch_result.get("results", [])):
        audio_path = result.get("audio_path", "")
        if not audio_path or not os.path.isfile(audio_path):
            print(f"  [FAIL] {item.get('audio', '?')}: no audio file")
            results.append((item, None, 0, f"synthesize_fail: {result.get('error', 'unknown')}"))
            continue
        src = Path(audio_path)
        dst = VOICE_DIR / item["audio"]
        # wav → flac（保持兼容性，用 ffmpeg 转换）
        flac_path = dst
        try:
            import subprocess
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error",
                 "-i", str(src), "-ac", "1", "-ar", "24000",
                 str(flac_path)],
                capture_output=True, timeout=30,
            )
        except Exception:
            # fallback: 直接 copy wav 改后缀
            shutil.copy2(src, dst.with_suffix(".wav"))
            # rename to flac extension
            shutil.move(dst.with_suffix(".wav"), flac_path)

        size_kb = flac_path.stat().st_size // 1024 if flac_path.exists() else 0
        status = result.get("status", "unknown")
        if status == "success" and size_kb > 0:
            results.append((item, flac_path, size_kb, "ok"))
        else:
            results.append((item, None, 0, f"failed: {result.get('error', 'unknown')}"))

    # 清理临时目录
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return results


# ---------------------------------------------------------------------------
# 生成 manifest.json
# ---------------------------------------------------------------------------

def generate_manifest(results: list[dict]) -> dict:
    """生成 inject_vocal.py 兼容的 manifest.json。"""
    lines_arr = []
    voices_info = {}
    for d, out, size_kb, status in results:
        if status != "ok" or out is None:
            continue
        sp = d["speaker"]
        voice_id = SPEAKER_VOICE_MAP.get(sp, "Cherry")
        voices_info.setdefault(sp, {
            "voice_id": voice_id,
            "engine": "qwen-tts",
        })
        lines_arr.append({
            "scene": d["scene"],
            "line": d["line"],
            "speaker": sp,
            "text": d["text"],
            "audio": d["audio"],
            "voice_id": voice_id,
        })
    return {
        "_generated_by": "gen_voice_vas.py (voice-acting-skill)",
        "engine": "qwen-tts",
        "voices": voices_info,
        "lines": lines_arr,
    }


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="TTS 批量生成（voice-acting-skill）")
    parser.add_argument("--engine", choices=["qwen", "cosy", "comfy"], default="qwen",
                        help="TTS 引擎（默认 qwen，使用 voice-acting-skill 的 QwenTTS 适配器）")
    parser.add_argument("--qwen-url", default=None,
                        help="QwenTTS 本地服务 URL（如 http://127.0.0.1:15001，留空则走 DashScope 云端）")
    parser.add_argument("--api-key", default=None,
                        help="DashScope API Key（云端模式必需，也可设 DASHSCOPE_API_KEY 环境变量）")
    parser.add_argument("--game-key", default=None,
                        help="游戏目录名（如 webgal_case02，默认从脚本位置推导的项目根下的 webgal_case02）")
    args = parser.parse_args()

    # 更新 game key（若指定）
    global GAME_KEY, CASE, SCENE_DIR, VOICE_DIR, MANIFEST_PATH
    if args.game_key:
        GAME_KEY = args.game_key
        CASE = ROOT / GAME_KEY
        SCENE_DIR = CASE / "scene"
        VOICE_DIR = CASE / "voice"
        MANIFEST_PATH = VOICE_DIR / "manifest.json"

    print("=" * 60)
    print(f"gen_voice_vas.py  — 引擎: {args.engine}")
    print("=" * 60)
    print(f"voice-acting-skill: {VAS_DIR}")
    print(f"游戏目录: {CASE}")

    # Step 1: 解析 scene/*.txt
    print()
    print("Step 1: 解析 scene/*.txt")
    dialogues = parse_dialogues()
    print(f"  共找到 {len(dialogues)} 条对话")
    by_sp = {}
    for d in dialogues:
        by_sp[d["speaker"]] = by_sp.get(d["speaker"], 0) + 1
    for sp, cnt in sorted(by_sp.items()):
        print(f"  {sp}: {cnt} 条 → voice_id={SPEAKER_VOICE_MAP.get(sp, '?')}")

    if not dialogues:
        print("  无对话需要合成，退出")
        return

    # Step 2: 合成
    print()
    print("Step 2: TTS 合成")
    api_key = args.api_key or os.environ.get("DASHSCOPE_API_KEY") or os.environ.get("QWEN_TTS_API_KEY")

    if args.engine == "qwen":
        results = synthesize_with_qwen(dialogues, args.qwen_url, api_key)
    elif args.engine == "cosy":
        print("[TODO] CosyVoice 适配器尚未集成，暂回退到 qwen")
        results = synthesize_with_qwen(dialogues, None, api_key)
    else:
        print("请使用 gen_voice.py（ComfyUI 管线）")
        sys.exit(1)

    ok = sum(1 for _, _, _, s in results if s == "ok")
    fail = sum(1 for _, _, _, s in results if s != "ok")
    print(f"  合成完成: {ok} 成功, {fail} 失败 / {len(results)}")

    # Step 3: 生成 manifest.json
    print()
    print("Step 3: 生成 manifest.json")
    manifest = generate_manifest(results)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  写入 {MANIFEST_PATH} ({len(manifest['lines'])} entries)")

    # Step 4: 复制到 engine
    print()
    print("Step 4: 复制到 _work/webgal-engine/public/game/voice/")
    ENGINE_PUBLIC_VOICE.mkdir(parents=True, exist_ok=True)
    copied = 0
    for d, out, size_kb, status in results:
        if status != "ok" or out is None:
            continue
        shutil.copy2(out, ENGINE_PUBLIC_VOICE / out.name)
        copied += 1
    print(f"  复制完成: {copied} 个文件")

    print()
    print("完成。运行 inject_vocal.py 将 playVocal 插入场景脚本。")


if __name__ == "__main__":
    main()
