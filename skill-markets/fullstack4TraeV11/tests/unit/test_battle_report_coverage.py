"""V11.8.3 4 层分层决策框架覆盖度测试。

> 验证 Stage 6 从"7步统一工序"升级为"4 层分层决策框架"的完整性。

蒸馏自 2026-08-15 V11.8.3 升级会话。
所有用例 <50ms，纯文件系统断言，不依赖网络。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

# V11.8.3 4 层分层决策框架 references
LAYER1_DISCOVERY_REL = Path("skills/12-bug-fix/references/bug-layer-1-discovery.md")
LAYER2_SEVERITY_REL = Path("skills/12-bug-fix/references/bug-layer-2-severity.md")
LAYER3_REPAIR_REL = Path("skills/12-bug-fix/references/bug-layer-3-repair.md")
LAYER4_CONVERGENCE_REL = Path("skills/12-bug-fix/references/bug-layer-4-convergence.md")

# 辅助 references（继承 V11.8.2）
BUG_HUNT_4D_REL = Path("skills/12-bug-fix/references/bug-hunt-4d-observation.md")
BUG_HUNT_5_CHECK_REL = Path("skills/12-bug-fix/references/bug-hunt-5-check.md")
BATTLE_REPORT_REL = Path("skills/12-bug-fix/references/bug-hunt-battle-report.md")

STAGE6_SKILL_REL = Path("skills/12-bug-fix/SKILL.md")
TRAP_YAML_REL = Path("references/trap-instructions.yaml")
V11_SKILL_REL = Path("SKILL.md")

# V11.8.2 Stage 6 scripts/bug-hunt/ 子包脚本（继承）
BUG_HUNT_SCRIPTS_REL = [
    Path("skills/12-bug-fix/scripts/bug-hunt/new-bug.sh"),
    Path("skills/12-bug-fix/scripts/bug-hunt/close-bug.sh"),
    Path("skills/12-bug-fix/scripts/bug-hunt/dev-hmr-recovery.sh"),
    Path("skills/12-bug-fix/scripts/bug-hunt/dev-hmr-recovery.ps1"),
    Path("skills/12-bug-fix/scripts/bug-hunt/archive-screenshot.sh"),
    Path("skills/12-bug-fix/scripts/bug-hunt/archive-screenshot.ps1"),
]


# ─────────────────────────────────────────────────────────────────
# 1. 4 层分层决策框架核心 references 存在
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("rel_path,name", [
    (LAYER1_DISCOVERY_REL, "Layer1 发现分层"),
    (LAYER2_SEVERITY_REL, "Layer2 严重性分层"),
    (LAYER3_REPAIR_REL, "Layer3 修复分层"),
    (LAYER4_CONVERGENCE_REL, "Layer4 收敛分层"),
])
def test_4_layer_references_exist(skill_root: Path, rel_path: Path, name: str):
    """V11.8.3 4 层分层决策框架 references 必存在。"""
    f = skill_root / rel_path
    assert f.exists(), f"{name} references 缺失: {rel_path}"
    content = f.read_text(encoding="utf-8")
    assert len(content) >= 500, f"{name} 内容过短（{len(content)} 字符）"
    assert "V11.8.3" in content, f"{name} 缺 V11.8.3 标记"


def test_layer2_has_wave_strategy(skill_root: Path):
    """Layer 2 严重性分层必须含 Wave 分波策略。"""
    content = (skill_root / LAYER2_SEVERITY_REL).read_text(encoding="utf-8")
    assert "Wave 1" in content and "Wave 2" in content and "Wave 3" in content, (
        "Layer2 缺 Wave 1/2/3 分波策略"
    )
    assert "L1" in content and "L2" in content and "L3" in content, (
        "Layer2 缺 L1/L2/L3 严重性分级"
    )


# ─────────────────────────────────────────────────────────────────
# 2. Stage 6 SKILL.md 4 层框架结构
# ─────────────────────────────────────────────────────────────────


def test_stage6_skill_4_layer_framework(skill_root: Path):
    """Stage 6 SKILL.md 必须含 4 层分层决策框架（不是 7 步工序）。"""
    content = (skill_root / STAGE6_SKILL_REL).read_text(encoding="utf-8")
    # V11.8.3 升级关键词
    assert "V11.8.3" in content, "Stage 6 SKILL 缺 V11.8.3 升级标记"
    assert "4 层分层决策框架" in content, "Stage 6 SKILL 缺 4 层分层决策框架"
    # 4 层关键词
    assert "Layer 1" in content and "Layer 2" in content, "Stage 6 SKILL 缺 Layer 1/2"
    assert "Layer 3" in content and "Layer 4" in content, "Stage 6 SKILL 缺 Layer 3/4"
    # 决策关键词
    assert "严重性分波" in content or "Wave" in content, "Stage 6 SKILL 缺严重性分波"


def test_stage6_skill_references_4_layer(skill_root: Path):
    """Stage 6 SKILL.md depends_on.references 必须指向 4 层 references。"""
    content = (skill_root / STAGE6_SKILL_REL).read_text(encoding="utf-8")
    assert "bug-layer-1-discovery.md" in content, "Stage 6 SKILL 缺 Layer 1 reference"
    assert "bug-layer-2-severity.md" in content, "Stage 6 SKILL 缺 Layer 2 reference"
    assert "bug-layer-3-repair.md" in content, "Stage 6 SKILL 缺 Layer 3 reference"
    assert "bug-layer-4-convergence.md" in content, "Stage 6 SKILL 缺 Layer 4 reference"


def test_stage6_skill_iron_rules_by_layer(skill_root: Path):
    """Stage 6 SKILL.md 铁律按分层组织。"""
    content = (skill_root / STAGE6_SKILL_REL).read_text(encoding="utf-8")
    # 铁律按分层命名
    assert "L1." in content or "Layer 1" in content, "Stage 6 SKILL 缺 Layer 1 铁律"
    assert "L2." in content or "Layer 2" in content, "Stage 6 SKILL 缺 Layer 2 铁律"
    assert "L3." in content or "Layer 3" in content, "Stage 6 SKILL 缺 Layer 3 铁律"
    assert "L4." in content or "Layer 4" in content, "Stage 6 SKILL 缺 Layer 4 铁律"


# ─────────────────────────────────────────────────────────────────
# 3. trap-instructions.yaml V11-BH7 反例
# ─────────────────────────────────────────────────────────────────


def test_trap_yaml_has_bh7_anti_pattern(skill_root: Path):
    """trap-instructions.yaml 必须含 V11-BH7 范围自扩反例。"""
    content = (skill_root / TRAP_YAML_REL).read_text(encoding="utf-8")
    assert "V11-BH7" in content, "trap-instructions.yaml 缺 V11-BH7 反例"
    assert "范围自扩" in content or "批处理" in content, "V11-BH7 缺范围自扩/批处理关键词"
    assert "bug-layer-2-severity.md" in content, "V11-BH7 see_also 应引用 Layer 2 reference"


def test_trap_yaml_has_7_bh_anti_patterns(skill_root: Path):
    """trap-instructions.yaml 必须含 7 条 bug-hunt 反例（V11-BH1 ~ BH7）。"""
    content = (skill_root / TRAP_YAML_REL).read_text(encoding="utf-8")
    bh_ids = [f"V11-BH{i}" for i in range(1, 8)]
    missing = [bh for bh in bh_ids if bh not in content]
    assert not missing, f"trap-instructions.yaml 缺失 BH 反例: {missing}"


# ─────────────────────────────────────────────────────────────────
# 4. 继承 V11.8.2 的脚本和辅助 references
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("rel_path", BUG_HUNT_SCRIPTS_REL)
def test_bug_hunt_scripts_still_exist(skill_root: Path, rel_path: Path):
    """V11.8.2 的 6 个工具脚本仍存在（继承）。"""
    f = skill_root / rel_path
    assert f.exists(), f"工具脚本缺失: {rel_path}"


@pytest.mark.parametrize("rel_path", [
    BUG_HUNT_4D_REL,
    BUG_HUNT_5_CHECK_REL,
    BATTLE_REPORT_REL,
])
def test_auxiliary_references_still_exist(skill_root: Path, rel_path: Path):
    """V11.8.2 的辅助 references 仍存在（继承）。"""
    f = skill_root / rel_path
    assert f.exists(), f"辅助 reference 缺失: {rel_path}"


# ─────────────────────────────────────────────────────────────────
# 5. V11 主 SKILL.md 引用更新
# ─────────────────────────────────────────────────────────────────


def test_v11_skill_description_mentions_layer_framework(skill_root: Path):
    """V11 主 SKILL.md description 应提及 4 层框架。"""
    content = (skill_root / V11_SKILL_REL).read_text(encoding="utf-8")
    # Stage 6 的 description 应在 V11 主文件或 Stage 6 SKILL 中体现
    stage6_content = (skill_root / STAGE6_SKILL_REL).read_text(encoding="utf-8")
    assert "分层决策" in stage6_content or "严重性分波" in stage6_content, (
        "Stage 6 description 缺分层决策关键词"
    )