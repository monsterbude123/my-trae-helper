#!/usr/bin/env python3
"""
Skill Capability Guard — 技能能力守卫

检查维度: 能力去重 / CAPABILITY-MAP.md 同步
触发时机: pre-create / pre-update / pre-delete

Usage:
    python scripts/skill-capability-guard.py skill-markets/<skill_name> [script_name]

注意: 与 skill-acceptance/scripts/verify.py 的关系
  - verify.py: check_capability_map(完整路径匹配,边界更严)
  - 本脚本: 单脚本参数 + basename 匹配(增量场景更灵活)
  - 互补,非冗余
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

CAPABILITY_MAP = Path(__file__).parent.parent / "skill-markets" / "CAPABILITY-MAP.md"


def check_capability_duplicate(skill_path: str, script_name: Optional[str] = None) -> Dict:
    """
    检查能力去重

    Args:
        skill_path: 技能目录路径
        script_name: 脚本名（可选）

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

    if not CAPABILITY_MAP.exists():
        warnings.append('CAPABILITY-MAP.md 不存在，跳过去重检查')
        return {'passed': True, 'errors': errors, 'warnings': warnings}

    capability_content = CAPABILITY_MAP.read_text()

    shared_full, shared_basename = extract_shared_scripts(capability_content)

    if script_name:
        if script_name in shared_full or script_name in shared_basename:
            errors.append(f'脚本 {script_name} 已存在于共享能力注册表，请复用')
    else:
        scripts_dir = skill_dir / 'scripts'
        if scripts_dir.exists():
            for script_file in scripts_dir.glob('*'):
                if not script_file.is_file() or script_file.name == 'README.md':
                    continue
                if script_file.name in shared_basename:
                    errors.append(f'脚本 {script_file.name} 已存在于共享能力注册表，请复用')

    return {
        'passed': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def check_capability_map_sync(skill_path: str) -> Dict:
    """
    检查 CAPABILITY-MAP.md 同步

    Args:
        skill_path: 技能目录路径

    Returns:
        {
            'passed': bool,
            'errors': List[str],
            'warnings': List[str],
            'missing_entries': List[str]
        }
    """
    skill_dir = Path(skill_path)
    errors = []
    warnings = []
    missing_entries = []

    if not skill_dir.exists():
        errors.append(f'技能目录不存在: {skill_path}')
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'missing_entries': missing_entries}

    if not CAPABILITY_MAP.exists():
        warnings.append('CAPABILITY-MAP.md 不存在')
        return {'passed': True, 'errors': errors, 'warnings': warnings, 'missing_entries': missing_entries}

    skill_name = skill_dir.name

    capability_content = CAPABILITY_MAP.read_text()

    if not re.search(rf'\[\s*{re.escape(skill_name)}\s*\]', capability_content):
        missing_entries.append(f'技能 {skill_name} 未在 CAPABILITY-MAP.md 中注册')

    skill_md = skill_dir / 'SKILL.md'
    if skill_md.exists():
        content = skill_md.read_text()
        meta = parse_yaml_frontmatter(content)

        if meta.get('requires'):
            requires = meta['requires']
            skills = requires.get('skills', [])
            optional = requires.get('optional', [])

            all_deps = (skills if isinstance(skills, list) else [skills] if skills else []) + \
                       (optional if isinstance(optional, list) else [optional] if optional else [])

            for dep in all_deps:
                if dep and not re.search(rf'\[\s*{re.escape(dep)}\s*\]', capability_content):
                    warnings.append(f'依赖 {dep} 未在 CAPABILITY-MAP.md 中注册')

    passed = len(missing_entries) == 0

    return {
        'passed': passed,
        'errors': errors,
        'warnings': warnings,
        'missing_entries': missing_entries
    }


def extract_shared_scripts(capability_content: str) -> List[str]:
    """从 CAPABILITY-MAP.md 提取已注册脚本(完整路径 + basename)

    返回:
        - shared_full: 完整相对路径列表,如 ['vision-audit/scripts/vision-audit.mjs']
        - shared_basename: 仅 basename 列表,如 ['vision-audit.mjs']
    """
    shared_full = []
    shared_basename = []

    # 找「共享能力注册表」章节
    shared_section = re.search(r'## 二、共享能力注册表(.*?)##', capability_content, re.DOTALL)
    if not shared_section:
        shared_section = re.search(r'## 二、共享能力注册表(.*)', capability_content, re.DOTALL)

    if not shared_section:
        return [], []

    section_content = shared_section.group(1)

    # 提取 `` `path/to/script.py` `` 形式的反引号引用
    script_matches = re.findall(r'`([^`]*\.(?:py|mjs|sh|ps1))`', section_content)

    for full_path in script_matches:
        # 过滤掉 examples/ logs/ 等非共享脚本
        if any(p in full_path for p in ['logs/', 'examples/', 'auto_reports/']):
            continue
        shared_full.append(full_path)
        shared_basename.append(Path(full_path).name)

    return shared_full, shared_basename


def parse_yaml_frontmatter(content: str) -> Dict:
    """解析 YAML frontmatter"""
    match = re.match(r'^---\n([\s\S]*?)\n---', content)
    if not match:
        return {}

    yaml_content = match.group(1)
    meta = {}

    for line in yaml_content.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if value.startswith('[') and value.endswith(']'):
                meta[key] = [s.strip() for s in value[1:-1].split(',')]
            else:
                meta[key] = value

    return meta


def check_capability_for_skill(skill_path: str) -> Dict:
    """统一接口 wrapper — 让 scripts/<name>-guard.py 可 import 调用.

    Args:
        skill_path: skill 目录路径

    Returns:
        {passed, errors, warnings, info}
    """
    r1 = check_capability_duplicate(skill_path)
    r2 = check_capability_map_sync(skill_path)
    errors = []
    warnings = []
    info = []
    for src in (r1, r2):
        errors.extend(src.get('errors') or [])
        warnings.extend(src.get('warnings') or [])
        info.extend(src.get('missing_entries') or [])
    return {
        'passed': r1.get('passed', False) and r2.get('passed', False),
        'errors': errors,
        'warnings': warnings,
        'info': info,
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python scripts/skill-capability-guard.py skill-markets/<skill_name> [script_name]")
        sys.exit(1)

    skill_path = sys.argv[1]
    script_name = sys.argv[2] if len(sys.argv) > 2 else None

    print("=== 能力去重检查 ===")
    result1 = check_capability_duplicate(skill_path, script_name)
    print(json.dumps(result1, indent=2))

    print("\n=== CAPABILITY-MAP.md 同步检查 ===")
    result2 = check_capability_map_sync(skill_path)
    print(json.dumps(result2, indent=2))

    if result1['warnings'] or result2['warnings']:
        print("\n⚠️ 警告:")
        for warn in result1['warnings'] + result2['warnings']:
            print(f"  - {warn}")

    if not result1['passed'] or not result2['passed']:
        print("\n❌ 检查失败:")
        for err in result1['errors'] + result2['errors'] + result2['missing_entries']:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\n✅ 检查通过")
        sys.exit(0)