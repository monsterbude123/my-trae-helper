#!/usr/bin/env python3
"""
scripts/build-manifest.py
自动从 skill-markets/<x>/ 实际结构生成 Manifest 草稿

策略:
  1. 遍历 skill-markets/ 下每个含 SKILL.md 的目录
  2. scripts/*.py / *.mjs → scripts: [{path, cli_entry, exit_codes}]
     - cli_entry 从文件名推断(strip .py/.mjs)
     - exit_codes 默认 [0, 2]
  3. SKILL.md 必含的字符串 → 取首段二级标题作为 must_contain(自动可校验)
  4. references/*.md → docs 列表(声明存在)
  5. 跳过 MANIFEST.yaml 自身 / CAPABILITY-MAP.md

输出:覆盖 skill-markets/MANIFEST.yaml(用户可手工微调)

用法:
  python scripts/build-manifest.py          # 写
  python scripts/build-manifest.py --print  # 仅打印,不改
  python scripts/build-manifest.py --check  # 仅校验现有 Manifest 是否与目录一致
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skill-markets"
MANIFEST = SKILL_DIR / "MANIFEST.yaml"


def discover_skill(skill_path: Path) -> dict | None:
    """从一个 skill 目录推断 Manifest 条目。"""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return None
    name = skill_path.name
    entry = {"name": name}

    # 1. scripts — 只列"真 CLI 入口"(有 __main__ 守卫 / argparse / shebang)
    scripts = []
    for ext in ("*.py", "*.mjs", "*.js", "*.sh"):
        for s in sorted((skill_path / "scripts").glob(ext)):
            # 跳过 lib / helpers / 子目录(非入口)
            rel = s.relative_to(skill_path)
            parts = rel.parts
            if any(p in ("lib", "audit_reports", "auto_reports", "_archived_", "__pycache__", ".publish", "logs", "tmp") for p in parts[:-1]):
                continue
            # 智能判断是否 CLI 入口
            try:
                text = s.read_text(encoding="utf8", errors="ignore")
            except Exception:
                continue
            is_cli = False
            if s.suffix == ".py":
                # 有 __name__ == '__main__' 守卫 或 用 argparse
                is_cli = ("__name__" in text and "__main__" in text) or ("argparse" in text)
            elif s.suffix in (".mjs", ".js"):
                # 有 process.argv 引用 或 shebang
                is_cli = ("process.argv" in text) or text.startswith("#!/usr/bin/env node") or ("#!/usr/bin/env node" in text)
            elif s.suffix == ".sh":
                is_cli = text.startswith("#!")
            if not is_cli:
                continue  # 库文件,跳过
            stem = s.stem
            scripts.append({
                "path": str(rel).replace("\\", "/"),
                "cli_entry": stem,
                "exit_codes": [0, 2],
            })
    if scripts:
        entry["scripts"] = scripts
    else:
        entry["scripts"] = []

    # 2. docs
    docs = []
    # SKILL.md 必含一个二级标题
    try:
        text = skill_md.read_text(encoding="utf8", errors="ignore")
        # 匹配第一个 ## 标题
        m = re.search(r"^##\s+(.+)$", text, re.MULTILINE)
        first_h2 = m.group(1).strip() if m else None
        skill_doc = {"path": "SKILL.md"}
        if first_h2:
            skill_doc["must_contain"] = [f"## {first_h2}"]
        else:
            # 退而求其次:取首句描述(从 frontmatter 的 description)
            fm = re.search(r"description:\s*(.+)", text)
            if fm:
                skill_doc["must_contain"] = [fm.group(1).strip()[:30]]
        docs.append(skill_doc)
    except Exception:
        pass
    # references/*.md 至少列一个(声明存在即可)
    refs_dir = skill_path / "references"
    if refs_dir.exists():
        # 取文件名最短的一个(通常是核心 reference)
        refs = sorted(refs_dir.glob("*.md"))
        if refs:
            docs.append({"path": f"references/{refs[0].name}"})
    entry["docs"] = docs

    # 3. tests — 跨 skill 自动映射 tests/unit/test_<x>.py(粗略,可能不存在)
    # 不强行断言 tests,留给人工加 must_assert
    entry["tests"] = []

    return entry


def build():
    entries = []
    for d in sorted(SKILL_DIR.iterdir()):
        if not d.is_dir():
            continue
        if d.name in ("CAPABILITY-MAP.md",):
            continue
        if d.name.startswith("."):
            continue
        e = discover_skill(d)
        if e:
            entries.append(e)
    return entries


def to_yaml(entries: list) -> str:
    lines = ["# skill-markets/MANIFEST.yaml", "# 自动生成 — 用 scripts/build-manifest.py 重建", "# 手工微调后请勿覆盖,除非重新跑 build-manifest.py", ""]
    lines.append("schema_version: 1")
    lines.append("")
    lines.append("skills:")
    for e in entries:
        lines.append(f"  - name: {e['name']}")
        # scripts
        if e.get("scripts"):
            lines.append("    scripts:")
            for s in e["scripts"]:
                lines.append(f"      - path: {s['path']}")
                lines.append(f"        cli_entry: {s['cli_entry']}")
                lines.append(f"        exit_codes: {s['exit_codes']}")
        else:
            lines.append("    scripts: []")
        # docs
        if e.get("docs"):
            lines.append("    docs:")
            for d in e["docs"]:
                lines.append(f"      - path: {d['path']}")
                if "must_contain" in d:
                    mc = d["must_contain"]
                    if len(mc) == 1:
                        lines.append(f"        must_contain:")
                        lines.append(f"          - \"{mc[0]}\"")
                    else:
                        lines.append(f"        must_contain:")
                        for x in mc:
                            lines.append(f"          - \"{x}\"")
        else:
            lines.append("    docs: []")
        # tests
        lines.append("    tests: []")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", action="store_true", help="只打印到 stdout,不写文件")
    ap.add_argument("--check", action="store_true", help="校验现有 Manifest 的每个 must_contain 是否真实存在")
    args = ap.parse_args()

    entries = build()

    if args.check:
        # 校验现有 MANIFEST.yaml
        import yaml
        cur = yaml.safe_load(MANIFEST.read_text(encoding="utf8"))
        cur_idx = {s["name"]: s for s in cur.get("skills", [])}
        fails = 0
        for e in entries:
            if e["name"] not in cur_idx:
                print(f"[MISS] skill '{e['name']}' not in MANIFEST")
                fails += 1
                continue
            spec = cur_idx[e["name"]]
            for doc in spec.get("docs", []) or []:
                full = SKILL_DIR / e["name"] / doc["path"]
                if not full.exists():
                    print(f"[MISS-doc] {e['name']}: {doc['path']}")
                    fails += 1
                for phrase in doc.get("must_contain", []) or []:
                    try:
                        if phrase not in full.read_text(encoding="utf8", errors="ignore"):
                            print(f"[MISS-phrase] {e['name']}: '{phrase}'")
                            fails += 1
                    except Exception as ex:
                        print(f"[ERR] {e['name']}: {ex}")
                        fails += 1
        if fails:
            print(f"\n❌ {fails} 处不一致")
            sys.exit(2)
        print(f"✅ Manifest 与目录一致 ({len(entries)} skill)")
        return

    yaml_text = to_yaml(entries)
    if args.print:
        print(yaml_text)
        return

    MANIFEST.write_text(yaml_text, encoding="utf8")
    print(f"✅ 已写 {MANIFEST} ({len(entries)} skill)")


if __name__ == "__main__":
    main()