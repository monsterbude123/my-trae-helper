"""V11.8.5 GitNexus First 覆盖度测试。

> 验证 5 个 P0 stage（04-spec / 06-contract / 09-review / 10-rot-scan / 12-bug-fix）
> 必含 gitnexus4Trae 依赖 + GitNexus First 铁律 + 必跑调用点。

蒸馏自 2026-08-15 用户反馈：bug 修复流程 agent 几乎不用 gitnexus。
所有用例 <50ms，纯文件系统断言。
"""
from __future__ import annotations

from pathlib import Path

import pytest

# 5 个 P0 stage 必须使用 gitnexus
P0_STAGES = [
    "04-spec",
    "06-contract",
    "09-review",
    "10-rot-scan",
    "12-bug-fix",
]


def _read_stage_skill(skill_root: Path, stage: str) -> str:
    return (skill_root / f"skills/{stage}/SKILL.md").read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────────────
# 1. depends_on.skills 必须含 gitnexus4Trae
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("stage", P0_STAGES)
def test_p0_stage_depends_on_gitnexus(skill_root: Path, stage: str):
    """P0 stage depends_on.skills 必含 gitnexus4Trae。"""
    content = _read_stage_skill(skill_root, stage)
    assert "gitnexus4Trae" in content, f"Stage {stage} depends_on 缺 gitnexus4Trae"


# ─────────────────────────────────────────────────────────────────
# 2. 必含 GitNexus First 铁律
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("stage", P0_STAGES)
def test_p0_stage_has_gitnexus_first_rule(skill_root: Path, stage: str):
    """P0 stage 必含 GitNexus First 铁律（V11.8.5 NEW）。"""
    content = _read_stage_skill(skill_root, stage)
    assert "GITNEXUS FIRST" in content, f"Stage {stage} 缺 GitNexus First 铁律"
    assert "V11.8.5" in content, f"Stage {stage} 缺 V11.8.5 版本标记"


# ─────────────────────────────────────────────────────────────────
# 3. 骨架流程必含 GitNexus 调用步骤
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("stage,marker", [
    ("04-spec", "GitNexus 影响面评估"),
    ("06-contract", "GitNexus 上下游评估"),
    ("09-review", "GitNexus 变更范围评估"),
    ("10-rot-scan", "GitNexus 知识图谱评估"),
    ("12-bug-fix", "GitNexus 影响面评估"),
])
def test_p0_stage_has_gitnexus_step(skill_root: Path, stage: str, marker: str):
    """P0 stage 骨架流程必含 GitNexus 调用步骤。"""
    content = _read_stage_skill(skill_root, stage)
    assert marker in content, f"Stage {stage} 缺 {marker} 步骤"


# ─────────────────────────────────────────────────────────────────
# 4. 必含具体 GitNexus 工具调用名
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("stage,tools", [
    ("04-spec", ["impact", "context"]),
    ("06-contract", ["impact", "context"]),
    ("09-review", ["detect_changes", "impact"]),
    ("10-rot-scan", ["query", "impact"]),
    ("12-bug-fix", ["impact", "context", "query"]),
])
def test_p0_stage_specifies_gitnexus_tools(skill_root: Path, stage: str, tools: list):
    """P0 stage 必含具体 GitNexus 工具调用名（不可笼统说"用 gitnexus"）。"""
    content = _read_stage_skill(skill_root, stage)
    for tool in tools:
        assert f"gitnexus__{tool}" in content or f"GitNexus {tool}" in content, (
            f"Stage {stage} 缺 gitnexus__{tool} 调用"
        )


# ─────────────────────────────────────────────────────────────────
# 5. 必含反 grep 声明（Article V 不可降级）
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("stage", P0_STAGES)
def test_p0_stage_declares_no_grep_replacement(skill_root: Path, stage: str):
    """P0 stage 必声明"禁止 grep/Glob 替代 GitNexus"。"""
    content = _read_stage_skill(skill_root, stage)
    assert "grep" in content.lower() or "替代" in content, (
        f"Stage {stage} 缺反 grep/替代 声明"
    )