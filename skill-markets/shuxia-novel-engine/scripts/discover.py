"""
discover.py · 项目结构发现 + 悲观检查

用法:
  python discover.py                      # 文件清单 (传统)
  python discover.py --mode check         # 悲观结构验证 — 报告缺什么
  python discover.py --mode check --json  # JSON 输出

设计原则:
  · 假设项目是坏的 → 逐项证明它是好的 (悲观检查)
  · 每次发现缺失 → 告诉用户缺了什么 + 为什么需要它
  · 分三级: critical(阻塞) / recommended(建议) / db_ready(可选)
"""
import argparse
import io
import json
import os
import re
import sys

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

LAYER_PATTERNS = {
    "worldview": {"dir": "世界观", "pattern": r"\.md$"},
    "characters": {"dir": "人物", "pattern": r"\.md$"},
    "plot": {"dir": "剧情", "pattern": r"\.md$"},
    "chapters": {"dir": "章节规划", "pattern": r"\.md$"},
    "state": {"dir": "状态", "pattern": r"\.(md|yaml|json)$"},
}

CHAPTER_PATTERN = re.compile(r"第(\d+)章")

# ═══════════════════════════════════════════════════════════
# 项目结构基线 — 定义"完整项目"应该有什么
# ═══════════════════════════════════════════════════════════

REQUIRED_STRUCTURE = {
    "critical": {
        "AGENTS.md": "AI 操作规则 — 宪法公理/角色锚点/术语红线/赢面公式",
        "skf.yaml": "项目配置 — content_root + exclude 规则，skill 通过它定位内容",
        "创作正文/世界观/亚文化建设宪法.md": "7 条公理 — 世界规则的不可违背边界",
        "创作正文/世界观/亚文化四层索引.md": "导航中枢 — 底层→协议→表示→会话 的完整索引",
        "创作正文/状态/S00_项目工作台.md": "项目工作台 — 资产盘点 + 优先级 + 修改日志",
        "创作正文/状态/S10_概念注册表.yaml": "概念注册表 — 废弃术语映射 + 违规严重度 (check.py 的数据源)",
    },
    "recommended": {
        "创作正文/世界观/赛博修真科技树.md": "科技树 — 五层工程架构 + 小真耦合 + 赢面映射",
        "创作正文/世界观/势力版图.md": "势力版图 — 宗门/王朝/散修联盟的关系网络",
        "创作正文/世界观/修真物理学.md": "L场/灵子模型 — 双重物理视角的数学基础",
        "创作正文/世界观/修真生物学与境界学.md": "境界/寿元 — 八境量化参数",
        "创作正文/人物/人物关系图.md": "人物关系图 — 全角色网络",
        "创作正文/剧情/全卷骨架_卷一.md": "全卷骨架 — 至少卷一必须存在",
        "创作正文/剧情/伏笔追踪.md": "伏笔追踪 — 投放/回收/跨卷状态",
        "创作正文/状态/S12_术语注册表.md": "术语注册表 — 人类可读版废弃术语清单",
        "创作正文/状态/S01_会话上下文.md": "会话上下文 — 新会话快速接入指南",
    },
    "db_ready": {
        "schema/schema.sql": "SQLite Schema — 20 表量化分析引擎 (运行 init_db.py 激活)",
    },
}


def _find_project_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    return os.path.dirname(skill_dir)


# ═══════════════════════════════════════════════════════════
# 传统模式: 文件发现 (保持向后兼容)
# ═══════════════════════════════════════════════════════════

def discover(project_root):
    scan_root = os.path.join(project_root, "创作正文")
    if not os.path.isdir(scan_root):
        return {"error": "创作正文目录未找到: " + scan_root}

    result = {"project_root": project_root, "total_files": 0, "layers": {}}

    for layer_name, cfg in LAYER_PATTERNS.items():
        layer_dir = os.path.join(scan_root, cfg["dir"])
        if not os.path.isdir(layer_dir):
            result["layers"][layer_name] = {"count": 0, "files": []}
            continue

        files = []
        for root, dirs, filenames in os.walk(layer_dir):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", "归档", ".git")]
            for fname in sorted(filenames):
                if re.search(cfg["pattern"], fname):
                    rel_path = os.path.relpath(os.path.join(root, fname), project_root)
                    file_info = {"name": fname, "path": rel_path}
                    if layer_name == "chapters":
                        m = CHAPTER_PATTERN.search(fname)
                        if m:
                            file_info["chapter_num"] = int(m.group(1))
                    files.append(file_info)

        result["layers"][layer_name] = {"count": len(files), "files": files}
        result["total_files"] += len(files)

    for extra in ["AGENTS.md", "README.md", "skf.yaml"]:
        if os.path.exists(os.path.join(project_root, extra)):
            result["total_files"] += 1

    return result


# ═══════════════════════════════════════════════════════════
# 悲观检查模式: 逐项验证项目结构
# ═══════════════════════════════════════════════════════════

def check_structure(project_root):
    """悲观检查: 假设每项都缺 → 逐项证明存在。返回 (missing, present, issues)。"""
    missing = {"critical": [], "recommended": [], "db_ready": []}
    present = {"critical": [], "recommended": [], "db_ready": []}
    issues = []  # (level, path, issue_description)

    for level in ["critical", "recommended", "db_ready"]:
        for path, description in REQUIRED_STRUCTURE[level].items():
            full_path = os.path.join(project_root, path)
            if os.path.exists(full_path):
                present[level].append({"path": path, "description": description})
                # 额外的健康检查
                if path.endswith(".yaml") and "概念注册表" in path:
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        if "concepts:" not in content and "deprecated_aliases:" not in content:
                            issues.append((level, path, "YAML 缺少 concepts 或 deprecated_aliases 字段"))
                    except Exception:
                        issues.append((level, path, "YAML 文件无法读取"))
            else:
                missing[level].append({"path": path, "description": description})

    # 额外检查: S10 注册表是否有废弃术语
    registry_path = os.path.join(project_root, "创作正文", "状态", "S10_概念注册表.yaml")
    if os.path.exists(registry_path):
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                content = f.read()
            if "deprecated_aliases:" not in content:
                issues.append(("critical", "创作正文/状态/S10_概念注册表.yaml",
                               "注册表存在但没有 deprecated_aliases 字段 — check.py 将无法检测任何残留"))
        except Exception:
            pass

    # 检查 skf.yaml 是否有效
    skf_path = os.path.join(project_root, "skf.yaml")
    if os.path.exists(skf_path):
        try:
            with open(skf_path, "r", encoding="utf-8") as f:
                content = f.read()
            if "content_root" not in content:
                issues.append(("critical", "skf.yaml", "缺少 content_root 字段 — skill 无法定位内容目录"))
        except Exception:
            issues.append(("critical", "skf.yaml", "skf.yaml 无法读取"))

    return missing, present, issues


# ═══════════════════════════════════════════════════════════
# 输出格式化
# ═══════════════════════════════════════════════════════════

def format_counts(result):
    layers = result.get("layers", {})
    for name, data in sorted(layers.items()):
        print(name + ": " + str(data["count"]) + " files")
    print("Total: " + str(result["total_files"]) + " files")


def format_list(result):
    layers = result.get("layers", {})
    for name, data in sorted(layers.items()):
        print("")
        print("--- " + name + " (" + str(data["count"]) + " files) ---")
        for f in data["files"]:
            marker = ""
            if "chapter_num" in f:
                marker = " [Ch." + str(f["chapter_num"]) + "]"
            print("  " + f["path"] + marker)
    print("")
    print("Total: " + str(result["total_files"]) + " files")


def format_check(missing, present, issues, as_json=False):
    if as_json:
        print(json.dumps({"missing": missing, "present": present, "issues": issues},
                         ensure_ascii=False, indent=2))
        return

    total_missing = sum(len(v) for v in missing.values())
    total_issues = len(issues)
    all_ok = total_missing == 0 and total_issues == 0

    # 图标
    OK = "OK" if sys.stdout.encoding == "utf-8" else "[OK]"
    MISS = "MISS" if sys.stdout.encoding == "utf-8" else "[MISS]"
    WARN = "WARN" if sys.stdout.encoding == "utf-8" else "[WARN]"

    if all_ok:
        print(f"  {OK}  项目结构完整 — 所有必需文件就位")
    else:
        print(f"  {MISS} 缺失 {total_missing} 项 · 问题 {total_issues} 项")
    print()

    for level, label, icon in [("critical", "阻塞级 (缺了 skill 无法工作)", MISS),
                                 ("recommended", "建议级 (缺了功能受限)", WARN),
                                 ("db_ready", "可选级 (SQLite 量化分析)", "   ")]:
        if missing.get(level) or present.get(level):
            print(f"── {label} ──")
            for item in present.get(level, []):
                print(f"  {OK}  {item['path']}")
            for item in missing.get(level, []):
                print(f"  {icon}  {item['path']}")
                print(f"       → {item['description']}")
            print()

    if issues:
        print("── 结构问题 ──")
        for level, path, desc in issues:
            print(f"  {WARN}  {path}")
            print(f"       → {desc}")
        print()

    if all_ok:
        print("  下一步: python init_db.py (初始化 SQLite 数据库)")
    else:
        print(f"  下一步: 创建上述 {total_missing} 个缺失文件，然后 python init_db.py")

    return 0 if all_ok else 1


# ═══════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="项目结构发现 + 悲观检查")
    parser.add_argument("--mode", choices=["discover", "check"], default="discover",
                        help="discover: 文件清单 / check: 悲观结构验证")
    parser.add_argument("--format", choices=["list", "json", "counts"], default="list")
    args = parser.parse_args()

    project_root = _find_project_root()

    if args.mode == "check":
        missing, present, issues = check_structure(project_root)
        exit_code = format_check(missing, present, issues, as_json=(args.format == "json"))
        sys.exit(exit_code)
    else:
        result = discover(project_root)
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.format == "counts":
            format_counts(result)
        else:
            format_list(result)