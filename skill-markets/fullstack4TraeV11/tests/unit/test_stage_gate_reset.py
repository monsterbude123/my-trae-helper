"""stage-gate.py --reset-to 子命令(V12 §2.1 重置协议)单测。

覆盖维度(对齐 V11.8.6 P0-v12-physical-rollout §6):
  #1 PASS:完整 v12-preview 项目 --reset-to 3/implement → 清 stage/4+ 后目录,保留 fact/ + stage/{0..3}/
  #2 PASS:边界 --reset-to 5/accept → 不删任何(已是最终 stage)
  #3 FAIL:target_stage 非法(不在 11 stage 顺序内)
  #4 FAIL:--reset-to 必须用 change 级状态卡(.state-card.md 在 docs/specs/changes/{id}/ 下),项目级 docs/specs/.state-card.md 拒绝
  #5 FAIL:change 目录不存在
  #6 PASS:--reset-to 重置当前 stage 状态卡内容(stage_status=pending + reset_at)
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "stage-gate.py"
)


def _load_sg():
    """动态加载 stage-gate.py(无 conftest 依赖)。"""
    spec = importlib.util.spec_from_file_location("stage_gate_reset", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["stage_gate_reset"] = mod
    spec.loader.exec_module(mod)
    return mod


# ============================================================================
# 工具:构造完整 v12-preview 项目骨架
# ============================================================================


def _build_v12_project(tmp_path: Path, change_id: str = "test-change") -> Path:
    """在 tmp_path 下建完整 v12-preview 骨架。

    包含:
      docs/specs/changes/{change_id}/
      ├── fact/{spec,plan,test-plan,prototype}.md
      ├── stage/
      │   ├── -1/intake/...     (含 handoff-out.md)
      │   ├── 0/plan/...
      │   ├── 0.5/test-plan/...
      │   ├── 1/spec/...
      │   ├── 1.5/prototype/...
      │   ├── 2/contract/...
      │   ├── 3/implement/{.state-card.md, backend-impl-notes.md, handoff-out.md}
      │   ├── 3.5/real-verify/...
      │   ├── 4/review/...
      │   ├── 4.5/rot-scan/...
      │   └── 5/accept/...
      └── archive/README.md
    """
    change_dir = tmp_path / "docs" / "specs" / "changes" / change_id
    (change_dir / "fact").mkdir(parents=True)
    for f in ["spec.md", "plan.md", "test-plan.md", "prototype.md"]:
        (change_dir / "fact" / f).write_text(f"# {f}\n", encoding="utf-8")

    # stage/ 11 个子目录(用 -1/intake 命名格式,与 V12 §1 对齐)
    stage_dir = change_dir / "stage"
    for sub in [
        "-1/intake", "0/plan", "0.5/test-plan", "1/spec", "1.5/prototype",
        "2/contract", "3/implement", "3.5/real-verify", "4/review",
        "4.5/rot-scan", "5/accept",
    ]:
        sub_dir = stage_dir / sub
        sub_dir.mkdir(parents=True)
        # Stage 3 加 .state-card.md + impl 笔记 + handoff-out
        if sub == "3/implement":
            (sub_dir / ".state-card.md").write_text(
                "---\ncurrent_stage: 3/implement\nstage_status: completed\n---\n",
                encoding="utf-8",
            )
            (sub_dir / "backend-impl-notes.md").write_text("# backend impl\n", encoding="utf-8")
            (sub_dir / "handoff-out.md").write_text("# handoff\n", encoding="utf-8")
        else:
            (sub_dir / "README.md").write_text(f"# {sub}\n", encoding="utf-8")
            (sub_dir / "notes.md").write_text(f"# {sub} notes\n", encoding="utf-8")
            (sub_dir / "handoff-out.md").write_text(f"# {sub} handoff\n", encoding="utf-8")

    # archive/
    (change_dir / "archive").mkdir()
    (change_dir / "archive" / "README.md").write_text("# archive\n", encoding="utf-8")

    return change_dir


def _write_state_card(change_dir: Path) -> Path:
    """在 change_dir 下写 .state-card.md(v12-preview change 级)。"""
    card = change_dir / ".state-card.md"
    card.write_text(
        """---
card_type: change
card_id: test-change
current_stage: 3/implement
stage_status: working
health: "🟢 on-track"
gate_result:
  status: PENDING
next_stage: {}
blocked_by: null
actor: test
duration_minutes: 0
notes: ""
updated_at: 2026-08-16T00:00:00
updated_by: test
artifacts: []
version: "1.0.0"
stage_started_at: 2026-08-16T00:00:00
stage_ended_at: null
visual_evidence:
  status: unverified
  screenshots: []
  verified_at: null
---
""",
        encoding="utf-8",
    )
    return card


def _invoke_sg(args, cwd: Path) -> tuple[int, str, str]:
    """以子进程跑 stage-gate.py,捕获 (returncode, stdout, stderr)。"""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


# ============================================================================
# #1 PASS: --reset-to 3/implement → 删 stage/4*/ 后,保留 fact + stage/{..3}/
# ============================================================================


def test_reset_to_3_implement_passes(tmp_path):
    """v12-preview 完整项目 --reset-to 3/implement 应:
      - exit 0
      - 删除 stage/3.5/real-verify, stage/4/review, stage/4.5/rot-scan, stage/5/accept
      - 保留 fact/ 整个目录(文件内容不变)
      - 保留 stage/{-1/intake, 0/plan, 0.5/test-plan, 1/spec, 1.5/prototype, 2/contract, 3/implement}
      - 保留 archive/
      - 重置 stage/3/implement/.state-card.md 为 pending
    """
    change_dir = _build_v12_project(tmp_path, change_id="reset-3-test")
    state_card = _write_state_card(change_dir)

    # 记录 fact/spec.md 原内容
    original_spec = (change_dir / "fact" / "spec.md").read_text(encoding="utf-8")

    rc, out, err = _invoke_sg(
        [
            "--state-card", str(state_card),
            "--reset-to", "3/implement",
        ],
        cwd=tmp_path,
    )

    assert rc == 0, f"--reset-to exit {rc}, stderr={err}"

    # fact/ 保留
    assert (change_dir / "fact" / "spec.md").read_text(encoding="utf-8") == original_spec

    # stage/3.5 ~ stage/5/accept 已删
    for gone in [
        "stage/3.5/real-verify",
        "stage/4/review",
        "stage/4.5/rot-scan",
        "stage/5/accept",
    ]:
        assert not (change_dir / gone).exists(), f"{gone} 应已被删除"

    # stage/{-1..3}/ 保留
    for kept in [
        "stage/-1/intake",
        "stage/0/plan",
        "stage/0.5/test-plan",
        "stage/1/spec",
        "stage/1.5/prototype",
        "stage/2/contract",
        "stage/3/implement",
    ]:
        assert (change_dir / kept).exists(), f"{kept} 应保留"

    # archive/ 保留
    assert (change_dir / "archive").exists()

    # stage/3/implement/.state-card.md 重置为 pending
    sc = change_dir / "stage" / "3" / "implement" / ".state-card.md"
    sc_text = sc.read_text(encoding="utf-8")
    assert "stage_status: pending" in sc_text
    assert "reset_at:" in sc_text
    assert "reset_by: stage-gate.py --reset-to 3/implement" in sc_text


# ============================================================================
# #2 PASS: 边界 --reset-to 5/accept → 不删任何 stage(已是最终)
# ============================================================================


def test_reset_to_5_accept_boundary(tmp_path):
    """--reset-to 5/accept(最终 stage)应:不删任何 stage/ 子目录。"""
    change_dir = _build_v12_project(tmp_path, change_id="reset-5-test")
    state_card = _write_state_card(change_dir)

    rc, out, err = _invoke_sg(
        ["--state-card", str(state_card), "--reset-to", "5/accept"],
        cwd=tmp_path,
    )

    assert rc == 0, f"边界 --reset-to 5/accept exit {rc}, stderr={err}"
    # 11 个 stage 子目录都保留
    for kept in [
        "stage/-1/intake", "stage/0/plan", "stage/0.5/test-plan", "stage/1/spec",
        "stage/1.5/prototype", "stage/2/contract", "stage/3/implement",
        "stage/3.5/real-verify", "stage/4/review", "stage/4.5/rot-scan",
        "stage/5/accept",
    ]:
        assert (change_dir / kept).exists(), f"{kept} 应保留"


# ============================================================================
# #3 FAIL: target_stage 非法
# ============================================================================


def test_reset_to_invalid_stage_fails(tmp_path):
    """target_stage=99/notexist 应 exit 1。"""
    change_dir = _build_v12_project(tmp_path, change_id="reset-invalid-test")
    state_card = _write_state_card(change_dir)

    rc, out, err = _invoke_sg(
        ["--state-card", str(state_card), "--reset-to", "99/notexist"],
        cwd=tmp_path,
    )

    assert rc == 1, f"非法 stage 应 exit 1,实际 {rc}"
    assert "99/notexist" in err or "不在 V12 stage 顺序内" in err


# ============================================================================
# #4 FAIL: --reset-to 必须用 change 级状态卡,项目级 docs/specs/.state-card.md 拒绝
# ============================================================================


def test_reset_to_with_project_level_card_fails(tmp_path):
    """--reset-to 项目级 docs/specs/.state-card.md 应 exit 1。"""
    # 建项目级状态卡(.state-card.md 在 docs/specs/ 下,父目录名 = specs)
    docs_specs = tmp_path / "docs" / "specs"
    docs_specs.mkdir(parents=True)
    project_card = docs_specs / ".state-card.md"
    project_card.write_text(
        "---\ncurrent_stage: 0/plan\nstage_status: working\n---\n",
        encoding="utf-8",
    )

    rc, out, err = _invoke_sg(
        ["--state-card", str(project_card), "--reset-to", "3/implement"],
        cwd=tmp_path,
    )

    assert rc == 1, f"项目级卡 + --reset-to 应 exit 1,实际 {rc}"
    assert "必须用 change 级状态卡" in err or "changes" in err


# ============================================================================
# #5 FAIL: change 目录不存在
# ============================================================================


def test_reset_to_with_nonexistent_change_fails(tmp_path):
    """--state-card 指向不存在的 change 目录应 exit 1。"""
    fake_card = tmp_path / "docs" / "specs" / "changes" / "ghost" / ".state-card.md"
    fake_card.parent.mkdir(parents=True)
    fake_card.write_text("---\n", encoding="utf-8")  # 空 state-card

    rc, out, err = _invoke_sg(
        ["--state-card", str(fake_card), "--reset-to", "3/implement"],
        cwd=tmp_path,
    )

    # 因 .state-card.md 已存在但 parse 失败 → 走 error 分支,exit 1
    assert rc == 1, f"应 exit 1,实际 {rc}"


# ============================================================================
# #6 PASS: --reset-to 重置当前 stage 状态卡内容(关键 content 校验)
# ============================================================================


def test_reset_to_updates_state_card_content(tmp_path):
    """--reset-to 后 stage/{target}/.state-card.md 内容应含 stage_status: pending + reset_at + reset_by。"""
    change_dir = _build_v12_project(tmp_path, change_id="reset-content-test")
    state_card = _write_state_card(change_dir)

    # 记录原始状态卡内容
    sc_before = (
        (change_dir / "stage" / "3" / "implement" / ".state-card.md")
        .read_text(encoding="utf-8")
    )
    assert "stage_status: completed" in sc_before

    rc, out, err = _invoke_sg(
        ["--state-card", str(state_card), "--reset-to", "3/implement"],
        cwd=tmp_path,
    )
    assert rc == 0

    sc_after = (
        (change_dir / "stage" / "3" / "implement" / ".state-card.md")
        .read_text(encoding="utf-8")
    )
    assert "stage_status: pending" in sc_after
    assert "reset_at:" in sc_after
    assert "current_stage: 3/implement" in sc_after


# ============================================================================
# #7 PASS: --reset-to 在 V12_STAGE_ORDER 顺序正确(v11-default project 不阻塞)
# ============================================================================


def test_cmd_reset_to_unit(tmp_path):
    """直接调用 cmd_reset_to 函数(单测,不走子进程)。"""
    sg = _load_sg()
    change_dir = _build_v12_project(tmp_path, change_id="unit-test")
    state_card = _write_state_card(change_card := change_dir)

    rc = sg.cmd_reset_to(change_dir, "2/contract")
    assert rc == 0

    # stage/3+, 4+, 5+ 全删
    for gone in [
        "stage/3/implement", "stage/3.5/real-verify", "stage/4/review",
        "stage/4.5/rot-scan", "stage/5/accept",
    ]:
        assert not (change_dir / gone).exists()

    # stage/{-1..2}/ 保留
    for kept in [
        "stage/-1/intake", "stage/0/plan", "stage/0.5/test-plan", "stage/1/spec",
        "stage/1.5/prototype", "stage/2/contract",
    ]:
        assert (change_dir / kept).exists()