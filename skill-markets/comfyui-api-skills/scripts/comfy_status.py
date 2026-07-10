#!/usr/bin/env python3
"""ComfyUI 服务健康检查 + 库存速览。

用法：
    python comfy_status.py              # 查服务状态 + 已装 checkpoint/LoRA/VAE 计数
    python comfy_status.py --checkpoints # 列出所有 checkpoint
    python comfy_status.py --loras       # 列出所有 LoRA
    python comfy_status.py --json        # 原始 JSON 输出
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from comfy_client import get_env, load_env, object_info, system_stats  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="ComfyUI 服务状态 + 库存速览")
    p.add_argument("--url", help="ComfyUI 地址（默认从 .env 读）")
    p.add_argument("--checkpoints", action="store_true", help="列出所有 checkpoint")
    p.add_argument("--loras", action="store_true", help="列出所有 LoRA")
    p.add_argument("--vae", action="store_true", help="列出所有 VAE")
    p.add_argument("--diffusion", action="store_true", help="列出 diffusion_models（视频）")
    p.add_argument("--json", action="store_true", help="输出原始 JSON")
    args = p.parse_args()

    env = load_env()
    url = (args.url or env.get("COMFYUI_URL") or "http://127.0.0.1:8188").rstrip("/")

    try:
        stats = system_stats(url)
    except Exception as e:
        print(f"[错误] 无法连接 {url}: {e}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return 0

    sys_info = stats["system"]
    dev = stats["devices"][0]
    print(f"服务地址: {url}")
    print(f"ComfyUI:  {sys_info['comfyui_version']}")
    print(f"Python:   {sys_info['python_version'].split()[0]}")
    print(f"PyTorch:  {sys_info['pytorch_version']}")
    print(f"GPU:      {dev.get('name', '?')}")
    print(f"显存:     {dev.get('vram_total', 0)/1024**3:.1f} GB 总, "
          f"{dev.get('vram_free', 0)/1024**3:.1f} GB 空闲")
    if dev.get('name'):
        print(f"启动参数: {' '.join(sys_info.get('argv', [])[1:])}")

    if not any([args.checkpoints, args.loras, args.vae, args.diffusion]):
        # 默认：拉 object_info 统计数量
        try:
            oi = object_info(url)
        except Exception as e:
            print(f"[警告] 拉取 /object_info 失败: {e}")
            return 0
        print(f"\n已装节点类数: {len(oi)}")
        # 列出模型目录端点
        for ep, label in [
            ("/models/checkpoints", "checkpoint"),
            ("/models/loras", "LoRA"),
            ("/models/vae", "VAE"),
            ("/models/controlnet", "ControlNet"),
            ("/models/diffusion_models", "diffusion"),
            ("/models/upscale_models", "upscaler"),
        ]:
            try:
                from comfy_client import _req
                lst = _req(f"{url}{ep}")
                print(f"  {label:14s}: {len(lst)} 个")
            except Exception:
                pass
        return 0

    # 列出具体模型
    from comfy_client import _req
    mapping = [
        (args.checkpoints, "/models/checkpoints", "Checkpoint"),
        (args.loras, "/models/loras", "LoRA"),
        (args.vae, "/models/vae", "VAE"),
        (args.diffusion, "/models/diffusion_models", "Diffusion"),
    ]
    for flag, ep, label in mapping:
        if not flag:
            continue
        try:
            lst = _req(f"{url}{ep}")
        except Exception as e:
            print(f"[错误] {ep}: {e}", file=sys.stderr)
            continue
        print(f"\n{label} ({len(lst)} 个):")
        for name in lst:
            print(f"  - {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
