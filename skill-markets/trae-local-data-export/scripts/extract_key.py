#!/usr/bin/env python3
"""
extract_key.py — Stage 1 of trae-local-data-export

Scan the ai-agent process memory on Windows for the SQLCipher 4 raw 32-byte
encryption key (64-char hex). Verify each candidate against the database's
HMAC-SHA512 signature on page 1. On match, write output/decrypted_key.json.

Algorithm derived from ZedeX/trae-chat-decrypt (MIT).
Windows only. Run as Administrator.
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import hashlib
import hmac
import json
import os
import re
import struct
import sys
from pathlib import Path

PAGE_SZ = 4096
SALT_SZ = 16
IV_SZ = 16
HMAC_SZ = 64
RESERVE_SZ = IV_SZ + HMAC_SZ
HEX64 = re.compile(rb"[0-9a-f]{64}")

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
MEM_COMMIT = 0x1000
PAGE_READABLE = 0x02 | 0x04 | 0x20 | 0x40 | 0x80 | 0x100 | 0x200 | 0x400

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


def is_windows():
    return sys.platform == "win32"


def find_ai_agent_pid():
    """Find ai-agent.exe process id by name."""
    import subprocess
    out = subprocess.check_output(
        ["tasklist", "/FO", "CSV", "/NH"], text=True, encoding="utf-8", errors="ignore"
    )
    for line in out.splitlines():
        parts = line.strip().strip('"').split('","')
        if len(parts) >= 2 and parts[0].lower() == "ai-agent.exe":
            return int(parts[1])
    return None


def verify_key(enc_key: bytes, db_page1: bytes) -> bool:
    """HMAC-SHA512 verification per SQLCipher 4 page 1 spec."""
    if len(db_page1) != PAGE_SZ:
        return False
    salt = db_page1[:SALT_SZ]
    mac_salt = bytes(b ^ 0x3A for b in salt)
    mac_key = hashlib.pbkdf2_hmac("sha512", enc_key, mac_salt, 2, dklen=32)
    hmac_data = db_page1[SALT_SZ : PAGE_SZ - RESERVE_SZ + SALT_SZ]
    stored_hmac = db_page1[PAGE_SZ - 64 :]
    hm = hmac.new(mac_key, hmac_data, hashlib.sha512)
    hm.update(struct.pack("<I", 1))
    return hm.digest() == stored_hmac


def scan_process_memory(pid: int):
    """Walk readable committed pages; yield 64-char hex candidates."""
    PROCESS_VM_READ |= 0
    hProcess = kernel32.OpenProcess(
        PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid
    )
    if not hProcess:
        raise PermissionError(
            f"OpenProcess({pid}) failed (err={ctypes.get_last_error()}). "
            "Re-run PowerShell as Administrator."
        )

    class MEMORY_BASIC_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BaseAddress", ctypes.c_void_p),
            ("AllocationBase", ctypes.c_void_p),
            ("AllocationProtect", wt.DWORD),
            ("RegionSize", ctypes.c_size_t),
            ("State", wt.DWORD),
            ("Protect", wt.DWORD),
            ("Type", wt.DWORD),
        ]

    mbi = MEMORY_BASIC_INFORMATION()
    address = 0
    seen_addrs = set()
    while address < 0x7FFFFFFFFFFFFFFF:
        if not kernel32.VirtualQueryEx(
            hProcess, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)
        ):
            break
        next_addr = address + mbi.RegionSize
        if (
            mbi.State == MEM_COMMIT
            and (mbi.Protect & PAGE_READABLE)
            and mbi.RegionSize not in seen_addrs
        ):
            seen_addrs.add(mbi.RegionSize)
            buf = (ctypes.c_ubyte * mbi.RegionSize)()
            bytes_read = ctypes.c_size_t(0)
            if kernel32.ReadProcessMemory(
                hProcess,
                ctypes.c_void_p(mbi.BaseAddress),
                buf,
                mbi.RegionSize,
                ctypes.byref(bytes_read),
            ):
                data = bytes(buf[: bytes_read.value])
                for m in HEX64.finditer(data):
                    yield m.group(0).decode("ascii"), mbi.BaseAddress + m.start()
        address = next_addr
    kernel32.CloseHandle(hProcess)


def main():
    ap = argparse.ArgumentParser(description="Stage 1: extract SQLCipher key from ai-agent memory")
    ap.add_argument("--db", required=True, help="Path to ModularData/ai-agent/database.db")
    ap.add_argument("--out", default="output", help="Output directory")
    ap.add_argument("--max-candidates", type=int, default=2000,
                    help="Stop after N candidates (perf safety)")
    args = ap.parse_args()

    if not is_windows():
        sys.exit("STUB: extract_key.py requires Windows (uses Win32 API). "
                 "On macOS/Linux, run decrypt_key on Windows first.")

    db_path = Path(args.db)
    if not db_path.exists():
        sys.exit(f"ERROR: database not found: {db_path}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    pid = find_ai_agent_pid()
    if pid is None:
        sys.exit("STUB: ai-agent.exe process not found. Start Trae and keep an AI chat window active.")
    print(f"[+] Found ai-agent.exe PID={pid}")

    with open(db_path, "rb") as f:
        page1 = f.read(PAGE_SZ)
    if len(page1) < PAGE_SZ:
        sys.exit("ERROR: database file too small (< 4KB)")
    print(f"[+] Read page 1 ({len(page1)} bytes), salt={page1[:SALT_SZ].hex()}")

    seen_hex = set()
    candidate_count = 0
    for hex_key, addr in scan_process_memory(pid):
        if hex_key in seen_hex:
            continue
        seen_hex.add(hex_key)
        candidate_count += 1
        if candidate_count > args.max_candidates:
            print(f"[!] Hit {args.max_candidates} candidates without match, aborting")
            break
        enc_key = bytes.fromhex(hex_key)
        if verify_key(enc_key, page1):
            print(f"[OK] Verified key at 0x{addr:x}: {hex_key[:8]}...{hex_key[-8:]}")
            key_json = {
                "db_path": str(db_path.resolve()),
                "salt": page1[:SALT_SZ].hex(),
                "enc_key": hex_key,
                "address": f"0x{addr:x}",
            }
            key_path = out_dir / "decrypted_key.json"
            key_path.write_text(json.dumps(key_json, indent=2), encoding="utf-8")
            print(f"[+] Wrote {key_path}")
            return 0

    sys.exit("STUB: no valid key found in process memory. "
             "Try scripts/extract_key_frida.py for the Frida fallback path.")


if __name__ == "__main__":
    sys.exit(main())
