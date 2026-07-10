#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
init_world_index.py — 世界观文档索引初始化/更新脚本

扫描世界观文档目录，生成/更新 world_index.yaml。
首次运行：从 skill-novel-engine/world_index.yaml.example 模板 + 文件扫描生成完整索引。
增量运行：检测新增/删除文档，保留已有手动分类。

用法:
  python skill-novel-engine/scripts/init_world_index.py                           # 使用默认路径
  python skill-novel-engine/scripts/init_world_index.py --content-root 创作正文/世界观  # 指定内容目录
  python skill-novel-engine/scripts/init_world_index.py --output ./my-index.yaml   # 指定输出路径
"""

import argparse
import os
import sys
import re
import io
import yaml
from datetime import datetime
from pathlib import Path

# Windows 控制台 UTF-8 编码修复
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── 路径解析（可被命令行参数覆盖）──────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_SKILL_DIR = _SCRIPT_DIR.parent
_PROJECT_ROOT = _SKILL_DIR.parent
_DEFAULT_CONTENT_ROOT = "创作正文/世界观"
_DEFAULT_OUTPUT = "world_index.yaml"

EXAMPLE_PATH = _SKILL_DIR / "world_index.yaml.example"

# 层级关键词推断规则
LAYER_KEYWORDS = {
    "foundation": [
        "灵子", "自旋", "Klein-Gordon", "灵压", "灵导率σ", "BEC", "公理", "常数",
        "宇宙", "星球", "大爆炸", "时间线", "双重物理", "灵场方程", "Maxwell",
        "标量玻色子", "L场量子", "物理公理"
    ],
    "protocol": [
        "转换", "耦合", "退相干", "阻抗", "压制公式", "伤害公式", "消耗率",
        "信仰之力", "谐振", "能效跃迁", "同位素", "波导", "路由协议",
        "基态转换", "精神力学", "灵魂理论", "时空论"
    ],
    "representation": [
        "分类", "品阶", "矩阵", "列表", "境界", "资质", "势力", "地图",
        "古籍", "对照表", "成员表", "σ_L", "S-ling", "凡品", "灵品", "地品", "天品",
        "九洲", "七层", "八境", "27种", "27部"
    ],
    "session": [
        "应用", "场景", "操作", "修炼", "战斗", "炼丹", "炼器", "声望",
        "角色", "叙事", "创新", "讽刺", "阶层", "穿越", "塑造原则",
        "创新范式", "绝灵近身", "双域", "监控"
    ]
}


def extract_title_from_md(filepath):
    """从 .md 文件提取第一个 # 标题"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# ") and not line.startswith("## "):
                    return line[2:].strip()
    except Exception:
        pass
    return None


def extract_keywords_from_md(filepath, max_lines=200):
    """从 .md 文件开头提取关键词"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = "".join(f.readline() for _ in range(max_lines))
        return set(re.findall(r'[\u4e00-\u9fff\w]+', content))
    except Exception:
        return set()


def classify_by_keywords(keywords):
    """用关键词启发式推断文档层级"""
    scores = {layer: 0 for layer in LAYER_KEYWORDS}
    for layer, kws in LAYER_KEYWORDS.items():
        for kw in kws:
            if kw in keywords or kw.lower() in (w.lower() for w in keywords):
                scores[layer] += 1
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "representation"  # 默认归类
    return best


def load_template():
    """加载 example 模板中已有的文档条目"""
    if not EXAMPLE_PATH.exists():
        print(f"[WARN] 模板文件不存在: {EXAMPLE_PATH}")
        return {}, []

    with open(EXAMPLE_PATH, "r", encoding="utf-8") as f:
        template = yaml.safe_load(f)

    # 构建 path → (layer, entry) 映射
    known = {}
    if "layers" in template:
        for layer_name in ["foundation", "protocol", "representation", "session", "meta_documents"]:
            entries = template.get("layers", {}).get(layer_name, [])
            if entries:
                for entry in entries:
                    if "path" in entry:
                        norm_path = entry["path"].replace("\\", "/")
                        known[norm_path] = (layer_name, entry)

    # 保留 cross_layer_queries
    cross_layer = template.get("cross_layer_queries", [])

    return known, cross_layer


def scan_world_directory(world_dir, project_root):
    """扫描世界观目录，返回所有 .md 文件"""
    md_files = []
    if world_dir.exists():
        for f in sorted(world_dir.glob("*.md")):
            md_files.append(str(f.relative_to(project_root)))
    return md_files


def generate_index(content_root=None, output_path=None, project_root=None):
    """主流程：生成 world_index.yaml"""
    # 参数解析
    if project_root is None:
        project_root = _PROJECT_ROOT
    else:
        project_root = Path(project_root).resolve()
    if content_root is None:
        content_root = _DEFAULT_CONTENT_ROOT
    if output_path is None:
        output_path = _DEFAULT_OUTPUT

    world_dir = project_root / content_root
    output_path = project_root / output_path

    print("=" * 60)
    print("init_world_index.py — 世界观文档索引生成器")
    print("=" * 60)
    print(f"  内容目录: {world_dir}")
    print(f"  输出文件: {output_path}")
    print(f"  项目根目录: {project_root}")
    print("=" * 60)

    # 1. 加载模板
    known_entries, cross_layer = load_template()
    print(f"\n[1] 模板加载: {len(known_entries)} 个已知文档条目")

    # 2. 扫描目录
    md_files = scan_world_directory(world_dir, project_root)
    print(f"[2] 目录扫描: {len(md_files)} 个 .md 文件")

    # 3. 按层级组织
    layers = {
        "foundation": [],
        "protocol": [],
        "representation": [],
        "session": [],
        "meta_documents": []
    }

    new_count = 0
    auto_count = 0
    skipped_count = 0

    for fpath in md_files:
        abspath = project_root / fpath
        title = extract_title_from_md(abspath) or os.path.splitext(os.path.basename(fpath))[0]

        # 检查是否已知 —— 路径归一化后匹配
        norm_path = fpath.replace("\\", "/")
        matched_layer = None
        matched_entry = None

        if norm_path in known_entries:
            matched_layer, matched_entry = known_entries[norm_path]
            matched_entry = dict(matched_entry)  # 深拷贝

        if matched_entry:
            # 已知文档 — 使用模板数据
            matched_entry.pop("_note", None)
            layers[matched_layer].append(matched_entry)
        else:
            # 新文档 — 自动推断
            keywords = extract_keywords_from_md(abspath)
            layer = classify_by_keywords(keywords)
            doc_id = os.path.splitext(os.path.basename(fpath))[0]

            new_entry = {
                "id": re.sub(r'\s+', '-', doc_id.lower()),
                "path": norm_path,
                "title": title,
                "category": "未分类",
                "description": "自动推断: " + (title or doc_id),
                "load_on": {
                    "agents": [],
                    "phases": [],
                    "conditions": []
                },
                "dependencies": [],
                "auto_classified": True
            }

            # 元文档检测
            title_lower = title.lower() if title else ""
            if any(kw in title_lower for kw in ["索引", "全貌", "定义全貌"]):
                layers["meta_documents"].append(new_entry)
            else:
                layers[layer].append(new_entry)
            auto_count += 1

    # 4. 统计
    total = len(md_files)
    new_count = len(md_files) - auto_count

    # 5. 生成 YAML
    output = {
        "meta": {
            "_note": "索引元数据 — 由 init_world_index.py 自动生成",
            "generated_at": datetime.now().isoformat(),
            "total_documents": total,
            "index_version": "1.0",
            "content_root": str(world_dir.relative_to(project_root)).replace("\\", "/"),
            "skill_version": "2.0"
        },
        "layers": layers,
        "cross_layer_queries": cross_layer
    }

    # 6. 写入文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# world_index.yaml — 由 init_world_index.py 自动生成\n")
        f.write("# 位置: 项目根目录\n")
        f.write("# 生成时间: " + datetime.now().isoformat() + "\n")
        f.write("# 手动编辑后请运行 check.py 验证一致性\n")
        f.write("# 新增文档后运行: python skill-novel-engine/scripts/init_world_index.py\n")
        f.write("\n")
        yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # 7. 输出报告
    print("\n[3] 索引生成完成")
    print("    总计: %d 个文档" % total)
    print("    模板匹配: %d 个" % new_count)
    print("    自动推断: %d 个" % auto_count)
    if total > 0:
        print("    覆盖率: %d%%" % int(new_count / total * 100))
    print("\n    分层统计:")
    for lname, entries in layers.items():
        if entries:
            count = len(entries)
            auto = sum(1 for e in entries if e.get("auto_classified"))
            print("      %-20s: %d 个 (%d 自动推断)" % (lname, count, auto))
    print("\n    输出文件: " + str(output_path))

    if auto_count > 0:
        print("\n[!] 有 %d 个文档为自动推断分类，请人工审核后删除 auto_classified 标记。" % auto_count)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="世界观文档索引初始化/更新脚本"
    )
    parser.add_argument(
        "--content-root",
        default=_DEFAULT_CONTENT_ROOT,
        help=f"世界观文档目录（相对于项目根目录，默认: {_DEFAULT_CONTENT_ROOT}）"
    )
    parser.add_argument(
        "--output",
        default=_DEFAULT_OUTPUT,
        help=f"输出文件路径（相对于项目根目录，默认: {_DEFAULT_OUTPUT}）"
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="项目根目录（默认: 自动检测为脚本的祖父目录）"
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve() if args.project_root else _PROJECT_ROOT
    sys.exit(generate_index(
        content_root=args.content_root,
        output_path=args.output,
        project_root=project_root
    ))
