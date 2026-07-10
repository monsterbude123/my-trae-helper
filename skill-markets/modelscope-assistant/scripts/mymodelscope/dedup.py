"""
去重检测 — 基于 SHA256 找完全相同的模型文件。

策略：
1. 找出所有 SHA256 重复的模型
2. 对每组重复，建议保留路径规范的，其余用硬链接替换
"""

from .db import Database
from pathlib import Path


def find_duplicates(db: Database, repo_path: str) -> list[dict]:
    """按 SHA256 分组，找出重复组。

    返回: [{sha256: str, models: [{id, file_path, size_gb}]}]
    """
    rows = db.conn.execute("""
        SELECT sha256, id, file_path, file_size_gb
        FROM models
        WHERE status = 'active' AND sha256 != ''
        ORDER BY sha256, file_size_gb DESC
    """).fetchall()

    groups: dict[str, list[dict]] = {}
    for row in rows:
        sha = row[0]
        if sha not in groups:
            groups[sha] = []
        groups[sha].append({
            "id": row[1],
            "file_path": row[2],
            "size_gb": row[3],
        })

    duplicates = []
    for sha, models in groups.items():
        if len(models) > 1:
            duplicates.append({
                "sha256": sha,
                "models": models,
                "wasted_gb": round(sum(m["size_gb"] for m in models[1:]), 2),
            })

    duplicates.sort(key=lambda x: x["wasted_gb"], reverse=True)
    return duplicates
