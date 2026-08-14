#!/usr/bin/env python3
"""
scripts/fullstack4TraeV11-flow-guard.py — fullstack4TraeV11 flow aspect

定位（V11.5 §3 拆分方案 A — aspect 2/4）:
  消费 skill-markets/fullstack4TraeV11/scripts/run-all-guards.py --validate-only,
  断言 13/13 PASS + 五表 schema 合法（registry/{gates,guards,state-machine,repair-flow,stacks}.yaml）。

  本 aspect 仅做白名单消费:不修改 skill 子目录任何文件,只把脚本当 CLI 调用。

用法:
  python scripts/fullstack4TraeV11-flow-guard.py fullstack4TraeV11

退出码:
  0 = PASS（run-all-guards 13/13 PASS 且 exit 0）
  1 = BLOCK（run-all-guards FAIL / 退出码非 0）
  2 = 参数错误（skill 目录不存在）
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPTS_DIR.parent


def _resolve_skill_dir(arg: str) -> Path:
    p = Path(arg)
    if p.is_absolute():
        return p
    candidate = REPO_ROOT / 'skill-markets' / arg
    if candidate.exists():
        return candidate
    if (REPO_ROOT / arg).exists():
        return REPO_ROOT / arg
    return candidate


def check_fullstack4TraeV11_flow(skill_path: str) -> dict:
    """aspect 2/4: flow 完整性（13 stage 五表 schema）。"""
    errors: list = []
    warnings: list = []
    info: list = []

    skill_dir = Path(skill_path)
    if not skill_dir.exists():
        errors.append(f'技能目录不存在: {skill_path}')
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'info': info}

    run_all_guards = skill_dir / 'scripts' / 'run-all-guards.py'
    if not run_all_guards.exists():
        errors.append(f'缺 run-all-guards.py: {run_all_guards}')
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'info': info}

    try:
        proc = subprocess.run(
            [sys.executable, str(run_all_guards), '--validate-only', '--json'],
            cwd=str(skill_dir),
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception as exc:
        errors.append(f'run-all-guards.py 调用异常: {type(exc).__name__}: {exc}')
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'info': info}

    if proc.returncode != 0:
        snippet = (proc.stdout or '')[:400] + (proc.stderr or '')[:400]
        errors.append(
            f'run-all-guards.py --validate-only 退出码 {proc.returncode}'
            f'（期望 0 表示 13/13 PASS + 五表 schema 合法）\n{snippet}'
        )
        info.append('run-all-guards 退出非零：registry/五表 schema 或 gate 数量不符')
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'info': info}

    # 解析 JSON 摘要,校验 pass=13, fail=0
    try:
        summary = json.loads(proc.stdout)
        total = summary.get('summary', {}).get('total')
        passed = summary.get('summary', {}).get('pass')
        failed = summary.get('summary', {}).get('fail')
        expected = summary.get('summary', {}).get('expected')
        if expected != 13 or total != 13 or passed != 13 or failed != 0:
            errors.append(
                f'run-all-guards 摘要异常: total={total} pass={passed} '
                f'fail={failed} expected={expected}'
            )
        else:
            info.append('run-all-guards 13/13 PASS（13 stage 五表 schema 合法）')
    except Exception as exc:
        warnings.append(f'run-all-guards JSON 摘要解析失败: {exc}')

    return {
        'passed': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'info': info,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print('用法: python scripts/fullstack4TraeV11-flow-guard.py <skill-name-or-path>',
              file=sys.stderr)
        return 2
    skill_dir = _resolve_skill_dir(sys.argv[1])
    try:
        result = check_fullstack4TraeV11_flow(str(skill_dir))
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
        print('\n❌ flow 检查失败:')
        for err in result.get('errors', []):
            print(f'  - {err}')
        return 1
    print('\n✅ flow 检查通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
