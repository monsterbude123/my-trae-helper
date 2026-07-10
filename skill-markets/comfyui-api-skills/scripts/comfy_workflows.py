"""列出 / 重用 / 删除缓存的成功工作流。

缓存位置：~/.comfyui-api-skills/cache/workflows/

用法：
    python comfy_workflows.py list                 # 列出
    python comfy_workflows.py show <name_or_idx>   # 显示详情
    python comfy_workflows.py reuse <name> --seed 99 --positive "..."   # 复用
    python comfy_workflows.py delete <name>        # 删除
    python comfy_workflows.py clean                # 清空
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "lib"))


def main() -> int:
    p = argparse.ArgumentParser(description="缓存工作流管理")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list", help="列出所有缓存")
    s.add_argument("--limit", type=int, default=20)

    s = sub.add_parser("show", help="显示详情")
    s.add_argument("target", help="name 或序号")

    s = sub.add_parser("reuse", help="复用：导出 JSON 到指定路径")
    s.add_argument("target", help="name 或序号")
    s.add_argument("--out", required=True, help="输出 JSON 路径")

    s = sub.add_parser("delete", help="删除")
    s.add_argument("target")

    sub.add_parser("clean", help="清空所有缓存")

    args = p.parse_args()

    from workflow_cache import CACHE_DIR, list_cached, load, extract_workflow

    if args.cmd == "list":
        items = list_cached()
        if not items:
            print(f"(空) {CACHE_DIR}")
            return 0
        print(f"缓存工作流 ({len(items)} 条，按时间倒序):\n")
        print(f"  {'#':<4} {'名称':<40} {'ckpt':<30} {'耗时':<8} {'保存时间'}")
        for i, it in enumerate(items[:args.limit]):
            print(f"  {i:<4} {it['name'][:38]:<40} {it['ckpt'][:28]:<30} "
                  f"{it['elapsed_sec']:.1f}s   {it['saved_at'][:19]}")
        return 0

    # 找目标
    items = list_cached()
    target = args.target
    item = None
    if target.isdigit():
        idx = int(target)
        if 0 <= idx < len(items):
            item = items[idx]
    else:
        for it in items:
            if it["name"] == target or it["path"].stem == target:
                item = it
                break
    if not item:
        print(f"[错误] 未找到: {target}", file=sys.stderr)
        return 1
    path = item["path"]

    if args.cmd == "show":
        data = load(path)
        meta = data.get("meta", {})
        wf = data.get("workflow", {})
        print(f"名称: {meta.get('name')}")
        print(f"路径: {path}")
        print(f"保存: {meta.get('saved_at')}")
        print(f"ckpt: {meta.get('ckpt')}")
        print(f"耗时: {meta.get('elapsed_sec')}s")
        print(f"输出: {', '.join(meta.get('output_files', []))}")
        print(f"参数: {json.dumps(meta.get('params', {}), ensure_ascii=False)}")
        pos = meta.get("positive", "")
        neg = meta.get("negative", "")
        if pos:
            print(f"\npositive: {pos[:200]}{'...' if len(pos) > 200 else ''}")
        if neg:
            print(f"negative: {neg[:200]}{'...' if len(neg) > 200 else ''}")
        print(f"\n节点数: {len(wf)}")
        return 0

    if args.cmd == "reuse":
        data = load(path)
        wf = extract_workflow(data)
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(wf, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已导出: {out}（{len(wf)} 节点）")
        return 0

    if args.cmd == "delete":
        path.unlink()
        print(f"已删除: {path}")
        return 0

    if args.cmd == "clean":
        n = 0
        for p in CACHE_DIR.glob("*.json"):
            p.unlink()
            n += 1
        print(f"已清空 {n} 个文件")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
