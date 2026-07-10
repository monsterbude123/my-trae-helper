"""
模型查询引擎

支持按 task、type、family、capability、keyword 组合查询。
按 quality 评分排序，返回结构化结果供 AI 格式化输出。
"""

from .db import Database


def query(
    db: Database,
    task: str = "",
    model_type: str = "",
    family: str = "",
    capability: str = "",
    keyword: str = "",
    limit: int = 10,
) -> list[dict]:
    """查询模型列表，按质量评分降序。

    参数：
        task: 任务类型（text-to-image, tts, ...）
        model_type: 模型类型（checkpoint, lora, ...）
        family: 模型家族（flux, sdxl, qwen, ...）
        capability: 能力筛选
        keyword: 在 name/recommendations/tags 中模糊搜索
        limit: 返回条数上限
    """
    conditions = ["m.status = 'active'"]
    params = []

    if task:
        conditions.append("m.task = ?")
        params.append(task)
    if model_type:
        conditions.append("m.type = ?")
        params.append(model_type)
    if family:
        conditions.append("m.family = ?")
        params.append(family)
    if capability:
        conditions.append(
            "EXISTS (SELECT 1 FROM capabilities c WHERE c.model_id = m.id AND c.capability = ?)"
        )
        params.append(capability)
    if keyword:
        conditions.append(
            """(
                m.name LIKE ?
                OR m.notes LIKE ?
                OR EXISTS (SELECT 1 FROM recommendations r WHERE r.model_id = m.id AND r.recommendation LIKE ?)
                OR EXISTS (SELECT 1 FROM tags t WHERE t.model_id = m.id AND t.tag LIKE ?)
            )"""
        )
        kw = f"%{keyword}%"
        params.extend([kw, kw, kw, kw])

    where = " AND ".join(conditions)
    sql = f"""
        SELECT m.*,
               (SELECT AVG(score) FROM quality_scores q WHERE q.model_id = m.id) as avg_quality
        FROM models m
        WHERE {where}
        ORDER BY avg_quality DESC, m.file_size_gb ASC
        LIMIT ?
    """
    params.append(limit)

    rows = db.conn.execute(sql, params).fetchall()
    results = []
    for row in rows:
        model_id = row[0]
        caps = [
            r[0] for r in db.conn.execute(
                "SELECT capability FROM capabilities WHERE model_id = ?", (model_id,)
            ).fetchall()
        ]
        recs = [
            r[0] for r in db.conn.execute(
                "SELECT recommendation FROM recommendations WHERE model_id = ?", (model_id,)
            ).fetchall()
        ]
        tags = [
            r[0] for r in db.conn.execute(
                "SELECT tag FROM tags WHERE model_id = ?", (model_id,)
            ).fetchall()
        ]
        quality = dict(
            db.conn.execute(
                "SELECT dimension, score FROM quality_scores WHERE model_id = ?", (model_id,)
            ).fetchall()
        )
        deps = [
            {"type": r[0], "family": r[1]}
            for r in db.conn.execute(
                "SELECT dep_type, dep_family FROM dependencies WHERE model_id = ?", (model_id,)
            ).fetchall()
        ]

        results.append({
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "family": row[3],
            "task": row[4],
            "file_path": row[5],
            "file_size_gb": row[6],
            "sha256": row[7],
            "source_url": row[8],
            "license": row[9],
            "status": row[10],
            "notes": row[11],
            "avg_quality": round(row[13], 1) if row[13] else None,
            "capabilities": caps,
            "recommendations": recs,
            "tags": tags,
            "quality": quality,
            "dependencies": deps,
        })
    return results


def stats(db: Database) -> dict:
    """获取仓库统计信息"""
    total = db.conn.execute(
        "SELECT COUNT(*), SUM(file_size_gb) FROM models WHERE status = 'active'"
    ).fetchone()

    by_type = {}
    for row in db.conn.execute(
        "SELECT type, COUNT(*), SUM(file_size_gb) FROM models WHERE status = 'active' GROUP BY type"
    ).fetchall():
        by_type[row[0]] = {"count": row[1], "size_gb": round(row[2] or 0, 2)}

    by_task = {}
    for row in db.conn.execute(
        "SELECT task, COUNT(*) FROM models WHERE status = 'active' AND task != '' GROUP BY task ORDER BY COUNT(*) DESC"
    ).fetchall():
        by_task[row[0]] = row[1]

    last_scan = db.conn.execute(
        "SELECT scan_time, models_found FROM scan_history ORDER BY id DESC LIMIT 1"
    ).fetchone()

    return {
        "total_models": total[0] or 0,
        "total_size_gb": round(total[1] or 0, 2),
        "by_type": by_type,
        "by_task": by_task,
        "last_scan": last_scan[0] if last_scan else None,
    }
