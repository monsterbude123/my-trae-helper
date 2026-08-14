"""MiniMax 共享 HTTP 客户端 — 双区域 + 指数退避 + Key 脱敏 + .env 自动加载。

所有模态脚本统一从这里导入,避免重复造轮子。
"""
from __future__ import annotations

import os
import re
import sys
import time
import json
import base64
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import requests

LOG = logging.getLogger("minimax")

CN_BASE = "https://api.minimaxi.com"
GLOBAL_BASE = "https://api.minimax.io"


def _load_dotenv() -> None:
    """从 .env 自动加载 Key(Key 值只入 os.environ,不打印、不日志)。

    查找顺序(高优先级 → 低优先级,先匹配先加载,后加载的不会覆盖):
      1. 当前工作目录 cwd/.env
      2. 调用脚本所在目录的祖先链中第一个 .env(从脚本向上找)
      3. skill 内 .env(<skill>/.env,兼容早期版本)

    标准库实现,无 python-dotenv 依赖。
    支持 # 注释、空行、KEY=value 格式(自动 strip 引号)。

    注意:已存在的环境变量优先级更高(.env 用 setdefault,不会覆盖)。
    """
    candidates: list[Path] = []
    # 1. cwd
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        candidates.append(cwd_env)
    # 2. 调用脚本的祖先链(从文件所在目录向上找)
    # 用 _load_dotenv 自身的 __file__ 定位 scripts/,再向上
    here = Path(__file__).resolve().parent
    for ancestor in [here, *here.parents]:
        env_at = ancestor / ".env"
        if env_at.exists() and env_at not in candidates:
            candidates.append(env_at)
        # 最多向上找 4 层,避免扫整个文件系统
        if ancestor == here.parent.parent.parent.parent:
            break
    # 3. 兼容:<skill>/.env 已在祖先链里,无需重复加

    for env_path in candidates:
        try:
            _parse_env_file(env_path)
        except Exception as e:
            LOG.debug("无法读取 %s:%s", env_path, e)


def _parse_env_file(env_path: Path) -> None:
    """解析 .env 文件并 setdefault 到 os.environ。"""
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # 去掉外层引号
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        # setdefault:shell 已设的优先于 .env
        os.environ.setdefault(key, value)


# 模块加载时立即执行一次
_load_dotenv()


def setup_logging(level: str = "INFO") -> None:
    """统一日志格式,中英混合。"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def mask_key(key: str) -> str:
    """API Key 脱敏:仅保留末 4 位。"""
    if not key:
        return "<empty>"
    if len(key) <= 4:
        return "*" * len(key)
    return f"{'*' * (len(key) - 4)}{key[-4:]}"


def get_credentials() -> Dict[str, Any]:
    """读取环境变量,返回 base_url + api_key + region。

    优先顺序:MINIMAX_BASE_URL(显式覆盖)> 国际 > 国内。
    """
    explicit_base = os.environ.get("MINIMAX_BASE_URL", "").strip()
    global_key = os.environ.get("MINIMAX_GLOBAL_API_KEY", "").strip()
    cn_key = os.environ.get("MINIMAX_API_KEY", "").strip()

    if explicit_base:
        base_url = explicit_base.rstrip("/")
        # 推断 region
        if "minimax.io" in base_url:
            region = "global"
            api_key = global_key or cn_key
        elif "minimaxi.com" in base_url:
            region = "cn"
            api_key = cn_key or global_key
        else:
            region = "custom"
            api_key = global_key or cn_key
    elif global_key:
        region = "global"
        base_url = GLOBAL_BASE
        api_key = global_key
    elif cn_key:
        region = "cn"
        base_url = CN_BASE
        api_key = cn_key
    else:
        raise RuntimeError(
            "未找到 API Key。请设置以下任一环境变量:\n"
            "  - MINIMAX_API_KEY(国内 api.minimaxi.com)\n"
            "  - MINIMAX_GLOBAL_API_KEY(国际 api.minimax.io)\n"
            "  - 或通过 --api-key 参数传入(不推荐,会落到 shell history)"
        )

    if not api_key:
        raise RuntimeError(f"region={region} 但 API Key 为空")

    return {
        "region": region,
        "base_url": base_url,
        "api_key": api_key,
        "timeout": int(os.environ.get("MINIMAX_TIMEOUT", "60")),
    }


def auth_headers(api_key: str, *, json_body: bool = True) -> Dict[str, str]:
    """MiniMax 同时支持 `Authorization: Bearer <key>` 和 `api-key` 头。"""
    return {
        "Authorization": f"Bearer {api_key}",
        "api-key": api_key,  # 兼容旧版接口
        **({"Content-Type": "application/json"} if json_body else {}),
    }


def request(
    method: str,
    url: str,
    *,
    headers: Dict[str, str],
    json_body: Optional[Dict[str, Any]] = None,
    timeout: int = 60,
    max_retries: int = 3,
    backoff: float = 1.5,
) -> Dict[str, Any]:
    """带指数退避的请求,失败 3 次后抛异常。

    返回 JSON dict;非 JSON 响应抛 ValueError。
    """
    last_err: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.request(
                method,
                url,
                headers=headers,
                json=json_body,
                timeout=timeout,
            )
            # 401/429 不重试
            if resp.status_code in (401, 403):
                raise PermissionError(
                    f"[{resp.status_code}] 鉴权失败 — 检查 API Key 是否有效。body={resp.text[:200]}"
                )
            if resp.status_code == 429:
                raise PermissionError(
                    f"[429] 触发限流 — 等待 {backoff ** attempt:.1f}s 后重试"
                )
            # 5xx 重试
            if resp.status_code >= 500:
                raise RuntimeError(
                    f"[{resp.status_code}] 服务端错误 — body={resp.text[:200]}"
                )

            # 2xx
            if resp.status_code >= 400:
                # 业务错误(4xx 非 401/403/429)
                try:
                    err = resp.json()
                except Exception:
                    err = {"raw": resp.text[:500]}
                raise RuntimeError(
                    f"[{resp.status_code}] {method} {url} 失败 — {json.dumps(err, ensure_ascii=False)[:300]}"
                )

            # 2xx 但可能不是 JSON(图片/音频直返 bytes 走 download_file)
            if not resp.content:
                return {}
            try:
                return resp.json()
            except ValueError:
                # 不是 JSON,返回原始文本
                return {"_raw": resp.text}

        except (requests.ConnectionError, requests.Timeout) as e:
            last_err = e
            wait = backoff ** attempt
            LOG.warning("网络异常(第 %d 次):%s — %.1fs 后重试", attempt, e, wait)
            time.sleep(wait)
        except (PermissionError,) as e:
            # 不重试
            raise
        except (RuntimeError,) as e:
            last_err = e
            wait = backoff ** attempt
            LOG.warning("业务异常(第 %d 次):%s — %.1fs 后重试", attempt, e, wait)
            time.sleep(wait)

    raise RuntimeError(f"重试 {max_retries} 次后仍失败:{last_err}")


def download_file(url: str, out_path: Path, *, timeout: int = 120) -> Path:
    """下载远程文件(视频/音频/图片)到本地。

    MiniMax 返回的 URL 有效期 9 小时,下载后立即落盘。
    """
    LOG.info("下载:%s -> %s", url, out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    return out_path


def poll_task(
    query_url: str,
    *,
    headers: Dict[str, str],
    interval: float = 5.0,
    timeout: float = 600.0,
    done_status: tuple = ("Success", "Finished", "succeeded"),
    fail_status: tuple = ("Fail", "Failed", "failed", "Failed"),
) -> Dict[str, Any]:
    """轮询异步任务直到完成 / 失败 / 超时。

    兼容两种响应结构:
      V1 风格:{"status": "Success", "file_id": "..."}
      V2 风格(H3):{"task": {"status": "succeeded", "content": {"url": "..."}}}
    """
    elapsed = 0.0
    last_status = None
    while elapsed < timeout:
        data = request("GET", query_url, headers=headers)
        # 兼容 H3 V2 嵌套结构
        inner = data.get("task") if isinstance(data.get("task"), dict) else data
        # 兼容不同接口的字段命名
        status = (
            inner.get("status")
            or inner.get("task_status")
            or inner.get("state")
            or data.get("status")
            or "Unknown"
        )
        if status != last_status:
            LOG.info("任务状态:%s (elapsed=%.1fs)", status, elapsed)
            last_status = status
        if status in done_status:
            return data
        if status in fail_status:
            raise RuntimeError(f"任务失败:status={status} body={json.dumps(data, ensure_ascii=False)[:500]}")
        time.sleep(interval)
        elapsed += interval
    raise TimeoutError(f"任务超时({timeout}s):last_status={last_status}")


def output_path(modality: str, suffix: str, explicit: Optional[str] = None) -> Path:
    """统一的产物输出路径。

    全部落 <project_root>/output/ 下,不污染项目路径。
    """
    if explicit:
        p = Path(explicit).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    out_dir = Path(__file__).resolve().parent.parent / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    return out_dir / f"{modality}_{ts}.{suffix}"


def file_to_base64(path: Path) -> str:
    """本地文件编码为 data URI(用于 vision / i2i 多模态输入)。"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在:{path}")
    ext = path.suffix.lower().lstrip(".")
    mime = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "mp4": "video/mp4",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "pdf": "application/pdf",
    }.get(ext, "application/octet-stream")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def main() -> int:
    """CLI 入口:打印当前 region + 脱敏 key(便于脚本自检)。"""
    setup_logging()
    try:
        cred = get_credentials()
        print(f"region:  {cred['region']}")
        print(f"base_url: {cred['base_url']}")
        print(f"api_key: {mask_key(cred['api_key'])}")
        print(f"timeout: {cred['timeout']}s")
        return 0
    except Exception as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())