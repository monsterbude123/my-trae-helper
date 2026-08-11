#!/usr/bin/env python3
"""
export_sessions.py — Stage 3 of trae-local-data-export

Read output/database_decrypted.db, emit the three deliverables:

  1. output/chat_export/sessions/NNN_标题_ID.json  (structured per-session JSON)
  2. output/chat_export/all_chats.txt              (merged human-readable TXT)
  3. output/database_decrypted.db                  (already produced by stage 2)

Schema is tolerant to column-name drift across Trae versions
(uses PRAGMA table_info to discover columns at runtime).
"""
import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def iso(ms: int) -> str:
    if not ms or ms <= 0:
        return ""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def col(cur, table):
    return {r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()}


def safe_text(val, max_len=8000):
    if val is None:
        return ""
    s = str(val)
    return s if len(s) <= max_len else s[:max_len] + "..."


def main():
    ap = argparse.ArgumentParser(description="Stage 3: export sessions as JSON + TXT")
    ap.add_argument("--db", default="output/database_decrypted.db")
    ap.add_argument("--out", default="output/chat_export")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        sys.exit(f"STUB: {db_path} not found. Run decrypt_db.py first.")

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = conn.cursor()

    msg_cols = col(cur, "chat_message")
    # idx / index column may have been renamed across versions
    idx_col = "idx" if "idx" in msg_cols else ("index" if "index" in msg_cols else "id")
    has_general = "chat_message_general" in {r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    has_task = "chat_message_task" in {r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}

    sessions = cur.execute(
        "SELECT id, title, type, project_id, created_at, updated_at "
        "FROM chat_session ORDER BY created_at"
    ).fetchall()
    project_map = dict(cur.execute("SELECT id, name FROM project").fetchall())

    # group messages by session
    messages = defaultdict(list)
    for sid, role, mtype, msg_id, idx in cur.execute(
        f"SELECT session_id, role, type, id, {idx_col} FROM chat_message"
    ):
        content = ""
        if mtype == "general" and has_general:
            row = cur.execute(
                "SELECT content FROM chat_message_general WHERE id = ?", (msg_id,)
            ).fetchone()
            content = safe_text(row[0] if row else "")
        elif mtype == "task" and has_task:
            row = cur.execute(
                "SELECT content, summary FROM chat_message_task WHERE id = ?", (msg_id,)
            ).fetchone()
            content = safe_text((row[1] or "") if row else "")
            if not content and row and row[0]:
                content = safe_text(row[0])
        messages[sid].append({"role": role, "type": mtype, "content": content, "idx": idx})

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    sessions_dir = out_dir / "sessions"
    sessions_dir.mkdir(exist_ok=True)
    merged_path = out_dir / "all_chats.txt"
    sessions_index = []

    print(f"[+] {len(sessions)} sessions, exporting...")
    with open(merged_path, "w", encoding="utf-8") as merged:
        for n, (sid, title, stype, pid, cts, uts) in enumerate(sessions, 1):
            msgs = sorted(messages.get(sid, []), key=lambda m: m.get("idx", 0))
            project = project_map.get(pid, "")
            session_doc = {
                "session_id": sid,
                "title": title or "(untitled)",
                "type": stype,
                "project": project,
                "created_at": iso(cts),
                "updated_at": iso(uts),
                "messages": [
                    {"role": m["role"], "content": m["content"]} for m in msgs
                ],
            }
            safe_title = (title or "untitled").replace("/", "_").replace("\\", "_")[:60]
            fname = f"{n:03d}_{safe_title}_{sid[:8]}.json"
            (sessions_dir / fname).write_text(
                json.dumps(session_doc, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            sessions_index.append(
                {
                    "id": sid,
                    "title": title,
                    "type": stype,
                    "project": project,
                    "created_at": session_doc["created_at"],
                    "message_count": len(msgs),
                    "file": f"sessions/{fname}",
                }
            )

            merged.write(f"\n{'=' * 70}\n")
            merged.write(f"Session #{n}  {title or '(untitled)'}\n")
            merged.write(f"ID: {sid}    Type: {stype}    Project: {project}\n")
            merged.write(f"Created: {session_doc['created_at']}\n")
            merged.write(f"{'=' * 70}\n\n")
            for m in msgs:
                role = m["role"].upper()
                merged.write(f"[{role}]\n{m['content']}\n\n")

    (out_dir / "sessions.json").write_text(
        json.dumps(sessions_index, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[+] Wrote {len(sessions)} session JSONs to {sessions_dir}/")
    print(f"[+] Wrote merged TXT: {merged_path} ({merged_path.stat().st_size} bytes)")
    print(f"[+] Wrote index: {out_dir / 'sessions.json'}")


if __name__ == "__main__":
    sys.exit(main())
