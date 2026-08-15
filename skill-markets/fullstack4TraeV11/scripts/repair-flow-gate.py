#!/usr/bin/env python3
"""
V11 repair-flow-gate.py — Bug 修复流程声明消费脚本（flow 层 registry）

程序化解析 registry/repair-flow.yaml，不靠 agent 硬读 md。
对齐 reason-classifier.py 的 argparse + 前缀输出风格。

Usage:
    python repair-flow-gate.py [--registry-dir <dir>] [--validate-only]
                               [--step <step-id>] [--list-steps]

Exit codes:
    0 = 校验通过 / 输出正常
    1 = 声明缺失 / 结构非法 / 校验失败
"""
import sys
import argparse
import pathlib
import json

try:
    import yaml
except ImportError:
    print("[repair-flow] ❌ 缺少 PyYAML，请先执行: pip install pyyaml")
    sys.exit(1)


DEFAULT_REGISTRY = pathlib.Path(__file__).resolve().parent.parent / "registry"


def load_flow(registry_dir: str) -> dict:
    """读取并解析 repair-flow.yaml，返回 dict；失败抛异常。"""
    path = pathlib.Path(registry_dir) / "repair-flow.yaml"
    if not path.exists():
        raise FileNotFoundError(f"未找到 repair-flow.yaml: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("repair-flow.yaml 顶层必须是 mapping")
    return data


def validate_structure(data: dict) -> list:
    """校验结构合法性，返回错误列表（空 = 合法）。"""
    errors = []

    if not data.get("version"):
        errors.append("缺少必填字段: version")
    if not data.get("description"):
        errors.append("缺少必填字段: description")

    triggers = data.get("triggers")
    if not isinstance(triggers, list) or not triggers:
        errors.append("缺少必填字段: triggers（非空列表）")
    else:
        for t in triggers:
            if not isinstance(t, dict) or not t.get("id"):
                errors.append("triggers 中存在缺少 id 的条目")

    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append("缺少必填字段: steps（非空列表）")
    else:
        for s in steps:
            if not isinstance(s, dict) or not s.get("id"):
                errors.append("steps 中存在缺少 id 的条目")
                continue
            if not s.get("gate"):
                errors.append(f"step {s['id']} 缺少 gate 声明")

    if not data.get("terminal_condition"):
        errors.append("缺少必填字段: terminal_condition")

    gates = data.get("gates")
    if not isinstance(gates, list) or not gates:
        errors.append("缺少必填字段: gates（非空列表）")
    else:
        for g in gates:
            if not isinstance(g, dict) or not g.get("id"):
                errors.append("gates 中存在缺少 id 的条目")

    # 交叉校验：每个 step.gate 必须能在 gates 中登记
    step_ids = [s["id"] for s in (steps or []) if isinstance(s, dict) and s.get("id")]
    gate_ids = [g["id"] for g in (gates or []) if isinstance(g, dict) and g.get("id")]
    for s in (steps or []):
        if not isinstance(s, dict) or not s.get("gate"):
            continue
        if s["gate"] not in gate_ids:
            errors.append(f"step {s.get('id')} 引用了未登记 gate: {s['gate']}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="V11 Bug 修复流程声明消费脚本")
    parser.add_argument("--registry-dir", default=str(DEFAULT_REGISTRY),
                        help="registry 目录（含 repair-flow.yaml）")
    parser.add_argument("--validate-only", action="store_true",
                        help="只校验声明结构，不做其他操作")
    parser.add_argument("--step", help="检查指定 step 的 gate 是否登记")
    parser.add_argument("--list-steps", action="store_true", help="列出所有步骤")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    try:
        data = load_flow(args.registry_dir)
    except Exception as e:
        print(f"[repair-flow] ❌ 声明加载失败: {e}")
        return 1

    # 结构校验（始终执行）
    errors = validate_structure(data)
    struct_ok = not errors

    step_ids = [s["id"] for s in data.get("steps", [])]
    gate_map = {g["id"]: g for g in data.get("gates", [])}
    step_gate_map = {s["id"]: s.get("gate") for s in data.get("steps", [])}

    if args.validate_only:
        if not struct_ok:
            print("[repair-flow] ❌ 结构校验失败: %d 个错误" % len(errors))
            for e in errors:
                print(f"   - {e}")
            return 1
        print(f"[repair-flow] ✅ 声明合法 — version={data.get('version')} "
              f"triggers={len(data.get('triggers', []))} "
              f"steps={len(step_ids)} gates={len(gate_map)}")
        if args.json:
            print(json.dumps({"status": "PASS"}, ensure_ascii=False))
        return 0

    if args.list_steps:
        if args.json:
            print(json.dumps({
                "steps": [{"id": s["id"], "name": s.get("name", ""),
                           "gate": s.get("gate")} for s in data.get("steps", [])],
            }, indent=2, ensure_ascii=False))
        else:
            print("[repair-flow] 📋 修复流程步骤:")
            for s in data.get("steps", []):
                gate_id = s.get("gate")
                registered = "✅" if gate_id in gate_map else "❌"
                print(f"   {registered} {s['id']} — {s.get('name', '')} "
                      f"(gate: {gate_id})")
        return 0

    if args.step:
        if args.step not in step_gate_map:
            print(f"[repair-flow] ❌ 未找到 step: {args.step}")
            return 1
        gate_id = step_gate_map[args.step]
        if not gate_id:
            print(f"[repair-flow] ❌ step {args.step} 未声明 gate")
            return 1
        if gate_id not in gate_map:
            print(f"[repair-flow] ❌ step {args.step} 的 gate 未登记: {gate_id}")
            return 1
        gate = gate_map[gate_id]
        result = {
            "step": args.step,
            "gate": gate_id,
            "gate_name": gate.get("name", ""),
            "script": gate.get("script"),
            "fail_action": gate.get("fail_action", ""),
        }
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"[repair-flow] ✅ step {args.step} gate 已登记: "
                  f"{gate_id} — {gate.get('name', '')} "
                  f"(script: {gate.get('script')}, fail_action: {gate.get('fail_action')})")
        return 0

    # 默认行为：仅校验 + 汇总
    if not struct_ok:
        print("[repair-flow] ❌ 结构校验失败: %d 个错误" % len(errors))
        for e in errors:
            print(f"   - {e}")
        return 1
    print(f"[repair-flow] ✅ 声明合法 — version={data.get('version')} "
          f"steps={len(step_ids)} gates={len(gate_map)}")
    print(f"[repair-flow]    terminal_condition: {data.get('terminal_condition')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())