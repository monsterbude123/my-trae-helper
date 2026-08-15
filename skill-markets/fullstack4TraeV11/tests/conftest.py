"""Conftest — fullstack4TraeV11 测试根配置

设计原则(按 acceptance-discipline §1.3 + test-experience §3):
  - 全程 tmp_path,不依赖项目路径
  - 自动装载 scripts/*.py(文件名含连字符,用 importlib)
  - 与主仓 pytest 隔离(主仓 conftest 通过 collect_ignore_glob 排除 skill-markets/**/tests)
<!-- scan-whitelist:SHELL_EXEC -->
SECURITY 标注 (V11.7.1 NEW): 本脚本含 SHELL_EXEC 调用, 全部为 V11 业务必需.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_ROOT / "scripts"
REGISTRY_DIR = SKILL_ROOT / "registry"
SCAFFOLDS_DIR = SKILL_ROOT / "scaffolds"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def skill_root() -> Path:
    return SKILL_ROOT


@pytest.fixture(scope="session")
def scripts_dir() -> Path:
    return SCRIPTS_DIR


@pytest.fixture(scope="session")
def validate_gate_config():
    """validate-gate-config.py 模块句柄。"""
    return _load_module(
        "validate_gate_config",
        SCRIPTS_DIR / "validate-gate-config.py",
    )


@pytest.fixture(scope="session")
def run_all_guards():
    """run-all-guards.py 模块句柄。"""
    return _load_module(
        "run_all_guards",
        SCRIPTS_DIR / "run-all-guards.py",
    )


@pytest.fixture(scope="session")
def run_gate_level():
    """scaffolds/nodejs/files/scripts/run-gate-level.py 模块句柄。"""
    return _load_module(
        "run_gate_level",
        SCAFFOLDS_DIR / "nodejs" / "files" / "scripts" / "run-gate-level.py",
    )


@pytest.fixture(scope="session")
def real_gate_config_path():
    """内置 nodejs scaffold 的 gate-config.json（真实数据）。"""
    return SCAFFOLDS_DIR / "nodejs" / "files" / "gates" / "gate-config.json"


@pytest.fixture
def invoke_cli():
    """以子进程跑 scripts/<x>.py,捕获 (returncode, stdout, stderr)。"""

    def _run(script: str, args, cwd: Path | None = None) -> tuple[int, str, str]:
        import subprocess

        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / script), *args],
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        return result.returncode, result.stdout, result.stderr

    return _run