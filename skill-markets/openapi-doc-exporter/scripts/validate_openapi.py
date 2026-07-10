#!/usr/bin/env python3
"""validate_openapi.py — 校验 openapi.json 是否符合 OpenAPI 3.0/3.1 规范。

用法：
    python validate_openapi.py --input openapi.json

退出码：
    0 — 校验通过（可能有 warning，但无 error）
    1 — 校验失败（有 error）
    2 — 文件无法读取/解析
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Windows 控制台编码兼容（cp1252 无法 print 中文）
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        # Python < 3.7 不支持 reconfigure，降级替换中文
        pass


VALID_METHODS = {"get", "post", "put", "delete", "patch", "head", "options"}
REQUIRED_TOP_FIELDS = ["openapi", "info", "paths"]
REQUIRED_INFO_FIELDS = ["title", "version"]


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warning(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


def _resolve_ref(ref: str, spec: dict[str, Any]) -> Any | None:
    """解析 $ref，仅支持内部引用（#/...）。"""
    if not ref.startswith("#/"):
        return None
    parts = ref.lstrip("#/").split("/")
    node: Any = spec
    for p in parts:
        if not isinstance(node, dict) or p not in node:
            return None
        node = node[p]
    return node


def _collect_refs(node: Any, spec: dict[str, Any], report: Report, path: str = "") -> int:
    """递归收集并校验所有 $ref。返回引用总数。"""
    count = 0
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "$ref" and isinstance(v, str):
                count += 1
                target = _resolve_ref(v, spec)
                if target is None:
                    report.error(f"{path}: $ref '{v}' 无法解析")
            else:
                count += _collect_refs(v, spec, report, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            count += _collect_refs(item, spec, report, f"{path}[{i}]")
    return count


def validate(spec: dict[str, Any]) -> Report:
    report = Report()

    # 1. 顶层必填字段
    for field in REQUIRED_TOP_FIELDS:
        if field not in spec:
            report.error(f"缺少顶层必填字段: '{field}'")

    # 2. info 必填字段
    info = spec.get("info", {})
    if not isinstance(info, dict):
        report.error("info 必须是对象")
    else:
        for f in REQUIRED_INFO_FIELDS:
            if f not in info:
                report.error(f"info.{f} 必填")

    # 3. openapi 版本
    openapi_ver = spec.get("openapi", "")
    if openapi_ver:
        if not (openapi_ver.startswith("3.0") or openapi_ver.startswith("3.1")):
            report.warning(f"未测试的 OpenAPI 版本: {openapi_ver}（本工具仅测试 3.0/3.1）")

    # 4. paths 校验
    paths = spec.get("paths", {})
    if not isinstance(paths, dict):
        report.error("paths 必须是对象")
        paths = {}

    path_count = 0
    op_count = 0
    for path, path_item in paths.items():
        path_count += 1
        if not path.startswith("/"):
            report.warning(f"paths.{path}: 路径应以 '/' 开头")
        if not isinstance(path_item, dict):
            report.error(f"paths.{path}: 必须是对象")
            continue
        for method, op in path_item.items():
            if method.startswith("x-"):
                continue  # 扩展字段跳过
            if method.lower() not in VALID_METHODS:
                report.warning(f"paths.{path}.{method}: 非标准 HTTP method")
                continue
            op_count += 1
            if not isinstance(op, dict):
                report.error(f"paths.{path}.{method}: 操作必须是对象")
                continue
            # 5. 每个操作必须有 responses
            if "responses" not in op:
                report.error(f"paths.{path}.{method}: 缺少 responses 字段")
            else:
                responses = op["responses"]
                if not isinstance(responses, dict) or not responses:
                    report.error(f"paths.{path}.{method}: responses 不能为空")
            # 6. parameters 基本校验
            params = op.get("parameters", [])
            if params is not None and not isinstance(params, list):
                report.error(f"paths.{path}.{method}: parameters 必须是数组")

    # 7. $ref 解析校验
    ref_count = _collect_refs(spec, spec, report)

    # 8. components.schemas 数量统计
    schemas = spec.get("components", {}).get("schemas", {})
    if schemas is not None and not isinstance(schemas, dict):
        report.warning("components.schemas 应为对象")
        schemas = {}

    # 输出
    _print_report(report, openapi_ver, path_count, op_count, len(schemas), ref_count)
    return report


def _print_report(
    report: Report,
    openapi_ver: str,
    path_count: int,
    op_count: int,
    schema_count: int,
    ref_count: int,
) -> None:
    if report.ok:
        print("OK openapi.json 格式有效")
        print(f"   - 版本: {openapi_ver or '(未指定)'}")
        print(f"   - 路径数: {path_count}")
        print(f"   - 操作数: {op_count}")
        print(f"   - Schema 数: {schema_count}")
        print(f"   - $ref 总数: {ref_count}")
        print(f"   - 错误: 0")
        print(f"   - 警告: {len(report.warnings)}")
        if report.warnings:
            print("   - 警告详情:")
            for w in report.warnings:
                print(f"     * {w}")
    else:
        print(f"FAIL 发现 {len(report.errors)} 个错误:")
        for i, e in enumerate(report.errors, 1):
            print(f"  {i}. {e}")
        if report.warnings:
            print(f"\n还有 {len(report.warnings)} 个警告:")
            for w in report.warnings:
                print(f"  * {w}")
        print(f"\n统计: 路径 {path_count} | 操作 {op_count} | Schema {schema_count} | $ref {ref_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="校验 openapi.json 是否符合 OpenAPI 3.0/3.1 规范"
    )
    parser.add_argument("--input", required=True, help="openapi.json 路径")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR 文件不存在: {input_path}", file=sys.stderr)
        return 2

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR JSON 解析失败: {e}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"ERROR 文件读取失败: {e}", file=sys.stderr)
        return 2

    if not isinstance(spec, dict):
        print("ERROR 顶层必须是 JSON 对象", file=sys.stderr)
        return 2

    report = validate(spec)
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
