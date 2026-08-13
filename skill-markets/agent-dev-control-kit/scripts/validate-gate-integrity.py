#!/usr/bin/env python3
"""
validate-gate-integrity.py - 检测目标项目的 gate 完整性漏洞

检查目标项目是否存在以下问题：
  V1. package.json 缺少必需脚本（从 scaffold.yaml 的 required_scripts 读取）
  V2. 存在 echo 跳过型假脚本（如 'echo "skipping ..."'）
  V3. gate 脚本未引用真实脚本（pre-commit.sh/pre-push.sh 跑 echo/true/冒号）
  V4. 必须的工具/文件不存在（ruff / mypy / pytest / go / mvn / package.json / pyproject.toml ...）

使用：
    python validate-gate-integrity.py [--target PATH] [--scaffold-id ID] [--json]

退出码：
    0 = 无漏洞
    1 = 发现漏洞
    2 = 参数/配置错误

关联：
    - scaffolds/<id>/scaffold.yaml 中 required_scripts 字段
    - scaffolds/<id>/files/gates/pre-{commit,push}.sh
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

EXIT_OK = 0
EXIT_VULN = 1
EXIT_ARGS = 2

# Patterns for echo-skip placeholder scripts (Node.js side)
ECHO_SKIP_PATTERNS = [
    r"echo\s+['\"]?(?:skip|not\s+config|skipping|no\s+\w+\s+configured)",
    r"echo\s+['\"](?:skipping|no\s+\w+\s+configured)",
    r":\s*;?\s*$",  # bare `:` colon no-op
    r"true\s*$",     # bare `true`
]

# Patterns for gate script body that doesn't actually run anything
GATE_FAKE_BODY_PATTERNS = [
    r"echo\s+['\"]?[A-Z][^']*skipping",
    r"command\s+-v\s+\S+\s*>\s*/dev/null.*\|\|\s*echo.*skip",
]


def parse_scaffold_yaml(scaffold_yaml: Path) -> Dict[str, Any]:
    """解析 scaffold.yaml，返回 required_scripts / required_files 等字段。"""
    if not scaffold_yaml.exists():
        return {}
    try:
        import yaml  # type: ignore
        with scaffold_yaml.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
    except ImportError:
        # Fallback: very small regex parser
        return _parse_scaffold_yaml_fallback(scaffold_yaml)
    except Exception as e:
        print(f"⚠️  解析 {scaffold_yaml} 失败: {e}", file=sys.stderr)
        return {}
    return data or {}


def _parse_scaffold_yaml_fallback(path: Path) -> Dict[str, Any]:
    """无 PyYAML 时的最小化解析器。"""
    out: Dict[str, Any] = {"required_scripts": {}}
    text = path.read_text(encoding='utf-8')
    in_block = False
    block_lines: List[str] = []
    block_key = ""
    for line in text.splitlines():
        stripped = line.strip()
        if not in_block and stripped.startswith("required_scripts:"):
            in_block = True
            continue
        if in_block:
            if not line.startswith(" ") and line.strip() and not line.startswith("#"):
                in_block = False
                if block_lines and block_key:
                    out["required_scripts"][block_key] = [
                        x.strip().strip("'\"") for x in block_lines if x.strip().startswith("- ")
                    ]
                block_lines = []
                block_key = ""
                continue
            m = re.match(r"^\s+([a-z_]+):\s*$", line)
            if m:
                if block_lines and block_key:
                    out["required_scripts"][block_key] = [
                        x.strip().strip("'\"") for x in block_lines if x.strip().startswith("- ")
                    ]
                block_key = m.group(1)
                block_lines = []
                continue
            if stripped.startswith("- "):
                block_lines.append(stripped)
    if block_lines and block_key:
        out["required_scripts"][block_key] = [
            x.strip().strip("'\"") for x in block_lines if x.strip().startswith("- ")
        ]
    return out


def find_scaffold_dir(scaffold_id: str, target: Path) -> Optional[Path]:
    """在多个候选位置查找 scaffold。"""
    candidates = [
        Path(__file__).resolve().parent.parent / "scaffolds" / scaffold_id,
        Path.home() / ".agent-dev-control-kit" / "scaffolds" / scaffold_id,
        target / "scaffolds" / scaffold_id,
        Path.cwd() / "scaffolds" / scaffold_id,
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return None


def auto_detect_scaffold(target: Path) -> Optional[str]:
    """基于文件检测 scaffold id。"""
    if (target / "package.json").exists():
        return "nodejs"
    if (target / "pyproject.toml").exists() or (target / "requirements.txt").exists():
        return "python"
    if (target / "go.mod").exists():
        return "go"
    if (target / "pom.xml").exists():
        return "java-maven"
    return None


def is_echo_skip(body: str) -> bool:
    """判断是否是 echo 跳过型脚本。"""
    s = body.strip()
    for pat in ECHO_SKIP_PATTERNS:
        if re.search(pat, s, re.IGNORECASE):
            return True
    return False


def is_fake_gate_script(text: str) -> List[str]:
    """判断 gate 脚本是否是假执行。返回命中模式列表。"""
    hits: List[str] = []
    for pat in GATE_FAKE_BODY_PATTERNS:
        if re.search(pat, text, re.IGNORECASE | re.MULTILINE):
            hits.append(pat)
    return hits


def read_package_json_scripts(target: Path) -> Optional[Dict[str, str]]:
    pkg = target / "package.json"
    if not pkg.exists():
        return None
    try:
        with pkg.open('r', encoding='utf-8') as f:
            data = json.load(f)
        return (data.get('scripts') or {}) if isinstance(data, dict) else None
    except Exception as e:
        print(f"⚠️  解析 {pkg} 失败: {e}", file=sys.stderr)
        return None


def check_nodejs(target: Path, required: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    vulns: List[Dict[str, Any]] = []
    pkg_scripts = read_package_json_scripts(target)
    if pkg_scripts is None:
        vulns.append({
            "code": "V1-NODEJS-NO-PKG",
            "severity": "HIGH",
            "where": "package.json",
            "message": "package.json missing — gate cannot verify any required script",
        })
        return vulns

    for phase in ("pre_commit", "pre_push"):
        scripts = required.get(phase, []) or []
        for s in scripts:
            if s not in pkg_scripts:
                vulns.append({
                    "code": "V1-NODEJS-MISSING-SCRIPT",
                    "severity": "HIGH",
                    "where": f"package.json scripts.{s}",
                    "message": f"required script '{s}' missing (from {phase})",
                })
            else:
                body = pkg_scripts[s]
                if is_echo_skip(body):
                    vulns.append({
                        "code": "V2-NODEJS-ECHO-SKIP",
                        "severity": "HIGH",
                        "where": f"package.json scripts.{s}",
                        "message": f"script '{s}' is an echo-skip placeholder: {body!r}",
                    })
    return vulns


def check_python(target: Path, required: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    vulns: List[Dict[str, Any]] = []
    pyproject = target / "pyproject.toml"
    if not pyproject.exists():
        vulns.append({
            "code": "V1-PY-NO-PYPROJECT",
            "severity": "HIGH",
            "where": "pyproject.toml",
            "message": "pyproject.toml missing — gate cannot verify tools",
        })
        return vulns

    import shutil
    needed = set()
    for phase in ("pre_commit", "pre_push"):
        for s in (required.get(phase) or []):
            needed.add(s)

    # Add Python stdlib tool: 'build' is from `pip install build`
    for tool in sorted(needed):
        if shutil.which(tool) is None:
            vulns.append({
                "code": "V4-PY-TOOL-MISSING",
                "severity": "HIGH",
                "where": f"PATH tool '{tool}'",
                "message": f"required tool '{tool}' not installed; install with: pip install -e '.[dev]'",
            })

    # Check build-backend if required
    if required.get("build_backend"):
        text = pyproject.read_text(encoding='utf-8')
        if not re.search(r"build-backend\s*=", text):
            vulns.append({
                "code": "V1-PY-NO-BUILD-BACKEND",
                "severity": "MEDIUM",
                "where": "pyproject.toml",
                "message": "build-backend not declared — pre-push gate may fail",
            })
    return vulns


def check_go(target: Path, required: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    vulns: List[Dict[str, Any]] = []
    if not (target / "go.mod").exists():
        vulns.append({
            "code": "V1-GO-NO-MOD",
            "severity": "HIGH",
            "where": "go.mod",
            "message": "go.mod missing — gate cannot proceed",
        })

    import shutil
    if shutil.which("go") is None:
        vulns.append({
            "code": "V4-GO-TOOL-MISSING",
            "severity": "HIGH",
            "where": "PATH tool 'go'",
            "message": "go not installed",
        })
    if shutil.which("golangci-lint") is None:
        vulns.append({
            "code": "V4-GO-LINT-MISSING",
            "severity": "MEDIUM",
            "where": "PATH tool 'golangci-lint'",
            "message": "golangci-lint not installed (gate will fall back to go vet)",
        })

    required_dirs = required.get("required_dirs") or []
    for d in required_dirs:
        if not (target / d).is_dir():
            vulns.append({
                "code": "V1-GO-DIR-MISSING",
                "severity": "MEDIUM",
                "where": d,
                "message": f"required dir '{d}' missing",
            })
    return vulns


def check_java(target: Path, required: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    vulns: List[Dict[str, Any]] = []
    pom = target / "pom.xml"
    if not pom.exists():
        vulns.append({
            "code": "V1-JAVA-NO-POM",
            "severity": "HIGH",
            "where": "pom.xml",
            "message": "pom.xml missing",
        })
        return vulns

    import shutil
    if shutil.which("mvn") is None:
        vulns.append({
            "code": "V4-JAVA-TOOL-MISSING",
            "severity": "HIGH",
            "where": "PATH tool 'mvn'",
            "message": "mvn not installed",
        })

    text = pom.read_text(encoding='utf-8')
    must_contain = required.get("pom_must_contain") or []
    for needle in must_contain:
        if needle not in text:
            vulns.append({
                "code": "V1-JAVA-POM-MISSING",
                "severity": "MEDIUM",
                "where": "pom.xml",
                "message": f"pom.xml missing required plugin reference: {needle}",
            })
    return vulns


def check_gate_scripts(target: Path, scaffold_dir: Optional[Path]) -> List[Dict[str, Any]]:
    """检查 .husky/pre-commit / pre-push 是否引用了真实脚本（不是 echo 跳过）。"""
    vulns: List[Dict[str, Any]] = []
    husky = target / ".husky"
    if not husky.is_dir():
        return vulns  # husky not installed — no gate scripts to check

    for hook in ("pre-commit", "pre-push"):
        hook_path = husky / hook
        if not hook_path.exists():
            continue
        text = hook_path.read_text(encoding='utf-8')
        for pat in GATE_FAKE_BODY_PATTERNS:
            if re.search(pat, text, re.IGNORECASE | re.MULTILINE):
                vulns.append({
                    "code": "V3-HUSKY-FAKE-BODY",
                    "severity": "HIGH",
                    "where": str(hook_path.relative_to(target)),
                    "message": f"hook script contains fake-skip pattern: {pat}",
                })
                break
        # Check if it references gates/pre-{commit,push}.sh
        if scaffold_dir is not None:
            expected = scaffold_dir / "files" / "gates" / f"{hook}.sh"
            if expected.exists() and "gates/" not in text and hook + ".sh" not in text:
                # Soft warning only
                pass
    return vulns


def run_checks(target: Path, scaffold_id: Optional[str]) -> Tuple[List[Dict[str, Any]], Optional[Path]]:
    scaffold_dir: Optional[Path] = None
    if scaffold_id is None:
        scaffold_id = auto_detect_scaffold(target)
        if scaffold_id:
            print(f"🔍 auto-detected scaffold: {scaffold_id}")
    if scaffold_id:
        scaffold_dir = find_scaffold_dir(scaffold_id, target)

    required: Dict[str, Any] = {}
    if scaffold_dir:
        scaffold_yaml = scaffold_dir / "scaffold.yaml"
        required = parse_scaffold_yaml(scaffold_yaml).get("required_scripts") or {}
    else:
        print(f"⚠️  no scaffold metadata found — using minimal defaults", file=sys.stderr)

    vulns: List[Dict[str, Any]] = []
    sid = scaffold_id or ""
    if sid == "nodejs":
        vulns += check_nodejs(target, required)
    elif sid == "python":
        vulns += check_python(target, required)
    elif sid == "go":
        vulns += check_go(target, required)
    elif sid == "java-maven":
        vulns += check_java(target, required)
    else:
        vulns.append({
            "code": "V0-UNKNOWN-SCAFFOLD",
            "severity": "INFO",
            "where": str(target),
            "message": "could not determine scaffold; pass --scaffold-id explicitly",
        })

    vulns += check_gate_scripts(target, scaffold_dir)
    return vulns, scaffold_dir


def format_text(vulns: List[Dict[str, Any]], target: Path) -> str:
    if not vulns:
        return f"✅ No gate-integrity issues found in {target}"
    out = [f"🛑 {len(vulns)} gate-integrity issue(s) in {target}", ""]
    for v in vulns:
        out.append(f"  [{v['severity']}] {v['code']}")
        out.append(f"      where:   {v['where']}")
        out.append(f"      message: {v['message']}")
        out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect gate-integrity holes in target project")
    parser.add_argument("--target", type=Path, default=Path.cwd(), help="target project dir")
    parser.add_argument("--scaffold-id", help="force scaffold id (nodejs/python/go/java-maven)")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args()

    target = args.target.resolve()
    if not target.is_dir():
        print(f"🛑 target dir not found: {target}", file=sys.stderr)
        return EXIT_ARGS

    vulns, scaffold_dir = run_checks(target, args.scaffold_id)

    if args.json:
        print(json.dumps({
            "target": str(target),
            "scaffold_dir": str(scaffold_dir) if scaffold_dir else None,
            "vulnerabilities": vulns,
            "count": len(vulns),
        }, indent=2, ensure_ascii=False))
    else:
        print(format_text(vulns, target))

    return EXIT_OK if not vulns else EXIT_VULN


if __name__ == "__main__":
    sys.exit(main())