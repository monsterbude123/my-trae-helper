"""ripple.py · 涟漪传播引擎

用法:
  python ripple.py --change "实体:字段:旧值->新值"
  python ripple.py --change "林岳:combat_power:3500->2500"

核心算法: BFS 分层传播 + 4跳截断 + 五级严重度
数据源: S10_概念注册表.yaml + 章节/骨架/伏笔文件全文扫描
自包含: 不依赖项目内任何 Python 模块，仅读 .yaml/.md 数据文件
"""
import argparse
import os
import re
import sys
from collections import deque
import io

# Windows UTF-8 兼容
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')



# ── 编码兼容 ──────────────────────────────────────────────
# 在 Windows 终端自动切换到 UTF-8，避免中文字符输出乱码
try:
    import io
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
# ── 项目路径工具 ──────────────────────────────────────────

def find_project_root():
    """从 skill-novel-engine/scripts/ 向上找到项目根目录"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


PROJECT_ROOT = find_project_root()
REGISTRY_PATH = os.path.join(PROJECT_ROOT, "创作正文", "状态", "S10_概念注册表.yaml")


# ── YAML 解析（轻量自包含，不依赖 PyYAML）─────────────────

def _parse_inline_list(text):
    """解析 [a, b, c] 或 [] 格式的列表"""
    text = text.strip()
    if text == "[]":
        return []
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1]
        items = []
        for item in inner.split(","):
            item = item.strip().strip("\"'")
            if item:
                items.append(item)
        return items
    return [text.strip().strip("\"'")] if text else []


def parse_concept_registry(path):
    """解析 S10_概念注册表.yaml，返回 {concept_name: {key: value|list}}"""
    concepts = {}
    current_concept = None
    current_key = None

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        s = line.rstrip()

        # 跳过注释、空行、顶层 "concepts:"
        if s.startswith("#") or s == "" or s == "concepts:":
            continue

        # 检测概念名: 恰好 2 空格缩进，以非空格字符开头，以 : 结尾
        if s.startswith("  ") and not s.startswith("    ") and s.endswith(":"):
            name = s[2:-1].strip()
            if name:
                current_concept = name
                concepts[current_concept] = {}
                current_key = None
            continue

        # 概念内的键值对: 4 空格缩进
        if current_concept and s.startswith("    "):
            inner = s[4:].strip()
            if ":" in inner:
                k, v = inner.split(":", 1)
                k, v = k.strip(), v.strip()

                # 去掉引号
                v = v.strip("\"'")

                # 检测是否为内联列表 [a, b, c]
                if v.startswith("[") and v.endswith("]"):
                    concepts[current_concept][k] = _parse_inline_list(v)
                else:
                    concepts[current_concept][k] = v
                current_key = k
            elif current_key:
                # 续行（理论上不会出现，但保留）
                pass

    return concepts


# ── 层级映射 ───────────────────────────────────────────────

CATEGORY_LAYER = {
    "character": "L1",
    "worldbuilding": "L2",
    "principle": "L0",
    "axiom": "L0",
}


def get_layer(concept):
    cat = concept.get("category", "")
    prov = concept.get("provenance", "")
    if cat in CATEGORY_LAYER:
        return CATEGORY_LAYER[cat]
    if prov == "constitutional":
        return "L0"
    return "L2"


def is_constitutional(concept):
    """仅 category=principle 的公理级概念触发 BLOCKER"""
    cat = concept.get("category", "")
    return cat == "principle"


# ── 依赖图构建 ─────────────────────────────────────────────

def build_graph(concepts, project_root):
    """从概念注册表 + 文件系统构建内存依赖图"""
    nodes = {}
    edges = []

    # 1. 概念节点
    for name, data in concepts.items():
        data["_name"] = name
        layer = get_layer(data)
        nodes[name] = {
            "type": "concept",
            "layer": layer,
            "label": name,
            "category": data.get("category", ""),
            "provenance": data.get("provenance", ""),
            "defined_in": data.get("defined_in", ""),
            "keywords": data.get("keywords", []),
            "is_constitutional": is_constitutional(data),
        }

        # defined_in → 文件节点 (ID 使用创作正文相对路径，/ 分隔)
        defined_in = data.get("defined_in", "")
        if defined_in:
            fp = os.path.join(project_root, "创作正文", defined_in)
            fid = "file:" + defined_in.replace("\\", "/")
            if fid not in nodes:
                nodes[fid] = {
                    "type": "file", "layer": "L1",
                    "label": defined_in, "path": fp,
                }
            edges.append((name, fid, "defined_in"))

        # related 边
        for rn in data.get("related", []):
            if rn in concepts:
                edges.append((name, rn, "related"))

    # 2. 章节节点
    cd = os.path.join(project_root, "创作正文", "章节规划")
    if os.path.exists(cd):
        for root, dirs, files in os.walk(cd):
            for fn in files:
                if fn.endswith(".md"):
                    rel = os.path.relpath(os.path.join(root, fn), project_root)
                    nodes["chapter:" + rel] = {
                        "type": "chapter", "layer": "L3",
                        "label": fn.replace(".md", ""),
                        "path": os.path.join(root, fn),
                    }

    # 3. 骨架 + 伏笔节点
    sd = os.path.join(project_root, "创作正文", "剧情")
    if os.path.exists(sd):
        for fn in os.listdir(sd):
            if not fn.endswith(".md"):
                continue
            fp = os.path.join(sd, fn)
            if fn.startswith("全卷骨架_"):
                nodes["skeleton:" + fn] = {
                    "type": "skeleton", "layer": "L2",
                    "label": fn.replace(".md", ""), "path": fp,
                }
            elif fn == "伏笔追踪.md":
                nodes["foreshadow:伏笔追踪"] = {
                    "type": "foreshadow", "layer": "L2",
                    "label": "伏笔追踪", "path": fp,
                }

    # 4. 科技树
    tp = os.path.join(project_root, "创作正文", "世界观", "赛博修真科技树.md")
    if os.path.exists(tp):
        nodes["file:世界观/赛博修真科技树.md"] = {
            "type": "file", "layer": "L1",
            "label": "赛博修真科技树", "path": tp,
        }

    # 5. 人物档案 + 其他世界观/状态文件 (补充 defined_in 未覆盖的)
    extra_dirs = [
        os.path.join(project_root, "创作正文", "人物"),
        os.path.join(project_root, "创作正文", "世界观"),
        os.path.join(project_root, "创作正文", "剧情"),
        os.path.join(project_root, "创作正文", "状态"),
    ]
    for ed in extra_dirs:
        if not os.path.exists(ed):
            continue
        for root, dirs, files in os.walk(ed):
            # 跳过归档和 superpowers 目录
            dirs[:] = [d for d in dirs if d not in ("归档", "superpowers", ".codex-plugin", ".claude-plugin", ".cursor-plugin", ".github", ".opencode")]
            for fn in files:
                if not fn.endswith(".md"):
                    continue
                    fp = os.path.join(root, fn)
                    # 使用创作正文下的相对路径作为 ID
                    try:
                        rel = os.path.relpath(fp, os.path.join(project_root, "创作正文"))
                    except ValueError:
                        rel = fn
                    fid = "file:" + rel.replace("\\", "/")
                    if fid not in nodes:
                        nodes[fid] = {
                            "type": "file", "layer": "L1",
                            "label": fn.replace(".md", ""),
                            "path": fp,
                        }

    return nodes, edges


# ── 文件关键词扫描 ──────────────────────────────────────────

def scan_file_for_keywords(filepath, keywords):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return [kw for kw in keywords if kw in content]
    except Exception:
        return []


def scan_project_files(nodes, concepts, project_root):
    """扫描章节/骨架/伏笔，建立 concept→file 的 mentions 边"""
    edges = []

    ck = {}
    for name, data in concepts.items():
        kws = list(data.get("keywords", []))
        kws.append(name)
        ck[name] = kws

    scan_targets = [
        (cid, nd) for cid, nd in nodes.items()
        if nd["type"] in ("chapter", "skeleton", "foreshadow")
    ]
    for node_id, nd in scan_targets:
        fp = nd.get("path", "")
        if not fp or not os.path.exists(fp):
            continue
        for cname, kws in ck.items():
            matched = scan_file_for_keywords(fp, kws)
            if matched:
                edges.append((cname, node_id, "mentions"))

    return edges


# ── BFS 涟漪传播 ───────────────────────────────────────────

def bfs_propagate(nodes, edges, start_entity, max_hops=4):
    """BFS 分层传播，返回 {node_id: (hop_distance, path_list)}"""
    adj = {}
    for src, dst, etype in edges:
        adj.setdefault(src, []).append((dst, etype))
        if etype in ("related", "mentions", "conflicts_with"):
            adj.setdefault(dst, []).append((src, etype))
        else:
            adj.setdefault(dst, [])

    visited = {}
    queue = deque()
    queue.append((start_entity, 0, [start_entity]))
    visited[start_entity] = (0, [start_entity])

    while queue:
        cur, hops, path = queue.popleft()
        if hops >= max_hops:
            continue
        for nb, et in adj.get(cur, []):
            if nb not in visited:
                np = path + ["%s(%s)" % (nb, et)]
                visited[nb] = (hops + 1, np)
                queue.append((nb, hops + 1, np))

    if start_entity in visited:
        del visited[start_entity]
    return visited


# ── 严重度判定 ─────────────────────────────────────────────

def assign_severity(node, hop):
    """严重度判定: BLOCKER 仅当直接变更宪法实体自身"""
    is_const = node.get("is_constitutional", False)
    ntype = node.get("type", "")
    cat = node.get("category", "")
    layer = node.get("layer", "L3")

    # BLOCKER: 直接修改宪法级概念自身
    if hop == 0 and is_const:
        return "BLOCKER"

    if hop == 0:
        if cat == "character":
            return "CRITICAL"
        if layer == "L0":
            return "CRITICAL"
        # L1/L2 概念定义变更
        return "HIGH"

    if hop == 1:
        # 宪法邻居 → CRITICAL (需审查但不阻塞)
        if is_const:
            return "CRITICAL"
        if ntype == "skeleton":
            return "HIGH"
        if ntype == "chapter":
            return "MEDIUM"
        if ntype == "concept" and cat == "character":
            return "CRITICAL"
        if ntype == "concept":
            return "HIGH"
        return "MEDIUM"

    if hop == 2:
        if ntype in ("chapter", "foreshadow"):
            return "MEDIUM"
        if ntype == "concept" and cat == "character":
            return "HIGH"
        if ntype == "concept":
            return "MEDIUM"
        return "MEDIUM"

    return "LOW"


def describe_impact(node, hop, change_info):
    ntype = node.get("type", "concept")
    label = node.get("label", node.get("_name", ""))
    cat = node.get("category", "")
    field = change_info.get("field", "")
    old = change_info.get("old", "")
    new = change_info.get("new", "")

    if hop == 0:
        # 变更实体自身
        if cat == "character":
            return "%s.%s %s->%s — 角色设定值变更，需更新档案和出场章节" % (label, field, old, new)
        if is_constitutional(node):
            return "%s.%s %s->%s — 宪法级原则变更，全项目需重审" % (label, field, old, new)
        if cat == "worldbuilding":
            return "%s.%s %s->%s — 世界观设定变更，需检查一致性" % (label, field, old, new)
        return "%s.%s %s->%s — 概念变更" % (label, field, old, new)

    if ntype == "concept":
        if cat == "character":
            return "角色 %s 与变更实体关联，需检查行为锚点和互动" % label
        if cat == "worldbuilding":
            return "世界观 %s 与变更实体关联，需检查一致性" % label
        if cat == "principle":
            return "核心原则 %s 受变更影响，需重审推导链" % label
        return "概念 %s 需审查" % label
    if ntype == "chapter":
        return "章节 %s 引用变更实体，内容可能需调整" % label
    if ntype == "skeleton":
        return "骨架 %s 引用变更实体，规划可能需调整" % label
    if ntype == "foreshadow":
        return "伏笔追踪引用变更实体，相关伏笔需审查"
    if ntype == "file":
        return "档案 %s 定义或引用变更实体" % label
    return "%s 受影响" % label


# ── 输出格式化 ─────────────────────────────────────────────

SEVERITY_ORDER = ["BLOCKER", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
SEVERITY_TAGS = {
    "BLOCKER": "[BLOCKER]",
    "CRITICAL": "[CRITICAL]",
    "HIGH": "[HIGH]   ",
    "MEDIUM": "[MEDIUM] ",
    "LOW": "[LOW]    ",
}
TYPE_LABEL = {
    "concept": "概念", "chapter": "章节",
    "skeleton": "骨架", "foreshadow": "伏笔", "file": "档案",
}


def format_output(change_info, affected, nodes):
    entity = change_info.get("entity", "?")
    field = change_info.get("field", "?")
    old_val = change_info.get("old", "?")
    new_val = change_info.get("new", "?")

    print()
    print("=== 涟漪传播 === 变更: %s.%s = %s -> %s" % (entity, field, old_val, new_val))
    print()

    if not affected:
        print("(无涟漪 - 此变更不影响其他实体)")
        return 0

    by_sev = {s: [] for s in SEVERITY_ORDER}
    hop0_item = None  # 变更实体自身，始终排最前

    for node_id, (hop, path) in affected.items():
        node = nodes.get(node_id, {})
        sev = assign_severity(node, hop)
        desc = describe_impact(node, hop, change_info)

        if node.get("type") in ("chapter", "skeleton", "foreshadow", "file"):
            dp = node.get("path", node_id)
        else:
            dp = node_id
        if PROJECT_ROOT in str(dp):
            dp = os.path.relpath(dp, PROJECT_ROOT)

        layer = node.get("layer", "?")
        tl = TYPE_LABEL.get(node.get("type", "concept"), node.get("type", "concept"))

        item = {
            "path": str(dp), "desc": desc, "hop": hop,
            "layer": layer, "type_label": tl,
        }

        if hop == 0:
            hop0_item = (sev, item)
        else:
            by_sev[sev].append(item)

    # 先输出 hop=0（变更实体自身）
    if hop0_item:
        sev, it = hop0_item
        tag = SEVERITY_TAGS[sev]
        print("%s %s %s — %s" % (tag, it["layer"], it["type_label"], it["desc"]))
        print("         %s" % it["path"])
        print()

    for sev in SEVERITY_ORDER:
        items = by_sev[sev]
        if not items:
            continue
        items.sort(key=lambda x: x["hop"])
        for it in items:
            tag = SEVERITY_TAGS[sev]
            print("%s %s %s — %s" % (tag, it["layer"], it["type_label"], it["desc"]))
            print("         %s" % it["path"])

    print()
    counts = {s: len(by_sev[s]) for s in SEVERITY_ORDER}
    if hop0_item:
        counts[hop0_item[0]] += 1
    total = sum(counts.values())
    parts = ["%s=%d" % (s, counts[s]) for s in SEVERITY_ORDER if counts[s] > 0]
    print("受影响实体: %d 个 | %s" % (total, " ".join(parts)))

    if counts["BLOCKER"] > 0:
        print("门禁: BLOCKER %d 个 - 必须解决后继续" % counts["BLOCKER"])
        return 1
    elif counts["CRITICAL"] > 0:
        print("门禁: %d CRITICAL - 建议解决后继续" % counts["CRITICAL"])
        return 0
    else:
        print("门禁: PASS")
        return 0


# ── 主函数 ────────────────────────────────────────────────

def propagate(entity, field, old_val, new_val):
    if not os.path.exists(REGISTRY_PATH):
        print("[ripple] 错误: 找不到概念注册表 %s" % REGISTRY_PATH, file=sys.stderr)
        sys.exit(1)

    concepts = parse_concept_registry(REGISTRY_PATH)
    nodes, edges = build_graph(concepts, PROJECT_ROOT)
    mention_edges = scan_project_files(nodes, concepts, PROJECT_ROOT)
    edges.extend(mention_edges)

    if entity not in nodes:
        print("[ripple] 错误: 实体 \"%s\" 不在概念注册表中" % entity, file=sys.stderr)
        print("[ripple] 可用实体: %s" % ", ".join(sorted(concepts.keys())), file=sys.stderr)
        sys.exit(1)

    affected = bfs_propagate(nodes, edges, entity, max_hops=4)

    # 变更实体自身始终出现在结果中（hop=0）
    affected[entity] = (0, [entity])

    change_info = {"entity": entity, "field": field, "old": old_val, "new": new_val}
    return format_output(change_info, affected, nodes)


# ── CLI ────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="亚文化创作引擎 · 涟漪传播",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  python ripple.py --change \"林岳:combat_power:3500->2500\"\n"
               "  python ripple.py --change \"严峰:divine_range:50->30\"\n"
               "  python ripple.py --change \"天地夺灵大阵:周期:73->60\"")
    parser.add_argument("--change", type=str,
                        help="变更描述: \"实体:字段:旧值->新值\"")
    args = parser.parse_args()

    if args.change:
        parts = args.change.split(":")
        if len(parts) == 3 and "->" in parts[2]:
            entity = parts[0]
            field = parts[1]
            vals = parts[2].split("->")
            old = vals[0]
            new = vals[1]
            exit_code = propagate(entity, field, old, new)
            sys.exit(exit_code)
        else:
            print("格式错误。正确格式: --change \"实体:字段:旧值->新值\"")
            print("示例: --change \"林岳:combat_power:3500->2500\"")
            sys.exit(1)
    else:
        parser.print_help()











