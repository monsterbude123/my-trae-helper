#!/usr/bin/env python3
"""
scripts/forge-skill-guard.py — Skill 专属守卫脚本模板生成器（2026-08-14 拆分方案 A）

设计目的:
  把 47 个 skill 的 scripts/<name>-guard.py 生成工作从"每个 agent 写全文"
  降到"传 1 个 skill 名 → 生成 1 个固定模板文件"。
  防止 47 份 guard 风格漂移 + 防止 sub-agent 互相冲突。

用法:
  # 生成 1 个
  python scripts/forge-skill-guard.py coding-xinfa

  # 生成多个(按空格分隔)
  python scripts/forge-skill-guard.py coding-xinfa goal-mode trae-professional

  # 从注册表批量生成全部 47 个
  python scripts/forge-skill-guard.py --all

  # Dry-run: 只打印生成内容,不写盘
  python scripts/forge-skill-guard.py --dry-run coding-xinfa

生成内容:
  scripts/<name>-guard.py 内含:
    1. 导入 _guard_lib 共享工具
    2. 继承 3 个共享守卫的检查(根据 SKILL.md 含 scripts/agents/ 决定组合)
    3. CLI 主入口: sys.exit(cli_main(check_fn, '<aspect>'))

检查策略(根据 skill 特征自动选择 1-N 个共享检查):
  - 纯 SKILL.md 文档型 skill      → structure-only
  - 含 scripts/ 的 skill          → structure + security
  - 含 agents/ 的 skill           → structure + capability

退出码: 0 = 全部生成成功
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_MARKETS = REPO_ROOT / 'skill-markets'
GUARDS_DIR = REPO_ROOT / 'scripts'
REGISTRY = REPO_ROOT / 'registry' / 'skills.yaml'

# 守卫脚本的合法字符（kebab-case + 历史大写命名）
# 设计目的:
#   AGENTS.md §1 要求 kebab-case,但 5 个历史 skill 名含大写字母(fullstack4TraeV9/V10/V11,
#   gitnexus4Trae, ponytail4Trae)是合法目录命名,rename 会破坏 CLI 已装的
#   symlink,因此放宽 KEBAB_RE 接受大写字母 + 数字开头。
#   详见 skill-markets/<name>/SKILL.md frontmatter name 字段(可与目录名不一致,如
#   fullstack4TraeV11/SKILL.md 声明 name: fullstack4traev11)。
KEBAB_RE = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]*$')


def detect_aspects(skill_dir: Path) -> list:
    """根据 skill 目录特征决定要调用哪些共享检查.

    Returns:
        列表,每个元素是 {'label': str, 'check_fn': str, 'import': str}
    """
    aspects = [{'label': 'structure', 'check_fn': 'check_structure_for_skill',
                'module_file': 'skill-structure-guard.py'}]

    has_scripts = (skill_dir / 'scripts').is_dir()
    has_agents = (skill_dir / 'agents').is_dir()

    if has_scripts:
        aspects.append({
            'label': 'security',
            'check_fn': 'check_security_for_skill',
            'module_file': 'skill-security-guard.py',
        })
    # capability 检查 2026-08-14 拆分后降级:
    #   原 capability 守卫检查"脚本 basename 重复",现在每个 skill 的 scripts/<name>-guard.py
    #   是项目侧唯一名,不会跨 skill 重复。CAPABILITY-MAP 同步检查继续保留(它检查的是
    #   skill 名是否在 CAPABILITY-MAP.md 注册,而非 guard 脚本名),但移到 CAPABILITY-MAP.md
    #   本身用 manifest-assert 自动验证,不再作为 per-skill guard 维度。
    #   → 这里不追加 capability aspect
    _ = has_agents  # 暂时保留 has_agents 探测供未来扩展

    return aspects


def _stub_function(aspect: str) -> str:
    """为未实现 check_fn 的 aspect 生成 stub.

    实际拆分完成后,这个 stub 由后续 commit 替换为真实实现.
    现在保证 47 个文件先落地,守卫脚本可以无 op PASS.
    """
    return f'''def { {
        'structure': 'check_structure',
        'security': 'check_security_for_skill',
        'capability': 'check_capability_for_skill',
    }.get(aspect, 'check_' + aspect) }(skill_path: str) -> dict:
    """stub — 待后续 commit 拆分共享守卫时填入真实实现."""
    return {{'passed': True, 'errors': [], 'warnings': [], 'info': [f'stub: {aspect} 待拆分']}}
'''


def render_guard_script(skill_name: str, aspects: list) -> str:
    """生成 scripts/<name>-guard.py 的完整内容."""
    label_main = aspects[0]['label'] if aspects else 'guard'
    aspect_names = [a['label'] for a in aspects]

    # loader 块：用 importlib 加载连字符文件名（Python 不支持直接 import hyphen 文件名）
    loader_block_lines = []
    for a in aspects:
        loader_block_lines.append(
            f'_module_{a["label"]} = _load_sibling_module("{a["module_file"]}")\n'
            f'check_{a["label"]}_fn = getattr(_module_{a["label"]}, "{a["check_fn"]}")'
        )
    loader_block = '\n'.join(loader_block_lines)

    # check 调用块
    check_calls = ',\n        '.join(f'check_{a["label"]}_fn(skill_path)' for a in aspects)

    return f'''#!/usr/bin/env python3
"""
scripts/{skill_name}-guard.py — {skill_name} 专属守卫（2026-08-14 拆分方案 A 自动生成）

设计目的:
  每个 skill 在 scripts/<name>-guard.py 自带守卫（项目侧，非 skill 子目录）。
  合并以下 aspect 的检查结果: {", ".join(aspect_names)}

用法:
  python scripts/{skill_name}-guard.py {skill_name}

退出码:
  0 = PASS（errors=0, warnings=0）
  1 = BLOCK（errors≥1）
  2 = WARN（errors=0 但 warnings≥1）

禁止:
  - 禁止 import skill-markets/<pkg>/scripts/*（与 AGENTS.md §1.11 冲突）
  - 禁止修改本文件的 import 顺序（与 _guard_lib 契约不一致会导致 guard-router 失败）
"""
import importlib.util
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent

def _load_sibling_module(filename: str):
    """加载同目录下的连字符文件名模块（Python import 不支持 hyphen 文件名）."""
    spec = importlib.util.spec_from_file_location(
        filename.replace('.py', ''),
        _SCRIPTS_DIR / filename
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# 共享守卫加载（连字符文件名用 importlib）
{loader_block}


def check_{skill_name.replace("-", "_")}(skill_path: str) -> dict:
    """{skill_name} 专属守卫 — 组合 {len(aspects)} 个 aspect 的检查结果.

    Aspects: {", ".join(aspect_names)}
    """
    results = [
        {check_calls}
    ]
    merged = {{'passed': True, 'errors': [], 'warnings': [], 'info': []}}
    for r in results:
        if not r.get('passed', False):
            merged['passed'] = False
        merged['errors'].extend(r.get('errors') or [])
        merged['warnings'].extend(r.get('warnings') or [])
        merged['info'].extend(r.get('info') or [])
    # 去重 errors / warnings / info（保持顺序）
    seen = set()
    for key in ('errors', 'warnings', 'info'):
        deduped = []
        for item in merged[key]:
            if item not in seen:
                deduped.append(item)
                seen.add(item)
        merged[key] = deduped
    return merged


# 主入口 — 统一通过 _guard_lib 输出 JSON + exit code
from _guard_lib import cli_main

if __name__ == '__main__':
    sys.exit(cli_main(check_{skill_name.replace("-", "_")}, '{label_main}'))
'''


def generate_for_skill(skill_name: str, dry_run: bool = False) -> bool:
    """为 1 个 skill 生成 scripts/<name>-guard.py. 成功返回 True."""
    if not KEBAB_RE.match(skill_name):
        print(f'❌ 非法 skill 名(非 kebab-case): {skill_name}', file=sys.stderr)
        return False

    skill_dir = SKILL_MARKETS / skill_name
    if not skill_dir.is_dir():
        print(f'❌ skill 目录不存在: {skill_dir}', file=sys.stderr)
        return False

    target = GUARDS_DIR / f'{skill_name}-guard.py'
    aspects = detect_aspects(skill_dir)
    content = render_guard_script(skill_name, aspects)

    if dry_run:
        print(f'--- DRY RUN: {target} ---')
        print(content)
        return True

    target.write_text(content, encoding='utf-8')
    print(f'✅ 生成: {target.relative_to(REPO_ROOT)} (aspects: {[a["label"] for a in aspects]})')
    return True


def list_skills_from_registry() -> list:
    """从 registry/skills.yaml 解析所有 skill 名."""
    if not REGISTRY.exists():
        return []
    text = REGISTRY.read_text(encoding='utf-8')
    return [m.group(1).strip() for m in re.finditer(r'^\s*- skill:\s*(.+)$', text, re.MULTILINE)]


def main():
    parser = argparse.ArgumentParser(description='Skill 专属守卫脚本模板生成器')
    parser.add_argument('skills', nargs='*', help='skill 名(可多个)')
    parser.add_argument('--all', action='store_true', help='从注册表批量生成全部')
    parser.add_argument('--dry-run', action='store_true', help='只打印不写盘')
    args = parser.parse_args()

    targets = list(args.skills)
    if args.all:
        targets = list_skills_from_registry()
    if not targets:
        parser.error('至少传 1 个 skill 名,或用 --all')

    ok = 0
    fail = 0
    for name in targets:
        if generate_for_skill(name, dry_run=args.dry_run):
            ok += 1
        else:
            fail += 1

    print(f'\n汇总: ✅ {ok} 成功, ❌ {fail} 失败, 总计 {len(targets)}')
    sys.exit(0 if fail == 0 else 1)


if __name__ == '__main__':
    main()