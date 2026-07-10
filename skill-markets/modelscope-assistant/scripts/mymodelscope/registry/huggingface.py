"""
HuggingFace Hub API client.
Queries https://huggingface.co/api/ for model metadata and downloads.
"""

from __future__ import annotations

import logging
import os
import os.path
import re
from typing import Any

import requests

from .base import RegistryClient

logger = logging.getLogger(__name__)

HF_API_BASE = "https://huggingface.co/api"

# ── tag/pipeline_tag → unified type & capability mapping ──────────────

_TAG_TO_TYPE: dict[str, str] = {
    "text-to-image": "checkpoint",
    "image-to-image": "checkpoint",
    "text-to-video": "checkpoint",
    "image-to-video": "checkpoint",
    "text-to-3d": "checkpoint",
    "image-to-3d": "checkpoint",
    "text-generation": "llm",
    "conversational": "llm",
    "text2text-generation": "llm",
    "translation": "llm",
    "summarization": "llm",
    "text-to-speech": "tts",
    "text-to-audio": "tts",
    "automatic-speech-recognition": "asr",
    "audio-classification": "asr",
    "image-classification": "classifier",
    "object-detection": "detector",
    "image-segmentation": "segmenter",
    "fill-mask": "llm",
    "feature-extraction": "embedding",
    "sentence-similarity": "embedding",
}

_TAG_TO_CAPABILITY: dict[str, str] = {
    "text-to-image": "text-to-image",
    "image-to-image": "image-to-image",
    "text-to-video": "text-to-video",
    "text-generation": "chat",
    "conversational": "chat",
    "text-to-speech": "tts",
    "automatic-speech-recognition": "asr",
    "image-classification": "image-classification",
    "object-detection": "object-detection",
    "fill-mask": "fill-mask",
    "feature-extraction": "embedding",
    "sentence-similarity": "embedding",
}


def _infer_type(tags: list[str], pipeline_tag: str | None) -> str:
    """从 HF tags / pipeline_tag 推断模型类型。"""
    candidates: list[str] = []
    if pipeline_tag:
        candidates.append(pipeline_tag)
    for t in tags:
        candidates.append(t)
    for c in candidates:
        c_lower = c.lower().replace("_", "-")
        if c_lower in _TAG_TO_TYPE:
            return _TAG_TO_TYPE[c_lower]
    return "unknown"


def _infer_capabilities(tags: list[str], pipeline_tag: str | None) -> list[str]:
    seen: set[str] = set()
    candidates: list[str] = []
    if pipeline_tag:
        candidates.append(pipeline_tag)
    for t in tags:
        candidates.append(t)
    for c in candidates:
        c_lower = c.lower().replace("_", "-")
        cap = _TAG_TO_CAPABILITY.get(c_lower)
        if cap:
            seen.add(cap)
    # 如果没有任何识别到的 capability，把 type 作为最小 capability
    tag_types = {_TAG_TO_CAPABILITY.get(t.lower().replace("_", "-")) for t in tags}
    tag_types.discard(None)
    return sorted(seen) if seen else sorted(tag_types)


class HFRegistry(RegistryClient):
    """HuggingFace Hub 模型注册表客户端。"""

    source_name = "huggingface"

    def __init__(self) -> None:
        self._token: str | None = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
        self._session = requests.Session()
        self._session.headers["User-Agent"] = "MyModelScope/1.0"
        if self._token:
            self._session.headers["Authorization"] = f"Bearer {self._token}"

    # ── public API ────────────────────────────────────────────────────

    def search_by_hash(self, sha256: str) -> dict[str, Any] | None:
        """搜索 SHA256 哈希对应的 HF 模型。

        HF API 不直接支持按 hash 搜索，策略：
        1. 先用 hash 的前 8 位作为关键词搜索模型列表
        2. 逐个检查模型的 siblings 中有无匹配的 sha256
        """
        logger.info("HF search_by_hash: %s", sha256)
        short_hash = sha256[:8]
        url = f"{HF_API_BASE}/models"
        try:
            resp = self._session.get(url, params={"search": short_hash, "full": "true", "limit": "10"}, timeout=30)
            if resp.status_code == 429:
                logger.warning("HF API rate-limited (search_by_hash)")
                return None
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("HF search_by_hash request failed: %s", exc)
            return None

        try:
            data: list[dict[str, Any]] = resp.json()
        except ValueError:
            logger.error("HF search_by_hash response is not valid JSON")
            return None

        for model in data:
            siblings = model.get("siblings", [])
            for sib in siblings:
                if isinstance(sib, dict) and sib.get("rfilename") is not None:
                    lfs = sib.get("lfs", {}) if isinstance(sib.get("lfs"), dict) else {}
                    blob_id = sib.get("blobId")
                    flat_sha = lfs.get("sha256", "")
                    if blob_id == sha256 or flat_sha == sha256:
                        logger.info("HF matched model=%s via sibling %s", model.get("id"), sib.get("rfilename"))
                        return self._normalize(model, sha256)
        return None

    def search_by_name(self, name: str, limit: int = 5) -> list[dict[str, Any]]:
        logger.info("HF search_by_name: %s limit=%d", name, limit)
        url = f"{HF_API_BASE}/models"
        try:
            resp = self._session.get(
                url,
                params={"search": name, "full": "true", "limit": str(limit)},
                timeout=30,
            )
            if resp.status_code == 429:
                logger.warning("HF API rate-limited (search_by_name)")
                return []
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("HF search_by_name request failed: %s", exc)
            return []

        try:
            data: list[dict[str, Any]] = resp.json()
        except ValueError:
            logger.error("HF search_by_name response is not valid JSON")
            return []
        return [self._normalize(model) for model in data]

    def get_model_info(self, source_id: str) -> dict[str, Any] | None:
        logger.info("HF get_model_info: %s", source_id)
        url = f"{HF_API_BASE}/models/{source_id}"
        try:
            resp = self._session.get(url, timeout=30)
            if resp.status_code == 404:
                logger.warning("HF model not found: %s", source_id)
                return None
            if resp.status_code == 429:
                logger.warning("HF API rate-limited (get_model_info)")
                return None
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("HF get_model_info request failed: %s", exc)
            return None

        try:
            model: dict[str, Any] = resp.json()
        except ValueError:
            logger.error("HF get_model_info response is not valid JSON")
            return None
        return self._normalize(model)

    def download(self, source_id: str, save_dir: str) -> str:
        """下载 HF 模型到本地。优先使用 huggingface_hub，降级为 HTTP 流式下载。"""
        logger.info("HF download: %s → %s", source_id, save_dir)
        os.makedirs(save_dir, exist_ok=True)

        # 尝试 huggingface_hub
        try:
            import huggingface_hub  # noqa: F811
            from huggingface_hub import hf_hub_download, snapshot_download
        except ImportError:
            huggingface_hub = None  # type: ignore[assignment]
        else:
            try:
                snapshot_path = snapshot_download(
                    repo_id=source_id,
                    local_dir=save_dir,
                    token=self._token,
                )
                logger.info("HF snapshot_download OK: %s", snapshot_path)
                return snapshot_path
            except Exception as exc:
                logger.warning("snapshot_download failed, try hf_hub_download: %s", exc)
                # 尝试下载单个 known file（如 README.md 同目录推断）
                try:
                    info = self.get_model_info(source_id)
                    siblings = (info or {}).get("raw", {}).get("siblings", [])
                    for sib in siblings:
                        fname = sib.get("rfilename", "")
                        if fname and not fname.startswith("."):
                            hf_hub_download(
                                repo_id=source_id,
                                filename=fname,
                                local_dir=save_dir,
                                token=self._token,
                            )
                    logger.info("HF hf_hub_download OK for %s", source_id)
                    return save_dir
                except Exception as exc2:
                    logger.warning("hf_hub_download also failed: %s", exc2)

        # 最终降级 —— 直接 HTTP 获取 model info 后流式下载首个非隐藏文件
        logger.info("HF download fallback: direct HTTP for %s", source_id)
        info = self.get_model_info(source_id)
        if info is None:
            raise RuntimeError(f"Cannot fetch model info for {source_id}")
        siblings: list[dict[str, Any]] = (info.get("raw", {}) or {}).get("siblings", [])
        for sib in siblings:
            fname = sib.get("rfilename", "")
            if not fname or fname.startswith("."):
                continue
            dl_url = f"https://huggingface.co/{source_id}/resolve/main/{fname}"
            local_path = os.path.join(save_dir, fname)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            logger.info("Downloading %s → %s", dl_url, local_path)
            r = self._session.get(dl_url, stream=True, timeout=600)
            r.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            return save_dir
        raise RuntimeError(f"No downloadable files found for {source_id}")

    # ── internal helpers ──────────────────────────────────────────────

    def _normalize(self, model: dict[str, Any], sha256: str = "") -> dict[str, Any]:
        """将 HF API 原始返回归一化。"""
        model_id: str = model.get("id", model.get("modelId", ""))
        tags: list[str] = model.get("tags", [])
        pipeline_tag: str | None = model.get("pipeline_tag")

        mtype = _infer_type(tags, pipeline_tag)
        capabilities = _infer_capabilities(tags, pipeline_tag)

        # 文件大小
        siblings = model.get("siblings", [])
        total_bytes = sum(
            s.get("size", 0) or s.get("lfs", {}).get("size", 0)
            for s in siblings
            if isinstance(s, dict)
        )
        size_gb = round(total_bytes / (1024**3), 2) if total_bytes else 0.0

        # 下载 URL 候选（取第一个非隐藏文件）
        download_url: str = ""
        main_file: str = ""
        for sib in siblings:
            if isinstance(sib, dict):
                fname = sib.get("rfilename", "") or ""
                if fname and not fname.startswith(".") and not main_file:
                    main_file = fname
        if main_file:
            download_url = f"https://huggingface.co/{model_id}/resolve/main/{main_file}"

        card_data = model.get("cardData", {}) or {}
        if isinstance(card_data, dict):
            license_name = str(card_data.get("license", "") or "")
        else:
            license_name = ""

        # SHA256: 如果给了就用，否则从 siblings 里取第一个 lfs sha256
        effective_sha = sha256
        if not effective_sha:
            for sib in siblings:
                if isinstance(sib, dict):
                    lfs = sib.get("lfs", {}) if isinstance(sib.get("lfs"), dict) else {}
                    s = lfs.get("sha256", "")
                    if s:
                        effective_sha = s
                        break

        return {
            "source": "huggingface",
            "source_id": model_id,
            "name": model_id.rsplit("/", 1)[-1],
            "type": mtype,
            "family": "",
            "task": pipeline_tag or "",
            "size_gb": size_gb,
            "sha256": effective_sha,
            "source_url": f"https://huggingface.co/{model_id}",
            "download_url": download_url,
            "capabilities": capabilities,
            "tags": tags,
            "license": license_name,
            "description": self._pick_description(model),
            "version": "",
            "base_model": "",
            "raw": model,
        }

    @staticmethod
    def _pick_description(model: dict[str, Any]) -> str:
        card_data = model.get("cardData", {}) or {}
        if isinstance(card_data, dict):
            desc = card_data.get("description", "") or ""
            if desc:
                return desc.split("\n")[0].strip()
        pipeline_tag = model.get("pipeline_tag", "")
        model_id = model.get("id", "")
        return f"{pipeline_tag} model: {model_id}"
