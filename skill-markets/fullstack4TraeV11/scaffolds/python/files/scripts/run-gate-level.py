#!/usr/bin/env python3
"""
run-gate-level.py — V11 项目级四档门禁执行器（L1-L4）

定位: 消费 scaffolds/nodejs/files/gates/gate-config.json，
按档位（--level）执行该档的 checks（npm scripts）+ 可选 gates（V11 stage 门禁脚本）。
对齐 agent-dev-control-kit 的 gate-check.py 模式：门禁声明在 gate-config.json，
本脚本是程序化消费入口，不靠 agent 硬读。

Usage:
    python run-gate-level.py --level L3 [--config gates/gate-config.json]
                              [--project-root .] [--gates-yaml gates/gates.yaml]
                              [--json] [--timeout 1800]

Exit codes:
    0 = 全 PASS（含 SKIP gate）
    1 = 任一 check FAIL / 配置缺失 / 档位未知
<!-- scan-whitelist:SHELL_EXEC -->
SECURITY 标注 (V11.7.1 NEW): 本脚本含 SHELL_EXEC 调用, 全部为 V11 业务必需.
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys

EXIT_OK = 0
EXIT_FAIL = 1

# 统一日志前缀（与 run-all-guards.py / gitnexus hooks 对齐，便于 grep）
LOG = "[v11-gate]"


def log(msg: str) -> None:
    print(f"{LOG} {msg}")


def load_config(config_path: pathlib.Path) -> dict:
    """加载 gate-config.json，返回 levels dict；失败抛 IOError。"""
    if not config_path.exists():
        raise IOError(f"缺 gate-config.json（路径 {config_path}）")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise IOError(f"gate-config.json JSON 解析失败: {e}")
    levels = data.get("levels")
    if not isinstance(levels, dict) or not levels:
        raise IOError("gate-config.json 缺 `levels` dict")
    return levels


def load_script_for_gate(gates_yaml: pathlib.Path, gate_id: str) -> str | None:
    """从项目内 gates.yaml 解析 gate id -> script。无 gates.yaml 或未登记则返回 None。"""
    if not gates_yaml.exists():
        return None
    try:
        import yaml
        with open(gates_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return None
    for g in (data or {}).get("gates", []):
        if isinstance(g, dict) and g.get("id") == gate_id:
            return g.get("script")
    return None


# Python 语义 check 名 -> CLI 命令映射（与 python scaffold 的 husky 脚本保持一致）
PY_CHECK_COMMANDS = {
    "lint": ["ruff", "check", "."],
    "typecheck": ["mypy", "src/"],
    "test:unit": ["pytest", "tests/unit", "-v"],
    "test:integration": ["pytest", "tests/integration", "-v"],
    "test:e2e": ["pytest", "tests/e2e", "-v"],
    "test:all": ["pytest", "tests", "-v"],
    "test:coverage": ["pytest", "tests/", "--cov=src", "--cov-report=term-missing"],
    "build": ["python", "-m", "build"],
    "security-scan": ["bandit", "-r", "src/"],
}


def detect_project_type(project_root: pathlib.Path) -> str:
    """自动检测项目类型:nodejs / python / unknown。"""
    if (project_root / "package.json").exists():
        return "nodejs"
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        return "python"
    return "unknown"


def has_script(pkg: dict, name: str) -> bool:
    scripts = pkg.get("scripts") or {}
    return name in scripts


def is_echo_skip(body: str) -> bool:
    import re
    stripped = body.strip().lower()
    return bool(re.match(r'^echo\s+["\']?(skip|not|skipp)', stripped))


def find_npm():
    """跨平台定位 npm 可执行文件（Windows 下为 npm.cmd）。"""
    exe = shutil.which("npm")
    if exe:
        return exe
    if os.name == "nt":
        return shutil.which("npm.cmd")
    return None


def run_npm_check(project_root: pathlib.Path, pkg: dict, name: str, timeout: int) -> str:
    """校验并真实执行 npm run <name>。返回 PASS / FAIL。"""
    if not has_script(pkg, name):
        log(f"check={name} status=FAIL reason=script-missing (package.json 无 scripts.{name})")
        return "FAIL"
    body = pkg.get("scripts", {}).get(name, "")
    if is_echo_skip(body):
        log(f"check={name} status=FAIL reason=echo-skip-detected body={body!r}")
        return "FAIL"
    npm = find_npm()
    if not npm:
        log(f"check={name} status=FAIL reason=npm-not-found")
        return "FAIL"
    try:
        log(f"check={name} status=RUN cmd=npm-run-{name}")
        subprocess.run([npm, "run", name], cwd=str(project_root),
                       check=True, timeout=timeout)
        log(f"check={name} status=PASS")
        return "PASS"
    except subprocess.TimeoutExpired:
        log(f"check={name} status=FAIL reason=timeout limit={timeout}s")
        return "FAIL"
    except subprocess.CalledProcessError as e:
        log(f"check={name} status=FAIL reason=exit-{e.returncode}")
        return "FAIL"


def run_python_check(project_root: pathlib.Path, name: str, timeout: int) -> str:
    """校验并真实执行 python CLI check（ruff/mypy/pytest/...）。返回 PASS / FAIL。"""
    cmd = PY_CHECK_COMMANDS.get(name)
    if cmd is None:
        log(f"check={name} status=FAIL reason=unknown-python-check (PY_CHECK_COMMANDS 无此映射)")
        return "FAIL"
    tool = cmd[0]
    if shutil.which(tool) is None and cmd[0] not in ("python", "python3"):
        log(f"check={name} status=FAIL reason=tool-missing tool={tool}")
        return "FAIL"
    try:
        log(f"check={name} status=RUN cmd={' '.join(cmd)}")
        subprocess.run(cmd, cwd=str(project_root), check=True, timeout=timeout)
        log(f"check={name} status=PASS")
        return "PASS"
    except subprocess.TimeoutExpired:
        log(f"check={name} status=FAIL reason=timeout limit={timeout}s")
        return "FAIL"
    except subprocess.CalledProcessError as e:
        log(f"check={name} status=FAIL reason=exit-{e.returncode}")
        return "FAIL"


def run_gate(project_root: pathlib.Path, gate_id: str, script: str | None, timeout: int) -> str:
    """执行单个 V11 gate 脚本。返回 PASS / SKIP / FAIL。"""
    if not script:
        log(f"gate={gate_id} status=SKIP reason=not-registered-in-gates-yaml")
        return "SKIP"
    for cand in (project_root / "scripts" / script, pathlib.Path(script)):
        if cand.exists():
            break
    else:
        log(f"gate={gate_id} status=SKIP reason=script-not-found script={script}")
        return "SKIP"
    try:
        log(f"gate={gate_id} status=RUN script={script}")
        subprocess.run([sys.executable, str(cand)], cwd=str(project_root),
                       check=True, timeout=timeout)
        log(f"gate={gate_id} status=PASS")
        return "PASS"
    except subprocess.TimeoutExpired:
        log(f"gate={gate_id} status=FAIL reason=timeout limit={timeout}s")
        return "FAIL"
    except subprocess.CalledProcessError as e:
        log(f"gate={gate_id} status=FAIL reason=exit-{e.returncode}")
        return "FAIL"


def main() -> int:
    parser = argparse.ArgumentParser(description="V11 项目级四档门禁执行器")
    parser.add_argument("--level", required=True, choices=["L1", "L2", "L3", "L4"],
                        help="门禁档位")
    parser.add_argument("--config", default="gates/gate-config.json",
                        help="gate-config.json 路径（默认 gates/gate-config.json）")
    parser.add_argument("--project-root", default=".", help="项目根")
    parser.add_argument("--gates-yaml", default="gates/gates.yaml",
                        help="V11 stage 门禁注册表（可选，用于解析 gate id -> script）")
    parser.add_argument("--timeout", type=int, default=None,
                        help="覆盖 timeout_seconds（默认读配置）")
    parser.add_argument("--json", action="store_true", help="JSON 输出（CI 集成）")
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    try:
        levels = load_config(pathlib.Path(args.config))
    except IOError as e:
        log(f"status=FAIL reason={e}")
        return EXIT_FAIL

    if args.level not in levels:
        log(f"level={args.level} status=FAIL reason=unknown-level (available={','.join(levels)})")
        return EXIT_FAIL

    cfg = levels[args.level]
    timeout = args.timeout or cfg.get("timeout_seconds", 600)
    checks = cfg.get("checks", [])
    gates = cfg.get("gates", [])

    # 自动检测项目类型（nodejs / python），决定 checks 执行方式
    ptype = detect_project_type(project_root)
    if ptype == "unknown":
        log(f"level={args.level} status=FAIL reason=unknown-project-type (无 package.json 且无 pyproject.toml)")
        return EXIT_FAIL

    # 加载 package.json（nodejs checks 需要）
    pkg = {}
    pkg_path = project_root / "package.json"
    if pkg_path.exists():
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                pkg = json.load(f)
        except Exception:
            pkg = {}

    results = {}   # name -> status
    for c in checks:
        if ptype == "nodejs":
            results[f"check:{c}"] = run_npm_check(project_root, pkg, c, timeout)
        else:
            results[f"check:{c}"] = run_python_check(project_root, c, timeout)

    gates_yaml = pathlib.Path(args.gates_yaml)
    for g in gates:
        script = load_script_for_gate(gates_yaml, g)
        results[f"gate:{g}"] = run_gate(project_root, g, script, timeout)

    # 汇总：blocking 档位 FAIL 即整体 FAIL；SKIP 不阻断
    failed = [k for k, v in results.items() if v == "FAIL"]
    passed = [k for k, v in results.items() if v == "PASS"]
    skipped = [k for k, v in results.items() if v == "SKIP"]
    overall_fail = bool(failed)

    if args.json:
        print(json.dumps({
            "level": args.level,
            "config": str(pathlib.Path(args.config)),
            "results": results,
            "summary": {"pass": len(passed), "fail": len(failed), "skip": len(skipped)},
            "exit_code": EXIT_FAIL if overall_fail else EXIT_OK,
        }, ensure_ascii=False, indent=2))
    else:
        log(f"level={args.level} summary pass={len(passed)} fail={len(failed)} skip={len(skipped)}")

    return EXIT_FAIL if overall_fail else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())