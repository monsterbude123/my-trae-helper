#!/usr/bin/env python3
"""
scripts/tools-infill-intent.py
为 skill-markets/<x>/SKILL.md 批量补 intent / category / audience frontmatter 字段。

策略(不依赖 LLM,纯启发式,可在 0 网络环境下运行):
  - intent   : 从 description 第 1 句前 60 字截断(中文按句号/分号切)
  - category : 按路径关键词分类
        scripts/ 有 CLI 子命令 → cli
        references/ 占比大 → knowledge
        agents/ 存在 → orchestration
        含 guard/security 字样 → guard
        含 acceptance/check/verify 字样 → gate
        含 exec/change-control 字样 → execution
        其它 → other
  - audience : 从 description 与 SKILL.md 中识别关键词
        developer / agent / devops / pm / designer / 工程师 / 开发者 / 代理 / 运维

只补缺的字段,已有值不动。默认 dry-run,加 --write 落盘。
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = ROOT / "skill-markets"

CATEGORY_RULES = [
    ("cli",        ("scripts",)),
    ("orchestration", ("agents",)),
    ("guard",      ("guard", "security", "scan", "审查", "扫描", "安全")),
    ("gate",       ("gate", "acceptance", "verify", "check", "verify", "门禁", "验收")),
    ("execution",   ("exec", "change-control", "install-control", "执行")),
    ("knowledge",  ("references",)),
]

AUDIENCE_KEYS = {
    "developer":  ("developer", "工程师", "开发者"),
    "agent":      ("agent", "代理", "subagent"),
    "devops":     ("devops", "ops", "运维", "deploy", "ci"),
    "pm":         ("pm", "product manager", "产品经理"),
    "designer":   ("designer", "ui", "设计"),
}


def parse_fm_min(text: str) -> tuple[dict, str, str]:
    """返回 (frontmatter dict, 完整 frontmatter 块(含 ---), body)。

    支持:
      - 普通 k: v
      - k: [a, b, c] 内联列表
      - k:  (cur_key,下一行 - item 列表)
      - k: >  / k: >-  / k: |  / k: |- 块标量(占多行,缩进 2+ 空格)
    """
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, "", text
    body = m.group(2)
    fm_text = m.group(1)
    lines = fm_text.splitlines()
    fm: dict = {}
    cur_key = None
    block_indent = -1  # 当前块标量的起始缩进(0 表示顶层)
    block_marker = None  # '|' / '>'
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        # 空行 / 注释
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        # 列表项(简单)
        if line.startswith(("  - ", "    - ", "- ")):
            if cur_key and isinstance(fm.get(cur_key), list):
                v = line.lstrip().lstrip("-").strip().strip('"\'')
                fm[cur_key].append(v)
            i += 1
            continue
        # 块标量延续(以缩进的非 - 行,块标量进行中)
        if cur_key and block_marker and line.startswith(("  ", "\t")):
            fm[cur_key] = (fm.get(cur_key, "") + "\n" + stripped).strip() if fm.get(cur_key) else stripped
            i += 1
            continue
        # k: v
        kv = re.match(r"^([A-Za-z_][\w\-]*)\s*:\s*(.*)$", line)
        if not kv:
            i += 1
            continue
        k, v = kv.group(1), kv.group(2).split("#", 1)[0].strip()
        if v in ("|", "|-", ">", ">-", "|+"):
            # 块标量起始
            cur_key = k
            fm[k] = ""
            block_marker = v[0]
            i += 1
            continue
        if v == "":
            cur_key = k
            fm[k] = []
            block_marker = None
            i += 1
            continue
        cur_key = k
        block_marker = None
        v = v.strip('"\'')
        if v.startswith("[") and v.endswith("]"):
            fm[k] = [x.strip().strip('"\'') for x in v[1:-1].split(",") if x.strip()]
        else:
            fm[k] = v
        i += 1
    return fm, m.group(0).split("\n---")[0] + "\n---", body


def infer_intent(description: str, name: str) -> str:
    """从 description 推断 intent(一句话, ≤ 60 字)。"""
    if not description:
        return f"{name} skill 包"
    # 取第一句
    first = re.split(r"[。;；.!?]", description, 1)[0].strip()
    if not first:
        first = description[:60]
    # 截断 60 字
    if len(first) > 60:
        first = first[:57] + "..."
    return first


def infer_category(skill_path: Path, description: str) -> str:
    blob = (skill_path.name + " " + (description or "")).lower()
    # 优先级:cli > orchestration > guard > gate > execution > knowledge
    for cat, keys in CATEGORY_RULES:
        for k in keys:
            if k.lower() in blob:
                return cat
    return "other"


def infer_audience(description: str) -> list[str]:
    if not description:
        return ["developer"]
    audiences = []
    for aud, keys in AUDIENCE_KEYS.items():
        for k in keys:
            if k.lower() in description.lower():
                audiences.append(aud)
                break
    return audiences if audiences else ["developer"]


def infill_one(skill_path: Path) -> tuple[bool, dict]:
    """补一个 skill 的 frontmatter,返回 (是否有改动, 推断结果)。"""
    sm = skill_path / "SKILL.md"
    if not sm.is_file():
        return False, {"error": "SKILL.md 缺失"}
    text = sm.read_text(encoding="utf-8", errors="replace")
    fm, fm_block, body = parse_fm_min(text)
    if not fm:
        return False, {"error": "frontmatter 缺失"}

    new_fm = dict(fm)
    changed = False
    inferred = {}

    # intent
    if not (isinstance(new_fm.get("intent"), str) and new_fm["intent"].strip()):
        v = infer_intent(new_fm.get("description", ""), skill_path.name)
        new_fm["intent"] = v
        inferred["intent"] = v
        changed = True
    # category
    if not (isinstance(new_fm.get("category"), str) and new_fm["category"].strip()):
        v = infer_category(skill_path, new_fm.get("description", ""))
        new_fm["category"] = v
        inferred["category"] = v
        changed = True
    # audience(列表)
    aud = new_fm.get("audience")
    if not (isinstance(aud, list) and aud) and not (isinstance(aud, str) and aud.strip()):
        v = infer_audience(new_fm.get("description", ""))
        new_fm["audience"] = v
        inferred["audience"] = v
        changed = True

    if not changed:
        return False, {"skipped": "已有全部字段"}

    # 序列化新 frontmatter(简化 YAML,只覆盖原 frontmatter 块)
    new_lines = ["---"]
    for k, v in new_fm.items():
        if isinstance(v, list):
            if not v:
                new_lines.append(f"{k}:")
            else:
                # 用 inline 列表写法,更紧凑
                new_lines.append(f"{k}: [{', '.join(str(x) for x in v)}]")
        else:
            # 含中文 / 冒号 / 引号时加引号
            s = str(v).strip()
            if any(c in s for c in ":#\n\"'") or s == "":
                s = '"' + s.replace('"', '\\"') + '"'
            new_lines.append(f"{k}: {s}")
    new_lines.append("---")
    new_fm_block = "\n".join(new_lines)
    new_text = new_fm_block + "\n" + body.lstrip("\n")
    return True, {"text": new_text, "inferred": inferred, "skill": skill_path.name}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="落盘,默认 dry-run")
    ap.add_argument("--target", help="只补单个 skill,不写全扫描")
    args = ap.parse_args()

    targets = [SKILL_DIR / args.target] if args.target else sorted(
        d for d in SKILL_DIR.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
        and d.name != "CAPABILITY-MAP.md"
    )

    filled = []
    skipped = []
    errors = []
    for sp in targets:
        changed, info = infill_one(sp)
        if "error" in info:
            errors.append((sp.name, info["error"]))
            continue
        if not changed:
            skipped.append(sp.name)
            continue
        if args.write:
            (sp / "SKILL.md").write_text(info["text"], encoding="utf-8")
            filled.append((sp.name, info["inferred"]))
        else:
            filled.append((sp.name, info["inferred"]))

    print(f"扫描: {len(targets)} 个 skill")
    print(f"补全: {len(filled)} {'(已落盘)' if args.write else '(dry-run)'}")
    print(f"跳过: {len(skipped)} (已有全部字段)")
    print(f"错误: {len(errors)}")
    if errors:
        for n, e in errors:
            print(f"  - {n}: {e}")
    print()
    print("前 10 个待补的样本:")
    for n, info in filled[:10]:
        print(f"  {n}:")
        for k, v in info.items():
            print(f"    {k}: {v}")


if __name__ == "__main__":
    main()