"""catalogs/_loader.py — 共用 catalog 加载辅助

设计原则(§1.7 ponytail):
  - 唯一一处 yaml 加载路径,集中错误处理
  - 路径解析全部相对 SKILL_ROOT 解析
  - 失败抛 ValueError 而非裸 yaml 报错,便于 trap 测试断言
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

# tests/catalogs/_loader.py → SKILL_ROOT = ../../../
SKILL_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CATALOG_PATH = SKILL_ROOT / "tests" / "catalogs" / "skill-catalog.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    """读 YAML 并返回 dict(空文件返回 {} 而非 None)。"""
    if not path.is_file():
        raise FileNotFoundError(f"catalog YAML 不存在:{path}")
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: YAML 顶层必须是 dict,实际 {type(data).__name__}")
    return data


def load_catalog(catalog_path: Path | None = None) -> dict[str, Any]:
    """加载 catalog 并对 top-level key 做基本校验。"""
    path = catalog_path or DEFAULT_CATALOG_PATH
    data = load_yaml(path)
    # 必含字段
    for key in ("version",):
        if key not in data:
            raise ValueError(f"{path}: catalog 缺顶层字段 {key!r}")
    return data


def resolve_relative(path_str: str) -> Path:
    """path_str 是相对 SKILL_ROOT 的相对路径,转成绝对。"""
    return (SKILL_ROOT / path_str).resolve(strict=False)


def dotted_path_exists(data: Any, dotted_path: str) -> bool:
    """检查 yaml 里 dotted path 存在。

    支持通配 `[*]`:
      - "stacks[*].id" → 至少一个 stack 有 id
      - "stacks[*].scaffold.tags[*]" → 嵌套通配

    规则:
      - 普通 key 必须存在且非 None
      - 通配段 `[*]` 在嵌套结构里:对每个 list item 都递归尝试,**至少** 一个通过
      - 叶子节点非 None 即视为存在(允许 0/False/"" 通过;缺 key 不通过)
    """
    if not dotted_path:
        return False
    parts = dotted_path.split(".")
    return _walk(data, parts)


def _walk(node: Any, parts: list[str]) -> bool:
    if not parts:
        # 走到底:非 None 即视为存在
        return node is not None
    head, *rest = parts
    if head.endswith("[*]"):
        # `[*]` 嵌在 key 名里(例如 stacks[*])
        # 先按 key=head[:-3] 取子节点,再对 list 的每个 item 走剩余 parts
        key = head[:-3]
        if not isinstance(node, dict) or key not in node:
            return False
        children = node[key]
        if not isinstance(children, list):
            return False
        if not rest:
            return len(children) > 0
        return any(_walk(item, rest) for item in children)
    if not isinstance(node, dict):
        return False
    if head not in node or node[head] is None:
        return False
    return _walk(node[head], rest)


def regex_find(text: str, pattern: str, flags: int = re.MULTILINE) -> bool:
    return re.search(pattern, text, flags) is not None


# 自举用常量,便于 trap 用例直接引用
CATALOG_REQUIRED_SECTIONS_MIN = 3
CATALOG_REQUIRED_DOCS_MIN = 2


if __name__ == "__main__":  # pragma: no cover
    try:
        c = load_catalog()
        print(f"✅ catalog v{c.get('version')} loaded")
        for k in ("required_docs", "required_scripts", "required_sections", "required_schema_fields"):
            n = len(c.get(k, []))
            print(f"  {k}: {n} entries")
    except Exception as e:
        print(f"🛑 catalog load failed: {e}", file=sys.stderr)
        sys.exit(1)
