"""模型知识库管理（CRUD + 验证 + 联网补全）。

零外部依赖（联网可选）。

用法：
    python model_kb.py list                       # 列出所有模型
    python model_kb.py show anima                 # 显示 anima 详情
    python model_kb.py add my-model               # 交互式新建
    python model_kb.py update anima --field steps.range "[20,40]"
    python model_kb.py match JANIMA_v10.safetensors  # 按文件名匹配
    python model_kb.py verify anima               # 显示验证状态
"""
import argparse
import fnmatch
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
KB_DIR_ENV = "COMFYUI_KB_DIR"
# 默认 KB 目录：用户全局 ~/.comfyui-api-skills/knowledge/models/
# 可被环境变量 COMFYUI_KB_DIR 覆盖
DEFAULT_KB_DIR = Path.home() / ".comfyui-api-skills" / "knowledge" / "models"


def resolve_kb_dir() -> Path:
    """解析 KB 目录。

    优先级：
        1. 环境变量 COMFYUI_KB_DIR
        2. CWD/knowledge/models/  （如果存在）
        3. ~/.comfyui-api-skills/knowledge/models/  （默认全局）

    不存在时自动创建。
    """
    import os
    custom = os.environ.get(KB_DIR_ENV)
    if custom:
        d = Path(custom)
    else:
        cwd_kb = Path.cwd() / "knowledge" / "models"
        d = cwd_kb if cwd_kb.is_dir() else DEFAULT_KB_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def _kb() -> Path:
    """内部便捷函数：返回当前 KB 目录。"""
    return resolve_kb_dir()


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _save_yaml(path: Path, data: dict) -> None:
    header = f"# 自动更新于 {date.today().isoformat()}\n"
    text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(header + text, encoding="utf-8")


def list_models() -> list[dict]:
    out = []
    for p in sorted(_kb().glob("*.yaml")):
        if p.name == "_index.yaml":
            continue
        d = _load_yaml(p)
        out.append({
            "model_id": d.get("model_id", p.stem),
            "display_name": d.get("display_name", "?"),
            "architecture": d.get("architecture", "?"),
            "last_verified": d.get("verification", {}).get("last_verified", "?"),
            "file": p.name,
        })
    return out


def show(model_id: str) -> dict | None:
    p = _kb() / f"{model_id}.yaml"
    if not p.is_file():
        return None
    return _load_yaml(p)


def match_by_checkpoint(ckpt_name: str) -> list[dict]:
    """根据 ckpt 文件名 glob 匹配所有可能模型。"""
    matches = []
    for p in _kb().glob("*.yaml"):
        d = _load_yaml(p)
        for pat in d.get("checkpoint_patterns", []):
            if fnmatch.fnmatch(ckpt_name, pat):
                matches.append(d)
                break
    return matches


def update_field(model_id: str, dotted_key: str, value: str) -> bool:
    """点分路径更新，如 steps.range = [20, 30]"""
    p = _kb() / f"{model_id}.yaml"
    if not p.is_file():
        print(f"[错误] 模型不存在: {model_id}", file=sys.stderr)
        return False
    d = _load_yaml(p)
    keys = dotted_key.split(".")
    cur = d
    for k in keys[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    # 尝试解析为 YAML / JSON
    try:
        parsed: Any = yaml.safe_load(value)
    except yaml.YAMLError:
        parsed = value
    cur[keys[-1]] = parsed
    d.setdefault("verification", {})["last_verified"] = date.today().isoformat()
    _save_yaml(p, d)
    print(f"[更新] {model_id}.{dotted_key} = {parsed!r}")
    return True


def add_model(model_id: str) -> Path:
    """交互式新建模型知识文件。"""
    p = _kb() / f"{model_id}.yaml"
    if p.is_file():
        print(f"[错误] 已存在: {p}", file=sys.stderr)
        sys.exit(1)
    print(f"交互式创建: {model_id}（Ctrl+C 退出）")
    data: dict[str, Any] = {
        "model_id": model_id,
        "display_name": input("display_name: ").strip() or model_id,
        "architecture": input("architecture (sd1.5/sdxl/flux/wan/cosmos/qwen): ").strip() or "unknown",
        "checkpoint_patterns": [],
    }
    print("checkpoint_patterns（glob，每行一个，空行结束）:")
    while True:
        line = input("  pattern: ").strip()
        if not line:
            break
        data["checkpoint_patterns"].append(line)

    # CLIP
    if input("需要配置 CLIP? [y/N]: ").strip().lower() == "y":
        data["clip"] = {
            "required": input("  required clip filename: ").strip(),
            "required_type": input("  type (stable_diffusion/wan/etc): ").strip() or "stable_diffusion",
        }
        forb = input("  forbidden clips (逗号分隔): ").strip()
        if forb:
            data["clip"]["forbidden"] = [x.strip() for x in forb.split(",")]
    # VAE
    if input("需要配置 VAE? [y/N]: ").strip().lower() == "y":
        data["vae"] = {"required": input("  required vae filename: ").strip()}

    # 采样参数
    data["sampler"] = {"recommended": input("recommended sampler: ").strip() or "euler"}
    data["cfg"] = {"recommended": float(input("recommended cfg (e.g. 7): ").strip() or "7")}
    data["steps"] = {"recommended": int(input("recommended steps (e.g. 20): ").strip() or "20")}

    # 验证
    data["verification"] = {
        "last_verified": date.today().isoformat(),
        "test_prompts": [],
        "success_count": 0,
        "failure_count": 0,
    }
    _save_yaml(p, data)
    print(f"[创建] {p}")
    return p


def import_from_inventory(url: str) -> list[dict]:
    """从 ComfyUI 拉取 ckpt 列表，让用户为每个未登记的模型创建条目。"""
    sys.path.insert(0, str(Path(__file__).parent / "lib"))
    from comfy_client import _req
    try:
        ckpts = _req(f"{url}/models/checkpoints")
    except Exception as e:
        print(f"[错误] 无法连接 {url}: {e}", file=sys.stderr)
        return []
    registered = {m["model_id"] for m in list_models()}
    registered_patterns = set()
    for m in list_models():
        d = show(m["model_id"])
        if d:
            registered_patterns.update(d.get("checkpoint_patterns", []))

    new_ones = []
    for c in ckpts:
        if any(fnmatch.fnmatch(c, p) for p in registered_patterns):
            continue
        new_ones.append(c)
    print(f"ComfyUI 装了 {len(ckpts)} 个 ckpt，其中 {len(new_ones)} 个未登记:")
    for c in new_ones:
        print(f"  - {c}")
    if not new_ones:
        return []
    if input("\n是否全部登记? [y/N]: ").strip().lower() != "y":
        return []
    for c in new_ones:
        # 派生 model_id
        mid = re.sub(r"[\s_]+", "-", c.split(".")[0].lower())
        if mid in registered:
            continue
        print(f"\n登记新模型: {c} → {mid}")
        p = _kb() / f"{mid}.yaml"
        data = {
            "model_id": mid,
            "display_name": c,
            "architecture": "unknown",
            "checkpoint_patterns": [c],
            "verification": {
                "last_verified": date.today().isoformat(),
                "test_prompts": [], "success_count": 0, "failure_count": 0,
            },
        }
        _save_yaml(p, data)
        registered.add(mid)
        print(f"  [创建] {p.name}（架构 unknown，请用 update --field 补全）")
    return new_ones


def main() -> int:
    p = argparse.ArgumentParser(description="模型知识库管理")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="列出所有模型")

    s = sub.add_parser("show", help="显示模型详情")
    s.add_argument("model_id")

    s = sub.add_parser("add", help="交互式新建")
    s.add_argument("model_id")

    s = sub.add_parser("update", help="更新字段（点分路径）")
    s.add_argument("model_id")
    s.add_argument("--field", required=True, help="如 steps.range")
    s.add_argument("--value", required=True, help="值（YAML / JSON / 文本）")

    s = sub.add_parser("match", help="按 checkpoint 文件名匹配")
    s.add_argument("ckpt_name")

    s = sub.add_parser("verify", help="查看验证状态")
    s.add_argument("model_id")

    s = sub.add_parser("import", help="从 ComfyUI 库存导入未登记的模型")
    s.add_argument("--url", help="ComfyUI 地址")

    s = sub.add_parser("enrich", help="联网拉取 HF/CivitAI 数据合并到本地 KB")
    s.add_argument("model_id", help="本地 model_id（kebab-case）")
    s.add_argument("--hf-id", help="HuggingFace model_id（black-forest-labs/FLUX.1-dev）")
    s.add_argument("--civitai-id", help="CivitAI model_id（数字）")
    s.add_argument("--hf-token", help="HF token（默认读 .env HF_TOKEN）")
    s.add_argument("--civitai-key", help="CivitAI API key（默认读 .env CIVITAI_API_KEY）")
    s.add_argument("--dry-run", action="store_true", help="只打印不保存")

    args = p.parse_args()
    if args.cmd == "list":
        rows = list_models()
        if not rows:
            print("(空) knowledge/models/ 下还没有 yaml")
            return 0
        print(f"已登记 {len(rows)} 个模型:\n")
        for r in rows:
            print(f"  [{r['model_id']:20s}] {r['display_name']:40s} "
                  f"({r['architecture']:14s}) verified={r['last_verified']}")
        return 0
    if args.cmd == "show":
        d = show(args.model_id)
        if not d:
            print(f"[错误] 模型不存在: {args.model_id}", file=sys.stderr)
            return 2
        print(yaml.safe_dump(d, allow_unicode=True, sort_keys=False, default_flow_style=False))
        return 0
    if args.cmd == "add":
        _kb().mkdir(parents=True, exist_ok=True)
        add_model(args.model_id)
        return 0
    if args.cmd == "update":
        return 0 if update_field(args.model_id, args.field, args.value) else 1
    if args.cmd == "match":
        matches = match_by_checkpoint(args.ckpt_name)
        if not matches:
            print(f"无匹配（{args.ckpt_name}）")
            return 1
        for m in matches:
            print(f"[{m['model_id']}] {m['display_name']}")
        return 0
    if args.cmd == "verify":
        d = show(args.model_id)
        if not d:
            return 2
        v = d.get("verification", {})
        print(f"模型: {d['display_name']} ({d['model_id']})")
        print(f"  最后验证: {v.get('last_verified', '?')}")
        print(f"  成功/失败: {v.get('success_count', 0)}/{v.get('failure_count', 0)}")
        print(f"  测试 prompts: {len(v.get('test_prompts', []))} 条")
        return 0
    if args.cmd == "import":
        env_path = ROOT / ".env"
        url = args.url or "http://127.0.0.1:8188"
        if env_path.is_file():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("COMFYUI_URL="):
                    url = line.split("=", 1)[1].strip().strip('"')
                    break
        import_from_inventory(url)
        return 0
    if args.cmd == "enrich":
        sys.path.insert(0, str(Path(__file__).parent / "lib"))
        from web_kb import enrich_kb  # noqa
        from comfy_client import load_env
        p = _kb() / f"{args.model_id}.yaml"
        existing = _load_yaml(p) if p.is_file() else {}
        # 读 env（先 cd 到含 .env 的目录；或设 COMFYUI_ENV_FILE；或环境变量直接传）
        env = load_env()
        import os
        hf_token = args.hf_token or env.get("HF_TOKEN", "") or os.environ.get("HF_TOKEN", "")
        civitai_key = args.civitai_key or env.get("CIVITAI_API_KEY", "") or os.environ.get("CIVITAI_API_KEY", "")
        if not args.hf_id and not args.civitai_id:
            print("[错误] 需要 --hf-id 或 --civitai-id 之一", file=sys.stderr)
            return 2
        # 关键：绝不打印 token。脱敏提示。
        if hf_token:
            print(f"[env] HF_TOKEN 已加载（{len(hf_token)} 字符）")
        if civitai_key:
            print(f"[env] CIVITAI_API_KEY 已加载（{len(civitai_key)} 字符）")
        kb, sources = enrich_kb(
            args.model_id,
            hf_id=args.hf_id or "",
            civitai_id=args.civitai_id or "",
            hf_token=hf_token, civitai_key=civitai_key,
            existing=existing,
        )
        print(f"\n# enrich {args.model_id}")
        for s in sources:
            mark = "✓" if s.get("ok") else "✗"
            extra = f"  fields: {s['fields_changed']}" if s.get("ok") else f"  error: {s.get('error','')}"
            print(f"  [{mark}] {s['source']} (id={s.get('id','')}){extra}")
        if not any(s.get("ok") for s in sources):
            print("所有源都失败，未保存")
            return 1
        if args.dry_run:
            print("\n[dry-run] 合并后 KB:")
            print(yaml.safe_dump(kb, allow_unicode=True, sort_keys=False, default_flow_style=False))
            return 0
        if not p.is_file():
            print(f"[错误] 本地 KB 不存在: {p}（先用 add 创建）", file=sys.stderr)
            return 1
        kb["verification"] = kb.get("verification", {}) or {}
        kb["verification"]["last_enriched"] = date.today().isoformat()
        _save_yaml(p, kb)
        print(f"\n[保存] {p}")
        print(f"  model_id:        {kb.get('model_id')}")
        print(f"  display_name:    {kb.get('display_name')}")
        print(f"  architecture:    {kb.get('architecture')}")
        print(f"  checkpoint_patterns: {len(kb.get('checkpoint_patterns', []) or [])} 个")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
