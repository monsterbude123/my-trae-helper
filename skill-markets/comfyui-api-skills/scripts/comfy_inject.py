#!/usr/bin/env python3
"""修改 ComfyUI 工作流 JSON（不提交）。

支持：替换正/负提示词、采样参数、分辨率、checkpoint、保存为新文件。

用法：
    python comfy_inject.py --json Anima_01.json --positive "..." --seed 12345 --out modified.json
    python comfy_inject.py --json Anima_01.json --show     # 显示当前 sampler 节点信息
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from comfy_client import apply_overrides, find_sampler_nodes  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="修改 ComfyUI 工作流 JSON（不提交）")
    p.add_argument("-j", "--json", required=True, help="源 JSON 文件")
    p.add_argument("-o", "--out", help="输出文件路径（默认覆盖源文件）")
    p.add_argument("-p", "--positive")
    p.add_argument("-n", "--negative")
    p.add_argument("--seed", type=int)
    p.add_argument("--steps", type=int)
    p.add_argument("--cfg", type=float)
    p.add_argument("--sampler")
    p.add_argument("--scheduler")
    p.add_argument("--width", type=int)
    p.add_argument("--height", type=int)
    p.add_argument("--batch-size", type=int)
    p.add_argument("--ckpt")
    p.add_argument("--output-prefix")
    p.add_argument("--show", action="store_true", help="显示当前关键参数后退出")
    args = p.parse_args()

    src = Path(args.json)
    if not src.is_file():
        print(f"[错误] 找不到: {src}", file=sys.stderr)
        return 2
    wf = json.loads(src.read_text(encoding="utf-8"))

    sid, pos_id, neg_id = find_sampler_nodes(wf)
    if args.show:
        print(f"文件: {src}")
        print(f"节点数: {len(wf)}")
        print(f"KSampler: {sid}")
        if sid:
            ins = wf[sid]["inputs"]
            print(f"  seed={ins.get('seed')}, steps={ins.get('steps')}, cfg={ins.get('cfg')}, "
                  f"sampler={ins.get('sampler_name')}, scheduler={ins.get('scheduler')}")
        print(f"正提示词节点: {pos_id}  负提示词节点: {neg_id}")
        if pos_id:
            text = wf[pos_id]["inputs"].get("text", "")
            print(f"  positive({len(text)}字): {text[:100]}{'...' if len(text) > 100 else ''}")
        if neg_id:
            text = wf[neg_id]["inputs"].get("text", "")
            print(f"  negative({len(text)}字): {text[:100]}{'...' if len(text) > 100 else ''}")
        for nid, n in wf.items():
            if n.get("class_type") in ("SaveImage", "VHS_VideoCombine"):
                print(f"  output_prefix({nid}): {n.get('inputs', {}).get('filename_prefix')}")
        return 0

    overrides = {k: v for k, v in dict(
        positive=args.positive, negative=args.negative, seed=args.seed,
        steps=args.steps, cfg=args.cfg, sampler=args.sampler,
        scheduler=args.scheduler, width=args.width, height=args.height,
        batch_size=args.batch_size, ckpt=args.ckpt,
        output_prefix=args.output_prefix,
    ).items() if v is not None}
    if not overrides:
        print("[错误] 没有指定要修改的参数（用 --show 只看不改）", file=sys.stderr)
        return 1
    wf = apply_overrides(wf, **overrides)
    out = Path(args.out) if args.out else src
    out.write_text(json.dumps(wf, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已写入: {out}（修改: {list(overrides.keys())}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
