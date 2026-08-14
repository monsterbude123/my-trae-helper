"""Conftest — agent-dev-control-kit 测试根配置

设计原则(按 acceptance-discipline §1.3 + test-experience §3):
  - 全程 tmp_path,不依赖项目路径
  - 自动装载 scripts/*.py(文件名含连字符,用 importlib)
  - autouse fixture 关闭外部副作用(shutil.copy / chmod)
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Iterable

import pytest

# ----------------------------------------------------------------------
# 路径常量
# ----------------------------------------------------------------------
SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_ROOT / "scripts"
REGISTRY_DIR = SKILL_ROOT / "registry"
SCAFFOLDS_DIR = SKILL_ROOT / "scaffolds"
TEMPLATES_DIR = SKILL_ROOT / "templates"
PRESETS_DIR = SKILL_ROOT / "presets"
SKILLS_DIR = SKILL_ROOT / "skills"


# ----------------------------------------------------------------------
# 模块动态导入
# ----------------------------------------------------------------------
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
def validate_gate_integrity():
    """validate-gate-integrity.py 模块句柄。"""
    return _load_module(
        "validate_gate_integrity",
        SCRIPTS_DIR / "validate-gate-integrity.py",
    )


@pytest.fixture(scope="session")
def validate_execution_skill():
    """validate-execution-skill.py 模块句柄。"""
    return _load_module(
        "validate_execution_skill",
        SCRIPTS_DIR / "validate-execution-skill.py",
    )


@pytest.fixture(scope="session")
def install_husky():
    """install-husky.py 模块句柄(自带 ENV 处理 R-2)。"""
    return _load_module(
        "install_husky",
        SCRIPTS_DIR / "install-husky.py",
    )


@pytest.fixture(scope="session")
def gate_check():
    return _load_module("gate_check", SCRIPTS_DIR / "gate-check.py")


@pytest.fixture(scope="session")
def run_all_guards():
    return _load_module("run_all_guards", SCRIPTS_DIR / "run-all-guards.py")


@pytest.fixture
def make_pkg_json():
    """工厂函数:写一份 package.json(覆盖正常 / echo-skip / 缺脚本三种档位)。"""

    def _make(
        tmp_path: Path,
        scripts: dict[str, str] | None = None,
        *,
        missing: bool = False,
    ) -> Path:
        pkg = tmp_path / "package.json"
        if missing:
            pkg.write_text("{}", encoding="utf-8")
            return pkg
        import json

        pkg.write_text(
            json.dumps(
                {"name": "fixture", "version": "1.0.0", "scripts": scripts or {}},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return pkg

    return _make


@pytest.fixture
def make_pyproject():
    """工厂函数:写一份 pyproject.toml。"""

    def _make(
        tmp_path: Path,
        *,
        with_build_backend: bool = True,
        section: str = "[project]\nname='x'\nversion='0.0.1'\n",
    ) -> Path:
        p = tmp_path / "pyproject.toml"
        body = section
        if with_build_backend:
            body += "\n[build-system]\nrequires=['setuptools']\nbuild-backend='setuptools.build_meta'\n"
        p.write_text(body, encoding="utf-8")
        return p

    return _make


@pytest.fixture
def write_husky_hook():
    """在 tmp 写 .husky/pre-commit 或 pre-push(可注入 fake-skip body)。"""

    def _write(tmp_path: Path, hook_name: str, body: str) -> Path:
        husky = tmp_path / ".husky"
        husky.mkdir(parents=True, exist_ok=True)
        path = husky / hook_name
        path.write_text(body, encoding="utf-8")
        return path

    return _write


@pytest.fixture
def invoke_cli():
    """以子进程跑 scripts/<x>.py,捕获 (returncode, stdout, stderr)。"""

    def _run(script: str, args: Iterable[str], cwd: Path | None = None) -> tuple[int, str, str]:
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


@pytest.fixture(autouse=True)
def _clean_hint_log_per_test():
    """每个测试前清空 hints 日志 — 避免跨测试污染。"""
    from tests._helpers.agent_hint import clear_emitted_hints

    clear_emitted_hints()
    yield
    # 测试中也清,让 hint 日志"当前测试期间的最末状态"
    # 可读 aggregation,而不被前一个测试影响
    clear_emitted_hints()
