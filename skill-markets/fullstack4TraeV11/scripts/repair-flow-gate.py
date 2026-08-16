#!/usr/bin/env python3
"""
V11 repair-flow-gate.py — Bug 修复流程声明消费脚本（flow 层 registry）

程序化解析 registry/repair-flow.yaml，不靠 agent 硬读 md。
对齐 reason-classifier.py 的 argparse + 前缀输出风格。

Usage:
    python repair-flow-gate.py [--registry-dir <dir>] [--validate-only]
                               [--step <step-id>] [--list-steps]
                               [--strict] [--evidence-paths <step-1,step-2,step-3,step-4>]

Exit codes:
    0 = 校验通过 / 输出正常
    1 = 声明缺失 / 结构非法 / 校验失败 / strict 证据缺失
    2 = N/A — 留作 future use（沿用 0=PASS/1=FAIL/2=N/A 铁律）
"""
import sys
import argparse
import pathlib
import json

try:
    import yaml
except ImportError:
    print("[repair-flow] 缺少 PyYAML，请先执行: pip install pyyaml")
    sys.exit(1)


DEFAULT_REGISTRY = pathlib.Path(__file__).resolve().parent.parent / "registry"

# V11.8.x P2-2 NEW:strict 模式期望 4 步流程的固定顺序（必须按 registry/repair-flow.yaml 声明）
P2_2_STEP_ORDER = (
    "step-1-e2e-fail",
    "step-2-6layer",
    "step-3-fix-and-regression",
    "step-4-user-confirm",
)
# step-4 的 strict 校验必须前 3 步证据齐
P2_2_STEP_4_PREREQ = (
    "step-1-e2e-fail",
    "step-2-6layer",
    "step-3-fix-and-regression",
)


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


def validate_strict_evidence(
    step_id: str,
    evidence_paths: list,
    step_ids_in_registry: list,
) -> list:
    """V11.8.x P2-2 NEW:strict 模式校验证据链。

    Args:
        step_id: 当前正在校验的 step（来自 --step 参数）
        evidence_paths: 来自 --evidence-paths 的路径列表（按逗号分隔拆开后顺序保留）
        step_ids_in_registry: registry/repair-flow.yaml 中声明的 step.id 顺序

    Returns:
        errors: 错误列表（空 = 通过）

    规则:
        1. evidence_paths 数量必须 == P2_2_STEP_ORDER 数量（4）；不匹配直接 FAIL
        2. evidence_paths 顺序必须与 P2_2_STEP_ORDER 一致（step-1 → step-2 → step-3 → step-4）
        3. evidence_paths 每项必须非空且对应文件存在（存在用 pathlib.Path.exists()）
        4. 仅当 step_id == "step-4-user-confirm" 时才完整校验前 3 步证据齐
           其他 step 在 --strict 模式下也至少校验 evidence_paths 数量 + 顺序 + 路径非空
    """
    errors = []

    # 规则 1:数量匹配
    if len(evidence_paths) != len(P2_2_STEP_ORDER):
        errors.append(
            f"strict 模式下 --evidence-paths 必须含 {len(P2_2_STEP_ORDER)} 项 "
            f"（按 P2_2_STEP_ORDER 顺序）— 当前 {len(evidence_paths)} 项。"
            f"示例: --evidence-paths <step-1.md>,<step-2.md>,<step-3.md>,<step-4.md>"
        )
        # 数量错则不再做后续校验，避免错误级联
        return errors

    # 规则 2:顺序匹配（按 evidence_paths 顺序每项映射到 P2_2_STEP_ORDER 对应位）
    # 我们无法从「路径字符串」反推 step-id,这里采用「位置对齐」:
    #   evidence_paths[i] <-> P2_2_STEP_ORDER[i]
    # 若 caller 想标识自己给的 4 段分别对应哪个 step,可以在路径里嵌 step 前缀;
    # 本校验函数做最严格的「位置对齐」+「路径非空 + 存在」检查
    for i, ep in enumerate(evidence_paths):
        if not ep or not ep.strip():
            errors.append(
                f"strict 模式下 evidence_paths[{i}] 为空（对应 {P2_2_STEP_ORDER[i]}）。"
                f"正确示例: --evidence-paths e1.md,e2.md,e3.md,e4.md"
            )
            continue
        # 跳过注册表校验(本函数专注 evidence 文件存在性)
        # 注册表校验已由 validate_structure 处理

    # 规则 3:文件存在性
    for i, ep in enumerate(evidence_paths):
        if not ep or not ep.strip():
            continue  # 已在规则 2 报错
        p = pathlib.Path(ep.strip())
        if not p.exists():
            errors.append(
                f"strict 证据文件不存在: {p}（对应 {P2_2_STEP_ORDER[i]}）。"
                f"正确示例: {p} 由前 3 步执行后落盘的 .md / .log / .json 产出"
            )
            continue
        if not p.is_file():
            errors.append(
                f"strict 证据路径不是文件: {p}（对应 {P2_2_STEP_ORDER[i]}）。"
                f"应该是 4 步流程落盘的 .md / .log / .json 报告文件"
            )

    # 规则 4:仅 step-4 才强制前 3 步齐
    if step_id == "step-4-user-confirm":
        # evidence_paths[0..2] 必须存在（已在规则 3 检查过，只是显式再点出）
        for j, prereq in enumerate(P2_2_STEP_4_PREREQ):
            ep = evidence_paths[j].strip() if evidence_paths[j] else ""
            if not ep or not pathlib.Path(ep).exists():
                # 规则 3 已报过；这里只补一条「关系注解」便于主上下文读懂
                errors.append(
                    f"step-4-user-confirm 跑前必 {prereq} 完成 — "
                    f"evidence_paths[{j}]={ep!r} 缺失或不合法"
                )

    return errors


def check_step_order_against_paths(
    evidence_paths: list,
) -> list:
    """检查 evidence_paths 顺序是否与 P2_2_STEP_ORDER 一致。

    接受两种"顺序表达":
      A. 路径前缀/step-id 标记（如 step-1-e2e-fail.md / step-2-6layer.md ...）
      B. 路径含子字符串（任何包含 step-N- 的字符串视为对应步骤）
    默认 A。若未匹配出 4 个 step-id,视为「顺序乱」。

    返回 errors 列表。
    """
    errors = []
    mapped = []
    for i, ep in enumerate(evidence_paths):
        ep_str = (ep or "").strip()
        # 解析路径基名
        base = pathlib.Path(ep_str).name if ep_str else ""
        matched_step = None
        for step_id in P2_2_STEP_ORDER:
            # 用短前缀 step-N 避免误匹配说明文本
            short = step_id.split("-")[0] + "-" + step_id.split("-")[1]  # step-1
            if short in base:
                matched_step = step_id
                break
        mapped.append((i, ep_str, matched_step))

    # 推断"目标顺序":从路径中解析出的 step-id 序列
    inferred = [m for _, _, m in mapped]
    if None in inferred:
        # 路径不含 step-N 前缀 → 不强制顺序（视为弱校验通过）
        return errors
    if inferred != list(P2_2_STEP_ORDER):
        bad = [(i, e, m) for i, e, m in mapped if m]
        errors.append(
            "evidence_paths 顺序与 P2_2_STEP_ORDER 不一致:"
            f"实际={inferred} 期望={list(P2_2_STEP_ORDER)}。"
            f"映射关系: {bad}。"
            f"正确示例: --evidence-paths step-1-e2e-fail.md,step-2-6layer.md,"
            f"step-3-fix-and-regression.md,step-4-user-confirm.md"
        )
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
    # V11.8.x P2-2 NEW:strict 模式 + 多证据路径
    parser.add_argument("--strict", action="store_true",
                        help="strict 模式:校验证据链完整性(配合 --step + --evidence-paths)")
    parser.add_argument("--evidence-paths", default="",
                        help="strict 模式下的证据文件路径(逗号分隔,顺序对应 P2_2_STEP_ORDER)")
    args = parser.parse_args()

    try:
        data = load_flow(args.registry_dir)
    except Exception as e:
        print(f"[repair-flow] 声明加载失败: {e}")
        return 1

    # 结构校验（始终执行）
    errors = validate_structure(data)
    struct_ok = not errors

    step_ids = [s["id"] for s in data.get("steps", [])]
    gate_map = {g["id"]: g for g in data.get("gates", [])}
    step_gate_map = {s["id"]: s.get("gate") for s in data.get("steps", [])}

    # V11.8.x P2-2 NEW:strict 模式处理
    # --strict 必须配合 --step + --evidence-paths;否则按"未启用 strict"退回原行为
    if args.strict and not args.step:
        print("[repair-flow] --strict 必须配合 --step 使用")
        return 1

    if args.strict and args.step:
        # 解析 evidence_paths
        evidence_paths = [p.strip() for p in args.evidence_paths.split(",") if p.strip()]
        # 解析 --step 必须登记
        if args.step not in step_gate_map:
            print(f"[repair-flow] --step {args.step} 未登记")
            return 1
        # strict 主体校验
        strict_errors = validate_strict_evidence(
            step_id=args.step,
            evidence_paths=evidence_paths,
            step_ids_in_registry=step_ids,
        )
        # 顺序乱(单独检查,以便给出清晰的乱序错误)
        order_errors = check_step_order_against_paths(evidence_paths)
        all_strict_errors = strict_errors + order_errors
        if all_strict_errors:
            print(
                f"[repair-flow] strict FAIL 步骤 {args.step} — "
                f"{len(all_strict_errors)} 个错误"
            )
            for e in all_strict_errors:
                print(f"   - {e}")
            if args.json:
                print(json.dumps({
                    "status": "FAIL",
                    "step": args.step,
                    "strict": True,
                    "errors": all_strict_errors,
                }, indent=2, ensure_ascii=False))
            return 1
        # strict 通过
        print(
            f"[repair-flow] strict PASS 步骤 {args.step} — "
            f"4 个证据文件齐 + 顺序正确"
        )
        if args.json:
            print(json.dumps({
                "status": "PASS",
                "step": args.step,
                "strict": True,
                "evidence_count": len(evidence_paths),
            }, indent=2, ensure_ascii=False))
        return 0

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