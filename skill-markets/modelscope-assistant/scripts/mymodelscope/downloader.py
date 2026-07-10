"""
模型下载器 — 从 HF / CivitAI / ModelScope 下载模型到本地仓库。

支持：
- 从平台 ID 直接下载
- 从 URL 自动识别来源后下载
- 下载到 {repo_path}/{type_dir}/{family}/ 规范路径
- 下载完成后自动扫描入库
"""

import logging
import os
from pathlib import Path
from urllib.parse import urlparse

from .registry import HFRegistry, CivitAIClient, ModelScopeClient

logger = logging.getLogger(__name__)

# 模型类型 → 目录映射（与 scanner.py 的 DIR_TYPE_MAP 对齐）
TYPE_TO_DIR: dict[str, str] = {
    "checkpoint": "checkpoints",
    "diffusion_model": "checkpoints",
    "lora": "loras",
    "vae": "vae",
    "text_encoder": "text_encoders",
    "controlnet": "controlnet",
    "upscaler": "upscale_models",
    "llm": "llm",
    "tts": "tts",
    "asr": "asr",
    "embedding": "embeddings",
}


def _get_client(source: str):
    if source == "huggingface":
        return HFRegistry()
    elif source == "civitai":
        return CivitAIClient()
    elif source == "modelscope":
        return ModelScopeClient()
    return None


def _extract_source_and_id(url: str) -> tuple[str, str]:
    """从 URL 提取来源和模型 ID"""
    try:
        host = urlparse(url).hostname or ""
        path = urlparse(url).path.strip("/")
    except Exception:
        return "", ""

    source = ""
    if "huggingface.co" in host or "hf.co" in host:
        source = "huggingface"
        parts = path.split("/")
        if len(parts) >= 2:
            # 去掉 tree/main 等后缀
            model_parts = []
            for p in parts:
                if p in ("tree", "blob", "resolve", "main"):
                    break
                model_parts.append(p)
            return source, "/".join(model_parts[:2]) if len(model_parts) >= 2 else ""
    elif "civitai.com" in host:
        source = "civitai"
        parts = path.split("/")
        if "models" in parts:
            idx = parts.index("models")
            if idx + 1 < len(parts):
                return source, parts[idx + 1]
    elif "modelscope.cn" in host or "modelscope.ai" in host:
        source = "modelscope"
        parts = path.split("/")
        if "models" in parts:
            idx = parts.index("models")
            remaining = parts[idx + 1:]
            return source, "/".join(remaining[:2]) if len(remaining) >= 2 else ""

    return source, ""


def _target_dir(repo_path: str, model_type: str, family: str = "") -> str:
    """确定下载目标目录"""
    type_dir = TYPE_TO_DIR.get(model_type, "other")
    base = Path(repo_path) / type_dir
    if family:
        base = base / family
    base.mkdir(parents=True, exist_ok=True)
    return str(base)


def download_from_url(url: str, repo_path: str) -> dict | None:
    """从 URL 下载模型。

    返回: {source, source_id, local_path, model_type, family} 或 None
    """
    source, source_id = _extract_source_and_id(url)
    if not source or not source_id:
        logger.error("无法解析下载 URL: %s", url)
        return None

    return download_from_source(source, source_id, repo_path)


def download_from_source(source: str, source_id: str, repo_path: str, model_type: str = "") -> dict | None:
    """从指定平台下载模型。

    Args:
        source: huggingface / civitai / modelscope
        source_id: 平台模型 ID
        repo_path: 仓库根目录
        model_type: 模型类型（可选，用于确定子目录）

    返回: {source, source_id, local_path, model_type, family} 或 None
    """
    if not repo_path or not Path(repo_path).exists():
        logger.error("仓库路径不存在: %s", repo_path)
        return None

    logger.info("download_from_source: %s/%s → %s", source, source_id, repo_path)

    client = _get_client(source)
    if not client:
        logger.error("不支持的下载来源: %s", source)
        return None

    # 先获取模型信息以确定类型和家族
    info = client.get_model_info(source_id)
    if info:
        detected_type = info.get("type", "")
        family = info.get("family", "")
    else:
        detected_type = ""
        family = ""

    if model_type:
        detected_type = model_type

    # 确定目标目录
    save_dir = _target_dir(repo_path, detected_type, family)
    logger.info("下载目标目录: %s", save_dir)

    try:
        local_path = client.download(source_id, save_dir)
        if not local_path:
            logger.error("下载返回空路径")
            return None
    except Exception as e:
        logger.error("下载失败: %s", e)
        return None

    return {
        "source": source,
        "source_id": source_id,
        "local_path": local_path,
        "model_type": detected_type,
        "family": family,
    }


def download_and_index(url: str, repo_path: str, db=None) -> dict | None:
    """下载模型并自动入库。

    下载完成后调用 scanner.scan() 将新模型索引到数据库。
    """
    from .scanner import scan

    result = download_from_url(url, repo_path)
    if not result:
        return None

    if db:
        try:
            found, new, updated, deleted, errors = scan(db, repo_path)
            logger.info("扫描完成: 发现=%d 新增=%d 更新=%d 删除=%d", found, new, updated, deleted)
            result["scan"] = {"found": found, "new": new, "updated": updated, "deleted": deleted}
        except Exception as e:
            logger.warning("扫描入库失败: %s", e)

    return result
