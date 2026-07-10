"""
init_db.py - SQLite 数据库初始化 + 填充

用法:
  python init_db.py                        # 完整初始化 (建表 + 填充)
  python init_db.py --check-only           # 仅检查 DB 是否存在
  python init_db.py --force                # 强制重建 (删除旧 DB)

数据源:
  schema/schema.sql                        -> DDL (20 表)
  创作正文/状态/S10_概念注册表.yaml         -> concept / axiom 表
  创作正文/章节规划/卷一/第*章.md           -> chapter / scene 表
  创作正文/剧情/全卷骨架_卷*.md             -> volume 表

输出: 创作正文/状态/project.db
"""
import argparse, io, os, re, sqlite3, sys, json

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def _root():
    d = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(d))

# ---- DDL ----
def _ddl(conn, root):
    p = os.path.join(root, "schema", "schema.sql")
    if not os.path.exists(p):
        print("[init_db] schema.sql 缺失"); return
    with open(p, encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    n = len(cur.fetchall())
    print(f"  [DDL] {n} 张表")

# ---- volumes (先于 chapters, 因为 FK) ----
def _volumes(conn, root):
    d = os.path.join(root, "创作正文", "剧情")
    if not os.path.isdir(d): return
    vmap = {"一":1,"二":2,"三":3,"四":4,"五":5,"1":1,"2":2,"3":3,"4":4,"5":5}
    n = 0
    for fn in sorted(os.listdir(d)):
        m = re.match(r"全卷骨架_卷([一二三四五1-5])\.md", fn)
        if not m: continue
        vn = vmap.get(m.group(1), 0)
        if not vn: continue
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            t = f.read()
        nm = f"卷{vn}"
        rm = re.search(r"卷名[：:]\s*(.+?)(?:\n|$)", t)
        if rm: nm = rm.group(1).strip()
        cr = ""
        cm = re.search(r"(\d+)[−\-~](\d+)\s*章", t)
        if cm: cr = f"{cm.group(1)}-{cm.group(2)}"
        try:
            conn.execute("INSERT OR IGNORE INTO volume (num, title, chapter_count, theme) VALUES (?,?,?,?)",
                         (vn, nm, int(cr.split("-")[-1]) if cr and "-" in cr else 0, ""))
            n += 1
        except: pass
    conn.commit()
    print(f"  [volume] {n} 卷")

# ---- concepts + axioms ----
def _concepts(conn, root):
    p = os.path.join(root, "创作正文", "状态", "S10_概念注册表.yaml")
    if not os.path.exists(p):
        print("[init_db] 注册表缺失"); return
    try:
        import yaml
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except ImportError:
        data = _yaml_pure(p)
    if not data or "concepts" not in data: return

    cc, ac = 0, 0
    for name, info in data["concepts"].items():
        cat = info.get("category", "term")
        can = info.get("canonical", "")
        dfn = info.get("defined_in", "")
        aliases = json.dumps(info.get("deprecated_aliases", []), ensure_ascii=False)
        try:
            conn.execute("INSERT OR IGNORE INTO concept (id, name, category, canonical_definition, deprecated_aliases, status) VALUES (?,?,?,?,?,'active')",
                         (name, name, cat, can, aliases))
            cc += 1
        except: pass
        if cat == "principle":
            try:
                conn.execute("INSERT OR IGNORE INTO axiom (name, statement) VALUES (?,?)", (name, can))
                ac += 1
            except: pass
    conn.commit()
    print(f"  [concept] {cc} 个 · [axiom] {ac} 条")

def _yaml_pure(path):
    """纯 Python YAML 解析。"""
    with open(path, encoding="utf-8") as f:
        ls = f.readlines()
    r = {"concepts": {}}
    cur, in_a, in_k = None, False, False
    for l in ls:
        s = l.rstrip()
        if not s or s.startswith("#"): continue
        ind = len(l) - len(l.lstrip())
        if ind == 2 and ":" in s:
            k = s.split(":")[0].strip().strip('"\'')
            if k != "concepts":
                cur = k; r["concepts"][cur] = {"category":"term","deprecated_aliases":[],"keywords":[]}
                in_a = in_k = False
        elif ind == 4:
            if s.startswith("category:"): 
                if cur: r["concepts"][cur]["category"] = s.split(":")[1].strip().strip('"\'')
            elif s.startswith("canonical:"): 
                if cur: r["concepts"][cur]["canonical"] = s.split(":",1)[1].strip().strip('"\'')
            elif s.startswith("defined_in:"): 
                if cur: r["concepts"][cur]["defined_in"] = s.split(":",1)[1].strip().strip('"\'')
            elif s.startswith("deprecated_aliases:"): in_a, in_k = True, False
            elif s.startswith("keywords:"): in_k, in_a = True, False
            elif in_a and s.startswith("- "):
                a = s[2:].strip().strip('"\'')
                if cur and a: r["concepts"][cur]["deprecated_aliases"].append(a)
            elif in_k and s.startswith("- "):
                kw = s[2:].strip().strip('"\'')
                if cur and kw: r["concepts"][cur]["keywords"].append(kw)
            else: in_a = in_k = False
        else: in_a = in_k = False
    return r

# ---- chapters + scenes + foreshadow ----
_CP = re.compile(r"第(\d+)章")
_TLP = re.compile(r"恒元年月[：:]\s*([^\n]+)")
_TTP = re.compile(r"^# 第(\d+)章[：:]\s*(.+)", re.MULTILINE)
_FP = re.compile(r"\b(F\d{2,3})\b")

def _chapters(conn, root):
    d = os.path.join(root, "创作正文", "章节规划", "卷一")
    if not os.path.isdir(d):
        print("[init_db] 章节目录缺失"); return
    cc, sc, fc = 0, 0, 0
    md_files = []
    for dirpath, _dirnames, filenames in os.walk(d):
        for fn in filenames:
            if fn.endswith(".md"):
                md_files.append((dirpath, fn))
    md_files.sort(key=lambda x: x[1])
    for dirpath, fn in md_files:
        m = _CP.search(fn)
        if not m: continue
        cn = int(m.group(1))
        with open(os.path.join(dirpath, fn), encoding="utf-8") as f:
            t = f.read()
        title = fn.replace(".md", "")
        tm = _TTP.search(t)
        if tm: title = tm.group(2).strip()
        tl = ""
        tlm = _TLP.search(t)
        if tlm: tl = tlm.group(1).strip()
        try:
            conn.execute("INSERT OR IGNORE INTO chapter (num, title, volume, timeline) VALUES (?,?,?,?)",
                         (cn, title, 1, tl))
            cc += 1
        except: pass
        # scenes
        ss = re.search(r"## 关键场景.*?(?=\n## |\Z)", t, re.DOTALL)
        if ss:
            for row in ss.group(0).split("\n"):
                if row.startswith("|") and not row.startswith("|--") and not row.startswith("| 序号"):
                    cols = [c.strip() for c in row.split("|") if c.strip()]
                    if len(cols) >= 4:
                        sid = f"ch{cn}_s{cols[0]}"
                        try:
                            conn.execute("INSERT OR IGNORE INTO scene (chapter_num, seq, location, time_of_day, characters) VALUES (?,?,?,?,'')",
                                         (cn, int(cols[0]) if cols[0].isdigit() else sc+1, cols[1] if len(cols)>1 else "", cols[2] if len(cols)>2 else ""))
                            sc += 1
                        except: pass
        # foreshadows
        seen = set()
        for fm in _FP.finditer(t):
            fid = fm.group(1)
            if fid in seen:
                continue
            seen.add(fid)
            # extract surrounding line for content
            ctx = ""
            pos = fm.start()
            line_start = t.rfind("\n", 0, pos) + 1
            line_end = t.find("\n", pos)
            if line_end == -1:
                line_end = len(t)
            ctx = t[line_start:line_end].strip()[:200]
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO foreshadow (id, name, type, introduced_ch, status, content) VALUES (?,?,\"事件\",?,\"open\",?)",
                    (fid, fid, cn, ctx))
                fc += 1
            except: pass
    conn.commit()
    print(f"  [chapter] {cc} 章 · [scene] {sc} 场景 · [foreshadow] {fc} 伏笔引用")

# ---- verify ----
def _verify(conn):
    for tbl in ["concept","axiom","chapter","scene","foreshadow","volume"]:
        try:
            cur = conn.execute(f"SELECT COUNT(*) FROM {tbl}")
            print(f"  {tbl}: {cur.fetchone()[0]} 行")
        except: print(f"  {tbl}: —")

# ---- main ----
def main(check_only=False, force=False):
    root = _root()
    dbp = os.path.join(root, "创作正文", "状态", "project.db")
    if check_only:
        sys.exit(0 if os.path.exists(dbp) else 1)
    if force and os.path.exists(dbp):
        os.remove(dbp); print("[init_db] 旧 DB 已删除")
    if os.path.exists(dbp):
        print(f"[init_db] DB 已存在: {dbp}\n  用 --force 重建")
        sys.exit(0)
    os.makedirs(os.path.dirname(dbp), exist_ok=True)
    conn = sqlite3.connect(dbp)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=OFF")
    print(f"[init_db] 项目: {root}")
    print(f"[init_db] 目标: {dbp}\n")
    _ddl(conn, root)
    _volumes(conn, root)
    _concepts(conn, root)
    _chapters(conn, root)
    print()
    _verify(conn)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.close()
    print(f"\n[init_db] 完成 -> {dbp}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="SQLite DB init")
    p.add_argument("--check-only", action="store_true")
    p.add_argument("--force", action="store_true")
    a = p.parse_args()
    main(a.check_only, a.force)