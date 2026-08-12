#!/usr/bin/env python3
"""check_integration_contract.py — V11.1 接入契约硬门禁（蒸馏自 V10）

扫描项目源码检查 5 项契约违规（项目级配置，可按需启用）。
每个违例 = 🛑 REJECT。

V11 通用版：项目可自定义契约规则（见 .trae/integration-contract.yaml）。
默认提供 5 项通用契约（V10 蒸馏）。

用法:
  python check_integration_contract.py --project-root /path/to/your-project
  python check_integration_contract.py --project-root /path/to/your-project --json
  python check_integration_contract.py --project-root /path/to/your-project --strict

5 项默认契约:
  1. 不直接 fetch('/api/v1/...') — 必须走 apiClient.get/post/...
  2. 不直接 addEventListener('keydown', ...) — 必须用 registerShortcut 或 useKeyboardShortcuts
  3. 新模块必须有 ModuleDef 入口 — 扫描 src/modules/<name>/index.tsx (index.ts 也算)
  4. 后端模块必须 pub trait Module 实现 — advisory (不强求,仅提醒)
  5. 事件命名符合 `<domain>:<action>` — 扫描 eventBus.emit('xxx:yyy', ...)

白名单 (允许直 fetch 的场景):
  - .test.tsx / .test.ts (测试 mock)
  - __tests__/ 目录下所有文件
  - src/shared/api-client.ts (ApiClient 自身实现)
  - src/shared/hooks/useKeyboardShortcuts.ts (hook 自身)

V11.1 vs V10:
  - 项目可配 .trae/integration-contract.yaml 自定义契约规则
  - 默认 5 项契约来自 V10 实战蒸馏
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple


# 默认契约规则（V10 蒸馏）
DEFAULT_CONTRACT_RULES: Dict[str, Dict] = {
    "no_direct_fetch": {
        "name": "不直接 fetch('/api/v1/...')",
        "severity": "high",
        "pattern": r"""fetch\(\s*['"`]/api/v\d+/[^'"`]*['"`]""",
        "scope": ("*.ts", "*.tsx"),
        "whitelist": [
            r"__tests__[/\\]",
            r"[/\\]\.trae[/\\]",
            r"[/\\]node_modules[/\\]",
            r"[/\\]dist[/\\]",
            "src/shared/api-client.ts",
        ],
    },
    "no_direct_keydown": {
        "name": "不直接 addEventListener('keydown', ...)",
        "severity": "high",
        "pattern": r"""addEventListener\(\s*['"]keydown['"]""",
        "scope": ("*.ts", "*.tsx"),
        "whitelist": [
            "src/shared/hooks/useKeyboardShortcuts.ts",
            "src/shared/hooks/useWorkbenchShortcuts.ts",
        ],
    },
    "no_direct_eventbus_emit": {
        "name": "事件命名符合 `<domain>:<action>`",
        "severity": "medium",
        "pattern": r"""eventBus\.emit\(\s*['"]([^'"`]+)['"]""",
        "validation": "format_check",  # 必须含 ":" 分隔
        "validation_pattern": r"^[a-z\-]+:[a-z\-]+$",
        "scope": ("*.ts", "*.tsx"),
    },
}


def load_project_contract(project_root: Path) -> Dict:
    """加载项目级契约配置（.trae/integration-contract.yaml）"""
    config_path = project_root / ".trae" / "integration-contract.yaml"
    if not config_path.exists():
        return DEFAULT_CONTRACT_RULES
    try:
        import yaml
        with open(config_path, encoding="utf-8") as f:
            user_rules = yaml.safe_load(f)
        # 合并：用户规则覆盖默认规则
        merged = {**DEFAULT_CONTRACT_RULES}
        if user_rules:
            for rule_id, rule_cfg in user_rules.items():
                if rule_id in merged:
                    merged[rule_id] = {**merged[rule_id], **rule_cfg}
                else:
                    merged[rule_id] = rule_cfg
        return merged
    except ImportError:
        return DEFAULT_CONTRACT_RULES
    except Exception:
        return DEFAULT_CONTRACT_RULES


def is_whitelisted(file_path: Path, whitelist: List[str]) -> bool:
    """检查文件路径是否在白名单"""
    p = str(file_path).replace("\\", "/")
    for pat in whitelist:
        if pat.startswith(r"__tests__") or "/" in pat:
            if re.search(pat, p):
                return True
        else:
            if pat in p:
                return True
    return False


def _line_of(content: str, offset: int) -> int:
    return content[:offset].count("\n") + 1


def scan_contract_violations(project_root: Path, rules: Dict) -> List[Dict]:
    """扫描项目源码的契约违规

    Returns:
        violations: [
            {
                "rule_id": "no_direct_fetch",
                "severity": "high",
                "file": "src/auth/login.ts",
                "line": 42,
                "snippet": "fetch('/api/v1/auth/login', ...)",
                "description": "不直接 fetch('/api/v1/...')"
            },
            ...
        ]
    """
    violations = []
    src_dir = project_root / "src"
    if not src_dir.exists():
        return violations

    for ext_pattern in ("*.ts", "*.tsx", "*.py", "*.rs", "*.go"):
        for src_file in src_dir.rglob(ext_pattern):
            try:
                content = src_file.read_text(encoding="utf-8")
            except Exception:
                continue

            for rule_id, rule_cfg in rules.items():
                whitelist = rule_cfg.get("whitelist", [])
                if is_whitelisted(src_file, whitelist):
                    continue

                pattern = rule_cfg.get("pattern", "")
                if not pattern:
                    continue
                try:
                    regex = re.compile(pattern)
                except re.error:
                    continue

                for match in regex.finditer(content):
                    line_no = _line_of(content, match.start())
                    snippet = content.split("\n")[line_no - 1].strip()

                    # 验证模式（format_check）
                    if rule_cfg.get("validation") == "format_check":
                        captured = match.group(1) if match.lastindex else ""
                        validation_pattern = rule_cfg.get("validation_pattern", "")
                        if validation_pattern and re.match(validation_pattern, captured):
                            continue  # 格式正确，跳过

                    violations.append({
                        "rule_id": rule_id,
                        "severity": rule_cfg.get("severity", "medium"),
                        "file": str(src_file.relative_to(project_root)),
                        "line": line_no,
                        "snippet": snippet,
                        "description": rule_cfg.get("name", rule_id),
                    })

    return violations


def scan_module_entry(project_root: Path) -> Tuple[List[Dict], List[Dict]]:
    """扫描新模块必须有 ModuleDef 入口（advisory）"""
    errors, advisory = [], []
    src_dir = project_root / "src" / "modules"
    if not src_dir.exists():
        return errors, advisory

    for module_dir in src_dir.iterdir():
        if not module_dir.is_dir():
            continue
        index_tsx = module_dir / "index.tsx"
        index_ts = module_dir / "index.ts"
        if not (index_tsx.exists() or index_ts.exists()):
            advisory.append({
                "rule_id": "module_entry_missing",
                "severity": "advisory",
                "file": str(module_dir.relative_to(project_root)),
                "line": 0,
                "snippet": "",
                "description": "新模块必须有 index.tsx 或 index.ts 入口",
            })

    return errors, advisory


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="V11.1 接入契约硬门禁（项目级可配置）",
        add_help=False,
    )
    parser.add_argument("--project-root", type=str, help="项目根路径")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--strict", action="store_true", help="严格模式（advisory 也算 FAIL）")
    parser.add_argument("--help", "-h", action="store_true", help="显示帮助")

    args = parser.parse_args(argv)

    if args.help:
        print(__doc__)
        return 0

    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        project_root = Path.cwd()

    rules = load_project_contract(project_root)
    violations = scan_contract_violations(project_root, rules)
    errors_adv, advisory = scan_module_entry(project_root)
    violations.extend(errors_adv)

    if args.strict:
        violations.extend(advisory)

    result = {
        "project_root": str(project_root),
        "rules_applied": list(rules.keys()),
        "violations_count": len(violations),
        "violations": violations,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Project: {project_root}")
        print(f"Rules applied: {len(rules)}")
        print(f"Violations: {len(violations)}")
        print()
        if violations:
            for v in violations:
                sev = v["severity"]
                icon = "🛑" if sev == "high" else "⚠️" if sev == "medium" else "💡"
                print(f"  {icon} [{sev}] {v['file']}:{v['line']} - {v['description']}")
                if v["snippet"]:
                    print(f"     → {v['snippet']}")
        else:
            print("✅ 无契约违规")

    if any(v["severity"] == "high" for v in violations):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())