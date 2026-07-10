#!/usr/bin/env python3
"""split_by_prefix.py — 按章节/前缀拆分已渲染的 markdown 文件为多文件。

可单独使用，也可被 render_md.py 内部逻辑参考。两种拆分策略：
    1. 有 --prefix-map：按前缀映射的章节标题（## 第 N 章：xxx）拆分
    2. 无 --prefix-map：按 ## 二级标题拆分

用法：
    # 按前缀映射拆分
    python split_by_prefix.py --input api.md --output-dir docs/api/ \
        --prefix-map prefix-map.yaml

    # 按二级标题自动拆分
    python split_by_prefix.py --input api.md --output-dir docs/api/

依赖：
    - Python 3.8+ 标准库
    - PyYAML（可选，YAML 格式 prefix-map 必需）
"""
from __future__ import annotations

import argparse
import json
import re
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


def load_prefix_map(path: Path) -> list[dict[str, Any]]:
    """加载 prefix-map 配置。"""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore
    except ImportError:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print(
                f"ERROR 无法解析 {path}：PyYAML 未安装且文件不是有效 JSON",
                file=sys.stderr,
            )
            sys.exit(2)
    return yaml.safe_load(text)


# ────────────────────────── Markdown 拆分 ──────────────────────────

CHAPTER_PATTERN = re.compile(r"^## (.+)$", re.MULTILINE)
APPENDIX_PATTERN = re.compile(r"^## 附录[:：](.*)$", re.MULTILINE)
CHAPTER_NUM_PATTERN = re.compile(r"^## 第\s*(\d+)\s*章[:：]\s*(.+)$", re.MULTILINE)


def split_by_h2(content: str) -> list[tuple[str, str]]:
    """按 ## 二级标题拆分。返回 [(title, body), ...]。

    第一个元素是标题前的前言（title 为空字符串）。
    """
    sections: list[tuple[str, str]] = []
    matches = list(CHAPTER_PATTERN.finditer(content))
    if not matches:
        return [("", content)]

    # 前言
    if matches[0].start() > 0:
        preface = content[: matches[0].start()].rstrip()
        if preface:
            sections.append(("", preface))

    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[start:end].rstrip() + "\n"
        sections.append((title, body))
    return sections


def slugify(title: str) -> str:
    """把章节标题转为文件名 slug。"""
    # 移除"第 N 章："前缀
    title = re.sub(r"^第\s*\d+\s*章[:：]\s*", "", title)
    # 移除"附录："前缀
    title = re.sub(r"^附录[:：]\s*", "appendix-", title)
    # 非字母数字转 -
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", title).strip("-").lower()
    # 中文段保留但不适合做文件名，进一步转写
    slug = re.sub(r"[\u4e00-\u9fff]+", "", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "section"


def split_with_prefix_map(
    content: str,
    prefix_map: list[dict[str, Any]],
) -> list[tuple[str, str, str]]:
    """按 prefix-map 拆分。返回 [(filename, title, body), ...]。

    匹配规则：在 ## 标题中查找 prefix-map 的 title，匹配则归到对应 module。
    """
    sections = split_by_h2(content)
    result: list[tuple[str, str, str]] = []

    # 构建 title → module 映射
    title_to_module: dict[str, tuple[str, int]] = {}
    for entry in prefix_map:
        t = entry.get("title", "")
        m = entry.get("module", "misc")
        order = entry.get("order", 99)
        if t:
            title_to_module[t] = (m, order)

    # 处理每个 section
    used_orders: set[int] = set()
    for title, body in sections:
        if not title:
            # 前言，跳过
            continue
        # 检查是否是"第 1 章"/"第 2 章"等概览章节
        ch_match = CHAPTER_NUM_PATTERN.match(f"## {title}")
        ch_num = int(ch_match.group(1)) if ch_match else None
        if ch_num is not None and ch_num <= 2:
            # 概览章节 → 01-overview.md
            filename = "01-overview.md"
            result.append((filename, title, body))
            continue
        # 检查是否是附录
        if title.startswith("附录"):
            filename = "appendix-schemas.md"
            result.append((filename, title, body))
            continue
        # 在 title 中查找匹配的 module
        matched_module: str | None = None
        matched_order: int = 99
        for map_title, (mod, order) in title_to_module.items():
            if map_title in title:
                if order < matched_order or matched_module is None:
                    matched_module = mod
                    matched_order = order
        if matched_module is not None:
            filename = f"{matched_order:02d}-{matched_module}.md"
            used_orders.add(matched_order)
        else:
            filename = "99-unclassified.md"
        result.append((filename, title, body))

    return result


def split_auto(content: str) -> list[tuple[str, str, str]]:
    """无 prefix-map 时，按 ## 标题自动拆分。"""
    sections = split_by_h2(content)
    result: list[tuple[str, str, str]] = []
    order_counter = 1
    for title, body in sections:
        if not title:
            continue
        # 概览章节特殊处理
        ch_match = CHAPTER_NUM_PATTERN.match(f"## {title}")
        ch_num = int(ch_match.group(1)) if ch_match else None
        if ch_num is not None and ch_num <= 2:
            filename = "01-overview.md"
        elif title.startswith("附录"):
            filename = "appendix-schemas.md"
        else:
            slug = slugify(title)
            filename = f"{order_counter:02d}-{slug}.md"
            order_counter += 1
        result.append((filename, title, body))
    return result


# ────────────────────────── README 生成 ──────────────────────────

def build_readme(
    title: str,
    files: list[tuple[str, str, str]],
    preface: str,
) -> str:
    """生成 README.md。"""
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    if preface:
        # 提取 preface 中的版本/日期信息
        for line in preface.split("\n"):
            if line.startswith(">"):
                lines.append(line)
        lines.append("")
    lines.append("## 目录")
    lines.append("")
    # 合并同名文件（同一 module 可能有多个章节）
    seen: dict[str, tuple[str, str]] = {}
    order: list[str] = []
    for filename, section_title, _ in files:
        if filename in seen:
            # 合并标题
            old_title, _ = seen[filename]
            seen[filename] = (f"{old_title} + {section_title}", "")
        else:
            seen[filename] = (section_title, "")
            order.append(filename)
    for filename in order:
        section_title, _ = seen[filename]
        lines.append(f"- [{section_title}]({filename})")
    lines.append("")
    return "\n".join(lines)


# ────────────────────────── 主入口 ──────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="按章节/前缀拆分已渲染的 markdown 文件为多文件"
    )
    parser.add_argument("--input", required=True, help="待拆分的 markdown 文件")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--prefix-map", help="前缀映射 YAML/JSON（可选，无则按 ## 标题拆分）")
    parser.add_argument("--title", default="API 协议 Spec", help="README 总标题")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR 文件不存在: {input_path}", file=sys.stderr)
        return 2

    content = input_path.read_text(encoding="utf-8")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 提取前言（第一个 ## 之前的内容）
    first_h2 = CHAPTER_PATTERN.search(content)
    preface = content[: first_h2.start()].rstrip() if first_h2 else ""

    if args.prefix_map:
        prefix_map_path = Path(args.prefix_map)
        if not prefix_map_path.exists():
            print(f"ERROR prefix-map 文件不存在: {prefix_map_path}", file=sys.stderr)
            return 2
        prefix_map = load_prefix_map(prefix_map_path)
        files = split_with_prefix_map(content, prefix_map)
    else:
        files = split_auto(content)

    if not files:
        print("ERROR 未找到可拆分的章节", file=sys.stderr)
        return 1

    # 写入文件（同名合并）
    file_contents: dict[str, list[str]] = {}
    file_titles: dict[str, str] = {}
    for filename, section_title, body in files:
        if filename not in file_contents:
            file_contents[filename] = []
            file_titles[filename] = section_title
        file_contents[filename].append(body)

    written_files: list[tuple[str, str]] = []
    for filename, bodies in file_contents.items():
        merged = "\n\n".join(bodies)
        # 加上文件级标题
        title = file_titles[filename]
        full = f"# {title}\n\n{merged}"
        (output_dir / filename).write_text(full, encoding="utf-8")
        written_files.append((filename, title))

    # 生成 README
    files_for_readme = [(fn, t, "") for fn, t in written_files]
    readme = build_readme(args.title, files_for_readme, preface)
    (output_dir / "README.md").write_text(readme, encoding="utf-8")

    print(f"OK split: {output_dir}")
    print(f"   - 输入: {input_path}")
    print(f"   - 输出文件:")
    print(f"     - README.md")
    for fn, _ in written_files:
        print(f"     - {fn}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
