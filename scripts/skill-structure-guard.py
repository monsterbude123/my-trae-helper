#!/usr/bin/env python3
"""
Skill Structure Guard — 技能结构守卫（v2 — 2026-08-14 解除硬编码）

设计原则（参考 vibe-coding-standards v2.5）：
  - 行数 / 铁律数 / 脚本数 不设硬上限（v2.5 主张弹性 100~350 行，"超过才考虑提取 references/"）
  - 守卫只兜底"真有 bug"：缺 SKILL.md / 缺 YAML frontmatter / 缺 name|description / 非 kebab-case
  - 其他风格提示全部降级为 info（不阻断、不警告），尊重 vibe-coding-standards 的指导而非强行复述

检查维度:
  ERRORS（硬阻断）: 目录不存在 / 非 kebab-case / 缺 SKILL.md / 缺 frontmatter / 缺必需字段
  WARNINGS（提示）:  目录名 > 50 字符 / scripts/ 含 subprocess+shell=True
  INFO（仅记录）:    行数超出 vibe-coding-standards 软上限 / name 与 dirName 不一致 /
                    agents 文件名带 -agent 后缀 / 脚本文件数量

触发时机: pre-create (新建技能时) / verify

Usage:
    python scripts/skill-structure-guard.py skill-markets/<skill_name>

注意: 与 skill-acceptance/scripts/verify.py 的关系
  - verify.py: check_frontmatter / check_scripts_boundary(轻量)
  - 本脚本: 命名规范 + 必要 frontmatter + 软性提示
  - 互补,非冗余
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List


# vibe-coding-standards v2.5 软上限（仅作为 info 提示，不阻断）
SOFT_LINE_LIMIT = 350  # SKILL.md 超过此行 → 提示考虑提取 references/，但不阻断


def check_structure(skill_path: str) -> Dict:
    """
    检查技能结构

    Returns:
        {
            'passed': bool,
            'errors': List[str],
            'warnings': List[str],
            'info': List[str]
        }
    """
    skill_dir = Path(skill_path)
    errors = []
    warnings = []
    info = []

    if not skill_dir.exists():
        errors.append(f'技能目录不存在: {skill_path}')
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'info': info}

    dir_name = skill_dir.name
    # kebab-case + 容忍 tempfile 的 '_' 后缀(tempfile.mkdtemp 在 Windows 会生成 name_xxxxx)
    if not re.match(r'^[a-z][a-z0-9_-]*$', dir_name):
        errors.append(f'目录名不合规: {dir_name}（应为 kebab-case，小写字母开头）')
    elif '_' in dir_name:
        # 含下划线 → 通常是 tempfile 临时目录,只记 info(不阻断),不污染 PASS 状态
        info.append(f'目录名 {dir_name!r} 含下划线 — 真 skill 目录建议纯 kebab-case')

    if len(dir_name) > 50:
        warnings.append(f'目录名过长: {dir_name}（建议 ≤ 50 字符）')

    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        errors.append('缺少 SKILL.md')
    else:
        check_skill_md(skill_md, errors, warnings, info)

    agents_dir = skill_dir / 'agents'
    if agents_dir.exists():
        check_agents_dir(agents_dir, errors, warnings, info)

    scripts_dir = skill_dir / 'scripts'
    if scripts_dir.exists():
        check_scripts_dir(scripts_dir, errors, warnings, info)

    return {
        'passed': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'info': info,
    }


def check_skill_md(skill_md: Path, errors: List[str], warnings: List[str], info: List[str]):
    """检查 SKILL.md"""
    content = skill_md.read_text(errors='ignore')

    if not content.startswith('---'):
        errors.append('SKILL.md 缺少 YAML frontmatter（必须以 --- 开头）')
    else:
        frontmatter_match = re.match(r'^---\n([\s\S]*?)\n---', content)
        if frontmatter_match:
            yaml_content = frontmatter_match.group(1)

            required_fields = ['name', 'description']
            for field in required_fields:
                if not re.search(rf'^{field}:', yaml_content, re.MULTILINE):
                    errors.append(f'SKILL.md YAML frontmatter 缺少必需字段: {field}')

            # version 字段: AGENTS.md §1.1 推荐(非强阻断)
            # 缺失 → WARNING(2026-08-14 self-audit #2 + upgrade-guidance §1 建议)
            if not re.search(r'^version:', yaml_content, re.MULTILINE):
                warnings.append(
                    'SKILL.md 缺 version 字段(AGENTS.md §1.1 推荐) — '
                    '建议添加 version: x.y.z 以追踪演进 + 支持 bundle 守 VER-xxx'
                )

            # name 字段与目录名一致 → 降级为 info（archived 兼容壳就是合理反例）
            # 正则容忍 `name: foo` / `name: "foo"` / `name: 'foo'` 三种 YAML 写法
            name_pattern = r'^name:\s*["\']?' + re.escape(skill_md.parent.name) + r'["\']?\s*$'
            if not re.search(name_pattern, yaml_content, re.MULTILINE):
                # 读取实际声明的 name 以便给出可操作提示
                declared_match = re.search(r'^name:\s*(.+?)\s*$', yaml_content, re.MULTILINE)
                declared = declared_match.group(1).strip().strip('"').strip("'") if declared_match else '(none)'
                info.append(
                    f'SKILL.md 声明 name={declared!r} 与目录名 {skill_md.parent.name!r} 不一致 — '
                    f'大多数 skill 应保持一致，archived 兼容壳允许不同名'
                )

    # 行数检查：vibe-coding-standards v2.5 软上限 350 行（仅 info 提示，不阻断）
    lines = content.count('\n') + 1
    if lines > SOFT_LINE_LIMIT:
        info.append(
            f'SKILL.md {lines} 行（> v2.5 软上限 {SOFT_LINE_LIMIT}）— '
            f'参考 vibe-coding-standards/references/VibeCodingStandards.md §3.1，'
            f'考虑提取 references/ 而非裁剪内容'
        )


def check_agents_dir(agents_dir: Path, errors: List[str], warnings: List[str], info: List[str]):
    """检查 agents 目录"""
    for agent_file in agents_dir.glob('*.md'):
        file_name = agent_file.stem

        # 命名规范：kebab-case（硬错误）
        if not re.match(r'^[a-z][a-z0-9-]*$', file_name):
            errors.append(f'agents 文件名不合规: {agent_file.name}（应为 kebab-case）')

        # `-agent` 后缀：仅 info（acceptance-discipline 全用 `-agent` 命名是合理实践）
        if file_name.endswith('-agent'):
            info.append(
                f'agents 文件名带 -agent 后缀: {agent_file.name} — '
                f'AGENTS.md §5 推荐省略，但 acceptance-discipline 等聚合 skill 实际使用此命名'
            )


def check_scripts_dir(scripts_dir: Path, errors: List[str], warnings: List[str], info: List[str]):
    """检查 scripts 目录"""
    # 脚本数量：仅 info（无硬性依据，按需记录）
    script_files = [p for p in scripts_dir.rglob('*') if p.is_file()]
    if len(script_files) > 20:
        info.append(
            f'scripts/ 含 {len(script_files)} 个文件 — '
            f'未设硬上限，请按 CAPABILITY-MAP.md 共享能力注册表去重'
        )

    # subprocess + shell=True：仍保留 warnings（安全相关，不是风格）
    for script_file in script_files:
        content = script_file.read_text(errors='ignore')

        if script_file.suffix in ['.py', '.js', '.mjs', '.ts']:
            if 'subprocess' in content and 'shell=True' in content:
                warnings.append(f'{script_file.name}: 使用 subprocess + shell=True（参数化命令更安全）')


def check_structure_for_skill(skill_path: str) -> Dict:
    """统一接口 wrapper — 让 scripts/<name>-guard.py 可 import 调用.

    Args:
        skill_path: skill 目录路径

    Returns:
        {passed, errors, warnings, info}
    """
    return check_structure(skill_path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python scripts/skill-structure-guard.py skill-markets/<skill_name>")
        sys.exit(1)

    skill_path = sys.argv[1]
    result = check_structure(skill_path)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result['info']:
        print("\nℹ️ 提示（来自 vibe-coding-standards 软性指导，不阻断）:")
        for item in result['info']:
            print(f"  - {item}")

    if result['warnings']:
        print("\n⚠️ 警告:")
        for warn in result['warnings']:
            print(f"  - {warn}")

    if not result['passed']:
        print("\n❌ 结构检查失败:")
        for err in result['errors']:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\n✅ 结构检查通过（errors=0；warnings 来自安全建议，info 来自风格指导）")
        sys.exit(0)