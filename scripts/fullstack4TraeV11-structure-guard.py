#!/usr/bin/env python3
"""
scripts/fullstack4TraeV11-structure-guard.py — fullstack4TraeV11 structure aspect

定位（V11.5 §3 拆分方案 A — aspect 1/4）:
  校验 fullstack4TraeV11 自身 SKILL.md / agents / scripts / 必含子目录结构。
  注意:不直接 import skill-structure-guard.py,因为该脚本对 camelCase 目录
  (如 fullstack4TraeV11) 会硬阻断"目录名不合规"——这是历史既有事实。

  本 aspect 复用同款正则做实质校验（frontmatter / name / description / version /
  agents 文件名 kebab-case / scripts 安全提示），但容忍 skill 目录自身 camelCase。

用法:
  python scripts/fullstack4TraeV11-structure-guard.py fullstack4TraeV11

退出码:
  0 = PASS（errors=0）
  1 = BLOCK（errors≥1）
  2 = WARN（errors=0 但 warnings≥1）
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPTS_DIR.parent
SOFT_LINE_LIMIT = 350


def _check_skill_md(skill_md: Path, errors: list, warnings: list, info: list) -> None:
    content = skill_md.read_text(encoding='utf-8', errors='ignore')
    if not content.startswith('---'):
        errors.append('SKILL.md 缺少 YAML frontmatter（必须以 --- 开头）')
        return

    m = re.match(r'^---\n([\s\S]*?)\n---', content)
    if not m:
        errors.append('SKILL.md 缺少闭合 YAML frontmatter（---）')
        return
    yaml_content = m.group(1)

    # 必填字段
    for field in ('name', 'description'):
        if not re.search(rf'^{field}:', yaml_content, re.MULTILINE):
            errors.append(f'SKILL.md YAML frontmatter 缺少必需字段: {field}')

    # 推荐字段（warning）
    if not re.search(r'^version:', yaml_content, re.MULTILINE):
        warnings.append(
            'SKILL.md 缺 version 字段(AGENTS.md §1.1 推荐) — '
            '建议添加 version: x.y.z 以追踪演进'
        )

    # name 与目录名一致性 → info
    declared = re.search(r'^name:\s*(.+?)\s*$', yaml_content, re.MULTILINE)
    declared_name = declared.group(1).strip().strip('"').strip("'") if declared else None
    if declared_name and declared_name != skill_md.parent.name:
        info.append(
            f'SKILL.md 声明 name={declared_name!r} 与目录名 {skill_md.parent.name!r} 不一致'
        )

    # 行数软提示
    lines = content.count('\n') + 1
    if lines > SOFT_LINE_LIMIT:
        info.append(
            f'SKILL.md {lines} 行（> v2.5 软上限 {SOFT_LINE_LIMIT}）— '
            f'考虑提取 references/ 而非裁剪内容'
        )


def _check_agents_dir(agents_dir: Path, errors: list, info: list) -> None:
    if not agents_dir.exists():
        return
    for agent_file in agents_dir.glob('*.md'):
        if not re.match(r'^[a-z][a-z0-9-]*$', agent_file.stem):
            errors.append(f'agents 文件名不合规: {agent_file.name}（应为 kebab-case）')
        if agent_file.stem.endswith('-agent'):
            info.append(
                f'agents 文件名带 -agent 后缀: {agent_file.name} — AGENTS.md §5 推荐省略'
            )


def _check_scripts_dir(scripts_dir: Path, errors: list, warnings: list, info: list) -> None:
    if not scripts_dir.exists():
        return
    files = [p for p in scripts_dir.rglob('*') if p.is_file()]
    if len(files) > 20:
        info.append(f'scripts/ 含 {len(files)} 个文件 — 按 CAPABILITY-MAP.md 共享能力注册表去重')
    for script_file in files:
        if script_file.suffix not in ('.py', '.js', '.mjs', '.ts'):
            continue
        content = script_file.read_text(encoding='utf-8', errors='ignore')
        if 'subprocess' in content and 'shell=True' in content:
            warnings.append(f'{script_file.name}: 使用 subprocess + shell=True（参数化命令更安全）')


def check_fullstack4TraeV11_structure(skill_path: str) -> dict:
    """aspect 1/4: structure 自定义校验。"""
    skill_dir = Path(skill_path)
    errors: list = []
    warnings: list = []
    info: list = []

    if not skill_dir.exists():
        errors.append(f'技能目录不存在: {skill_path}')
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'info': info}

    # 容忍 camelCase 目录名（fullstack4TraeV11 / V9 / V10 / ponytail4Trae 同款约定）
    info.append(
        f'目录名 {skill_dir.name!r} 为 camelCase — V11 既有命名,允许(已记 info)'
    )

    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        errors.append('缺少 SKILL.md')
    else:
        _check_skill_md(skill_md, errors, warnings, info)

    _check_agents_dir(skill_dir / 'agents', errors, info)
    _check_scripts_dir(skill_dir / 'scripts', errors, warnings, info)

    return {
        'passed': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'info': info,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print('用法: python scripts/fullstack4TraeV11-structure-guard.py <skill-name-or-path>',
              file=sys.stderr)
        return 2
    arg = sys.argv[1]
    p = Path(arg)
    if not p.is_absolute():
        candidate = REPO_ROOT / 'skill-markets' / arg
        if candidate.exists():
            p = candidate
        elif (REPO_ROOT / arg).exists():
            p = REPO_ROOT / arg
        else:
            p = candidate  # 让 check 自己报"不存在"
    try:
        result = check_fullstack4TraeV11_structure(str(p))
    except Exception as exc:  # pragma: no cover
        result = {
            'passed': False,
            'errors': [f'守卫内部异常: {type(exc).__name__}: {exc}'],
            'warnings': [],
            'info': [],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get('info'):
        print('\nℹ️ info（不阻断）:')
        for item in result['info']:
            print(f'  - {item}')
    if result.get('warnings'):
        print('\n⚠️ warnings:')
        for w in result['warnings']:
            print(f'  - {w}')
    if not result.get('passed'):
        print('\n❌ structure 检查失败:')
        for err in result.get('errors', []):
            print(f'  - {err}')
        return 1
    print('\n✅ structure 检查通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
