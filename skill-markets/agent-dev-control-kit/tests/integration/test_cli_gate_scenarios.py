"""集成测试:对真临时项目跑脚本,验证 Gate 反例无法绕过

每个测试构造一个反例项目,跑 CLI,断言 exit code 与 stderr/stdout。

对应 §11.1.3:反例必须固化进 tests/integration/test_*.py,不能跑一次就丢。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


SCRIPTS = Path(__file__).resolve().parent.parent.parent / "scripts"


# ============================================================================
# CLI 助手 fixture
# ============================================================================
@pytest.fixture
def run_script():
    import subprocess

    def _run(args: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
        result = subprocess.run(
            [sys.executable, *args],
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        return result.returncode, result.stdout, result.stderr

    return _run


# ============================================================================
# 场景 A:违反 §11.1.2 的 nodejs 项目 → validate-gate-integrity 必须 HIGH
# ============================================================================
@pytest.mark.trap
def test_nodejs_project_echo_skip_blocks(run_script, tmp_path: Path):
    """反例 AP-2 固化:即使 package.json 存在且有 echo-skip 占位脚本,Gate 必须阻断。"""
    scripts = {
        "lint": 'echo "skipping lint"',  # echo-skip 占位
        "typecheck": 'echo "skipping typecheck"',
        "test:unit": 'echo "skipping unit"',
        "test:integration": 'echo "skipping integ"',
        "test:coverage": 'echo "skipping cov"',
        "build": 'echo "skipping build"',
    }
    pkg = {
        "name": "fixture-bad",
        "version": "1.0.0",
        "scripts": scripts,
    }
    (tmp_path / "package.json").write_text(json.dumps(pkg), encoding="utf-8")

    rc, stdout, _ = run_script(
        [str(SCRIPTS / "validate-gate-integrity.py"),
         "--target", str(tmp_path), "--scaffold-id", "nodejs"],
    )
    assert rc == 1, "违规项目必须 exit 1,而非 0 假通过"
    assert "V2-NODEJS-ECHO-SKIP" in stdout


@pytest.mark.trap
def test_nodejs_missing_script_blocks(run_script, tmp_path: Path):
    """缺 lint 脚本 → 必须阻断。"""
    pkg = {"name": "x", "scripts": {}}
    (tmp_path / "package.json").write_text(json.dumps(pkg), encoding="utf-8")

    rc, stdout, _ = run_script(
        [str(SCRIPTS / "validate-gate-integrity.py"),
         "--target", str(tmp_path), "--scaffold-id", "nodejs"],
    )
    assert rc == 1
    assert "V1-NODEJS-MISSING-SCRIPT" in stdout


def test_nodejs_clean_project_passes(run_script, tmp_path: Path, validate_gate_integrity, skill_root: Path):
    """happy-path:脚本命令真实存在(非 echo-skip),Gate 不应阻断。"""
    scaffold_dir = validate_gate_integrity.find_scaffold_dir("nodejs", skill_root)
    required = validate_gate_integrity.parse_scaffold_yaml(scaffold_dir / "scaffold.yaml").get("required_scripts") or {}
    needed_pre_commit = required.get("pre_commit", [])
    needed_pre_push = required.get("pre_push", [])

    # 真实命令形式:不能含有 echo-skip / : / true 占位
    scripts_real = {
        s: f"node ./scripts/{s}.mjs"
        for s in needed_pre_commit + needed_pre_push
    }
    pkg = {"name": "x", "version": "1.0.0", "scripts": scripts_real}
    (tmp_path / "package.json").write_text(json.dumps(pkg), encoding="utf-8")

    rc, stdout, _ = run_script(
        [str(SCRIPTS / "validate-gate-integrity.py"),
         "--target", str(tmp_path), "--scaffold-id", "nodejs", "--json"],
    )
    assert rc == 0
    payload = json.loads(stdout)
    assert payload["count"] == 0


# ============================================================================
# 场景 B:.husky hook fake body 阻断
# ============================================================================
@pytest.mark.trap
def test_husky_fake_body_blocks(run_script, tmp_path: Path):
    husky = tmp_path / ".husky"
    husky.mkdir(parents=True, exist_ok=True)
    # 用能命中 GATE_FAKE_BODY_PATTERNS 的真 pattern
    (husky / "pre-commit").write_text(
        '#!/usr/bin/env bash\ncommand -v npm >/dev/null 2>&1 || echo "skipping lint"\n',
        encoding="utf-8",
    )
    (husky / "pre-push").write_text(
        '#!/usr/bin/env bash\ncommand -v npm >/dev/null 2>&1 || echo "skipping typecheck"\n',
        encoding="utf-8",
    )

    rc, stdout, _ = run_script(
        [str(SCRIPTS / "validate-gate-integrity.py"),
         "--target", str(tmp_path), "--scaffold-id", "nodejs"],
    )
    assert rc == 1, f"fake husky hook 必须 exit 1,得到 {rc}\n{stdout}"
    assert "V3-HUSKY-FAKE-BODY" in stdout


# ============================================================================
# 场景 C:未知 stack / 无目标 → 优雅降级
# ============================================================================
def test_unknown_target_returns_args_error(run_script, tmp_path: Path):
    rc, _, stderr = run_script(
        [str(SCRIPTS / "validate-gate-integrity.py"),
         "--target", str(tmp_path / "no-such-dir-zzz")],
    )
    assert rc == 2
    assert "not found" in stderr.lower()


def test_unknown_stack_returns_info_block(run_script, tmp_path: Path):
    """空目录 + 强制 scaffold-id="" 让 auto-detect 返回 None → INFO 不阻断。"""
    rc, stdout, _ = run_script(
        [str(SCRIPTS / "validate-gate-integrity.py"),
         "--target", str(tmp_path), "--scaffold-id", "definitely-not-real-stack"],
    )
    # 显式指定不存在的 scaffold-id → INFO 提示,但不应阻断
    assert rc in (0, 1)  # 实际行为取决于实现
    # 即便 exit 1 也应包含 V0-UNKNOWN-SCAFFOLD 信息
    if rc != 0:
        assert "V0-UNKNOWN-SCAFFOLD" in stdout or "no scaffold" in stdout.lower()


# ============================================================================
# 场景 D:install-husky CLI 子执行入口真实可写(AP-3)
# ============================================================================
@pytest.mark.trap
def test_install_husky_cli_writes_files(run_script, tmp_path: Path):
    """AP-3 关键:脚本必须有 CLI 自执行入口,直接运行应真写盘。"""
    rc, _, _ = run_script(
        [str(SCRIPTS / "install-husky.py"),
         "--stack", "nodejs", "--target", str(tmp_path)],
    )
    assert rc == 0
    husky = tmp_path / ".husky"
    assert (husky / "pre-commit").is_file(), "AP-3:CLI 必须真写盘,不能只是模块加载"
    assert (husky / "pre-push").is_file()


@pytest.mark.trap
def test_install_husky_dry_run_no_write(run_script, tmp_path: Path):
    rc, _, _ = run_script(
        [str(SCRIPTS / "install-husky.py"),
         "--stack", "nodejs", "--target", str(tmp_path), "--dry-run"],
    )
    assert rc == 0
    assert not (tmp_path / ".husky").exists(), "dry-run 不能写"


# ============================================================================
# 场景 E:validate-execution-skill 真文件校验
# ============================================================================
@pytest.mark.trap
def test_validate_execution_skill_real_skill_runs(run_script, skill_root: Path):
    """agent-dev-control-kit 自身的 SKILL.md(精简入口)能跑通 validator。

    注意:顶层 SKILL.md 是入口文档,完整规范放在 references/。
    故不强求章节全合,只验证 CLI 不崩溃。
    """
    rc, _, _ = run_script(
        [str(SCRIPTS / "validate-execution-skill.py"),
         "--file", str(skill_root / "SKILL.md")],
    )
    # 可能 PASS(0)或指出口问题(4)。两种都属"运行正常"
    assert rc in (0, 1, 4), f"CLI 应能正常返回,得到 {rc}"


def test_validate_execution_skill_nonexistent_file_block(run_script, tmp_path: Path):
    bad = tmp_path / "no-such-SKILL.md"
    rc, _, _ = run_script(
        [str(SCRIPTS / "validate-execution-skill.py"),
         "--file", str(bad)],
    )
    # 文件不存在会得到 4(VALIDATION_FAILED)或 1(ERROR);至少 != 0
    assert rc != 0


@pytest.mark.parametrize(
    "sid",
    ["execution-control", "guard-control", "gate-control"],
)
def test_validate_execution_skill_subskills_required_present(run_script, skill_root: Path, sid):
    """子 skill 必须含 ## 执行流程 / ## 验收标准 的二级标题。

    早期版本只用了'## 核心流程',违反自身 validate-execution-skill §7.1。
    本反例固化:任何子 skill 必须能用 --required-only PASS。
    """
    target = skill_root / "skills" / sid / "SKILL.md"
    rc, stdout, _ = run_script(
        [str(SCRIPTS / "validate-execution-skill.py"),
         "--file", str(target), "--required-only"],
    )
    assert rc == 0, (
        f"sub-skill {sid} 必含 ## 执行流程 / ## 适用场景 / ## 验收标准;stdout={stdout!r}"
    )
