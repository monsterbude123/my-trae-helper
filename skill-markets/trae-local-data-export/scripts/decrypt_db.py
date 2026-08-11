#!/usr/bin/env python3
"""
decrypt_db.py — Stage 2 of trae-local-data-export

Read output/decrypted_key.json + encrypted database.db, page-decrypt the
SQLCipher 4 database using AES-256-CBC + PBKDF2-HMAC-SHA512 derived keys.
Write output/database_decrypted.db (openable in any SQLite 3 client).

Algorithm: ZedeX/trae-chat-decrypt decrypt logic (MIT).
"""
import argparse
import json
import os
import sys
from pathlib import Path

PAGE_SZ = 4096
SALT_SZ = 16
IV_SZ = 16
HMAC_SZ = 64
RESERVE_SZ = IV_SZ + HMAC_SZ


def decrypt_page(enc_key: bytes, page_data: bytes, pgno: int) -> bytes:
    """Per-page AES-256-CBC decryption. Page 1 rebuilds SQLite header."""
    from Crypto.Cipher import AES
    iv = page_data[PAGE_SZ - RESERVE_SZ : PAGE_SZ - RESERVE_SZ + IV_SZ]
    if pgno == 1:
        encrypted = page_data[SALT_SZ : PAGE_SZ - RESERVE_SZ]
        cipher = AES.new(enc_key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted)
        return b"SQLite format 3\x00" + decrypted + b"\x00" * RESERVE_SZ
    else:
        encrypted = page_data[: PAGE_SZ - RESERVE_SZ]
        cipher = AES.new(enc_key, AES.MODE_CBC, iv)
        return cipher.decrypt(encrypted) + b"\x00" * RESERVE_SZ


def main():
    ap = argparse.ArgumentParser(description="Stage 2: decrypt SQLCipher 4 database")
    ap.add_argument("--key", default="output/decrypted_key.json",
                    help="Path to decrypted_key.json from stage 1")
    ap.add_argument("--out", default="output")
    ap.add_argument("--page-batch", type=int, default=500,
                    help="Pages per batch (lower = less memory)")
    args = ap.parse_args()

    try:
        from Crypto.Cipher import AES  # noqa: F401
    except ImportError:
        sys.exit("STUB: install pycryptodome: pip install pycryptodome")

    key_path = Path(args.key)
    if not key_path.exists():
        sys.exit(f"STUB: missing {key_path}. Run extract_key.py first.")
    key_data = json.loads(key_path.read_text(encoding="utf-8"))
    db_path = Path(key_data["db_path"])
    enc_key = bytes.fromhex(key_data["enc_key"])
    if not db_path.exists():
        sys.exit(f"STUB: database not found: {db_path}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "database_decrypted.db"

    total = db_path.stat().st_size
    pages = total // PAGE_SZ
    print(f"[+] Decrypting {total} bytes ({pages} pages) → {out_path}")

    written = 0
    with open(db_path, "rb") as fin, open(out_path, "wb") as fout:
        for pgno in range(1, pages + 1):
            page = fin.read(PAGE_SZ)
            if len(page) < PAGE_SZ:
                break
            fout.write(decrypt_page(enc_key, page, pgno))
            written += 1
            if written % args.page_batch == 0:
                pct = written / pages * 100
                print(f"  [{pct:5.1f}%] page {written}/{pages}")

    print(f"[+] Wrote {out_path} ({out_path.stat().st_size} bytes)")
    print(f"[+] Next: run scripts/verify_decrypted_db.py")


if __name__ == "__main__":
    sys.exit(main())
