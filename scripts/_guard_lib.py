#!/usr/bin/env python3
"""
scripts/_guard_lib.py — 所有 skill 守卫脚本共用的工具库（2026-08-14 拆分方案 A）

设计目的:
  把 3 个共享守卫脚本(skill-structure-guard.py / skill-security-guard.py /
  skill-capability-guard.py)共用的"主入口"逻辑抽出来,让每个 skill 的专属
  scripts/<name>-guard.py 只写自己的检查逻辑,主入口统一继承本工具。

  这样:
  - 47 个 skill-guard.py 风格统一(主入口 0 重复)
  - 输出 JSON / exit code 0|1|2 永远一致(契约稳定)
  - guard-router.mjs 不需要改协议
  - 后续 guard-smith 加新 skill 时,只需调用 scripts/forge-skill-guard.py 生成

禁止:
  - 本文件不能 import skill-markets/<pkg>/scripts/*(那是 skill 自己的子目录,与 §1.11 冲突)
  - 本文件不能依赖 yaml 包外其他三方库(标准库优先,§1.7 ponytail)

用法 (skill-guard.py 内):
    from _guard_lib import run_guard

    def my_check(skill_path: str) -> dict:
        return {'passed': True, 'errors': [], 'warnings': [], 'info': []}

    if __name__ == '__main__':
        run_guard('my-skill', my_check, guard_label='structure')
"""

import sys
import json
from pathlib import Path
from typing import Callable, Dict, List, Any

# scripts/<name>-guard.py 的输入约定: 第 1 个 argv = skill 名
# runner 通过 guard-router.mjs 传入绝对路径 skill-markets/<name>
REPO_ROOT = Path(__file__).resolve().parent.parent


def _resolve_skill_path(arg: str) -> Path:
    """接收 skill 名或绝对路径,统一解析为 Path.

    Args:
        arg: skill 名(如 "coding-xinfa") 或完整路径(如 "skill-markets/coding-xinfa")

    Returns:
        解析后的 skill 目录绝对路径
    """
    p = Path(arg)
    if p.is_absolute():
        return p
    # 相对路径: 优先按 REPO_ROOT/skill-markets/<arg> 解析
    if (REPO_ROOT / 'skill-markets' / arg).exists():
        return REPO_ROOT / 'skill-markets' / arg
    if (REPO_ROOT / arg).exists():
        return REPO_ROOT / arg
    # 不存在也返回猜测的路径(让 check 函数自己报错)
    return REPO_ROOT / 'skill-markets' / arg


def _format_output(result: Dict[str, Any], guard_label: str, skill_name: str) -> int:
    """统一输出格式 + 返回 exit code.

    Args:
        result: {passed, errors, warnings, info}
        guard_label: 'structure' | 'security' | 'capability' | ...
        skill_name: 用于日志抬头

    Returns:
        0 = PASS, 1 = BLOCK, 2 = WARN-only
    """
    print(json.dumps(result, indent=2, ensure_ascii=False))

    info = result.get('info') or []
    warnings = result.get('warnings') or []
    errors = result.get('errors') or []
    passed = bool(result.get('passed', False))

    if info:
        print('\nℹ️ 提示（不阻断）:')
        for item in info:
            print(f'  - {item}')

    if warnings:
        print('\n⚠️ 警告:')
        for w in warnings:
            print(f'  - {w}')

    if not passed:
        print(f'\n❌ {guard_label} 检查失败 [{skill_name}]:')
        for err in errors:
            print(f'  - {err}')
        return 1
    # passed=True 时,warnings 仅记录不阻断(返回 0 而非 2)
    # 理由:wrapper 内 warning 是合规建议(如 SKILL.md 缺 version),不影响 gate 决策。
    # 真正需要 BLOCK 的场景由 passed=False 触发。
    print(f'\n✅ {guard_label} 检查通过 [{skill_name}]' + (f' (含 {len(warnings)} 条 warnings)' if warnings else ''))
    return 0


def run_guard(skill_name: str, check_fn: Callable[[str], Dict[str, Any]], guard_label: str = 'guard') -> int:
    """守卫脚本主入口统一封装.

    Args:
        skill_name: skill 名(从 sys.argv[1] 传入)
        check_fn: 实际检查函数,接收 skill 路径字符串,返回 {passed, errors, warnings, info}
        guard_label: 输出用标签(默认 'guard')

    Returns:
        exit code (0/1/2)
    """
    skill_path = _resolve_skill_path(skill_name)
    try:
        result = check_fn(str(skill_path))
    except Exception as e:
        result = {
            'passed': False,
            'errors': [f'守卫内部异常: {type(e).__name__}: {e}'],
            'warnings': [],
            'info': [],
        }
    return _format_output(result, guard_label, skill_name)


def cli_main(check_fn: Callable[[str], Dict[str, Any]], guard_label: str = 'guard') -> int:
    """CLI 入口辅助: 解析 sys.argv[1] 后调用 run_guard.

    用法:
        if __name__ == '__main__':
            sys.exit(cli_main(check_my_skill, 'my-aspect'))
    """
    if len(sys.argv) < 2:
        print(f'用法: python scripts/<skill>-guard.py <skill-name>')
        sys.exit(1)
    return run_guard(sys.argv[1], check_fn, guard_label)