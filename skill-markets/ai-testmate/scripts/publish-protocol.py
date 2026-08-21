#!/usr/bin/env python3
"""
ai-testmate 协议覆盖自检脚本
- 校验 references/*.md 章节齐全
- 校验 SKILL.md frontmatter 完整
- 借鉴 V11 protocol-coverage 思路,但独立实现,不依赖 V11
"""

import sys
import pathlib
import re

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent

REQUIRED_SECTIONS = {
    "references/ai-testmate-protocol.md": [
        "## §1 scope",
        "## §2 必填元数据",
        "## §3 结构规则",
        "## §4 反例库",
        "## §5 测试要求",
        "## §6 协议版本",
    ],
    "references/workflow.md": [
        "## §1 6 步流水线",
        "## §2 test-cases.yaml 字段规范",
        "## §3 时间戳目录规范",
    ],
    "references/zentao-integration.md": [
        "## §1 调用时机表",
        "## §2 字段映射",
    ],
    "references/env-config-spec.md": [
        "## §1 必填变量",
        "## §4 缺失降级",
    ],
    "references/lark-webhook-spec.md": [
        "## §1 消息卡片格式",
        "## §4 失败降级",
    ],
    "references/pytest-patterns.md": [
        "## §1 用例骨架",
        "## §2 夹具复用",
    ],
    "references/playwright-patterns.md": [
        "## §1 登录态复用",
        "## §2 截图脱敏",
    ],
    "references/report-templates.md": [
        "## §1 report.html",
        "## §2 report.md",
        "## §3 junit.xml",
        "## §4 manifest.json",
    ],
}

REQUIRED_FRONTMATTER = ["name:", "description:", "version:", "requires:"]


def check_sections(rel_path: str) -> list:
    full = SKILL_DIR / rel_path
    if not full.exists():
        return [f"<文件不存在: {rel_path}>"]
    text = full.read_text(encoding="utf-8")
    return [s for s in REQUIRED_SECTIONS[rel_path] if s not in text]


def check_frontmatter() -> list:
    skill = SKILL_DIR / "SKILL.md"
    if not skill.exists():
        return ["<SKILL.md 不存在>"]
    text = skill.read_text(encoding="utf-8")
    # 取 frontmatter 区
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return ["<SKILL.md 缺 frontmatter 区(--- ... ---)>"]
    fm = m.group(1)
    return [f for f in REQUIRED_FRONTMATTER if f not in fm]


def main() -> int:
    print("=== ai-testmate 协议覆盖自检 ===")
    fails = []

    # 1. 章节覆盖
    for rel in REQUIRED_SECTIONS:
        missing = check_sections(rel)
        if missing:
            print(f"  ❌ {rel} 缺章节: {missing}")
            fails.append(rel)
        else:
            print(f"  ✅ {rel}")

    # 2. frontmatter
    fm_missing = check_frontmatter()
    if fm_missing:
        print(f"  ❌ SKILL.md frontmatter 缺: {fm_missing}")
        fails.append("SKILL.md")
    else:
        print(f"  ✅ SKILL.md frontmatter")

    print()
    if fails:
        print(f"🛑 BLOCKED: {len(fails)} 项不通过")
        return 1
    print("✅ PASS:协议覆盖齐全")
    return 0


if __name__ == "__main__":
    sys.exit(main())