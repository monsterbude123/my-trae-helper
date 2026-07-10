"""工作流缓存：把成功的工作流 JSON 保存到本地，便于复用。

位置：~/.comfyui-api-skills/cache/workflows/<name>.json

每个文件含：
    {
        "workflow": { ... },          # 应用 override 后的最终 JSON
        "meta": {
            "name": "...",
            "saved_at": "ISO",
            "params": { ... },        # 应用过的参数
            "ckpt": "...",
            "positive": "...",
            "negative": "...",
            "elapsed_sec": 12.3,
            "output_files": [...]
        }
    }
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

CACHE_DIR = Path.home() / ".comfyui-api-skills" / "cache" / "workflows"


def _safe_name(name: str) -> str:
    """生成文件名友好的 slug。"""
    s = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-")
    return s[:80] or "workflow"


def save(workflow: dict, *, name: str = "", ckpt: str = "",
         positive: str = "", negative: str = "",
         params: dict | None = None,
         elapsed_sec: float = 0,
         output_files: list | None = None) -> Path:
    """保存工作流到 cache。

    name 用作文件基础名；不传则用 timestamp。
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    base = _safe_name(name) if name else datetime.now().strftime("run_%Y%m%d_%H%M%S")
    # 同名不覆盖，加后缀
    dst = CACHE_DIR / f"{base}.json"
    n = 1
    while dst.exists():
        dst = CACHE_DIR / f"{base}_{n}.json"
        n += 1
    payload = {
        "workflow": workflow,
        "meta": {
            "name": name or base,
            "saved_at": datetime.now().isoformat(),
            "ckpt": ckpt,
            "positive": positive,
            "negative": negative,
            "params": params or {},
            "elapsed_sec": elapsed_sec,
            "output_files": output_files or [],
        },
    }
    dst.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return dst


def list_cached() -> list[dict]:
    """列出所有缓存。返回 [{name, path, saved_at, ckpt, ...}]"""
    if not CACHE_DIR.exists():
        return []
    out = []
    for p in sorted(CACHE_DIR.glob("*.json"), key=lambda x: -x.stat().st_mtime):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            meta = data.get("meta", {})
            out.append({
                "name": meta.get("name", p.stem),
                "path": p,
                "saved_at": meta.get("saved_at", ""),
                "ckpt": meta.get("ckpt", ""),
                "elapsed_sec": meta.get("elapsed_sec", 0),
            })
        except Exception:
            continue
    return out


def load(path: str | Path) -> dict:
    """读回完整 {workflow, meta}。"""
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def extract_workflow(payload: dict) -> dict:
    """从 payload 拿 workflow 字段。"""
    return payload.get("workflow", {})
