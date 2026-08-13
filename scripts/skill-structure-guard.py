#!/usr/bin/env python3
"""
Skill Structure Guard — 技能结构守卫

检查维度: 目录结构 / 命名规范 / YAML frontmatter / 铁律数量
触发时机: pre-create (新建技能时)

Usage:
    python scripts/skill-structure-guard.py skill-markets/<skill_name>

注意: 与 skill-acceptance/scripts/verify.py 的关系
  - verify.py: check_frontmatter / check_scripts_boundary(轻量)
  - 本脚本: 行数 + 铁律数量(更细)
  - 互补,非冗余
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List


def check_structure(skill_path: str) -> Dict:
    """
    检查技能结构

    Args:
        skill_path: 技能目录路径

    Returns:
        {
            'passed': bool,
            'errors': List[str],
            'warnings': List[str]
        }
    """
    skill_dir = Path(skill_path)
    errors = []
    warnings = []

    if not skill_dir.exists():
        errors.append(f'技能目录不存在: {skill_path}')
        return {'passed': False, 'errors': errors, 'warnings': warnings}

    dir_name = skill_dir.name
    if not re.match(r'^[a-z][a-z0-9-]*$', dir_name):
        errors.append(f'目录名不合规: {dir_name}（应为 kebab-case，小写字母开头）')

    if len(dir_name) > 50:
        warnings.append(f'目录名过长: {dir_name}（建议 ≤ 50 字符）')

    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        errors.append('缺少 SKILL.md')
    else:
        check_skill_md(skill_md, errors, warnings)

    agents_dir = skill_dir / 'agents'
    if agents_dir.exists():
        check_agents_dir(agents_dir, errors, warnings)

    scripts_dir = skill_dir / 'scripts'
    if scripts_dir.exists():
        check_scripts_dir(scripts_dir, errors, warnings)

    return {
        'passed': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def check_skill_md(skill_md: Path, errors: List[str], warnings: List[str]):
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

            if re.search(r'^name:\s*' + re.escape(skill_md.parent.name), yaml_content, re.MULTILINE):
                pass
            else:
                warnings.append(f'SKILL.md 的 name 字段应与目录名一致: {skill_md.parent.name}')

    lines = content.count('\n') + 1
    if lines > 800:
        errors.append(f'SKILL.md 过长: {lines} 行（应 ≤ 800）')
    elif lines > 500:
        warnings.append(f'SKILL.md 较长: {lines} 行（建议 ≤ 500）')
    elif lines > 300:
        warnings.append(f'SKILL.md 较长: {lines} 行（建议 ≤ 300）')

    iron_rules = len(re.findall(r'^\d+\.\s+', content, re.MULTILINE))
    if iron_rules > 10:
        errors.append(f'铁律过多: {iron_rules} 条（应 ≤ 10）')


def check_agents_dir(agents_dir: Path, errors: List[str], warnings: List[str]):
    """检查 agents 目录"""
    for agent_file in agents_dir.glob('*.md'):
        file_name = agent_file.stem

        if file_name.endswith('-agent'):
            warnings.append(f'agents 文件名不应带 -agent 后缀: {agent_file.name}（已在 agents/ 目录内）')

        if not re.match(r'^[a-z][a-z0-9-]*$', file_name):
            errors.append(f'agents 文件名不合规: {agent_file.name}（应为 kebab-case）')


def check_scripts_dir(scripts_dir: Path, errors: List[str], warnings: List[str]):
    """检查 scripts 目录"""
    script_count = len(list(scripts_dir.rglob('*')))

    if script_count > 20:
        warnings.append(f'脚本过多: {script_count} 个文件（建议 ≤ 20）')

    for script_file in scripts_dir.rglob('*'):
        if script_file.is_file():
            content = script_file.read_text(errors='ignore')

            if script_file.suffix in ['.py', '.js', '.mjs', '.ts']:
                if 'subprocess' in content and 'shell=True' in content:
                    warnings.append(f'{script_file.name}: 使用 subprocess + shell=True（参数化命令更安全）')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python scripts/skill-structure-guard.py skill-markets/<skill_name>")
        sys.exit(1)

    skill_path = sys.argv[1]
    result = check_structure(skill_path)

    print(json.dumps(result, indent=2))

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
        print("\n✅ 结构检查通过")
        sys.exit(0)