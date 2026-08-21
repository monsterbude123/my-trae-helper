#!/usr/bin/env python3
"""
ai-testmate OpenAPI → test-cases.yaml 提取器
- 读 openapi.json / yaml
- 遍历 paths × methods
- 每 op 生成 1 正例 + 1 负例
- 输出 yaml(可由 api-tester 加载)
"""

import argparse
import json
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    print("[FATAL] PyYAML 未装,跑:pip install --user pyyaml", file=sys.stderr)
    sys.exit(2)


METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}

# tags → priority 映射
TAG_PRIORITY = {
    "core": "P0",
    "critical": "P0",
    "admin": "P2",
    "internal": "P2",
}


def to_kebab(s: str) -> str:
    """operationId → kebab-case"""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s)
    return s.lower().replace("_", "-")


def infer_priority(operation: dict, path: str) -> str:
    tags = operation.get("tags", [])
    if tags:
        return TAG_PRIORITY.get(tags[0].lower(), "P1")
    # 启发式:含 /admin 路径 → P2,其他 P1
    if "/admin" in path:
        return "P2"
    return "P1"


def parse_params(operation: dict) -> tuple:
    """分离 path_params / query_params,返回 (path_params, query_params)"""
    path_params = {}
    query_params = {}
    for p in operation.get("parameters", []):
        if p.get("in") == "path":
            path_params[p["name"]] = "<fill>"
        elif p.get("in") == "query":
            query_params[p["name"]] = "<fill>"
    return path_params, query_params


def pick_expected_status(responses: dict) -> int:
    """从 responses 选主要期望状态码(优先 200/201/204)"""
    if not responses:
        return 200
    for code in ("200", "201", "204"):
        if code in responses:
            return int(code)
    # 取第一个数字状态
    for code in responses:
        if code.isdigit():
            return int(code)
    return 200


def pick_negative_status(responses: dict) -> int:
    """从 responses 选 4xx 负例状态码"""
    for code in sorted(responses.keys()):
        if code.startswith("4"):
            try:
                return int(code)
            except ValueError:
                pass
    return 404  # 默认


def is_security_required(operation: dict, spec: dict) -> bool:
    """检测 operation 是否需要鉴权(V2-AP-1 防止)"""
    if "security" in operation:
        return bool(operation["security"])
    # 检查全局 security
    return bool(spec.get("security"))


def build_test_case(op_id: str, method: str, path: str, operation: dict, spec: dict, idx: int) -> dict:
    """构建单条 test-cases.yaml 用例"""
    responses = operation.get("responses", {})
    expected_status = pick_expected_status(responses)
    negative_status = pick_negative_status(responses)
    path_params, query_params = parse_params(operation)
    priority = infer_priority(operation, path)
    auth_required = is_security_required(operation, spec)

    preconditions = []
    if auth_required:
        preconditions.append("需 auth(bearer)")
    if operation.get("requestBody", {}).get("required"):
        preconditions.append("需提供 requestBody")

    return {
        "id": f"TC-API-{to_kebab(op_id)}" if op_id else f"TC-API-{idx:03d}",
        "story_ref": None,
        "name": op_id or f"{method.upper()} {path}",
        "type": "api",
        "priority": priority,
        "source": "openapi",
        "preconditions": preconditions,
        "steps": [
            f"{method.upper()} {path} 传有效参数(期望 {expected_status})",
            f"{method.upper()} {path} 传非法参数(期望 {negative_status})",
        ],
        "expected": [
            f"HTTP {expected_status}",
            f"HTTP {negative_status}",
        ],
        "data": {
            "method": method.upper(),
            "url": path,
            "path_params": path_params or None,
            "query_params": query_params or None,
            "expected_status": expected_status,
            "negative_cases": [
                {"url": path, "expected_status": negative_status}
            ] if expected_status < 400 else None,
            "auth_required": auth_required,
        },
    }


def extract(input_path: pathlib.Path, mode: str = "auto") -> list:
    """主入口:读 openapi → 返回 test-cases 列表"""
    text = input_path.read_text(encoding="utf-8")
    if input_path.suffix in (".yaml", ".yml"):
        spec = yaml.safe_load(text)
    else:
        spec = json.loads(text)

    cases = []
    idx = 0
    paths = spec.get("paths", {})
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            if method.lower() not in METHODS or not isinstance(operation, dict):
                continue
            idx += 1
            op_id = operation.get("operationId") or f"{method}-{path}"
            case = build_test_case(op_id, method, path, operation, spec, idx)
            if mode == "full":
                # 全状态码穷举(可选,默认不开)
                for code in operation.get("responses", {}):
                    if code.isdigit() and int(code) != case["data"]["expected_status"]:
                        case["steps"].append(f"{method.upper()} {path} 期望 {code}")
                        case["expected"].append(f"HTTP {code}")
            cases.append(case)

    return cases


def to_yaml(cases: list) -> str:
    """test-cases 列表 → yaml 字符串"""
    return yaml.safe_dump({"test_cases": cases}, allow_unicode=True, sort_keys=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="openapi.json/yaml 路径")
    parser.add_argument("--output", help="输出 yaml 路径(默认 stdout)")
    parser.add_argument("--mode", default="auto", choices=["auto", "full"])
    args = parser.parse_args()

    input_path = pathlib.Path(args.input)
    if not input_path.exists():
        print(f"[FATAL] openapi 文件不存在:{input_path}", file=sys.stderr)
        return 2

    cases = extract(input_path, mode=args.mode)
    yaml_text = to_yaml(cases)

    if args.output:
        out = pathlib.Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(yaml_text, encoding="utf-8")
        print(f"[INFO] 生成 {len(cases)} 条用例 → {out}", file=sys.stderr)
    else:
        print(yaml_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())