#!/usr/bin/env python3
"""
scripts/fullstack4TraeV11-guard.py — fullstack4TraeV11 专属守卫主 wrapper

设计目的（V11.5 §3 拆分方案 A — 2026-08-14 升级）:
  组合 4 个 aspect 子脚本的检查结果:
    1. structure   → scripts/fullstack4TraeV11-structure-guard.py
    2. flow        → scripts/fullstack4TraeV11-flow-guard.py
    3. gate-config → scripts/fullstack4TraeV11-gate-config-guard.py
    4. trap        → scripts/fullstack4TraeV11-trap-guard.py

  每个 aspect 独立子进程隔离,任一 BLOCK → 整体 fail。
  不直接 import skill-markets/fullstack4TraeV11/scripts/*（与 AGENTS.md §1.11 冲突）。

用法:
  python scripts/fullstack4TraeV11-guard.py fullstack4TraeV11

退出码:
  0 = PASS（4 个 aspect 全部 PASS）
  1 = BLOCK（任一 aspect FAIL）
  2 = WARN（errors=0 但 warnings≥1）

禁止:
  - 禁止 import skill-markets/<pkg>/scripts/*（与 AGENTS.md §1.11 冲突）
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPTS_DIR.parent

# 4 个 aspect 子脚本（顺序敏感：structure → flow → gate-config → trap）
ASPECTS = [
    ('structure', 'fullstack4TraeV11-structure-guard.py'),
    ('flow', 'fullstack4TraeV11-flow-guard.py'),
    ('gate-config', 'fullstack4TraeV11-gate-config-guard.py'),
    ('trap', 'fullstack4TraeV11-trap-guard.py'),
]


def _run_aspect(label: str, script_name: str, skill_arg: str) -> dict:
    """调单个 aspect 子脚本,解析 stdout 第一行 JSON;失败兜底为 errors。"""
    script_path = _SCRIPTS_DIR / script_name
    if not script_path.exists():
        return {
            'aspect': label,
            'passed': False,
            'errors': [f'aspect 子脚本不存在: {script_name}'],
            'warnings': [],
            'info': [],
        }
    try:
        # Windows 默认 cp1252 解码会丢失中文/emoji,强制 UTF-8
        proc = subprocess.run(
            [sys.executable, str(script_path), skill_arg],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300,
        )
    except Exception as exc:
        return {
            'aspect': label,
            'passed': False,
            'errors': [f'aspect 调用异常: {type(exc).__name__}: {exc}'],
            'warnings': [],
            'info': [],
        }

    # aspect 子脚本退出码: 0=PASS, 1=BLOCK, 2=WARN/参数错
    aspect_passed = proc.returncode == 0
    aspect_warn = proc.returncode == 2

    # 解析多行 JSON（aspect 子脚本用 json.dumps(..., indent=2),需 brace matching）
    parsed: dict = {}
    stdout = proc.stdout or ''
    start = stdout.find('{')
    if start >= 0:
        depth = 0
        end = -1
        for i in range(start, len(stdout)):
            ch = stdout[i]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end > start:
            try:
                parsed = json.loads(stdout[start:end])
            except Exception:
                parsed = {}

    if not parsed:
        return {
            'aspect': label,
            'passed': False,
            'errors': [f'aspect {label} 输出未含可解析 JSON（exit={proc.returncode}）'],
            'warnings': [],
            'info': [],
        }

    # 以子脚本退出码为权威,JSON 仅用于 errors / warnings / info 透传
    parsed['aspect'] = label
    if not aspect_passed and not aspect_warn:
        parsed['passed'] = False
        # 若 JSON 里没 errors 但 exit 非 0 → 兜底
        if not parsed.get('errors'):
            snippet = (proc.stdout or '')[-400:] + (proc.stderr or '')[-200:]
            parsed['errors'] = [f'aspect {label} exit={proc.returncode}（无 JSON errors）\n{snippet}']
    return parsed


def check_fullstack4TraeV11(skill_path: str) -> dict:
    """组合 4 个 aspect 的检查结果。

    Args:
        skill_path: skill 目录路径（绝对路径或 skill 名）

    Returns:
        {passed, errors, warnings, info, aspects: [...]}
    """
    aspects_results = [
        _run_aspect(label, script_name, skill_path)
        for label, script_name in ASPECTS
    ]

    merged = {'passed': True, 'errors': [], 'warnings': [], 'info': [], 'aspects': aspects_results}
    for r in aspects_results:
        if not r.get('passed', False):
            merged['passed'] = False
        # errors 加 aspect 前缀,便于定位失败环节
        for e in r.get('errors') or []:
            merged['errors'].append(f"[{r.get('aspect', '?')}] {e}")
        for w in r.get('warnings') or []:
            merged['warnings'].append(f"[{r.get('aspect', '?')}] {w}")
        for i in r.get('info') or []:
            merged['info'].append(f"[{r.get('aspect', '?')}] {i}")
    return merged


def main() -> int:
    if len(sys.argv) < 2:
        print('用法: python scripts/fullstack4TraeV11-guard.py <skill-name-or-path>',
              file=sys.stderr)
        return 2
    skill_arg = sys.argv[1]
    try:
        result = check_fullstack4TraeV11(skill_arg)
    except Exception as exc:  # pragma: no cover
        result = {
            'passed': False,
            'errors': [f'守卫内部异常: {type(exc).__name__}: {exc}'],
            'warnings': [],
            'info': [],
            'aspects': [],
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
        print('\n❌ fullstack4TraeV11 守卫 BLOCK:')
        for err in result.get('errors', []):
            print(f'  - {err}')
        return 1
    print('\n✅ fullstack4TraeV11 守卫 PASS（4 aspects: structure+flow+gate-config+trap）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
