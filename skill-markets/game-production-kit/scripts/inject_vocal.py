"""把 voice/manifest.json 中记录的 playVocal 插入到对应 scene 脚本的对话行/旁白行后。

新 manifest 格式：
{
  "voices": {...},
  "lines": [
    {"scene": "start.txt", "line": 3, "speaker": "...", "text": "...", "audio": "v_..."},
    ...
  ]
}

特点：
- 严格按 line 号插入（在匹配行的下一行插入 playVocal）
- 用幂等检查：playVocal 已存在则跳过
- 保留原脚本的 ;、换行、缩进
- 不修改 if/choose/label 等控制流
- 旁白行也支持（{旁白}:...;）
"""
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"d:\workspace\ai-github\OpenWebGAL\WebGAL_Demo")
CASE = ROOT / "webgal_case02"
SCENE_DIR = CASE / "scene"
MANIFEST = CASE / "voice" / "manifest.json"

RE_BRACKET = re.compile(r"^\{")
COMMAND_KEYWORDS = {
    "changeBg", "changeFigure", "bgm", "choose", "jumpLabel", "label",
    "setVar", "changeScene", "callScene", "playEffect", "pixiInit",
    "pixiPerform", "if", "unlockCg", "unlockBgm", "filmMode", "miniAvatar",
    "playVideo", "intro", "say", "end", "getUserInput", "showVars",
    "setTextbox", "setAnimation", "setTransform", "applyStyle",
    "setComplexAnimation", "setTempAnimation", "setTransition",
    "playVocal", "wait",
}
RE_DIALOGUE = re.compile(r"^([^:\s{][^:\s{]*?):(.+);$")
RE_NARRATOR = re.compile(r"^\s*\{旁白\}:(.+);$")
VALID_SPEAKERS = {"邱苏晚", "林之一", "咖啡馆老板", "旁白", "新闻主播", "主持人"}


def is_dialogue_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if s.startswith(";") or s.startswith("//"):
        return False
    if RE_NARRATOR.match(s):
        return True
    if RE_BRACKET.match(s):
        return False
    if s.startswith(":"):
        return False
    m = RE_DIALOGUE.match(s)
    if not m:
        return False
    speaker = m.group(1).strip()
    if speaker in COMMAND_KEYWORDS:
        return False
    if speaker not in VALID_SPEAKERS:
        return False
    return True


def process_scene(scene_name: str, items: list) -> tuple:
    """处理单个 scene 文件。返回 (inserted, already_present, replaced, total)"""
    path = SCENE_DIR / scene_name
    if not path.exists():
        return 0, 0, 0
    lines = path.read_text(encoding="utf-8").splitlines(keepends=False)
    line_to_audio = {item["line"]: item["audio"] for item in items}
    # 找到所有需要清理的旧 playVocal（与新生成文件名不同的）
    expected_audios = set(line_to_audio.values())

    out_lines = []
    inserted = already = replaced = 0
    pending_audio = None  # 当前对话行后需要插入的音频
    for idx, raw in enumerate(lines, start=1):
        # 跳过被替换的旧 playVocal：如果当前 raw 是 playVocal 且不在期望列表中，且 idx-1 有音频要插入
        s = raw.strip()
        if s.startswith("playVocal:") and pending_audio is not None:
            # 解析旧 audio 名
            old_audio = s[len("playVocal:") :].rstrip(";").strip()
            if old_audio == pending_audio:
                # 已正确指向新文件，跳过
                already += 1
                pending_audio = None
                continue
            else:
                # 旧 playVocal 与新文件名不匹配，替换
                replaced += 1
                indent = raw[: len(raw) - len(raw.lstrip())]
                out_lines.append(f"{indent}playVocal:{pending_audio};")
                pending_audio = None
                continue
        elif s.startswith("playVocal:"):
            # 不在 pending_audio 列表中：可能是孤立的 playVocal，跳过（清理）
            continue

        out_lines.append(raw)
        if idx in line_to_audio:
            audio = line_to_audio[idx]
            if not is_dialogue_line(raw):
                print(
                    f"  [WARN] {scene_name} L{idx} 不是对话/旁白行，但 manifest 指定了音频: {raw!r}",
                    flush=True,
                )
                continue
            pending_audio = audio

    # 末尾未关闭的 pending_audio
    if pending_audio is not None:
        out_lines.append(f"playVocal:{pending_audio};")
        inserted += 1

    new_content = "\n".join(out_lines) + "\n"
    path.write_text(new_content, encoding="utf-8")
    return inserted, already, replaced, len(items)


def main():
    if not MANIFEST.exists():
        print(f"manifest.json 不存在: {MANIFEST}")
        sys.exit(1)
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # 新格式: {"voices":..., "lines": [...]}
    if "lines" in data and isinstance(data["lines"], list):
        lines = data["lines"]
        # 按 scene 分组
        by_scene = {}
        for item in lines:
            by_scene.setdefault(item["scene"], []).append(item)
    else:
        # 旧格式兼容
        by_scene = data

    print(f"manifest 覆盖 {len(by_scene)} 个 scene", flush=True)
    total_inserted = total_already = total_replaced = total = 0
    scripts_with_vocal = 0
    for scene_name, items in by_scene.items():
        ins, already, replaced, tot = process_scene(scene_name, items)
        total_inserted += ins
        total_already += already
        total_replaced += replaced
        total += tot
        if ins > 0 or already > 0 or replaced > 0:
            scripts_with_vocal += 1
        status = "OK" if (ins + already + replaced) > 0 else "nochange"
        print(
            f"  [{status}] {scene_name}: insert={ins} already={already} replaced={replaced} total={tot}",
            flush=True,
        )
    print()
    print(f"scripts_with_vocal: {scripts_with_vocal}", flush=True)
    print(f"total_inserted: {total_inserted}", flush=True)
    print(f"total_already: {total_already}", flush=True)
    print(f"total_replaced: {total_replaced}", flush=True)


if __name__ == "__main__":
    main()
