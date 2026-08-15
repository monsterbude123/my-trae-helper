#!/usr/bin/env python3
"""
catalog-v21-evaluate-requires.py — Catalog V2.1 准备工具(2026-08-15 NEW)

自动扫描 31 个缺 requires 的 SKILL,基于:
  1. SKILL.md 正文 cross-skill 引用(skill-markets/<name>/ 提及)
  2. references/* 内容引用其他 skill 名
  3. agents/*.md 头部 requires 字段
  4. 现有 SKILL.md 已声明的 requires 字段(参考示例)
  5. registry/skills.yaml 注册表

输出:V2.1 评估清单(YAML),供人工 review + 批量 commit。

Usage:
    python catalog-v21-evaluate-requires.py [--dry-run] [--output logs/v2.1-requires-evaluation.yaml]
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections import defaultdict

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS_ROOT = PROJECT_ROOT / "skill-markets"
REGISTRY_PATH = PROJECT_ROOT / "registry" / "skills.yaml"

# 修正 output 默认路径(脚本从 logs/ → scripts/ 升级)
DEFAULT_OUTPUT = PROJECT_ROOT / "references" / "v2.1-requires-evaluation.yaml"

# V2 实扫出的 31 缺 requires 的 SKILL(已知清单)
NO_REQUIRES_SKILLS = [
    "browser-use-cloud", "coding-xinfa", "comfyui-api-skills", "daily-vibe-coding",
    "deep-research", "deepagents_teach_skill", "doc-map-manager", "docsify-doc-builder",
    "e2e-module-audit", "goal-mode", "guard-approver", "langgraph_teach_skill",
    "learn-plan-skill", "meeting-minutes-taker", "mini-game-p2p-room",
    "minimax-multimodal", "modelscope-assistant", "openapi-doc-exporter",
    "project-rules-gate", "screenshot", "session-distiller", "shuxia-novel-engine",
    "skill-bundle", "skill-creator-claude", "skills-security-scan",
    "test-experience", "test-partition-runner", "trae-professional",
    "vibe-coding-standards", "vision-audit", "window-process-skills",
]

# 跨 SKILL 关键词映射(基于已有 SKILL 描述)
# 格式:(regex, requires skill 名)
CROSS_SKILL_PATTERNS = [
    (r"\bacceptance-discipline\b", "acceptance-discipline"),
    (r"\bguard-approver\b", "guard-approver"),
    (r"\btrae-security-review\b", "trae-security-review"),
    (r"\bvibe-coding-standards\b", "vibe-coding-standards"),
    (r"\btest-experience\b", "test-experience"),
    (r"\btest-partition-runner\b", "test-partition-runner"),
    (r"\be2e-module-audit\b", "e2e-module-audit"),
    (r"\bskill-acceptance\b", "skill-acceptance"),
    (r"\bagent-dev-control-kit\b", "agent-dev-control-kit"),
    (r"\bskill-bundle\b", "skill-bundle"),
    (r"\bguard-gate-smith\b", "guard-gate-smith"),
    (r"\bproject-rules-gate\b", "project-rules-gate"),
    (r"\bgoal-mode\b", "goal-mode"),
    (r"\bskill-creator\b", "skill-creator-claude"),
    (r"\btrae-professional\b", "trae-professional"),
    (r"\bwindow-process-skills\b", "window-process-skills"),
    (r"\bself-improving-agent\b", "self-improving-agent"),
    (r"\bproject-rule-skill\b", "project-rule-skill"),
]


def load_existing_requires() -> dict:
    """加载已有 SKILL 的 requires 字段作为参考"""
    existing = {}
    for skill_dir in sorted(SKILLS_ROOT.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text(encoding="utf-8", errors="ignore")
        if "requires:" not in text:
            continue
        # 极简提取 requires 下的子项
        m = re.search(r"requires:\s*\n((?:\s*-\s*\S.*\n?)+)", text)
        if m:
            reqs = [line.strip().lstrip("-").strip() for line in m.group(1).split("\n") if line.strip()]
            existing[skill_dir.name] = reqs
    return existing


def scan_cross_skill_refs(skill_dir: pathlib.Path) -> list:
    """扫描 SKILL.md + references/*.md 找 cross-skill 引用"""
    refs = set()
    search_files = [skill_dir / "SKILL.md"]
    for p in skill_dir.rglob("*.md"):
        if p != skill_dir / "SKILL.md":
            search_files.append(p)

    for f in search_files:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        for pattern, skill_name in CROSS_SKILL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                refs.add(skill_name)
    return sorted(refs)


def evaluate_skill(skill_name: str, existing_refs: dict) -> dict:
    """评估单个 SKILL 的 requires 建议"""
    skill_dir = SKILLS_ROOT / skill_name
    if not skill_dir.exists():
        return {"skill": skill_name, "error": "目录不存在"}

    auto_refs = scan_cross_skill_refs(skill_dir)
    # 排除自身
    auto_refs = [r for r in auto_refs if r != skill_name]

    # 评分:自动识别覆盖度
    if not auto_refs:
        confidence = "LOW"  # 无自动证据
        suggestion = []  # 留空,人工补
    elif len(auto_refs) <= 2:
        confidence = "MEDIUM"  # 可能有遗漏
        suggestion = auto_refs
    else:
        confidence = "HIGH"  # 多证据
        suggestion = auto_refs

    return {
        "skill": skill_name,
        "auto_detected": auto_refs,
        "confidence": confidence,
        "suggestion": suggestion,
        "status": "auto" if confidence == "HIGH" else "manual_review",
    }


def main():
    ap = argparse.ArgumentParser(description="Catalog V2.1 requires 评估")
    ap.add_argument("--dry-run", action="store_true", help="仅打印,不改文件")
    ap.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT,
                    help="评估清单输出(默认 references/)")
    ap.add_argument("--auto-fill", action="store_true", help="自动填 HIGH 置信度的 SKILL")
    args = ap.parse_args()

    existing_refs = load_existing_requires()
    evaluations = []
    auto_fill_count = 0

    for skill_name in NO_REQUIRES_SKILLS:
        ev = evaluate_skill(skill_name, existing_refs)
        evaluations.append(ev)

        # 自动填 HIGH 置信度
        if args.auto_fill and ev.get("confidence") == "HIGH" and ev.get("suggestion"):
            skill_md = SKILLS_ROOT / skill_name / "SKILL.md"
            text = skill_md.read_text(encoding="utf-8")
            if "requires:" not in text:
                # 在 version 行后插入 requires
                requires_block = "requires:\n" + "".join(f"  - {r}\n" for r in ev["suggestion"])
                new_text = re.sub(
                    r"(version: [^\n]+\n)",
                    lambda m: m.group(1) + requires_block,
                    text,
                    count=1,
                )
                if not args.dry_run:
                    skill_md.write_text(new_text, encoding="utf-8")
                    auto_fill_count += 1
                    print(f"  ✅ {skill_name}: 自动填 {len(ev['suggestion'])} 个 requires")

    # 输出 YAML 评估清单
    if not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("# Catalog V2.1 requires 评估清单(2026-08-15)\n")
            f.write("# 由 catalog-v21-evaluate-requires.py 自动生成\n")
            f.write("# 31 个 SKILL 评估, 按 confidence 排序:\n")
            f.write("#   HIGH: 多证据自动识别, --auto-fill 可批量填\n")
            f.write("#   MEDIUM: 有引用, 但可能不全, 需人工 review\n")
            f.write("#   LOW: 无自动证据, 全部人工补\n\n")
            f.write(f"version: 2.1\n")
            f.write(f"total_skills: {len(evaluations)}\n")
            f.write(f"high_confidence: {sum(1 for e in evaluations if e.get('confidence') == 'HIGH')}\n")
            f.write(f"medium_confidence: {sum(1 for e in evaluations if e.get('confidence') == 'MEDIUM')}\n")
            f.write(f"low_confidence: {sum(1 for e in evaluations if e.get('confidence') == 'LOW')}\n\n")
            for ev in sorted(evaluations, key=lambda x: (x.get("confidence", "ZZZ"), x["skill"])):
                f.write(f"- skill: {ev['skill']}\n")
                f.write(f"  confidence: {ev.get('confidence', '?')}\n")
                f.write(f"  status: {ev.get('status', '?')}\n")
                f.write(f"  auto_detected:\n")
                for r in ev.get("auto_detected", []):
                    f.write(f"    - {r}\n")
                if not ev.get("auto_detected"):
                    f.write(f"    []  # 无自动证据, 需人工补\n")
                f.write(f"  suggestion:\n")
                for r in ev.get("suggestion", []):
                    f.write(f"    - {r}\n")
                if not ev.get("suggestion"):
                    f.write(f"    []  # 留空\n")
                f.write("\n")

    # 打印统计
    high = sum(1 for e in evaluations if e.get("confidence") == "HIGH")
    medium = sum(1 for e in evaluations if e.get("confidence") == "MEDIUM")
    low = sum(1 for e in evaluations if e.get("confidence") == "LOW")
    print(f"\n=== Catalog V2.1 requires 评估 ===")
    print(f"  总 SKILL: {len(evaluations)}")
    print(f"  HIGH 置信度(可批量填): {high}")
    print(f"  MEDIUM 置信度(需 review): {medium}")
    print(f"  LOW 置信度(全人工补): {low}")
    if args.auto_fill and not args.dry_run:
        print(f"\n已自动填 HIGH 置信度 SKILL: {auto_fill_count} 个")
    if not args.dry_run:
        print(f"\n评估清单: {args.output}")


if __name__ == "__main__":
    main()