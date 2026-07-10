"""矩阵测试工具：跑参数矩阵，把结果整理成对比表。

用法：
    # 简单矩阵
    python comfy_matrix.py --json Anima_01.json \\
        --axes "seed:1,2,3" "cfg:3,4,5" --output-dir ./matrix_test

    # 多个轴
    python comfy_matrix.py --json Anima_01.json \\
        --axes "sampler:er_sde,euler" "scheduler:normal,karras" \\
        --output-dir ./matrix_test

    # 每个组合只跑一次（默认 1）
    python comfy_matrix.py --json Anima_01.json --axes "seed:100,200,300,400" --output-dir ./m

结果：
    output_dir/
    ├── summary.json     # 每个 run 的关键参数 + 状态 + 耗时
    ├── summary.md       # 表格对比
    ├── <run_name>.png   # 生成的图
    └── log.txt          # 完整日志
"""
import argparse
import itertools
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from comfy_client import (  # noqa: E402
    apply_overrides, download_view, extract_output_files, get_env, load_env,
    poll_history, submit_prompt, system_stats,
)


def parse_axes(specs: list[str]) -> list[tuple[str, list]]:
    """解析 --axes "name:v1,v2" 列表"""
    axes = []
    for s in specs:
        if ":" not in s:
            print(f"[错误] axis 格式错误（需 name:v1,v2）: {s}", file=sys.stderr)
            sys.exit(2)
        name, vals = s.split(":", 1)
        vals = [v.strip() for v in vals.split(",") if v.strip()]
        # 类型转换
        if name in ("seed", "steps", "width", "height", "batch_size", "batch-size"):
            try:
                vals = [int(v) for v in vals]
            except ValueError:
                pass
        elif name in ("cfg", "denoise"):
            try:
                vals = [float(v) for v in vals]
            except ValueError:
                pass
        axes.append((name, vals))
    return axes


def expand_combinations(axes: list[tuple[str, list]]) -> list[dict]:
    """笛卡尔积展开为参数组合列表"""
    names = [a[0] for a in axes]
    pools = [a[1] for a in axes]
    out = []
    for combo in itertools.product(*pools):
        d = dict(zip(names, combo))
        # 短横线转下划线（与 comfy_pipeline.py 一致）
        if "batch-size" in d:
            d["batch_size"] = d.pop("batch-size")
        out.append(d)
    return out


def slug(d: dict) -> str:
    """把参数组合压缩为文件名友好的字符串。"""
    return "_".join(f"{k}-{v}" for k, v in sorted(d.items()))


def main() -> int:
    p = argparse.ArgumentParser(description="矩阵测试工具")
    p.add_argument("-j", "--json", required=True, help="工作流 JSON")
    p.add_argument("--axes", nargs="+", required=True,
                   help='参数轴，如 "seed:1,2,3" "cfg:4,5"')
    p.add_argument("--output-dir", required=True, help="结果目录")
    p.add_argument("--name", default="matrix", help="矩阵名（用于子目录）")
    p.add_argument("--prompt", help="覆盖正提示词")
    p.add_argument("--negative", help="覆盖负提示词")
    p.add_argument("--url")
    p.add_argument("--poll-interval", type=int, default=5)
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--prefix", default="mtx", help="输出文件名前缀")
    p.add_argument("--stop-on-fail", action="store_true", help="遇错即停")
    p.add_argument("--summary-only", action="store_true", help="不下载图片，只记录元数据")
    args = p.parse_args()

    env = load_env()
    url = (args.url or env.get("COMFYUI_URL") or "http://127.0.0.1:8188").rstrip("/")
    poll = args.poll_interval or int(env.get("COMFYUI_POLL_INTERVAL", "5"))
    total = args.timeout or int(env.get("COMFYUI_POLL_TIMEOUT", "600"))

    base_wf = json.loads(Path(args.json).read_text(encoding="utf-8"))
    axes = parse_axes(args.axes)
    combos = expand_combinations(axes)

    out_dir = Path(args.output_dir) / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "log.txt"
    summary: list[dict] = []

    print(f"\n== 矩阵测试 ==")
    print(f"JSON:     {args.json}")
    print(f"轴:       {args.axes}")
    print(f"组合:     {len(combos)}")
    print(f"输出:     {out_dir}")
    print(f"URL:      {url}\n")

    log_lines = []
    log_lines.append(f"# 矩阵测试 {datetime.now().isoformat()}")
    log_lines.append(f"JSON={args.json}")
    log_lines.append(f"AXES={args.axes}")
    log_lines.append(f"COMBOS={len(combos)}")
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    # 健康检查
    try:
        stats = system_stats(url)
        print(f"[健康] ComfyUI {stats['system']['comfyui_version']}\n")
    except Exception as e:
        print(f"[错误] {e}", file=sys.stderr)
        return 3

    for i, combo in enumerate(combos, 1):
        wf = json.loads(json.dumps(base_wf))  # deep copy
        if args.prompt is not None:
            combo = {"positive": args.prompt, **combo}
        if args.negative is not None:
            combo = {"negative": args.negative, **combo}
        # 写 prefix
        combo = {"output_prefix": f"{args.prefix}_{i:02d}", **combo}

        run_name = f"{i:02d}_{slug(combo)}"
        print(f"[{i:02d}/{len(combos)}] {run_name}")
        record = {"idx": i, "name": run_name, "params": combo, "ok": False}
        try:
            wf = apply_overrides(wf, **{k: v for k, v in combo.items() if v is not None})
            t0 = time.time()
            r = submit_prompt(url, wf, client_id="comfy-matrix")
            pid = r["prompt_id"]
            entry = poll_history(url, pid, interval=poll, total_timeout=total)
            elapsed = time.time() - t0
            files = extract_output_files(entry)
            record.update({
                "ok": True, "prompt_id": pid, "queue": r.get("number"),
                "elapsed_sec": round(elapsed, 1), "output_files": [f["filename"] for f in files],
            })
            if not args.summary_only:
                for f in files:
                    dst = out_dir / f"{run_name}_{f['filename']}"
                    try:
                        download_view(url, f["filename"], subfolder=f.get("subfolder", ""),
                                      _type=f.get("type", "output"), out_dir=dst.parent)
                        # 下载到 dst
                        (dst.parent / f["filename"]).rename(dst)
                        record.setdefault("downloaded", []).append(dst.name)
                    except Exception as e:
                        record["download_error"] = str(e)
            print(f"        ✓ {elapsed:.1f}s  {[f['filename'] for f in files]}")
        except Exception as e:
            record["error"] = str(e)
            print(f"        ✗ {e}")
            if args.stop_on_fail:
                summary.append(record)
                break
        summary.append(record)
        # 增量保存
        (out_dir / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"\n[{i:02d}] {run_name}: {record.get('ok')} {record.get('error', '')}\n")

    # 生成 markdown 表格
    md = ["# 矩阵测试结果\n",
          f"- JSON: `{args.json}`",
          f"- 时间: {datetime.now().isoformat()}",
          f"- 组合: {len(combos)}（成功 {sum(1 for r in summary if r['ok'])}）\n",
          "| # | 状态 | 耗时 | 参数 | prompt_id | 输出 |",
          "|---|------|------|------|-----------|------|"]
    for r in summary:
        status = "✓" if r["ok"] else "✗"
        params = ", ".join(f"{k}={v}" for k, v in sorted(r["params"].items()))
        out = ", ".join(r.get("output_files", [])) or r.get("error", "")
        md.append(f"| {r['idx']:02d} | {status} | {r.get('elapsed_sec', '-')}s | {params} | "
                  f"{r.get('prompt_id', '-')[:8]} | {out} |")
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")

    print(f"\n完成：{len(summary)}/{len(combos)} 成功")
    print(f"结果: {out_dir}/summary.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
