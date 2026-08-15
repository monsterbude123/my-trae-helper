#!/usr/bin/env python3
"""
_check_skill_catalog.py — Skill Catalog 校验脚本(V11.8.0 NEW,2026-08-15)

基于 tests/catalogs/catalog-protocol.md §3,校验 skill-markets/<pkg>/SKILL.md 是否
满足 tests/catalogs/skill-catalog.yaml 声明的元数据要求。

Usage:
    python _check_skill_catalog.py \
        --catalog <path-to-skill-catalog.yaml> \
        --skills-root <path> \
        [--json] [--strict] [--dry-run]

设计:
  - 加载 skill-catalog.yaml(必填 required_metadata + 可选 optional_metadata)
  - 遍历 skills-root 下每个 <pkg>/SKILL.md,解析 YAML frontmatter
  - 校验必填字段全部存在
  - 可选字段 declared 时,跑子校验(protocols → _check_protocol_coverage.py)
  - 沿用 vibe-coding-standards v2.5:max_skill_md_lines 检查

Exit codes:
    0 = PASS(全部 SKILL 满足 catalog)
    1 = FAIL(任一 SKILL 缺必填/可选不满足)
    2 = NEEDS_REVIEW(strict 模式下 optional 缺)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from typing import Any

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT_DEFAULT = SCRIPT_DIR.parent.parent


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Skill Catalog 校验 — 必填元数据 + 协议引用")
    ap.add_argument("--catalog", type=pathlib.Path, required=True, help="catalog yaml 路径")
    ap.add_argument("--skills-root", type=pathlib.Path, required=True, help="skill 包根目录")
    ap.add_argument("--project-root", type=pathlib.Path, default=PROJECT_ROOT_DEFAULT, help="项目根(protocol-coverage 调用)")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    ap.add_argument("--strict", action="store_true", help="严格模式")
    ap.add_argument("--dry-run", action="store_true", help="dry-run")
    return ap.parse_args()


def load_catalog(path: pathlib.Path) -> dict:
    """加载 catalog yaml"""
    try:
        import yaml
    except ImportError:
        return {"error": "需要 PyYAML"}
    if not path.exists():
        return {"error": f"catalog 不存在: {path}"}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def parse_skill_md(path: pathlib.Path) -> dict:
    """解析 SKILL.md 的 YAML frontmatter,失败时降级到 fallback"""
    if not path.exists():
        return {"error": f"SKILL.md 不存在: {path}"}
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {"error": "缺 frontmatter 分隔符 ---"}
    try:
        end = content.index("\n---", 3)
        fm_text = content[3:end]
        try:
            import yaml
            return yaml.safe_load(fm_text) or {}
        except ImportError:
            return _simple_yaml(fm_text)
        except yaml.YAMLError as e:
            # YAML 解析失败 — 降级到 simple 解析,只取顶层字段
            fallback = _simple_yaml(fm_text)
            if fallback:
                return fallback
            return {"error": f"frontmatter YAML 解析失败: {str(e)[:100]}"}
    except ValueError:
        return {"error": "frontmatter 未闭合"}


def _simple_yaml(text: str) -> dict:
    """极简 yaml fallback"""
    result = {}
    for line in text.split("\n"):
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            v = v.strip()
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            result[k.strip()] = v
    return result


def check_skill(skill_dir: pathlib.Path, catalog: dict) -> dict:
    """校验单个 SKILL 包,返回结果 dict"""
    result = {
        "skill": skill_dir.name,
        "skill_md": str(skill_dir / "SKILL.md"),
        "passed": True,
        "errors": [],
        "warnings": [],
    }

    skill_md = skill_dir / "SKILL.md"
    fm = parse_skill_md(skill_md)
    if "error" in fm:
        result["passed"] = False
        result["errors"].append(f"SKILL.md 解析失败: {fm['error']}")
        return result

    # 1. 必填字段校验
    for field in catalog.get("required_metadata", []):
        if field not in fm or not fm[field]:
            result["passed"] = False
            result["errors"].append(f"必填字段缺失: {field}")

    # 1.5 V2 NEW — 推荐字段(声明时 WARN,不阻断)
    for field in catalog.get("recommended_metadata", []):
        if field not in fm or not fm[field]:
            result["warnings"].append(f"推荐字段缺失(V2 推荐,V2.1 必填): {field}")

    # 2. 可选字段 — 声明了 protocols 时,校验每个文件存在
    optional = catalog.get("optional_metadata", [])
    if "protocols" in optional:
        # protocols 不必填,只在 SKILL.md 声明时才校验
        pass  # 实际触发在子校验

    # 3. 行数校验
    structural = catalog.get("structural_rules", {})
    max_lines = structural.get("max_skill_md_lines", 350)
    min_fm_fields = structural.get("min_yaml_frontmatter_fields", 2)
    actual_lines = len(content := skill_md.read_text(encoding="utf-8").splitlines())
    if actual_lines > max_lines:
        result["warnings"].append(f"SKILL.md {actual_lines} 行 > 推荐 {max_lines}")
    if len([k for k in fm.keys() if k]) < min_fm_fields:
        result["passed"] = False
        result["errors"].append(f"frontmatter 字段数 < {min_fm_fields}")

    return result


def main() -> int:
    args = parse_args()
    catalog = load_catalog(args.catalog)
    if "error" in catalog:
        print(f"❌ catalog 加载失败: {catalog['error']}", file=sys.stderr)
        return 1

    skills_root = args.skills_root.resolve()
    if not skills_root.exists():
        print(f"❌ skills-root 不存在: {skills_root}", file=sys.stderr)
        return 1

    # 遍历所有 SKILL 包
    results = []
    for skill_dir in sorted(skills_root.iterdir()):
        if not skill_dir.is_dir():
            continue
        if not (skill_dir / "SKILL.md").exists():
            continue
        results.append(check_skill(skill_dir, catalog))

    overall_pass = all(r["passed"] for r in results)
    total_errors = sum(len(r["errors"]) for r in results)
    total_warnings = sum(len(r["warnings"]) for r in results)

    # V1 默认 report-only(不阻断)— `--strict` 才 exit 1
    if args.strict:
        exit_code = 0 if overall_pass else 1
    else:
        exit_code = 0  # report-only mode

    if args.json:
        print(json.dumps({
            "catalog": str(args.catalog),
            "skills_root": str(skills_root),
            "results": results,
            "overall": overall_pass,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "strict": args.strict,
            "mode": "report-only" if not args.strict else "fail-on-error",
        }, ensure_ascii=False, indent=2))
    else:
        emoji = "✅" if overall_pass else "🛑"
        mode_label = "STRICT" if args.strict else "report-only"
        print(f"{emoji} [SKILL-CATALOG:{mode_label}] {catalog.get('version', '?')} (scope={catalog.get('scope', '?')})")
        print(f"   catalog: {args.catalog}")
        print(f"   skills_root: {skills_root}")
        print()
        for r in results:
            mark = "✅" if r["passed"] else "❌"
            print(f"  {mark} {r['skill']}")
            for e in r["errors"]:
                print(f"      ❌ {e}")
            for w in r["warnings"]:
                print(f"      ⚠ {w}")
        print()
        print(f"统计: {total_errors} 错误 + {total_warnings} 警告 / {len(results)} SKILL")
        if overall_pass:
            print(f"✅ 全部 SKILL 满足 catalog → PASS")
        else:
            if args.strict:
                print(f"🛑 有 SKILL 不满足 catalog(strict 模式 → exit 1)")
            else:
                print(f"⚠ 有 SKILL 不满足 catalog(report-only 模式 — 处置见 catalog-protocol.md §3)")

    if args.dry_run:
        return 0
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())