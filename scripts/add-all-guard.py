#!/usr/bin/env python3
"""
scripts/add-all-guard.py — add-all CLI 命令专属守卫 (2026-08-18 guard-smith 委派生成)

设计目的:
  `add-all` 是 CLI 命令(src/add-all.mjs)而非 skill 包,不在 skill-markets/ 下。
  按 doc-sync / find-skills / github-kownledge-helper 先例注册为 "meta skill" 条目。

  本守卫验证:
    1. src/add-all.mjs 存在 + 语法 OK (node --check)
    2. bin/cli.mjs 已注册 add-all + install-all 命令(可通过 --help 冒烟)
    3. tests/unit/test_add_all.mjs 存在 + 单元测试通过(node 跑通即视为 PASS)

  与常规 skill 守卫(指向 skill-markets/<pkg>/)不同,本守卫不依赖 skill-markets/<name>/ 目录;
  guard-router.mjs 调用时传入 `skill-markets/add-all` 作为 positional argv,本脚本忽略之。

用法:
  python scripts/add-all-guard.py add-all          # 完整检查(默认走真实路径)
  python scripts/add-all-guard.py add-all --self-test   # 反例自检(用临时 mock)

退出码:
  0 = PASS (errors=0, warnings=0)
  1 = BLOCK (errors≥1)
  2 = WARN (errors=0 但 warnings≥1)

禁止:
  - 不要 import skill-markets/<pkg>/scripts/*(与 AGENTS.md §1.11 冲突)
  - 不要硬编码任何 key / token / 个人路径
  - 不要静默跳过任一检查(任一 FAIL = exit 1)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest.mock as mock
from pathlib import Path
from typing import List, Tuple

# Windows cp1252 兜底(AGENTS.md §4.1.3 + trap-instructions.yaml AP-9)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent

# ─── 关键路径(全部相对 REPO_ROOT,可在 self-test 时被 monkeypatch 覆盖) ─────────────────
ADD_ALL_SRC = REPO_ROOT / "src" / "add-all.mjs"
CLI_BIN = REPO_ROOT / "bin" / "cli.mjs"
TEST_FILE = REPO_ROOT / "tests" / "unit" / "test_add_all.mjs"


def _subprocess_env() -> dict:
    """跨平台子进程环境 — 不显式 PYTHONIOENCODING(stdlib 即可读 utf-8)。"""
    env = os.environ.copy()
    env.setdefault("NO_COLOR", "1")
    return env


def _creationflags() -> int:
    """Windows 下隐藏 subprocess 弹出的 cmd 窗口;POSIX 下为 0。"""
    return getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0


def _check_src_syntax() -> Tuple[bool, str]:
    """检查 src/add-all.mjs 存在 + node --check 通过。"""
    if not ADD_ALL_SRC.exists():
        return False, f"src/add-all.mjs 不存在: {ADD_ALL_SRC}"
    try:
        r = subprocess.run(
            ["node", "--check", str(ADD_ALL_SRC)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(REPO_ROOT),
            env=_subprocess_env(),
            creationflags=_creationflags(),
            timeout=15,
        )
        if r.returncode != 0:
            return False, f"node --check src/add-all.mjs 失败: {(r.stderr or r.stdout).strip()}"
        return True, f"src/add-all.mjs 语法 OK ({ADD_ALL_SRC.stat().st_size} bytes)"
    except FileNotFoundError:
        return False, "node 命令未找到 — 请确认 Node.js 已安装且在 PATH 中"
    except subprocess.TimeoutExpired:
        return False, "node --check src/add-all.mjs 超时(>15s)"
    except Exception as e:
        return False, f"node --check src/add-all.mjs 异常: {type(e).__name__}: {e}"


def _run_cli_subcommand(subcommand: str) -> Tuple[bool, str]:
    """跑 `node bin/cli.mjs <subcommand> --help`,返回 (success, detail)。"""
    if not CLI_BIN.exists():
        return False, f"bin/cli.mjs 不存在: {CLI_BIN}"
    try:
        r = subprocess.run(
            ["node", str(CLI_BIN), subcommand, "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(REPO_ROOT),
            env=_subprocess_env(),
            creationflags=_creationflags(),
            timeout=15,
        )
        out = (r.stdout or "") + (r.stderr or "")
        if r.returncode != 0 or "add-all" not in out:
            return False, (
                f"bin/cli.mjs {subcommand} --help 失败(exit={r.returncode}): "
                f"{out.strip()[:300] or '(空输出)'}"
            )
        return True, f"bin/cli.mjs {subcommand} --help OK"
    except subprocess.TimeoutExpired:
        return False, f"bin/cli.mjs {subcommand} --help 超时(>15s)"
    except Exception as e:
        return False, f"bin/cli.mjs {subcommand} --help 异常: {type(e).__name__}: {e}"


def _check_cli_registration() -> Tuple[bool, str]:
    """检查 bin/cli.mjs add-all + install-all 都已注册。"""
    parts: List[str] = []
    for sub in ("add-all", "install-all"):
        ok, detail = _run_cli_subcommand(sub)
        if not ok:
            return False, detail
        parts.append(detail)
    return True, "; ".join(parts)


def _check_test_file() -> Tuple[bool, str]:
    """检查 tests/unit/test_add_all.mjs 存在 + 跑一遍(node 退出码 0)。"""
    if not TEST_FILE.exists():
        return False, f"tests/unit/test_add_all.mjs 不存在: {TEST_FILE}"

    try:
        r = subprocess.run(
            ["node", str(TEST_FILE)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(REPO_ROOT),
            env=_subprocess_env(),
            creationflags=_creationflags(),
            timeout=60,
        )
        out = (r.stdout or "") + (r.stderr or "")
        if r.returncode != 0:
            return False, (
                f"node tests/unit/test_add_all.mjs 失败(exit={r.returncode}): "
                f"{out.strip()[-400:]}"
            )
        return True, "tests/unit/test_add_all.mjs PASS (node 跑通)"
    except subprocess.TimeoutExpired:
        return False, "node tests/unit/test_add_all.mjs 超时(>60s)"
    except Exception as e:
        return False, f"node tests/unit/test_add_all.mjs 异常: {type(e).__name__}: {e}"


# ─── 主检查函数 ──────────────────────────────────────────────────────────────
def check_add_all(_skill_path_unused: str) -> dict:
    """add-all 专属守卫 — 组合 3 项 CLI 检查。

    _skill_path_unused: guard-router.mjs 传入的 positional argv,
                       本守卫不依赖 skill-markets/<pkg>/ 目录(忽略之)。
    """
    errors: List[str] = []
    warnings: List[str] = []
    info: List[str] = []

    checks = [
        ("src 语法", _check_src_syntax),
        ("CLI 注册", _check_cli_registration),
        ("单元测试", _check_test_file),
    ]

    for label, fn in checks:
        ok, detail = fn()
        if not ok:
            errors.append(f"[{label}] {detail}")
        else:
            info.append(f"[{label}] {detail}")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "info": info,
    }


# ─── Self-test(用临时 mock 文件) ──────────────────────────────────────────────
def _write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def _patch_paths(tmp: Path):
    """monkeypatch 模块级路径常量到 tmp 目录,返回 patcher(调用方负责 start/stop)。"""
    return mock.patch.multiple(
        __name__,
        REPO_ROOT=tmp,
        ADD_ALL_SRC=tmp / "src" / "add-all.mjs",
        CLI_BIN=tmp / "bin" / "cli.mjs",
        TEST_FILE=tmp / "tests" / "unit" / "test_add_all.mjs",
    )


def _run_case_with_mock(tmp_root: Path, setup_fn) -> Tuple[int, bool]:
    """通用 case runner — 准备 tmp 文件 → monkeypatch → 跑 check → 还原。"""
    setup_fn(tmp_root)
    patcher = _patch_paths(tmp_root)
    patcher.start()
    try:
        result = check_add_all("unused")
        code = 0 if result["passed"] else 1
        return code, True
    except Exception as e:
        print(f"     内部异常: {type(e).__name__}: {e}")
        return 1, False
    finally:
        patcher.stop()


def _case_a_src_missing(tmp: Path) -> int:
    """A: src/add-all.mjs 缺失 → 守卫应 BLOCK。"""

    def setup(t: Path) -> None:
        _write(t / "bin" / "cli.mjs", "console.log('add-all --help OK');\n")
        _write(t / "tests" / "unit" / "test_add_all.mjs", "console.log('test PASS');\n")

    code, _ = _run_case_with_mock(tmp, setup)
    return code


def _case_b_cli_unregistered(tmp: Path) -> int:
    """B: bin/cli.mjs 没注册 add-all 命令(exit=1) → 守卫应 BLOCK。"""

    def setup(t: Path) -> None:
        _write(t / "src" / "add-all.mjs", "export const x = 1;\n")
        _write(t / "bin" / "cli.mjs", "console.log('no add-all here'); process.exit(1);\n")
        _write(t / "tests" / "unit" / "test_add_all.mjs", "console.log('test');\n")

    code, _ = _run_case_with_mock(tmp, setup)
    return code


def _case_c_test_missing(tmp: Path) -> int:
    """C: 测试文件缺失 → 守卫应 BLOCK。"""

    def setup(t: Path) -> None:
        _write(t / "src" / "add-all.mjs", "export const x = 1;\n")
        _write(
            t / "bin" / "cli.mjs",
            "const c = process.argv[2];\n"
            "if (c === 'add-all' || c === 'install-all') { console.log('add-all --help OK'); process.exit(0); }\n"
            "process.exit(1);\n",
        )
        # 测试文件故意缺失

    code, _ = _run_case_with_mock(tmp, setup)
    return code


def _case_d_all_present(tmp: Path) -> int:
    """D: 全部就绪 → 守卫应 PASS。"""

    def setup(t: Path) -> None:
        _write(t / "src" / "add-all.mjs", "export const x = 1;\n")
        _write(
            t / "bin" / "cli.mjs",
            "const c = process.argv[2];\n"
            "if (c === 'add-all' || c === 'install-all') { console.log('add-all --help OK'); process.exit(0); }\n"
            "process.exit(1);\n",
        )
        _write(t / "tests" / "unit" / "test_add_all.mjs", "console.log('test PASS');\n")

    code, _ = _run_case_with_mock(tmp, setup)
    return code


def _self_test() -> int:
    """反例自检 — 临时目录 mock → 跑 4 个 case。"""
    print("━━━ add-all-guard self-test ━━━")
    cases = [
        ("A: src/add-all.mjs 缺失 → BLOCK", 1, _case_a_src_missing),
        ("B: bin/cli.mjs 未注册 add-all → BLOCK", 1, _case_b_cli_unregistered),
        ("C: 测试文件缺失 → BLOCK", 1, _case_c_test_missing),
        ("D: 全部就绪 → PASS", 0, _case_d_all_present),
    ]

    ok_count = 0
    for name, expect, fn in cases:
        tmp = Path(tempfile.mkdtemp(prefix="add-all-guard-"))
        try:
            code = fn(tmp)
            ok = code == expect
            mark = "✅" if ok else "❌"
            print(f"  {mark} {name} (期望 exit {expect}, 实际 exit {code})")
            if ok:
                ok_count += 1
        except Exception as e:
            print(f"  ❌ {name} — 异常: {type(e).__name__}: {e}")
        finally:
            shutil.rmtree(str(tmp), ignore_errors=True)

    print(f"\n  汇总: {ok_count}/{len(cases)} 通过")
    return 0 if ok_count == len(cases) else 1


# ─── 主入口 ──────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(
        description="add-all CLI 命令专属守卫 (meta skill guard)",
        allow_abbrev=False,
    )
    parser.add_argument(
        "skill_path",
        nargs="?",
        default="add-all",
        help="被 guard-router.mjs 传入的 positional argv(本守卫忽略)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="跑反例自检(monkeypatch 路径 + 临时目录)",
    )
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    result = check_add_all(args.skill_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    info = result.get("info") or []
    warnings = result.get("warnings") or []
    errors = result.get("errors") or []
    passed = bool(result.get("passed", False))

    if info:
        print("\nℹ️ 提示(不阻断):")
        for item in info:
            print(f"  - {item}")
    if warnings:
        print("\n⚠️ 警告:")
        for w in warnings:
            print(f"  - {w}")
    if not passed:
        print("\n❌ add-all 守卫检查失败:")
        for e in errors:
            print(f"  - {e}")
        return 1

    label = "add-all CLI 守卫"
    suffix = f" (含 {len(warnings)} 条 warnings)" if warnings else ""
    print(f"\n✅ {label} PASS{suffix}")
    return 0


if __name__ == "__main__":
    sys.exit(main())