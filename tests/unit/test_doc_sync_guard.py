#!/usr/bin/env python3
"""
tests/unit/test_doc_sync_guard.py — doc-sync-guard.py 守卫单元测试 (2026-08-15 NEW)

设计目的:
  验证 scripts/doc-sync-guard.py 的核心判定逻辑符合预期:
    - SKILL 实质内容变更 → 触发同步检查
    - 仅注释 / 仅空行 → 不触发
    - SKILL.md frontmatter 关键字段变更 → 必触发
    - 全部同步后 → PASS
    - 子目录 README 不算 skill 一级人类入口文档

测试策略:
  调 scripts/doc-sync-guard.py --self-test(自检模式内置反例),断言 exit 0
  + 包含所有 6 个反例 PASS 字样。这样:
    1. 测试本身极简(子进程调用 + 输出断言)
    2. 反例集中在 doc-sync-guard.py 内,改逻辑只改一个文件
    3. 复用 doc-sync-guard.py 自身的 tmp git 仓库构造,无需 pytest 重复造

运行:
  python tests/unit/test_doc_sync_guard.py
  # 或 pytest
  python -m pytest tests/unit/test_doc_sync_guard.py -q
"""
import os
import subprocess
import sys
from pathlib import Path

# Windows cp1252 兜底(AGENTS.md §4.1.3)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GUARD = REPO_ROOT / "scripts" / "doc-sync-guard.py"

passed = 0
failed = 0


def _safe_decode(b: bytes | None) -> str:
    """Windows cp1252 兜底解码。"""
    if not b:
        return ""
    return b.decode("utf-8", errors="replace")


def run_self_test() -> tuple[int, str]:
    """调用 doc-sync-guard.py --self-test,返回 (exit_code, stdout+stderr)。"""
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    proc = subprocess.run(
        [sys.executable, str(GUARD), "--self-test"],
        capture_output=True,
        cwd=str(REPO_ROOT),
        creationflags=creationflags,
    )
    return proc.returncode, _safe_decode(proc.stdout) + _safe_decode(proc.stderr)


def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  ✅ {name}")
        passed += 1
    except AssertionError as e:
        print(f"  ❌ {name}")
        print(f"     {e}")
        failed += 1


print("━━━ doc-sync-guard.py ━━━")


def test_self_test_exits_zero():
    """self-test 6 个反例全部通过 → exit 0。"""
    code, output = run_self_test()
    assert code == 0, f"--self-test exit={code}\noutput={output}"


def test_self_test_covers_substantial_change():
    """Case A: SKILL 改 8 行实质语义 → BLOCK。

    _self_test_case 的输出格式是单行 '  ✅ A: SKILL 8 行语义 ... (期望 exit 1, 实际 exit 1)'。
    """
    code, output = run_self_test()
    expected = "✅ A: SKILL 8 行语义 + 缺同步 → BLOCK (期望 exit 1, 实际 exit 1)"
    assert expected in output, f"未找到 Case A 完整成功行:\n{output[:500]}"


def test_self_test_covers_comment_only():
    """Case B: SKILL 只改 8 行注释 → 不触发 → PASS。"""
    code, output = run_self_test()
    assert "B: SKILL 只改 8 行注释 → PASS" in output


def test_self_test_covers_blank_only():
    """Case C: SKILL 只改 8 行空行 → 不触发 → PASS。"""
    code, output = run_self_test()
    assert "C: SKILL 只改 8 行空行 → PASS" in output


def test_self_test_covers_frontmatter_change():
    """Case D: SKILL.md frontmatter 关键字段变更 → 必触发 → README 缺 → BLOCK。"""
    code, output = run_self_test()
    assert "D: SKILL frontmatter 改 + README 缺 → BLOCK" in output


def test_self_test_covers_full_sync():
    """Case E: SKILL 改 8 行 + 全部项目侧 + skill 一级 README/AGENTS 同步 → PASS。"""
    code, output = run_self_test()
    assert "E: SKILL 8 行 + 全部同步 → PASS" in output


def test_self_test_covers_excluded_subdir():
    """Case F: skill 内子目录 README 改 → 不算 skill 一级 → 不触发 → PASS。"""
    code, output = run_self_test()
    assert "F: 子目录 README 不算 skill 一级 → 不触发 → PASS" in output


def test_self_test_six_of_six_pass():
    """汇总行必须是 6/6 通过(防"某 case 偷偷改成 WARN 通过"反模式)。"""
    code, output = run_self_test()
    assert "汇总: 6/6 通过" in output, (
        f"汇总行不是 6/6 — 有 case 被偷偷 WARN 跳过或失败:\n{output}"
    )


def test_default_no_args_help_or_pass():
    """无参数:不传 --self-test 时,要么是 PASS(空 staged),要么是非 0;不会 BLOCK 在反例路径。"""
    # 此测试不调子进程(避免污染真实仓库 staged) — 仅校验脚本能在没 self-test 时正常启动。
    # 直接 python -c 调 main() 的 help 路径
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    proc = subprocess.run(
        [sys.executable, str(GUARD), "--help"],
        capture_output=True,
        cwd=str(REPO_ROOT),
        creationflags=creationflags,
    )
    assert proc.returncode == 0, f"--help 失败: exit={proc.returncode}"


test("self-test 全部通过 (exit 0)", test_self_test_exits_zero)
test("覆盖 Case A (8 行实质 → BLOCK)", test_self_test_covers_substantial_change)
test("覆盖 Case B (注释 → PASS)", test_self_test_covers_comment_only)
test("覆盖 Case C (空行 → PASS)", test_self_test_covers_blank_only)
test("覆盖 Case D (frontmatter → BLOCK)", test_self_test_covers_frontmatter_change)
test("覆盖 Case E (全部同步 → PASS)", test_self_test_covers_full_sync)
test("覆盖 Case F (子目录 README 不算一级)", test_self_test_covers_excluded_subdir)
test("汇总 6/6 通过(防 WARN 反模式)", test_self_test_six_of_six_pass)
test("脚本 --help 可正常调用", test_default_no_args_help_or_pass)

print(f"\n━━━ 汇总: ✅ {passed} 通过  ❌ {failed} 失败 ━━━")

if failed > 0:
    sys.exit(1)