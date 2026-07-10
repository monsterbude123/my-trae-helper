"""联网查询模型知识（HuggingFace + CivitAI），结果合并到本地 KB。

零外部依赖（仅用 stdlib 的 urllib + json）。

API 文档：
  HF:   https://huggingface.co/docs/hub/api
  Civit: https://developer.civitai.com/reference/api-overview

用法（被 model_kb.py 内部调用）：
    from web_kb import enrich_kb
    kb, sources = enrich_kb("flux-dev", hf_id="black-forest-labs/FLUX.1-dev",
                            civitai_id=None, hf_token=..., civitai_key=...)

公开 API（无需 key 也能调）：
    fetch_huggingface("black-forest-labs/FLUX.1-dev")
    search_civitai("FLUX.1-dev", api_key=...)
"""
import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

HF_API = "https://huggingface.co/api"
CIVITAI_API = "https://civitai.com/api/v1"


# ---- HTTP 工具 ------------------------------------------------------------

def _get(url: str, headers: dict | None = None, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, method="GET")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


# ---- HuggingFace ----------------------------------------------------------

def _hf_headers(token: str = "") -> dict:
    h = {"User-Agent": "comfyui-api-skills/1.0"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def fetch_huggingface(model_id: str, token: str = "") -> dict:
    """获取 HF 模型完整信息。model_id 形如 'black-forest-labs/FLUX.1-dev'"""
    url = f"{HF_API}/models/{model_id}"
    return _get(url, headers=_hf_headers(token))


def search_huggingface(query: str, token: str = "", limit: int = 20) -> list[dict]:
    """全库搜索。返回 [{id, tags, pipeline_tag, last_modified, downloads, likes}, ...]"""
    url = f"{HF_API}/models?search={urllib.parse.quote(query)}&limit={limit}"
    return _get(url, headers=_hf_headers(token))


def parse_hf_to_kb(raw: dict, existing: dict | None = None) -> tuple[dict, list[str]]:
    """把 HF 模型响应解析为 KB yaml 字段。

    返回 (merged_kb, changed_fields)
    """
    kb = dict(existing or {})
    changed: list[str] = []

    mid = raw.get("id", "").split("/")[-1] if raw.get("id") else ""
    if mid and kb.get("model_id") != mid:
        kb["model_id"] = mid
        changed.append("model_id")

    # 显示名：取 cardData.name 或 id
    card = raw.get("cardData") or {}
    name = card.get("name") or raw.get("id", "")
    if isinstance(name, str) and name and kb.get("display_name") != name:
        kb["display_name"] = name
        changed.append("display_name")

    # 架构：从 tags / cardData.inference / base_model 推断
    tags = [str(t).lower() for t in raw.get("tags", [])]
    base_model = (card.get("base_model") or "").lower()
    arch = None
    if "flux" in " ".join(tags) or "flux" in base_model:
        arch = "flux"
    elif "sdxl" in " ".join(tags) or "sdxl" in base_model:
        arch = "sdxl"
    elif "stable-diffusion" in tags or "stable diffusion" in base_model:
        arch = "sd1.5"
    elif "wan" in " ".join(tags) or "wan" in base_model:
        arch = "wan"
    elif "cosmos" in " ".join(tags):
        arch = "cosmos"
    elif "qwen" in " ".join(tags) or "qwen" in base_model:
        arch = "qwen"
    if arch and kb.get("architecture") in (None, "unknown", ""):
        kb["architecture"] = arch
        changed.append("architecture")

    # checkpoint 文件（从 siblings 抓 .safetensors）
    files = [s["rfilename"] for s in raw.get("siblings", [])
             if s.get("rfilename", "").endswith(".safetensors")]
    # 排除明显非主模型的（VAE/CLIP/text_encoder/tokenizer/LoRA/ControlNet/Upscaler/embedding/feature_extractor）
    skip = ("vae", "clip_", "text_encoder", "tokenizer", "scheduler",
            "lora", "controlnet", "upscaler", "embedding", "feature_extractor",
            ".fp8", ".fp16", ".int8", ".gguf", ".onnx")
    # 也排除分片主模型（transformer/diffusion_pytorch_model-NNNNN-of-NNNNN）
    ckpt_only = [f for f in files
                 if not any(s in f.lower() for s in skip)
                 and not re.search(r"-of-\d{5}\.safetensors$", f)]
    if ckpt_only:
        existing_patterns = set(kb.get("checkpoint_patterns", []) or [])
        new_patterns = [f for f in ckpt_only if f not in existing_patterns]
        if new_patterns:
            kb["checkpoint_patterns"] = list(existing_patterns) + new_patterns
            changed.append("checkpoint_patterns")

    # 触发词 / tags → notes
    triggers = card.get("trigger_phrase") or card.get("trigger_phrases")
    if triggers and "tags" not in kb:
        kb["tags"] = triggers if isinstance(triggers, list) else [triggers]
        changed.append("tags")

    # 来源标记
    src = kb.setdefault("sources", {})
    if raw.get("id"):
        src["huggingface"] = f"https://huggingface.co/{raw['id']}"
    return kb, changed


# ---- CivitAI --------------------------------------------------------------

def _civitai_headers(api_key: str = "") -> dict:
    h = {"User-Agent": "comfyui-api-skills/1.0",
         "Content-Type": "application/json"}
    if api_key:
        h["Authorization"] = f"Bearer {api_key}"
    return h


def fetch_civitai(model_id: int | str, api_key: str = "") -> dict:
    """获取 CivitAI 模型完整信息。model_id 是数字或数字字符串。"""
    url = f"{CIVITAI_API}/models/{model_id}"
    return _get(url, headers=_civitai_headers(api_key))


def search_civitai(query: str, api_key: str = "", limit: int = 20,
                   model_type: str = "") -> list[dict]:
    """搜索 CivitAI 模型。model_type ∈ Checkpoint / LORA / VAE / ...（留空不限制）"""
    import urllib.parse
    q = {"query": query, "limit": str(limit)}
    if model_type:
        q["types"] = model_type
    url = f"{CIVITAI_API}/models?{urllib.parse.urlencode(q)}"
    return _get(url, headers=_civitai_headers(api_key))


def parse_civitai_to_kb(raw: dict, existing: dict | None = None) -> tuple[dict, list[str]]:
    """把 CivitAI 模型响应解析为 KB yaml 字段。"""
    kb = dict(existing or {})
    changed: list[str] = []

    mid = str(raw.get("id", ""))
    if mid and kb.get("model_id") != mid:
        # CivitAI 模型名可能含空格和特殊字符 → 转 kebab-case
        slug = re.sub(r"[^a-z0-9]+", "-", raw.get("name", "").lower()).strip("-")
        if slug and kb.get("model_id") != slug:
            kb["model_id"] = slug
            changed.append("model_id")

    name = raw.get("name", "")
    if name and kb.get("display_name") != name:
        kb["display_name"] = name
        changed.append("display_name")

    # baseModel → architecture
    versions = raw.get("modelVersions", []) or []
    base_model = ""
    if versions:
        base_model = (versions[0].get("baseModel") or "").lower()
    arch = None
    if "flux" in base_model:
        arch = "flux"
    elif "sdxl" in base_model:
        arch = "sdxl"
    elif "sd 1" in base_model or "sd1" in base_model:
        arch = "sd1.5"
    elif "wan" in base_model:
        arch = "wan"
    elif "cosmos" in base_model:
        arch = "cosmos"
    if arch and kb.get("architecture") in (None, "unknown", ""):
        kb["architecture"] = arch
        changed.append("architecture")

    # checkpoint 文件
    seen: set[str] = set()
    ckpts: list[str] = []
    for v in versions:
        for f in v.get("files", []):
            name = f.get("name", "")
            if name.endswith((".safetensors", ".ckpt", ".pt", ".pth")) and name not in seen:
                seen.add(name)
                ckpts.append(name)
    if ckpts:
        existing_patterns = set(kb.get("checkpoint_patterns", []) or [])
        new_patterns = [f for f in ckpts if f not in existing_patterns]
        if new_patterns:
            kb["checkpoint_patterns"] = list(existing_patterns) + new_patterns
            changed.append("checkpoint_patterns")

    # 触发词（每个 version 有 trainedWords）
    triggers = set()
    for v in versions:
        for tw in (v.get("trainedWords") or []):
            if isinstance(tw, str) and tw.strip():
                triggers.add(tw.strip())
    if triggers and not kb.get("triggers"):
        kb["triggers"] = sorted(triggers)
        changed.append("triggers")

    # 来源
    src = kb.setdefault("sources", {})
    if mid:
        src["civitai"] = f"https://civitai.com/models/{mid}"

    # 描述
    desc = (raw.get("description") or "").strip()
    if desc and not kb.get("description"):
        kb["description"] = desc[:500] + ("..." if len(desc) > 500 else "")
        changed.append("description")
    return kb, changed


# ---- 一站式 enrich --------------------------------------------------------

def enrich_kb(local_id: str, *, hf_id: str = "", civitai_id: str = "",
              hf_token: str = "", civitai_key: str = "",
              existing: dict | None = None) -> tuple[dict, list[dict]]:
    """拉取并合并多源信息。

    返回 (merged_kb, sources_used)
    sources_used: [{source, ok, error, fields_changed}, ...]
    """
    kb = dict(existing or {})
    if not kb.get("model_id"):
        kb["model_id"] = local_id
    sources: list[dict] = []

    if hf_id:
        try:
            raw = fetch_huggingface(hf_id, token=hf_token)
            kb, changed = parse_hf_to_kb(raw, existing=kb)
            sources.append({"source": "huggingface", "id": hf_id, "ok": True,
                            "fields_changed": changed})
        except Exception as e:
            sources.append({"source": "huggingface", "id": hf_id, "ok": False,
                            "error": str(e)})

    if civitai_id:
        try:
            raw = fetch_civitai(civitai_id, api_key=civitai_key)
            kb, changed = parse_civitai_to_kb(raw, existing=kb)
            sources.append({"source": "civitai", "id": civitai_id, "ok": True,
                            "fields_changed": changed})
        except Exception as e:
            sources.append({"source": "civitai", "id": civitai_id, "ok": False,
                            "error": str(e)})

    return kb, sources
