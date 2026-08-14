#!/usr/bin/env python3
"""scripts/run-agent-dev-control-kit-tests.py — 跨平台跑 agent-dev-control-kit 子套件

用途:
  - CI (GitHub Actions) 跑子套件
  - 本地开发用,与 catalog-guard.py 搭配
  - 跨平台:Windows / macOS / Linux(纯 Python,不依赖 bash)

触发时机:
  - L3 merge gate:agent-dev-control-kit 子目录有变更
  - L4 publish gate:每次发布
  - 本地:python scripts/run-agent-dev-control-kit-tests.py

反例自验收(§2.4):
  - FAIL 态:故意破坏 catalog -> 期望 exit != 0
  - PASS 态:现状 catalog -> 期望 exit 0
  - 边界态:logs/agent-hints.jsonl 缺失 -> 期望 exit 0

退出码:
  0 = 全部通过
  1 = 测试失败
  2 = 依赖缺失
  3 = 路径错误
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_DIR = REPO_ROOT / "skill-markets" / "agent-dev-control-kit"


def _find_python() -> str:
    """找 python 解释器。

    优先级:
      1. 环境变量 MY_TRAE_HELPER_PY(由 pre-commit 注入,带 pytest)
      2. sys.executable(脚本自身用的解释器)
      3. python3 / python(PATH 中)

    Git Bash 在 Windows 上 `python3` 经常没 pip 模块,会卡 _step_install_deps。
    """
    candidates = []
    env_py = os.environ.get("MY_TRAE_HELPER_PY")
    if env_py:
        candidates.append(env_py)
    if sys.executable:
        candidates.append(sys.executable)
    candidates += ["python3", "python"]
    for candidate in candidates:
        if not candidate:
            continue
        if Path(candidate).is_file() or shutil.which(candidate):
            return candidate
    print("ERR: 找不到 python / python3", file=sys.stderr)
    sys.exit(2)


def _step_install_deps(python: str) -> None:
    """缺 pytest/pyyaml 时安装。"""
    # 用子进程探测(python 参数可能与本进程的 sys.executable 不同,
    # 例如 Git Bash 用 python3 启脚本,但 MY_TRAE_HELPER_PY 指向 miniconda python)
    probe = subprocess.run(
        [python, "-c", "import pytest, yaml"],
        capture_output=True, text=True, check=False,
    )
    if probe.returncode == 0:
        return
    print("install pytest + pyyaml ...")
    subprocess.run(
        [python, "-m", "pip", "install", "--quiet", "pytest>=7.0", "pyyaml>=6.0"],
        check=True,
    )


def _run(label: str, args: list[str], cwd: Path) -> int:
    print(f"run {label} ...")
    r = subprocess.run(args, cwd=str(cwd), check=False)
    return r.returncode


def main() -> int:
    if not TARGET_DIR.is_dir():
        print(f"ERR: 找不到目录 {TARGET_DIR}", file=sys.stderr)
        return 3

    python = _find_python()
    _step_install_deps(python)

    # 1. catalog-guard
    rc = _run("catalog-guard", [python, "scripts/catalog-guard.py"], cwd=TARGET_DIR)
    if rc != 0:
        print("ERR: catalog-guard 失败", file=sys.stderr)
        return 1

    # 2. trap 反例集(自验收,§2.4)
    rc = _run(
        "trap-反例集",
        [python, "-m", "pytest", "tests", "-m", "trap", "--tb=short", "-q"],
        cwd=TARGET_DIR,
    )
    if rc != 0:
        print("ERR: trap 反例集失败", file=sys.stderr)
        return 1

    # 3. 全量测试
    rc = _run(
        "全量-pytest",
        [python, "-m", "pytest", "tests", "--tb=short", "-q"],
        cwd=TARGET_DIR,
    )
    if rc != 0:
        print("ERR: 全量 pytest 失败", file=sys.stderr)
        return 1

    # 4. 聚合 hints(可选,不阻断)
    hint_log = TARGET_DIR / "logs" / "agent-hints.jsonl"
    if hint_log.is_file():
        print("残留 hints:")
        try:
            subprocess.run(
                [python, "scripts/agent-hint-emit.py", "--group-by", "trap"],
                cwd=str(TARGET_DIR),
                check=False,
            )
        except Exception as exc:
            print(f"  hints 聚合失败,可忽略: {exc}")

    print("OK: agent-dev-control-kit 测试全通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
