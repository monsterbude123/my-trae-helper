"""根据 checkpoint 名称 → 加载知识库约束 → 校验 / 应用到 JSON。

用法：
    # 1. 列出本地已装模型（来自 ComfyUI inventory）
    python comfy_resolve.py models

    # 2. 选择模型，显示可用参数约束
    python comfy_resolve.py select JANIMA_v10.safetensors

    # 3. 校验 JSON 是否违反约束（不修改）
    python comfy_resolve.py validate JANIMA_v10.safetensors --json Anima_01.json

    # 4. 自动应用约束默认值到 JSON
    python comfy_resolve.py apply JANIMA_v10.safetensors --json Anima_01.json --out safe.json
"""
import argparse
import fnmatch
import json
import sys
from pathlib import Path

import yaml  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent / "lib"))
sys.path.insert(0, str(Path(__file__).parent))

from comfy_client import (  # noqa: E402
    _req, apply_overrides, find_checkpoint_node, find_sampler_nodes,
    find_text_nodes, find_latent_node, get_env, load_env,
)
from model_kb import match_by_checkpoint, resolve_kb_dir  # noqa: E402


def _find_clip_node(workflow: dict) -> str | None:
    for nid, node in workflow.items():
        if "CLIPLoader" in node.get("class_type", "") or node.get("class_type") == "CLIPLoader":
            return nid
        if "DualCLIPLoader" in node.get("class_type", ""):
            return nid
    return None


def _find_vae_node(workflow: dict) -> str | None:
    for nid, node in workflow.items():
        if "VAELoader" in node.get("class_type", ""):
            return nid
        # 也找 CheckpointLoaderSimple 输出的 VAE（不推荐单独校验）
    return None


def select_model(ckpt_name: str) -> dict | None:
    """从知识库选一个匹配的模型，返回完整 yaml 字典。"""
    matches = match_by_checkpoint(ckpt_name)
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]
    print(f"'{ckpt_name}' 匹配到 {len(matches)} 个模型，取第一个：{matches[0]['model_id']}")
    return matches[0]


def list_local_models(url: str) -> list[str]:
    """拉取 ComfyUI 已装的所有 checkpoint。"""
    return list(_req(f"{url}/models/checkpoints"))


def show_constraints(ckpt: dict) -> None:
    """打印模型可调参数约束。"""
    print(f"\n# {ckpt['display_name']} ({ckpt['model_id']})")
    print(f"# 架构: {ckpt.get('architecture', '?')}")
    print(f"# 验证: {ckpt.get('verification', {}).get('last_verified', '?')}\n")
    clip = ckpt.get("clip", {})
    if clip:
        print(f"## CLIP（必填）")
        print(f"  required: {clip.get('required', '?')}")
        if clip.get("required_type"):
            print(f"  type:     {clip.get('required_type')}")
        if clip.get("forbidden"):
            print(f"  forbidden: {', '.join(clip['forbidden'])}")
        if clip.get("reason"):
            print(f"  reason:   {clip['reason'].strip()[:120]}")
        print()
    vae = ckpt.get("vae", {})
    if vae:
        print(f"## VAE")
        print(f"  required: {vae.get('required', '?')}")
        print()
    s = ckpt.get("sampler", {})
    if s:
        print(f"## Sampler")
        print(f"  compatible: {', '.join(s.get('compatible', []))}")
        print(f"  recommended: {s.get('recommended', '?')}")
        sch = ckpt.get("scheduler", {})
        if sch:
            print(f"  scheduler.recommended: {sch.get('recommended', '?')}")
        print()
    cfg = ckpt.get("cfg", {})
    steps = ckpt.get("steps", {})
    if cfg or steps:
        print(f"## 经验值")
        if cfg:
            r = cfg.get("range", [])
            print(f"  cfg:   {r[0]}-{r[1]} (推荐 {cfg.get('recommended', '?')})")
        if steps:
            r = steps.get("range", [])
            print(f"  steps: {r[0]}-{r[1]} (推荐 {steps.get('recommended', '?')})")
        print()
    res = ckpt.get("resolution", {})
    if res:
        print(f"## 分辨率")
        print(f"  recommended: {res.get('recommended', [])}")
        sup = res.get("supported", [])
        if sup:
            print(f"  supported: {', '.join(f'{w}x{h}' for w, h in sup)}")
        if res.get("avoid"):
            print(f"  avoid:     {', '.join(f'{w}x{h}' for w, h in res['avoid'])}")
        print()
    errs = ckpt.get("errors", [])
    if errs:
        print(f"## 已知错误（{len(errs)} 条）")
        for e in errs:
            print(f"  - [{e.get('code', '?')}] {e.get('signature', '?')[:80]}")
            print(f"      fix: {e.get('fix', '?')[:100]}")
        print()


def validate(ckpt: dict, workflow: dict) -> list[str]:
    """校验 workflow 是否违反约束，返回问题列表。"""
    issues = []
    # 1. checkpoint
    ckpt_id = find_checkpoint_node(workflow, find_sampler_nodes(workflow)[0])
    if ckpt_id:
        ins = workflow[ckpt_id]["inputs"]
        actual = ins.get("ckpt_name") or ins.get("unet_name", "")
        patterns = ckpt.get("checkpoint_patterns", [])
        if not any(fnmatch.fnmatch(actual, p) for p in patterns):
            issues.append(f"checkpoint '{actual}' 不匹配 {patterns}")

    # 2. CLIP
    clip_spec = ckpt.get("clip", {})
    if clip_spec:
        clip_id = _find_clip_node(workflow)
        if clip_id:
            ins = workflow[clip_id]["inputs"]
            actual = ins.get("clip_name", "")
            required = clip_spec.get("required")
            if required and actual != required:
                issues.append(f"CLIP '{actual}' ≠ required '{required}'")
            for fb in clip_spec.get("forbidden", []):
                if fnmatch.fnmatch(actual, fb):
                    issues.append(f"CLIP '{actual}' 在 forbidden 列表中（{fb}）")
            rt = clip_spec.get("required_type")
            if rt and ins.get("type") and ins["type"] != rt:
                issues.append(f"CLIP type '{ins.get('type')}' ≠ required '{rt}'")

    # 3. VAE
    vae_spec = ckpt.get("vae", {})
    if vae_spec:
        vae_id = _find_vae_node(workflow)
        if vae_id:
            ins = workflow[vae_id]["inputs"]
            actual = ins.get("vae_name", "")
            required = vae_spec.get("required")
            if required and actual != required:
                issues.append(f"VAE '{actual}' ≠ required '{required}'")

    # 4. sampler
    sid, _, _ = find_sampler_nodes(workflow)
    if sid:
        ins = workflow[sid]["inputs"]
        sampler = ins.get("sampler_name")
        compat = ckpt.get("sampler", {}).get("compatible", [])
        if compat and sampler and sampler not in compat:
            issues.append(f"sampler '{sampler}' 不在兼容列表 {compat}")
        sched = ins.get("scheduler")
        scompat = ckpt.get("scheduler", {}).get("compatible", [])
        if scompat and sched and sched not in scompat:
            issues.append(f"scheduler '{sched}' 不在兼容列表 {scompat}")
        cfg = ins.get("cfg")
        crange = ckpt.get("cfg", {}).get("range", [])
        if crange and cfg is not None and not (crange[0] <= cfg <= crange[1]):
            issues.append(f"cfg {cfg} 超出范围 {crange}")
        steps = ins.get("steps")
        srange = ckpt.get("steps", {}).get("range", [])
        if srange and steps is not None and not (srange[0] <= steps <= srange[1]):
            issues.append(f"steps {steps} 超出范围 {srange}")

    # 5. resolution
    lat_id = find_latent_node(workflow, sid)
    if lat_id:
        ins = workflow[lat_id]["inputs"]
        w, h = ins.get("width"), ins.get("height")
        sup = ckpt.get("resolution", {}).get("supported", [])
        if sup and (w, h) and [w, h] not in sup:
            issues.append(f"resolution {w}x{h} 不在 supported 列表")
        avoid = ckpt.get("resolution", {}).get("avoid", [])
        if avoid and (w, h) and [w, h] in avoid:
            issues.append(f"resolution {w}x{h} 在 avoid 列表中")

    return issues


def apply_constraints(ckpt: dict, workflow: dict) -> tuple[dict, list[str]]:
    """把约束默认值应用到 workflow，返回 (新workflow, 改了什么)。"""
    changes = []
    w = workflow
    sid, _, _ = find_sampler_nodes(w)
    if sid:
        ins = w[sid]["inputs"]
        rec_sampler = ckpt.get("sampler", {}).get("recommended")
        if rec_sampler and ins.get("sampler_name") not in (ckpt.get("sampler", {}).get("compatible", []) or [rec_sampler]):
            ins["sampler_name"] = rec_sampler
            changes.append(f"sampler_name → {rec_sampler}")
        rec_sch = ckpt.get("scheduler", {}).get("recommended")
        if rec_sch:
            ins["scheduler"] = rec_sch
            changes.append(f"scheduler → {rec_sch}")
        cfg_rec = ckpt.get("cfg", {}).get("recommended")
        if cfg_rec is not None:
            ins["cfg"] = cfg_rec
            changes.append(f"cfg → {cfg_rec}")
        steps_rec = ckpt.get("steps", {}).get("recommended")
        if steps_rec is not None:
            ins["steps"] = steps_rec
            changes.append(f"steps → {steps_rec}")

    # CLIP
    clip_spec = ckpt.get("clip", {})
    if clip_spec:
        clip_id = _find_clip_node(w)
        if clip_id:
            ins = w[clip_id]["inputs"]
            req = clip_spec.get("required")
            if req and ins.get("clip_name") != req:
                ins["clip_name"] = req
                changes.append(f"clip_name → {req}")
            rt = clip_spec.get("required_type")
            if rt:
                ins["type"] = rt
                changes.append(f"clip type → {rt}")
            dev = clip_spec.get("required_device")
            if dev:
                ins["device"] = dev
                changes.append(f"clip device → {dev}")

    # VAE
    vae_spec = ckpt.get("vae", {})
    if vae_spec:
        vae_id = _find_vae_node(w)
        if vae_id:
            req = vae_spec.get("required")
            if req and w[vae_id]["inputs"].get("vae_name") != req:
                w[vae_id]["inputs"]["vae_name"] = req
                changes.append(f"vae_name → {req}")

    # resolution
    res_spec = ckpt.get("resolution", {})
    if res_spec:
        lat_id = find_latent_node(w, sid)
        if lat_id:
            rec = res_spec.get("recommended")
            if rec:
                w[lat_id]["inputs"]["width"] = rec[0]
                w[lat_id]["inputs"]["height"] = rec[1]
                changes.append(f"resolution → {rec[0]}x{rec[1]}")
    return w, changes


def main() -> int:
    p = argparse.ArgumentParser(description="模型约束解析 / 校验 / 应用")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("models", help="列出本地已装模型")
    s.add_argument("--url")

    s = sub.add_parser("select", help="显示某模型约束")
    s.add_argument("ckpt_name")

    s = sub.add_parser("validate", help="校验 JSON 是否违反约束")
    s.add_argument("ckpt_name")
    s.add_argument("--json", required=True)

    s = sub.add_parser("apply", help="应用约束到 JSON")
    s.add_argument("ckpt_name")
    s.add_argument("--json", required=True)
    s.add_argument("--out", required=True)

    args = p.parse_args()
    env = load_env()
    url = (env.get("COMFYUI_URL") or "http://127.0.0.1:8188").rstrip("/")

    if args.cmd == "models":
        try:
            ckpts = list_local_models(url)
        except Exception as e:
            print(f"[错误] {e}", file=sys.stderr)
            return 3
        registered = {}
        for c in ckpts:
            ms = match_by_checkpoint(c)
            if ms:
                registered[c] = ms[0]["model_id"]
        print(f"ComfyUI 已装 {len(ckpts)} 个 ckpt；其中 {len(registered)} 个有知识库登记:\n")
        for c in ckpts:
            tag = f"  → [{registered[c]}]" if c in registered else "  (未登记)"
            print(f"  {c}{tag}")
        return 0

    kb = select_model(args.ckpt_name)
    if not kb:
        print(f"[错误] 知识库无 '{args.ckpt_name}' 匹配")
        print(f"  提示: python model_kb.py add <new-model-id>")
        return 1

    if args.cmd == "select":
        show_constraints(kb)
        return 0
    if args.cmd == "validate":
        wf = json.loads(Path(args.json).read_text(encoding="utf-8"))
        issues = validate(kb, wf)
        if not issues:
            print(f"✓ 符合 {kb['model_id']} 约束")
            return 0
        print(f"✗ 违反 {kb['model_id']} 约束的 {len(issues)} 条:")
        for i in issues:
            print(f"  - {i}")
        return 1
    if args.cmd == "apply":
        wf = json.loads(Path(args.json).read_text(encoding="utf-8"))
        new_wf, changes = apply_constraints(kb, wf)
        if not changes:
            print(f"已符合 {kb['model_id']} 约束，无需修改")
        else:
            print(f"已应用 {len(changes)} 项修改:")
            for c in changes:
                print(f"  ✓ {c}")
        Path(args.out).write_text(json.dumps(new_wf, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n写入: {args.out}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
