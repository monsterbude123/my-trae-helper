#!/usr/bin/env python3
"""
scripts/quality-documentation-manager-guard.py — quality-documentation-manager 项目侧薄壳守卫(2026-08-21 NEW)

设计目的:
  quality-documentation-manager 是元项目方法论沉淀 skill(Diátaxis + SSOT + Docs-as-Code 工具栈),
  纯文档 skill(SKILL.md + references/),无 scripts 子目录。本守卫作为项目侧薄壳入口,
  仅做结构验证(SKILL.md 存在 + frontmatter 合规 + 行数在 100~350 弹性内)。

  遵循 AGENTS.md §1.11 铁律 11 — 项目侧 guard 必带,实现可极简。

用法:
  python scripts/quality-documentation-manager-guard.py skill-markets/quality-documentation-manager

退出码:
  0 = PASS
  1 = BLOCK(结构异常)
  2 = WARN(行数超弹性下限/上限)
"""
import sys
import pathlib
import re

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_SKILL_DIR = _REPO_ROOT / "skill-markets" / "quality-documentation-manager"
_SKILL_MD = _SKILL_DIR / "SKILL.md"

_LINE_LOW = 100
_LINE_HIGH = 350


def _check_skill_md() -> tuple[bool, str]:
    """检查 SKILL.md 存在 + frontmatter 必填 name/description 字段。"""
    if not _SKILL_MD.exists():
        return False, f"❌ SKILL.md 缺失: {_SKILL_MD}"

    text = _SKILL_MD.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return False, "❌ SKILL.md 缺 YAML frontmatter(以 '---' 起始)"

    # 极简 frontmatter 解析
    end = text.find("\n---", 3)
    if end < 0:
        return False, "❌ SKILL.md frontmatter 未闭合(缺第二个 '---')"

    fm_block = text[3:end]
    if not re.search(r"^name:\s*\S+", fm_block, re.MULTILINE):
        return False, "❌ SKILL.md frontmatter 缺 'name' 字段"
    if not re.search(r"^description:\s*\S+", fm_block, re.MULTILINE):
        return False, "❌ SKILL.md frontmatter 缺 'description' 字段"

    return True, "✅ SKILL.md 存在 + frontmatter 合规"


def _check_line_range() -> tuple[int, str]:
    """检查 SKILL.md 行数是否在 100~350 弹性范围内。"""
    if not _SKILL_MD.exists():
        return 2, f"⚠️  SKILL.md 缺失,跳过行数检查"

    line_count = len(_SKILL_MD.read_text(encoding="utf-8", errors="replace").splitlines())
    if _LINE_LOW <= line_count <= _LINE_HIGH:
        return 0, f"✅ SKILL.md {line_count} 行(弹性 {_LINE_LOW}~{_LINE_HIGH})"
    return 2, f"⚠️  SKILL.md {line_count} 行(超弹性 {_LINE_LOW}~{_LINE_HIGH})"


def main() -> int:
    """主入口。"""
    if not _SKILL_DIR.exists():
        print(f"❌ quality-documentation-manager 目录缺失: {_SKILL_DIR}", file=sys.stderr)
        return 1

    # 过滤位置参数(husky gate 调用时会传入 skill 路径)
    _ = [a for a in sys.argv[1:] if not a.startswith("-") and a != "--"]

    print(f"🔍 quality-documentation-manager 结构守卫 (skill dir: {_SKILL_DIR})")

    # 1. SKILL.md + frontmatter
    ok, msg = _check_skill_md()
    print(f"  {msg}")
    if not ok:
        return 1

    # 2. 行数弹性
    code, msg = _check_line_range()
    print(f"  {msg}")
    if code == 0:
        print("\n✅ quality-documentation-manager 结构守卫 PASS")
        return 0
    elif code == 2:
        print("\n⚠️  quality-documentation-manager 结构守卫 WARN(行数超弹性)")
        return 2
    else:
        return code


if __name__ == "__main__":
    sys.exit(main())
