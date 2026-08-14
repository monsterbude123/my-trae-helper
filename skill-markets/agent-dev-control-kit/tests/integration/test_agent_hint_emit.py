"""tests/integration/test_agent_hint_emit.py — agent-hint-emit.py 自验收
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

SKILL_ROOT = Path(__file__).resolve().parents[2]
HINT_LOG = SKILL_ROOT / "logs" / "agent-hints.jsonl"
EMIT_SCRIPT = SKILL_ROOT / "scripts" / "agent-hint-emit.py"


def _run(*args: str) -> tuple[int, str, str]:
    r = subprocess.run(
        [sys.executable, str(EMIT_SCRIPT), *args],
        cwd=str(SKILL_ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    return r.returncode, r.stdout, r.stderr


def _seed_hints(records: list[dict]) -> None:
    HINT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with HINT_LOG.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


@pytest.fixture(autouse=True)
def _isolate_hints():
    """隔离 logs/agent-hints.jsonl,测试完恢复。"""
    backup = None
    if HINT_LOG.is_file():
        backup = SKILL_LOG_BACKUP = SKILL_ROOT / "logs" / "agent-hints.test.bak.jsonl"
        backup.write_text(HINT_LOG.read_text(encoding="utf-8"), encoding="utf-8")
    yield
    if backup and backup.is_file():
        backup.unlink()
    if HINT_LOG.is_file():
        HINT_LOG.unlink()


@pytest.mark.trap
def test_empty_state_reports_nothing():
    rc, stdout, _ = _run()
    assert rc == 0
    assert "当前无 hints" in stdout


@pytest.mark.trap
def test_per_hint_render_lists_each_record():
    """happy-path:有 hints 时,逐条打印 + 含核心字段。"""
    _seed_hints([
        {
            "id": "HINT-AP-2-demo",
            "timestamp": "2026-08-14T00:00:00+08:00",
            "trap_id": "AP-2",
            "severity": "HIGH",
            "what": "缺 lint 脚本",
            "where": "package.json",
            "minimal_fix": ["加 lint 命令", "跑 install-husky"],
            "next_skill": "trae-ponytail",
            "next_skill_action": "补命令",
            "see_also": ["references/traps.md §AP-2"],
            "extra": {},
        },
    ])
    rc, stdout, _ = _run()
    assert rc == 0
    assert "AP-2" in stdout
    assert "缺 lint 脚本" in stdout
    assert "trae-ponytail" in stdout


@pytest.mark.trap
def test_group_by_trap_collapses_same_id():
    """分组模式:同 trap_id 折叠。"""
    _seed_hints([
        {
            "id": "HINT-AP-2-a",
            "timestamp": "2026-08-14T00:00:00+08:00",
            "trap_id": "AP-2",
            "severity": "HIGH",
            "what": "缺 lint",
            "where": "a",
            "minimal_fix": [],
            "next_skill": "",
            "next_skill_action": "",
            "see_also": [],
            "extra": {},
        },
        {
            "id": "HINT-AP-2-b",
            "timestamp": "2026-08-14T00:00:00+08:00",
            "trap_id": "AP-2",
            "severity": "HIGH",
            "what": "缺 typecheck",
            "where": "b",
            "minimal_fix": [],
            "next_skill": "",
            "next_skill_action": "",
            "see_also": [],
            "extra": {},
        },
        {
            "id": "HINT-AP-3-a",
            "timestamp": "2026-08-14T00:00:00+08:00",
            "trap_id": "AP-3",
            "severity": "HIGH",
            "what": "缺 main",
            "where": "c",
            "minimal_fix": [],
            "next_skill": "",
            "next_skill_action": "",
            "see_also": [],
            "extra": {},
        },
    ])
    rc, stdout, _ = _run("--group-by", "trap")
    assert rc == 0
    # 应当按 trap 分两段
    assert "AP-2 (2 条)" in stdout
    assert "AP-3 (1 条)" in stdout


@pytest.mark.trap
def test_json_output_is_valid():
    """--json 输出能被 json.loads 解析。"""
    _seed_hints([
        {
            "id": "HINT-DEMO",
            "timestamp": "2026-08-14T00:00:00+08:00",
            "trap_id": "DEMO",
            "severity": "MEDIUM",
            "what": "demo",
            "where": "x",
            "minimal_fix": [],
            "next_skill": "",
            "next_skill_action": "",
            "see_also": [],
            "extra": {},
        },
    ])
    rc, stdout, _ = _run("--json")
    assert rc == 0
    parsed = json.loads(stdout)
    assert isinstance(parsed, list)
    assert parsed[0]["trap_id"] == "DEMO"


@pytest.mark.trap
def test_reset_clears_log():
    _seed_hints([
        {
            "id": "HINT-X",
            "timestamp": "2026-08-14T00:00:00+08:00",
            "trap_id": "X",
            "severity": "HIGH",
            "what": "x",
            "where": "x",
            "minimal_fix": [],
            "next_skill": "",
            "next_skill_action": "",
            "see_also": [],
            "extra": {},
        },
    ])
    assert HINT_LOG.is_file()
    rc, stdout, _ = _run("--reset")
    assert rc == 0
    assert not HINT_LOG.is_file()
