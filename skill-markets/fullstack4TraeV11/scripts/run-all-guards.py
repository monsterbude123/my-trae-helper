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


def validate_stack(stack, gates_ids, guards_ids) -> list:
    """校验单个 stack。

    返回错误列表（空 = PASS）。

    校验维度:
      - name/gates/guards 三必填字段(P3-2 scaffold 模式)
      - stacks[].gates ⊆ gates.yaml 登记(gate id)(P3-1 交叉校验)
      - stacks[].guards ⊆ guards.yaml 登记(guard id)(P3-1 交叉校验)
    """
    errors = []
    if not isinstance(stack, dict):
        return ["stack 条目不是 dict"]

    # P3-2: 三必填字段(name / gates / guards)
    for field in ("name", "gates", "guards"):
        if field not in stack or stack[field] in (None, ""):
            errors.append(f"stack 缺必填字段 `{field}`")
    if errors:
        return errors  # 必填缺失 → 跳过后续交叉校验

    stack_id = stack.get("id", "?")

    # P3-1: stacks[].gates 必须登记在 gates.yaml
    gates = stack.get("gates", [])
    if not isinstance(gates, list):
        errors.append("stack.gates 不是 list")
    else:
        for g in gates:
            if g not in gates_ids:
                errors.append(
                    f"stacks[{stack_id}].gates 含未登记 gate: {g}"
                )

    # P3-1: stacks[].guards 必须登记在 guards.yaml
    sg = stack.get("guards", [])
    if not isinstance(sg, list):
        errors.append("stack.guards 不是 list")
    else:
        for gd in sg:
            if gd not in guards_ids:
                errors.append(
                    f"stacks[{stack_id}].guards 含未登记 guard: {gd}"
                )

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


def resolve_registry_dir(explicit: str | None, project_root: str | None, skill_root: pathlib.Path) -> tuple:
    """决定 registry_dir,优先级:显式 > 项目级自动探测 > V11 通用。

    返回 (registry_dir, auto_detected: bool)。
    """
    if explicit:
        return pathlib.Path(explicit), False

    project_registry = None
    if project_root:
        pr = pathlib.Path(project_root)
        candidate = pr / ".trae" / "registry"
        required = ["gates.yaml", "guards.yaml", "state-machine.yaml", "repair-flow.yaml"]
        if candidate.is_dir() and all((candidate / r).is_file() for r in required):
            project_registry = candidate

    if project_registry is not None:
        return project_registry, True

    return skill_root / "registry", False


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
    scripts_dir = skill_root / "scripts"
    hooks_dir = skill_root / "templates" / "hooks"

    # registry 目录解析优先级:
    #   1. 显式 --registry-dir(用户主动指定)
    #   2. <project_root>/.trae/registry/(自动探测,项目级覆盖 V11 通用)
    #   3. skill_root/registry/(V11 通用层)
    registry_dir, auto_detected = resolve_registry_dir(
        args.registry_dir, args.project_root, skill_root
    )
    if auto_detected:
        print(
            f"[v11-gate] auto-detected project registry: {registry_dir}",
            file=sys.stderr,
        )

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
    gates_ids = {g.get("id") for g in tables["gates"].get("gates", [])
                 if isinstance(g, dict) and g.get("id")}

    gates_data = tables["gates"].get("gates", [])
    stacks_data = tables["stacks"].get("stacks", [])

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

    # ---- 3.5 P3-1 + P3-2: 逐个 stack 交叉校验 + scaffold 必填字段 ----
    stack_rows = []
    for stack in stacks_data:
        errors = validate_stack(stack, gates_ids, guards_ids)
        sid = stack.get("id", "?") if isinstance(stack, dict) else "?"
        status = "FAIL" if errors else "PASS"
        stack_rows.append({"id": sid, "status": status, "errors": errors})

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

    # stack 校验:任一 FAIL → 整体 FAIL
    stack_failed = sum(1 for s in stack_rows if s["status"] == "FAIL")
    if stack_failed > 0:
        overall_fail = True

    # ---- 6. 输出 ----
    if args.json:
        print(json.dumps({
            "gates": rows,
            "stacks": stack_rows,
            "count_note": count_note,
            "summary": {
                "total": total,
                "pass": passed,
                "fail": failed,
                "expected": len(EXPECTED_STAGES),
                "stack_total": len(stack_rows),
                "stack_fail": stack_failed,
            },
            "exit_code": 1 if overall_fail else 0,
        }, ensure_ascii=False, indent=2))
    else:
        for r in rows:
            script_part = f" script={r['script']}" if r['script'] else ""
            print(f"[v11-gate] gate={r['id']} stage={r['stage']}{script_part} status={r['status']}")
            for e in r["errors"]:
                print(f"[v11-gate]   - {e}")
        for s in stack_rows:
            print(f"[v11-gate] stack={s['id']} status={s['status']}")
            for e in s["errors"]:
                print(f"[v11-gate]   - {e}")
        if count_note:
            print(f"[v11-gate] count-fail {count_note}")
        print(f"[v11-gate] summary total={total} pass={passed} fail={failed} stack_total={len(stack_rows)} stack_fail={stack_failed}")

    return 1 if overall_fail else 0


if __name__ == "__main__":
    sys.exit(main())