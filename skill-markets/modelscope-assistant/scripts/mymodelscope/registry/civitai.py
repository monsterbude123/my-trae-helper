"""
CivitAI API client.
Queries https://civitai.com/api/v1/ for model metadata and downloads.
"""

from __future__ import annotations

import logging
import os
import os.path
from typing import Any

import requests

from .base import RegistryClient

logger = logging.getLogger(__name__)

CIVITAI_API_BASE = "https://civitai.com/api/v1"

# ── type mapping ──────────────────────────────────────────────────────

_CIVITAI_TYPE_MAP: dict[str, str] = {
    "Checkpoint": "checkpoint",
    "LORA": "lora",
    "LoCon": "lora",
    "VAE": "vae",
    "TextualInversion": "embedding",
    "Controlnet": "controlnet",
    "Upscaler": "upscaler",
    "MotionModule": "motion",
    "AestheticGradient": "embedding",
    "Poses": "pose",
    "Wildcards": "wildcard",
    "Other": "other",
}


class CivitAIClient(RegistryClient):
    """CivitAI 模型注册表客户端。"""

    source_name = "civitai"

    def __init__(self) -> None:
        self._api_key: str | None = os.environ.get("CIVITAI_API_KEY")
        self._session = requests.Session()
        self._session.headers["User-Agent"] = "MyModelScope/1.0"

    # ── helpers ───────────────────────────────────────────────────────

    def _token_param(self) -> dict[str, str]:
        if self._api_key:
            return {"token": self._api_key}
        return {}

    def _get(self, path: str, params: dict[str, Any] | None = None, timeout: int = 30) -> requests.Response | None:
        url = f"{CIVITAI_API_BASE}{path}"
        merged: dict[str, Any] = dict(params or {})
        merged.update(self._token_param())
        try:
            resp = self._session.get(url, params=merged, timeout=timeout)
        except requests.RequestException as exc:
            logger.error("CivitAI request failed [%s]: %s", url, exc)
            return None

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After", "unknown")
            logger.warning("CivitAI rate-limited, retry-after=%s", retry_after)
            return None
        if resp.status_code == 404:
            return None
        try:
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("CivitAI HTTP error [%s]: %s", url, exc)
            return None
        return resp

    # ── public API ────────────────────────────────────────────────────

    def search_by_hash(self, sha256: str) -> dict[str, Any] | None:
        """通过 SHA256 精确搜索 CivitAI 模型版本。"""
        logger.info("CivitAI search_by_hash: %s", sha256)
        resp = self._get(f"/model-versions/by-hash/{sha256}")
        if resp is None:
            return None
        try:
            data: dict[str, Any] = resp.json()
        except ValueError:
            logger.error("CivitAI search_by_hash response is not valid JSON")
            return None
        return self._normalize(data, sha256)

    def search_by_name(self, name: str, limit: int = 5) -> list[dict[str, Any]]:
        logger.info("CivitAI search_by_name: %s limit=%d", name, limit)
        resp = self._get("/models", params={"query": name, "limit": str(limit), "n": "1"})
        if resp is None:
            return []
        try:
            data = resp.json()
        except ValueError:
            logger.error("CivitAI search_by_name response is not valid JSON")
            return []
        items: list[dict[str, Any]] = data.get("items", []) if isinstance(data, dict) else []
        return [self._normalize(item) for item in items]

    def get_model_info(self, source_id: str) -> dict[str, Any] | None:
        logger.info("CivitAI get_model_info: %s", source_id)
        resp = self._get(f"/models/{source_id}")
        if resp is None:
            return None
        try:
            data: dict[str, Any] = resp.json()
        except ValueError:
            logger.error("CivitAI get_model_info response is not valid JSON")
            return None
        return self._normalize(data)

    def download(self, source_id: str, save_dir: str) -> str:
        """下载 CivitAI 模型到本地目录。"""
        logger.info("CivitAI download: %s → %s", source_id, save_dir)
        info = self.get_model_info(source_id)
        if info is None:
            raise RuntimeError(f"Cannot fetch model info for CivitAI id={source_id}")
        download_url: str = info.get("download_url", "")
        if not download_url:
            raise RuntimeError(f"No download URL in CivitAI model {source_id}")
        os.makedirs(save_dir, exist_ok=True)
        file_name = download_url.rsplit("/", 1)[-1].split("?")[0]
        if not file_name:
            file_name = f"{source_id}.safetensors"
        local_path = os.path.join(save_dir, file_name)
        logger.info("Downloading %s → %s", download_url, local_path)
        r = self._session.get(download_url, stream=True, timeout=600)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info("CivitAI download OK: %s", local_path)
        return local_path

    # ── internal helpers ──────────────────────────────────────────────

    def _normalize(self, data: dict[str, Any], sha256: str = "") -> dict[str, Any]:
        """将 CivitAI API 原始返回归一化。

        data 可能是 model 对象或 model-version 对象（by-hash 返回的是 version）。
        """
        effective_sha = sha256

        # 判断是 model 还是 model-version
        if "modelId" in data:
            # 这是一个 model-version 对象
            version = data
            model = data.get("model", {}) if isinstance(data.get("model"), dict) else {}
            effective_sha = effective_sha or version.get("files", {}).get("sha256", "")
        else:
            # 这是一个 model 对象，取最新版本
            model = data
            versions: list[dict[str, Any]] = model.get("modelVersions", [])
            version = versions[0] if versions else {}
            effective_sha = effective_sha or version.get("files", {}).get("sha256", "")

        model_id: str = str(model.get("id", "") or data.get("id", ""))
        model_name: str = model.get("name", "") or version.get("name", "") or ""
        if not model_name:
            model_name = version.get("baseModel", "Unknown")

        # 类型映射
        raw_type: str = model.get("type", "") or version.get("baseModelType", "")
        mapped_type = _CIVITAI_TYPE_MAP.get(raw_type, raw_type.lower() if raw_type else "unknown")

        # 文件信息
        files = version.get("files", [])
        if isinstance(files, dict):
            files = [files]
        total_bytes = sum(f.get("sizeKB", 0) for f in files if isinstance(f, dict)) * 1024
        size_gb = round(total_bytes / (1024**3), 2) if total_bytes else 0.0

        # 下载 URL
        download_url = version.get("downloadUrl", "")
        if not download_url and files:
            first_file = files[0] if isinstance(files, list) else None
            download_url = (first_file or {}).get("downloadUrl", "")

        # 标签和能力
        raw_tags: list[str] = model.get("tags", []) or []
        capabilities = [t for t in raw_tags if t.lower() in {
            "text-to-image", "image-to-image", "controlnet", "inpainting", "upscaling", "lora",
        }]

        # baseModel 映射到 family
        base_model: str = version.get("baseModel", "") or ""

        description: str = (
            model.get("description", "") or version.get("description", "") or ""
        )
        if isinstance(description, str) and description:
            # 截取第一句
            description = description.split("\n")[0].strip()

        return {
            "source": "civitai",
            "source_id": model_id,
            "name": model_name,
            "type": mapped_type,
            "family": base_model,
            "task": raw_type,
            "size_gb": size_gb,
            "sha256": effective_sha,
            "source_url": f"https://civitai.com/models/{model_id}",
            "download_url": download_url,
            "capabilities": capabilities,
            "tags": raw_tags,
            "license": "",
            "description": description,
            "version": version.get("name", ""),
            "base_model": base_model,
            "raw": data,
        }
