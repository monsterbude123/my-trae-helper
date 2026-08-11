#!/usr/bin/env python3
"""
sanitize_export.py — Stage 4 PII sanitization

Default-on: deep sanitize all JSON / TXT outputs from stage 3.
Replaces absolute paths, emails, 32+ and 64-char hex, and IPv4
with placeholders, mirroring trae-chat-decrypt's default sanitization.
"""
import argparse
import json
import re
import sys
from pathlib import Path

PATTERNS = [
    (re.compile(r"[A-Za-z]:\\[^\s\"']+"), "<WINDOWS_PATH>"),
    (re.compile(r"/(?:Users|home|root|var|tmp|etc|opt)/[^\s\"']+"), "<UNIX_PATH>"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "<EMAIL>"),
    (re.compile(r"\b[0-9a-fA-F]{64}\b"), "<HEX_64>"),
    (re.compile(r"\b[0-9a-fA-F]{32}\b"), "<HEX_32>"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "<IP>"),
]


def sanitize(text: str) -> str:
    for pat, repl in PATTERNS:
        text = pat.sub(repl, text)
    return text


def sanitize_json(obj):
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_json(v) for v in obj]
    if isinstance(obj, str):
        return sanitize(obj)
    return obj


def main():
    ap = argparse.ArgumentParser(description="PII sanitize stage-3 outputs")
    ap.add_argument("--in", dest="src", default="output/chat_export",
                    help="Input dir from stage 3")
    ap.add_argument("--out", default="output/chat_export/sanitized")
    args = ap.parse_args()

    src = Path(args.src)
    dst = Path(args.out)
    if not src.exists():
        sys.exit(f"STUB: {src} not found. Run export_sessions.py first.")
    dst.mkdir(parents=True, exist_ok=True)

    # sessions.json
    if (src / "sessions.json").exists():
        idx = json.loads((src / "sessions.json").read_text(encoding="utf-8"))
        (dst / "sessions.json").write_text(
            json.dumps(sanitize_json(idx), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"[+] sanitized sessions.json")

    # sessions/*.json
    sessions_dir = src / "sessions"
    if sessions_dir.is_dir():
        (dst / "sessions").mkdir(exist_ok=True)
        for f in sessions_dir.glob("*.json"):
            doc = json.loads(f.read_text(encoding="utf-8"))
            (dst / "sessions" / f.name).write_text(
                json.dumps(sanitize_json(doc), indent=2, ensure_ascii=False), encoding="utf-8"
            )
        print(f"[+] sanitized {len(list((dst / 'sessions').glob('*.json')))} session JSONs")

    # all_chats.txt
    if (src / "all_chats.txt").exists():
        raw = (src / "all_chats.txt").read_text(encoding="utf-8")
        (dst / "all_chats.txt").write_text(sanitize(raw), encoding="utf-8")
        print(f"[+] sanitized all_chats.txt")
    print(f"[+] Done → {dst}")


if __name__ == "__main__":
    sys.exit(main())
