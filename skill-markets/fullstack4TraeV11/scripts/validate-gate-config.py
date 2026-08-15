#!/usr/bin/env python3
"""
validate-gate-config.py - 校验 gate-config.json（L1-L4 四档门禁声明）schema 完整性

定位:
  gate-config.json 是 V11 项目级四档 Git/CI 门禁的"单一权威源"，
  由 scripts/run-gate-level.py 程序化消费。本脚本负责校验该文件的
  schema 是否合法，防止"结构被改坏仍被 run-gate-level 静默消费"。

  对齐 agent-dev-control-kit 的 validate-gate-integrity.py 模式：
  机器可读、可 pytest 断言、能阻断 CI/husky。

检查维度:
  G1. 顶层 JSON 是否可解析 / 是否缺 levels
  G2. 每个档位是否缺必填字段（description / stage / host / checks / timeout_seconds / blocking）
  G3. checks / gates 是否结构合法（list of str）
  G4. timeout_seconds 是否正 int、blocking 是否 bool、stage 是否非空
  G5. L1-L4 四档是否齐全（缺档 = WARN，不阻断）

用法:
    python validate-gate-config.py [--config gates/gate-config.json] [--json]

退出码:
    0 = schema 合法（G5 缺档 WARN 不阻断）
    1 = 存在 HIGH/MEDIUM 违规
    2 = 参数/文件不存在
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

EXIT_OK = 0
EXIT_VULN = 1
EXIT_ARGS = 2

# 每个档位的必填字段
REQUIRED_FIELDS = [
    "description",
    "stage",
    "host",
    "checks",
    "timeout_seconds",
    "blocking",
]

# 期望的档位集合（V11 四档）
EXPECTED_LEVELS = ["L1", "L2", "L3", "L4"]

# 统一日志前缀（与 run-gate-level.py / run-all-guards.py 对齐）
LOG = "[v11-gate-config]"


def log(msg: str, stderr: bool = False) -> None:
    print(f"{LOG} {msg}", file=sys.stderr if stderr else sys.stdout)


def load_config(config_path: Path) -> Tuple[Optional[dict], List[dict]]:
    """加载 gate-config.json。返回 (data, vulns)；data=None 表示加载失败。"""
    if not config_path.exists():
        return None, [{
            "code": "G1-GATE-CONFIG-MISSING",
            "severity": "HIGH",
            "where": str(config_path),
            "message": f"gate-config.json 不存在（路径 {config_path}）",
        }]
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return None, [{
            "code": "G1-GATE-CONFIG-INVALID-JSON",
            "severity": "HIGH",
            "where": str(config_path),
            "message": f"gate-config.json JSON 解析失败: {e}",
        }]
    except Exception as e:
        return None, [{
            "code": "G1-GATE-CONFIG-READ-ERROR",
            "severity": "HIGH",
            "where": str(config_path),
            "message": f"读取 gate-config.json 失败: {e}",
        }]
    return data, []


def validate_level(level_id: str, cfg: Any) -> List[dict]:
    """校验单个档位。返回 vuln 列表（空 = 合法）。"""
    vulns: List[dict] = []
    if not isinstance(cfg, dict):
        vulns.append({
            "code": "G2-LEVEL-NOT-DICT",
            "severity": "HIGH",
            "where": f"levels.{level_id}",
            "message": f"档位 {level_id} 不是 dict（当前 type={type(cfg).__name__}）",
        })
        return vulns

    # G2 必填字段
    for field in REQUIRED_FIELDS:
        if field not in cfg:
            vulns.append({
                "code": "G2-LEVEL-MISSING-FIELD",
                "severity": "HIGH",
                "where": f"levels.{level_id}.{field}",
                "message": f"档位 {level_id} 缺必填字段 `{field}`",
            })

    # G3 checks 结构
    checks = cfg.get("checks")
    if checks is not None and not isinstance(checks, list):
        vulns.append({
            "code": "G3-CHECKS-NOT-LIST",
            "severity": "HIGH",
            "where": f"levels.{level_id}.checks",
            "message": f"档位 {level_id} 的 checks 不是 list",
        })
    elif isinstance(checks, list):
        for i, c in enumerate(checks):
            if not isinstance(c, str) or not c.strip():
                vulns.append({
                    "code": "G3-CHECKS-NOT-STR",
                    "severity": "HIGH",
                    "where": f"levels.{level_id}.checks[{i}]",
                    "message": f"档位 {level_id} 的 checks[{i}] 不是非空字符串",
                })

    # G3 gates 结构（可选字段）
    gates = cfg.get("gates")
    if gates is not None and not isinstance(gates, list):
        vulns.append({
            "code": "G3-GATES-NOT-LIST",
            "severity": "HIGH",
            "where": f"levels.{level_id}.gates",
            "message": f"档位 {level_id} 的 gates 不是 list",
        })
    elif isinstance(gates, list):
        for i, g in enumerate(gates):
            if not isinstance(g, str) or not g.strip():
                vulns.append({
                    "code": "G3-GATES-NOT-STR",
                    "severity": "MEDIUM",
                    "where": f"levels.{level_id}.gates[{i}]",
                    "message": f"档位 {level_id} 的 gates[{i}] 不是非空字符串",
                })

    # G4 timeout_seconds 正 int
    timeout = cfg.get("timeout_seconds")
    if timeout is not None and (not isinstance(timeout, int) or isinstance(timeout, bool) or timeout <= 0):
        vulns.append({
            "code": "G4-TIMEOUT-INVALID",
            "severity": "HIGH",
            "where": f"levels.{level_id}.timeout_seconds",
            "message": f"档位 {level_id} 的 timeout_seconds={timeout!r} 不是正 int",
        })

    # G4 blocking 是 bool
    blocking = cfg.get("blocking")
    if blocking is not None and not isinstance(blocking, bool):
        vulns.append({
            "code": "G4-BLOCKING-INVALID",
            "severity": "HIGH",
            "where": f"levels.{level_id}.blocking",
            "message": f"档位 {level_id} 的 blocking={blocking!r} 不是 bool",
        })

    # G4 stage 非空
    stage = cfg.get("stage")
    if stage is not None and (not isinstance(stage, str) or not stage.strip()):
        vulns.append({
            "code": "G4-STAGE-EMPTY",
            "severity": "MEDIUM",
            "where": f"levels.{level_id}.stage",
            "message": f"档位 {level_id} 的 stage 为空或非字符串",
        })

    return vulns


def run_checks(config_path: Path) -> Tuple[List[dict], List[str]]:
    """执行校验。返回 (vulns, warnings)。"""
    data, vulns = load_config(config_path)
    if data is None:
        return vulns, []

    warnings: List[str] = []
    if not isinstance(data, dict):
        vulns.append({
            "code": "G1-GATE-CONFIG-NOT-DICT",
            "severity": "HIGH",
            "where": str(config_path),
            "message": "gate-config.json 顶层不是 dict",
        })
        return vulns, warnings

    levels = data.get("levels")
    if not isinstance(levels, dict) or not levels:
        vulns.append({
            "code": "G1-GATE-CONFIG-MISSING-LEVELS",
            "severity": "HIGH",
            "where": f"{config_path} levels",
            "message": "gate-config.json 缺 `levels` dict（或为空）",
        })
        return vulns, warnings

    # G5 缺档检查（WARN 不阻断）
    present = set(levels.keys())
    missing = [lv for lv in EXPECTED_LEVELS if lv not in present]
    if missing:
        warnings.append(f"缺档位: {','.join(missing)}（run-gate-level 会因 unknown-level FAIL，建议补齐）")

    for level_id, cfg in levels.items():
        vulns += validate_level(level_id, cfg)

    return vulns, warnings


def format_text(vulns: List[dict], warnings: List[str], target: Path) -> str:
    if not vulns and not warnings:
        return f"✅ gate-config.json schema 合法: {target}"
    out: List[str] = []
    if vulns:
        out.append(f"🛑 {len(vulns)} gate-config schema 违规: {target}")
        for v in vulns:
            out.append(f"  [{v['severity']}] {v['code']}")
            out.append(f"      where:   {v['where']}")
            out.append(f"      message: {v['message']}")
            out.append("")
    if warnings:
        for w in warnings:
            out.append(f"  ⚠️  {w}")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="validate gate-config.json (L1-L4) schema 完整性"
    )
    parser.add_argument("--config", default="gates/gate-config.json",
                        help="gate-config.json 路径")
    parser.add_argument("--json", action="store_true", help="JSON 输出（CI 集成）")
    args = parser.parse_args()

    target = Path(args.config).resolve()
    vulns, warnings = run_checks(target)

    if args.json:
        print(json.dumps({
            "config": str(target),
            "vulnerabilities": vulns,
            "warnings": warnings,
            "count": len(vulns),
            "exit_code": EXIT_VULN if vulns else EXIT_OK,
        }, ensure_ascii=False, indent=2))
    else:
        print(format_text(vulns, warnings, target))

    return EXIT_VULN if vulns else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())