"""ComfyUI 模型下载器（HF + CivitAI + KB 集成）。

基于 HF_auto_downloader_cmd.py 升级：
    - 支持 CivitAI（按 model id + version id）
    - 与 ~/.comfyui-api-skills/knowledge/models/ 集成（自动补缺失）
    - HF hub 作为依赖（更稳的元数据）；requests + tqdm 走下载
    - 文件按类型自动归类到 ComfyUI 标准目录

用法：
    # 直接给 HF URL
    python comfy_download.py "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors"

    # 给 CivitAI 模型页 URL
    python comfy_download.py "https://civitai.com/models/139562"

    # 多个链接
    python comfy_download.py URL1 URL2 URL3

    # 读 KB 补缺失（自动查 ComfyUI 已有 + KB download 段）
    python comfy_download.py --from-kb flux-dev

    # 全部 KB 缺失的模型
    python comfy_download.py --from-kb --all

    # 指定 ComfyUI 根目录
    python comfy_download.py URL --comfyui-root D:/ComfyUI
"""
import argparse
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

import requests
from tqdm import tqdm

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

# ComfyUI 标准模型目录
PATH_RULES = {
    "checkpoints": "models/checkpoints",
    "checkpoint": "models/checkpoints",
    "lora": "models/loras",
    "loras": "models/loras",
    "vae": "models/vae",
    "controlnet": "models/controlnet",
    "unet": "models/unet",
    "diffusion": "models/diffusion_models",
    "upscale": "models/upscale_models",
    "clip": "models/clip",
    "embeddings": "embeddings",
}
DEFAULT_COMFYUI_ROOT = "D:/workspace/AIGC/"  # 可被 .env 覆盖
MAX_PARALLEL = 2
MAX_RETRIES = 5
RETRY_DELAY = 3
CHUNK_SIZE = 1024 * 1024  # 1MB


# ---- 任务抽象 ------------------------------------------------------------

class DownloadTask:
    def __init__(self, url: str, source: str = "huggingface"):
        self.url = url
        self.source = source  # huggingface / civitai
        self.repo_id = ""       # HF: owner/repo
        self.civitai_model_id = 0
        self.civitai_version_id = 0
        self.filename = ""
        self.suggested_dir = "models/checkpoints"
        self.size_bytes = 0
        self.download_url = ""  # 实际下载 URL
        self.valid = False
        self.error = ""

    def inspect_hf(self):
        """HF: 解析 URL，调用 huggingface_hub 拿元数据。"""
        # /resolve/<rev>/<file> 或 /blob/<rev>/<file>
        m = re.match(
            r"https?://huggingface\.co/([^/]+/[^/]+)/(?:resolve|blob)/[^/]+/(.+)",
            self.url)
        if not m:
            self.error = f"无法解析 HF URL: {self.url}"
            return
        self.repo_id = m.group(1)
        self.filename = m.group(2).split("?")[0]
        # 实际下载 URL：/resolve/main/...
        self.download_url = (
            f"https://huggingface.co/{self.repo_id}/resolve/main/{self.filename}")
        try:
            from huggingface_hub import model_info
            info = model_info(self.repo_id)
            tags = [t.lower() for t in getattr(info, "tags", [])]
            self._classify(tags)
            for sib in info.siblings:
                if sib.rfilename == self.filename:
                    self.size_bytes = getattr(sib, "size", 0) or 0
                    break
            self.valid = True
        except Exception as e:
            self.error = f"HF 元数据获取失败: {e}"
            # fallback：按文件名猜
            self._classify_by_filename()
            self.valid = True

    def inspect_civitai(self):
        """CivitAI: 解析 URL / 数字 ID，拉元数据。"""
        # URL: https://civitai.com/models/<id> 或带 ?modelVersionId=<vid>
        m = re.match(r"https?://civitai\.com/models/(\d+)", self.url)
        if m:
            self.civitai_model_id = int(m.group(1))
            mv = re.search(r"modelVersionId=(\d+)", self.url)
            if mv:
                self.civitai_version_id = int(mv.group(1))
        elif self.url.isdigit():
            self.civitai_model_id = int(self.url)
        else:
            self.error = f"无法解析 CivitAI 引用: {self.url}"
            return
        # API 拉取
        from comfy_client import _civitai_headers, load_env
        env = load_env()
        api_key = env.get("CIVITAI_API_KEY", "") or os.environ.get("CIVITAI_API_KEY", "")
        try:
            r = requests.get(
                f"https://civitai.com/api/v1/models/{self.civitai_model_id}",
                headers=_civitai_headers(api_key), timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            self.error = f"CivitAI API 失败: {e}"
            return
        # 选 version
        versions = data.get("modelVersions", [])
        if not versions:
            self.error = "无 version"
            return
        version = next((v for v in versions if v["id"] == self.civitai_version_id),
                       versions[0])
        self.civitai_version_id = version["id"]
        # 选主文件
        files = version.get("files", [])
        safetensors = [f for f in files if f.get("name", "").endswith(".safetensors")]
        if not safetensors:
            safetensors = files
        if not safetensors:
            self.error = "无下载文件"
            return
        primary = max(safetensors, key=lambda f: f.get("sizeKB", 0) * 1024)
        self.filename = primary["name"]
        self.size_bytes = (primary.get("sizeKB") or 0) * 1024
        self.download_url = primary.get("downloadUrl", "")
        if not self.download_url:
            self.error = "无 downloadUrl"
            return
        # 分类
        t = (data.get("type", "") or "").lower()
        if t == "checkpoint":
            self.suggested_dir = "models/checkpoints"
        elif t == "lora":
            self.suggested_dir = "models/loras"
        elif t == "vae":
            self.suggested_dir = "models/vae"
        elif t == "controlnet":
            self.suggested_dir = "models/controlnet"
        elif t == "upscale" or "upscaler" in t:
            self.suggested_dir = "models/upscale_models"
        else:
            self._classify_by_filename()
        self.valid = True

    def _classify(self, tags: list[str]):
        if "lora" in tags:
            self.suggested_dir = "models/loras"
        elif "vae" in tags:
            self.suggested_dir = "models/vae"
        elif "controlnet" in tags:
            self.suggested_dir = "models/controlnet"
        else:
            self._classify_by_filename()

    def _classify_by_filename(self):
        fn = self.filename.lower()
        for kw, path in PATH_RULES.items():
            if kw in fn:
                self.suggested_dir = path
                return
        # 默认：checkpoint
        self.suggested_dir = "models/checkpoints"

    def inspect(self):
        if self.source == "civitai":
            self.inspect_civitai()
        else:
            self.inspect_hf()


# ---- 下载 ----------------------------------------------------------------

def download_one(task: DownloadTask, root: Path, position: int):
    """下载单个任务（带断点续传 + 重试）。"""
    target_dir = root / task.suggested_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    local_file = target_dir / Path(task.filename).name
    current_size = local_file.stat().st_size if local_file.exists() else 0
    if task.size_bytes > 0 and current_size >= task.size_bytes:
        return True, "Exists"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            headers = {"Authorization": f"Bearer hf_{os.environ.get('HF_TOKEN','')}"} if task.source == "huggingface" else {}
            if current_size > 0:
                headers["Range"] = f"bytes={current_size}-"
            r = requests.get(task.download_url, headers=headers, stream=True, timeout=60)
            if r.status_code == 416:
                return True, "Complete"
            r.raise_for_status()
            content_len = r.headers.get("content-length")
            total_expected = (int(content_len) + current_size) if content_len else task.size_bytes
            mode = "ab" if current_size > 0 else "wb"
            with open(local_file, mode) as f, tqdm(
                total=total_expected, initial=current_size, unit="B", unit_scale=True,
                desc=Path(task.filename).name[:15], position=position, leave=False,
                bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            ) as pbar:
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
            return True, "Success"
        except Exception as e:
            if attempt == MAX_RETRIES:
                return False, str(e)
            time.sleep(RETRY_DELAY)
            current_size = local_file.stat().st_size if local_file.exists() else 0
    return False, "Failed"


# ---- KB 集成 -------------------------------------------------------------

def kb_to_download_tasks(comfyui_root: Path) -> List[DownloadTask]:
    """从 ~/.comfyui-api-skills/knowledge/models/*.yaml 提取缺失任务。"""
    sys.path.insert(0, str(ROOT / "scripts"))
    from model_kb import resolve_kb_dir, _load_yaml
    try:
        from comfy_client import _req, load_env
        env = load_env()
        url = env.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
        installed_ckpts = set(_req(f"{url}/models/checkpoints"))
        installed_loras = set(_req(f"{url}/models/loras"))
    except Exception as e:
        print(f"[错误] 无法连接 ComfyUI: {e}", file=sys.stderr)
        return []
    tasks: List[DownloadTask] = []
    for p in sorted(resolve_kb_dir().glob("*.yaml")):
        d = _load_yaml(p)
        model_id = d.get("model_id", p.stem)
        # 跳过完全没 download 段
        for item in d.get("download", []):
            files = item.get("files", [])
            # 已装检查
            target_dir = None
            for f in files:
                base = Path(f).name
                if base in installed_ckpts:
                    target_dir = "checkpoints"
                    break
                if base in installed_loras:
                    target_dir = "loras"
                    break
            if target_dir:
                continue
            # 构造任务
            if item.get("source") == "civitai" and item.get("id"):
                tasks.append(DownloadTask(str(item["id"]), source="civitai"))
            elif item.get("source") == "huggingface":
                repo = item.get("repo", "")
                for f in files:
                    url = f"https://huggingface.co/{repo}/resolve/main/{f}"
                    t = DownloadTask(url, source="huggingface")
                    t.inspect()
                    if t.valid:
                        tasks.append(t)
        # checkpoint_patterns 里缺的也提示
        for pat in d.get("checkpoint_patterns", []):
            base = Path(pat).name
            if base in installed_ckpts or base in installed_loras:
                continue
            print(f"  [缺] {model_id}: {base}")
    return tasks


# ---- CLI -----------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="ComfyUI 模型下载器（HF + CivitAI）")
    p.add_argument("urls", nargs="*", help="HF URL / CivitAI URL / model id")
    p.add_argument("--comfyui-root", help=f"ComfyUI 根目录（默认 {DEFAULT_COMFYUI_ROOT}）")
    p.add_argument("--from-kb", help="从 KB 指定 model_id 拉取缺失文件")
    p.add_argument("--all", action="store_true", help="--from-kb 时拉所有 KB 缺失")
    p.add_argument("--parallel", type=int, default=MAX_PARALLEL)
    args = p.parse_args()

    sys.path.insert(0, str(ROOT / "scripts" / "lib"))
    from comfy_client import load_env
    env = load_env()
    root = Path(args.comfyui_root or env.get("COMFYUI_INSTALL_DIR", "") or DEFAULT_COMFYUI_ROOT)
    if not root.is_dir():
        print(f"[错误] ComfyUI 根目录不存在: {root}", file=sys.stderr)
        return 1
    print(f"[目录] ComfyUI root: {root}")

    tasks: List[DownloadTask] = []
    if args.from_kb:
        target = [] if args.all else [args.from_kb]
        print(f"[KB] 扫描 KB 缺失文件{f'（指定: {args.from_kb}）' if args.from_kb else '（全部）'}")
        all_tasks = kb_to_download_tasks(root)
        if target:
            tasks = [t for t in all_tasks if any(targ in t.url for targ in target)]
        else:
            tasks = all_tasks
    else:
        for u in args.urls:
            t = DownloadTask(u, source="civitai" if "civitai.com" in u or u.isdigit() else "huggingface")
            t.inspect()
            if not t.valid:
                print(f"[跳过] {u}: {t.error}")
                continue
            tasks.append(t)

    if not tasks:
        print("[完成] 无任务可执行")
        return 0

    # 预览
    print(f"\n{'#':<4} {'文件名':<40} {'大小':<10} {'目标目录'}")
    for i, t in enumerate(tasks):
        size = f"{t.size_bytes/(1024**2):.1f}MB" if t.size_bytes else "Unknown"
        print(f"{i:<4} {t.filename[:38]:<40} {size:<10} {t.suggested_dir}")
    if input(f"\n确认下载 {len(tasks)} 个文件? [Y/n]: ").strip().lower() == "n":
        return 0

    # 下载
    with ThreadPoolExecutor(max_workers=args.parallel) as ex:
        futures = {ex.submit(download_one, t, root, i + 1): t for i, t in enumerate(tasks)}
        ok = 0
        for fut in as_completed(futures):
            t = futures[fut]
            try:
                success, msg = fut.result()
                if success:
                    ok += 1
                    print(f"  [OK] {t.filename}  ({msg})")
                else:
                    print(f"  [FAIL] {t.filename}: {msg}")
            except Exception as e:
                print(f"  [ERROR] {t.filename}: {e}")
    print(f"\n[完成] {ok}/{len(tasks)} 成功")
    return 0 if ok == len(tasks) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[中断]")
        sys.exit(130)
