"""
元数据解析器 — 通过 SHA256 / URL / 文件路径查询模型信息。

场景 1：用户问"磁盘上这个模型是干什么的？"
→ compute SHA256 → 查本地 DB → 查外部 registry → 返回描述

场景 2：用户给一个 URL/链接
→ 解析 URL → 识别来源 → 查 registry API → 返回元数据

场景 3：用户给本地文件
→ compute SHA256 → 查所有 registry → 匹配 → 返回元数据
"""

import hashlib
import logging
from pathlib import Path
from urllib.parse import urlparse

from .db import Database
from .registry import HFRegistry, CivitAIClient, ModelScopeClient

logger = logging.getLogger(__name__)

# URL 来源识别
SOURCE_PATTERNS = {
    "huggingface": ["huggingface.co", "hf.co"],
    "civitai": ["civitai.com"],
    "modelscope": ["modelscope.cn", "modelscope.ai"],
}


def _sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _identify_source(url: str) -> str:
    """从 URL 识别模型来源平台"""
    try:
        host = urlparse(url).hostname or ""
    except Exception:
        return ""
    for source, domains in SOURCE_PATTERNS.items():
        for domain in domains:
            if domain in host:
                return source
    return ""


def _extract_model_id(url: str, source: str) -> str:
    """从 URL 提取模型 platform ID"""
    if source == "huggingface":
        # https://huggingface.co/black-forest-labs/FLUX.1-dev
        # https://huggingface.co/black-forest-labs/FLUX.1-dev/tree/main
        parts = urlparse(url).path.strip("/").split("/")
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
    elif source == "modelscope":
        # https://modelscope.cn/models/Qwen/Qwen3-0.5B
        parts = urlparse(url).path.strip("/").split("/")
        if "models" in parts:
            idx = parts.index("models")
            if idx + 1 < len(parts):
                # 可能还有子路径
                remaining = parts[idx + 1:]
                return "/".join(remaining[:2]) if len(remaining) >= 2 else remaining[0]
    elif source == "civitai":
        # https://civitai.com/models/12345/some-model
        parts = urlparse(url).path.strip("/").split("/")
        if "models" in parts:
            idx = parts.index("models")
            if idx + 1 < len(parts):
                return parts[idx + 1]
    return ""


def _get_registry(source: str):
    """根据来源名获取对应的 registry client"""
    if source == "huggingface":
        return HFRegistry()
    elif source == "civitai":
        return CivitAIClient()
    elif source == "modelscope":
        return ModelScopeClient()
    return None


def identify_by_url(url: str) -> dict | None:
    """通过 URL 识别模型。

    返回: {model: dict, source: str, source_id: str} 或 None
    """
    source = _identify_source(url)
    if not source:
        logger.warning("无法识别 URL 来源: %s", url)
        return None

    source_id = _extract_model_id(url, source)
    if not source_id:
        logger.warning("无法从 URL 提取模型 ID: %s", url)
        return None

    logger.info("identify_by_url: source=%s source_id=%s", source, source_id)

    client = _get_registry(source)
    if not client:
        return None

    info = client.get_model_info(source_id)
    if info:
        return {"model": info, "source": source, "source_id": source_id}
    return None


def identify_by_file(filepath: str, db: Database = None) -> dict | None:
    """通过本地文件识别模型。

    流程：
    1. 计算 SHA256
    2. 查本地 DB（如果连接了）
    3. 查外部 registry（HF → CivitAI → ModelScope）

    返回: {model: dict, source: str, sha256: str, local_match: bool} 或 None
    """
    path = Path(filepath)
    if not path.exists() or not path.is_file():
        logger.warning("文件不存在: %s", filepath)
        return None

    sha256 = _sha256_file(path)
    logger.info("identify_by_file: %s sha256=%s", path.name, sha256)

    # 先查本地 DB
    if db:
        local = db.conn.execute(
            "SELECT id, name, type, family, task FROM models WHERE sha256 = ?",
            (sha256,),
        ).fetchone()
        if local:
            return {
                "model": {
                    "id": local[0],
                    "name": local[1],
                    "type": local[2],
                    "family": local[3],
                    "task": local[4],
                    "sha256": sha256,
                    "source": "local",
                },
                "source": "local",
                "sha256": sha256,
                "local_match": True,
            }

    # 查外部 registry
    registries = [
        ("huggingface", HFRegistry()),
        ("civitai", CivitAIClient()),
        ("modelscope", ModelScopeClient()),
    ]

    for name, client in registries:
        try:
            result = client.search_by_hash(sha256)
            if result:
                return {
                    "model": result,
                    "source": name,
                    "sha256": sha256,
                    "local_match": False,
                }
        except Exception as e:
            logger.debug("%s search_by_hash 失败: %s", name, e)

    # 都没有匹配 — 尝试按文件名搜索
    stem = path.stem
    for name, client in registries:
        try:
            results = client.search_by_name(stem, limit=3)
            if results:
                return {
                    "model": results[0],
                    "source": name,
                    "sha256": sha256,
                    "local_match": False,
                    "fuzzy_match": True,
                }
        except Exception as e:
            logger.debug("%s search_by_name 失败: %s", name, e)

    return {
        "sha256": sha256,
        "source": "unknown",
        "local_match": False,
        "unknown": True,
        "filename": path.name,
        "size_gb": round(path.stat().st_size / (1024**3), 4),
    }


def identify_by_sha256(sha256: str, db: Database = None) -> dict | None:
    """通过 SHA256 哈希识别模型（不依赖本地文件）。"""
    if not sha256 or len(sha256) < 8:
        return None

    logger.info("identify_by_sha256: %s", sha256)

    if db:
        local = db.conn.execute(
            "SELECT id, name, type, family, task FROM models WHERE sha256 = ?",
            (sha256,),
        ).fetchone()
        if local:
            return {
                "model": {
                    "id": local[0],
                    "name": local[1],
                    "type": local[2],
                    "family": local[3],
                    "task": local[4],
                    "sha256": sha256,
                    "source": "local",
                },
                "source": "local",
                "sha256": sha256,
                "local_match": True,
            }

    registries = [
        ("huggingface", HFRegistry()),
        ("civitai", CivitAIClient()),
    ]

    for name, client in registries:
        try:
            result = client.search_by_hash(sha256)
            if result:
                return {
                    "model": result,
                    "source": name,
                    "sha256": sha256,
                    "local_match": False,
                }
        except Exception as e:
            logger.debug("%s search_by_hash 失败: %s", name, e)

    return None


def search_online(name: str, limit: int = 5) -> dict[str, list[dict]]:
    """跨平台搜索模型（用于"我需要某类模型"场景）。

    返回: {"huggingface": [...], "civitai": [...], "modelscope": [...]}
    """
    logger.info("search_online: %s", name)
    results = {}

    registries = {
        "huggingface": HFRegistry(),
        "civitai": CivitAIClient(),
        "modelscope": ModelScopeClient(),
    }

    for src_name, client in registries.items():
        try:
            hits = client.search_by_name(name, limit=limit)
            if hits:
                results[src_name] = hits
        except Exception as e:
            logger.debug("%s search_by_name 失败: %s", name, e)

    return results
