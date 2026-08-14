"""
07_bundle_structure.py — 校验"含子 skills 的父包"结构

触发条件(目标 skill 的 SKILL.md 存在,且同级目录存在 skills/<sub>/SKILL.md):
  1. 子 skills 命名必须为 kebab-case (lowercase + 短横线)
  2. 子 skills 目录名不能与父包名相同
  3. 子 skills 的 SKILL.md frontmatter 必须含 name 字段
  4. 双层嵌套 skills/<x>/skills/<y>/ → BLOCK(TRAE 协议只识别单层)
  5. 跨包同名(同 marketplace 内 frontmatter name 相同)→ BLOCK
  6. 子 skill 数量 > 30 → WARN(过度拆分,考虑合并)

CLI:    python 07_bundle_structure.py --target <skill-path> [--json]
退出码: 0=PASS  2=WARN  4=BLOCK  5=ARG_ERROR  6=INTERNAL_ERROR
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path


CHECK_ID = "07_bundle_structure"
KEBAB_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
SKILLS_DIR_NAME = "skills"


def find_yaml_field(block: str, key: str):
    """极简取顶层字段值(支持多行 block scalar | / >)"""
    m = re.search(rf"^{key}\s*:\s*(.*)$", block, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    if v in ("|", ">"):
        # 简单取下一段缩进行
        lines = block.split("\n")
        idx = next(
            (i for i, ln in enumerate(lines) if re.match(rf"^{key}\s*:", ln)),
            None,
        )
        if idx is not None:
            collected = []
            for ln in lines[idx + 1 :]:
                if re.match(r"^\s+\S", ln) or ln.strip() == "":
                    collected.append(ln.strip())
                else:
                    break
            return " ".join(collected).strip()
    return v.strip('"').strip("'")


def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end].strip("\n")


def collect_sub_skills(skill_root: Path):
    """返回 [{name, path, fm, nested}]"""
    skills_dir = skill_root / SKILLS_DIR_NAME
    if not skills_dir.is_dir():
        return []
    result = []
    for entry in sorted(skills_dir.iterdir()):
        if entry.name.startswith("."):
            continue
        if not entry.is_dir():
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.is_file():
            continue
        nested_skills = entry / SKILLS_DIR_NAME
        nested = nested_skills.is_dir()
        fm_block = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        result.append({
            "name": entry.name,
            "path": entry,
            "fm": parse_fm(fm_block) if fm_block else {},
            "nested": nested,
        })
    return result


def parse_fm(block: str):
    return {
        "name": find_yaml_field(block, "name"),
        "version": find_yaml_field(block, "version") or "0.0.0",
        "description": find_yaml_field(block, "description") or "",
        "user_invocable": find_yaml_field(block, "user-invocable") == "true",
        "status": find_yaml_field(block, "status"),
        "redirect_to": find_yaml_field(block, "redirect_to"),
    }


def collect_all_marketplace_names(repo_root: Path):
    """扫整个 skill-markets/ 返回所有子 skill 的 frontmatter name 集合"""
    markets = repo_root / "skill-markets"
    if not markets.is_dir():
        return set()
    names = set()
    for child in markets.iterdir():
        if not child.is_dir():
            continue
        for sub in collect_sub_skills(child):
            if sub["fm"].get("name"):
                names.add(sub["fm"]["name"])
    return names


def run(target: Path) -> dict:
    issues = []  # (severity, code, msg)
    if not target.is_dir():
        return {
            "check": CHECK_ID,
            "target": str(target),
            "status": "PASS",
            "issues": [],
            "summary": "target is not a directory; skip (not a bundle)",
        }

    # 只在有子 skills 时跑
    subs = collect_sub_skills(target)
    if not subs:
        return {
            "check": CHECK_ID,
            "target": str(target),
            "status": "PASS",
            "issues": [],
            "summary": "no skills/ subdir; not a bundle, skip",
        }

    parent_name = target.name

    # 检查 1+2+3: kebab-case / 不与父包同名 / frontmatter name
    for sub in subs:
        if not KEBAB_RE.match(sub["name"]):
            issues.append(("BLOCK", "BND-001",
                          f"子 skill 目录名 {sub['name']!r} 不符合 kebab-case (lowercase + 短横线)"))
        if sub["name"] == parent_name:
            issues.append(("BLOCK", "BND-002",
                          f"子 skill 目录名与父包同名: {sub['name']}"))
        if not sub["fm"].get("name"):
            issues.append(("BLOCK", "BND-003",
                          f"子 skill {sub['name']}/SKILL.md frontmatter 缺 name 字段"))
        if sub["fm"].get("status") == "deprecated" and not sub["fm"].get("redirect_to"):
            issues.append(("WARN", "BND-004",
                          f"子 skill {sub['name']} 标记为 deprecated 但缺 redirect_to 字段"))

    # 检查 4: 双层嵌套
    nested_subs = [s["name"] for s in subs if s["nested"]]
    if nested_subs:
        issues.append(("BLOCK", "BND-005",
                      f"子 skills 含嵌套 skills/ 目录(TRAE 协议只识别单层): {', '.join(nested_subs)}"))

    # 检查 5: 跨包同名(扫整个 marketplace)
    repo_root = Path(__file__).resolve().parents[3]
    all_names = collect_all_marketplace_names(repo_root)
    for sub in subs:
        fn = sub["fm"].get("name")
        if not fn:
            continue
        # 同名出现在其他父包
        # 用 file system 扫描:对每个其他父包,看是否有同 name
        markets = repo_root / "skill-markets"
        for other in markets.iterdir():
            if other == target or not other.is_dir():
                continue
            for other_sub in collect_sub_skills(other):
                if other_sub["fm"].get("name") == fn:
                    issues.append(("BLOCK", "BND-006",
                                  f"frontmatter name {fn!r} 在其他包 {other.name}/{other_sub['name']} 中重复"))
                    break

    # 检查 6: 子 skills 数量
    if len(subs) > 30:
        issues.append(("WARN", "BND-007",
                      f"子 skills 数量 {len(subs)} 超过 30,考虑合并"))

    # 汇总
    has_block = any(sev == "BLOCK" for sev, _, _ in issues)
    has_warn = any(sev == "WARN" for sev, _, _ in issues)
    status = "BLOCK" if has_block else ("WARN" if has_warn else "PASS")
    return {
        "check": CHECK_ID,
        "target": str(target),
        "status": status,
        "issues": [{"severity": s, "code": c, "message": m} for s, c, m in issues],
        "summary": f"{len(subs)} sub-skills, {len(issues)} issues ({sum(1 for s,_,_ in issues if s=='BLOCK')} BLOCK / {sum(1 for s,_,_ in issues if s=='WARN')} WARN)",
    }


def collect_all_frontmatter_names(markets: Path):
    """扫整个 marketplace 返回 { frontmatter_name: [(pkg, sub_skill), ...] }"""
    name_index = {}
    for child in markets.iterdir():
        if not child.is_dir():
            continue
        for sub in collect_sub_skills(child):
            fn = sub["fm"].get("name")
            if not fn:
                continue
            name_index.setdefault(fn, []).append((child.name, sub["name"]))
    return name_index


def cross_pkg_conflicts(markets: Path, changed_names=None):
    """
    纯 BND-006 检查: 跨包 frontmatter name 重复
    @param changed_names: 可选 set[str] - 只报告"涉及变更父包"的冲突(其他当背景)
    @returns list[(pkg, sub, other_pkg, other_sub, name)]
    """
    if not markets.is_dir():
        return []
    name_index = collect_all_frontmatter_names(markets)
    conflicts = []
    for name, locations in name_index.items():
        if len(locations) < 2:
            continue
        # 涉及 changed_names 优先
        for (pkg, sub) in locations:
            for (other_pkg, other_sub) in locations:
                if pkg >= other_pkg:  # 去重 (a,b) == (b,a)
                    continue
                if changed_names is None or pkg in changed_names or other_pkg in changed_names:
                    conflicts.append((pkg, sub, other_pkg, other_sub, name))
    # 去重 (按排序元组)
    seen = set()
    unique = []
    for c in conflicts:
        key = tuple(sorted([c[0], c[2]])) + (c[4],)
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", help="单个父包目录路径")
    ap.add_argument("--mode", choices=["single", "all", "diff"], default="single",
                    help="single=单个父包(default); all=扫整个 skill-markets 全部父包; "
                         "diff=只跑 BND-006 跨包冲突(轻量,用于 L1 commit)")
    ap.add_argument("--changed", help="--mode diff 时用,逗号分隔的变更父包名 (如 'fullstack4TraeV11,game-production-kit')")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results = []
    exit_code = 0
    markets = Path(__file__).resolve().parents[3] / "skill-markets"

    if args.mode == "single":
        if not args.target:
            print("ERROR: --mode single 需要 --target", file=sys.stderr)
            sys.exit(5)
        results.append(run(Path(args.target).resolve()))
    elif args.mode == "all":
        if not markets.is_dir():
            print("ERROR: skill-markets/ 不存在", file=sys.stderr)
            sys.exit(5)
        for child in sorted(markets.iterdir()):
            if not child.is_dir():
                continue
            if (child / "SKILL.md").is_file() and (child / "skills").is_dir():
                results.append(run(child))
    elif args.mode == "diff":
        # 增量: 只跑 BND-006 跨包冲突(其他结构问题 git diff 自己能看)
        if not args.changed:
            print("ERROR: --mode diff 需要 --changed", file=sys.stderr)
            sys.exit(5)
        changed = {n.strip() for n in args.changed.split(",") if n.strip()}
        conflicts = cross_pkg_conflicts(markets, changed)
        # 把冲突组装成与 single 模式结构相同的 result
        pkg_to_conflicts = {}
        for (pkg_a, sub_a, pkg_b, sub_b, name) in conflicts:
            pkg_to_conflicts.setdefault(pkg_a, []).append((sub_a, pkg_b, sub_b, name))
            pkg_to_conflicts.setdefault(pkg_b, []).append((sub_b, pkg_a, sub_a, name))
        for pkg, items in pkg_to_conflicts.items():
            target = markets / pkg
            issues = [("BLOCK", "BND-006",
                       f"frontmatter name {items[0][3]!r} 与 {items[0][1]}/{items[0][2]} 重复")
                      for _ in [None]][:1]  # 每个 pkg 只报首个
            issues = [("BLOCK", "BND-006",
                       f"frontmatter name {items[0][3]!r} 在其他包中重复({len(items)} 处)")]
            results.append({
                "check": CHECK_ID,
                "target": str(target),
                "status": "BLOCK",
                "issues": [{"severity": s, "code": c, "message": m} for s, c, m in issues],
                "summary": f"diff mode: BND-006 cross-package conflicts detected",
            })
        # 加上"未涉及变更"的父包 PASS(给完整视图)
        for child in sorted(markets.iterdir()):
            if not child.is_dir() or not (child / "SKILL.md").is_file() or not (child / "skills").is_dir():
                continue
            if child.name not in pkg_to_conflicts:
                results.append({
                    "check": CHECK_ID,
                    "target": str(child),
                    "status": "PASS",
                    "issues": [],
                    "summary": "diff mode: no cross-package conflicts",
                })

    # 输出
    if args.json:
        print(json.dumps({"mode": args.mode, "results": results}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"[{CHECK_ID}] {r['status']}  {r['summary']}  ({r['target']})")
            for it in r["issues"]:
                print(f"  [{it['severity']}] {it['code']}: {it['message']}")

    # 退出码
    if any(r["status"] == "BLOCK" for r in results):
        exit_code = 4
    elif any(r["status"] == "WARN" for r in results):
        exit_code = 2
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
