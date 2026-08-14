"""tests/integration/test_catalog_guard.py — §11.1.1 Gate 自验收

catalog-guard 是新写的 Gate,必须用真反例跑自验收:
  - 故意造违规 catalog → catalog-guard exit != 0 + stderr 含 HINT-
  - happy-path → exit 0 + ✅
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parents[2]
GUARD_SCRIPT = SKILL_ROOT / "scripts" / "catalog-guard.py"


def _run_guard() -> tuple[int, str, str]:
    r = subprocess.run(
        [sys.executable, str(GUARD_SCRIPT)],
        cwd=str(SKILL_ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    return r.returncode, r.stdout, r.stderr


@pytest.mark.trap
def test_catalog_guard_runs_clean_in_default_state():
    """happy-path:现状 catalog 应通过。"""
    rc, _, _ = _run_guard()
    assert rc == 0, "干净状态必须 exit 0"


@pytest.mark.trap
def test_catalog_guard_blocks_on_violation(tmp_path: Path, monkeypatch):
    """AP-CAT 反例:故意造一个'缺文档'的 catalog → guard 必须阻断。"""
    # 把 catalog 临时备份
    real_catalog = SKILL_ROOT / "tests" / "catalogs" / "skill-catalog.yaml"
    backup = tmp_path / "catalog.bak.yaml"
    backup.write_text(real_catalog.read_text(encoding="utf-8"), encoding="utf-8")
    try:
        # 注入:声明一个不存在的文档路径
        bad = yaml.safe_load(backup.read_text(encoding="utf-8")) or {}
        bad.setdefault("required_docs", []).append(
            {
                "path": "DOES_NOT_EXIST_SENTINEL_zzz.md",
                "purpose": "反例自验收用",
                "must_contain": ["X"],
            }
        )
        real_catalog.write_text(
            yaml.safe_dump(bad, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        rc, _, stderr = _run_guard()
        assert rc != 0, "违规 catalog 必须阻断"
        assert "DOES_NOT_EXIST_SENTINEL_zzz.md" in stderr or "AP-CAT" in stderr
    finally:
        # 恢复原 catalog
        real_catalog.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")


@pytest.mark.trap
def test_catalog_guard_emits_block_banner(tmp_path: Path):
    """§11.1.4:Gate 失败必须显眼提示,不能"自动回滚"却无日志。"""
    real_catalog = SKILL_ROOT / "tests" / "catalogs" / "skill-catalog.yaml"
    backup = tmp_path / "catalog.bak.yaml"
    backup.write_text(real_catalog.read_text(encoding="utf-8"), encoding="utf-8")
    try:
        bad = yaml.safe_load(backup.read_text(encoding="utf-8")) or {}
        bad.setdefault("required_sections", []).append(
            {
                "in_file": "DOES_NOT_EXIST_SENTINEL_xxx.md",
                "level": 2,
                "heading": "fake section",
                "purpose": "block banner test",
            }
        )
        real_catalog.write_text(
            yaml.safe_dump(bad, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        rc, _, stderr = _run_guard()
        assert rc != 0
        assert "🛑 CATALOG GUARD 阻断 commit" in stderr, "必须输出 banner"

        # 确认 hint 日志被写入
        hint_log = SKILL_ROOT / "logs" / "agent-hints.jsonl"
        if hint_log.is_file():
            data = [
                json.loads(line)
                for line in hint_log.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            assert any("AP-CAT" in h.get("trap_id", "") for h in data)
    finally:
        real_catalog.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")


# 用法定义(顶部 import 没 yaml,这里补)
import yaml  # noqa: E402
