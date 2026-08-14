"""
tests/unit/test_skill_verify_upgrade.py
对 skill-acceptance/scripts/verify.py §4 升级(新增 intent + smoke + total_score)
的反例自验收(沿用 agent-dev-control-kit §11.1.3)。

覆盖维度:
  - intent 检查:缺 intent / 缺 category / 缺 audience / 全缺 / 全有
  - smoke 检查:scripts/*.py 语法错误 → BLOCK
  - total_score:8 维总分汇总存在,值为 0-100 整数

每个反例用 tmp 目录隔离,不污染真实仓库。
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY = REPO_ROOT / "skill-markets" / "skill-acceptance" / "scripts" / "verify.py"


def run_verify(skill_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VERIFY), "--target", str(skill_path), "--new-skill", "--json"],
        capture_output=True, text=True, timeout=60,
    )


def test_intent_all_missing_blocks(tmp_path):
    """intent / category / audience 全缺 → BLOCK(score=0)。"""
    sp = tmp_path / "fake"
    sp.mkdir()
    (sp / "SKILL.md").write_text(
        "---\nname: fake\ndescription: test\n---\n# fake\n",
        encoding="utf-8",
    )
    r = run_verify(sp)
    assert r.returncode == 4  # BLOCK
    payload = json.loads(r.stdout)
    intent = next(c for c in payload["checks"] if c["id"] == "intent")
    assert intent["status"] == "BLOCK"
    assert intent["score"] == 0
    assert "INTENT_MISSING" in str(intent["issues"])
    assert "CATEGORY_MISSING" in str(intent["issues"])
    assert "AUDIENCE_MISSING" in str(intent["issues"])


def test_intent_partial_filled(tmp_path):
    """intent 有,category 缺 → intent 仍 BLOCK。"""
    sp = tmp_path / "fake"
    sp.mkdir()
    (sp / "SKILL.md").write_text(
        "---\nname: fake\ndescription: test\nintent: 做某事\naudience: [developer]\n---\n# fake\n",
        encoding="utf-8",
    )
    r = run_verify(sp)
    payload = json.loads(r.stdout)
    intent = next(c for c in payload["checks"] if c["id"] == "intent")
    assert intent["status"] == "BLOCK"
    codes = [i["code"] for i in intent["issues"]]
    assert "CATEGORY_MISSING" in codes
    assert "INTENT_MISSING" not in codes
    assert "AUDIENCE_MISSING" not in codes


def test_intent_all_filled_passes(tmp_path):
    """3 字段全有 → intent PASS。"""
    sp = tmp_path / "fake"
    sp.mkdir()
    (sp / "SKILL.md").write_text(
        "---\nname: fake\ndescription: test\n"
        "intent: 做某事\ncategory: cli\naudience: [developer]\n---\n# fake\n",
        encoding="utf-8",
    )
    r = run_verify(sp)
    payload = json.loads(r.stdout)
    intent = next(c for c in payload["checks"] if c["id"] == "intent")
    assert intent["status"] == "PASS"
    assert intent["score"] == 100


def test_smoke_python_syntax_error_blocks(tmp_path):
    """scripts/foo.py 有语法错误 → smoke BLOCK。"""
    sp = tmp_path / "fake"
    sp.mkdir()
    (sp / "SKILL.md").write_text(
        "---\nname: fake\ndescription: test\nintent: 做某事\ncategory: cli\naudience: [developer]\n---\n# fake\n",
        encoding="utf-8",
    )
    scripts = sp / "scripts"
    scripts.mkdir()
    # 故意写语法错
    (scripts / "broken.py").write_text("def foo(:\n    pass\n", encoding="utf-8")
    r = run_verify(sp)
    payload = json.loads(r.stdout)
    smoke = next(c for c in payload["checks"] if c["id"] == "smoke")
    assert smoke["status"] == "BLOCK"
    codes = [i["code"] for i in smoke["issues"]]
    assert "SMOKE_SYNTAX_FAIL" in codes
    assert "broken.py" in str(smoke["issues"])


def test_smoke_clean_python_passes(tmp_path):
    """scripts/foo.py 语法正确 → smoke PASS。"""
    sp = tmp_path / "fake"
    sp.mkdir()
    (sp / "SKILL.md").write_text(
        "---\nname: fake\ndescription: test\nintent: 做某事\ncategory: cli\naudience: [developer]\n---\n# fake\n",
        encoding="utf-8",
    )
    scripts = sp / "scripts"
    scripts.mkdir()
    (scripts / "ok.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
    r = run_verify(sp)
    payload = json.loads(r.stdout)
    smoke = next(c for c in payload["checks"] if c["id"] == "smoke")
    assert smoke["status"] == "PASS"
    assert "tested=1" in smoke["note"]


def test_smoke_no_scripts_dir_passes(tmp_path):
    """无 scripts/ 目录 → smoke PASS(100 分),note 提示跳过。"""
    sp = tmp_path / "fake"
    sp.mkdir()
    (sp / "SKILL.md").write_text(
        "---\nname: fake\ndescription: test\nintent: 做某事\ncategory: cli\naudience: [developer]\n---\n# fake\n",
        encoding="utf-8",
    )
    r = run_verify(sp)
    payload = json.loads(r.stdout)
    smoke = next(c for c in payload["checks"] if c["id"] == "smoke")
    assert smoke["status"] == "PASS"
    assert "跳过" in smoke["note"]


def test_total_score_present(tmp_path):
    """总分 total_score 字段存在且为 0-100 整数。"""
    sp = tmp_path / "fake"
    sp.mkdir()
    (sp / "SKILL.md").write_text(
        "---\nname: fake\ndescription: test\nintent: 做某事\ncategory: cli\naudience: [developer]\n---\n# fake\n",
        encoding="utf-8",
    )
    r = run_verify(sp)
    payload = json.loads(r.stdout)
    assert "total_score" in payload
    s = payload["total_score"]
    assert isinstance(s, int) and 0 <= s <= 100
    # summary 里也有
    assert payload["summary"]["total_score"] == s
    assert "min_score" in payload["summary"]