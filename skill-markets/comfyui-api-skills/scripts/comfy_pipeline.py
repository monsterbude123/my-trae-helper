#!/usr/bin/env python3
"""ComfyUI 工作流一键提交工具。

用法示例：
    # 1. 最简：直接提交原始 JSON
    python comfy_pipeline.py --json Anima_01.json

    # 2. 替换提示词 + 改参数
    python comfy_pipeline.py --json Anima_01.json \
        --positive "1girl, blue hair, sunset" \
        --negative "worst quality, blurry" \
        --seed 12345 --steps 30 --cfg 7 \
        --output-dir ./out --output-prefix TestRun

    # 3. 指定不同 checkpoint
    python comfy_pipeline.py --json Anima_01.json \
        --ckpt flux1-dev-fp8.safetensors --steps 25

    # 4. 只生成修改后的 JSON 不提交
    python comfy_pipeline.py --json Anima_01.json \
        --positive "..." --seed 999 --save-json modified.json --dry-run

    # 5. 远程 ComfyUI
    python comfy_pipeline.py --json Anima_01.json --url http://192.168.1.20:8188
"""
import argparse
import json
import sys
import time
from pathlib import Path

# 允许从 scripts/ 目录直接运行
sys.path.insert(0, str(Path(__file__).parent / "lib"))
from comfy_client import (  # noqa: E402
    apply_overrides, download_view, extract_output_files, get_env, load_env,
    poll_history, submit_prompt, system_stats,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="ComfyUI 工作流一键提交工具（替换 prompt / 改参 / 自动下载）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # 必填
    p.add_argument("-j", "--json", required=True, help="工作流 JSON 文件路径")

    # 提示词
    p.add_argument("-p", "--positive", help="替换正提示词（CLIPTextEncode → KSampler.positive）")
    p.add_argument("-n", "--negative", help="替换负提示词（CLIPTextEncode → KSampler.negative）")

    # 采样参数
    p.add_argument("--seed", type=int, help="随机种子")
    p.add_argument("--steps", type=int, help="采样步数")
    p.add_argument("--cfg", type=float, help="CFG 缩放")
    p.add_argument("--sampler", help="采样器名称（euler/euler_ancestral/dpmpp_2m/er_sde...）")
    p.add_argument("--scheduler", help="调度器（normal/karras/exponential/sgm_uniform...）")

    # 分辨率与批量
    p.add_argument("--width", type=int, help="图像宽度")
    p.add_argument("--height", type=int, help="图像高度")
    p.add_argument("--batch-size", type=int, help="批量大小")

    # 图像处理（非生成类 workflow，如抠图/放大）
    p.add_argument("-i", "--image", help="替换 LoadImage 节点的输入图片名（ComfyUI input 目录下）")

    # 音频生成
    p.add_argument("--audio-duration", type=float, help="音频时长（秒），如 30/60/150")
    p.add_argument("--audio-category", choices=["Music", "Instrument", "SFX", "One-shot"],
                   help="音频类别：Music=完整曲目, Instrument=乐器独奏, SFX=音效, One-shot=单次采样")
    p.add_argument("--audio-description", help="音乐/音效的文字描述（英文）")
    p.add_argument("--generate-prompt", choices=["yes", "no"],
                   help="是否用 LLM 扩展提示词（默认 yes，更快可选 no）")

    # TTS 语音合成
    p.add_argument("--tts-text", help="要朗读的文本（中文/英文均可）")
    p.add_argument("--tts-instruct", help="声音设计指令（年龄、性别、情绪、语速等描述）")
    p.add_argument("--tts-language", choices=["Chinese", "English", "Japanese", "Korean"],
                   help="语言，默认 Chinese。非必要勿动")

    # 模型与输出
    p.add_argument("--ckpt", help="替换 checkpoint / UNET 名称")
    p.add_argument("--output-prefix", help="SaveImage 的 filename_prefix")

    # 连接
    p.add_argument("--url", help=f"ComfyUI 地址（默认 {get_env('COMFYUI_URL', 'http://127.0.0.1:8188')}）")
    p.add_argument("--poll-interval", type=int, help="轮询间隔（秒），默认 5")
    p.add_argument("--timeout", type=int, help="轮询总超时（秒），默认 600")
    p.add_argument("--no-download", action="store_true", help="提交后不下载输出")
    p.add_argument("--output-dir", default="./out", help="输出目录，默认 ./out")

    # 调试
    p.add_argument("--save-json", help="把修改后的 JSON 保存到该路径")
    p.add_argument("--dry-run", action="store_true", help="只生成 JSON 不提交（与 --save-json 搭配）")
    p.add_argument("--no-health-check", action="store_true", help="跳过 /system_stats 健康检查")

    return p.parse_args()


def main() -> int:
    args = parse_args()
    env = load_env()
    url = (args.url or env.get("COMFYUI_URL") or "http://127.0.0.1:8188").rstrip("/")
    poll = args.poll_interval or int(env.get("COMFYUI_POLL_INTERVAL", "5"))
    total = args.timeout or int(env.get("COMFYUI_POLL_TIMEOUT", "600"))
    client_id = env.get("COMFYUI_CLIENT_ID", "comfyui-api-skills")

    # 1. 读 JSON
    json_path = Path(args.json)
    if not json_path.is_file():
        print(f"[错误] 找不到 JSON: {json_path}", file=sys.stderr)
        return 2
    workflow = json.loads(json_path.read_text(encoding="utf-8"))
    print(f"[1] 读取工作流: {json_path}（{len(workflow)} 个节点）")

    # 2. 应用覆盖
    overrides = dict(
        positive=args.positive, negative=args.negative, seed=args.seed,
        steps=args.steps, cfg=args.cfg, sampler=args.sampler,
        scheduler=args.scheduler, width=args.width, height=args.height,
        batch_size=args.batch_size, ckpt=args.ckpt, output_prefix=args.output_prefix,
        audio_description=args.audio_description,
        audio_duration=args.audio_duration,
        audio_category=args.audio_category,
        generate_prompt=True if args.generate_prompt == "yes" else False if args.generate_prompt == "no" else None,
        tts_text=args.tts_text,
        tts_instruct=args.tts_instruct,
        tts_language=args.tts_language,
    )
    overrides = {k: v for k, v in overrides.items() if v is not None}
    # --image：替换所有 LoadImage 节点的图片名
    if args.image:
        for nid, node in workflow.items():
            if isinstance(node, dict) and node.get("class_type") == "LoadImage":
                node.setdefault("inputs", {})["image"] = args.image
                print(f"[1.5] LoadImage({nid}) → {args.image}")
    if overrides:
        workflow = apply_overrides(workflow, **overrides)
        print(f"[2] 已应用覆盖: {list(overrides.keys())}")
    else:
        print("[2] 未指定覆盖参数，使用原始 JSON")

    # 3. 探测 sampler / 输出 prefix
    from comfy_client import find_sampler_nodes
    sid, pos_id, neg_id = find_sampler_nodes(workflow)
    if sid:
        ins = workflow[sid]["inputs"]
        print(f"    KSampler({sid}): seed={ins.get('seed')} steps={ins.get('steps')} "
              f"cfg={ins.get('cfg')} sampler={ins.get('sampler_name')} scheduler={ins.get('scheduler')}")
    prefix = next((n.get('inputs', {}).get('filename_prefix')
                   for n in workflow.values()
                   if isinstance(n, dict) and n.get('class_type') == 'SaveImage'), None)
    if prefix:
        print(f"    output_prefix: {prefix}")

    # 4. 保存 JSON
    if args.save_json:
        Path(args.save_json).write_text(
            json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[3] 已保存修改后 JSON: {args.save_json}")

    if args.dry_run:
        print("[--dry-run] 不提交，退出")
        return 0

    # 5. 健康检查
    if not args.no_health_check:
        try:
            stats = system_stats(url)
            dev = stats.get("devices", [{}])[0]
            print(f"[4] 服务 OK: ComfyUI {stats['system']['comfyui_version']} | "
                  f"GPU {dev.get('name','?').split(':')[1].strip() if ':' in dev.get('name','') else dev.get('name','?')} | "
                  f"VRAM 空闲 {dev.get('vram_free',0)/1024**3:.1f} GB")
        except Exception as e:
            print(f"[错误] 无法连接 {url}: {e}", file=sys.stderr)
            return 3

    # 6. 提交
    t0 = time.time()
    r = submit_prompt(url, workflow, client_id=client_id)
    prompt_id = r["prompt_id"]
    print(f"[5] 已提交: prompt_id={prompt_id} (queue #{r.get('number')})")

    # 7. 轮询
    entry = poll_history(url, prompt_id, interval=poll, total_timeout=total)
    elapsed = time.time() - t0
    print(f"[6] 完成！耗时 {elapsed:.1f}s")

    # 8. 下载
    files = extract_output_files(entry)
    if not files:
        print("[7] 无输出文件")
        return 0
    if args.no_download:
        print(f"[7] 输出文件（未下载）: {[f['filename'] for f in files]}")
        # 即便不下载也保存工作流到 cache（用户偏好复用）
        try:
            sys.path.insert(0, str(Path(__file__).parent / "lib"))
            from workflow_cache import save as cache_save
            ckpt_id, _, _ = find_sampler_nodes(workflow)
            ckpt_name = (workflow.get(ckpt_id, {}).get("inputs", {}).get("ckpt_name", "")
                         if ckpt_id else "")
            cache_path = cache_save(
                workflow, name=args.json, ckpt=ckpt_name,
                positive=args.positive or "", negative=args.negative or "",
                params=overrides, elapsed_sec=elapsed,
                output_files=[f["filename"] for f in files],
            )
            print(f"[8] 工作流已缓存: {cache_path}")
        except Exception as e:
            print(f"[8] 缓存失败: {e}")
        return 0
    print(f"[7] 下载 {len(files)} 个文件到 {args.output_dir}/")
    for f in files:
        dst = download_view(url, f["filename"], subfolder=f.get("subfolder", ""),
                            _type=f.get("type", "output"), out_dir=args.output_dir)
        print(f"    ✓ {dst.name} ({dst.stat().st_size/1024:.1f} KB)")
    # 9. 缓存成功的工作流（用户偏好复用）
    try:
        sys.path.insert(0, str(Path(__file__).parent / "lib"))
        from workflow_cache import save as cache_save
        from comfy_client import find_sampler_nodes
        ckpt_id, _, _ = find_sampler_nodes(workflow)
        ckpt_name = (workflow.get(ckpt_id, {}).get("inputs", {}).get("ckpt_name", "")
                     if ckpt_id else "")
        cache_path = cache_save(
            workflow, name=args.json, ckpt=ckpt_name,
            positive=args.positive or "", negative=args.negative or "",
            params=overrides, elapsed_sec=elapsed,
            output_files=[f["filename"] for f in files],
        )
        print(f"[8] 工作流已缓存: {cache_path}")
    except Exception as e:
        print(f"[8] 缓存失败（非致命）: {e}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[中断]", file=sys.stderr)
        sys.exit(130)
