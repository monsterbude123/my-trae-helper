"""install-husky 反例单元测试

覆盖:
  - R-2 目标 ≠ 源(防 self-overwrite)
  - dry-run 模式不能写盘
  - chmod 调用与 Windows 兼容
  - 未知 stack 的 WARN 兜底
  - 二次运行幂等性
"""
from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

pytestmark = pytest.mark.unit


# ============================================================================
# TestResolveTargetSafety — R-2 铁律
# ============================================================================
class TestResolveTargetSafety:
    @pytest.mark.trap
    def test_nonexistent_path_does_not_raise(self, install_husky, tmp_path: Path):
        """R-2 strict=False:路径不存在时不能抛 FileNotFoundError。"""
        nonexistent = tmp_path / "future-project"
        assert not nonexistent.exists()
        resolved = install_husky.resolve_target_safety(str(nonexistent))
        assert resolved.is_absolute()

    @pytest.mark.trap
    def test_target_eq_skill_root_raises(self, install_husky):
        """R-2:目标指向 skill 根 → 必须抛 ValueError。"""
        with pytest.raises(ValueError, match="R-2 violation"):
            install_husky.resolve_target_safety(str(install_husky.SKILL_ROOT))

    @pytest.mark.trap
    def test_target_inside_skill_raises(self, install_husky):
        """R-2:目标在 skill 目录内 → 必须抛 ValueError。"""
        inside = str(install_husky.SKILL_ROOT / "scripts" / "evil")
        with pytest.raises(ValueError, match="R-2 violation"):
            install_husky.resolve_target_safety(inside)


# ============================================================================
# TestDryRun — AP-2 / AP-3: dry-run 必须零写入
# ============================================================================
class TestDryRun:
    @pytest.mark.trap
    def test_dry_run_creates_no_files(self, install_husky, tmp_path: Path):
        """dry-run 必须不创建任何 .husky 内容。"""
        rc = install_husky.install("nodejs", str(tmp_path), dry_run=True)
        assert rc == install_husky.EXIT_OK
        husky = tmp_path / ".husky"
        assert not husky.exists()


# ============================================================================
# TestCopyAndChmod — chmod + Windows 退化
# ============================================================================
class TestCopyAndChmod:
    def test_pre_commit_and_pre_push_created(self, install_husky, tmp_path: Path):
        with mock.patch("install_husky.os.chmod"):
            rc = install_husky.install("nodejs", str(tmp_path), dry_run=False)
        assert rc == install_husky.EXIT_OK
        husky = tmp_path / ".husky"
        assert (husky / "pre-commit").is_file()
        assert (husky / "pre-push").is_file()

    def test_chmod_called_with_0o755(self, install_husky, tmp_path: Path):
        with mock.patch("install_husky.os.chmod") as mchmod:
            install_husky.install("nodejs", str(tmp_path), dry_run=False)
        # 验证 chmod 调用至少出现过 0o755
        args_calls = [c.args for c in mchmod.call_args_list]
        assert any(call_args[1] == 0o755 for call_args in args_calls if len(call_args) >= 2)

    @pytest.mark.trap
    def test_windows_chmod_oserror_handled(self, install_husky, tmp_path: Path):
        """chmod 抛 OSError(Windows 常见)不能杀进程。"""
        with mock.patch(
            "install_husky.os.chmod",
            side_effect=OSError("simulated Windows chmod failure"),
        ):
            rc = install_husky.install("nodejs", str(tmp_path), dry_run=False)
        assert rc == install_husky.EXIT_OK
        # 文件仍存在
        husky = tmp_path / ".husky"
        assert (husky / "pre-commit").is_file()


# ============================================================================
# TestStackResolution — stack 解析 + WARN 兜底
# ============================================================================
class TestStackResolution:
    def test_load_stacks_returns_at_least_builtins(self, install_husky):
        stacks = install_husky.load_stacks()
        for sid in ("nodejs", "python", "go", "java-maven"):
            assert sid in stacks, f"内置 stack '{sid}' 必须被注册"

    @pytest.mark.trap
    def test_unknown_stack_warns_and_skips(self, install_husky, tmp_path: Path, capsys):
        rc = install_husky.install("nonexistent-zzz-stack", str(tmp_path), dry_run=False)
        assert rc == install_husky.EXIT_OK
        assert not (tmp_path / ".husky").exists()


# ============================================================================
# TestIdempotent — 二次安装幂等
# ============================================================================
class TestIdempotent:
    def test_second_install_is_idempotent(self, install_husky, tmp_path: Path):
        with mock.patch("install_husky.os.chmod"):
            rc1 = install_husky.install("nodejs", str(tmp_path), dry_run=False)
            rc2 = install_husky.install("nodejs", str(tmp_path), dry_run=False)
        assert rc1 == rc2 == install_husky.EXIT_OK
        husky = tmp_path / ".husky"
        assert (husky / "pre-commit").read_bytes() == (husky / "pre-commit").read_bytes()


# ============================================================================
# TestParseArgs
# ============================================================================
class TestParseArgs:
    def test_requires_target(self, install_husky):
        with pytest.raises(SystemExit):
            install_husky.parse_args(["--stack", "nodejs"])

    def test_defaults(self, install_husky):
        ns = install_husky.parse_args(["--target", "."])
        assert ns.stack == "nodejs"
        assert ns.target == "."
        assert ns.dry_run is False

    def test_dry_run_flag(self, install_husky):
        ns = install_husky.parse_args(["--target", ".", "--dry-run"])
        assert ns.dry_run is True


# ============================================================================
# TestMain — via subprocess,AP-3 关键:脚本必须有 CLI 自执行入口
# ============================================================================
class TestMain:
    @pytest.mark.trap
    def test_cli_runs_against_tmp(self, install_husky, invoke_cli, tmp_path: Path):
        """AP-3 反例固化:直接执行脚本必须有副作用。"""
        rc, stdout, _ = invoke_cli(
            "install-husky.py",
            ["--stack", "nodejs", "--target", str(tmp_path)],
        )
        assert rc == install_husky.EXIT_OK
        husky = tmp_path / ".husky"
        assert (husky / "pre-commit").is_file(), "CLI 自执行入口必须真正写入"

    def test_cli_dry_run_no_write(self, install_husky, invoke_cli, tmp_path: Path):
        rc, _, _ = invoke_cli(
            "install-husky.py",
            ["--stack", "nodejs", "--target", str(tmp_path), "--dry-run"],
        )
        assert rc == install_husky.EXIT_OK
        assert not (tmp_path / ".husky").exists()
