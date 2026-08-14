#!/usr/bin/env python3
"""
skills-security-scan/main.py — DEPRECATED 兼容壳（2026-08-14 归档）

扫描能力已迁移至 trae-security-review/scripts/scan_skills_dir.py V2.1
（8 类风险 + 三层白名单 + 平台识别 + 词边界，比原 5 类更强）。

用法保持兼容：
  python main.py <skills_dir> [output_dir]

新用法：
  python ../trae-security-review/scripts/scan_skills_dir.py <skills_dir> [output_dir]
"""

import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <skills_dir> [output_dir]")
        print("DEPRECATED: 请改用 trae-security-review/scripts/scan_skills_dir.py")
        sys.exit(1)

    target = Path(sys.argv[1]).resolve()
    if not target.exists():
        print(f"Error: skills_dir not found: {target}", file=sys.stderr)
        sys.exit(1)

    # 委托给 trae-security-review
    new_cli = Path(__file__).parent.parent / "trae-security-review" / "scripts" / "scan_skills_dir.py"
    if not new_cli.exists():
        print(f"Error: redirect target missing: {new_cli}", file=sys.stderr)
        sys.exit(2)

    # 透传参数
    args = [sys.executable, str(new_cli), str(target)]
    if len(sys.argv) > 2:
        args.append(sys.argv[2])

    print(f"[DEPRECATED redirect] {sys.argv[0]} → {new_cli.name}", file=sys.stderr)
    sys.exit(__import__("subprocess").call(args))


if __name__ == "__main__":
    main()