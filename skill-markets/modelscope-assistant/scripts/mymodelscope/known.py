"""
种子数据导入 — 从 known-models.yaml 导入精品模型数据到数据库。

用法：
    python -m mymodelscope.known <path-to-known-models.yaml>

在 CLI 中：
    mymodelscope import-known
"""

import logging
from pathlib import Path

import yaml

from .db import Database

logger = logging.getLogger(__name__)

# quality 维度 → DB 中 quality_scores.dimension 的映射
# known-models.yaml 用中文维度名，DB 存英文
QUALITY_DIM_MAP = {
    "realism": "realism",
    "style_flexibility": "style_flexibility",
    "speed": "speed",
    "motion_naturalness": "motion_naturalness",
    "temporal_consistency": "temporal_consistency",
    "content_accuracy": "content_accuracy",
    "speaker_similarity": "speaker_similarity",
    "naturalness": "naturalness",
    "reasoning": "reasoning",
    "coding": "coding",
    "chinese": "chinese",
    "precision": "precision",
    "semantic_understanding": "semantic_understanding",
    "accuracy": "accuracy",
    "voice_naturalness": "voice_naturalness",
}


def _load_yaml(filepath: str) -> dict:
    """加载 YAML 文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def import_known(db: Database, yaml_path: str) -> dict:
    """导入 known-models.yaml 到数据库。

    返回: {total, new, updated, skipped, errors}
    """
    path = Path(yaml_path)
    if not path.exists():
        logger.error("种子数据文件不存在: %s", yaml_path)
        return {"total": 0, "new": 0, "updated": 0, "skipped": 0, "errors": [f"文件不存在: {yaml_path}"]}

    try:
        data = _load_yaml(yaml_path)
    except Exception as e:
        logger.error("解析 YAML 失败: %s", e)
        return {"total": 0, "new": 0, "updated": 0, "skipped": 0, "errors": [str(e)]}

    models = data.get("models", [])
    total = len(models)
    new = 0
    updated = 0
    skipped = 0
    errors = []

    for entry in models:
        try:
            model_id = entry.get("id", "")
            if not model_id:
                skipped += 1
                continue

            name = entry.get("name", model_id)
            mtype = entry.get("type", "unknown")
            family = entry.get("family", "")
            task = entry.get("task", "")
            file_info = entry.get("file", {})
            source_info = entry.get("source", {})

            # 构造 model 主记录
            model_data = {
                "id": model_id,
                "name": name,
                "type": mtype,
                "family": family,
                "task": task,
                "file_path": f"{mtype}s/{family}/{file_info.get('name', '')}",
                "file_size_gb": file_info.get("size_gb", 0),
                "sha256": entry.get("sha256", ""),
                "source_url": source_info.get("url", ""),
                "license": source_info.get("license", ""),
                "status": entry.get("status", "active"),
                "notes": entry.get("notes", ""),
            }

            is_new = db.upsert_model(model_data)
            if is_new:
                new += 1
            else:
                updated += 1

            # capabilities
            caps = entry.get("capabilities", [])
            if caps:
                db.set_relations(model_id, "capabilities", caps)

            # recommendations (recommended_for)
            recs = entry.get("recommended_for", [])
            if recs:
                db.set_relations(model_id, "recommendations", recs)

            # tags
            tags = entry.get("tags", [])
            if tags:
                db.set_relations(model_id, "tags", tags)

            # quality scores
            quality = entry.get("quality", {})
            if quality:
                scores = {}
                for dim, val in quality.items():
                    db_dim = QUALITY_DIM_MAP.get(dim, dim)
                    # 1-10 评分
                    scores[db_dim] = min(10, max(1, int(val)))
                db.set_quality(model_id, scores)

            # dependencies
            deps = entry.get("dependencies", [])
            if deps:
                db.set_dependencies(model_id, deps)

            logger.info("导入模型: %s (%s)", name, "新增" if is_new else "更新")

        except Exception as e:
            logger.error("导入模型 %s 失败: %s", entry.get("id", "?"), e)
            errors.append(f"{entry.get('id', '?')}: {e}")

    logger.info("导入完成: 总计=%d 新增=%d 更新=%d 跳过=%d 错误=%d",
                total, new, updated, skipped, len(errors))

    return {
        "total": total,
        "new": new,
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
    }
