#!/usr/bin/env python3
"""ComfyUI 懒人功能菜单。

用法：
    # 列出所有功能
    python comfy_menu.py list

    # 一键执行
    python comfy_menu.py run remove_bg -i my_photo.png
    python comfy_menu.py run upscale_4x -i my_photo.png
    python comfy_menu.py run watermark -i my_photo.png

    # 覆盖输出目录 / 前缀
    python comfy_menu.py run remove_bg -i in.png --out ./results --prefix MyBG

menu.yaml 放 example/comfyui-test/ 下，可自由增删功能条目。
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
PIPELINE = SCRIPT_DIR / "comfy_pipeline.py"

# 默认从 CWD 找 menu.yaml；也支持环境变量 COMFYUI_MENU_FILE
DEFAULT_CWD = Path.cwd()
MENU_FILE_ENV = "COMFYUI_MENU_FILE"


def load_menu() -> dict:
    menu_path = os.environ.get(MENU_FILE_ENV, "")
    if menu_path:
        p = Path(menu_path)
    else:
        p = DEFAULT_CWD / "menu.yaml"
    if not p.is_file():
        print(f"[错误] 找不到 menu.yaml: {p}", file=sys.stderr)
        print(f"       请 cd 到 example/comfyui-test 或设置 {MENU_FILE_ENV}", file=sys.stderr)
        sys.exit(2)
    menu = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    # 解析 json 相对路径
    base = p.parent
    for name, item in menu.items():
        jpath = item.get("json", "")
        if jpath and not Path(jpath).is_absolute():
            item["_json_abs"] = str(base / jpath)
        else:
            item["_json_abs"] = jpath
    return menu


def cmd_list(_args):
    menu = load_menu()
    if not menu:
        print("(空菜单)")
        return 0
    print(f"{'功能名':<16} {'说明'}")
    print("-" * 60)
    for name, item in menu.items():
        desc = item.get("desc", "")
        note = item.get("note", "")
        suffix = f"  [注意: {note}]" if note else ""
        print(f"  {name:<14} {desc}{suffix}")
    return 0


def cmd_run(args):
    menu = load_menu()
    if args.func not in menu:
        print(f"[错误] 未知功能: {args.func}", file=sys.stderr)
        print(f"       可用: {', '.join(menu.keys())}", file=sys.stderr)
        return 2

    item = menu[args.func]
    json_path = item.get("_json_abs", "")
    if not json_path or not Path(json_path).is_file():
        print(f"[错误] JSON 不存在: {json_path}", file=sys.stderr)
        return 3

    # 构建 comfy_pipeline.py 命令行
    cmd = [sys.executable, str(PIPELINE), "--json", json_path]

    if args.image:
        # 复制到 ComfyUI input 目录
        src = Path(args.image)
        if not src.is_file():
            print(f"[错误] 图片不存在: {args.image}", file=sys.stderr)
            return 4
        basename = src.name
        # 尝试放到 ComfyUI input 目录
        comfy_input = _find_comfyui_input()
        if comfy_input:
            dst = comfy_input / basename
            import shutil
            shutil.copy2(src, dst)
            print(f"[copy] {src.name} → {dst}")
            cmd.extend(["-i", basename])
        else:
            cmd.extend(["-i", args.image])

    prefix = args.prefix or args.func.replace("_", "-")
    cmd.extend(["--output-prefix", prefix])

    out = args.out or f"./out/{args.func}"
    cmd.extend(["--output-dir", str(out)])

    # 音频参数
    if args.audio_duration is not None:
        cmd.extend(["--audio-duration", str(args.audio_duration)])
    if args.audio_category:
        cmd.extend(["--audio-category", args.audio_category])
    if args.audio_description:
        cmd.extend(["--audio-description", args.audio_description])
    if args.generate_prompt:
        cmd.extend(["--generate-prompt", args.generate_prompt])

    # TTS 参数
    if args.tts_text:
        cmd.extend(["--tts-text", args.tts_text])
    if args.tts_instruct:
        cmd.extend(["--tts-instruct", args.tts_instruct])
    if args.tts_language:
        cmd.extend(["--tts-language", args.tts_language])

    print(f"[run] {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def _find_comfyui_input() -> Path | None:
    """找 ComfyUI input 目录（启发式）。"""
    # 读 .env 找 COMFYUI_INSTALL_DIR
    candidates = []
    env_path = DEFAULT_CWD / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("COMFYUI_INSTALL_DIR="):
                v = line.split("=", 1)[1].strip().strip('"')
                if v:
                    candidates.append(Path(v) / "input")
    # 常见路径
    candidates.extend([
        Path("D:/workspace/AIGC/StabilityMatrix/Packages/ComfyUI_Video/input"),
        Path("D:/ComfyUI/input"),
        Path("C:/ComfyUI/input"),
    ])
    for d in candidates:
        if d.is_dir():
            return d
    return None


def main() -> int:
    p = argparse.ArgumentParser(description="ComfyUI 懒人功能菜单")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="列出所有功能")

    s = sub.add_parser("run", help="执行指定功能")
    s.add_argument("func", help="功能名（菜单里的 key）")
    s.add_argument("-i", "--image", help="输入图片路径（自动复制到 ComfyUI input 目录）")
    s.add_argument("--out", help="输出目录，默认 ./out/<功能名>")
    s.add_argument("--prefix", help="输出前缀，默认功能名")
    # 音频参数
    s.add_argument("--audio-duration", type=float, help="音频时长（秒）")
    s.add_argument("--audio-category", choices=["Music", "Instrument", "SFX", "One-shot"], help="音频类别")
    s.add_argument("--audio-description", help="音乐/音效文字描述（英文）")
    s.add_argument("--generate-prompt", choices=["yes", "no"], help="是否 LLM 扩展提示词")
    # TTS 参数
    s.add_argument("--tts-text", help="要朗读的文本")
    s.add_argument("--tts-instruct", help="声音设计指令")
    s.add_argument("--tts-language", choices=["Chinese", "English", "Japanese", "Korean"], help="语言")

    args = p.parse_args()
    if args.cmd == "list":
        return cmd_list(args)
    if args.cmd == "run":
        return cmd_run(args)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[中断]", file=sys.stderr)
        sys.exit(130)
