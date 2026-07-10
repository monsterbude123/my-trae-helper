"""
SQLite 数据库管理 — Schema 定义、迁移、CRUD 操作

数据库文件位置：{repo_path}/.mymodelscope.db
由 config.py 的 db_path 指定。
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timezone

SCHEMA_VERSION = 2

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS models (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    family TEXT DEFAULT '',
    task TEXT DEFAULT '',
    file_path TEXT NOT NULL,
    file_size_gb REAL DEFAULT 0,
    sha256 TEXT DEFAULT '',
    source_url TEXT DEFAULT '',
    license TEXT DEFAULT '',
    status TEXT DEFAULT 'active',
    notes TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS capabilities (
    model_id TEXT NOT NULL,
    capability TEXT NOT NULL,
    PRIMARY KEY (model_id, capability),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quality_scores (
    model_id TEXT NOT NULL,
    dimension TEXT NOT NULL,
    score INTEGER NOT NULL CHECK(score >= 1 AND score <= 10),
    PRIMARY KEY (model_id, dimension),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recommendations (
    model_id TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    PRIMARY KEY (model_id, recommendation),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tags (
    model_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (model_id, tag),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dependencies (
    model_id TEXT NOT NULL,
    dep_type TEXT NOT NULL,
    dep_family TEXT NOT NULL,
    PRIMARY KEY (model_id, dep_type, dep_family),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_time TEXT DEFAULT (datetime('now')),
    repo_path TEXT NOT NULL,
    models_found INTEGER DEFAULT 0,
    new_models INTEGER DEFAULT 0,
    updated_models INTEGER DEFAULT 0,
    errors TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    source_url TEXT DEFAULT '',
    content_type TEXT NOT NULL DEFAULT 'model_info',
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT DEFAULT '[]',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(model_name, content_type, title)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_models_type ON models(type);
CREATE INDEX IF NOT EXISTS idx_models_task ON models(task);
CREATE INDEX IF NOT EXISTS idx_models_family ON models(family);
CREATE INDEX IF NOT EXISTS idx_models_status ON models(status);
CREATE INDEX IF NOT EXISTS idx_capabilities_cap ON capabilities(capability);
CREATE INDEX IF NOT EXISTS idx_recommendations_rec ON recommendations(recommendation);
CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);
CREATE INDEX IF NOT EXISTS idx_kb_model ON knowledge_base(model_name);
CREATE INDEX IF NOT EXISTS idx_kb_type ON knowledge_base(content_type);
"""


class Database:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.conn: sqlite3.Connection | None = None

    def connect(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        return self

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, *args):
        self.close()

    def init_schema(self):
        """初始化数据库表结构 + 版本号"""
        self.conn.executescript(CREATE_TABLES_SQL)
        existing = self.conn.execute(
            "SELECT version FROM schema_version WHERE version = ?", (SCHEMA_VERSION,)
        ).fetchone()
        if not existing:
            self.conn.execute(
                "INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,)
            )
        self.conn.commit()

    # ─── CRUD: models ───

    def upsert_model(self, data: dict) -> bool:
        """插入或更新模型记录。返回 True 表示新插入，False 表示更新。"""
        existing = self.conn.execute(
            "SELECT id FROM models WHERE id = ?", (data["id"],)
        ).fetchone()

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        if existing:
            self.conn.execute("""
                UPDATE models SET name=?, type=?, family=?, task=?, file_path=?,
                file_size_gb=?, sha256=?, source_url=?, license=?, notes=?, updated_at=?
                WHERE id=?
            """, (
                data["name"], data["type"], data.get("family", ""), data.get("task", ""),
                data["file_path"], data.get("file_size_gb", 0), data.get("sha256", ""),
                data.get("source_url", ""), data.get("license", ""), data.get("notes", ""),
                now, data["id"]
            ))
            return False
        else:
            self.conn.execute("""
                INSERT INTO models (id, name, type, family, task, file_path,
                file_size_gb, sha256, source_url, license, status, notes, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                data["id"], data["name"], data["type"], data.get("family", ""), data.get("task", ""),
                data["file_path"], data.get("file_size_gb", 0), data.get("sha256", ""),
                data.get("source_url", ""), data.get("license", ""),
                data.get("status", "active"), data.get("notes", ""), now, now
            ))
            return True

    def set_relations(self, model_id: str, relation_type: str, items: list[str]):
        """批量设置关联数据（capabilities/recommendations/tags）"""
        table_map = {
            "capabilities": "capabilities",
            "recommendations": "recommendations",
            "tags": "tags",
        }
        col_map = {
            "capabilities": "capability",
            "recommendations": "recommendation",
            "tags": "tag",
        }
        table = table_map[relation_type]
        col = col_map[relation_type]
        self.conn.execute(f"DELETE FROM {table} WHERE model_id = ?", (model_id,))
        for item in items:
            self.conn.execute(
                f"INSERT OR IGNORE INTO {table} (model_id, {col}) VALUES (?,?)",
                (model_id, item.strip()),
            )

    def set_quality(self, model_id: str, scores: dict[str, int]):
        """批量设置质量评分"""
        self.conn.execute("DELETE FROM quality_scores WHERE model_id = ?", (model_id,))
        for dim, score in scores.items():
            self.conn.execute(
                "INSERT INTO quality_scores (model_id, dimension, score) VALUES (?,?,?)",
                (model_id, dim, score),
            )

    def set_dependencies(self, model_id: str, deps: list[dict]):
        """设置依赖关系"""
        self.conn.execute("DELETE FROM dependencies WHERE model_id = ?", (model_id,))
        for dep in deps:
            self.conn.execute(
                "INSERT INTO dependencies (model_id, dep_type, dep_family) VALUES (?,?,?)",
                (model_id, dep.get("type", ""), dep.get("family", "")),
            )

    def get_models_by_sha256(self, sha256: str) -> list[dict]:
        """通过 SHA256 查找模型（用于去重）"""
        rows = self.conn.execute(
            "SELECT id, file_path FROM models WHERE sha256 = ? AND sha256 != ''",
            (sha256,),
        ).fetchall()
        return [{"id": r[0], "file_path": r[1]} for r in rows]

    def get_all_active_models(self) -> list[str]:
        """获取所有 active 状态的模型 ID 列表"""
        rows = self.conn.execute(
            "SELECT id FROM models WHERE status = 'active'"
        ).fetchall()
        return [r[0] for r in rows]

    def mark_archived(self, model_ids: list[str]):
        """批量标记为 archived（模型文件已被删除）"""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        for mid in model_ids:
            self.conn.execute(
                "UPDATE models SET status = 'archived', updated_at = ? WHERE id = ?",
                (now, mid),
            )
        self.conn.commit()

    def mark_deprecated(self, model_ids: list[str]):
        """批量标记为 deprecated"""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        for mid in model_ids:
            self.conn.execute(
                "UPDATE models SET status = 'deprecated', updated_at = ? WHERE id = ?",
                (now, mid),
            )
        self.conn.commit()

    def record_scan(self, repo_path: str, found: int, new: int, updated: int, errors: str = ""):
        """记录一次扫描"""
        self.conn.execute(
            "INSERT INTO scan_history (repo_path, models_found, new_models, updated_models, errors) VALUES (?,?,?,?,?)",
            (repo_path, found, new, updated, errors),
        )
        self.conn.commit()
