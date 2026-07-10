"""环境自检：跑 comfyui-api-skills 之前先确认一切就绪。

检查项：
  1. Python 版本
  2. 依赖：requests / tqdm / huggingface_hub / pyyaml / Pillow
  3. 系统工具：ffmpeg / uv
  4. ComfyUI 服务连接 + /system_stats
  5. KB 目录可写
  6. .env（HF_TOKEN / CIVITAI_API_KEY 长度）
  7. ComfyUI 模型目录（ckpt / lora / vae 数量）
  8. 音频生成所需的模型（stable_audio_3_medium / qwen3.5_2b / t5gemma）

用法：
    python check_env.py                  # 全检
    python check_env.py --no-network     # 不连 ComfyUI / 联网
    python check_env.py --json           # 输出 JSON
    python check_env.py --fix            # pip 自动安装缺失包

退出码：0 = 全部通过；1 = 有 warning；2 = 有 error。
"""
import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_KB_DIR = Path.home() / ".comfyui-api-skills" / "knowledge" / "models"
CACHE_DIR = Path.home() / ".comfyui-api-skills" / "cache"

REPORT: list[dict] = []
HAS_PIP = False


def check(label: str, ok: bool, detail: str = "", fix: str = ""):
    REPORT.append({"label": label, "ok": ok, "detail": detail, "fix": fix})


# ---- 单项检查 ------------------------------------------------------------

def check_python():
    v = sys.version_info
    ok = (v.major, v.minor) >= (3, 10)
    check("Python 版本", ok,
          f"{v.major}.{v.minor}.{v.micro}",
          "需要 Python 3.10+" if not ok else "")


def _pip_install(pkg: str) -> bool:
    """尝试 pip install。返回 True 表示安装成功。"""
    global HAS_PIP
    if not HAS_PIP:
        check("pip 可用", False, "pip 不可用", "请手动安装 pip")
        return False
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg, "-q"],
            check=True, capture_output=True, timeout=120)
        return True
    except Exception as e:
        return False


def check_dep(name: str, pip_name: str = "", required: bool = True, auto_install: bool = False) -> bool:
    pip_name = pip_name or name
    try:
        m = importlib.import_module(name)
        ver = getattr(m, "__version__", "?")
        check(f"依赖: {name}", True, f"v{ver}", "")
        return True
    except ImportError:
        if auto_install:
            print(f"  [auto] 正在 pip install {pip_name} ...")
            if _pip_install(pip_name):
                check(f"依赖: {name}", True, "已自动安装", "")
                return True
        check(f"依赖: {name}", False,
              "未安装" + ("（尝试自动安装失败）" if auto_install else ""),
              f"pip install {pip_name}" if required else "可选，跳过")
        return False


def check_system_tool(name: str, check_cmd: list[str], download_url: str = "",
                      pkg_manager_hint: str = "") -> bool:
    """检查系统工具（ffmpeg / uv 等）。"""
    exe = shutil.which(name)
    if exe:
        try:
            r = subprocess.run([name] + check_cmd, capture_output=True, text=True, timeout=10)
            first_line = (r.stdout or r.stderr or "").strip().split("\n")[0][:80]
            check(f"系统工具: {name}", True, f"{exe}  {first_line}", "")
            return True
        except Exception:
            check(f"系统工具: {name}", True, f"找到 {exe}（无法执行 --version）", "")
            return True
    else:
        hints = []
        if download_url:
            hints.append(f"下载: {download_url}")
        if pkg_manager_hint:
            hints.append(pkg_manager_hint)
        fix = " | ".join(hints) if hints else f"请安装 {name} 并加入 PATH"
        check(f"系统工具: {name}", False, "未找到 (PATH 中不存在)", fix)
        return False


def check_comfyui(url: str) -> dict | None:
    try:
        sys.path.insert(0, str(ROOT / "scripts" / "lib"))
        from comfy_client import system_stats
        stats = system_stats(url)
        dev = stats.get("devices", [{}])[0]
        vram_total = dev.get("vram_total", 0) / 1024**3
        vram_free = dev.get("vram_free", 0) / 1024**3
        name = dev.get("name", "?")
        if ":" in name:
            name = name.split(":")[1].strip()
        check("ComfyUI 服务", True,
              f"{url}  v{stats['system']['comfyui_version']}  "
              f"GPU {name}  VRAM {vram_free:.1f}/{vram_total:.1f}GB", "")
        return stats
    except Exception as e:
        check("ComfyUI 服务", False, f"无法连接 {url}: {e}",
              f"确认 ComfyUI 已启动，或修改 .env COMFYUI_URL")
        return None


def check_kb_dir():
    ok = True
    detail = str(DEFAULT_KB_DIR)
    fix = ""
    if not DEFAULT_KB_DIR.exists():
        if not _can_create(DEFAULT_KB_DIR):
            ok = False
            fix = f"无法创建 {DEFAULT_KB_DIR}，检查权限"
    if DEFAULT_KB_DIR.exists() and not os.access(DEFAULT_KB_DIR, os.W_OK):
        ok = False
        fix = f"目录不可写: {DEFAULT_KB_DIR}"
    n = len(list(DEFAULT_KB_DIR.glob("*.yaml"))) if DEFAULT_KB_DIR.exists() else 0
    check("KB 目录", ok, f"{detail}（{n} 个 yaml）", fix)
    return ok


def _can_create(p: Path) -> bool:
    try:
        p.mkdir(parents=True, exist_ok=True)
        return True
    except (PermissionError, OSError):
        return False


def check_env_keys():
    sys.path.insert(0, str(ROOT / "scripts" / "lib"))
    from comfy_client import load_env
    env = load_env()
    hf = env.get("HF_TOKEN", "")
    cv = env.get("CIVITAI_API_KEY", "")
    check("HF_TOKEN", bool(hf), f"已加载（{len(hf)} 字符）" if hf else "未配置（HF 公开 API 限速低）",
          f"在 .env 加 HF_TOKEN=..." if not hf else "")
    check("CIVITAI_API_KEY", bool(cv), f"已加载（{len(cv)} 字符）" if cv else "未配置（CivitAI 限速严）",
          f"在 .env 加 CIVITAI_API_KEY=..." if not cv else "")


def check_models(url: str) -> None:
    try:
        sys.path.insert(0, str(ROOT / "scripts" / "lib"))
        from comfy_client import _req
        n_ckpt = len(_req(f"{url}/models/checkpoints"))
        n_lora = len(_req(f"{url}/models/loras"))
        n_vae = len(_req(f"{url}/models/vae"))
        check("ComfyUI 模型", True, f"checkpoint {n_ckpt}  lora {n_lora}  vae {n_vae}", "")

        # 音频模型专项检查
        audio_ckpts = _req(f"{url}/models/checkpoints")
        audio_clips = _req(f"{url}/models/text_encoders")
        needs = {
            "stable_audio_3_medium.safetensors": audio_ckpts,
            "qwen3.5_2b_bf16.safetensors": audio_clips,
            "audio\\t5gemma_b_b_ul2.safetensors": audio_clips,
        }
        for name, pool in needs.items():
            found = any(name in m.replace("/", "\\") for m in pool)
            if found:
                check(f"音频模型: {name.split('.')[0]}", True, "已安装", "")
            else:
                check(f"音频模型: {name.split('.')[0]}", False,
                      f"缺失 {name}",
                      f"用 comfy_download.py 下载，或手动放到 ComfyUI models/")
    except Exception as e:
        check("ComfyUI 模型", False, str(e), "")


def check_cache_dir():
    if not CACHE_DIR.exists():
        if not _can_create(CACHE_DIR):
            check("缓存目录", False, f"无法创建 {CACHE_DIR}", "")
            return
    check("缓存目录", True, str(CACHE_DIR), "")


# ---- 主流程 --------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="环境自检")
    p.add_argument("--no-network", action="store_true", help="跳过网络检查")
    p.add_argument("--url", help="ComfyUI 地址（默认读 .env）")
    p.add_argument("--json", action="store_true", help="JSON 输出")
    p.add_argument("--fix", action="store_true", help="pip 自动安装缺失包")
    args = p.parse_args()

    global HAS_PIP
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                       capture_output=True, check=True, timeout=10)
        HAS_PIP = True
    except Exception:
        HAS_PIP = False

    # 1. Python
    check_python()

    # 2. 系统工具
    check_system_tool("ffmpeg", ["-version"],
                      download_url="https://ffmpeg.org/download.html",
                      pkg_manager_hint="winget install ffmpeg  或  choco install ffmpeg  或  scoop install ffmpeg")
    check_system_tool("uv", ["--version"],
                      download_url="https://docs.astral.sh/uv/",
                      pkg_manager_hint="pip install uv  或  winget install astral-sh.uv")

    # 3. pip 依赖（auto_install 需 --fix）
    auto = bool(args.fix)
    check_dep("requests", required=True, auto_install=auto)
    check_dep("tqdm", required=False, auto_install=auto)
    check_dep("huggingface_hub", required=True, auto_install=auto)
    check_dep("yaml", pip_name="pyyaml", required=True, auto_install=auto)
    check_dep("PIL", pip_name="Pillow", required=False, auto_install=auto)

    # 4. KB 目录
    check_kb_dir()

    # 5. 缓存目录
    check_cache_dir()

    if not args.no_network:
        # 6. env keys
        check_env_keys()

        # 7. ComfyUI
        url = args.url
        if not url:
            sys.path.insert(0, str(ROOT / "scripts" / "lib"))
            from comfy_client import load_env
            url = load_env().get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
        stats = check_comfyui(url)
        if stats:
            check_models(url)

    # 输出
    if args.json:
        out = [{"label": r["label"], "ok": r["ok"], "detail": r["detail"]} for r in REPORT]
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        n_ok = sum(1 for r in REPORT if r["ok"])
        n_total = len(REPORT)
        print(f"\n=== 环境自检（{n_ok}/{n_total} 通过）===\n")
        for r in REPORT:
            mark = "[OK]" if r["ok"] else "[!!]"
            print(f"  {mark} {r['label']:32s} {r['detail']}")
            if not r["ok"] and r.get("fix"):
                print(f"       → {r['fix']}")
        # 区分需要手动 vs 可自动的
        manual = [r for r in REPORT if not r["ok"] and "下载:" in r.get("fix", "")]
        if manual:
            print(f"\n--- 需手动准备 ---")
            for r in manual:
                print(f"  [ ] {r['label']}: {r.get('fix','')}")
        # 整体评估
        n_err = sum(1 for r in REPORT if not r["ok"])
        if n_err == 0:
            print(f"\n[OK] 全部通过，可以正常使用")
            return 0
        else:
            print(f"\n[!!] {n_err} 项需修复（其中 pip 依赖可选 --fix 自动安装）")
            return 2


if __name__ == "__main__":
    sys.exit(main())
