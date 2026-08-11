#!/usr/bin/env python3
"""
extract_key_frida.py — Stage 1 fallback via Frida dynamic instrumentation

Used when scripts/extract_key.py finds no candidates in process memory
(e.g. statically linked sqlcipher). Hooks sqlite3_key_v2 / sqlite3_key
to capture the raw key passed in by the application.

Requires: pip install frida frida-tools
Algorithm: ZedeX/trae-chat-decrypt _frida_hook5.py (MIT).
"""
import argparse
import json
import sys
import time
from pathlib import Path

JS_HOOK = r"""
'use strict';

const SQLITE_KEY_FUNC = ['sqlite3_key_v2', 'sqlite3_key', 'sqlite3_rekey'];

function findModule(name) {
    const m = Process.findModuleByName(name);
    if (m) return m;
    return null;
}

const seen = new Set();
const candidates = [];

function tryAdd(hex) {
    if (!/^[0-9a-f]{64}$/.test(hex)) return;
    if (seen.has(hex)) return;
    seen.add(hex);
    candidates.push(hex);
    send({type: 'candidate', hex: hex});
}

function attachAll() {
    const mod = findModule('ai_agent.dll') || findModule('sqlcipher.dll');
    if (mod) {
        for (const fname of SQLITE_KEY_FUNC) {
            const f = mod.findExportByName(fname);
            if (f) {
                Interceptor.attach(f, {
                    onEnter(args) {
                        try {
                            const p = args[1];
                            if (p.isNull()) return;
                            const len = args[2].toInt32();
                            const buf = p.readByteArray(len);
                            if (!buf) return;
                            const hex = Array.from(new Uint8Array(buf))
                                .map(b => b.toString(16).padStart(2, '0')).join('');
                            tryAdd(hex);
                        } catch (e) {}
                    }
                });
                send({type: 'hook', func: fname, addr: f.toString()});
            }
        }
    } else {
        send({type: 'warn', msg: 'ai_agent.dll / sqlcipher.dll not in this process'});
    }
}

attachAll();
rpc.exports = {
    getCandidates: () => candidates.slice()
};
"""


def main():
    ap = argparse.ArgumentParser(description="Stage 1 fallback: Frida-based key extraction")
    ap.add_argument("--db", required=True, help="Path to database.db (for HMAC verify)")
    ap.add_argument("--out", default="output")
    ap.add_argument("--timeout", type=int, default=60, help="Seconds to keep Frida attached")
    args = ap.parse_args()

    try:
        import frida
    except ImportError:
        sys.exit("STUB: install frida first: pip install frida frida-tools")

    import subprocess
    out = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True, encoding="utf-8", errors="ignore")
    pid = None
    for line in out.splitlines():
        parts = line.strip().strip('"').split('","')
        if len(parts) >= 2 and parts[0].lower() == "ai-agent.exe":
            pid = int(parts[1])
            break
    if pid is None:
        sys.exit("STUB: ai-agent.exe not found. Start Trae first.")

    print(f"[+] Attaching Frida to ai-agent.exe PID={pid}")
    session = frida.attach(pid)
    script = session.create_script(JS_HOOK)
    candidates = []
    script.on("message", lambda m, _: candidates.append(m) if m.get("type") == "candidate" else None)
    script.load()
    print(f"[+] Listening for {args.timeout}s — interact with Trae to trigger PRAGMA key...")
    time.sleep(args.timeout)
    script.unload()
    session.detach()

    hex_candidates = [m["hex"] for m in candidates]
    print(f"[+] Collected {len(hex_candidates)} unique candidates")

    # verify against db page 1
    import hashlib, hmac, struct
    with open(args.db, "rb") as f:
        page1 = f.read(4096)
    salt = page1[:16]
    mac_salt = bytes(b ^ 0x3A for b in salt)

    for hex_key in hex_candidates:
        enc_key = bytes.fromhex(hex_key)
        mac_key = hashlib.pbkdf2_hmac("sha512", enc_key, mac_salt, 2, dklen=32)
        hmac_data = page1[16: 4096 - 80 + 16]
        stored_hmac = page1[4096 - 64:]
        hm = hmac.new(mac_key, hmac_data, hashlib.sha512)
        hm.update(struct.pack("<I", 1))
        if hm.digest() == stored_hmac:
            print(f"[OK] Frida hook captured valid key: {hex_key[:8]}...{hex_key[-8:]}")
            out_dir = Path(args.out)
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "decrypted_key.json").write_text(
                json.dumps(
                    {"db_path": str(Path(args.db).resolve()),
                     "salt": salt.hex(),
                     "enc_key": hex_key,
                     "source": "frida"},
                    indent=2,
                ),
                encoding="utf-8",
            )
            return 0
    sys.exit("STUB: no valid key in Frida hooks. Database may have changed KDF.")


if __name__ == "__main__":
    sys.exit(main())
