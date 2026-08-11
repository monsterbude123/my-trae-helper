#!/usr/bin/env python3
"""
extract_trae_jsonl.py — Cross-platform fallback for stage 3

When the database is already decrypted (or when running on macOS/Linux
where Win32 process memory is unavailable), scan a Trae installation
directory for both JSONL session files and SQLite databases, and emit
one JSONL file per the ai-data-extraction convention.

Algorithm: adapted from cgint/ai-data-extraction extract_trae.py (MIT).
Pure stdlib, no external dependencies.
"""
import argparse
import json
import os
import platform
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def find_trae_installations():
    home = Path.home()
    if platform.system() == "Darwin":
        bases = [home / "Library/Application Support", home / ".config", home]
    elif platform.system() == "Windows":
        appdata = os.environ.get("APPDATA", str(home / "AppData/Roaming"))
        bases = [Path(appdata), Path(os.environ.get("LOCALAPPDATA", str(home / "AppData/Local"))), home]
    else:
        bases = [home / ".config", home / ".local/share", home]
    found = []
    for base in bases:
        if not base.exists():
            continue
        for pattern in ["Trae CN", "Trae", "trae", ".trae"]:
            d = base / pattern
            if d.exists():
                found.append(d)
    return list({d.resolve() for d in found})


def extract_from_db(db_file: Path):
    out = []
    try:
        conn = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
        cur = conn.cursor()
        tables = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "chat_session" not in tables:
            conn.close()
            return out
        msg_cols = {r[1] for r in cur.execute("PRAGMA table_info(chat_message)")}
        idx_col = "idx" if "idx" in msg_cols else ("index" if "index" in msg_cols else "id")
        has_general = "chat_message_general" in tables
        sessions = cur.execute(
            "SELECT id, title, type, created_at FROM chat_session"
        ).fetchall()
        for sid, title, stype, cts in sessions:
            msgs = []
            for role, mtype, mid, idx in cur.execute(
                f"SELECT role, type, id, {idx_col} FROM chat_message WHERE session_id = ?", (sid,)
            ):
                content = ""
                if mtype == "general" and has_general:
                    r = cur.execute("SELECT content FROM chat_message_general WHERE id = ?", (mid,)).fetchone()
                    content = (r[0] if r else "") or ""
                out.append({
                    "source": "trae",
                    "name": title or "(untitled)",
                    "session_id": sid,
                    "type": stype,
                    "created_at": cts,
                    "messages": msgs,
                })
        conn.close()
    except Exception as e:
        print(f"[!] {db_file}: {e}")
    return out


def main():
    ap = argparse.ArgumentParser(description="Cross-platform Trae data extraction (already-decrypted or non-Windows)")
    ap.add_argument("--source", help="Explicit installation root (skip auto-discovery)")
    ap.add_argument("--out", default="output")
    args = ap.parse_args()

    if args.source:
        installations = [Path(args.source)]
    else:
        installations = find_trae_installations()
    if not installations:
        sys.exit("STUB: no Trae installations found. Pass --source <path>.")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"trae_conversations_{ts}.jsonl"

    total = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for inst in installations:
            print(f"[+] Scanning {inst}")
            for db_file in inst.rglob("*.db"):
                for conv in extract_from_db(db_file):
                    f.write(json.dumps(conv, ensure_ascii=False) + "\n")
                    total += 1
            for db_file in inst.rglob("*.vscdb"):
                for conv in extract_from_db(db_file):
                    f.write(json.dumps(conv, ensure_ascii=False) + "\n")
                    total += 1

    print(f"[+] Wrote {total} conversations → {out_path}")


if __name__ == "__main__":
    sys.exit(main())
