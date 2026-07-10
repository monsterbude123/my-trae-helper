#!/usr/bin/env python3
"""
export_subculture_package.py — 将 world_index.yaml 导出为 PlotPilot 亚文化包 (.zip)

用法:
    python skill-novel-engine/scripts/export_subculture_package.py \
        --name "万古余烬" \
        --version "1.0" \
        --author "作者名" \
        --description "硬核赛博修仙世界观" \
        --compatible-genres xianxia,xuanhuan \
        --output ./万古余烬_v1.0.zip

输入: skill-novel-engine/world_index.yaml + 创作正文/世界观/*.md
输出: 符合 PlotPilot manifest.yaml 规范的 .zip 包

目录结构:
    my_subculture.zip
    ├── manifest.yaml       ← PlotPilot 亚文化包元数据 + 文档索引
    ├── docs/               ← 世界观文档副本
    │   ├── 01_物理规则.md
    │   └── ...
    └── README.md           ← 亚文化说明
"""

import argparse
import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml


# ─── 项目根路径 ───────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORLD_INDEX_PATH = PROJECT_ROOT / "world_index.yaml"
CONTENT_ROOT = PROJECT_ROOT / "创作正文" / "世界观"


# ─── Category 映射表 ──────────────────────────────────────────────
# skill-novel-engine 的 category 标签 → PlotPilot manifest category key
CATEGORY_MAP = {
    "公理体系": "meta",
    "物理底层": "physics",
    "能量转换": "physics",
    "境界体系": "physics",
    "战斗系统": "technique",
    "装备系统": "technique",
    "资源经济": "economy",
    "地理": "geography",
    "势力": "faction",
    "技能树": "technique",
    "角色": "character",
    "叙事素材": "culture",
    "映射参考": "meta",
    "元文档": "meta",
}

# PlotPilot manifest 要求的 9 个标准 category
STANDARD_CATEGORIES = [
    {"key": "physics", "label": "物理规则"},
    {"key": "faction", "label": "势力版图"},
    {"key": "character", "label": "角色设定"},
    {"key": "economy", "label": "经济系统"},
    {"key": "geography", "label": "地理"},
    {"key": "technique", "label": "功法体系"},
    {"key": "culture", "label": "文化禁忌"},
    {"key": "style", "label": "文风约定"},
    {"key": "meta", "label": "元规则"},
]

# 始终加载的文档：即使 load_triggers 为空也设为 ["*"]
ALWAYS_LOAD_CATEGORIES = {"公理体系", "映射参考", "文风约定"}


# ─── 工具函数 ─────────────────────────────────────────────────────

def _parse_conditions(conditions: list) -> list[str]:
    """从 load_on.conditions（自然语言）提取 PlotPilot load_triggers 关键词。"""
    if not conditions:
        return []

    triggers: list[str] = []
    for cond in conditions:
        cond_str = str(cond)
        # 提取中文关键词（/分隔的第一段）
        parts = cond_str.replace("涉及", "").replace("描写", "").split("/")
        main = parts[0].strip()
        if main and len(main) <= 12:
            triggers.append(main)

    return triggers


def _to_doc_filepath(entry_path: str, index: int) -> str:
    """生成 docs/ 下的文件名，保持原始文件名的可读性。"""
    original = Path(entry_path).name
    return f"docs/{index:02d}_{original}"


def _extract_query_chains(raw_queries: list) -> list[dict]:
    """将 world_index 的 cross_layer_queries 转为 manifest 格式。"""
    chains = []
    for q in raw_queries:
        chain_desc = []
        for step in q.get("chain", []):
            # "session.equipment-quantification" → "装备法器量化 → §量化参数"
            parts = step.split(".", 1)
            doc_id = parts[1] if len(parts) > 1 else parts[0]
            chain_desc.append(f"{doc_id}")
        chains.append({
            "question": q.get("name", ""),
            "chain": chain_desc,
        })
    return chains


def _file_stem(path_str: str) -> str:
    """无扩展名的文件名。"""
    return Path(path_str).stem


# ─── 主逻辑 ──────────────────────────────────────────────────────

def build_manifest(
    world_index: dict,
    name: str,
    version: str,
    author: str,
    description: str,
    compatible_genres: list[str],
) -> tuple[dict, list[tuple[str, Path]]]:
    """
    从 world_index 构建 manifest.yaml 数据结构。
    返回: (manifest_dict, [(doc_rel_path, src_abs_path), ...])
    """
    layers = world_index.get("layers", {})

    # 收集所有非元文档条目
    entries_raw: list[dict] = []
    file_mapping: list[tuple[str, Path]] = []  # (manifest 中路径, 源文件绝对路径)

    layer_order = ["foundation", "protocol", "representation", "session"]
    for layer_name in layer_order:
        for entry in layers.get(layer_name, []):
            # 跳过废弃文档
            if entry.get("meta", {}).get("deprecates"):
                continue
            # 跳过空 triggers 且 phases 为空的废弃标记
            if not entry.get("load_on", {}).get("agents") and not entry.get("load_on", {}).get("phases"):
                continue

            src_path = CONTENT_ROOT / Path(entry["path"]).name
            if not src_path.exists():
                print(f"  ⚠ 跳过不存在的文件: {src_path}", file=sys.stderr)
                continue

            category = entry.get("category", "元文档")
            manifest_category = CATEGORY_MAP.get(category, "meta")

            entries_raw.append({
                "file": None,  # 稍后统一填充
                "title": entry.get("title", _file_stem(entry["path"])),
                "category": manifest_category,
                "description": entry.get("description", ""),
                "load_triggers": _parse_conditions(
                    entry.get("load_on", {}).get("conditions", [])
                ) or (["*"] if category in ALWAYS_LOAD_CATEGORIES else []),
                "_src_path": entry["path"],
                "_category_label": category,
            })

    # 分配文件路径（排序后分配编号）
    entries_raw.sort(key=lambda e: e["_src_path"])

    entries: list[dict] = []
    idx = 1
    for e in entries_raw:
        doc_rel = _to_doc_filepath(e["_src_path"], idx)
        file_mapping.append((doc_rel, CONTENT_ROOT / Path(e["_src_path"]).name))
        e["file"] = doc_rel
        del e["_src_path"]
        del e["_category_label"]
        entries.append(e)
        idx += 1

    # 只输出实际使用了的 category
    used_cats = set(e["category"] for e in entries)
    categories = [c for c in STANDARD_CATEGORIES if c["key"] in used_cats]

    # 处理 cross_layer_queries
    raw_queries = world_index.get("cross_layer_queries", [])
    query_chains = _extract_query_chains(raw_queries)

    manifest = {
        "meta": {
            "name": name,
            "version": version,
            "author": author,
            "description": description,
            "compatible_genres": compatible_genres,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
        },
        "docs": {
            "categories": categories,
            "entries": entries,
            "query_chains": query_chains,
        },
    }

    return manifest, file_mapping


def generate_readme(manifest: dict) -> str:
    """生成 README.md 内容。"""
    meta = manifest["meta"]
    entries = manifest["docs"]["entries"]
    lines = [
        f"# {meta['name']} — 亚文化包",
        "",
        f"- **版本**: {meta['version']}",
        f"- **作者**: {meta['author']}",
        f"- **兼容题材**: {', '.join(meta['compatible_genres'])}",
        f"- **导出时间**: {meta['created_at']}",
        "",
        meta["description"],
        "",
        "## 文档清单",
        "",
    ]
    for e in entries:
        lines.append(f"- [{e['title']}]({e['file']}) — {e['description']}")

    lines.append("")
    lines.append("## 使用说明")
    lines.append("")
    lines.append("在 PlotPilot 的亚文化管理页上传此 .zip 包，即可在创建小说时选择此亚文化。")
    lines.append("写作时，AI 会根据当前场景自动加载相关文档。")

    return "\n".join(lines) + "\n"


def run_check_before_export() -> bool:
    """导出前运行 check.py 做质量校验。"""
    check_script = PROJECT_ROOT / "skill-novel-engine" / "scripts" / "check_chapters.py"
    if not check_script.exists():
        print("  ⚠ check.py 不存在，跳过校验", file=sys.stderr)
        return True

    import subprocess
    result = subprocess.run(
        [sys.executable, str(check_script)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  ✗ check.py 校验失败 (exit={result.returncode})", file=sys.stderr)
        print(result.stdout[-500:], file=sys.stderr)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="将 world_index.yaml 导出为 PlotPilot 亚文化包 (.zip)"
    )
    parser.add_argument("--name", required=True, help="亚文化名称")
    parser.add_argument("--version", required=True, help="版本号")
    parser.add_argument("--author", default="", help="作者名")
    parser.add_argument("--description", required=True, help="一句话描述")
    parser.add_argument(
        "--compatible-genres",
        required=True,
        help="兼容的题材 genre_key，逗号分隔，如 xianxia,xuanhuan"
    )
    parser.add_argument("--output", "-o", default=None, help="输出 .zip 路径")
    parser.add_argument("--skip-check", action="store_true", help="跳过导出前校验")
    args = parser.parse_args()

    compatible_genres = [g.strip() for g in args.compatible_genres.split(",") if g.strip()]
    if not compatible_genres:
        print("错误: --compatible-genres 不能为空", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or f"{args.name}_v{args.version}.zip"

    # ── 校验 ─────────────────────────────────────────────────
    if not WORLD_INDEX_PATH.exists():
        print(f"错误: world_index.yaml 不存在: {WORLD_INDEX_PATH}", file=sys.stderr)
        sys.exit(1)

    if not args.skip_check:
        print("[1/4] 运行质量校验...")
        if not run_check_before_export():
            print("  → 使用 --skip-check 跳过校验，或修复问题后重试", file=sys.stderr)
            sys.exit(1)
        print("  ✓ 校验通过")
    else:
        print("[1/4] 跳过校验 (--skip-check)")

    # ── 读取 world_index.yaml ───────────────────────────────
    print(f"[2/4] 读取 world_index.yaml...")
    with open(WORLD_INDEX_PATH, "r", encoding="utf-8") as f:
        world_index = yaml.safe_load(f)

    # ── 构建 manifest ───────────────────────────────────────
    print(f"[3/4] 构建 manifest.yaml...")
    manifest, file_mapping = build_manifest(
        world_index,
        args.name,
        args.version,
        args.author,
        args.description,
        compatible_genres,
    )
    print(f"  → 包含 {len(file_mapping)} 份文档")

    # ── 打包 .zip ──────────────────────────────────────────
    print(f"[4/4] 打包 {output_path}...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # 写 manifest.yaml
        manifest_path = tmp / "manifest.yaml"
        with open(manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(manifest, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        print(f"  ✓ manifest.yaml")

        # 写 README.md
        readme_path = tmp / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(generate_readme(manifest))
        print(f"  ✓ README.md")

        # 复制文档到 docs/
        docs_dir = tmp / "docs"
        docs_dir.mkdir()
        for rel_path, src_path in file_mapping:
            dst = tmp / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst)
            print(f"  ✓ {rel_path}")

        # 创建 .zip
        output_abs = Path(output_path).resolve()
        with zipfile.ZipFile(str(output_abs), "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(tmp.rglob("*")):
                if f.is_file():
                    arcname = str(f.relative_to(tmp))
                    zf.write(f, arcname)

        size_mb = output_abs.stat().st_size / (1024 * 1024)

    print(f"\n✓ 导出完成: {output_abs} ({size_mb:.1f} MB)")
    print(f"  可在 PlotPilot 亚文化管理页上传此文件。")


if __name__ == "__main__":
    main()
