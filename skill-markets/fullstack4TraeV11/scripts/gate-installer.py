#!/usr/bin/env python3
"""
V11 gate-installer.py — 贾维斯时机①安装器(项目初始化/分层新增)

从 V11 registry/gates.yaml 读 layer 分层,在目标项目生成:
  gates/gate-config.json   — L1-L4 + module/app/system 分层段(单一权威门禁源)
  .husky/pre-commit        — L1(module 层)hook,先过 integrity 校验
  .husky/pre-push          — L2(app 层)hook,先过 integrity 校验

仅贾维斯 sub-agent 可调用(见 skills/00-boot/agents/jarvis.md §3 白名单)。

Usage:
    python gate-installer.py --target <目标项目根> --preset <nodejs|python> [--layers module,app,system] [--dry-run]

Exit codes:
    0 = 安装/更新成功
    1 = 参数错误 / registry 缺失 / 写入失败
"""
import sys
import json
import argparse
import pathlib

VALID_LAYERS = ("docs", "module", "app", "system")
PRESETS = {
    "nodejs": {
        "L1": ["lint", "typecheck", "test:unit"],
        "L2": ["test:integration", "test:coverage", "build"],
        "L3": ["test:e2e"],
        "L4": ["test:all", "security-scan"],
    },
    "python": {
        "L1": ["ruff", "mypy", "pytest -m unit"],
        "L2": ["pytest -m integration", "pytest --cov", "build"],
        "L3": ["pytest -m e2e"],
        "L4": ["pytest", "safety check"],
    },
}

INTEGRITY_PRELUDE = """# --- V11 hash 锁校验(贾维斯机械防线,勿删) ---
GATE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if [ -f "$GATE_DIR/scripts/gate-integrity-guard.py" ] && [ -f "$GATE_DIR/gates/gate.lock.yaml" ]; then
  "$GATE_DIR/scripts/gate-integrity-guard.py" --verify --root "$GATE_DIR" || exit 1
else
  echo "🛑 [V11] gate.lock.yaml 或 integrity-guard 缺失 — 请委派贾维斯(gate-installer)初始化" >&2
  exit 1
fi
# --- hash 锁校验结束 ---
"""


def load_gates_registry(v11_root: pathlib.Path) -> dict:
    """解析 registry/gates.yaml(无 PyYAML 依赖的最小解析:V12 扩展消费 layer / host / stage / required_artifacts / script 字段)。"""
    gates_path = v11_root / "registry" / "gates.yaml"
    if not gates_path.exists():
        print(f"❌ registry 不存在: {gates_path}", file=sys.stderr)
        sys.exit(1)
    gates = []
    current = {}
    # V12 扩展:消费 layer / host / stage / required_artifacts / script 字段
    v12_field_keys = ("layer:", "host:", "stage:", "required_artifacts:", "script:")
    for line in gates_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            if current:
                gates.append(current)
            current = {"id": stripped.split(":", 1)[1].strip()}
        elif current and any(stripped.startswith(k) for k in v12_field_keys):
            key, _, value = stripped.partition(":")
            k = key.strip()
            v = value.strip()
            # V12 多值字段: required_artifacts 支持列表展开
            if k == "required_artifacts":
                current[k] = [x.strip() for x in v.split(",")] if v else []
            else:
                current[k] = v
    if current:
        gates.append(current)
    return {"gates": gates}


def build_gate_config(preset: str, layers: list, registry: dict) -> dict:
    """按贾维斯分层模型生成目标项目 gate-config.json。"""
    checks = PRESETS[preset]

    def gate_ids_for(*layer_values):
        return [
            g["id"] for g in registry["gates"]
            if g.get("layer") in layer_values
        ]

    config = {
        "version": "1.2.0",
        "preset": preset,
        "jarvis": {
            "layers": layers,
            "protocol": "references/gate-configuration-protocol.md",
            "lock": "gates/gate.lock.yaml",
        },
        "description": "V11 分层门禁配置(贾维斯体系)。修改必经 [JARVIS-DELEGATION] 委派,勿直改。",
        "levels": {
            "L1": {
                "description": "Pre-commit — L-module 模块基础层(CRUD 单元级)",
                "layer": "module",
                "stage": "3/implement",
                "host": "husky-pre-commit",
                "checks": checks["L1"],
                "gates": gate_ids_for("module") if "module" in layers else [],
                "timeout_seconds": 120,
                "blocking": True,
            },
            "L2": {
                "description": "Pre-push — L-app 应用层(契约 + 模块集成 + 真实验证)",
                "layer": "app",
                "stage": "2/contract,3.5/real-verify",
                "host": "husky-pre-push",
                "checks": checks["L2"],
                "gates": gate_ids_for("app") if "app" in layers else [],
                "timeout_seconds": 600,
                "blocking": True,
            },
            "L3": {
                "description": "PR merge — L-system 系统层(AC 核销验收 + 腐化扫描)",
                "layer": "system",
                "stage": "4/review,4.5/rot-scan",
                "host": "github-actions",
                "checks": checks["L3"],
                "gates": gate_ids_for("system") if "system" in layers else [],
                "timeout_seconds": 1800,
                "blocking": True,
            },
            "L4": {
                "description": "Release — L-system 发布门禁(验收归档 + 安全审计)",
                "layer": "system",
                "stage": "5/accept",
                "host": "github-actions",
                "checks": checks["L4"],
                "gates": ["stage-accept"] if "system" in layers else [],
                "timeout_seconds": 3600,
                "blocking": True,
            },
        },
    }
    return config


def write_hooks(target: pathlib.Path) -> list:
    """生成 .husky hooks(注入 hash 锁 prelude)。幂等:重复安装覆盖。"""
    written = []
    hooks_dir = target / ".husky"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    pre_commit = "#!/usr/bin/env bash\n# V11 L1 pre-commit(L-module)— 贾维斯生成,修改必经委派\nset -euo pipefail\n" + INTEGRITY_PRELUDE + """
echo "==> [V11 L1 / L-module] pre-commit gate..."
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
FAILURES=0
"""
    # 按 preset 读 checks
    pre_commit += '\n# 逐项跑 gate-config L1 checks(由 run-gate-level.py 或 npm/pip scripts 承载)\n'
    pre_commit += 'echo "    L1 checks 定义于 gates/gate-config.json levels.L1.checks"\n'
    pre_commit += 'if [ -f scripts/run-gate-level.py ]; then\n  python scripts/run-gate-level.py --level L1 || FAILURES=$((FAILURES+1))\nfi\n'
    pre_commit += """
if [ $FAILURES -gt 0 ]; then
  echo "==> [L1] FAILED ($FAILURES)"
  exit 1
fi
echo "==> [L1 / L-module] PASSED"
"""

    pre_push = "#!/usr/bin/env bash\n# V11 L2 pre-push(L-app)— 贾维斯生成,修改必经委派\nset -euo pipefail\n" + INTEGRITY_PRELUDE + """
echo "==> [V11 L2 / L-app] pre-push gate..."
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
FAILURES=0
if [ -f scripts/run-gate-level.py ]; then
  python scripts/run-gate-level.py --level L2 || FAILURES=$((FAILURES+1))
fi
if [ $FAILURES -gt 0 ]; then
  echo "==> [L2] FAILED ($FAILURES)"
  exit 1
fi
echo "==> [L2 / L-app] PASSED"
"""
    (hooks_dir / "pre-commit").write_text(pre_commit, encoding="utf-8", newline="\n")
    (hooks_dir / "pre-push").write_text(pre_push, encoding="utf-8", newline="\n")
    written.extend([hooks_dir / "pre-commit", hooks_dir / "pre-push"])
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description="V11 贾维斯 gate 安装器")
    ap.add_argument("--target", required=True, type=pathlib.Path, help="目标项目根目录")
    ap.add_argument("--preset", required=True, choices=list(PRESETS), help="技术栈 preset")
    ap.add_argument("--layers", default="module,app,system",
                    help="安装的分层(逗号分隔,默认 module,app,system)")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划不写盘")
    args = ap.parse_args()

    layers = [x.strip() for x in args.layers.split(",") if x.strip()]
    invalid = [x for x in layers if x not in VALID_LAYERS]
    if invalid:
        print(f"❌ 非法 layer: {invalid}(可选 {VALID_LAYERS})", file=sys.stderr)
        return 1

    v11_root = pathlib.Path(__file__).resolve().parent.parent
    registry = load_gates_registry(v11_root)
    config = build_gate_config(args.preset, layers, registry)

    gates_dir = args.target / "gates"
    plan = [
        f"gates/gate-config.json  (layers={layers}, preset={args.preset})",
        ".husky/pre-commit       (L1 / L-module + hash 锁 prelude)",
        ".husky/pre-push         (L2 / L-app + hash 锁 prelude)",
    ]
    print("[JARVIS-INSTALLER] 计划写入:")
    for p in plan:
        print(f"  - {p}")

    if args.dry_run:
        print(json.dumps(config, ensure_ascii=False, indent=2))
        print("[JARVIS-INSTALLER] dry-run 结束,未写盘")
        return 0

    gates_dir.mkdir(parents=True, exist_ok=True)
    (gates_dir / "gate-config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_hooks(args.target)

    print("[JARVIS-INSTALLER] ✅ 安装完成")
    print("  下一步(贾维斯时机①收尾): 跑 gate-integrity-guard.py --generate 生成 gate.lock.yaml")
    print("  提示: lock 生成后,任何未委派贾维斯的 gate 文件改动都会被 --verify 拦截")
    return 0


if __name__ == "__main__":
    sys.exit(main())
