#!/usr/bin/env python3
"""install-v10.py — 一键升级 fullstack4TraeV10 到 10.2.0

用法（在 my-trae-helper 目录执行）：
    python install-v10.py
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE = Path(r"D:\workspace\my-trae-helper\skill-markets\fullstack4TraeV10")
TARGET = Path(os.path.expanduser(r"~\.trae-cn\skills\fullstack4TraeV10"))


def banner(msg: str) -> None:
    print("=" * 60)
    print(msg)
    print("=" * 60)


def step(n: int, total: int, msg: str) -> None:
    print(f"\n[{n}/{total}] {msg}")


def main() -> int:
    banner("Fullstack4TraeV10 10.2.0 升级安装")
    print(f"源:   {SOURCE}")
    print(f"目标: {TARGET}")

    # 1. 验证源
    if not (SOURCE / "SKILL.md").exists():
        print(f"[FAIL] 源路径不存在: {SOURCE / 'SKILL.md'}")
        return 1
    print(f"[OK]   源验证通过")

    # 2. 覆盖安装（不备份，避免 skills/ 下残留多版本技能造成污染）
    if TARGET.exists():
        print(f"[1/4] 删除旧版本: {TARGET.name}")
        shutil.rmtree(TARGET)
    else:
        print(f"[1/4] 无旧版本")

    # 3. 复制新版本
    print(f"[2/4] 复制 10.2.0 → {TARGET}")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, TARGET, dirs_exist_ok=False)

    # 4. 验证
    print(f"[3/4] 验证安装...")

    skill = TARGET / "SKILL.md"
    version_line = next(
        (l for l in skill.read_text(encoding="utf-8").splitlines() if l.startswith("version:")), ""
    )
    print(f"  SKILL.md:           {version_line.strip()}")

    scripts = list((TARGET / "scripts").glob("*.py"))
    print(f"  scripts/*.py:       {len(scripts)} 个")

    has_audit = (TARGET / "scripts" / "acceptance-audit.py").exists()
    print(f"  acceptance-audit.py: {'OK' if has_audit else 'MISSING'}")

    agents = list((TARGET / "agents").glob("*.md"))
    print(f"  agents/*.md:        {len(agents)} 个")

    refs = list((TARGET / "references").glob("*.md"))
    print(f"  references/*.md:    {len(refs)} 个")

    hooks = list((TARGET / "templates" / "hooks").glob("*.py"))
    print(f"  templates/hooks/*.py: {len(hooks)} 个")

    # 5. 检查 acceptance-precheck 帮助注册
    print(f"\n[4/4] 验证 acceptance-precheck 注册:")
    r = subprocess.run(
        [sys.executable, str(TARGET / "scripts" / "check_prerequisites.py"), "--help"],
        capture_output=True, text=True, timeout=10,
    )
    if "acceptance-precheck" in (r.stdout + r.stderr):
        print(f"  acceptance-precheck: 已注册")
    else:
        print(f"  acceptance-precheck: 未注册（FAIL）")
        return 2

    banner("安装完成。请重启 Trae IDE 使新版本生效。")
    print()
    print("验证命令（重启后执行）:")
    print(f"  python {TARGET / 'scripts' / 'acceptance-audit.py'} --help")
    print(f"  python {TARGET / 'scripts' / 'check_prerequisites.py'} --phase acceptance-precheck --feature 00-01-foundation --project-root D:\\workspace\\ai-dev\\AIGCMediaDesktop --json")

    return 0


if __name__ == "__main__":
    sys.exit(main())