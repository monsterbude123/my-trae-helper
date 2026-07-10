#!/usr/bin/env python3
"""
query-index.py — 文档索引查询工具 (SQLite)

五种检索模式:
  精确匹配  → python query-index.py "Agent 层"
  模糊匹配  → python query-index.py --fuzzy "agent通信"
  语义搜索  → python query-index.py --semantic "多Agent怎么发消息"
  文件浏览  → python query-index.py --file ARCHITECTURE.md

环境变量:
  DOCMAP_EXTRA_DOCS_DIRS  额外文档目录（分号/逗号分隔），搜索时跨所有目录检索
"""

import argparse
import json
import re
import sqlite3
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

# Windows cmd 编码适配
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DOCMAP_DIR = ".docmap"
DB_NAME = "docmap.db"


# ── Embedding 配置 ──────────────────────────────────────────

def _load_dotenv() -> dict:
    try:
        script_dir = Path(__file__).resolve().parent
        repo_root = script_dir.parent.parent.parent
        env_path = repo_root / ".env"
        if not env_path.exists():
            return {}
        config: dict = {}
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                config[k.strip()] = v.strip().strip("\"'")
        return config
    except Exception:
        return {}


def _create_embedding_function(config: dict):
    import chromadb
    from chromadb.utils import embedding_functions
    provider = config.get("DOCMAP_EMBEDDING_PROVIDER", "sentence_transformers")
    if provider == "openai":
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=config.get("DOCMAP_EMBEDDING_API_KEY", "ollama"),
            api_base=config.get("DOCMAP_EMBEDDING_API_BASE", "http://localhost:11434/v1"),
            model_name=config.get("DOCMAP_EMBEDDING_MODEL", "nomic-embed-text"),
        )
    if provider == "chroma_default":
        return embedding_functions.DefaultEmbeddingFunction()
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.get("DOCMAP_EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5"),
    )


# ── SQLite 数据加载 ───────────────────────────────────────────

def load_index_from_db(docs_dir: Path) -> dict[str, Any]:
    """从 SQLite 加载完整的索引结构（兼容旧版 .docindex.json 格式）。"""
    db_path = docs_dir / DOCMAP_DIR / DB_NAME
    if not db_path.exists():
        print(f"[ERROR] 索引数据库不存在: {db_path}")
        print("  请先运行 build-index.py 构建索引。")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    result: dict[str, Any] = {"files": {}}
    cur = conn.execute("SELECT path, source_dir, summary, mtime, size FROM files")
    for row in cur.fetchall():
        rel_path = row["path"]
        source_dir = row["source_dir"]
        hcur = conn.execute(
            "SELECT line, end_line, level, title, breadcrumb FROM headings "
            "WHERE file_path=? AND source_dir=? ORDER BY line",
            (rel_path, source_dir),
        )
        headings = [{
            "line": h["line"], "end_line": h["end_line"],
            "level": h["level"], "title": h["title"],
            "breadcrumb": h.get("breadcrumb", h["title"]),
        } for h in hcur.fetchall()]

        total_lines = headings[-1]["end_line"] if headings else 0
        result["files"][rel_path] = {
            "path": f"docs/{rel_path}",
            "total_lines": total_lines,
            "headings": headings,
            "source_dir": source_dir,
        }

    conn.close()
    return result


def flatten_headings(index: dict) -> list[dict]:
    """将嵌套的 files → headings 平铺为列表。"""
    results = []
    for rel_path, data in index.get("files", {}).items():
        source_dir = data.get("source_dir")
        for h in data.get("headings", []):
            entry: dict[str, Any] = {
                "file": rel_path,
                "line": h["line"],
                "end_line": h.get("end_line", 0),
                "level": h["level"],
                "title": h["title"],
                "breadcrumb": h.get("breadcrumb", h["title"]),
            }
            if source_dir:
                entry["source_dir"] = source_dir
            results.append(entry)
    return results


def load_headings_flat(docs_dir: Path) -> list[dict]:
    """直接从 SQLite 查询平铺标题列表，无需加载整棵树。"""
    db_path = docs_dir / DOCMAP_DIR / DB_NAME
    if not db_path.exists():
        return []
    conn = sqlite3.connect(str(db_path))
    cur = conn.execute(
        "SELECT h.file_path, h.line, h.end_line, h.level, h.title, h.breadcrumb, f.source_dir "
        "FROM headings h JOIN files f ON h.file_path = f.path AND h.source_dir = f.source_dir "
        "ORDER BY h.file_path, h.line"
    )
    results = []
    for row in cur.fetchall():
        results.append({
            "file": row[0], "line": row[1], "end_line": row[2],
            "level": row[3], "title": row[4], "breadcrumb": row[5] or row[4],
            "source_dir": row[6] or "",
        })
    conn.close()
    return results


# ── 精确匹配 ──────────────────────────────────────────────────

def search_exact(headings: list[dict], query: str, level: int = 0) -> list[dict]:
    results = []
    q_lower = query.lower()
    for h in headings:
        if level and h["level"] != level:
            continue
        if q_lower in h["title"].lower():
            results.append({"entry": h, "score": 1.0, "method": "exact"})
    return results


# ── 模糊匹配 ──────────────────────────────────────────────────

def search_fuzzy(headings: list[dict], query: str, level: int = 0) -> list[dict]:
    results = []
    try:
        from rapidfuzz import fuzz
        scorer = lambda q, t: fuzz.partial_ratio(q.lower(), t.lower()) / 100.0
        method = "rapidfuzz"
    except ImportError:
        scorer = lambda q, t: SequenceMatcher(None, q.lower(), t.lower()).ratio()
        method = "difflib"

    for h in headings:
        if level and h["level"] != level:
            continue
        search_text = h.get("breadcrumb", h["title"])
        score = scorer(query, search_text)
        if score > 0.3:
            results.append({"entry": h, "score": score, "method": method})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


# ── 语义搜索 ──────────────────────────────────────────────────

def _get_embedding_model(config: dict) -> tuple:
    """加载 embedding 模型，返回 (embed_fn, dim)。"""
    provider = config.get("DOCMAP_EMBEDDING_PROVIDER", "sentence_transformers")
    model_name = config.get("DOCMAP_EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")

    if provider == "openai":
        import requests

        api_base = config.get("DOCMAP_EMBEDDING_API_BASE", "http://localhost:11434/v1")
        api_key = config.get("DOCMAP_EMBEDDING_API_KEY", "ollama")

        def _openai_embed(texts: list[str]) -> list[list[float]]:
            resp = requests.post(
                f"{api_base.rstrip('/')}/embeddings",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": model_name, "input": texts},
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            # 按 index 排序
            sorted_data = sorted(data["data"], key=lambda x: x["index"])
            return [item["embedding"] for item in sorted_data]

        # 先发一个请求获取 dim
        try:
            test_vec = _openai_embed(["test"])
            dim = len(test_vec[0])
        except Exception:
            dim = 768
        return _openai_embed, dim

    # 默认：sentence_transformers 本地模型
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_name, trust_remote_code=True)
        dim = model.get_sentence_embedding_dimension()
        return lambda texts: model.encode(texts, show_progress_bar=False).tolist(), dim
    except Exception as e:
        print(f"[WARN] 加载本地模型失败 ({e})，回退到 ChromaDB sentence_transformers")
        # 回退：尝试去除 BAAI/ 前缀
        try:
            fallback_name = model_name.replace("BAAI/", "")
            model = SentenceTransformer(fallback_name, trust_remote_code=True)
            dim = model.get_sentence_embedding_dimension()
            return lambda texts: model.encode(texts, show_progress_bar=False).tolist(), dim
        except Exception as e2:
            print(f"[ERROR] 所有模型加载失败: {e2}")
            raise

def _search_zvec(query: str, level: int, docs_dir: Path) -> list[dict] | None:
    """用 Zvec 做语义搜索。"""
    zvec_dir = docs_dir / DOCMAP_DIR / "zvec"
    if not zvec_dir.exists():
        return None

    config = _load_dotenv()
    embed_fn, dim = _get_embedding_model(config)

    try:
        import zvec
        collection = zvec.open(str(zvec_dir))
    except Exception as e:
        print(f"[WARN] Zvec 打开失败: {e}")
        return None

    try:
        query_vec = embed_fn([query])[0]
    except Exception as e:
        print(f"[WARN] 向量化查询失败: {e}")
        return None

    try:
        results = collection.query(
            zvec.Query(field_name="embedding", vector=query_vec),
            topk=30,
        )
    except Exception as e:
        print(f"[WARN] Zvec 查询执行失败: {e}")
        return None

    output = []
    for r in results:
        meta = r.fields if hasattr(r, 'fields') else {}
        if level and meta.get("level", 0) != level:
            continue
        score = r.score if hasattr(r, 'score') and r.score is not None else 0
        if score < 0.3:
            continue
        output.append({
            "entry": {
                "file": meta.get("file", ""),
                "line": meta.get("line", 0),
                "end_line": meta.get("end_line", 0),
                "level": meta.get("level", 0),
                "title": meta.get("title", ""),
                "breadcrumb": meta.get("breadcrumb", ""),
                "source_dir": meta.get("source_dir", ""),
            },
            "score": score,
            "method": "zvec",
        })

    output.sort(key=lambda x: x["score"], reverse=True)
    return output


def _search_chromadb_fast(query: str, level: int, docs_dir: Path) -> list[dict] | None:
    if not (docs_dir / DOCMAP_DIR / "chroma").exists():
        return None
    try:
        ef = _create_embedding_function(_load_dotenv())
        import chromadb
        from chromadb.config import Settings
        client = chromadb.PersistentClient(
            path=str(docs_dir / DOCMAP_DIR / "chroma"),
            settings=Settings(anonymized_telemetry=False),
        )
        collection = client.get_collection("doc_headings", embedding_function=ef)
    except Exception:
        return None

    try:
        where_filter = {"level": level} if level else None
        results = collection.query(query_texts=[query], n_results=30, where=where_filter)
    except Exception:
        return None

    output = []
    ids = results.get("ids", [[]])[0]
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    for uid, distance, meta in zip(ids, distances, metadatas):
        score = round(1.0 - float(distance), 4)
        if score < 0.3:
            continue
        output.append({
            "entry": {
                "file": meta.get("file", ""),
                "line": meta.get("line", 0),
                "end_line": meta.get("end_line", 0),
                "level": meta.get("level", 0),
                "title": meta.get("title", ""),
                "breadcrumb": meta.get("breadcrumb", ""),
                "source_dir": meta.get("source_dir", ""),
            },
            "score": score,
            "method": "chromadb",
        })

    output.sort(key=lambda x: x["score"], reverse=True)
    return output


def _search_tfidf(headings: list[dict], query: str, level: int = 0) -> list[dict]:
    try:
        import jieba
        tokenize = lambda s: list(jieba.cut(s))
    except ImportError:
        tokenize = lambda s: re.split(r"\s+", s)

    import math

    corpus: list[str] = []
    valid_indices: list[int] = []
    for i, h in enumerate(headings):
        if level and h["level"] != level:
            continue
        corpus.append(h.get("breadcrumb", h["title"]))
        valid_indices.append(i)

    if not corpus:
        return []

    tokenized = [tokenize(doc) for doc in corpus]
    query_tokens = tokenize(query)

    N = len(corpus)
    idf: dict[str, float] = {}
    all_tokens = set(t for tokens in tokenized for t in tokens)
    for token in all_tokens:
        df = sum(1 for tokens in tokenized if token in tokens)
        idf[token] = math.log((N + 1) / (df + 1)) + 1

    query_vec: dict[str, float] = {}
    for t in query_tokens:
        query_vec[t] = query_vec.get(t, 0) + 1

    results = []
    for idx, tokens in enumerate(tokenized):
        doc_vec: dict[str, float] = {}
        for t in tokens:
            doc_vec[t] = doc_vec.get(t, 0) + 1

        dot = 0.0
        q_norm = 0.0
        d_norm = 0.0
        for t, q_tf in query_vec.items():
            q_w = q_tf * idf.get(t, 0)
            d_w = doc_vec.get(t, 0) * idf.get(t, 0)
            dot += q_w * d_w
            q_norm += q_w * q_w
        for t, d_tf in doc_vec.items():
            d_w = d_tf * idf.get(t, 0)
            d_norm += d_w * d_w

        denom = math.sqrt(q_norm) * math.sqrt(d_norm)
        score = dot / denom if denom > 0 else 0.0

        if score > 0.05:
            h = headings[valid_indices[idx]]
            results.append({"entry": h, "score": round(score, 4), "method": "tfidf"})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


# ── 文件浏览 ──────────────────────────────────────────────────

def browse_file_from_db(docs_dir: Path, filename: str) -> None:
    """从 SQLite 查询单个文件的章节结构。"""
    conn = sqlite3.connect(str(docs_dir / DOCMAP_DIR / DB_NAME))
    conn.row_factory = sqlite3.Row

    # 模糊匹配文件名
    cur = conn.execute(
        "SELECT path, source_dir FROM files WHERE path LIKE ?",
        (f"%{filename}%",)
    )
    rows = cur.fetchall()
    if not rows:
        # 再试一次精确匹配
        cur = conn.execute("SELECT path, source_dir FROM files WHERE path = ?", (filename,))
        rows = cur.fetchall()

    if not rows:
        print(f"[WARN] 未找到匹配文件: {filename}")
        cur = conn.execute("SELECT path FROM files ORDER BY path LIMIT 50")
        print("\n可用文件（前 50）:")
        for r in cur.fetchall():
            print(f"  - {r[0]}")
        conn.close()
        return

    for row in rows:
        rel_path = row["path"]
        source_dir = row["source_dir"]
        hcur = conn.execute(
            "SELECT line, end_line, level, title, breadcrumb FROM headings "
            "WHERE file_path=? AND source_dir=? ORDER BY line",
            (rel_path, source_dir),
        )
        headings = hcur.fetchall()

        total_lines = headings[-1]["end_line"] if headings else 0
        print(f"\n{'=' * 60}")
        print(f"  [{rel_path}] ({total_lines} lines, {len(headings)} headings)")
        print(f"{'=' * 60}")
        for h in headings:
            indent = "  " * (h["level"] - 1)
            prefix = "#" * h["level"]
            line_range = f"L{h['line']}-L{h['end_line']}"
            print(f"{indent}{prefix} {h['title']}  [{line_range}]")

    conn.close()


# ── 格式化输出 ────────────────────────────────────────────────

def format_results(results: list[dict], top_n: int, as_json: bool) -> None:
    if not results:
        print("(无匹配结果)")
        return

    results = results[:top_n]

    if as_json:
        output = []
        for r in results:
            entry = r["entry"]
            output.append({
                "file": entry["file"], "line": entry["line"],
                "end_line": entry.get("end_line", 0),
                "score": round(r["score"], 4), "method": r.get("method", "unknown"),
                "title": entry["title"],
                "breadcrumb": entry.get("breadcrumb", entry["title"]),
                "level": entry["level"],
            })
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    for r in results:
        entry = r["entry"]
        pct = int(r["score"] * 100)
        indent = "  " * (entry["level"] - 1)
        line_range = f"L{entry['line']}-L{entry.get('end_line', '?')}"
        print(f"  {entry['file']:<50}  {line_range:<16}  {pct:>3}%  {indent}{entry['title']}")


# ── GRAB 模式 ─────────────────────────────────────────────────

def grab_results(results: list[dict], top_n: int, docs_dir: Path, context_lines: int = 3) -> None:
    if not results:
        print("(无匹配结果)")
        return

    results = results[:top_n]
    for r in results:
        entry = r["entry"]
        source_dir = entry.get("source_dir")
        if source_dir:
            filepath = Path(source_dir) / entry["file"]
        else:
            filepath = docs_dir / entry["file"]

        if not filepath.exists():
            print(f"  [{entry['file']}] (文件不存在)")
            continue
        try:
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            print(f"  [{entry['file']}] (无法读取)")
            continue

        line_start = max(0, entry["line"] - 1 - context_lines)
        line_end = min(len(lines), entry.get("end_line", entry["line"]) + context_lines)

        print(f"\n{'=' * 60}")
        print(f"  ## {entry['file']} L{entry['line']}-L{entry.get('end_line', '?')} (score: {r['score']:.2f})")
        print()

        for i in range(line_start, line_end):
            line_no = i + 1
            prefix = "  >" if context_lines and (i < entry["line"] - 1 or i >= entry.get("end_line", entry["line"])) else "   "
            print(f"  L{line_no:<5}{prefix} {lines[i].rstrip()}")

    print(f"\n{'=' * 60}")


# ── LOOKUP 模式 ───────────────────────────────────────────────

def search_lookup_from_db(keyword: str, docs_dir: Path, top_n: int, as_json: bool) -> None:
    """从 SQLite 查找匹配标题的关键词。"""
    db_path = docs_dir / DOCMAP_DIR / DB_NAME
    if not db_path.exists():
        return  # 静默跳过不存在的目录

    conn = sqlite3.connect(str(db_path))
    pattern = f"%{keyword}%"
    cur = conn.execute(
        "SELECT DISTINCT h.file_path, h.title, h.line, f.source_dir "
        "FROM headings h JOIN files f ON h.file_path = f.path AND h.source_dir = f.source_dir "
        "WHERE h.title LIKE ? ORDER BY h.file_path, h.line LIMIT ?",
        (pattern, top_n),
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return

    matches = [{
        "file": r[0], "title": r[1], "line": r[2],
        "source_dir": r[3] or "", "source": "sqlite",
    } for r in rows]

    if as_json:
        print(json.dumps(matches, ensure_ascii=False, indent=2))
        return

    for m in matches:
        print(f"  [sqlite] {m['file']:<50} L{m['line']:<8} {m['title']}")


# ── 主流程 ────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="文档索引查询工具 (SQLite)")
    parser.add_argument("query", type=str, nargs="?", default=None,
                        help="精确搜索关键词（标题包含）")
    parser.add_argument("--fuzzy", type=str, default=None, help="模糊搜索")
    parser.add_argument("--semantic", type=str, default=None, help="语义搜索（自然语言描述）")
    parser.add_argument("--file", type=str, default=None, help="浏览指定文件的所有章节")
    parser.add_argument("--grab", type=str, default=None,
                        help="GRAB 模式：搜索后直接输出匹配章节的正文内容")
    parser.add_argument("--lookup", type=str, default=None, help="关键词匹配查询")
    parser.add_argument("--level", type=int, default=0, help="只搜索指定标题层级")
    parser.add_argument("--top", type=int, default=15, help="最多返回 N 条结果")
    parser.add_argument("--json", action="store_true", default=False, help="JSON 输出")
    parser.add_argument("--context", type=int, default=3, help="--grab 模式上下文行数")
    parser.add_argument("--docs-dir", type=str, default=None, help="文档目录路径")
    args = parser.parse_args()

    # 确定 docs 目录
    if args.docs_dir:
        docs_dir = Path(args.docs_dir).resolve()
    else:
        script_dir = Path(__file__).resolve().parent
        repo_root = script_dir.parent.parent.parent
        docs_dir = repo_root / "docs"
        if not docs_dir.exists():
            cwd_docs = Path.cwd() / "docs"
            if cwd_docs.exists():
                docs_dir = cwd_docs
            else:
                for parent in Path.cwd().parents:
                    candidate = parent / "docs"
                    if candidate.exists() and candidate.is_dir():
                        docs_dir = candidate
                        break

    if not docs_dir.exists():
        print(f"[ERROR] 文档目录不存在: {docs_dir}")
        sys.exit(1)

    # 构建 docs_dirs 列表
    docs_dirs = [docs_dir]
    config = _load_dotenv()
    extra_raw = config.get("DOCMAP_EXTRA_DOCS_DIRS", "")
    if extra_raw:
        for d in re.split(r"[;,]", extra_raw):
            d = d.strip()
            if not d:
                continue
            p = Path(d).resolve()
            if p.exists() and p.is_dir():
                docs_dirs.append(p)
            else:
                print(f"[WARN] DOCMAP_EXTRA_DOCS_DIRS 目录不存在: {p}")

    # 文件浏览模式
    if args.file:
        browse_file_from_db(docs_dir, args.file)
        return

    # LOOKUP 模式
    if args.lookup:
        db_path = docs_dir / DOCMAP_DIR / DB_NAME
        if not db_path.exists():
            print("[INFO] 无可用索引，请先运行 build-index.py 构建索引。")
            return
        search_lookup_from_db(args.lookup, docs_dir, args.top, args.json)
        return

    # 确定查询模式
    if args.grab:
        mode, query_text = "grab", args.grab
    elif args.semantic:
        mode, query_text = "semantic", args.semantic
    elif args.fuzzy:
        mode, query_text = "fuzzy", args.fuzzy
    elif args.query:
        mode, query_text = "exact", args.query
    else:
        parser.print_help()
        sys.exit(1)

    # ── 语义搜索（Zvec → ChromaDB → TF-IDF 降级） ──
    if mode == "semantic":
        sr = _search_zvec(query_text, args.level, docs_dir)
        if sr:
            format_results(sr, args.top, args.json)
            return
        sr = _search_chromadb_fast(query_text, args.level, docs_dir)
        if sr:
            format_results(sr, args.top, args.json)
            return
        # 降级 TF-IDF
        headings = load_headings_flat(docs_dir)
        if not headings:
            print("[INFO] 无可用索引")
            return
        results = _search_tfidf(headings, query_text, args.level)
        format_results(results, args.top, args.json)
        return

    # grab / fuzzy / exact
    all_headings = load_headings_flat(docs_dir)

    if not all_headings:
        print("[INFO] 无可用索引，请先运行 build-index.py 构建索引。")
        return

    if mode == "grab":
        results = search_fuzzy(all_headings, query_text, args.level)
        grab_results(results, args.top, docs_dir, args.context)
    elif mode == "exact":
        results = search_exact(all_headings, query_text, args.level)
        format_results(results, args.top, args.json)
    elif mode == "fuzzy":
        results = search_fuzzy(all_headings, query_text, args.level)
        format_results(results, args.top, args.json)


if __name__ == "__main__":
    main()
