"""battle-report 实战报告 V11.8.2 多维度同步覆盖度测试。

> 反向校验 Stage 6 Bug Fix & Hunt 统一工序的多维度引用完整性,
> 防止"做一半就 commit"（skill-creation-workflow §2.2 反例 AP-1）。

蒸馏自 2026-08-15 V11.8.2 Stage 6 升级会话。
所有用例 <50ms，纯文件系统断言，不依赖网络。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

# V11.8.2 起路径全迁 Stage 6 同包
BATTLE_REPORT_REL = Path("skills/12-bug-fix/references/bug-hunt-battle-report.md")
STAGE6_SKILL_REL = Path("skills/12-bug-fix/SKILL.md")
BUG_HUNT_PHASE_A_REL = Path("skills/12-bug-fix/references/bug-hunt-phase-a.md")
BUG_HUNT_4D_REL = Path("skills/12-bug-fix/references/bug-hunt-4d-observation.md")
BUG_HUNT_5_CHECK_REL = Path("skills/12-bug-fix/references/bug-hunt-5-check.md")
TRAP_YAML_REL = Path("references/trap-instructions.yaml")
V11_SKILL_REL = Path("SKILL.md")

# V11.8.2 Stage 6 scripts/bug-hunt/ 子包脚本
BUG_HUNT_SCRIPTS_REL = [
    Path("skills/12-bug-fix/scripts/bug-hunt/new-bug.sh"),
    Path("skills/12-bug-fix/scripts/bug-hunt/close-bug.sh"),
    Path("skills/12-bug-fix/scripts/bug-hunt/dev-hmr-recovery.sh"),
    Path("skills/12-bug-fix/scripts/bug-hunt/dev-hmr-recovery.ps1"),
    Path("skills/12-bug-fix/scripts/bug-hunt/archive-screenshot.sh"),
    Path("skills/12-bug-fix/scripts/bug-hunt/archive-screenshot.ps1"),
]

# V11.8.2 Stage 6 anti-patterns/ 05-06.md（Phase A 专属）
PHASE_A_ANTI_PATTERNS = [
    Path("skills/12-bug-fix/anti-patterns/05-skip-real-login.md"),
    Path("skills/12-bug-fix/anti-patterns/06-serial-no-delegate.md"),
]

# 老路径不应再存在（V11.8.2 已迁出）
OLD_BATTLE_REPORT_REL = Path("references/stage-08-real-verify-battle-report.md")


# ─────────────────────────────────────────────────────────────────
# 1. Stage 6 Bug Fix & Hunt 统一工序核心文件齐全
# ─────────────────────────────────────────────────────────────────


def test_stage6_skill_exists_and_13_iron_rules(skill_root: Path):
    """Stage 6 SKILL.md 存在 + 含 V11.8.2 升级标记 + 13 铁律关键词。"""
    skill = skill_root / STAGE6_SKILL_REL
    assert skill.exists(), f"Stage 6 SKILL 缺失: {skill}"
    content = skill.read_text(encoding="utf-8")
    # V11.8.2 升级关键词
    assert "V11.8.2" in content, "Stage 6 SKILL 缺 V11.8.2 升级标记"
    assert "Phase A" in content and "Phase B" in content, "Stage 6 SKILL 缺 Phase A/B 分段"
    # 13 铁律（5 共享 + 7 Phase A + 3 Phase B = 15；标题按编号）
    iron_rule_pattern = re.compile(r"^\s*\d{1,2}\.\s+", re.MULTILINE)
    matches = iron_rule_pattern.findall(content)
    # 至少 13 条数字开头铁律（容许 1-2 行注释数字）
    iron_rule_lines = [m for m in content.split("\n") if re.match(r"^\s*\d{1,2}\.\s+", m) and not re.match(r"^\s*\d{1,2}\.\s+\d+\.\d+", m)]
    assert len(iron_rule_lines) >= 13, f"Stage 6 SKILL 铁律数 < 13, 实测 {len(iron_rule_lines)}"


def test_stage6_7_step_unified_flow(skill_root: Path):
    """Stage 6 SKILL.md 含 7 步统一工序（Phase A 3 + Phase B 5 = 7）。"""
    content = (skill_root / STAGE6_SKILL_REL).read_text(encoding="utf-8")
    assert "7 步统一工序" in content, "Stage 6 SKILL 缺 7 步统一工序段"
    # Phase A Step 1-3 + Phase B Step 4-7
    for step in ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5", "Step 6", "Step 7"]:
        assert step in content, f"Stage 6 SKILL 缺 {step}"


def test_stage6_6_anti_patterns_index(skill_root: Path):
    """Stage 6 SKILL.md 反模式表必须含 6 条。"""
    content = (skill_root / STAGE6_SKILL_REL).read_text(encoding="utf-8")
    for i in range(1, 7):
        # 表格行格式 "| i | ..."
        pattern = rf"\|\s*{i}\s*\|"
        assert re.search(pattern, content), f"Stage 6 SKILL 反模式表缺第 {i} 条"


# ─────────────────────────────────────────────────────────────────
# 2. Stage 6 子包内 4 个 references 齐全（V11.8.2 NEW）
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("rel_path", [
    BUG_HUNT_PHASE_A_REL,
    BUG_HUNT_4D_REL,
    BUG_HUNT_5_CHECK_REL,
    BATTLE_REPORT_REL,
])
def test_stage6_references_files_exist(skill_root: Path, rel_path: Path):
    """Stage 6 子包 4 个 references 必存在。"""
    f = skill_root / rel_path
    assert f.exists(), f"Stage 6 references 缺失: {rel_path}"
    content = f.read_text(encoding="utf-8")
    assert len(content) >= 500, f"{rel_path} 内容过短（{len(content)} 字符）"


# ─────────────────────────────────────────────────────────────────
# 3. 6 工具脚本存在 + Stage 6 sub-scripts/bug-hunt/ 子包
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("rel_path", BUG_HUNT_SCRIPTS_REL)
def test_bug_hunt_scripts_exist(skill_root: Path, rel_path: Path):
    """Stage 6 scripts/bug-hunt/ 6 工具脚本必存在。"""
    f = skill_root / rel_path
    assert f.exists(), f"工具脚本缺失: {rel_path}"
    content = f.read_text(encoding="utf-8")
    assert len(content) >= 200, f"{rel_path} 内容过短（{len(content)} 字符）"
    # 每个脚本必含 generated-by / V11.8.2 / 反例引用关键词
    assert "V11.8.2" in content or "V11-BH" in content, f"{rel_path} 缺 V11.8.2 / V11-BH 引用"


def test_bug_hunt_scripts_executable_marker(skill_root: Path):
    """bash 脚本必含 shebang。"""
    sh_scripts = [
        BUG_HUNT_SCRIPTS_REL[0],
        BUG_HUNT_SCRIPTS_REL[1],
        BUG_HUNT_SCRIPTS_REL[2],
        BUG_HUNT_SCRIPTS_REL[4],
    ]
    for rel in sh_scripts:
        f = skill_root / rel
        content = f.read_text(encoding="utf-8")
        first_line = content.split("\n", 1)[0]
        assert first_line.startswith("#!"), f"{rel} 缺 shebang"


# ─────────────────────────────────────────────────────────────────
# 4. trap-instructions.yaml V11-BH 反例 see_also 指向 Stage 6 同包
# ─────────────────────────────────────────────────────────────────


def test_trap_yaml_bh_see_also_stage6_paths(skill_root: Path):
    """trap-instructions.yaml V11-BH1~6 see_also 必含 Stage 6 同包路径（V11.8.2 迁移后）。"""
    content = (skill_root / TRAP_YAML_REL).read_text(encoding="utf-8")
    # 老路径不应再出现（V11.8.2 已迁出）
    assert "references/stage-08-real-verify-battle-report.md" not in content, (
        "trap-instructions.yaml 仍含老路径 references/stage-08-real-verify-battle-report.md"
    )
    # bug-hunt-tooling skill 引用也应已撤（V11.8.2 不外挂独立 skill）
    assert "skill-markets/bug-hunt-tooling" not in content, (
        "trap-instructions.yaml 仍引用外部 bug-hunt-tooling skill（V11.8.2 已折叠进 Stage 6）"
    )
    # 新路径应出现
    assert "skills/12-bug-fix/references/bug-hunt-battle-report.md" in content
    assert "skills/12-bug-fix/SKILL.md" in content


def test_trap_yaml_has_6_bh_anti_patterns(skill_root: Path):
    """trap-instructions.yaml 必须含 6 条 bug-hunt 反例（V11-BH1 ~ BH6）。"""
    content = (skill_root / TRAP_YAML_REL).read_text(encoding="utf-8")
    bh_ids = [f"V11-BH{i}" for i in range(1, 7)]
    missing = [bh for bh in bh_ids if bh not in content]
    assert not missing, f"trap-instructions.yaml 缺失 BH 反例: {missing}"


# ─────────────────────────────────────────────────────────────────
# 5. 老路径已撤出（V11.8.2 迁移完成）
# ─────────────────────────────────────────────────────────────────


def test_old_battle_report_path_removed(skill_root: Path):
    """V11.8.2 老路径 references/stage-08-real-verify-battle-report.md 不应再存在。"""
    f = skill_root / OLD_BATTLE_REPORT_REL
    assert not f.exists(), f"V11.8.2 老路径仍存在: {OLD_BATTLE_REPORT_REL}"


# ─────────────────────────────────────────────────────────────────
# 6. V11 SKILL.md §0.5.1 同类清单 [5] + §13 references 索引引用 Stage 6
# ─────────────────────────────────────────────────────────────────


def test_v11_skill_e2e_row_references_stage6(skill_root: Path):
    """V11 SKILL.md §0.5.1 同类清单 [5] E2E 框架行必须含 Stage 6 实战报告链接。"""
    content = (skill_root / V11_SKILL_REL).read_text(encoding="utf-8")
    pattern = r"\|\s*5\s*\|\s*\*\*E2E 框架\*\*.*?skills/12-bug-fix/references/bug-hunt-battle-report\.md"
    assert re.search(pattern, content, re.DOTALL), (
        "V11 SKILL.md §0.5.1 同类清单 [5] 行未引用 Stage 6 bug-hunt-battle-report.md"
    )


def test_v11_skill_section13_references_stage6(skill_root: Path):
    """V11 SKILL.md §13 references 索引必含 Stage 6 bug-hunt-battle-report 指引。"""
    content = (skill_root / V11_SKILL_REL).read_text(encoding="utf-8")
    assert "## §13 参考索引" in content, "V11 SKILL.md 缺 §13 参考索引段"
    section13_start = content.find("## §13 参考索引")
    tail = content[section13_start:]
    assert "skills/12-bug-fix/references/bug-hunt-battle-report.md" in tail, (
        "V11 SKILL.md §13 references 索引未含 Stage 6 bug-hunt-battle-report 指引"
    )


# ─────────────────────────────────────────────────────────────────
# 7. anti-patterns/05-06.md（V11.8.2 Phase A 专属反例）
# ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("rel_path", PHASE_A_ANTI_PATTERNS)
def test_phase_a_anti_patterns_exist(skill_root: Path, rel_path: Path):
    """Stage 6 anti-patterns/05-06.md（V11.8.2 Phase A 专属反例）必存在。"""
    f = skill_root / rel_path
    assert f.exists(), f"Phase A anti-pattern 缺失: {rel_path}"
    content = f.read_text(encoding="utf-8")
    assert "V11.8.2" in content, f"{rel_path} 缺 V11.8.2 标记"
    assert "Phase A" in content, f"{rel_path} 缺 Phase A 标识"


# ─────────────────────────────────────────────────────────────────
# 8. Stage 6 sub-scripts 子包自动加载（hooks-fidelity 可发现）
# ─────────────────────────────────────────────────────────────────


def test_stage6_scripts_bug_hunt_is_subpackage(skill_root: Path):
    """Stage 6 scripts/bug-hunt/ 是 Stage 6 子包，不是公共 scripts/。"""
    # Stage 6 子包 scripts/bug-hunt/ 应存在
    subpkg = skill_root / Path("skills/12-bug-fix/scripts/bug-hunt")
    assert subpkg.is_dir(), f"Stage 6 scripts/bug-hunt/ 子包缺失: {subpkg}"

    # 公共 scripts/bug-hunt/ 不应存在（V11.8.2 已折叠）
    public_pkg = skill_root / Path("scripts/bug-hunt")
    assert not public_pkg.exists(), (
        f"V11.8.2 公共 scripts/bug-hunt/ 不应再存在（已折叠进 Stage 6）: {public_pkg}"
    )