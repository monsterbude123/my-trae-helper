"""
01_frontmatter.py — SKILL.md YAML frontmatter 校验

校验 <skill>/SKILL.md 的 YAML frontmatter 是否符合 skill-optimization-method
与 AGENTS.md §2 铁律 1 + §F 的约定。

CLI:    python 01_frontmatter.py --target <skill-path> [--json]
退出码: 0=PASS  2=WARN  4=BLOCK  5=ARG_ERROR  6=INTERNAL_ERROR
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path


CHECK_ID = "01_frontmatter"
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[A-Za-z0-9.]+)?$")
KEBAB_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


def parse_frontmatter(text: str):
    """提取 --- 包裹的 YAML frontmatter 原始字符串与剩余正文"""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    block = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    return block, body


def extract_scalar(block: str, key: str):
    """极简正则取顶层 key 的字符串值（多行用 block scalar | / >）"""
    m = re.search(rf"^{key}\s*:\s*(.*)$", block, re.M)
    if not m:
        return None
    val = m.group(1).strip()
    if not val:
        return ""
    # 块标量 | / > 取首行
    if val.startswith("|") or val.startswith(">"):
        return ""
    # 去掉引号
    if (val.startswith('"') and val.endswith('"')) or (
        val.startswith("'") and val.endswith("'")
    ):
        return val[1:-1]
    return val


def extract_list_or_dict(block: str, key: str):
    """取 triggers / requires 等 key 的缩进子项，返回 (kind, payload)
    kind: 'list' | 'dict' | None
    """
    lines = block.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf"^{key}\s*:\s*(.*)$", line)
        if not m:
            continue
        tail = m.group(1).strip()
        if tail == "" or tail is None:
            # 缩进子块
            sub = []
            for j in range(i + 1, len(lines)):
                if not lines[j].startswith("  "):
                    break
                sub.append(lines[j].strip())
            if not sub:
                return None, None
            # 判断 list / dict
            if any(re.match(r"^- ", s) for s in sub):
                items = [re.sub(r"^- ", "", s).strip() for s in sub]
                return "list", items
            # dict 形态：xxx: yyy
            items = {}
            for s in sub:
                mm = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*\[(.+)\]\s*$", s)
                if mm:
                    k = mm.group(1)
                    arr = [x.strip().strip("'\"") for x in mm.group(2).split(",") if x.strip()]
                    items[k] = arr
                    continue
                mm2 = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+)$", s)
                if mm2:
                    items[mm2.group(1)] = mm2.group(2).strip()
            if items:
                return "dict", items
            return None, None
        # 单行 list 形如 [...]
        if tail.startswith("[") and tail.endswith("]"):
            inner = tail[1:-1].strip()
            if not inner:
                return "list", []
            items = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
            return "list", items
        # 单行 scalar
        return "scalar", tail
    return None, None


def evaluate(target: Path):
    issues = []
    skill_md = target / "SKILL.md"
    if not skill_md.is_file():
        return {
            "id": CHECK_ID,
            "status": "BLOCK",
            "score": 0,
            "issues": [
                {
                    "code": "SKILL_MD_MISSING",
                    "severity": "HIGH",
                    "message": "SKILL.md 不存在",
                    "file": str(skill_md),
                    "line": None,
                }
            ],
        }

    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "id": CHECK_ID,
            "status": "BLOCK",
            "score": 0,
            "issues": [
                {
                    "code": "SKILL_MD_UNREADABLE",
                    "severity": "HIGH",
                    "message": f"无法读取 SKILL.md: {exc}",
                    "file": str(skill_md),
                    "line": None,
                }
            ],
        }

    block, _ = parse_frontmatter(text)
    if block is None:
        issues.append(
            {
                "code": "FRONTMATTER_MISSING",
                "severity": "HIGH",
                "message": "frontmatter 缺失或未用 --- 包裹",
                "file": str(skill_md),
                "line": 1,
            }
        )
        block = ""

    dirname = target.name
    name = extract_scalar(block, "name")
    if name is None:
        issues.append(
            {
                "code": "NAME_MISSING",
                "severity": "HIGH",
                "message": "name 字段缺失",
                "file": str(skill_md),
                "line": None,
            }
        )
    else:
        if not KEBAB_RE.match(name):
            issues.append(
                {
                    "code": "NAME_NOT_KEBAB",
                    "severity": "HIGH",
                    "message": f"name 不是 kebab-case: {name}",
                    "file": str(skill_md),
                    "line": None,
                }
            )
        if name != dirname:
            issues.append(
                {
                    "code": "NAME_DIR_MISMATCH",
                    "severity": "HIGH",
                    "message": f"name={name!r} 与目录名 {dirname!r} 不一致",
                    "file": str(skill_md),
                    "line": None,
                }
            )

    desc = extract_scalar(block, "description")
    if desc is None or not desc:
        issues.append(
            {
                "code": "DESCRIPTION_MISSING",
                "severity": "HIGH",
                "message": "description 字段缺失",
                "file": str(skill_md),
                "line": None,
            }
        )
    else:
        if len(desc) < 20:
            issues.append(
                {
                    "code": "DESCRIPTION_TOO_SHORT",
                    "severity": "HIGH",
                    "message": f"description 过短 ({len(desc)} 字符, <20)",
                    "file": str(skill_md),
                    "line": None,
                }
            )
        elif len(desc) < 30:
            issues.append(
                {
                    "code": "DESCRIPTION_BORDERLINE",
                    "severity": "MEDIUM",
                    "message": f"description 仅 {len(desc)} 字符 (推荐 ≥30)",
                    "file": str(skill_md),
                    "line": None,
                }
            )

    ver = extract_scalar(block, "version")
    if ver is None:
        issues.append(
            {
                "code": "VERSION_MISSING",
                "severity": "LOW",
                "message": "version 字段不存在（推荐 1.2.3 语义版本）",
                "file": str(skill_md),
                "line": None,
            }
        )
    elif not SEMVER_RE.match(ver):
        issues.append(
            {
                "code": "VERSION_NOT_SEMVER",
                "severity": "LOW",
                "message": f"version={ver!r} 非 semver 形如 1.2.3",
                "file": str(skill_md),
                "line": None,
            }
        )

    triggers_kind, triggers = extract_list_or_dict(block, "triggers")
    if triggers_kind != "list" or not triggers:
        issues.append(
            {
                "code": "TRIGGERS_MISSING",
                "severity": "MEDIUM",
                "message": "triggers 字段缺失或不是非空列表",
                "file": str(skill_md),
                "line": None,
            }
        )

    req_kind, req = extract_list_or_dict(block, "requires")
    if req_kind is None:
        issues.append(
            {
                "code": "REQUIRES_MISSING",
                "severity": "MEDIUM",
                "message": "requires 字段缺失（推荐声明 skills/optional）",
                "file": str(skill_md),
                "line": None,
            }
        )
    elif req_kind == "dict":
        for sub_key, val in req.items():
            if not isinstance(val, list):
                issues.append(
                    {
                        "code": "REQUIRES_NOT_LIST",
                        "severity": "MEDIUM",
                        "message": f"requires.{sub_key} 不是 list",
                        "file": str(skill_md),
                        "line": None,
                    }
                )

    high = sum(1 for x in issues if x["severity"] == "HIGH")
    medium = sum(1 for x in issues if x["severity"] == "MEDIUM")
    low = sum(1 for x in issues if x["severity"] == "LOW")
    if high > 0:
        status, score = "BLOCK", max(0, 50 - 20 * high)
    elif medium >= 3:
        status, score = "WARN", max(40, 100 - 10 * medium)
    else:
        score = 100 - 5 * medium - 2 * low
        score = max(0, min(100, score))
        status = "PASS"
    return {"id": CHECK_ID, "status": status, "score": score, "issues": issues}


def main():
    parser = argparse.ArgumentParser(description="SKILL.md frontmatter 校验")
    parser.add_argument("--target", required=True, help="skill 目录路径")
    parser.add_argument("--json", action="store_true", help="强制 JSON 输出")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not target.is_dir():
        sys.stdout.write(
            json.dumps(
                {
                    "id": CHECK_ID,
                    "status": "BLOCK",
                    "score": 0,
                    "issues": [
                        {
                            "code": "TARGET_NOT_DIR",
                            "severity": "HIGH",
                            "message": f"目标不是目录: {target}",
                            "file": str(target),
                            "line": None,
                        }
                    ],
                    "duration_ms": 0,
                },
                ensure_ascii=False,
            )
        )
        sys.stdout.write("\n")
        sys.exit(5)

    t0 = time.time()
    try:
        result = evaluate(target)
    except Exception as exc:  # noqa: BLE001
        sys.stdout.write(
            json.dumps(
                {
                    "id": CHECK_ID,
                    "status": "INTERNAL_ERROR",
                    "score": 0,
                    "issues": [
                        {
                            "code": "EXCEPTION",
                            "severity": "HIGH",
                            "message": f"内部异常: {exc}",
                            "file": str(target),
                            "line": None,
                        }
                    ],
                    "duration_ms": int((time.time() - t0) * 1000),
                },
                ensure_ascii=False,
            )
        )
        sys.stdout.write("\n")
        sys.exit(6)

    result["duration_ms"] = int((time.time() - t0) * 1000)
    sys.stdout.write(json.dumps(result, ensure_ascii=False))
    sys.stdout.write("\n")
    code_map = {"PASS": 0, "WARN": 2, "BLOCK": 4}
    sys.exit(code_map.get(result["status"], 4))


if __name__ == "__main__":
    main()
