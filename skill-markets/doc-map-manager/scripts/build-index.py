#!/usr/bin/env python3
"""
build-index.py — 文档索引构建器 (SQLite)

解析 docs/ 下所有 .md 文件，存储到 SQLite（.docmap/docmap.db）：
  - 按文件 mtime+size 增量检测，只解析变更文件
  - ProcessPoolExecutor 并行解析
  - 可选同步到 ChromaDB 向量数据库（--chroma）

用法:
  python build-index.py                          # 全量构建
  python build-index.py --incremental --chroma   # 增量 + ChromaDB
  python build-index.py --diff                   # 显示变更
  python build-index.py --files "ARCHITECTURE.md adr.md"  # 仅指定文件

环境变量:
  DOCMAP_EXTRA_DOCS_DIRS  额外文档目录（分号/逗号分隔）
"""

import argparse
import fnmatch
import hashlib
import json
import multiprocessing as mp
import os
import re
import sqlite3
import sys
import time
from collections import OrderedDict
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Windows cmd 编码适配
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ── SQLite Schema ─────────────────────────────────────────────

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS files (
    path TEXT NOT NULL,
    source_dir TEXT NOT NULL DEFAULT '',
    mtime REAL NOT NULL DEFAULT 0,
    size INTEGER NOT NULL DEFAULT 0,
    hash TEXT DEFAULT '',
    summary TEXT DEFAULT '',
    last_indexed TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (path, source_dir)
);

CREATE TABLE IF NOT EXISTS headings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    source_dir TEXT NOT NULL DEFAULT '',
    line INTEGER NOT NULL,
    end_line INTEGER DEFAULT 0,
    level INTEGER NOT NULL,
    title TEXT NOT NULL,
    breadcrumb TEXT DEFAULT '',
    FOREIGN KEY (file_path, source_dir) REFERENCES files(path, source_dir)
);

CREATE INDEX IF NOT EXISTS idx_headings_file ON headings(file_path, source_dir);
CREATE INDEX IF NOT EXISTS idx_headings_source ON headings(source_dir);
CREATE INDEX IF NOT EXISTS idx_headings_title ON headings(title);
"""

DOCMAP_DIR = ".docmap"
DB_NAME = "docmap.db"


def _connect_db(db_dir: Path) -> sqlite3.Connection:
    """打开 SQLite 连接（WAL 模式），创建表。"""
    docmap_dir = db_dir / DOCMAP_DIR
    docmap_dir.mkdir(parents=True, exist_ok=True)
    db_path = docmap_dir / DB_NAME
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_SQL)
    return conn


# ── 标题提取（与旧版一致） ────────────────────────────────────

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)")


def _heading_tree(headings: list[dict], total_lines: int) -> list[dict]:
    """构建标题树：end_line + breadcrumb。"""
    if not headings:
        return []
    result = []
    for h in headings:
        result.append({
            "level": h["level"], "title": h["title"], "line": h["line"],
            "end_line": 0, "parent_index": -1, "breadcrumb": h["title"],
        })
    for i in range(len(result)):
        result[i]["end_line"] = result[i + 1]["line"] - 1 if i + 1 < len(result) else total_lines
    for i in range(len(result)):
        lvl = result[i]["level"]
        for j in range(i - 1, -1, -1):
            if result[j]["level"] < lvl:
                result[i]["parent_index"] = j
                break
    for i in range(len(result)):
        parts = []
        cur = i
        while cur >= 0:
            parts.insert(0, result[cur]["title"])
            cur = result[cur]["parent_index"]
        result[i]["breadcrumb"] = " > ".join(parts)
    return result


def _extract_summary(filepath: Path, max_chars: int = 120) -> str:
    """提取文件首段摘要。"""
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return "(无法读取)"
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break
    parts = []
    for i in range(start, min(start + 15, len(lines))):
        line = lines[i].strip()
        if not line or line.startswith(("#", "---", "===", "```", ">")):
            continue
        if re.match(r"^[-*+]\s", line):
            continue
        parts.append(line)
        if len(" ".join(parts)) > max_chars:
            break
    text = " ".join(parts)
    return (text[:max_chars - 3] + "...") if len(text) > max_chars else (text or "(无摘要)")


# ── .gitignore 解析（与旧版一致） ────────────────────────────

def _load_gitignore(repo_root: Path) -> list[tuple[str, bool]]:
    gitignore = repo_root / ".gitignore"
    if not gitignore.exists():
        return []
    patterns: list[tuple[str, bool]] = []
    with open(gitignore, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue
            neg = line.startswith("!")
            if neg:
                line = line[1:]
            line = line.lstrip("/")
            patterns.append((line, neg))
    return patterns


def _match_gitignore_pattern(pattern: str, rel_path: str) -> bool:
    dir_only = pattern.endswith("/")
    if dir_only:
        pattern = pattern[:-1]
    if "/" not in pattern:
        if fnmatch.fnmatch(rel_path, "*/" + pattern) or fnmatch.fnmatch(rel_path.split("/")[-1], pattern):
            return True
        if dir_only and fnmatch.fnmatch(rel_path, "*/" + pattern + "/*"):
            return True
        return False
    if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(rel_path, "*/" + pattern):
        return True
    if dir_only and (rel_path.startswith(pattern + "/") or fnmatch.fnmatch(rel_path, pattern + "/*")):
        return True
    return False


def _is_ignored(path: Path, repo_root: Path, patterns: list[tuple[str, bool]]) -> bool:
    try:
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return False
    ignored = False
    for pattern, negated in patterns:
        if _match_gitignore_pattern(pattern, rel):
            ignored = not negated
    return ignored


# ── 文件解析（可序列化，供 ProcessPoolExecutor 调用） ─────────

_ParseResult = dict  # type alias: {"path","source_dir","mtime","size","hash","summary","headings"}


def _parse_single_file(args: tuple) -> _ParseResult:
    """解析单个 .md 文件，返回可序列化的 dict。

    args: (filepath_str, source_dir_str)
    子进程可序列化调用。
    """
    filepath_str, source_dir_str = args
    filepath = Path(filepath_str)
    source_dir = Path(source_dir_str)

    try:
        rel_path = str(filepath.relative_to(source_dir)).replace("\\", "/")
        stat = filepath.stat()
        mtime = stat.st_mtime
        size = stat.st_size
    except Exception as e:
        print(f"[WARN] 无法访问 {filepath}: {e}")
        return None  # caller 会跳过 None

    raw_headings = []
    total_lines = 0
    h = hashlib.blake2b()

    try:
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                total_lines += 1
                h.update(line.encode("utf-8"))
                stripped = line.rstrip("\n\r")
                m = _HEADING_RE.match(stripped)
                if m:
                    title = m.group(2).strip()
                    if title:
                        raw_headings.append({
                            "line": total_lines,
                            "level": len(m.group(1)),
                            "title": title,
                        })
    except Exception as e:
        print(f"[WARN] 读取失败 {filepath}: {e}")
        return {
            "path": rel_path, "source_dir": source_dir_str,
            "mtime": mtime, "size": size, "hash": "", "summary": "(读取失败)",
            "headings": [],
        }

    content_hash = h.hexdigest()
    headings = _heading_tree(raw_headings, total_lines)
    summary = _extract_summary(filepath)

    return {
        "path": rel_path,
        "source_dir": source_dir_str,
        "mtime": mtime,
        "size": size,
        "hash": content_hash,
        "summary": summary,
        "headings": headings,
    }


# ── SQLite 读写 ───────────────────────────────────────────────


def _get_changed_files(conn: sqlite3.Connection, md_files: list[Path], source_dir: str) -> list[Path]:
    """对比 SQLite 中的 mtime+size，返回变更/新增的文件列表。"""
    changed = []
    cur = conn.execute("SELECT path, mtime, size FROM files WHERE source_dir = ?", (source_dir,))
    known = {(row[0], row[1], row[2]) for row in cur.fetchall()}

    for fp in md_files:
        rel = str(fp.relative_to(source_dir)).replace("\\", "/")
        try:
            stat = fp.stat()
        except OSError:
            print(f"[WARN] 无法访问（增量检测）: {fp}")
            changed.append(fp)  # 纳入处理，_parse_single_file 会跳过
            continue
        key = (rel, stat.st_mtime, stat.st_size)
        if key not in known:
            changed.append(fp)

    return changed


def _write_batch(conn: sqlite3.Connection, parsed_results: list[_ParseResult]):
    """批量写入解析结果到 SQLite（事务内完成）。"""
    conn.execute("BEGIN")
    try:
        for r in parsed_results:
            conn.execute(
                """INSERT INTO files (path, source_dir, mtime, size, hash, summary, last_indexed)
                   VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                   ON CONFLICT(path, source_dir) DO UPDATE SET
                       mtime=excluded.mtime, size=excluded.size, hash=excluded.hash,
                       summary=excluded.summary, last_indexed=datetime('now')""",
                (r["path"], r["source_dir"], r["mtime"], r["size"], r["hash"], r["summary"]),
            )
            conn.execute("DELETE FROM headings WHERE file_path=? AND source_dir=?",
                         (r["path"], r["source_dir"]))
            for h in r["headings"]:
                conn.execute(
                    "INSERT INTO headings (file_path, source_dir, line, end_line, level, title, breadcrumb) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (r["path"], r["source_dir"], h["line"], h["end_line"],
                     h["level"], h["title"], h.get("breadcrumb", h["title"])),
                )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def _build_files_data_from_db(conn: sqlite3.Connection) -> OrderedDict:
    """从 SQLite 构建 files_data dict（用于 ChromaDB 同步）。"""
    files_data: OrderedDict = OrderedDict()
    cur = conn.execute("SELECT path, source_dir, summary FROM files")
    for row in cur.fetchall():
        rel_path, source_dir, summary = row
        hcur = conn.execute(
            "SELECT line, end_line, level, title, breadcrumb FROM headings "
            "WHERE file_path=? AND source_dir=? ORDER BY line",
            (rel_path, source_dir),
        )
        headings = [{"line": r[0], "end_line": r[1], "level": r[2],
                      "title": r[3], "breadcrumb": r[4]} for r in hcur.fetchall()]
        key = rel_path
        # 多目录时文件名可能冲突，用 [dir_tag] 前缀
        files_data[key] = {
            "summary": summary or "",
            "headings": headings,
            "source_dir": source_dir,
        }
    # 重新计算多目录前缀
    sources = {v["source_dir"] for v in files_data.values() if v.get("source_dir")}
    if len(sources) > 1:
        new_fd: OrderedDict = OrderedDict()
        seen_paths: dict[str, int] = {}
        for key, data in files_data.items():
            sd = data.get("source_dir", "")
            if sd:
                dir_tag = Path(sd).name
                new_key = f"[{dir_tag}] {key}"
            else:
                new_key = key
            new_fd[new_key] = data
        files_data = new_fd
    return files_data


# ── ChromaDB 集成（与旧版一致） ──────────────────────────────

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
        api_base = config.get("DOCMAP_EMBEDDING_API_BASE", "http://localhost:11434/v1")
        api_key = config.get("DOCMAP_EMBEDDING_API_KEY", "local llm")
        model = config.get("DOCMAP_EMBEDDING_MODEL", "nomic-embed-text")
        print(f"[ChromaDB] 使用 OpenAI 兼容端点: {api_base} / {model}")
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key, api_base=api_base, model_name=model,
        )
    if provider == "chroma_default":
        print("[ChromaDB] 使用 chromadb 默认模型: all-MiniLM-L6-v2")
        return embedding_functions.DefaultEmbeddingFunction()
    model = config.get("DOCMAP_EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
    print(f"[ChromaDB] 使用本地模型: {model}")
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model)


def sync_to_chromadb(files_data: dict, docs_dir: Path) -> bool:
    """将标题索引同步到 ChromaDB 向量数据库。"""
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError:
        print("[ChromaDB] chromadb 未安装，跳过向量同步。")
        return False
    config = _load_dotenv()
    chroma_dir = docs_dir / DOCMAP_DIR / "chroma"
    chroma_dir.mkdir(parents=True, exist_ok=True)
    ef = _create_embedding_function(config)
    client = chromadb.PersistentClient(
        path=str(chroma_dir),
        settings=Settings(anonymized_telemetry=False),
    )
    try:
        client.delete_collection("doc_headings")
    except Exception:
        pass
    collection = client.create_collection(
        name="doc_headings", embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []
    for rel_path, data in files_data.items():
        if rel_path == "DOCSMAP.md":
            continue
        summary = data.get("summary", "")
        for h in data.get("headings", []):
            uid = f"{rel_path}:L{h['line']}"
            doc_text = (
                f"文件: {rel_path}\n摘要: {summary}\n"
                f"路径: {h.get('breadcrumb', h['title'])}\n标题: {h['title']}"
            )
            ids.append(uid)
            documents.append(doc_text)
            metadatas.append({
                "file": rel_path,
                "line": h["line"],
                "end_line": h.get("end_line", 0),
                "level": h["level"],
                "title": h["title"],
                "breadcrumb": h.get("breadcrumb", h["title"]),
                "source_dir": data.get("source_dir", ""),
            })
    if not ids:
        print("[ChromaDB] 无标题数据，跳过同步")
        return True
    provider = config.get("DOCMAP_EMBEDDING_PROVIDER", "sentence_transformers")
    if provider == "openai":
        _sync_concurrent(collection, ef, ids, documents, metadatas, config)
    else:
        _sync_serial(collection, ids, documents, metadatas)
    print(f"[ChromaDB] 同步完成 ({len(ids)} 条)")
    return True


def _sync_serial(collection, ids, documents, metadatas):
    batch_size = 200
    total_batches = (len(ids) + batch_size - 1) // batch_size
    try:
        from tqdm import tqdm
        it = tqdm(range(0, len(ids), batch_size), total=total_batches, desc="[ChromaDB]", unit="batch")
    except ImportError:
        it = range(0, len(ids), batch_size)
    for i in it:
        b_end = min(i + batch_size, len(ids))
        collection.add(ids=ids[i:b_end], documents=documents[i:b_end], metadatas=metadatas[i:b_end])


def _sync_concurrent(collection, ef, ids, documents, metadatas, config):
    import concurrent.futures
    batch_size = 200
    workers = int(os.environ.get("DOCMAP_CONCURRENCY", "10"))
    sub_batches = [(i, min(i + batch_size, len(ids))) for i in range(0, len(ids), batch_size)]
    total = len(sub_batches)
    print(f"[ChromaDB] 并发模式: {workers} workers, {total} batches")
    try:
        from tqdm import tqdm
        pbar = tqdm(total=total, desc="[ChromaDB]", unit="batch")
    except ImportError:
        pbar = None
    all_embeddings: list = [None] * total
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        f2i = {}
        for idx, (s, e) in enumerate(sub_batches):
            f2i[executor.submit(ef, documents[s:e])] = idx
        for f in concurrent.futures.as_completed(f2i):
            all_embeddings[f2i[f]] = f.result()
            if pbar:
                pbar.update(1)
    if pbar:
        pbar.close()
    write_batch = 5000
    for i in range(0, len(ids), write_batch):
        b_end = min(i + write_batch, len(ids))
        emb_slice = []
        for bidx, (s, e) in enumerate(sub_batches):
            if s >= b_end:
                break
            if e <= i:
                continue
            emb_slice.extend(all_embeddings[bidx])
        collection.add(ids=ids[i:b_end], embeddings=emb_slice, metadatas=metadatas[i:b_end])


# ── Zvec 同步（动态队列 + 流式写入 + 多源嵌入） ─────────────────

def _compute_data_version(conn: sqlite3.Connection) -> str:
    """计算 SQLite 中所有文件的数据版本哈希。"""
    import hashlib
    cur = conn.execute("SELECT path, source_dir, mtime, size, hash FROM files ORDER BY path, source_dir")
    h = hashlib.blake2b()
    for row in cur:
        h.update(f"{row[0]}|{row[1]}|{row[2]}|{row[3]}|{row[4]}".encode())
    return h.hexdigest()


def _load_zvec_state(path: Path) -> dict:
    """加载 Zvec 状态：{data_version, file_paths}。缺失返回空 dict。"""
    try:
        if path.exists():
            import json
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_zvec_state(path: Path, version: str, file_paths: list[str]):
    """持久化 Zvec 状态。"""
    import json
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(
        {"data_version": version, "file_paths": sorted(set(file_paths))},
        ensure_ascii=False, indent=2,
    ), encoding="utf-8")


def _parse_embedding_sources(config: dict) -> list[dict]:
    """解析 .env 配置，返回所有 embedding 源（本地 CPU + N个 OpenAI）。"""
    sources = []

    # 1) 本地 CPU（sentence_transformers）
    local_weight = int(config.get("DOCMAP_EMBEDDING_LOCAL_WEIGHT", "1"))
    if local_weight > 0:
        try:
            from sentence_transformers import SentenceTransformer
            raw_name = config.get("DOCMAP_EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
            if "/" not in raw_name:
                candidates = [f"BAAI/{raw_name}", raw_name]
            else:
                candidates = [raw_name]
            model = None
            model_name = ""
            for name in candidates:
                try:
                    model = SentenceTransformer(name)
                    model_name = name
                    break
                except Exception:
                    continue
            if model is not None:
                dim = model.get_sentence_embedding_dimension()
                sources.append({
                    "type": "local",
                    "weight": local_weight,
                    "model": model,
                    "model_name": model_name,
                    "dim": dim,
                    "label": f"CPU({model_name})",
                })
                print(f"[Zvec] CPU 源已加载: {model_name} (dim={dim}, weight={local_weight})")
        except Exception as e:
            print(f"[Zvec] CPU 源不可用: {e}")

    batch_size = int(config.get("DOCMAP_EMBEDDING_BATCH", "200"))

    # 2) 兼容旧式单端点
    single_base = config.get("DOCMAP_EMBEDDING_API_BASE", "")
    if single_base:
        from openai import OpenAI
        api_key = config.get("DOCMAP_EMBEDDING_API_KEY", "local llm")
        model_name = config.get("DOCMAP_EMBEDDING_MODEL", "bge-small-zh-v1.5")
        client = OpenAI(api_key=api_key, base_url=single_base, timeout=60)
        probe = client.embeddings.create(input="probe", model=model_name)
        dim = len(probe.data[0].embedding)
        sources.append({
            "type": "openai",
            "weight": int(config.get("DOCMAP_EMBEDDING_API_WEIGHT", "3")),
            "client": client,
            "model_name": model_name,
            "dim": dim,
            "batch_size": batch_size,
            "label": f"API({model_name})",
        })
        print(f"[Zvec] API 源: {single_base} / {model_name} (dim={dim})")

    # 3) 多端点（JSON 数组）
    endpoints_raw = config.get("DOCMAP_EMBEDDING_ENDPOINTS", "")
    if endpoints_raw:
        import json as _json
        try:
            eps = _json.loads(endpoints_raw)
            for i, ep in enumerate(eps):
                from openai import OpenAI
                client = OpenAI(api_key=ep.get("key", "local llm"), base_url=ep["base"], timeout=60)
                mn = ep.get("model", config.get("DOCMAP_EMBEDDING_MODEL", "bge-small-zh-v1.5"))
                probe = client.embeddings.create(input="probe", model=mn)
                dim = len(probe.data[0].embedding)
                sources.append({
                    "type": "openai",
                    "weight": int(ep.get("weight", 2)),
                    "client": client,
                    "model_name": mn,
                    "dim": dim,
                    "batch_size": int(ep.get("batch_size", batch_size)),
                    "label": f"EP{i+1}({mn})",
                })
                print(f"[Zvec] API 源 EP{i+1}: {ep['base']} / {mn} (dim={dim}, weight={ep.get('weight',2)})")
        except Exception as e:
            print(f"[Zvec] 多端点解析失败: {e}")

    return sources


def _embed_chunk_local(source: dict, texts: list[str], start: int) -> tuple[int, list[list[float]]]:
    """本地 CPU 执行一部分文本的 embedding。"""
    model = source["model"]
    vecs = model.encode(texts, show_progress_bar=False).tolist()
    return start, vecs


def _embed_chunk_openai(source: dict, texts: list[str], start: int) -> tuple[int, list[list[float]]]:
    """单个 OpenAI 端点执行一部分文本的 embedding（内部分批并发）。"""
    import concurrent.futures
    client = source["client"]
    mn = source["model_name"]
    batch_size = source.get("batch_size", 200)
    sub_batches = [(i, min(i + batch_size, len(texts))) for i in range(0, len(texts), batch_size)]
    results: list[list[list[float]] | None] = [None] * len(sub_batches)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        f2i = {}
        for idx, (s, e) in enumerate(sub_batches):
            batch = texts[s:e]
            f2i[pool.submit(_openai_embed_batch, client, batch, mn)] = idx
        for f in concurrent.futures.as_completed(f2i):
            results[f2i[f]] = f.result()
    all_vecs: list[list[float]] = []
    for r in results:
        all_vecs.extend(r)
    return start, all_vecs


def _openai_embed_batch(client, batch: list[str], model_name: str) -> list[list[float]]:
    """单 batch 的 OpenAI embedding 调用。"""
    resp = client.embeddings.create(input=batch, model=model_name)
    sorted_data = sorted(resp.data, key=lambda x: x.index)
    return [d.embedding for d in sorted_data]


def _sync_embedding(entries: list[dict], zvec_dir: Path, config: dict) -> bool:
    """多源并发嵌入 → 流式写入 Zvec。

    使用动态工作队列：所有 embedding 源从共享队列中取任务，
    按实际消费速度分配。每个块向量化后立即写入 Zvec，不积攒内存。
    """
    try:
        import zvec as _zv
    except ImportError:
        print("[Zvec] zvec 未安装，跳过向量同步。")
        return False

    texts = [e["text"] for e in entries]
    if not texts:
        return True

    sources = _parse_embedding_sources(config)
    if not sources:
        print("[Zvec] 无可用 embedding 源，跳过。")
        return False

    dim = sources[0]["dim"]

    # 重建 Zvec collection
    if zvec_dir.exists():
        import shutil
        shutil.rmtree(str(zvec_dir), ignore_errors=True)
    schema = _zv.CollectionSchema(
        name="doc_headings",
        vectors=_zv.VectorSchema("embedding", _zv.DataType.VECTOR_FP32, dim),
        fields=[
            _zv.FieldSchema("file", _zv.DataType.STRING),
            _zv.FieldSchema("line", _zv.DataType.INT32),
            _zv.FieldSchema("end_line", _zv.DataType.INT32),
            _zv.FieldSchema("level", _zv.DataType.INT32),
            _zv.FieldSchema("title", _zv.DataType.STRING),
            _zv.FieldSchema("breadcrumb", _zv.DataType.STRING),
            _zv.FieldSchema("source_dir", _zv.DataType.STRING),
        ],
    )
    collection = _zv.create_and_open(path=str(zvec_dir), schema=schema)

    # 动态消费队列
    import concurrent.futures
    import queue
    import threading

    CHUNK = 500
    work_queue: queue.Queue = queue.Queue()
    for i in range(0, len(texts), CHUNK):
        end = min(i + CHUNK, len(texts))
        work_queue.put((i, texts[i:end]))

    total_chunks = (len(texts) + CHUNK - 1) // CHUNK
    insert_lock = threading.Lock()

    print(f"[Zvec] 动态队列: {len(texts)} 条, {total_chunks} 块, {len(sources)} 个源")

    from tqdm import tqdm
    pbar = tqdm(total=total_chunks, desc="Embedding", unit="chunk")

    def _worker(source: dict):
        while True:
            try:
                start, chunk = work_queue.get_nowait()
            except queue.Empty:
                return
            try:
                if source["type"] == "local":
                    _, vecs = _embed_chunk_local(source, chunk, start)
                else:
                    _, vecs = _embed_chunk_openai(source, chunk, start)

                # 流式写入：每块向量化完立即写 Zvec
                docs = []
                for j, v in enumerate(vecs):
                    idx = start + j
                    e = entries[idx]
                    docs.append(_zv.Doc(
                        id=e["uid"],
                        vectors={"embedding": v},
                        fields={
                            "file": e["file"],
                            "line": e["line"],
                            "end_line": e["end_line"],
                            "level": e["level"],
                            "title": e["title"],
                            "breadcrumb": e["breadcrumb"],
                            "source_dir": e["source_dir"],
                        },
                    ))
                with insert_lock:
                    collection.insert(docs)

                pbar.update(1)
            except Exception as e:
                print(f"\n  ❌ {source.get('label', '?')} 块失败 (start={start}): {e}")
                raise

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(sources)) as pool:
        futures = [pool.submit(_worker, src) for src in sources]
        for f in concurrent.futures.as_completed(futures):
            exc = f.exception()
            if exc:
                pbar.close()
                return False

    pbar.close()
    print(f"[Zvec] 同步完成 ({len(entries)} 条, dim={dim})")
    return True


def _sync_zvec_from_db(conn: sqlite3.Connection, db_dir: Path, config: dict) -> None:
    """从 SQLite 读取数据，同步到 Zvec。"""
    zvec_dir = db_dir / DOCMAP_DIR / "zvec"
    zvec_state_path = zvec_dir / "zvec_state.json"

    # 检查 SQLite 中是否有数据
    cur = conn.execute("SELECT COUNT(*) FROM files")
    row_count = cur.fetchone()[0]
    if row_count == 0:
        print("[Zvec] SQLite 中无数据，跳过同步。")
        return

    data_version = _compute_data_version(conn)
    old_state = _load_zvec_state(zvec_state_path)

    # 检测是否需同步
    need_sync = not old_state or data_version != old_state.get("data_version", "")
    if not need_sync and old_state.get("file_paths"):
        cur = conn.execute("SELECT path FROM files")
        current_paths = {row[0] for row in cur.fetchall()}
        removed = [p for p in old_state["file_paths"] if p not in current_paths]
        if removed:
            print(f"[Zvec] 检测到 {len(removed)} 个文件被移除，触发重建")
            need_sync = True

    if need_sync:
        files_data = _build_files_data_from_db(conn)
        if files_data:
            print(f"\n[Zvec] 从 SQLite 读取 {len(files_data)} 个文件数据 ({row_count} files)...")
            entries = []
            for rel_path, data in files_data.items():
                if rel_path == "DOCSMAP.md":
                    continue
                for h in data.get("headings", []):
                    entries.append({
                        "uid": hashlib.md5(f"{rel_path}:L{h['line']}".encode()).hexdigest(),
                        "text": h["title"],
                        "file": rel_path,
                        "line": h["line"],
                        "end_line": h.get("end_line", 0),
                        "level": h["level"],
                        "title": h["title"],
                        "breadcrumb": h.get("breadcrumb", h["title"]),
                        "source_dir": data.get("source_dir", ""),
                    })
            if entries and _sync_embedding(entries, zvec_dir, config):
                cur = conn.execute("SELECT path FROM files")
                raw_paths = [row[0] for row in cur.fetchall()]
                _save_zvec_state(zvec_state_path, data_version, raw_paths)
    else:
        print(f"[Zvec] 数据无变更，跳过同步")


# ── Git Diff 检测（与旧版一致） ──────────────────────────────

def _run_git_diff(repo_root: Path, git_ref: str | None) -> None:
    import subprocess
    git_dir = repo_root / ".git"
    if not git_dir.exists():
        print("[GIT-DIFF] 当前目录不是 Git 仓库。使用 --diff 进行基于 mtime 的变更检测。")
        return
    ref = git_ref or "HEAD"
    try:
        cmd = ["git", "diff", "--name-status", ref, "--", "docs/"]
        result = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"[GIT-DIFF] git diff 失败: {result.stderr}")
            return
        output = result.stdout.strip()
        if not output:
            print(f"[GIT-DIFF] 与 {ref} 对比：docs/ 无变更。")
            return
    except FileNotFoundError:
        print("[GIT-DIFF] 未找到 git 命令。")
        return
    except subprocess.TimeoutExpired:
        print("[GIT-DIFF] git diff 超时。")
        return
    lines = output.split("\n")
    categories: dict[str, list[tuple[str, str]]] = {
        "docs/modules/": [], "docs/specs/changes/": [], "docs/contracts/": [],
        "docs/prototypes/": [], "docs/test-plan/": [], "docs/archive/": [],
        "docs/CODEMAPS/": [], "docs/ 其他": [],
    }
    for line in lines:
        parts = line.split("\t")
        if len(parts) < 2 or not parts[1].endswith(".md"):
            continue
        status, path = parts[0], parts[1]
        matched = False
        for cat in sorted(categories, reverse=True):
            if cat == "docs/ 其他":
                continue
            if path.startswith(cat):
                categories[cat].append((status, path))
                matched = True
                break
        if not matched:
            categories["docs/ 其他"].append((status, path))
    status_labels = {"A": "ADDED", "M": "MODIFIED", "D": "DELETED", "R": "RENAMED", "C": "COPIED"}
    print(f"\n[GIT-DIFF] 与 {ref} 对比，docs/ 变更如下：\n")
    for cat, entries in categories.items():
        if not entries:
            continue
        print(f"  [{cat}] ({len(entries)} files)")
        for status, path in entries:
            label = status_labels.get(status, status)
            print(f"    {label:<10} {path[5:] if path.startswith('docs/') else path}")
        print()
    total = sum(len(v) for v in categories.values())
    print(f"  共 {total} 个文件变更")
    changes_specs = len(categories["docs/specs/changes/"]) + len(categories["docs/contracts/"])
    changes_modules = len(categories["docs/modules/"])
    if changes_specs > 0 and changes_modules == 0:
        print(f"\n  ⚠️  DOC SYNC 提醒：{changes_specs} 个 specs/contracts/ 文件变更，")
        print("     但 docs/modules/ 无对应变更。可能需要执行 DOC SYNC 回流。")
    elif changes_specs > 0 and changes_modules > 0:
        print(f"\n  ℹ️  DOC SYNC 状态：specs/ 和 modules/ 均有变更，建议确认。")
    print()


# ── diff 模式 ──────────────────────────────────────────────────

def _diff_vs_sqlite(conn: sqlite3.Connection, md_files: list[Path], source_dir: str, docs_dir: Path):
    """对比 SQLite 输出变更清单。"""
    cur = conn.execute("SELECT path, mtime, size FROM files WHERE source_dir = ?", (source_dir,))
    known = {(row[0], row[1], row[2]) for row in cur.fetchall()}
    current = {}
    for fp in md_files:
        rel = str(fp.relative_to(source_dir)).replace("\\", "/")
        stat = fp.stat()
        current[rel] = (stat.st_mtime, stat.st_size)

    added = [k for k in current if k not in {r[0] for r in known}]
    deleted = [r[0] for r in known if r[0] not in current]
    modified = [k for k in current if k in {r[0] for r in known}
                and current[k] != (next(r[1] for r in known if r[0] == k), next(r[2] for r in known if r[0] == k))]

    print(f"\n[DIFF] 与上次索引相比的变更：")
    if added:
        print(f"\n  [ADDED] ({len(added)})")
        for f in sorted(added):
            print(f"    + {f}")
    if deleted:
        print(f"\n  [DELETED] ({len(deleted)})")
        for f in sorted(deleted):
            print(f"    - {f}")
    if modified:
        print(f"\n  [MODIFIED] ({len(modified)})")
        for f in sorted(modified):
            print(f"    ~ {f}")
    if not added and not deleted and not modified:
        print("    (无变更)")
    print()


# ── 核心流程 ──────────────────────────────────────────────────


def _process_single_dir(
    docs_dir: Path,
    repo_root: Path,
    target_files: list[str] | None = None,
    use_chroma: bool = False,
    use_gitignore: bool = True,
    incremental: bool = False,
    diff_mode: bool = False,
    db_dir: Path | None = None,
) -> int:
    """处理单个文档目录，返回处理文件数。"""
    # 集中式模式：所有目录数据写入同一个 db_dir；向后兼容：None 则用 docs_dir
    connect_dir = db_dir if db_dir is not None else docs_dir
    conn = _connect_db(connect_dir)

    # 加载 .gitignore
    gitignore_patterns = _load_gitignore(repo_root) if use_gitignore else []

    # 收集 .md 文件
    md_files: list[Path] = []
    if target_files:
        for f in target_files:
            fp = docs_dir / f
            if fp.exists() and fp.suffix == ".md":
                md_files.append(fp)
            else:
                print(f"[WARN] 文件不存在或非 .md: {f}")
    else:
        md_files = sorted(docs_dir.rglob("*.md"))
        # 自我排除：忽略 .docmap/ 目录下的所有文件
        docmap_dir = docs_dir / DOCMAP_DIR
        if docmap_dir.exists():
            md_files = [f for f in md_files if not str(f.resolve()).startswith(str(docmap_dir.resolve()))]
        if gitignore_patterns:
            before = len(md_files)
            md_files = [f for f in md_files if not _is_ignored(f, repo_root, gitignore_patterns)]
            skipped = before - len(md_files)
            if skipped:
                print(f"[gitignore] 排除 {skipped} 个被忽略的文件")

    if not md_files:
        print("[ERROR] 未找到任何 .md 文件")
        conn.close()
        return 0

    source_dir = str(docs_dir)

    # diff 模式
    if diff_mode:
        _diff_vs_sqlite(conn, md_files, source_dir, docs_dir)
        conn.close()
        return 0

    # 增量：找出变更文件
    if incremental and not target_files:
        changed = _get_changed_files(conn, md_files, source_dir)
        if not changed:
            print(f"\n[增量] {docs_dir.name}: 无变更文件，跳过。")
            conn.close()
            return 0
        print(f"\n[增量] {docs_dir.name}: {len(changed)}/{len(md_files)} 文件需要处理")
        md_files = changed
    else:
        print(f"\n[全量] {docs_dir.name}: {len(md_files)} 个文件")

    # 并行解析
    n_workers = min(mp.cpu_count(), len(md_files), 8)
    parse_args = [(str(fp), source_dir) for fp in md_files]
    results: list[_ParseResult] = []

    if n_workers <= 1:
        # 单文件直接跑（避免进程启动开销）
        for i, args in enumerate(parse_args):
            print(f"  [{i + 1}/{len(parse_args)}] {Path(args[0]).name}", end="")
            r = _parse_single_file(args)
            if r is None:
                print(" (跳过-无法访问)")
                continue
            results.append(r)
            print(f" ({len(r['headings'])} headings)")
    else:
        print(f"  并行解析 ({n_workers} workers)...")
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            futures = {pool.submit(_parse_single_file, args): args for args in parse_args}
            for i, future in enumerate(as_completed(futures), 1):
                r = future.result()
                if r is None:
                    print(f"  [{i}/{len(parse_args)}] (跳过-无法访问)")
                    continue
                results.append(r)
                print(f"  [{i}/{len(parse_args)}] {r['path']} ({len(r['headings'])} headings)")

    # 批量写入 SQLite
    _write_batch(conn, results)

    total_h = sum(len(r["headings"]) for r in results)
    print(f"  → 写入 SQLite: {len(results)} files, {total_h} headings")
    conn.close()
    return len(results)


# ── Main ──────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="构建文档索引 (SQLite + ChromaDB + Zvec)"
    )
    parser.add_argument("--files", type=str, nargs="*", default=None,
                        help="指定文件列表（相对于 docs/），默认扫描所有 .md")
    parser.add_argument("--docs-dir", type=str, default=None, action="append",
                        help="文档目录路径（可多次指定）")
    parser.add_argument("--chroma", action="store_true", default=False,
                        help="同步到 ChromaDB 向量数据库")
    parser.add_argument("--no-chroma", action="store_true", default=False,
                        help="强制跳过 ChromaDB 同步")
    parser.add_argument("--zvec", action="store_true", default=False,
                        help="同步到 Zvec 向量数据库（动态队列 + 流式写入 + 多源嵌入）")
    parser.add_argument("--no-zvec", action="store_true", default=False,
                        help="强制跳过 Zvec 同步")
    parser.add_argument("--no-gitignore", action="store_true", default=False,
                        help="不读取 .gitignore，扫描全部文件")
    parser.add_argument("--incremental", action="store_true", default=False,
                        help="增量模式：只索引新增/修改的文件（基于 mtime+size）")
    parser.add_argument("--diff", action="store_true", default=False,
                        help="显示自上次索引以来的变更清单")
    parser.add_argument("--git-diff", action="store_true", default=False,
                        help="使用 git diff 检测 docs/ 变更")
    parser.add_argument("--git-ref", type=str, default=None,
                        help="--git-diff 的对比基准")
    args = parser.parse_args()

    # ── 解析 docs_dirs ────────────────────────────────────
    if args.docs_dir:
        docs_dirs = [Path(d).resolve() for d in args.docs_dir]
        repo_root = docs_dirs[0].parent
    else:
        script_dir = Path(__file__).resolve().parent
        skill_root = script_dir.parent
        repo_root = skill_root.parent.parent
        docs_dirs = [repo_root / "docs"]
        if not docs_dirs[0].exists():
            cwd_docs = Path.cwd() / "docs"
            if cwd_docs.exists():
                docs_dirs = [cwd_docs]
                repo_root = cwd_docs.parent
            else:
                found = False
                for parent in Path.cwd().parents:
                    candidate = parent / "docs"
                    if candidate.exists() and candidate.is_dir():
                        docs_dirs = [candidate]
                        repo_root = parent
                        found = True
                        break
                if not found:
                    docs_dirs = [Path.cwd() / "docs"]
                    repo_root = Path.cwd()

    # git-diff 模式
    if args.git_diff:
        diff_docs = docs_dirs[0] if docs_dirs[0].exists() else repo_root / "docs"
        _run_git_diff(repo_root, args.git_ref)
        return

    # 从 .env 加载额外目录
    config = _load_dotenv()
    extra_raw = config.get("DOCMAP_EXTRA_DOCS_DIRS", "")
    if extra_raw:
        for d in re.split(r"[;,]", extra_raw):
            d = d.strip()
            if not d:
                continue
            p = Path(d).resolve()
            if p.exists() and p.is_dir():
                if p not in docs_dirs:
                    docs_dirs.append(p)
            else:
                print(f"[WARN] DOCMAP_EXTRA_DOCS_DIRS 目录不存在: {p}")

    # 验证
    for d in docs_dirs:
        if not d.exists():
            print(f"[ERROR] 文档目录不存在: {d}")
            sys.exit(1)

    use_chroma = args.chroma and not args.no_chroma
    use_zvec = args.zvec and not args.no_zvec
    use_gitignore = not args.no_gitignore

    # 集中式数据目录（SQLite + ChromaDB + Zvec）
    db_dir = docs_dirs[0]

    # 从 .env 读取额外配置（Zvec 多源等）
    zvec_config = _load_dotenv()

    mode = "mtime-diff" if args.diff else ("incremental" if args.incremental else "全量")
    print(f"Docs dirs: {[str(d) for d in docs_dirs]}")
    print(f"Mode: {mode}, ChromaDB: {'启用' if use_chroma else '跳过'}, Zvec: {'启用' if use_zvec else '跳过'}, Gitignore: {'启用' if use_gitignore else '跳过'}")
    print()

    # 逐个处理
    total_processed = 0
    for i, docs_dir in enumerate(docs_dirs):
        if len(docs_dirs) > 1:
            print(f"\n{'='*50}")
            print(f"  [{i + 1}/{len(docs_dirs)}] {docs_dir}")
            print(f"{'='*50}")
        n = _process_single_dir(
            docs_dir, repo_root, args.files, use_chroma, use_gitignore,
            incremental=args.incremental, diff_mode=args.diff,
            db_dir=db_dir,
        )
        total_processed += n

    if args.diff:
        print(f"\n[OK] diff 完成。")
        return

    # ChromaDB 同步
    if use_chroma and total_processed > 0:
        conn = _connect_db(db_dir)
        files_data = _build_files_data_from_db(conn)
        conn.close()
        if files_data:
            print(f"\n[ChromaDB] 从 SQLite 读取 {len(files_data)} 个文件数据...")
            sync_to_chromadb(files_data, db_dir)

    # Zvec 同步
    if use_zvec:
        conn = _connect_db(db_dir)
        _sync_zvec_from_db(conn, db_dir, zvec_config)
        conn.close()

    print(f"\n[OK] 完成。处理 {total_processed} 个文件。")


if __name__ == "__main__":
    main()
