"""
知识库 — 存储模型部署文档、使用指南、应用场景等结构化知识。

场景：用户说"我想部署 Fun-CosyVoice3-0.5B-2512"
→ AI 查知识库 → 如果有 → 直接返回部署指南
→ 如果没有 → AI 从 ModelScope/HF 收集信息 → 整理 → 存入知识库

知识库表在 db.py 的 knowledge_base 表中定义。
"""

import json
import logging
from datetime import datetime, timezone

from .db import Database

logger = logging.getLogger(__name__)

KB_TABLE = "knowledge_base"

# 知识条目类型
CONTENT_TYPES = ["deployment_guide", "usage_guide", "model_info", "applications", "references", "other"]


def ensure_table(db: Database):
    """确保 knowledge_base 表存在"""
    db.conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {KB_TABLE} (
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
        )
    """)
    db.conn.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_kb_model ON {KB_TABLE}(model_name)
    """)
    db.conn.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_kb_type ON {KB_TABLE}(content_type)
    """)
    db.conn.commit()
    logger.info("知识库表已就绪")


def add_entry(
    db: Database,
    model_name: str,
    content_type: str,
    title: str,
    content: str,
    source_url: str = "",
    tags: list[str] = None,
) -> int:
    """添加知识库条目。返回条目 ID。

    Args:
        model_name: 模型名称（如 "Fun-CosyVoice3-0.5B-2512"）
        content_type: 内容类型 (deployment_guide/usage_guide/model_info/applications/references/other)
        title: 标题
        content: Markdown 格式内容
        source_url: 参考来源 URL
        tags: 标签列表
    """
    ensure_table(db)

    if content_type not in CONTENT_TYPES:
        logger.warning("未知 content_type: %s，使用 'other'", content_type)
        content_type = "other"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    tags_json = json.dumps(tags or [], ensure_ascii=False)

    try:
        db.conn.execute(
            f"INSERT INTO {KB_TABLE} (model_name, source_url, content_type, title, content, tags, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (model_name, source_url, content_type, title, content, tags_json, now, now),
        )
        db.conn.commit()
        entry_id = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        logger.info("知识库条目添加成功: id=%d model=%s type=%s title=%s", entry_id, model_name, content_type, title)
        return entry_id
    except Exception as e:
        logger.error("添加知识库条目失败: %s", e)
        return -1


def query_by_model(db: Database, model_name: str) -> list[dict]:
    """查询指定模型的所有知识库条目"""
    ensure_table(db)
    rows = db.conn.execute(
        f"SELECT id, model_name, source_url, content_type, title, content, tags, created_at "
        f"FROM {KB_TABLE} WHERE model_name = ? ORDER BY content_type, created_at",
        (model_name,),
    ).fetchall()

    return [
        {
            "id": r[0],
            "model_name": r[1],
            "source_url": r[2],
            "content_type": r[3],
            "title": r[4],
            "content": r[5],
            "tags": json.loads(r[6]) if r[6] else [],
            "created_at": r[7],
        }
        for r in rows
    ]


def query_by_type(db: Database, content_type: str, limit: int = 20) -> list[dict]:
    """按内容类型查询知识库条目"""
    ensure_table(db)
    rows = db.conn.execute(
        f"SELECT id, model_name, source_url, content_type, title, content, tags, created_at "
        f"FROM {KB_TABLE} WHERE content_type = ? ORDER BY created_at DESC LIMIT ?",
        (content_type, limit),
    ).fetchall()

    return [
        {
            "id": r[0],
            "model_name": r[1],
            "source_url": r[2],
            "content_type": r[3],
            "title": r[4],
            "content": r[5],
            "tags": json.loads(r[6]) if r[6] else [],
            "created_at": r[7],
        }
        for r in rows
    ]


def search(db: Database, keyword: str, limit: int = 20) -> list[dict]:
    """全文搜索知识库"""
    ensure_table(db)
    kw = f"%{keyword}%"
    rows = db.conn.execute(
        f"SELECT id, model_name, source_url, content_type, title, content, tags, created_at "
        f"FROM {KB_TABLE} WHERE model_name LIKE ? OR title LIKE ? OR content LIKE ? "
        f"ORDER BY created_at DESC LIMIT ?",
        (kw, kw, kw, limit),
    ).fetchall()

    return [
        {
            "id": r[0],
            "model_name": r[1],
            "source_url": r[2],
            "content_type": r[3],
            "title": r[4],
            "content": r[5],
            "tags": json.loads(r[6]) if r[6] else [],
            "created_at": r[7],
        }
        for r in rows
    ]


def list_models(db: Database) -> list[str]:
    """列出知识库中所有模型名称"""
    ensure_table(db)
    rows = db.conn.execute(
        f"SELECT DISTINCT model_name FROM {KB_TABLE} ORDER BY model_name"
    ).fetchall()
    return [r[0] for r in rows]


def delete_entry(db: Database, entry_id: int) -> bool:
    """删除知识库条目"""
    ensure_table(db)
    db.conn.execute(f"DELETE FROM {KB_TABLE} WHERE id = ?", (entry_id,))
    db.conn.commit()
    return True


def get_entry(db: Database, entry_id: int) -> dict | None:
    """获取单条知识库条目"""
    ensure_table(db)
    row = db.conn.execute(
        f"SELECT id, model_name, source_url, content_type, title, content, tags, created_at "
        f"FROM {KB_TABLE} WHERE id = ?",
        (entry_id,),
    ).fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "model_name": row[1],
        "source_url": row[2],
        "content_type": row[3],
        "title": row[4],
        "content": row[5],
        "tags": json.loads(row[6]) if row[6] else [],
        "created_at": row[7],
    }
