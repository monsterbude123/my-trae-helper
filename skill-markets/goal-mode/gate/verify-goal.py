#!/usr/bin/env python3 -E
"""
Goal-Mode 强门禁外部验证器

Agent 无法编辑此文件（受 .husky/CODEOWNERS 保护）。
只读真实产物，不读 run_state，不读 Agent 声明。

状态机：
  in_progress -> candidate_complete -> [本脚本] -> complete / blocked

使用：
  python gate/verify-goal.py --manifest gate/acceptance_manifest.yaml --candidate state/completion_candidate.yaml

安全不变量：
  1. gate/manifest/inventory 受保护（Agent 不可编辑）
  2. 验证器只读真实产物
  3. 未知项 fail-closed
  4. 唯一完成信号（gate verdict）
  5. 产物内容是敌对数据
  6. python3 -E 禁止环境注入

参考：
  - https://github.com/zhjai/agent-completion-gate
  - https://github.com/momomuchu/make-no-mistakes
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


def parse_args():
    parser = argparse.ArgumentParser(description="Goal-Mode 强门禁外部验证器")
    parser.add_argument("--manifest", required=True, help="验收清单 YAML 文件路径")
    parser.add_argument("--candidate", required=True, help="候选状态 YAML 文件路径")
    parser.add_argument("--repo", default=".", help="仓库根目录")
    parser.add_argument("--strict-surfaces", action="store_true", help="严格模式：未知 surface = blocked")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    return parser.parse_args()


def load_yaml(path: str) -> dict:
    if yaml:
        return yaml.safe_load(open(path, encoding="utf-8"))
    else:
        import json
        content = open(path, encoding="utf-8").read()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print(f"ERROR: 需要 PyYAML 来解析 YAML 文件: {path}", file=sys.stderr)
            sys.exit(2)


def check_file_exists(repo: str, artifact: str) -> tuple[bool, str]:
    path = Path(repo) / artifact
    if path.exists():
        return True, f"文件存在: {artifact}"
    return False, f"文件不存在: {artifact}"


def check_file_contains(repo: str, artifact: str, substring: str) -> tuple[bool, str]:
    path = Path(repo) / artifact
    if not path.exists():
        return False, f"文件不存在: {artifact}"
    content = path.read_text(encoding="utf-8", errors="ignore")
    if substring in content:
        return True, f"包含目标字符串: {substring}"
    return False, f"不包含目标字符串: {substring}"


def check_command_exit_zero(repo: str, command: str) -> tuple[bool, str]:
    result = subprocess.run(
        command,
        shell=True,
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode == 0:
        return True, f"命令成功: {command}"
    return False, f"命令失败 ({result.returncode}): {command}\n{result.stderr}"


def check_min_series_points(repo: str, artifact: str, series: str, min_points: int) -> tuple[bool, str]:
    path = Path(repo) / artifact
    if not path.exists():
        return False, f"文件不存在: {artifact}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        points = len(data.get(series, []))
        if points >= min_points:
            return True, f"数据点数 {points} >= {min_points}"
        return False, f"数据点数 {points} < {min_points}"
    except Exception as e:
        return False, f"解析失败: {e}"


def run_check(repo: str, check: dict) -> tuple[bool, str, dict]:
    check_type = check.get("type")
    check_id = check.get("id", "unknown")
    
    if check_type == "file_exists":
        artifact = check.get("path") or check.get("artifact")
        passed, evidence = check_file_exists(repo, artifact)
    elif check_type == "file_contains":
        artifact = check.get("path") or check.get("artifact")
        substring = check.get("substring")
        passed, evidence = check_file_contains(repo, artifact, substring)
    elif check_type == "command_exit_zero":
        command = check.get("command")
        passed, evidence = check_command_exit_zero(repo, command)
    elif check_type == "min_series_points":
        artifact = check.get("path") or check.get("artifact")
        series = check.get("series")
        min_points = check.get("min_points", 2)
        passed, evidence = check_min_series_points(repo, artifact, series, min_points)
    else:
        passed = False
        evidence = f"未知检查类型: {check_type}"
    
    result = {
        "id": check_id,
        "type": check_type,
        "passed": passed,
        "evidence": evidence,
    }
    return passed, evidence, result


def main():
    args = parse_args()
    
    manifest = load_yaml(args.manifest)
    candidate = load_yaml(args.candidate)
    
    status = candidate.get("status", "unknown")
    
    if status != "candidate_complete":
        verdict = {
            "status": "blocked",
            "reason": f"Agent 状态不是 candidate_complete，而是: {status}",
            "checks": [],
        }
        print(f"BLOCKED: Agent 未提议 candidate_complete (当前: {status})")
        if args.json:
            print(json.dumps(verdict, indent=2))
        sys.exit(1)
    
    goal = manifest.get("goal", "unknown goal")
    checks = manifest.get("checks", [])
    surfaces = manifest.get("surfaces", [])
    
    if not checks:
        verdict = {
            "status": "blocked",
            "reason": "验收清单无检查项",
            "checks": [],
        }
        print("BLOCKED: 验收清单无检查项")
        if args.json:
            print(json.dumps(verdict, indent=2))
        sys.exit(1)
    
    print(f"验证目标: {goal}")
    print(f"检查项数: {len(checks)}")
    print("-" * 50)
    
    all_passed = True
    results = []
    failures = []
    
    for check in checks:
        passed, evidence, result = run_check(args.repo, check)
        results.append(result)
        
        status_icon = "PASS" if passed else "FAIL"
        print(f"[{status_icon}] {check.get('id')}: {evidence}")
        
        if not passed:
            all_passed = False
            failures.append(check.get("id"))
    
    print("-" * 50)
    
    if all_passed:
        candidate["status"] = "complete"
        candidate["verdict"] = {
            "status": "complete",
            "passed_checks": len(results),
            "total_checks": len(results),
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
        
        if yaml:
            yaml.dump(candidate, open(args.candidate, "w", encoding="utf-8"))
        else:
            import json
            json.dump(candidate, open(args.candidate, "w", encoding="utf-8"), indent=2)
        
        print("COMPLETE-OK")
        if args.json:
            print(json.dumps(candidate.get("verdict"), indent=2))
        sys.exit(0)
    else:
        print(f"BLOCKED: {len(failures)} 项未通过: {', '.join(failures)}")
        if args.json:
            verdict = {
                "status": "blocked",
                "failures": failures,
                "checks": results,
            }
            print(json.dumps(verdict, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()