"""tests/integration/test_catalog_guard.py — §11.1.1 Gate 自验收

catalog-guard 是新写的 Gate,必须用真反例跑自验收:
  - 故意造违规 catalog → catalog-guard exit != 0 + stderr 含 HINT-
  - happy-path → exit 0 + ✅

§11.1.1 强制:每个 trap 测试必须**可靠复原 catalog**。修复点:
  - backup 写到 tmp_path(隔离)
  - finally 用 filecmp 校验实际复原
  - 若不一致 → pytest.fail 强报错(不让测试"假通过")
"""
from __future__ import annotations

import filecmp
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SKILL_ROOT = Path(__file__).resolve().parents[2]
GUARD_SCRIPT = SKILL_ROOT / "scripts" / "catalog-guard.py"
REAL_CATALOG = SKILL_ROOT / "tests" / "catalogs" / "skill-catalog.yaml"


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


def _restore_catalog(backup: Path, *, original_text: str) -> None:
    """还原 catalog,跨盘符用 shutil.copy + remove(Windows 兼容)。

    策略:同盘用 os.replace(原子),跨盘用 shutil.copy(Windows 上 os.replace 抛 WinError 17)。
    最后 filecmp 校验 — 不一致就 pytest.fail 强报错。
    """
    tmp = backup.with_suffix(".restore.tmp")
    tmp.write_text(original_text, encoding="utf-8")
    try:
        os.replace(tmp, REAL_CATALOG)
    except OSError:
        # 跨盘符(Windows):fallback 到 copy + unlink
        import shutil
        shutil.copy(str(tmp), str(REAL_CATALOG))
        tmp.unlink(missing_ok=True)
    if not filecmp.cmp(REAL_CATALOG, backup, shallow=False):
        pytest.fail(
            f"catalog 复原失败,期望等于 backup({backup});"
            f"实际内容可能已被并发进程破坏"
        )


@pytest.mark.trap
def test_catalog_guard_runs_clean_in_default_state():
    """happy-path:现状 catalog 应通过。"""
    rc, _, _ = _run_guard()
    assert rc == 0, "干净状态必须 exit 0"


@pytest.mark.trap
def test_catalog_guard_blocks_on_violation(tmp_path: Path):
    """AP-CAT 反例:故意造一个'缺文档'的 catalog → guard 必须阻断。"""
    backup = tmp_path / "catalog.bak.yaml"
    original_text = REAL_CATALOG.read_text(encoding="utf-8")
    backup.write_text(original_text, encoding="utf-8")
    try:
        bad = yaml.safe_load(original_text) or {}
        bad.setdefault("required_docs", []).append(
            {
                "path": "DOES_NOT_EXIST_SENTINEL_zzz.md",
                "purpose": "反例自验收用",
                "must_contain": ["X"],
            }
        )
        REAL_CATALOG.write_text(
            yaml.safe_dump(bad, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        rc, _, stderr = _run_guard()
        assert rc != 0, "违规 catalog 必须阻断"
        assert "DOES_NOT_EXIST_SENTINEL_zzz.md" in stderr or "AP-CAT" in stderr
    finally:
        _restore_catalog(backup, original_text=original_text)


@pytest.mark.trap
def test_catalog_guard_emits_block_banner(tmp_path: Path):
    """§11.1.4:Gate 失败必须显眼提示。"""
    backup = tmp_path / "catalog.bak2.yaml"
    original_text = REAL_CATALOG.read_text(encoding="utf-8")
    backup.write_text(original_text, encoding="utf-8")
    try:
        bad = yaml.safe_load(original_text) or {}
        bad.setdefault("required_sections", []).append(
            {
                "in_file": "DOES_NOT_EXIST_SENTINEL_xxx.md",
                "level": 2,
                "heading": "fake section",
                "purpose": "block banner test",
            }
        )
        REAL_CATALOG.write_text(
            yaml.safe_dump(bad, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        rc, _, stderr = _run_guard()
        assert rc != 0
        assert "🛑 CATALOG GUARD 阻断 commit" in stderr, "必须输出 banner"

        hint_log = SKILL_ROOT / "logs" / "agent-hints.jsonl"
        if hint_log.is_file():
            data = [
                json.loads(line)
                for line in hint_log.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            assert any("AP-CAT" in h.get("trap_id", "") for h in data)
    finally:
        _restore_catalog(backup, original_text=original_text)