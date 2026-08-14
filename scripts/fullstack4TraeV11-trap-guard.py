#!/usr/bin/env python3
"""
scripts/fullstack4TraeV11-trap-guard.py — fullstack4TraeV11 trap aspect

定位（V11.5 §3 拆分方案 A — aspect 4/4）:
  消费 skill-markets/fullstack4TraeV11/tests/ 下 pytest 收集（标记 trap）,
  断言所有 trap 反例测试 PASS,作为门禁硬化兜底。

  trap 测试源自 references/trap-instructions.yaml,固化反例可被程序化校验。
  跨平台:子进程用 sys.executable,不带硬编码路径。

用法:
  python scripts/fullstack4TraeV11-trap-guard.py fullstack4TraeV11

退出码:
  0 = PASS（pytest exit 0）
  1 = BLOCK（pytest FAIL / exit 非 0）
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


def check_fullstack4TraeV11_trap(skill_path: str) -> dict:
    """aspect 4/4: trap 反例测试（pytest -m trap）。"""
    errors: list = []
    warnings: list = []
    info: list = []

    skill_dir = Path(skill_path)
    if not skill_dir.exists():
        errors.append(f'技能目录不存在: {skill_path}')
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'info': info}

    tests_dir = skill_dir / 'tests'
    if not tests_dir.exists():
        errors.append(f'缺 tests/ 目录: {tests_dir}')
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'info': info}

    try:
        # 跨平台：用当前 Python 解释器,不带硬编码路径
        proc = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests', '-m', 'trap', '-v', '--tb=short'],
            cwd=str(skill_dir),
            capture_output=True,
            text=True,
            timeout=300,
        )
    except Exception as exc:
        errors.append(f'pytest 调用异常: {type(exc).__name__}: {exc}')
        return {'passed': False, 'errors': errors, 'warnings': warnings, 'info': info}

    # pytest exit 0 = 全 PASS；exit 1 = 有 FAIL；exit 2 = 测试中断
    if proc.returncode != 0:
        snippet = (proc.stdout or '')[-2000:] + '\n' + (proc.stderr or '')[-1000:]
        errors.append(
            f'pytest -m trap 退出码 {proc.returncode}（trap 反例 FAIL，期望全 PASS）\n{snippet}'
        )
    else:
        # 解析末尾 "X passed" 行
        for line in (proc.stdout or '').splitlines():
            if 'passed' in line and ('deselected' in line or line.strip().endswith('passed')):
                info.append(f'pytest trap: {line.strip()}')
                break
        else:
            info.append('pytest trap: 全 PASS（exit 0）')

    return {
        'passed': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'info': info,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print('用法: python scripts/fullstack4TraeV11-trap-guard.py <skill-name-or-path>',
              file=sys.stderr)
        return 2
    skill_dir = _resolve_skill_dir(sys.argv[1])
    try:
        result = check_fullstack4TraeV11_trap(str(skill_dir))
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
        print('\n❌ trap 检查失败:')
        for err in result.get('errors', []):
            print(f'  - {err}')
        return 1
    print('\n✅ trap 检查通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
