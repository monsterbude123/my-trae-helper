"""new-bug.sh 第 7 字段 source 测试（V11.9 NEW，role-protocol §6）。

覆盖维度:
  - PASS:默认(不传 --source) → source=qa-found, 写入 bug 单 frontmatter 第 7 字段
  - PASS:--source user-feedback → 第 7 字段 = user-feedback
  - PASS:--source scan → 第 7 字段 = scan
  - FAIL:非法 source 值 → 脚本拒绝（exit ≠ 0）
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

# skill-markets/fullstack4TraeV11
SKILL_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = SKILL_ROOT / "skills" / "12-bug-fix" / "scripts" / "bug-hunt" / "new-bug.sh"


def _run_new_bug(tmp_path: Path, args: list[str]) -> subprocess.CompletedProcess:
    """把 new-bug.sh 复制进临时目录后以 basename 运行（产物 docs/bugs/ 落在 tmp_path）。

    规避跨平台 bash 挂载差异（Git-bash /d/... vs WSL /mnt/d/...）：脚本复制到 cwd，
    用相对文件名调用，不依赖绝对路径在 bash 内的解析。
    """
    local_script = tmp_path / "new-bug.sh"
    shutil.copyfile(SCRIPT_PATH, local_script)
    return subprocess.run(
        ["bash", "new-bug.sh"] + args,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )


def _find_bug_file(tmp_path: Path, bug_id: str) -> Path:
    """在 tmp_path/docs/bugs/<date>/ 下定位生成的 bug 单。"""
    files = sorted(tmp_path.glob(f"docs/bugs/*/{bug_id}-*.md"))
    assert files, f"未生成 bug 单: bug_id={bug_id}, docs/bugs/* -> {list(tmp_path.glob('docs/bugs/*'))}"
    return files[0]


def _assert_source(content: str, expected: str):
    """断言 frontmatter 表中第 7 字段 source 行 = expected。"""
    # 表行形如: | source | qa-found |
    assert f"| source | {expected} |" in content, (
        f"期望 source 行 '| source | {expected} |' 存在, 实际内容:\n{content}"
    )


class TestSourceField:
    def test_default_source_is_qa_found(self, tmp_path):
        """PASS:不传 --source → 默认 source=qa-found。"""
        proc = _run_new_bug(
            tmp_path,
            ["BUG-T001", "M1-basic", "/api/health", "L2", "evidence"],
        )
        assert proc.returncode == 0, f"exit={proc.returncode}: {proc.stdout}\n{proc.stderr}"
        content = _find_bug_file(tmp_path, "BUG-T001").read_text(encoding="utf-8")
        _assert_source(content, "qa-found")

    def test_user_feedback_source(self, tmp_path):
        """PASS:--source user-feedback → 第 7 字段 = user-feedback。"""
        proc = _run_new_bug(
            tmp_path,
            ["BUG-T002", "M2-auth", "/login", "L1", "500 on login",
             "--source", "user-feedback"],
        )
        assert proc.returncode == 0, f"exit={proc.returncode}: {proc.stdout}\n{proc.stderr}"
        content = _find_bug_file(tmp_path, "BUG-T002").read_text(encoding="utf-8")
        _assert_source(content, "user-feedback")

    def test_scan_source(self, tmp_path):
        """PASS:--source scan → 第 7 字段 = scan。"""
        proc = _run_new_bug(
            tmp_path,
            ["BUG-T003", "M3-asset", "/asset-hub", "L3", "css missing",
             "--source", "scan"],
        )
        assert proc.returncode == 0, f"exit={proc.returncode}: {proc.stdout}\n{proc.stderr}"
        content = _find_bug_file(tmp_path, "BUG-T003").read_text(encoding="utf-8")
        _assert_source(content, "scan")

    def test_illegal_source_rejected(self, tmp_path):
        """FAIL:非法 source 值 → 脚本拒绝（exit ≠ 0）+ 报错信息含 source。"""
        proc = _run_new_bug(
            tmp_path,
            ["BUG-T004", "M1-basic", "/api/x", "L2", "ev", "--source", "illegal"],
        )
        assert proc.returncode != 0, f"期望拒绝, 实际 exit=0: {proc.stdout}"
        assert "source" in proc.stderr, f"stderr 应含 source 报错: {proc.stderr}"
