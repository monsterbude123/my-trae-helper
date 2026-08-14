#!/usr/bin/env python3
"""
scripts/fullstack4TraeV11-gate-config-guard.py — fullstack4TraeV11 gate-config aspect

定位（V11.5 §3 拆分方案 A — aspect 3/4）:
  消费 skill-markets/fullstack4TraeV11/scripts/validate-gate-config.py 校验
  scaffolds/{nodejs,python}/files/gates/gate-config.json 的 L1-L4 四档 schema,
  防止 run-gate-level.py 静默消费坏 JSON。

  双 stack 都必须 exit 0,任一失败 → aspect BLOCK。

用法:
  python scripts/fullstack4TraeV11-gate-config-guard.py fullstack4TraeV11

退出码:
  0 = PASS（两 stack gate-config.json 都 exit 0）
  1 = BLOCK（任一 stack gate-config.json FAIL / 退出码非 0）
  2 = 参数错误
"""
from __future__ import annotations

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


def check_fullstack4TraeV11_gate_config(skill_path: str) -> dict:
    """aspect 3/4: gate-config.json schema 校验（两 stack）。"""
    errors: list = []
    warnings: list = []
    info: list = []

    skill_dir = Path(skill_path)
    if not skill_dir.exists():
        errors.append(f'技能目录不存在: {skill_path}')
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'info': info}

    vgc = skill_dir / 'scripts' / 'validate-gate-config.py'
    if not vgc.exists():
        errors.append(f'缺 validate-gate-config.py: {vgc}')
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'info': info}

    stacks = ('nodejs', 'python')
    checked = 0
    for stack in stacks:
        cfg = skill_dir / 'scaffolds' / stack / 'files' / 'gates' / 'gate-config.json'
        if not cfg.exists():
            errors.append(f'缺 gate-config.json: {cfg}')
            continue
        try:
            proc = subprocess.run(
                [sys.executable, str(vgc), '--config', str(cfg)],
                cwd=str(skill_dir),
                capture_output=True,
                text=True,
                timeout=60,
            )
        except Exception as exc:
            errors.append(f'validate-gate-config 调用异常({stack}): {type(exc).__name__}: {exc}')
            continue

        if proc.returncode != 0:
            snippet = (proc.stdout or '')[:300] + (proc.stderr or '')[:300]
            errors.append(
                f'gate-config.json schema 校验失败 ({stack}, exit {proc.returncode}): {snippet}'
            )
        else:
            info.append(f'gate-config.json schema 合法 ({stack})')
            checked += 1

    if checked == 0 and not errors:
        errors.append('未校验任何 gate-config.json')

    return {
        'passed': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'info': info,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print('用法: python scripts/fullstack4TraeV11-gate-config-guard.py <skill-name-or-path>',
              file=sys.stderr)
        return 2
    skill_dir = _resolve_skill_dir(sys.argv[1])
    try:
        result = check_fullstack4TraeV11_gate_config(str(skill_dir))
    except Exception as exc:  # pragma: no cover
        result = {
            'passed': False,
            'errors': [f'守卫内部异常: {type(exc).__name__}: {exc}'],
            'warnings': [],
            'info': [],
        }
    import json
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
        print('\n❌ gate-config 检查失败:')
        for err in result.get('errors', []):
            print(f'  - {err}')
        return 1
    print('\n✅ gate-config 检查通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
