#!/usr/bin/env python3
"""
verify_decrypted_db.py — Stage 2.5 sanity check

Open output/database_decrypted.db, run PRAGMA integrity_check, list all
tables + row counts, write output/table_summary.json.
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Verify decrypted SQLite database")
    ap.add_argument("--db", default="output/database_decrypted.db")
    ap.add_argument("--out", default="output")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        sys.exit(f"STUB: {db_path} not found. Run decrypt_db.py first.")

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = conn.cursor()

    try:
        integrity = cur.execute("PRAGMA integrity_check").fetchone()[0]
    except Exception as e:
        sys.exit(f"STUB: integrity_check failed: {e}")

    if integrity != "ok":
        sys.exit(f"STUB: integrity_check returned: {integrity}")
    print(f"[+] PRAGMA integrity_check = ok")

    tables = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    summary = {}
    print(f"[+] {len(tables)} tables:")
    for (name,) in tables:
        try:
            cols = [r[1] for r in cur.execute(f"PRAGMA table_info({name})").fetchall()]
            count = cur.execute(f"SELECT COUNT(*) FROM \"{name}\"").fetchone()[0]
            summary[name] = {"columns": cols, "rows": count}
            print(f"  {name:40s}  rows={count:>8}  cols={len(cols)}")
        except Exception as e:
            summary[name] = {"error": str(e)}
            print(f"  {name:40s}  ERROR: {e}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "table_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[+] Wrote {out_dir / 'table_summary.json'}")

    # dump schema
    schema_path = out_dir / "chat_export"
    schema_path.mkdir(parents=True, exist_ok=True)
    with open(schema_path / "schema.sql", "w", encoding="utf-8") as f:
        for row in cur.execute(
            "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type, name"
        ).fetchall():
            f.write(row[0] + ";\n\n")
    print(f"[+] Wrote {schema_path / 'schema.sql'}")


if __name__ == "__main__":
    sys.exit(main())
