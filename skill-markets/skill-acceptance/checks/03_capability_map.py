"""
03_capability_map.py — 校验目标 skill 在 CAPABILITY-MAP.md 的登记 + 脚本去重

• 索引表：skill 目录名必须出现在「| [<name>](<name>/SKILL.md) |」一行
• 共享能力注册表：扫描 scripts/*.py/.mjs/.ps1/.sh，文件名若被某 skill 名外的"提供者"
  列注册 → HIGH（重复造轮子）；未在注册表任何位置登记 → LOW

CLI:    python 03_capability_map.py --target <skill-path> [--json]
退出码: 0=PASS  2=WARN  4=BLOCK  5=ARG_ERROR  6=INTERNAL_ERROR
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path


CHECK_ID = "03_capability_map"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CAPABILITY_MAP = PROJECT_ROOT / "skill-markets" / "CAPABILITY-MAP.md"
SCRIPT_EXTS = {".py", ".mjs", ".ps1", ".sh"}
PROVIDER_RE = re.compile(r"`([^`]+)`")


def parse_capability_map(text: str):
    """返回 { indexed: set[str], registry: dict[script_name, provider_skill] }
    indexed: 在技能索引表出现过的 skill 目录名集合
    registry: 注册过的脚本名 → 提供者 skill 名
    """
    indexed = set()
    registry = {}
    section = None  # "index" | "registry"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            section = None
            if "技能索引" in stripped:
                section = "index"
            elif "共享能力注册表" in stripped:
                section = "registry"
            continue
        if section is None:
            continue
        if not stripped.startswith("|"):
            continue
        if section == "index":
            m = re.search(r"\[\s*([a-z][a-z0-9-]*)\s*\]\(", line)
            if m:
                indexed.add(m.group(1))
        elif section == "registry":
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            if cells[0].startswith("---") or cells[0] in {"能力", "提供者"}:
                continue
            provider = cells[1]
            pm = PROVIDER_RE.search(provider)
            if not pm:
                continue
            provider_text = pm.group(1).strip()
            # 提供者形如 vision-audit/scripts/vision-audit.mjs 或 forge_project_rules_skill.py
            script_path = provider_text
            script_name = Path(script_path).name
            # 取 skill 名（路径第一段）
            parts = provider_text.split("/")
            skill_name = parts[0] if len(parts) > 1 else "(unknown)"
            registry[script_name] = skill_name
    return {"indexed": indexed, "registry": registry}


def evaluate(target: Path):
    issues = []
    skill_name = target.name
    raw_map = ""
    parsed = {"indexed": set(), "registry": {}}
    if not CAPABILITY_MAP.is_file():
        issues.append(
            {
                "code": "CAPABILITY_MAP_MISSING",
                "severity": "MEDIUM",
                "message": "无法找到 CAPABILITY-MAP.md",
                "file": str(CAPABILITY_MAP),
                "line": None,
            }
        )
    else:
        try:
            raw_map = CAPABILITY_MAP.read_text(encoding="utf-8")
            parsed = parse_capability_map(raw_map)
        except OSError as exc:
            issues.append(
                {
                    "code": "CAPABILITY_MAP_UNREADABLE",
                    "severity": "MEDIUM",
                    "message": f"无法读取 CAPABILITY-MAP.md: {exc}",
                    "file": str(CAPABILITY_MAP),
                    "line": None,
                }
            )

    if parsed["indexed"] and skill_name not in parsed["indexed"]:
        issues.append(
            {
                "code": "SKILL_NOT_INDEXED",
                "severity": "MEDIUM",
                "message": f"未登记到 CAPABILITY-MAP 技能索引表（skill={skill_name}）",
                "file": str(CAPABILITY_MAP),
                "line": None,
            }
        )

    scripts_dir = target / "scripts"
    if scripts_dir.is_dir():
        for p in scripts_dir.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in SCRIPT_EXTS:
                continue
            name = p.name
            if name in parsed["registry"]:
                provider = parsed["registry"][name]
                if provider != skill_name:
                    issues.append(
                        {
                            "code": "DUPLICATE_WHEEL",
                            "severity": "HIGH",
                            "message": (
                                f"脚本重复造轮子：{name} 已在 {provider} 注册"
                            ),
                            "file": str(p),
                            "line": None,
                        }
                    )
            else:
                issues.append(
                    {
                        "code": "SCRIPT_UNREGISTERED",
                        "severity": "LOW",
                        "message": f"脚本未在共享能力注册表登记: {name}",
                        "file": str(p),
                        "line": None,
                    }
                )

    high = sum(1 for x in issues if x["severity"] == "HIGH")
    medium = sum(1 for x in issues if x["severity"] == "MEDIUM")
    if high > 0:
        status, score = "BLOCK", max(0, 50 - 20 * high)
    elif medium >= 3:
        status, score = "WARN", max(40, 100 - 10 * medium)
    else:
        score = max(0, 100 - 5 * medium)
        status = "PASS"

    return {
        "id": CHECK_ID,
        "status": status,
        "score": score,
        "issues": issues,
        "indexed_count": len(parsed["indexed"]),
        "registry_count": len(parsed["registry"]),
        "map_present": bool(raw_map),
    }


def main():
    parser = argparse.ArgumentParser(description="CAPABILITY-MAP 校验 + 脚本去重")
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
