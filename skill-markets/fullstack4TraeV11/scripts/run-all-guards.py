#!/usr/bin/env python3
"""
V11 run-all-guards.py — V11 flow 层统一消费脚本（13 stage 门禁总入口）

定位: registry 四表（gates/guards/state-machine/repair-flow）的程序化消费入口。
不再靠 agent 硬读 md 表格，而是由本脚本读四表决定跑什么门禁，输出 PASS/FAIL 矩阵。

Usage:
    python run-all-guards.py [--registry-dir registry/]
                             [--project-root .]
                             [--validate-only]
                             [--json]

参数:
    --registry-dir    registry 目录（默认 registry/，相对 skill 根）
    --project-root    项目根（用于校验 required_artifacts 实际文件，可选）
    --validate-only   只校验四表结构，不检查脚本存在性
    --json            JSON 输出（CI 集成）

Exit codes:
    0 = 全 PASS
    1 = 任一 gate FAIL / 四表缺失 / 结构非法
"""
import argparse
import json
import pathlib
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    print("[v11-gate] FATAL: PyYAML 未安装，请先 pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# 13 stage 名单（必须严格匹配编排器 stage_config / stage-gate.py VALID_STAGES）
EXPECTED_STAGES = [
    "-1/intake", "0/plan", "0.5/test-plan", "1/spec", "1.5/prototype",
    "2/contract", "3/implement", "3.5/real-verify", "4/review",
    "4.5/rot-scan", "5/accept", "6/bug-fix", "7/project-health",
]

# 五表清单
TABLES = ["gates", "guards", "state-machine", "repair-flow", "stacks"]

# 每个 gate 的必填字段（缺则结构 FAIL）
GATE_REQUIRED_FIELDS = ["id", "stage", "script"]


def load_table(path: pathlib.Path):
    """加载单个 yaml 表。返回 (data, error)；data 为 None 表示加载失败。"""
    if not path.exists():
        return None, f"缺表: {path.name}（路径 {path}）"
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return None, f"{path.name} YAML 解析失败: {e}"
    return data, None


def validate_table_structure(name: str, data) -> list:
    """校验单表结构合法。返回错误列表（空 = 合法）。"""
    errors = []
    if not isinstance(data, dict):
        errors.append(f"{name}.yaml 顶层不是 dict（当前 type={type(data).__name__})")
        return errors

    # gates / guards / state-machine / stacks 必须有对应 list 主键
    list_key = {
        "gates": "gates",
        "guards": "guards",
        "state-machine": "states",
        "repair-flow": "gates",
        "stacks": "stacks",
    }.get(name)

    if list_key is not None:
        if list_key not in data:
            errors.append(f"{name}.yaml 缺主键 `{list_key}`")
        elif not isinstance(data[list_key], list):
            errors.append(f"{name}.yaml `{list_key}` 不是 list")
    return errors


def validate_gate(gate, guards_ids, scripts_dir, hooks_dir, project_root, validate_only):
    """校验单个 gate。返回错误列表（空 = PASS）。"""
    errors = []
    if not isinstance(gate, dict):
        return ["gate 条目不是 dict"]

    # 必填字段
    for field in GATE_REQUIRED_FIELDS:
        if field not in gate or gate[field] in (None, ""):
            errors.append(f"缺必填字段 `{field}`")

    # required_artifacts 结构合法（必须是字符串 list）
    ra = gate.get("required_artifacts", [])
    if not isinstance(ra, list):
        errors.append("required_artifacts 不是 list")
    else:
        for a in ra:
            if not isinstance(a, str):
                errors.append(f"required_artifacts 含非字符串项: {a!r}")
        # 可选: 校验实际文件存在（--project-root 提供时）
        if project_root and not validate_only:
            for a in ra:
                if isinstance(a, str) and a.strip():
                    ap = pathlib.Path(project_root) / a
                    if not ap.exists():
                        errors.append(f"required_artifacts 文件不存在: {ap}")

    # guards 字段必须登记在 guards.yaml
    guards = gate.get("guards", [])
    if not isinstance(guards, list):
        errors.append("guards 不是 list")
    else:
        for g in guards:
            if g not in guards_ids:
                errors.append(f"guard 未登记在 guards.yaml: {g}")

    # 关联脚本存在性（--validate-only 跳过）
    # 脚本可能位于 scripts/ 或 templates/hooks/（hook 类脚本如 spec-validate-hook / pre-accept）
    if not validate_only:
        script = gate.get("script")
        if script:
            candidates = [scripts_dir / script, hooks_dir / script]
            if not any(p.exists() for p in candidates):
                locations = " / ".join(f"scripts/{script}" for _ in [0]) + \
                            f" 或 templates/hooks/{script}"
                errors.append(f"脚本不存在: {locations}")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="V11 flow 层统一消费脚本（registry 四表 → 13 stage 门禁矩阵）"
    )
    parser.add_argument("--registry-dir", default=None,
                        help="registry 目录（默认 registry/，相对 skill 根）")
    parser.add_argument("--project-root", default=None,
                        help="项目根（校验 required_artifacts 实际文件，可选）")
    parser.add_argument("--validate-only", action="store_true",
                        help="只校验四表结构，不检查脚本存在性")
    parser.add_argument("--json", action="store_true", help="JSON 输出（CI 集成）")
    args = parser.parse_args()

    # skill 根 = 本脚本所在目录的上一级
    skill_root = pathlib.Path(__file__).resolve().parent.parent
    registry_dir = pathlib.Path(args.registry_dir) if args.registry_dir else skill_root / "registry"
    scripts_dir = skill_root / "scripts"
    hooks_dir = skill_root / "templates" / "hooks"

    # ---- 1. 加载四表 ----
    tables = {}
    table_errors = {}
    for name in TABLES:
        data, err = load_table(registry_dir / f"{name}.yaml")
        if err:
            table_errors[name] = err
            continue
        struct_errs = validate_table_structure(name, data)
        if struct_errs:
            table_errors[name] = "; ".join(struct_errs)
            continue
        tables[name] = data

    # 任一表缺失/非法 → 统一报 FAIL + exit 1（不崩溃）
    if table_errors:
        if args.json:
            print(json.dumps({
                "status": "FAIL",
                "missing_tables": {k: v for k, v in table_errors.items()},
            }, ensure_ascii=False, indent=2))
        else:
            for name, err in table_errors.items():
                print(f"[v11-gate] table={name} status=FAIL reason={err}")
        return 1

    # ---- 2. 收集 guards 登记 id ----
    guards_ids = {g.get("id") for g in tables["guards"].get("guards", [])
                  if isinstance(g, dict) and g.get("id")}

    gates_data = tables["gates"].get("gates", [])

    # ---- 3. 逐个 gate 检查 ----
    rows = []
    for gate in gates_data:
        if not isinstance(gate, dict):
            errors = ["gate 条目不是 dict"]
        else:
            errors = validate_gate(gate, guards_ids, scripts_dir, hooks_dir,
                                   pathlib.Path(args.project_root) if args.project_root else None,
                                   args.validate_only)
        gid = gate.get("id", "?") if isinstance(gate, dict) else "?"
        stage = gate.get("stage", "?") if isinstance(gate, dict) else "?"
        script = gate.get("script", "") if isinstance(gate, dict) else ""
        status = "FAIL" if errors else "PASS"
        rows.append({"id": gid, "stage": stage, "script": script,
                     "status": status, "errors": errors})

    # ---- 4. gate 数量校验（应为 13）----
    count_note = None
    if len(gates_data) != len(EXPECTED_STAGES):
        count_note = (f"gate 数量={len(gates_data)}，期望={len(EXPECTED_STAGES)}"
                      f"（13 stage 每个必登记一门禁）")

    # ---- 5. 汇总 ----
    total = len(rows)
    passed = sum(1 for r in rows if r["status"] == "PASS")
    failed = total - passed
    overall_fail = (failed > 0) or bool(count_note) or bool(rows) is False
    # 无任何 gate 也视为 FAIL
    if total == 0:
        overall_fail = True

    # ---- 6. 输出 ----
    if args.json:
        print(json.dumps({
            "gates": rows,
            "count_note": count_note,
            "summary": {
                "total": total,
                "pass": passed,
                "fail": failed,
                "expected": len(EXPECTED_STAGES),
            },
            "exit_code": 1 if overall_fail else 0,
        }, ensure_ascii=False, indent=2))
    else:
        for r in rows:
            script_part = f" script={r['script']}" if r['script'] else ""
            print(f"[v11-gate] gate={r['id']} stage={r['stage']}{script_part} status={r['status']}")
            for e in r["errors"]:
                print(f"[v11-gate]   - {e}")
        if count_note:
            print(f"[v11-gate] count-fail {count_note}")
        print(f"[v11-gate] summary total={total} pass={passed} fail={failed}")

    return 1 if overall_fail else 0


if __name__ == "__main__":
    sys.exit(main())