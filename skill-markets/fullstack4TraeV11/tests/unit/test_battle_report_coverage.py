"""battle-report 实战报告 V11.8.1 多维度同步覆盖度测试。

> 反向校验 stage-08-real-verify-battle-report.md 在 V11 体系内被多维度引用,
> 防止"做一半就 commit"（skill-creation-workflow §2.2 反例 AP-1）。

蒸馏自 2026-08-15 V11.8.1 bug-hunt / E2E 跨阶段实战报告升级会话。
所有用例 <50ms，纯文件系统断言，不依赖网络。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

BATTLE_REPORT_REL = Path("references/stage-08-real-verify-battle-report.md")
TRAP_YAML_REL = Path("references/trap-instructions.yaml")
V11_SKILL_REL = Path("SKILL.md")

STAGE_SKILLS_REL = [
    Path("skills/08-real-verify/SKILL.md"),
    Path("skills/09-review/SKILL.md"),
    Path("skills/12-bug-fix/SKILL.md"),
]


# ─────────────────────────────────────────────────────────────────
# 1. 报告本体存在性 + 必含章节
# ─────────────────────────────────────────────────────────────────


def test_battle_report_exists(skill_root: Path):
    """实战报告文件存在（V11.8.1 NEW）。"""
    report = skill_root / BATTLE_REPORT_REL
    assert report.exists(), f"实战报告缺失: {report}"
    content = report.read_text(encoding="utf-8")
    assert len(content) >= 5000, f"实战报告内容过短（{len(content)} 字符）"
    # 必含章节（10 段）
    required_sections = [
        "§0 为什么需要本报告",
        "§1 bug-hunt/E2E 在 V11 13 stage 的位置",
        "§2 真登录取证 7 步",
        "§3 4 维度观察法",
        "§4 5 项证据独立抽检",
        "§5 sub-agent 委派头部 6 字段",
        "§6 bug 单状态机守恒",
        "§7 工具脚本清单",
        "§8 6 反例库",
        "§9 V11.5 5 个 V11 缺漏吸收",
        "§10 一句话铁律 + 验证矩阵",
    ]
    missing = [s for s in required_sections if s not in content]
    assert not missing, f"实战报告缺失章节: {missing}"


# ─────────────────────────────────────────────────────────────────
# 2. 6 反例库全部命中报告标题（V11.8.1 §8）
# ─────────────────────────────────────────────────────────────────


def test_battle_report_contains_6_anti_patterns(skill_root: Path):
    """§8 6 反例库标题齐全（与实战失败案例一一对应）。"""
    content = (skill_root / BATTLE_REPORT_REL).read_text(encoding="utf-8")
    anti_patterns = [
        "§反例 1 — 跳过 fixture 手写真登录",
        "§反例 2 — 14 模块串行未委派",
        "§反例 3 — bug 单手填 6 字段",
        "§反例 4 — 修复后 bug 单 status 未回写",
        "§反例 5 — HMR 反复重 navigate",
        "§反例 6 — 主代理证据未独立抽检",
    ]
    missing = [ap for ap in anti_patterns if ap not in content]
    assert not missing, f"§8 反例库缺失: {missing}"


# ─────────────────────────────────────────────────────────────────
# 3. trap-instructions.yaml 新增 V11-BH1 ~ V11-BH6 反例
# ─────────────────────────────────────────────────────────────────


def test_trap_yaml_has_6_bh_anti_patterns(skill_root: Path):
    """trap-instructions.yaml 必须含 6 条 bug-hunt 反例（V11-BH1 ~ BH6）。"""
    trap_path = skill_root / TRAP_YAML_REL
    content = trap_path.read_text(encoding="utf-8")
    bh_ids = [f"V11-BH{i}" for i in range(1, 7)]
    missing = [bh for bh in bh_ids if bh not in content]
    assert not missing, f"trap-instructions.yaml 缺失 BH 反例: {missing}"

    # 每条 BH 反例必含 detect_signal + fix_template_after + see_also
    for bh in bh_ids:
        # 找到该反例块（id: V11-BH{N} 到下一个反例块）
        pattern = rf"  - id: {bh}\b(.*?)(?=\n  - id: V11-|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        assert match, f"{bh} 反例块未找到"
        block = match.group(1)
        assert "detect_signal" in block, f"{bh} 缺 detect_signal 字段"
        assert "fix_template_after" in block, f"{bh} 缺 fix_template_after 字段"
        assert "see_also" in block, f"{bh} 缺 see_also 字段"


# ─────────────────────────────────────────────────────────────────
# 4. Stage 3.5 / 4 / 6 depends_on.references 引用实战报告
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("stage_skill_rel", STAGE_SKILLS_REL)
def test_stage_skill_depends_on_battle_report(skill_root: Path, stage_skill_rel: Path):
    """3 个跨 stage SKILL.md 的 depends_on.references 必须含实战报告路径。"""
    stage_skill = skill_root / stage_skill_rel
    assert stage_skill.exists(), f"Stage SKILL 缺失: {stage_skill}"
    content = stage_skill.read_text(encoding="utf-8")
    assert "stage-08-real-verify-battle-report.md" in content, (
        f"{stage_skill_rel.name} depends_on.references 未引用实战报告"
    )


# ─────────────────────────────────────────────────────────────────
# 5. V11 SKILL.md §0.5.1 同类清单 [5] + §13 references 索引引用实战报告
# ─────────────────────────────────────────────────────────────────


def test_v11_skill_e2e_row_references_battle_report(skill_root: Path):
    """V11 SKILL.md §0.5.1 同类清单 [5] E2E 框架行必须含实战报告链接。"""
    content = (skill_root / V11_SKILL_REL).read_text(encoding="utf-8")
    # §0.5.1 表格第 5 行
    pattern = (
        r"\|\s*5\s*\|\s*\*\*E2E 框架\*\*.*?stage-08-real-verify-battle-report\.md"
    )
    assert re.search(pattern, content, re.DOTALL), (
        "V11 SKILL.md §0.5.1 同类清单 [5] 行未引用 stage-08-real-verify-battle-report.md"
    )


def test_v11_skill_section13_references_index(skill_root: Path):
    """V11 SKILL.md §13 references 索引必须含实战报告。"""
    content = (skill_root / V11_SKILL_REL).read_text(encoding="utf-8")
    # §13 references 索引段
    assert "## §13 参考索引" in content, "V11 SKILL.md 缺 §13 参考索引段"
    # §13 后到文件末尾之间必须含实战报告
    section13_start = content.find("## §13 参考索引")
    tail = content[section13_start:]
    assert "stage-08-real-verify-battle-report" in tail, (
        "V11 SKILL.md §13 references 索引未含 stage-08-real-verify-battle-report"
    )