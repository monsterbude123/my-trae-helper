"""
ModelScope 注册表客户端

基于 modelscope SDK 或 HTTP API 实现模型搜索、信息获取和下载。
优先使用 SDK，不可用时降级为原生 HTTP 请求。

凭证来源（优先级）：
  1. 环境变量 MODELSCOPE_ACCESS_TOKEN
  2. 环境变量 MODELSCOPE_ACCESS_KEY
  无凭证时以匿名模式运行。
"""

import os
import logging
from typing import Any

from .base import RegistryClient

logger = logging.getLogger(__name__)

# ── ModelScope API 端点 ─────────────────────────────────────────
API_BASE = "https://modelscope.cn/api/v1"
MODEL_DETAIL_URL = "https://modelscope.cn/models/{}"

# ── 任务类型映射：ModelScope TaskType → 内部 model type ─────────
TASK_TYPE_MAP: dict[str, str] = {
    "text-to-image": "checkpoint",
    "image-generation": "checkpoint",
    "text-generation": "llm",
    "chat": "llm",
    "text-to-speech": "tts",
    "automatic-speech-recognition": "asr",
    "image-to-video": "diffusion_model",
    "text-to-video": "diffusion_model",
    "image-segmentation": "other",
    "object-detection": "other",
}

# ── SDK 可用性检测 ──────────────────────────────────────────────

def _has_sdk() -> bool:
    """检测 modelscope SDK 是否已安装"""
    try:
        import modelscope  # noqa: F401
        return True
    except ImportError:
        return False


def _has_requests() -> bool:
    """检测 requests 是否已安装"""
    try:
        import requests  # noqa: F401
        return True
    except ImportError:
        return False


# ── 凭据 ─────────────────────────────────────────────────────────

def _get_access_token() -> str | None:
    """从环境变量获取 ModelScope 访问令牌"""
    return os.environ.get("MODELSCOPE_ACCESS_TOKEN") or os.environ.get("MODELSCOPE_ACCESS_KEY")


# ── 类型映射 ─────────────────────────────────────────────────────

def _map_task_type(task_type: str) -> str:
    """将 ModelScope TaskType 映射为内部 model type"""
    if not task_type:
        return ""
    return TASK_TYPE_MAP.get(task_type.lower(), "other")


def _normalize_model(raw: dict[str, Any], source_id: str = "") -> dict:
    """将 API 返回的原始模型数据标准化为统一格式

    Args:
        raw: API 返回的原始字典
        source_id: 若 raw 中缺 id，使用此值

    Returns:
        标准化模型字典
    """
    model_id = raw.get("Id", raw.get("id", source_id)) or source_id
    task_type = raw.get("Data", {}).get("TaskType", "") if isinstance(raw.get("Data"), dict) else ""
    model_type = _map_task_type(task_type)

    return {
        "source": "modelscope",
        "source_id": model_id,
        "name": raw.get("Name", raw.get("ChineseName", raw.get("name", ""))),
        "type": model_type,
        "family": raw.get("Data", {}).get("ModelFamily", "") if isinstance(raw.get("Data"), dict) else "",
        "task": task_type,
        "size_gb": 0,
        "sha256": raw.get("Sha256", raw.get("sha256", "")),
        "source_url": MODEL_DETAIL_URL.format(model_id),
        "download_url": "",
        "capabilities": [],
        "tags": raw.get("Tags", []) if isinstance(raw.get("Tags"), list) else [],
        "license": raw.get("Data", {}).get("License", "") if isinstance(raw.get("Data"), dict) else "",
        "description": raw.get("Description", raw.get("description", "")),
        "version": "",
        "base_model": "",
        "raw": raw,
    }


# ── HTTP 备用实现 ────────────────────────────────────────────────

class _HTTPClient:
    """ModelScope HTTP API 最小封装"""

    def __init__(self, access_token: str | None = None):
        self.access_token = access_token
        self._session = None

    @property
    def session(self):
        if self._session is None:
            import requests
            self._session = requests.Session()
            if self.access_token:
                self._session.headers["Authorization"] = f"Bearer {self.access_token}"
        return self._session

    def _get(self, endpoint: str, params: dict | None = None) -> dict | None:
        """GET 请求，返回 JSON dict 或 None"""
        try:
            url = f"{API_BASE}/{endpoint.lstrip('/')}"
            resp = self.session.get(url, params=params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning("HTTP GET %s 失败: %s", endpoint, e)
            return None


# ── ModelScopeClient ─────────────────────────────────────────────

class ModelScopeClient(RegistryClient):
    """ModelScope 模型源客户端

    SDK 模式：使用 modelscope SDK 的 HubApi
    HTTP 模式：直接调用 ModelScope REST API
    """

    def __init__(self):
        self._access_token = _get_access_token()
        self._sdk_available = _has_sdk()
        self._requests_available = _has_requests()
        self._api: Any = None          # HubApi 实例（SDK 模式）
        self._http: _HTTPClient | None = None  # HTTP 备用客户端

        if self._sdk_available:
            try:
                from modelscope.hub.api import HubApi
                self._api = HubApi()
                if self._access_token:
                    self._api.login(self._access_token)
                    logger.info("ModelScope SDK 已就绪（登录模式）")
                else:
                    logger.info("ModelScope SDK 已就绪（匿名模式）")
            except Exception as e:
                logger.warning("ModelScope SDK 初始化失败: %s，降级为 HTTP", e)
                self._sdk_available = False

        if not self._sdk_available and self._requests_available:
            self._http = _HTTPClient(self._access_token)
            logger.info("ModelScope HTTP 客户端已就绪")

        if not self._sdk_available and not self._requests_available:
            logger.warning(
                "ModelScope 客户端不可用：请安装 modelscope（pip install modelscope）"
                " 或 requests（pip install requests）"
            )

    # ── 属性 ─────────────────────────────────────────────────

    @property
    def source_name(self) -> str:
        return "modelscope"

    # ── search_by_hash ───────────────────────────────────────

    def search_by_hash(self, sha256: str) -> dict | None:
        """通过 SHA256 搜索模型。

        ModelScope SDK/API 不直接支持 SHA256 搜索。
        策略：尝试 API 端点的 sha256 参数 → 失败则返回 None。
        调用方可基于 search_by_name 进一步验证。
        """
        if not sha256:
            return None

        logger.info("search_by_hash: sha256=%s", sha256)

        # 尝试 HTTP 端点（如果存在）
        if self._http:
            result = self._http._get("models", {"sha256": sha256})
            if result and isinstance(result, dict):
                data = result.get("Data", result)
                if isinstance(data, dict):
                    model_list = data.get("Models", data.get("models", []))
                elif isinstance(data, list):
                    model_list = data
                else:
                    model_list = []
                if model_list:
                    return _normalize_model(model_list[0])

        # SDK 没有直接的 hash 搜索方法
        if self._api:
            logger.debug("SDK 模式不支持 SHA256 直接搜索，请改用 search_by_name")
            return None

        logger.debug("未找到 SHA256=%s 的模型", sha256)
        return None

    # ── search_by_name ───────────────────────────────────────

    def _search_sdk(self, name: str, limit: int) -> list[dict]:
        """SDK 模式名称搜索"""
        try:
            result = self._api.get_models(search=name, page_size=limit)
            if not result:
                return []
            if isinstance(result, dict):
                items = result.get("Models", result.get("models", []))
            elif isinstance(result, list):
                items = result
            else:
                return []

            models = []
            for item in items[:limit]:
                source_id = item.get("Id", item.get("id", ""))
                if source_id:
                    models.append(_normalize_model(item, source_id=source_id))
            return models
        except Exception as e:
            logger.warning("SDK search_by_name 失败: %s", e)
            return []

    def _search_http(self, name: str, limit: int) -> list[dict]:
        """HTTP 模式名称搜索"""
        if not self._http:
            return []
        result = self._http._get("models", {"search": name, "limit": limit})
        if not result:
            return []

        data = result.get("Data", result)
        if isinstance(data, dict):
            items = data.get("Models", data.get("models", []))
        elif isinstance(data, list):
            items = data
        else:
            return []

        models = []
        for item in items[:limit]:
            source_id = item.get("Id", item.get("id", ""))
            if source_id:
                models.append(_normalize_model(item, source_id=source_id))
        return models

    def search_by_name(self, name: str, limit: int = 5) -> list[dict]:
        """通过名称搜索模型。

        Args:
            name: 搜索关键词
            limit: 返回结果数上限

        Returns:
            标准化模型字典列表
        """
        if not name:
            return []

        logger.info("search_by_name: name=%s limit=%d", name, limit)

        if self._sdk_available:
            return self._search_sdk(name, limit)

        if self._requests_available:
            return self._search_http(name, limit)

        logger.error("ModelScope 客户端不可用，无法搜索")
        return []

    # ── get_model_info ───────────────────────────────────────

    def _get_info_sdk(self, source_id: str) -> dict | None:
        """SDK 模式获取模型详情"""
        try:
            result = self._api.get_model_info(source_id)
            if not result:
                return None
            if isinstance(result, dict):
                return _normalize_model(result, source_id=source_id)
            return None
        except Exception as e:
            logger.warning("SDK get_model_info(%s) 失败: %s", source_id, e)
            return None

    def _get_info_http(self, source_id: str) -> dict | None:
        """HTTP 模式获取模型详情"""
        if not self._http:
            return None
        result = self._http._get(f"models/{source_id}")
        if not result:
            return None

        data = result.get("Data", result)
        if isinstance(data, dict):
            return _normalize_model(data, source_id=source_id)
        if isinstance(result, dict) and result.get("Id"):
            return _normalize_model(result, source_id=source_id)
        return None

    def get_model_info(self, source_id: str) -> dict | None:
        """获取模型详细信息。

        Args:
            source_id: 模型平台 ID（如 'Qwen/Qwen3-0.5B'）

        Returns:
            标准化模型字典或 None
        """
        if not source_id:
            return None

        logger.info("get_model_info: source_id=%s", source_id)

        if self._sdk_available:
            return self._get_info_sdk(source_id)

        if self._requests_available:
            return self._get_info_http(source_id)

        logger.error("ModelScope 客户端不可用，无法获取模型信息")
        return None

    # ── download ─────────────────────────────────────────────

    def download(self, source_id: str, save_dir: str) -> str:
        """下载模型到指定目录。

        SDK 模式：使用 modelscope.snapshot_download
        HTTP 模式不可用，提示用户安装 SDK。

        Args:
            source_id: 模型平台 ID
            save_dir: 保存目录路径

        Returns:
            模型文件本地路径
        """
        if not source_id or not save_dir:
            logger.error("download: source_id 或 save_dir 为空")
            return ""

        logger.info("download: source_id=%s save_dir=%s", source_id, save_dir)

        if self._sdk_available:
            try:
                from modelscope import snapshot_download
                local_path = snapshot_download(source_id, cache_dir=save_dir)
                logger.info("下载完成: %s", local_path)
                return str(local_path)
            except ImportError:
                try:
                    from modelscope.hub.snapshot_download import snapshot_download
                    local_path = snapshot_download(source_id, cache_dir=save_dir)
                    logger.info("下载完成: %s", local_path)
                    return str(local_path)
                except ImportError:
                    logger.error("无法导入 snapshot_download，请安装 modelscope")
                    return ""
            except Exception as e:
                logger.error("下载失败: %s", e)
                return ""

        logger.error(
            "下载功能需要 modelscope SDK，请执行: pip install modelscope"
        )
        return ""
