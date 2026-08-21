#!/usr/bin/env python3
"""
scripts/ai-testmate-guard.py — ai-testmate 项目侧薄壳守卫（2026-08-20 guard-smith 委派落地）

设计目的：
  ai-testmate 是独立专精测试工程师 Skill(8 references + 5 agents + 4 scripts),
  8 AP 反例库(AP-1~AP-8)由 skill 内置守卫负责。本文件仅作为项目侧薄壳入口,
  委托调用 skill-markets/ai-testmate/scripts/ai-testmate-guard.py。

  遵循 AGENTS.md §1.11 铁律 11 — 项目侧 guard 必带,但实现可委托 skill 子目录脚本。
  本薄壳 0 业务逻辑,纯转发,所有 8 AP 检测逻辑都在 skill 内置脚本。

用法:
  python scripts/ai-testmate-guard.py skill-markets/ai-testmate
  python scripts/ai-testmate-guard.py --test-pass

退出码:
  透传 skill 内置 guard 的 exit code
    0 = PASS
    1 = BLOCK（任意 AP 命中）
    2 = WARN
"""
import subprocess
import sys
import pathlib

# 项目根 = 本文件上一级
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
# skill 内置守卫绝对路径
_SKILL_GUARD = (
    _REPO_ROOT
    / "skill-markets"
    / "ai-testmate"
    / "scripts"
    / "ai-testmate-guard.py"
)


def main() -> int:
    """薄壳入口：过滤参数后透传到 skill 内置守卫。

    内置守卫 argparse 只接受 --xxx flag,位置参数(如 .husky gate 传入的
    'skill-markets/ai-testmate')会让 argparse 报 'unrecognized arguments'
    → exit 2 → L1 commit BLOCK。本薄壳过滤掉所有位置参数(以非 '-' 开头的实参)
    与 '--' 之后的所有实参,仅透传 flag 形式参数(以 '-' 开头)。
    """
    if not _SKILL_GUARD.exists():
        print(f"❌ ai-testmate 内置守卫缺失: {_SKILL_GUARD}", file=sys.stderr)
        print(f"   修复:确认 skill-markets/ai-testmate/scripts/ai-testmate-guard.py 存在", file=sys.stderr)
        return 1

    # 过滤:仅透传 flag(以 '-' 开头),丢弃位置参数与 '--' 之后的分隔项
    filtered: list[str] = []
    stop = False
    for arg in sys.argv[1:]:
        if stop:
            break
        if arg == "--":
            stop = True
            continue
        if arg.startswith("-"):
            filtered.append(arg)
        # else: 位置参数(如 skill 路径)丢弃,内置守卫从 SKILL_DIR 自动取

    cmd = [sys.executable, str(_SKILL_GUARD), *filtered]
    r = subprocess.run(cmd, capture_output=True, text=True)

    # stdout/stderr 直接透传
    if r.stdout:
        sys.stdout.write(r.stdout)
    if r.stderr:
        sys.stderr.write(r.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())