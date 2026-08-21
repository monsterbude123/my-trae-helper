#!/usr/bin/env python3
"""
scripts/vibe-coding-standards-line-guard.py — vibe-coding-standards 行数弹性守卫(2026-08-19 NEW)

设计目的:
  封装 skill-markets/vibe-coding-standards/scripts/validate_vibe_docs.sh 的核心逻辑,
  即"SKILL.md 行数 100~350 体积弹性检查 + 5 Pillar 联动检查",
  从 Git Hook(pre-commit)层面强制执行 —— 任何 skill 改 SKILL.md 后体积超 350 行即硬阻断。

阈值(v2.5 — 与 skill-markets/vibe-coding-standards SKILL.md 一致):
  AGENTS.md / SKILL.md / Subagent 弹性 100~350 行:
    - < 100 → WARN(过薄,可能缺地图)
    - > 350 → BLOCK(超过弹性上限,必须拆分到 references/)
  Rule .mdc ≤ 120 → BLOCK

输入/输出契约:
  输入:argv[1] = skill 名(如 "vibe-coding-standards")或绝对路径
  输出:JSON {passed, errors, warnings, info} + exit code 0/1
  exit 0 = PASS / exit 1 = BLOCK(含 errors)

禁止:
  - 禁止 import skill-markets/<pkg>/scripts/*(与 AGENTS.md §1.11 冲突)
  - 禁止改 _guard_lib(避免破坏其他 47 个 skill 的契约)

依据:
  - AGENTS.md §1.7(ponytail — 标准库优先)
  - AGENTS.md §2.4(Gate 自验收:实跑反例)
  - vibe-coding-standards/SKILL.md(v2.5 阈值)
"""
import re
import sys
from pathlib import Path

# scripts/ 是本守卫所在的目录
_HERE = Path(__file__).resolve().parent
# 用 importlib 加载同目录下的 _guard_lib(连字符文件名走 spec_from_file_location)
import importlib.util

_spec = importlib.util.spec_from_file_location("_guard_lib", _HERE / "_guard_lib.py")
_guard_lib = importlib.util.module_from_spec(_spec)
sys.modules["_guard_lib"] = _guard_lib
_spec.loader.exec_module(_guard_lib)


# ── 阈值(与 vibe-coding-standards/SKILL.md v2.5 强一致)─────────────
TH_MIN = 100   # 弹性下限(< 100 WARN)
TH_MAX = 350   # 弹性上限(> 350 BLOCK)
TH_RULE = 120  # Rule .mdc 硬上限


def _count_lines(path: Path) -> int:
    """读文件行数;无法读则返回 0。"""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0
    # 与 bash `wc -l` 等价:换行符数(尾部无换行不计数)
    return text.count("\n") + (0 if text.endswith("\n") and len(text) > 0 else 1) if text else 0


def _parse_frontmatter(text: str) -> str:
    """提取 SKILL.md / AGENTS.md 的 YAML frontmatter(首对 --- 之间的内容)。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    # 找第二个 ---
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i])
    return ""


def _check_one_md(file_path: Path, kind: str) -> dict:
    """检查单个文档行数,返回 {passed, errors, warnings, info}。"""
    lines = _count_lines(file_path)
    result = {"errors": [], "warnings": [], "info": []}
    rel = str(file_path)

    # 统一适用范围:SKILL.md / AGENTS.md / Subagent(.md in agents/)
    if lines < TH_MIN:
        result["warnings"].append(
            f"{rel} ({kind}) 只有 {lines} 行(< 弹性下限 {TH_MIN},建议补充地图/示例)"
        )
    elif lines > TH_MAX:
        result["errors"].append(
            f"{rel} ({kind}) 共 {lines} 行(> 弹性上限 {TH_MAX},必须拆分到 references/)"
        )
    else:
        result["info"].append(
            f"{rel} ({kind}) {lines} 行 → 100~350 弹性范围内 ✅"
        )

    # Subagent 必须声明 timeout(Pillar 3 — sub-agent timeout 强制)
    if kind == "subagent" and file_path.suffix == ".md":
        text = file_path.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"^timeout:", text, re.MULTILINE):
            result["warnings"].append(
                f"{rel} (subagent) 缺少 'timeout:' 字段(vibe 子代理强制)"
            )

    # AGENTS.md 必须含地图元素(Pillar 1 — 地图)
    if kind == "agents" and "AGENTS" in file_path.name:
        text = file_path.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"技术栈|目录树|启动命令|目录结构|架构", text):
            result["warnings"].append(
                f"{rel} (AGENTS) 缺少地图元素(技术栈/目录树/启动命令)"
            )

    return result


def _check_5_pillar(skill_md: Path) -> list:
    """5 Pillar 联动检查 — 封装 validate_vibe_docs.sh 的 Pillar 4 段。"""
    warnings = []
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return warnings

    fm = _parse_frontmatter(text)

    # Pillar 1/2:description 与 requires.optional 缺降级影响说明 → WARN
    if re.search(r"^requires:", fm, re.MULTILINE):
        optional_block_match = re.search(
            r"optional:\s*\n((?:\s+-\s+.+\n)+)", fm, re.MULTILINE
        )
        if optional_block_match:
            optional_block = optional_block_match.group(1)
            lines = [ln for ln in optional_block.splitlines() if ln.strip()]
            for ln in lines:
                # 排除注释行 + 空行
                stripped = ln.strip()
                if stripped.startswith("#") or stripped == "-":
                    continue
                if not re.search(r"(降级|→|代价|影响)", stripped):
                    warnings.append(
                        f"5 Pillar: {skill_md.name} optional 缺降级影响说明 — '{stripped[:60]}'"
                    )
                    break  # 一条示例即可

    # Pillar 4:SKILL.md 必须含 Examples 章节(可选,但缺失 → INFO 标记,不强阻断)
    if not re.search(r"^##\s+(Examples|示例)", text, re.MULTILINE):
        # 不计入 warnings,只在 info(可选增强)
        pass

    return warnings


def check_vibe_coding_standards_line(skill_path: str) -> dict:
    """vibe-coding-standards-line 守卫 — 检查 skill 的 SKILL.md / agents/*.md 行数弹性。

    Args:
        skill_path: skill 目录绝对路径或名字(由 _guard_lib._resolve_skill_path 解析)

    Returns:
        {passed: bool, errors: list, warnings: list, info: list}
    """
    p = Path(skill_path)
    if not p.exists():
        return {
            "passed": False,
            "errors": [f"skill 路径不存在: {p}"],
            "warnings": [],
            "info": [],
        }

    all_errors = []
    all_warnings = []
    all_info = []

    # 1. SKILL.md(主文档 — Pillar 1 / 2 直接关联)
    skill_md = p / "SKILL.md"
    if skill_md.exists():
        r = _check_one_md(skill_md, "skill")
        all_errors.extend(r["errors"])
        all_warnings.extend(r["warnings"])
        all_info.extend(r["info"])
        # 5 Pillar 联动
        all_warnings.extend(_check_5_pillar(skill_md))

    # 2. AGENTS.md(项目级入口 — 如果该 skill 自己有 AGENTS.md 才查,跨项目不强制)
    agents_md = p / "AGENTS.md"
    if agents_md.exists():
        r = _check_one_md(agents_md, "agents")
        all_errors.extend(r["errors"])
        all_warnings.extend(r["warnings"])
        all_info.extend(r["info"])

    # 3. agents/*.md(Subagent Pillar 3)
    agents_dir = p / "agents"
    if agents_dir.exists():
        for sub_md in sorted(agents_dir.rglob("*.md")):
            r = _check_one_md(sub_md, "subagent")
            all_errors.extend(r["errors"])
            all_warnings.extend(r["warnings"])
            all_info.extend(r["info"])

    # 4. rules/*.mdc(规则文件硬上限)
    rules_dir = p / "rules"
    if rules_dir.exists():
        for rule_mdc in sorted(rules_dir.rglob("*.mdc")):
            lines = _count_lines(rule_mdc)
            if lines > TH_RULE:
                all_errors.append(
                    f"{rule_mdc} (rule) 共 {lines} 行(> 硬上限 {TH_RULE})"
                )
            else:
                all_info.append(f"{rule_mdc} (rule) {lines} 行 ≤ {TH_RULE} ✅")

    return {
        "passed": len(all_errors) == 0,
        "errors": all_errors,
        "warnings": all_warnings,
        "info": all_info,
    }


# 主入口 — 复用 _guard_lib 的统一 CLI 契约(guards/skill-registration-guard 兜底一致)
if __name__ == "__main__":
    sys.exit(_guard_lib.cli_main(check_vibe_coding_standards_line, "vibe-line"))
