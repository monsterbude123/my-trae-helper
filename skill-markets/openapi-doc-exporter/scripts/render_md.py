#!/usr/bin/env python3
"""render_md.py — 将 openapi.json 渲染为可读 Markdown 文档。

支持两种模式：
    single  — 所有接口汇总到单个 md 文件
    split   — 按路由前缀拆分为多个 md 文件 + 一个总览 README

用法：
    # 一体导出
    python render_md.py --input openapi.json --output api.md --mode single

    # 分模块导出
    python render_md.py --input openapi.json --output-dir docs/api/ \
        --mode split --prefix-map prefix-map.yaml

依赖：
    - Python 3.8+ 标准库
    - PyYAML（可选，用于 YAML 格式的 prefix-map；不可用时降级支持 JSON）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date
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

VALID_METHODS = ("get", "post", "put", "delete", "patch", "head", "options")
DEFAULT_TITLE = "API 协议 Spec"


# ────────────────────────── YAML 加载（带降级） ──────────────────────────

def load_prefix_map(path: Path) -> list[dict[str, Any]]:
    """加载 prefix-map 配置。YAML 优先，PyYAML 不可用时尝试 JSON。"""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".json",):
        return json.loads(text)
    # 尝试 YAML
    try:
        import yaml  # type: ignore
    except ImportError:
        # 降级：尝试当 JSON 解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print(
                f"ERROR 无法解析 {path}：PyYAML 未安装且文件不是有效 JSON",
                file=sys.stderr,
            )
            sys.exit(2)
    return yaml.safe_load(text)


# ────────────────────────── $ref 解析 ──────────────────────────

def resolve_ref(ref: str, spec: dict[str, Any]) -> Any | None:
    """解析 $ref，仅支持内部引用（#/...）。"""
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return None
    parts = ref.lstrip("#/").split("/")
    node: Any = spec
    for p in parts:
        if not isinstance(node, dict) or p not in node:
            return None
        node = node[p]
    return node


def ref_name(ref: str) -> str:
    """从 $ref 提取 schema 名（最后一段）。"""
    if not isinstance(ref, str):
        return ""
    return ref.rsplit("/", 1)[-1]


def deref(node: Any, spec: dict[str, Any], depth: int = 0) -> Any:
    """解引用 $ref（最多 10 层防循环）。"""
    if depth > 10:
        return node
    if isinstance(node, dict) and "$ref" in node:
        target = resolve_ref(node["$ref"], spec)
        if target is None:
            return node
        return deref(target, spec, depth + 1)
    return node


# ────────────────────────── 类型渲染 ──────────────────────────

def render_type(tdef: Any, spec: dict[str, Any] | None = None) -> str:
    """渲染 schema 为类型字符串。"""
    if not tdef:
        return "any"
    if not isinstance(tdef, dict):
        return "any"
    if "$ref" in tdef:
        return ref_name(tdef["$ref"])
    spec = spec or {}
    # allOf / anyOf / oneOf
    for combinator in ("allOf", "anyOf", "oneOf"):
        if combinator in tdef:
            variants = tdef[combinator]
            if isinstance(variants, list):
                parts = [render_type(deref(v, spec), spec) for v in variants]
                sep = " & " if combinator == "allOf" else " | "
                return sep.join(p for p in parts if p)
    t = tdef.get("type")
    if t == "array":
        items = tdef.get("items", {})
        return f"array<{render_type(deref(items, spec), spec)}>"
    if t == "object":
        return "object"
    if "enum" in tdef and tdef["enum"]:
        return f"enum({','.join(str(e) for e in tdef['enum'])})"
    if t:
        return t
    return "any"


# ────────────────────────── 字段表格 ──────────────────────────

def render_schema_field_table(schema_def: dict[str, Any], spec: dict[str, Any], indent: str = "") -> str:
    """渲染 schema 的字段表格。"""
    schema_def = deref(schema_def, spec)
    if not isinstance(schema_def, dict):
        return ""
    props = schema_def.get("properties", {})
    if not props:
        return ""
    required = set(schema_def.get("required", []))
    lines = [
        f"{indent}| 字段 | 类型 | 必填 | 说明 |",
        f"{indent}|------|------|------|------|",
    ]
    for fname, fdef in props.items():
        ftype = render_type(fdef, spec)
        req = "是" if fname in required else "否"
        desc = (fdef.get("description") or fdef.get("title") or "").replace("\n", " ").strip()
        if fdef.get("default") is not None:
            desc += f" (默认: `{fdef['default']}`)"
        lines.append(f"{indent}| {fname} | {ftype} | {req} | {desc} |")
    return "\n".join(lines)


def render_params_table(op: dict[str, Any], location: str, spec: dict[str, Any]) -> str:
    """渲染 path/query/header/cookie 参数表格。"""
    params = []
    for p in op.get("parameters", []):
        p = deref(p, spec)
        if p.get("in") == location:
            params.append(p)
    if not params:
        return ""
    lines = ["| 字段 | 类型 | 必填 | 说明 |", "|------|------|------|------|"]
    for p in params:
        sch = p.get("schema", {}) or {}
        ptype = render_type(sch, spec)
        req = "是" if p.get("required") else "否"
        desc = (p.get("description") or "").replace("\n", " ").strip()
        lines.append(f"| {p['name']} | {ptype} | {req} | {desc} |")
    return "\n".join(lines)


# ────────────────────────── Schema 示例 ──────────────────────────

def render_schema_example(schema_def: Any, spec: dict[str, Any], depth: int = 0) -> str:
    """根据 schema 生成示例 JSON 字符串。"""
    if depth > 5:
        return "{}"
    schema_def = deref(schema_def, spec)
    if not isinstance(schema_def, dict):
        return "null"
    # 优先用 example
    if "example" in schema_def:
        return json.dumps(schema_def["example"], ensure_ascii=False, indent=2)
    t = schema_def.get("type")
    if t == "object":
        props = schema_def.get("properties", {})
        if not props:
            return "{}"
        example: dict[str, Any] = {}
        for fname, fdef in props.items():
            example[fname] = _example_value(deref(fdef, spec), spec, depth + 1)
        return json.dumps(example, ensure_ascii=False, indent=2)
    if t == "array":
        items = schema_def.get("items", {})
        items = deref(items, spec)
        return json.dumps([_example_value(items, spec, depth + 1)], ensure_ascii=False, indent=2)
    return json.dumps(_example_value(schema_def, spec, depth), ensure_ascii=False)


def _example_value(schema_def: Any, spec: dict[str, Any], depth: int) -> Any:
    if depth > 5:
        return None
    schema_def = deref(schema_def, spec)
    if not isinstance(schema_def, dict):
        return None
    if "example" in schema_def:
        return schema_def["example"]
    if "default" in schema_def:
        return schema_def["default"]
    if "enum" in schema_def and schema_def["enum"]:
        return schema_def["enum"][0]
    t = schema_def.get("type")
    if t == "string":
        return "string"
    if t == "integer":
        return 0
    if t == "number":
        return 0
    if t == "boolean":
        return True
    if t == "object":
        props = schema_def.get("properties", {})
        return {fname: _example_value(deref(fdef, spec), spec, depth + 1) for fname, fdef in props.items()}
    if t == "array":
        return [_example_value(deref(schema_def.get("items", {}), spec), spec, depth + 1)]
    return None


# ────────────────────────── 请求/响应渲染 ──────────────────────────

def render_request_body(op: dict[str, Any], spec: dict[str, Any]) -> str:
    """渲染请求体。"""
    rb = deref(op.get("requestBody"), spec)
    if not rb:
        return ""
    content = rb.get("content", {})
    if not content:
        return ""
    parts = ["**请求**："]
    for ct, ct_def in content.items():
        parts.append(f"- Content-Type: `{ct}`")
        schema = ct_def.get("schema", {})
        schema = deref(schema, spec)
        if isinstance(schema, dict) and "$ref" in op.get("requestBody", {}).get("content", {}).get(ct, {}).get("schema", {}):
            # 保留原始 $ref 名
            name = ref_name(op["requestBody"]["content"][ct]["schema"]["$ref"])
            parts.append(f"- Body Schema: `{name}`（见附录）")
        elif isinstance(schema, dict) and schema.get("type") == "object" and schema.get("properties"):
            parts.append("- Body 字段：")
            parts.append("")
            parts.append(render_schema_field_table(schema, spec, "  "))
            parts.append("")
            parts.append("- Body 示例：")
            parts.append(f"  ```json")
            for line in render_schema_example(schema, spec).split("\n"):
                parts.append(f"  {line}")
            parts.append("  ```")
        elif isinstance(schema, dict) and schema.get("type") == "array":
            items_type = render_type(schema.get("items", {}), spec)
            parts.append(f"- Body: `array<{items_type}>`")
        else:
            parts.append(f"- Body: `{render_type(schema, spec)}`")
    return "\n".join(parts)


def render_responses(op: dict[str, Any], spec: dict[str, Any]) -> str:
    """渲染响应。返回文本（SSE/WS 检测在 render_op 中统一做）。"""
    responses = op.get("responses", {})
    if not responses:
        return ""
    parts = ["**响应**："]
    for code, resp in responses.items():
        resp = deref(resp, spec)
        desc = resp.get("description", "")
        parts.append(f"- `{code}` {desc}")
        content = resp.get("content", {})
        for ct, ct_def in content.items():
            parts.append(f"  - Content-Type: `{ct}`")
            schema = ct_def.get("schema", {})
            if isinstance(schema, dict) and "$ref" in schema:
                name = ref_name(schema["$ref"])
                parts.append(f"  - Schema: `{name}`（见附录）")
            else:
                schema_deref = deref(schema, spec)
                if isinstance(schema_deref, dict) and schema_deref.get("type") == "object" and schema_deref.get("properties"):
                    parts.append("  - Body 字段：")
                    parts.append("")
                    parts.append(render_schema_field_table(schema_deref, spec, "    "))
                    parts.append("")
                    parts.append("  - Body 示例：")
                    parts.append("  ```json")
                    for line in render_schema_example(schema_deref, spec).split("\n"):
                        parts.append(f"  {line}")
                    parts.append("  ```")
                elif isinstance(schema_deref, dict) and schema_deref.get("type") == "array":
                    items_type = render_type(schema_deref.get("items", {}), spec)
                    parts.append(f"  - Body: `array<{items_type}>`")
                else:
                    parts.append(f"  - Body: `{render_type(schema_deref, spec)}`")
    return "\n".join(parts)


# ────────────────────────── SSE / WebSocket 检测 ──────────────────────────

# SSE 启发式关键词（路径 + 描述）
_SSE_PATH_HINTS = ("/stream", "/sse", "/events")
_SSE_DESC_KEYWORDS = (
    "sse", "server-sent events", "server sent events",
    "text/event-stream", "流式", "事件流", "event-stream",
)

# WebSocket 启发式关键词
_WS_PATH_HINTS = ("/ws", "/websocket", "/socket")
_WS_DESC_KEYWORDS = (
    "websocket", "ws://", "wss://", "web socket",
    "双向通信", "双工",
)


def detect_sse_ws(path: str, op: dict[str, Any], spec: dict[str, Any]) -> tuple[bool, bool]:
    """检测端点是否为 SSE / WebSocket。

    多重启发式（任一命中即判定）：
      1. 响应 Content-Type 含 text/event-stream（最权威，但 FastAPI 不输出）
      2. 路径包含 /stream /sse /events（SSE）/ /ws /websocket（WS）
      3. summary/description 含 SSE/流式/WebSocket/ws:// 等关键词
    """
    path_lower = path.lower()
    summary = (op.get("summary") or "").lower()
    desc = (op.get("description") or "").lower()
    op_id = (op.get("operationId") or "").lower()
    text_blob = f"{summary} {desc} {op_id}"

    is_sse = False
    is_ws = False

    # 1. 从 responses 的 content-type 检测（最权威）
    for resp in op.get("responses", {}).values():
        resp = deref(resp, spec)
        if not isinstance(resp, dict):
            continue
        for ct in resp.get("content", {}).keys():
            ct_lower = ct.lower()
            if "text/event-stream" in ct_lower:
                is_sse = True
            if "websocket" in ct_lower:
                is_ws = True

    # 2. 路径启发式
    if not is_sse:
        if any(hint in path_lower for hint in _SSE_PATH_HINTS):
            is_sse = True
    if not is_ws:
        if any(hint in path_lower for hint in _WS_PATH_HINTS):
            is_ws = True

    # 3. 描述启发式
    if not is_sse:
        if any(kw in text_blob for kw in _SSE_DESC_KEYWORDS):
            is_sse = True
    if not is_ws:
        if any(kw in text_blob for kw in _WS_DESC_KEYWORDS):
            is_ws = True

    return is_sse, is_ws


# ────────────────────────── 单个操作渲染 ──────────────────────────

def render_op(path: str, method: str, op: dict[str, Any], spec: dict[str, Any]) -> tuple[str, bool, bool]:
    """渲染单个操作。返回 (markdown, is_sse, is_ws)。"""
    lines: list[str] = []
    summary = op.get("summary", "")
    desc = op.get("description", "") or summary
    op_id = op.get("operationId", "")
    tags = op.get("tags", [])
    lines.append(f"### {method.upper()} {path}")
    lines.append("")
    lines.append(f"**概述**：{desc or '（无描述）'}")
    if tags:
        lines.append(f"**Tags**：{', '.join(tags)}")
    if op_id:
        lines.append(f"**operationId**：`{op_id}`")
    # Path 参数
    path_params = render_params_table(op, "path", spec)
    if path_params:
        lines.append("")
        lines.append("**Path 参数**：")
        lines.append("")
        lines.append(path_params)
    # Query 参数
    query_params = render_params_table(op, "query", spec)
    if query_params:
        lines.append("")
        lines.append("**Query 参数**：")
        lines.append("")
        lines.append(query_params)
    # Header 参数
    header_params = render_params_table(op, "header", spec)
    if header_params:
        lines.append("")
        lines.append("**Header 参数**：")
        lines.append("")
        lines.append(header_params)
    # 请求体
    rb = render_request_body(op, spec)
    if rb:
        lines.append("")
        lines.append(rb)
    # 响应
    resp = render_responses(op, spec)
    if resp:
        lines.append("")
        lines.append(resp)
    # SSE / WebSocket 检测（多重启发式）
    is_sse, is_ws = detect_sse_ws(path, op, spec)
    # SSE / WebSocket 标注
    if is_sse:
        lines.append("")
        lines.append("> **SSE 端点**：响应 Content-Type 为 `text/event-stream`，使用 Server-Sent Events 协议推送流式数据。")
    if is_ws:
        lines.append("")
        lines.append("> **WebSocket 端点**：使用 ws:// 或 wss:// 协议进行双向通信。")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines), is_sse, is_ws


# ────────────────────────── 前缀分组 ──────────────────────────

def match_prefix(path: str, prefix_map: list[dict[str, Any]]) -> dict[str, Any] | None:
    """最长前缀匹配。返回匹配的映射项，无匹配返回 None。"""
    best: dict[str, Any] | None = None
    best_len = -1
    for entry in prefix_map:
        prefix = entry.get("prefix", "")
        if not prefix:
            continue
        # 大小写不敏感比较（path 通常小写，但保守起见）
        if path.lower().startswith(prefix.lower()) and len(prefix) > best_len:
            best = entry
            best_len = len(prefix)
    return best


def group_ops_by_prefix(
    paths: dict[str, Any],
    spec: dict[str, Any],
    prefix_map: list[dict[str, Any]],
) -> dict[str, list[tuple[str, str, dict[str, Any]]]]:
    """按 prefix-map 分组所有操作。返回 {module: [(path, method, op), ...]}。

    module 字段直接作为 key（和输出文件名 stem）。
    若 module 已含序号前缀（如 "01-health"），文件名就是 01-health.md；
    若不含（如 "health"），则由调用方按 order 排序后输出。
    """
    groups: dict[str, list[tuple[str, str, dict[str, Any]]]] = defaultdict(list)
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, op in path_item.items():
            if method.lower() not in VALID_METHODS:
                continue
            if not isinstance(op, dict):
                continue
            matched = match_prefix(path, prefix_map)
            if matched:
                key = matched.get("module", "misc")
            else:
                key = "99-unclassified"
            groups[key].append((path, method.upper(), op))
    return groups


def sort_module_keys(groups: dict[str, list], prefix_map: list[dict[str, Any]]) -> list[str]:
    """按 prefix-map 的 order 字段排序 module key。"""
    module_to_order: dict[str, int] = {
        entry.get("module", "misc"): entry.get("order", 99)
        for entry in prefix_map
    }
    return sorted(groups.keys(), key=lambda k: (module_to_order.get(k, 99), k))


def group_ops_auto(paths: dict[str, Any]) -> dict[str, list[tuple[str, str, dict[str, Any]]]]:
    """无 prefix-map 时，按路径前缀自动分组（/api/v1/xxx 或 /api/xxx）。"""
    groups: dict[str, list[tuple[str, str, dict[str, Any]]]] = defaultdict(list)
    order_counter = 1
    prefix_to_module: dict[str, str] = {}
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        # 提取前缀：/api/v1/foo/bar → /api/v1/foo；/api/foo/bar → /api/foo
        m = re.match(r"(/api/v\d+/[^/]+|/[^/]+/[^/]+|/[^/]+)", path)
        prefix = m.group(1) if m else path
        if prefix not in prefix_to_module:
            slug = re.sub(r"[^a-zA-Z0-9]+", "-", prefix).strip("-").lower() or "root"
            prefix_to_module[prefix] = f"{order_counter:02d}-{slug}"
            order_counter += 1
        for method, op in path_item.items():
            if method.lower() not in VALID_METHODS:
                continue
            if not isinstance(op, dict):
                continue
            groups[prefix_to_module[prefix]].append((path, method.upper(), op))
    return dict(sorted(groups.items()))


# ────────────────────────── 文档头部 ──────────────────────────

def build_header(
    title: str,
    version: str,
    openapi_version: str,
    gen_date: str,
    total_ops: int,
    total_paths: int,
    total_schemas: int,
    group_stats: list[tuple[str, str, int]],
) -> str:
    """构建文档头 + 目录。"""
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"> 版本：v{version} | 生成日期：{gen_date} | OpenAPI 版本：{openapi_version}")
    lines.append(f"> 接口总数：{total_ops} | 路径数：{total_paths} | Schema 数：{total_schemas}")
    lines.append("")
    lines.append("## 目录")
    lines.append("")
    lines.append("- 第 1 章：API 概览")
    lines.append("- 第 2 章：通用约定")
    chapter_num = 3
    for module_key, module_title, op_count in group_stats:
        lines.append(f"- 第 {chapter_num} 章：{module_title}（{op_count} ops）")
        chapter_num += 1
    lines.append("- 附录：Schema 定义")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def build_overview_chapter(
    openapi_version: str,
    info: dict[str, Any],
    total_ops: int,
    total_paths: int,
    total_schemas: int,
    group_stats: list[tuple[str, str, int]],
) -> str:
    """构建第 1 章：API 概览。"""
    lines: list[str] = []
    lines.append("## 第 1 章：API 概览")
    lines.append("")
    lines.append("### 1.1 总体信息")
    lines.append("")
    lines.append("| 项目 | 值 |")
    lines.append("|------|-----|")
    lines.append(f"| OpenAPI 版本 | {openapi_version} |")
    lines.append(f"| API 标题 | {info.get('title', '(未指定)')} |")
    lines.append(f"| API 版本 | {info.get('version', '(未指定)')} |")
    desc = info.get("description", "")
    if desc:
        lines.append(f"| API 描述 | {desc.replace(chr(10), ' ').strip()[:200]} |")
    lines.append("")
    lines.append("### 1.2 接口统计")
    lines.append("")
    lines.append("| 模块 | 操作数 |")
    lines.append("|------|--------|")
    for module_key, module_title, op_count in group_stats:
        lines.append(f"| {module_title} | {op_count} |")
    lines.append(f"| **合计** | **{total_ops}** |")
    lines.append("")
    lines.append(f"**路径数**：{total_paths}")
    lines.append(f"**Schema 数**：{total_schemas}")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def build_conventions_chapter(spec: dict[str, Any], sse_endpoints: list[str], ws_endpoints: list[str]) -> str:
    """构建第 2 章：通用约定（从 openapi 推断）。"""
    lines: list[str] = []
    lines.append("## 第 2 章：通用约定")
    lines.append("")
    # 收集所有 content-type
    content_types: set[str] = set()
    for path_item in spec.get("paths", {}).values():
        if not isinstance(path_item, dict):
            continue
        for method, op in path_item.items():
            if method.lower() not in VALID_METHODS or not isinstance(op, dict):
                continue
            rb = op.get("requestBody", {})
            if isinstance(rb, dict):
                for ct in rb.get("content", {}).keys():
                    content_types.add(ct)
    lines.append("### 2.1 请求")
    lines.append("")
    if content_types:
        lines.append("**支持的 Content-Type**：")
        lines.append("")
        for ct in sorted(content_types):
            lines.append(f"- `{ct}`")
        lines.append("")
    lines.append("- 路径参数：`{param}` 形式")
    lines.append("- Query 参数：可选参数有默认值")
    lines.append("- 请求体：schema 校验失败通常返回 422")
    lines.append("")
    lines.append("### 2.2 响应")
    lines.append("")
    lines.append("- 成功：HTTP 2xx + JSON body")
    lines.append("- 错误：HTTP 4xx/5xx，body 结构由各框架决定")
    lines.append("- 错误码语义见各接口的 responses 定义")
    lines.append("")
    # SSE / WebSocket 提示
    if sse_endpoints:
        lines.append("### 2.3 流式响应（SSE）")
        lines.append("")
        lines.append("以下端点使用 Server-Sent Events 推送流式数据：")
        lines.append("")
        for ep in sse_endpoints:
            lines.append(f"- `{ep}`")
        lines.append("")
        lines.append("- Content-Type: `text/event-stream`")
        lines.append("- 响应头：`Cache-Control: no-cache`、`Connection: keep-alive`")
        lines.append("- 数据格式：`data: {JSON}\\n\\n`")
        lines.append("")
    if ws_endpoints:
        lines.append("### 2.4 WebSocket")
        lines.append("")
        lines.append("以下端点使用 WebSocket 双向通信：")
        lines.append("")
        for ep in ws_endpoints:
            lines.append(f"- `{ep}`")
        lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def build_schemas_appendix(spec: dict[str, Any]) -> str:
    """构建附录：Schema 定义。"""
    schemas = spec.get("components", {}).get("schemas", {})
    if not isinstance(schemas, dict) or not schemas:
        return ""
    lines: list[str] = []
    lines.append("## 附录：Schema 定义")
    lines.append("")
    lines.append(f"> 共 {len(schemas)} 个 schema，按字母顺序列出。")
    lines.append("")
    for schema_name in sorted(schemas.keys()):
        schema_def = schemas[schema_name]
        schema_def = deref(schema_def, spec)
        if not isinstance(schema_def, dict):
            continue
        lines.append(f"### {schema_name}")
        lines.append("")
        desc = schema_def.get("description", "")
        if desc:
            lines.append(f"**说明**：{desc}")
            lines.append("")
        table = render_schema_field_table(schema_def, spec)
        if table:
            lines.append(table)
            lines.append("")
        else:
            t = schema_def.get("type")
            if t == "string" and "enum" in schema_def:
                lines.append(f"类型：`enum({', '.join(str(e) for e in schema_def['enum'])})`")
                lines.append("")
            elif t:
                lines.append(f"类型：`{t}`")
                lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


# ────────────────────────── single 模式 ──────────────────────────

def render_single(
    spec: dict[str, Any],
    output: Path,
    title: str,
    version: str,
    prefix_map: list[dict[str, Any]] | None,
) -> None:
    """single 模式：所有内容写到一个文件。"""
    paths = spec.get("paths", {})
    schemas = spec.get("components", {}).get("schemas", {})
    info = spec.get("info", {})
    openapi_version = spec.get("openapi", "unknown")
    gen_date = date.today().isoformat()

    # 分组
    if prefix_map:
        groups = group_ops_by_prefix(paths, spec, prefix_map)
        # 构建 module → title 映射
        module_to_title: dict[str, str] = {}
        for entry in prefix_map:
            mod = entry.get("module", "misc")
            module_to_title[mod] = entry.get("title", mod)
        # 按 order 排序
        sorted_keys = sort_module_keys(groups, prefix_map)
        group_stats: list[tuple[str, str, int]] = []
        for key in sorted_keys:
            if key == "99-unclassified":
                title_str = "未分类 API"
            else:
                title_str = module_to_title.get(key, key)
            group_stats.append((key, title_str, len(groups[key])))
    else:
        groups = group_ops_auto(paths)
        group_stats = []
        for key, ops in groups.items():
            # 从 key 提取标题（去掉 NN- 前缀）
            title_str = key.split("-", 1)[-1] if "-" in key else key
            group_stats.append((key, title_str, len(ops)))

    total_ops = sum(len(ops) for ops in groups.values())
    total_paths = len(paths)
    total_schemas = len(schemas) if isinstance(schemas, dict) else 0

    # 收集 SSE / WS 端点
    sse_endpoints: list[str] = []
    ws_endpoints: list[str] = []

    # 渲染各章节
    chapter_contents: list[str] = []
    chapter_num = 3
    for module_key, module_title, op_count in group_stats:
        ops = groups.get(module_key, [])
        if not ops:
            continue
        lines: list[str] = []
        lines.append(f"## 第 {chapter_num} 章：{module_title}")
        lines.append("")
        lines.append(f"> 共 {op_count} 个操作")
        lines.append("")
        # 按 path 排序
        for path, method, op in sorted(ops, key=lambda x: (x[0], x[1])):
            md, is_sse, is_ws = render_op(path, method, op, spec)
            if is_sse:
                sse_endpoints.append(f"{method} {path}")
            if is_ws:
                ws_endpoints.append(f"{method} {path}")
            lines.append(md)
        chapter_contents.append("\n".join(lines))
        chapter_num += 1

    # 组装
    header = build_header(
        title, version, openapi_version, gen_date,
        total_ops, total_paths, total_schemas, group_stats,
    )
    overview = build_overview_chapter(
        openapi_version, info, total_ops, total_paths, total_schemas, group_stats,
    )
    conventions = build_conventions_chapter(spec, sse_endpoints, ws_endpoints)
    appendix = build_schemas_appendix(spec)

    final = header + overview + conventions + "\n".join(chapter_contents) + appendix
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(final, encoding="utf-8")

    print(f"OK single mode: {output}")
    print(f"   - 总操作数: {total_ops}")
    print(f"   - 路径数: {total_paths}")
    print(f"   - Schema 数: {total_schemas}")
    print(f"   - 模块数: {len(group_stats)}")
    print(f"   - SSE 端点: {len(sse_endpoints)}")
    print(f"   - WebSocket 端点: {len(ws_endpoints)}")


# ────────────────────────── split 模式 ──────────────────────────

def render_split(
    spec: dict[str, Any],
    output_dir: Path,
    title: str,
    version: str,
    prefix_map: list[dict[str, Any]],
) -> None:
    """split 模式：按模块拆分为多文件。"""
    paths = spec.get("paths", {})
    schemas = spec.get("components", {}).get("schemas", {})
    info = spec.get("info", {})
    openapi_version = spec.get("openapi", "unknown")
    gen_date = date.today().isoformat()

    groups = group_ops_by_prefix(paths, spec, prefix_map)

    # 模块元数据：module → title
    module_to_title: dict[str, str] = {}
    for entry in prefix_map:
        mod = entry.get("module", "misc")
        module_to_title[mod] = entry.get("title", mod)

    total_ops = sum(len(ops) for ops in groups.values())
    total_paths = len(paths)
    total_schemas = len(schemas) if isinstance(schemas, dict) else 0

    # 构建 group_stats（按 order 排序）
    sorted_keys = sort_module_keys(groups, prefix_map)
    group_stats: list[tuple[str, str, int]] = []
    for key in sorted_keys:
        if key == "99-unclassified":
            title_str = "未分类 API"
        else:
            title_str = module_to_title.get(key, key)
        group_stats.append((key, title_str, len(groups[key])))

    # 收集 SSE / WS
    sse_endpoints: list[str] = []
    ws_endpoints: list[str] = []

    # 输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 01-overview.md
    overview = build_overview_chapter(
        openapi_version, info, total_ops, total_paths, total_schemas, group_stats,
    )
    # 在 split 模式下，overview 文件单独写
    overview_lines: list[str] = []
    overview_lines.append(f"# {title} — 概览")
    overview_lines.append("")
    overview_lines.append(f"> 版本：v{version} | 生成日期：{gen_date} | OpenAPI 版本：{openapi_version}")
    overview_lines.append("")
    overview_lines.append(overview)
    (output_dir / "01-overview.md").write_text("\n".join(overview_lines), encoding="utf-8")

    # 2. 02-{module}.md 各模块文件
    written_files: list[tuple[str, str, str]] = []  # (filename, title, op_count)
    for module_key, module_title, op_count in group_stats:
        ops = groups.get(module_key, [])
        if not ops:
            continue
        # 文件名：用 module_key（已含 order 前缀）
        filename = f"{module_key}.md"
        lines: list[str] = []
        lines.append(f"# {module_title}")
        lines.append("")
        lines.append(f"> 共 {op_count} 个操作")
        lines.append("")
        for path, method, op in sorted(ops, key=lambda x: (x[0], x[1])):
            md, is_sse, is_ws = render_op(path, method, op, spec)
            if is_sse:
                sse_endpoints.append(f"{method} {path}")
            if is_ws:
                ws_endpoints.append(f"{method} {path}")
            lines.append(md)
        (output_dir / filename).write_text("\n".join(lines), encoding="utf-8")
        written_files.append((filename, module_title, str(op_count)))

    # 3. 通用约定章节合并到 overview（split 模式下作为 overview 的第 2 章）
    # 重新写 overview，加上通用约定
    conventions = build_conventions_chapter(spec, sse_endpoints, ws_endpoints)
    overview_lines = []
    overview_lines.append(f"# {title} — 概览")
    overview_lines.append("")
    overview_lines.append(f"> 版本：v{version} | 生成日期：{gen_date} | OpenAPI 版本：{openapi_version}")
    overview_lines.append("")
    overview_lines.append(overview)
    overview_lines.append(conventions)
    (output_dir / "01-overview.md").write_text("\n".join(overview_lines), encoding="utf-8")

    # 4. appendix-schemas.md
    appendix = build_schemas_appendix(spec)
    appendix_lines: list[str] = []
    appendix_lines.append(f"# {title} — Schema 定义附录")
    appendix_lines.append("")
    appendix_lines.append(appendix)
    (output_dir / "appendix-schemas.md").write_text("\n".join(appendix_lines), encoding="utf-8")

    # 5. README.md 总览
    readme_lines: list[str] = []
    readme_lines.append(f"# {title}")
    readme_lines.append("")
    readme_lines.append(f"> 版本：v{version} | 生成日期：{gen_date} | OpenAPI 版本：{openapi_version}")
    readme_lines.append(f"> 接口总数：{total_ops} | 路径数：{total_paths} | Schema 数：{total_schemas}")
    readme_lines.append("")
    readme_lines.append("## 目录")
    readme_lines.append("")
    readme_lines.append("- [概览与通用约定](01-overview.md)")
    for filename, module_title, op_count in written_files:
        readme_lines.append(f"- [{module_title} ({op_count} ops)]({filename})")
    readme_lines.append("- [Schema 定义附录](appendix-schemas.md)")
    readme_lines.append("")
    if sse_endpoints:
        readme_lines.append("## SSE 端点")
        readme_lines.append("")
        for ep in sse_endpoints:
            readme_lines.append(f"- `{ep}`")
        readme_lines.append("")
    if ws_endpoints:
        readme_lines.append("## WebSocket 端点")
        readme_lines.append("")
        for ep in ws_endpoints:
            readme_lines.append(f"- `{ep}`")
        readme_lines.append("")
    (output_dir / "README.md").write_text("\n".join(readme_lines), encoding="utf-8")

    print(f"OK split mode: {output_dir}")
    print(f"   - 总操作数: {total_ops}")
    print(f"   - 路径数: {total_paths}")
    print(f"   - Schema 数: {total_schemas}")
    print(f"   - 模块文件数: {len(written_files)}")
    print(f"   - SSE 端点: {len(sse_endpoints)}")
    print(f"   - WebSocket 端点: {len(ws_endpoints)}")
    print(f"   - 输出文件:")
    print(f"     - README.md")
    print(f"     - 01-overview.md")
    for fn, _, _ in written_files:
        print(f"     - {fn}")
    print(f"     - appendix-schemas.md")


# ────────────────────────── 主入口 ──────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="将 openapi.json 渲染为可读 Markdown 文档"
    )
    parser.add_argument("--input", required=True, help="openapi.json 路径")
    parser.add_argument("--output", help="单文件输出路径（mode=single 必填）")
    parser.add_argument("--output-dir", help="输出目录（mode=split 必填）")
    parser.add_argument("--mode", choices=["single", "split"], default="single", help="输出模式（默认 single）")
    parser.add_argument("--prefix-map", help="前缀映射 YAML/JSON（mode=split 必填，single 可选）")
    parser.add_argument("--title", default=DEFAULT_TITLE, help=f"文档总标题（默认 '{DEFAULT_TITLE}'）")
    parser.add_argument("--version", help="文档版本（默认从 openapi.json info.version 读取）")
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

    if not isinstance(spec, dict):
        print("ERROR 顶层必须是 JSON 对象", file=sys.stderr)
        return 2

    # 版本号
    version = args.version or spec.get("info", {}).get("version", "1.0")

    # 加载 prefix-map
    prefix_map: list[dict[str, Any]] | None = None
    if args.prefix_map:
        prefix_map_path = Path(args.prefix_map)
        if not prefix_map_path.exists():
            print(f"ERROR prefix-map 文件不存在: {prefix_map_path}", file=sys.stderr)
            return 2
        prefix_map = load_prefix_map(prefix_map_path)
        if not isinstance(prefix_map, list):
            print("ERROR prefix-map 必须是数组", file=sys.stderr)
            return 2

    # 模式校验
    if args.mode == "single":
        if not args.output:
            print("ERROR single 模式需要 --output 参数", file=sys.stderr)
            return 2
        render_single(spec, Path(args.output), args.title, version, prefix_map)
    else:  # split
        if not args.output_dir:
            print("ERROR split 模式需要 --output-dir 参数", file=sys.stderr)
            return 2
        if not prefix_map:
            print("ERROR split 模式需要 --prefix-map 参数", file=sys.stderr)
            return 2
        render_split(spec, Path(args.output_dir), args.title, version, prefix_map)

    return 0


if __name__ == "__main__":
    sys.exit(main())
