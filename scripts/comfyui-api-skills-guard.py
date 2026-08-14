#!/usr/bin/env python3
"""
scripts/comfyui-api-skills-guard.py — comfyui-api-skills 专属守卫（2026-08-14 拆分方案 A 自动生成）

设计目的:
  每个 skill 在 scripts/<name>-guard.py 自带守卫（项目侧，非 skill 子目录）。
  合并以下 aspect 的检查结果: structure, security

用法:
  python scripts/comfyui-api-skills-guard.py comfyui-api-skills

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
_module_structure = _load_sibling_module("skill-structure-guard.py")
check_structure_fn = getattr(_module_structure, "check_structure_for_skill")
_module_security = _load_sibling_module("skill-security-guard.py")
check_security_fn = getattr(_module_security, "check_security_for_skill")


def check_comfyui_api_skills(skill_path: str) -> dict:
    """comfyui-api-skills 专属守卫 — 组合 2 个 aspect 的检查结果.

    Aspects: structure, security
    """
    results = [
        check_structure_fn(skill_path),
        check_security_fn(skill_path)
    ]
    merged = {'passed': True, 'errors': [], 'warnings': [], 'info': []}
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
    sys.exit(cli_main(check_comfyui_api_skills, 'structure'))
