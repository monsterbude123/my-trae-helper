"""TTS 批量生成（Qwen3 VoiceDesign，urllib 直接调 ComfyUI）。

权威 workflow：.trae/skills/webgal-create-deploy-skill/templates/workflows/tts_qwen.json

任务：
- 朗读 webgal_case02/scene/*.txt 中的所有对话行 + 旁白行
- 匹配 `角色:内容;` 与 `{旁白}:内容;` 两种形式
- 不同 speaker 用不同 instruct（从 voices.json 读取 5 维度配置）
- max_new_tokens：≤25 字→300，>25 字→500
- temperature/top_p/repetition_penalty 来自 voices.json（音色稳定）
- 强制重生成（先删除 voice/*.flac 和 _work/.../voice/*.flac）
- 每条独立 seed
- 输出 flac 到 webgal_case02/voice/
- 文件名 v_<scene>_<index>_<speaker>.flac
- 进度每 5 个文件打印一次
- 生成 manifest.json（含 voices 配置 + lines 清单）
"""
import json
import os
import re
import shutil
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(r"d:\workspace\ai-github\OpenWebGAL\WebGAL_Demo")
CASE = ROOT / "webgal_case02"
SCENE_DIR = CASE / "scene"
VOICE_DIR = CASE / "voice"
GEN_VOICE = ROOT / "_work" / "gen_voice"
ENGINE_PUBLIC_VOICE = ROOT / "_work" / "webgal-engine" / "public" / "game" / "voice"
VOICES_JSON = VOICE_DIR / "voices.json"
MANIFEST_PATH = VOICE_DIR / "manifest.json"
LOG_PATH = ROOT / "_work" / "gen_voice_v2.log"

# 独立日志文件（解决 stdout 重定向缓冲问题）
_LOG_HANDLE = open(LOG_PATH, "a", encoding="utf-8", buffering=1)  # line buffered

def _log(*args, **kwargs):
    end = kwargs.get("end", "\n")
    msg = " ".join(str(a) for a in args) if args else ""
    _LOG_HANDLE.write(msg + end)
    _LOG_HANDLE.flush()
    print(msg, end=end, flush=True)


for d in (VOICE_DIR, GEN_VOICE, ENGINE_PUBLIC_VOICE):
    d.mkdir(parents=True, exist_ok=True)

COMFY = "http://127.0.0.1:8188"
TPL = ROOT / ".trae/skills/webgal-create-deploy-skill/templates/workflows/tts_qwen.json"

# ---------------------------------------------------------------------------
# 命令行（speaker 行首不能是这些）
# ---------------------------------------------------------------------------
COMMAND_KEYWORDS = {
    "changeBg", "changeFigure", "bgm", "choose", "jumpLabel", "label",
    "setVar", "changeScene", "callScene", "playEffect", "pixiInit",
    "pixiPerform", "if", "unlockCg", "unlockBgm", "filmMode", "miniAvatar",
    "playVideo", "intro", "say", "end", "getUserInput", "showVars",
    "setTextbox", "setAnimation", "setTransform", "applyStyle",
    "setComplexAnimation", "setTempAnimation", "setTransition",
    "playVocal", "wait",
}

# 6 个有效 speaker（含旁白）
VALID_SPEAKERS = {"邱苏晚", "林之一", "咖啡馆老板", "旁白", "新闻主播", "主持人"}

# 普通对话行：speaker:content;（行首不以 { 开头）
RE_DIALOGUE = re.compile(r"^([^:\s{][^:\s{]*?):(.+);$")
# 旁白行：{旁白}:content;（允许前后空格）
RE_NARRATOR = re.compile(r"^\s*\{旁白\}:(.+);$")

# speaker → 文件名 token
SPEAKER_TOKEN = {
    "邱苏晚": "qiusuwan",
    "林之一": "linzhiyi",
    "咖啡馆老板": "cafeboss",
    "旁白": "narrator",
    "新闻主播": "newsanchor",
    "主持人": "host",
}


def safe_name(speaker: str) -> str:
    return SPEAKER_TOKEN.get(speaker, "narrator")


def load_voices() -> dict:
    return json.loads(VOICES_JSON.read_text(encoding="utf-8"))["speakers"]


def is_pure_brackets_line(s: str) -> bool:
    """是否以 { 开头但不匹配旁白的行（如 {系统提示}）"""
    return s.startswith("{") and not RE_NARRATOR.match(s)


def parse_dialogues() -> list:
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

            results.append(
                {"scene": scene, "line": i, "speaker": speaker, "text": text}
            )
    return results


def clean_text_for_tts(text: str) -> str:
    """TTS 前清理：去掉外层引号、首尾空格"""
    t = text.strip()
    # 去掉成对的中文/英文引号
    for q in ('"', '"', '"', ''', ''', "'", "'"):
        if t.startswith(q) and t.endswith(q):
            t = t[1:-1].strip()
            break
    return t


def main():
    _log("=" * 70)
    _log("Step 1: 加载 voices.json 配置")
    _log("=" * 70)
    voices = load_voices()
    for sp, cfg in voices.items():
        _log(
            f"  {sp}: temperature={cfg.get('temperature')}, "
            f"top_p={cfg.get('top_p')}, rep_pen={cfg.get('repetition_penalty')}, "
            f"max_tokens={cfg.get('max_new_tokens')}"
        )

    _log()
    _log("=" * 70)
    _log("Step 2: 解析 scene/*.txt")
    _log("=" * 70)
    dialogues = parse_dialogues()
    _log(f"  共找到 {len(dialogues)} 条")
    by_speaker = {}
    for d in dialogues:
        by_speaker[d["speaker"]] = by_speaker.get(d["speaker"], 0) + 1
    for sp, cnt in sorted(by_speaker.items()):
        _log(f"  {sp}: {cnt} 条")

    # 编号：按 scene 分组，组内 0001 起
    by_scene = {}
    for d in dialogues:
        by_scene.setdefault(d["scene"], []).append(d)
    for scene, items in by_scene.items():
        for idx, item in enumerate(items, start=1):
            item["audio"] = f"v_{scene}_{idx:04d}_{safe_name(item['speaker'])}.flac"

    # 强制重生成：删除所有旧 flac
    _log()
    _log("=" * 70, flush=True)
    _log("Step 3: 强制重生成（先删除旧 flac）", flush=True)
    _log("=" * 70, flush=True)
    removed = 0
    for target_dir in (VOICE_DIR, GEN_VOICE, ENGINE_PUBLIC_VOICE):
        if not target_dir.exists():
            continue
        for f in target_dir.glob("*.flac"):
            f.unlink()
            removed += 1
    _log(f"  删除 {removed} 个旧 flac", flush=True)

    _log()
    _log("=" * 70, flush=True)
    _log("Step 4: 检查 ComfyUI", flush=True)
    _log("=" * 70, flush=True)
    try:
        urllib.request.urlopen(f"{COMFY}/system_stats", timeout=5).read()
        _log("  ComfyUI OK", flush=True)
    except Exception as e:
        _log(f"  ComfyUI 连接失败: {e}", flush=True)
        sys.exit(1)

    template = json.loads(TPL.read_text(encoding="utf-8"))["workflow"]

    def render(text, instruct, seed, prefix, max_new_tokens, temperature, top_p, rep_pen):
        wf = json.loads(json.dumps(template))
        wf["1"]["inputs"]["text"] = text
        wf["1"]["inputs"]["instruct"] = instruct
        wf["1"]["inputs"]["language"] = "Chinese"
        wf["1"]["inputs"]["model_choice"] = "1.7B"
        wf["1"]["inputs"]["seed"] = int(seed)
        wf["1"]["inputs"]["max_new_tokens"] = int(max_new_tokens)
        wf["1"]["inputs"]["temperature"] = float(temperature)
        wf["1"]["inputs"]["top_p"] = float(top_p)
        wf["1"]["inputs"]["repetition_penalty"] = float(rep_pen)
        wf["2"]["inputs"]["filename_prefix"] = prefix
        return wf

    def submit(wf):
        body = json.dumps({"prompt": wf, "client_id": "webgal-gen-voice"}).encode()
        req = urllib.request.Request(
            f"{COMFY}/prompt", data=body, headers={"Content-Type": "application/json"}
        )
        return json.loads(urllib.request.urlopen(req).read())["prompt_id"]

    def poll(pid, timeout=300):
        t0 = time.time()
        while time.time() - t0 < timeout:
            h = json.loads(urllib.request.urlopen(f"{COMFY}/history/{pid}").read())
            if pid in h and h[pid].get("outputs"):
                return h[pid]
            time.sleep(2)
        return None

    def download(history, out_dir):
        files = []
        for node_out in history["outputs"].values():
            for aud in node_out.get("audio", []) or []:
                params = (
                    f"filename={aud['filename']}&subfolder={aud.get('subfolder','')}"
                    f"&type={aud.get('type','output')}"
                )
                data = urllib.request.urlopen(f"{COMFY}/view?{params}").read()
                p = Path(out_dir) / aud["filename"]
                p.write_bytes(data)
                files.append(p)
        return files

    _log()
    _log("=" * 70, flush=True)
    _log("Step 5: 提交 TTS 任务并下载", flush=True)
    _log("=" * 70, flush=True)
    results = []
    ok = fail = 0
    total = len(dialogues)
    for i, d in enumerate(dialogues):
        out = VOICE_DIR / d["audio"]
        speaker = d["speaker"]
        cfg = voices[speaker]
        tts_text = clean_text_for_tts(d["text"])
        # 自适应 max_new_tokens
        # ComfyUI FB_Qwen3TTSVoiceDesign 约束: min=512, step=256, max=4096
        # 经验公式: 音频秒数 × 12.5 + 余量; 中文 4 字/秒
        # 短文本用 min(512),靠 instruct 的 "crisp/forward-moving" 减少拖音
        n_chars = len([c for c in tts_text if not c.isspace()])
        if n_chars <= 25:
            max_new_tokens = 512      # 短句 (min)
        elif n_chars <= 50:
            max_new_tokens = 768      # 中等
        else:
            max_new_tokens = 1024     # 长句
        seed = (int(time.time() * 1000) + i * 7919 + hash(d["audio"]) & 0xFFFFFFFF) & 0x7FFFFFFF
        prefix = d["audio"][:-5]
        _log(
            f"  [{i+1:03d}/{total}] {d['audio']} spk={speaker} chars={n_chars} "
            f"tok={max_new_tokens} seed={seed}",
            flush=True,
        )
        try:
            wf = render(
                tts_text,
                cfg["instruct"],
                seed,
                prefix,
                max_new_tokens,
                cfg["temperature"],
                cfg["top_p"],
                cfg["repetition_penalty"],
            )
            pid = submit(wf)
        except Exception as e:
            _log(f"     submit FAIL: {e}", flush=True)
            fail += 1
            results.append((d, None, 0, f"submit_fail: {e}"))
            continue
        _log(f"     pid={pid[:8]}", flush=True)
        res = poll(pid, timeout=300)
        if not res:
            _log(f"     poll FAIL", flush=True)
            fail += 1
            results.append((d, None, 0, "poll_fail"))
            continue
        files = download(res, GEN_VOICE)
        if not files:
            _log(f"     no audio file", flush=True)
            fail += 1
            results.append((d, None, 0, "no_file"))
            continue
        target = None
        for f in files:
            if f.stem.startswith(prefix):
                target = f
                break
        if target is None:
            target = files[0]
        shutil.copy2(target, out)
        size_kb = out.stat().st_size // 1024
        _log(f"     OK {out.name} {size_kb}KB", flush=True)
        results.append((d, out, size_kb, "ok"))
        ok += 1
        if (i + 1) % 5 == 0:
            _log(
                f"  --- 进度 {i+1}/{total}: {ok} 成功, {fail} 失败 ---",
                flush=True,
            )

    _log()
    _log(f"生成完成: {ok} 成功, {fail} 失败, total {total}", flush=True)

    # Step 6: 生成 manifest.json
    _log()
    _log("=" * 70, flush=True)
    _log("Step 6: 生成 manifest.json", flush=True)
    _log("=" * 70, flush=True)
    lines_arr = []
    for d, out, size_kb, status in results:
        if status != "ok" or out is None:
            continue
        sp = d["speaker"]
        cfg = voices[sp]
        n_chars = len([c for c in clean_text_for_tts(d["text"]) if not c.isspace()])
        max_tok = 768 if n_chars > 25 else 512
        lines_arr.append(
            {
                "scene": d["scene"],
                "line": d["line"],
                "speaker": sp,
                "text": d["text"],
                "audio": d["audio"],
                "instruct_used": cfg["instruct"],
                "params": {
                    "temperature": cfg["temperature"],
                    "top_p": cfg["top_p"],
                    "repetition_penalty": cfg["repetition_penalty"],
                    "max_new_tokens": max_tok,
                    "seed": None,
                },
            }
        )
    manifest = {
        "voices": voices,
        "lines": lines_arr,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _log(f"  写入 {MANIFEST_PATH} ({len(lines_arr)} entries)", flush=True)

    # Step 7: 复制到 _work/webgal-engine/public/game/voice/
    _log()
    _log("=" * 70, flush=True)
    _log("Step 7: 复制到 _work/webgal-engine/public/game/voice/", flush=True)
    _log("=" * 70, flush=True)
    copied = 0
    for d, out, size_kb, status in results:
        if status != "ok" or out is None:
            continue
        try:
            shutil.copy2(out, ENGINE_PUBLIC_VOICE / out.name)
            copied += 1
        except Exception as e:
            _log(f"  [ERR COPY] {out.name}: {e}", flush=True)
    _log(f"  复制完成: {copied} 个文件", flush=True)

    # 报告
    _log()
    _log("=" * 70, flush=True)
    _log("最终报告", flush=True)
    _log("=" * 70, flush=True)
    _log(f"voice_files_generated: {ok}", flush=True)
    _log(f"manifest_entries: {len(lines_arr)}", flush=True)


if __name__ == "__main__":
    main()
