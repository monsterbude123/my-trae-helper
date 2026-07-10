"""ComfyUI HTTP 客户端（标准库，零依赖）。

公共函数：
    load_env()              - 解析 .env（多路径自动发现）
    get_env(key, default)   - 读单个变量
    system_stats(url)       - 健康检查
    object_info(url)        - 已装节点清单
    submit_prompt(url, ...) - 提交工作流
    poll_history(url, ...)  - 轮询直到完成
    download_view(url, ...) - 下载输出
"""
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


# ---- .env 解析 ------------------------------------------------------------

# 极简 .env 解析：KEY=VALUE，支持 # 注释与空行。
# 用法：先 `cd` 到含 .env 的目录，再调用 `load_env()` —— 默认读当前目录 .env。
# 也支持传 path 参数或环境变量 COMFYUI_ENV_FILE 指定文件。
# 进程环境变量永远最后覆盖。

ENV_FILE_VAR = "COMFYUI_ENV_FILE"


def _parse_env_file(p: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not p.is_file():
        return env
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def load_env(path: str | Path | None = None) -> dict[str, str]:
    """极简 .env 解析。

    解析顺序（早出现优先，后面的不覆盖前面的）：
        1. path 参数
        2. 环境变量 COMFYUI_ENV_FILE 指定的文件
        3. CWD/.env
    最后：进程环境变量覆盖一切。
    """
    parsed: dict[str, str] = {}
    if path:
        paths: list[Path] = [Path(path)]
    else:
        env_file = os.environ.get(ENV_FILE_VAR)
        paths = [Path(env_file), Path.cwd() / ".env"] if env_file else [Path.cwd() / ".env"]
    for p in paths:
        for k, v in _parse_env_file(p).items():
            if k not in parsed:
                parsed[k] = v
    # 进程环境覆盖
    for k, v in os.environ.items():
        parsed[k] = v
    return parsed


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key) or default


# ---- HTTP 工具 ------------------------------------------------------------

def _req(url: str, data: bytes | None = None, timeout: int = 30,
         method: str = "GET") -> dict | list:
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


# ---- ComfyUI 接口 ---------------------------------------------------------

def system_stats(url: str) -> dict:
    return _req(f"{url}/system_stats")


def object_info(url: str) -> dict:
    return _req(f"{url}/object_info")


def submit_prompt(url: str, workflow: dict, client_id: str = "comfyui-api-skills",
                  timeout: int = 30) -> dict:
    payload = json.dumps({"prompt": workflow, "client_id": client_id}).encode()
    return _req(f"{url}/prompt", data=payload, timeout=timeout, method="POST")


def poll_history(url: str, prompt_id: str, interval: int = 5,
                 total_timeout: int = 600) -> dict:
    """轮询直到 status.completed=true 或出错。返回完整 history 节点。"""
    deadline = time.time() + total_timeout
    n = 0
    while time.time() < deadline:
        n += 1
        h = _req(f"{url}/history/{prompt_id}")
        if prompt_id in h:
            entry = h[prompt_id]
            if entry.get("status", {}).get("completed"):
                return entry
            errs = [m for m in entry.get("status", {}).get("messages", [])
                    if m and m[0] == "execution_error"]
            if errs:
                raise RuntimeError(f"执行错误: {errs[0][1].get('exception_message', errs)}")
        print(f"  轮询 #{n} 仍执行中... ({int(deadline - time.time())}s 剩余)")
        time.sleep(interval)
    raise TimeoutError(f"轮询 {total_timeout}s 仍未完成")


def download_view(url: str, filename: str, subfolder: str = "",
                  _type: str = "output", out_dir: str | Path = ".",
                  timeout: int = 60) -> Path:
    """下载 /view 资源到本地，返回保存路径。"""
    from urllib.parse import urlencode
    qs = urlencode({"filename": filename, "subfolder": subfolder, "type": _type})
    full = f"{url}/view?{qs}"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / filename
    req = urllib.request.Request(full)
    with urllib.request.urlopen(req, timeout=timeout) as r, open(dst, "wb") as f:
        f.write(r.read())
    return dst


# ---- 工作流改参工具 -------------------------------------------------------

def find_sampler_nodes(workflow: dict) -> tuple[str | None, str | None, str | None]:
    """定位 KSampler 节点，返回 (sampler_id, positive_clip_id, negative_clip_id)。

    支持 KSampler / KSamplerAdvanced / SamplerCustom 等所有 *_sampler 字段指向
    model/positive/negative 的节点（启发式：找 inputs 含 positive+negative+model）。
    无 KSampler 的工作流（如放大/抠图）返回 (None, None, None)。
    """
    for nid, node in workflow.items():
        if not isinstance(node, dict):  # 跳过 _note / _meta 字符串
            continue
        ins = node.get("inputs", {})
        if all(k in ins for k in ("positive", "negative", "model", "latent_image")):
            pos = ins["positive"]
            neg = ins["negative"]
            if isinstance(pos, list) and len(pos) == 2 and isinstance(neg, list) and len(neg) == 2:
                return nid, pos[0], neg[0]
    return None, None, None


def find_text_nodes(workflow: dict) -> tuple[str | None, str | None]:
    """定位一对 CLIPTextEncode 节点：通过 sampler 找到 positive/negative 文本节点。"""
    _, pos_id, neg_id = find_sampler_nodes(workflow)
    return pos_id, neg_id


def find_latent_node(workflow: dict, sampler_id: str | None) -> str | None:
    if not sampler_id:
        return None
    ins = workflow.get(sampler_id, {}).get("inputs", {})
    lat = ins.get("latent_image")
    if isinstance(lat, list) and len(lat) == 2:
        return lat[0]
    return None


def find_checkpoint_node(workflow: dict, sampler_id: str | None) -> str | None:
    """回溯 model input 到 CheckpointLoaderSimple 节点。"""
    if not sampler_id:
        return None
    seen = set()
    cur = workflow.get(sampler_id, {}).get("inputs", {}).get("model")
    while isinstance(cur, list) and len(cur) == 2 and cur[0] not in seen:
        seen.add(cur[0])
        node = workflow.get(cur[0], {})
        ct = node.get("class_type", "")
        ins = node.get("inputs", {})
        if "CheckpointLoader" in ct or "UNETLoader" in ct:
            return cur[0]
        if "MODEL" in ins or "model" in ins:
            cur = ins.get("MODEL") or ins.get("model")
        else:
            break
    return None


def apply_overrides(workflow: dict, *, positive: str | None = None,
                    negative: str | None = None, seed: int | None = None,
                    steps: int | None = None, cfg: float | None = None,
                    sampler: str | None = None, scheduler: str | None = None,
                    width: int | None = None, height: int | None = None,
                    batch_size: int | None = None,
                    ckpt: str | None = None,
                    output_prefix: str | None = None,
                    # 音频生成
                    audio_description: str | None = None,
                    audio_duration: float | None = None,
                    audio_category: str | None = None,
                    generate_prompt: bool | None = None,
                    # TTS 语音合成
                    tts_text: str | None = None,
                    tts_instruct: str | None = None,
                    tts_language: str | None = None) -> dict:
    """根据参数原地修改 workflow，并返回（也支持链式 .copy() 后再传）。"""
    w = workflow
    sampler_id, pos_id, neg_id = find_sampler_nodes(w)
    lat_id = find_latent_node(w, sampler_id)
    ckpt_id = find_checkpoint_node(w, sampler_id)

    if pos_id and positive is not None:
        w[pos_id]["inputs"]["text"] = positive
    if neg_id and negative is not None:
        w[neg_id]["inputs"]["text"] = negative

    if sampler_id:
        ins = w[sampler_id]["inputs"]
        if seed is not None:
            ins["seed"] = int(seed)
        if steps is not None:
            ins["steps"] = int(steps)
        if cfg is not None:
            ins["cfg"] = float(cfg)
        if sampler is not None:
            ins["sampler_name"] = sampler
        if scheduler is not None:
            ins["scheduler"] = scheduler

    if lat_id:
        ins = w[lat_id]["inputs"]
        if width is not None:
            ins["width"] = int(width)
        if height is not None:
            ins["height"] = int(height)
        if batch_size is not None:
            ins["batch_size"] = int(batch_size)

    if ckpt_id and ckpt is not None:
        ins = w[ckpt_id]["inputs"]
        for k in ("ckpt_name", "unet_name"):
            if k in ins:
                ins[k] = ckpt
                break

    if output_prefix is not None:
        for nid, node in w.items():
            if not isinstance(node, dict):
                continue
            if node.get("class_type") == "SaveImage":
                node.setdefault("inputs", {})["filename_prefix"] = output_prefix
            elif node.get("class_type") == "VHS_VideoCombine":
                node.setdefault("inputs", {})["filename_prefix"] = output_prefix
            elif node.get("class_type") == "SaveAudioMP3":
                node.setdefault("inputs", {})["filename_prefix"] = output_prefix
            elif node.get("class_type") == "SaveAudio":
                node.setdefault("inputs", {})["filename_prefix"] = output_prefix

    # 音频生成覆盖
    for nid, node in w.items():
        if not isinstance(node, dict):
            continue
        ct = node.get("class_type", "")
        if ct == "PrimitiveStringMultiline" and audio_description is not None:
            node.setdefault("inputs", {})["value"] = audio_description
        elif ct == "PrimitiveFloat" and audio_duration is not None:
            node.setdefault("inputs", {})["value"] = float(audio_duration)
        elif ct == "CustomCombo" and audio_category is not None:
            ins = node.setdefault("inputs", {})
            ins["choice"] = audio_category
            # 找匹配的 option index
            for i in range(1, 6):
                opt = ins.get(f"option{i}", "")
                if opt == audio_category:
                    ins["index"] = i - 1
                    break
        elif ct == "PrimitiveBoolean" and generate_prompt is not None:
            node.setdefault("inputs", {})["value"] = bool(generate_prompt)

    # TTS 覆盖
    for nid, node in w.items():
        if not isinstance(node, dict):
            continue
        ct = node.get("class_type", "")
        if ct == "FB_Qwen3TTSVoiceDesign":
            ins = node.setdefault("inputs", {})
            if tts_text is not None:
                ins["text"] = tts_text
            if tts_instruct is not None:
                ins["instruct"] = tts_instruct
            if tts_language is not None:
                ins["language"] = tts_language

    return w


def extract_output_files(history_entry: dict) -> list[dict]:
    """从 history entry 提取所有输出文件。"""
    out = []
    for nid, out_data in history_entry.get("outputs", {}).items():
        for k in ("images", "gifs", "videos", "audio"):
            for f in out_data.get(k, []):
                out.append(f)
    return out
