"""
check.py · 一致性扫描 (统一引擎)

单一入口，协议式扩展:
  · 读取 S10_概念注册表.yaml → 结构化概念 + 违规分类(宪法/弃用/残留)
  · 读取 skf.yaml → content_root + exclude 规则
  · 读取 AGENTS.md §9 → 术语红线补充
  · 零外部依赖的 yaml 解析器 (自包含回退)

用法:
  python check.py                        # 传统模式
  python check.py --mode score           # 评分模式 (0-100)
  python check.py --mode score --min-score 0.8

扩展协议 (项目通过文件位置实例化):
  创作正文/状态/S10_概念注册表.yaml  → 项目词典 + 违规严重度
  skf.yaml                            → 项目配置 (content_root, exclude)
  AGENTS.md §9                        → 术语红线补充 (纯文本解析)
"""
import argparse
import sys
import os
import re
import json
import io

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


# ═══════════════════════════════════════════════════════════
# 零 · 配置加载 (自实现，零依赖)
# ═══════════════════════════════════════════════════════════

def _load_dotenv(env_path):
    result = {}
    if not os.path.exists(env_path):
        return result
    try:
        with open(env_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, val = line.partition("=")
                    result[key.strip()] = val.strip()
    except Exception:
        pass
    return result


def _load_json_config(json_path):
    if not os.path.exists(json_path):
        return {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {k: v for k, v in data.items() if not k.startswith("_")}
    except Exception:
        return {}


def _cfg(key, default, env=None, config=None, defaults=None):
    if env and key in env:
        val = env[key]
        try: return int(val)
        except: pass
        try: return float(val)
        except: pass
        return val
    if config and key in config:
        return config[key]
    if defaults and key in defaults:
        return defaults[key]
    return default


def find_project_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    return os.path.dirname(skill_dir)


# ═══════════════════════════════════════════════════════════
# 一 · 概念注册表加载 (吸收 SKF Registry 精华)
# ═══════════════════════════════════════════════════════════

# 违规类型常量
VIOLATION_PRINCIPLE = "constitution_violation"   # 宪法公理违规 (严重)
VIOLATION_DEPRECATED = "concept_deprecation"      # 概念弃用 (中等)
VIOLATION_TERM = "term_residual"                   # 术语残留 (轻微)

# 默认严重度——按概念类别
_CATEGORY_SEVERITY = {
    "principle": 8,
    "character": 3,
    "worldbuilding": 3,
    "plot": 3,
    "term": 1,
}


def _load_registry(project_root):
    """
    读取 S10_概念注册表.yaml，返回:
      {
        "deprecated_map": {废弃术语: (违规类型, 严重度, 所属概念)},
        "concept_count": int,
      }
    
    这是 SKF Registry.classify_violation() 的等价实现。
    项目通过文件位置实例化 —— 只需把 YAML 放在约定路径。
    """
    registry_path = os.path.join(project_root, "创作正文", "状态", "S10_概念注册表.yaml")
    if not os.path.exists(registry_path):
        return {"deprecated_map": {}, "concept_count": 0}

    # 自包含 YAML 解析 (首选 pyyaml，回退纯 Python)
    data = None
    try:
        import yaml
        with open(registry_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except ImportError:
        data = _parse_yaml_pure(registry_path)

    if not data or "concepts" not in data:
        return {"deprecated_map": {}, "concept_count": 0}

    concepts = data["concepts"]
    deprecated_map = {}
    for concept_name, info in concepts.items():
        category = info.get("category", "term")
        severity = info.get("severity", 0)
        if severity <= 0:
            severity = _CATEGORY_SEVERITY.get(category, 1)
        for alias in info.get("deprecated_aliases", []):
            if category == "principle":
                deprecated_map[alias] = (VIOLATION_PRINCIPLE, severity, concept_name)
            elif alias == concept_name or alias in concepts:
                deprecated_map[alias] = (VIOLATION_DEPRECATED, 2, concept_name)
            else:
                deprecated_map[alias] = (VIOLATION_TERM, 1, concept_name)

    return {"deprecated_map": deprecated_map, "concept_count": len(concepts)}


def _parse_yaml_pure(yaml_path):
    """纯 Python YAML 解析器 —— 自包含回退，零外部依赖。"""
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return None

    result = {"concepts": {}}
    current_concept = None
    in_aliases = False
    in_keywords = False

    for line in lines:
        stripped = line.rstrip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())

        if indent == 0 and ":" in stripped and not stripped.startswith(" "):
            continue  # 顶层键

        if indent == 2 and ":" in stripped:
            key = stripped.split(":")[0].strip().strip('"').strip("'")
            if key not in ("concepts",):
                current_concept = key
                if "concepts" not in result:
                    result["concepts"] = {}
                result["concepts"][current_concept] = {
                    "category": "term",
                    "deprecated_aliases": [],
                    "keywords": [],
                }
                in_aliases = False
                in_keywords = False

        elif indent == 4:
            if stripped.startswith("category:"):
                cat = stripped.split(":")[1].strip().strip('"').strip("'")
                if current_concept:
                    result["concepts"][current_concept]["category"] = cat
            elif stripped.startswith("deprecated_aliases:"):
                in_aliases = True
                in_keywords = False
            elif stripped.startswith("keywords:"):
                in_keywords = True
                in_aliases = False
            elif in_aliases and stripped.startswith("- "):
                alias = stripped[2:].strip().strip('"').strip("'")
                if current_concept and alias:
                    result["concepts"][current_concept]["deprecated_aliases"].append(alias)
            elif in_keywords and stripped.startswith("- "):
                kw = stripped[2:].strip().strip('"').strip("'")
                if current_concept and kw:
                    result["concepts"][current_concept]["keywords"].append(kw)
            else:
                in_aliases = False
                in_keywords = False
        else:
            in_aliases = False
            in_keywords = False

    return result


# ═══════════════════════════════════════════════════════════
# 二 · 项目配置加载 (skf.yaml)
# ═══════════════════════════════════════════════════════════

def _load_project_config(project_root):
    """读取 skf.yaml 获取 content_root + exclude 规则。"""
    config_path = os.path.join(project_root, "skf.yaml")
    config = {"content_root": "创作正文", "exclude": []}
    if not os.path.exists(config_path):
        return config

    data = None
    try:
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except ImportError:
        # 简单解析 skf.yaml 的 source.exclude
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        exclude = []
        for m in re.finditer(r'-\s*"([^"]+)"', content):
            exclude.append(m.group(1))
        config["exclude"] = exclude
        return config

    if data:
        config["content_root"] = data.get("project", {}).get("content_root", "创作正文")
        config["exclude"] = data.get("source", {}).get("exclude", [])
    return config


# ═══════════════════════════════════════════════════════════
# 三 · 文件扫描
# ═══════════════════════════════════════════════════════════

def _should_skip(rel_path, exclude_patterns):
    """任何 exclude 模式匹配路径则跳过。"""
    for pat in exclude_patterns:
        if pat in rel_path:
            return True
    return False


def _scan_content(project_root, content_dir, exclude, deprecated_map):
    """扫描内容目录，返回 [(文件, 行号, 术语, 违规类型, 严重度)]。"""
    hits = []
    scan_dir = os.path.join(project_root, content_dir)
    if not os.path.exists(scan_dir):
        return hits

    # 默认排除
    default_exclude = ["concept_graph", "S11_概念注册表", "S12_术语注册表",
                       "AGENTS.md", "S00_工程方法论", "S00_项目工作台", "S30_", "S50_",
                       "归档", "工具", "__pycache__", ".git"]
    all_exclude = list(default_exclude)
    for item in exclude:
        if item not in all_exclude:
            all_exclude.append(item)

    files_scanned = 0
    for root, dirs, files in os.walk(scan_dir):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "node_modules")]
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(root, fname)
            try:
                rel = os.path.relpath(fpath, project_root)
            except ValueError:
                rel = fpath
            if _should_skip(rel, all_exclude):
                continue
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception:
                continue
            files_scanned += 1

            for term, (vtype, severity, parent) in deprecated_map.items():
                if term not in text:
                    continue
                idx = 0
                while True:
                    idx = text.find(term, idx)
                    if idx == -1:
                        break
                    line_num = text[:idx].count("\n") + 1
                    hits.append((rel, line_num, term, vtype, severity))
                    idx += len(term)

    return hits, files_scanned


# ═══════════════════════════════════════════════════════════
# 四 · 报告输出
# ═══════════════════════════════════════════════════════════

def _format_violation_type(vtype):
    return {"constitution_violation": "宪法", "concept_deprecation": "弃用", "term_residual": "残留"}.get(vtype, vtype)


def _print_report(hits, files_scanned, mode, min_score):
    if mode != "score":
        if not hits:
            print(f"CLEAN: {files_scanned} files")
        else:
            for rel, line, term, vtype, severity in hits:
                label = _format_violation_type(vtype)
                print(f"  {rel}:L{line} [{label}:{severity}] {term}")
            print(f"\n共 {len(hits)} 处问题 · {files_scanned} 文件")
        return

    # 评分模式
    score = max(0, 100 - sum(s for _, _, _, _, s in hits))
    term_count = sum(1 for _, _, _, v, _ in hits if v == VIOLATION_TERM)
    depr_count = sum(1 for _, _, _, v, _ in hits if v == VIOLATION_DEPRECATED)
    princ_count = sum(1 for _, _, _, v, _ in hits if v == VIOLATION_PRINCIPLE)

    parts = [f"得分 {score}/100"]
    if term_count: parts.append(f"残留 {term_count} 处")
    if depr_count: parts.append(f"概念弃用 {depr_count} 处")
    if princ_count: parts.append(f"宪法违规 {princ_count} 处")
    parts.append(f"扫描 {files_scanned} 文件")
    print(" | ".join(parts))

    if hits:
        for rel, line, term, vtype, severity in hits[:15]:
            label = _format_violation_type(vtype)
            print(f"  {rel}:L{line} [{label}:{severity}] {term}")
        if len(hits) > 15:
            print(f"  ... 还有 {len(hits)-15} 条")

    if score >= 85:
        print("[PASS]")
    elif score >= 60:
        print("[CONDITIONAL]")
    else:
        print("[FAIL]")

    if score < min_score * 100:
        sys.exit(1)


# ═══════════════════════════════════════════════════════════
# 五 · 主入口
# ═══════════════════════════════════════════════════════════

def run_check(mode="check", min_score=0.8):
    project_root = find_project_root()

    # 协议式加载：项目通过文件位置实例化
    registry = _load_registry(project_root)
    config = _load_project_config(project_root)

    # 二次补充：AGENTS.md §9 术语红线
    agents_path = os.path.join(project_root, "AGENTS.md")
    if os.path.exists(agents_path):
        with open(agents_path, "r", encoding="utf-8") as f:
            agents_text = f.read()
        table_section = re.search(r"### 全局废弃术语.*?(?=\n##|\n---|\Z)", agents_text, re.DOTALL)
        if table_section:
            for row in table_section.group(0).split("\n"):
                cols = [c.strip() for c in row.split("|") if c.strip()]
                if len(cols) >= 1 and cols[0] not in ("废弃", "------", ""):
                    kw = cols[0]
                    if len(kw) >= 2 and kw not in registry["deprecated_map"]:
                        registry["deprecated_map"][kw] = (VIOLATION_TERM, 1, "AGENTS.md")

    print(f"[check] 项目: {project_root}")
    print(f"[check] 概念: {registry['concept_count']} 个 · 废弃术语: {len(registry['deprecated_map'])} 个")

    hits, files_scanned = _scan_content(
        project_root,
        config["content_root"],
        config["exclude"],
        registry["deprecated_map"],
    )

    _print_report(hits, files_scanned, mode, min_score)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="一致性扫描 (协议式扩展: YAML注册表 + skf.yaml + AGENTS.md)")
    parser.add_argument("--mode", choices=["check", "score"], default="check")
    parser.add_argument("--min-score", type=float, default=0.8)
    args = parser.parse_args()
    run_check(args.mode, args.min_score)