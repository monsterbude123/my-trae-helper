#!/usr/bin/env python3
"""
V11 gate-integrity-guard.py — 贾维斯时机② hash 锁(机械防线)

原理: 安装时把所有 gate 相关文件的 sha256 写入 gates/gate.lock.yaml;
      每次跑 gate 前 --verify 校验;任何未委派贾维斯的改动 → hash 不匹配 → BLOCK。
      这是防"agent 改标准通过自己"的最终兜底(文档约束是软的,hash 锁是硬的)。

仅贾维斯 sub-agent 可执行 --generate(重签);--verify 任何 agent/hook 都可跑。

Usage:
    python gate-integrity-guard.py --generate [--root <项目根>]   # 贾维斯:生成/重签锁
    python gate-integrity-guard.py --verify  [--root <项目根>]   # 任何人:校验(不匹配=exit 1)

锁定范围(--generate 时扫描):
    gates/gate-config.json
    .husky/pre-commit .husky/pre-push
    (V11 包侧) registry/gates.yaml registry/guards.yaml

Exit codes:
    0 = PASS(锁存在且全部匹配)
    1 = BLOCK(锁缺失 / 文件缺失 / hash 不匹配)
"""
import sys
import hashlib
import argparse
import pathlib
from datetime import datetime, timezone

# 锁定文件清单(相对 --root;不存在则跳过并记录)
LOCKED_FILES = [
    "gates/gate-config.json",
    ".husky/pre-commit",
    ".husky/pre-push",
]
V11_LOCKED = [
    "registry/gates.yaml",
    "registry/guards.yaml",
]


def sha256_of(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_files(root: pathlib.Path, v11_root: pathlib.Path) -> list:
    """返回 [(相对标识, 绝对路径)] — 目标项目文件 + V11 包侧注册表。"""
    items = [(rel, root / rel) for rel in LOCKED_FILES]
    items += [(f"v11::{rel}", v11_root / rel) for rel in V11_LOCKED]
    return items


def generate(root: pathlib.Path, v11_root: pathlib.Path, force: bool = False, reason: str = "") -> int:
    """生成/重签锁。仅贾维斯委派场景调用。

    防未授权前提漏洞(V11.7.0 P0 自检发现):
      若当前锁与实际 hash 不一致(说明发生过未经授权改动),
      直接 --generate 会把篡改状态固化成基线 → 必须先 --force 并提供 --reason(会话审计)。
      默认严格模式:未授权前提 = BLOCK。
    """
    lock_path = root / "gates" / "gate.lock.yaml"
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    # 前置门禁:已有锁且 verify 不一致 → 拒绝非强制重签
    if lock_path.exists() and not force:
        rc = verify(root, v11_root)
        if rc != 0:
            print("🛑 [JARVIS-GENERATE] 拒绝:当前锁与文件 hash 不一致", file=sys.stderr)
            print("   说明:本次会话已有 gate 文件发生未经 --generate 重签的改动", file=sys.stderr)
            print("   防漏洞:若继续默认 --generate,篡改状态会被固化成新基线(V11.7.0 P0 自检发现)", file=sys.stderr)
            print("   处置:", file=sys.stderr)
            print("     ① diff gate-config.json/.husky/* 找改动", file=sys.stderr)
            print("     ② 确属正当变更 → 加 --force --reason '<[JARVIS-DELEGATION] 委派编号>'", file=sys.stderr)
            print("     ③ 确属篡改 → 恢复文件后普通 --generate", file=sys.stderr)
            return 1

    lines = [
        "# V11 gate.lock — 贾维斯 hash 锁(机械防线)",
        "# 重签必经 [JARVIS-DELEGATION] 委派;直改本文件 = 下次 --verify BLOCK",
        f"generated_at: {datetime.now(timezone.utc).isoformat()}",
    ]
    if force:
        lines.append(f"# forced: true(检测到未授权前提,会话审计 reason: {reason or '未提供'})")
    lines.append("files:")
    count = 0
    for rel, path in collect_files(root, v11_root):
        if not path.exists():
            lines.append(f"  # SKIPPED(不存在): {rel}")
            continue
        lines.append(f"  {rel}:")
        lines.append(f"    sha256: {sha256_of(path)}")
        count += 1

    lock_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if force:
        print(f"[JARVIS-LOCK] ⚠ 强制重签(审计): {lock_path}({count} 个文件)")
        print(f"           reason={reason!r}  ← 应附 [JARVIS-DELEGATION] 委派编号")
    else:
        print(f"[JARVIS-LOCK] ✅ 锁已生成: {lock_path}({count} 个文件)")
    return 0


def verify(root: pathlib.Path, v11_root: pathlib.Path) -> int:
    lock_path = root / "gates" / "gate.lock.yaml"
    if not lock_path.exists():
        print("🛑 [JARVIS-VERIFY] gate.lock.yaml 不存在 — 请委派贾维斯跑 gate-installer + --generate", file=sys.stderr)
        return 1

    locked = {}
    current_rel = None
    for line in lock_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        if stripped.startswith("files:"):
            continue
        if stripped.startswith("v11::") or (":" in stripped and not stripped.startswith("sha256:")):
            indent = len(line) - len(line.lstrip())
            if indent == 2:  # 文件条目
                current_rel = stripped.rstrip(":")
                locked[current_rel] = None
        elif stripped.startswith("sha256:") and current_rel:
            locked[current_rel] = stripped.split(":", 1)[1].strip()

    violations = []
    checked = 0
    for rel, expected in locked.items():
        path = v11_root / rel[len("v11::"):] if rel.startswith("v11::") else root / rel
        if not path.exists():
            violations.append(f"文件缺失: {rel}")
            continue
        actual = sha256_of(path)
        checked += 1
        if actual != expected:
            violations.append(f"hash 不匹配: {rel}(被未授权改动!期望 {expected[:12]}… 实际 {actual[:12]}…)")

    if not locked:
        print("🛑 [JARVIS-VERIFY] lock 文件无有效条目", file=sys.stderr)
        return 1

    if violations:
        print(f"🛑 [JARVIS-VERIFY] BLOCK — {len(violations)} 处违规:", file=sys.stderr)
        for v in violations:
            print(f"  ❌ {v}", file=sys.stderr)
        print("处置: ① diff 上述文件找改动 ② 若正当变更 → 委派贾维斯重签(--generate) ③ 若篡改 → 恢复文件后 --verify", file=sys.stderr)
        return 1

    print(f"[JARVIS-VERIFY] ✅ PASS — {checked} 个 gate 文件 hash 全部匹配")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="V11 贾维斯 hash 锁")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--generate", action="store_true", help="生成/重签锁(仅贾维斯)")
    group.add_argument("--verify", action="store_true", help="校验锁(hook 前置调用)")
    ap.add_argument("--root", type=pathlib.Path, default=None, help="目标项目根(默认 cwd)")
    ap.add_argument("--force", action="store_true", help="V11.7.0 NEW: 强制重签(检测到未授权前提时,需附 --reason)")
    ap.add_argument("--reason", default="", help="V11.7.0 NEW: 强制重签的会话审计原因(应附 [JARVIS-DELEGATION] 委派编号)")
    args = ap.parse_args()

    root = args.root.resolve() if args.root else pathlib.Path.cwd()
    v11_root = pathlib.Path(__file__).resolve().parent.parent

    if args.generate:
        return generate(root, v11_root, force=args.force, reason=args.reason)
    return verify(root, v11_root)


if __name__ == "__main__":
    sys.exit(main())
