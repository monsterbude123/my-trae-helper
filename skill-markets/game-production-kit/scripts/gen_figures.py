"""单文件：立绘批量生成（anima workflow，urllib 直接调 ComfyUI）。
权威来源：comfyui-api-skills/cache/workflows/workflows-txt2img_anima.json
不依赖本 skill 的 lib/。每个生成脚本都是独立单文件。
"""
import json, sys, time, urllib.request, urllib.error
from pathlib import Path
import numpy as np
from PIL import Image

if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"d:\workspace\ai-github\OpenWebGAL\WebGAL_Demo")
CASE = ROOT / "webgal_case02"
FIG = CASE / "figure"
GEN = ROOT / "_work" / "gen_figures"
GEN.mkdir(parents=True, exist_ok=True)
FIG.mkdir(exist_ok=True)

COMFY = "http://127.0.0.1:8188"
TPL = ROOT / ".trae/skills/webgal-create-deploy-skill/templates/workflows/anima_txt2img.json"
CKPT = "miaomiaoHarem_anima13.safetensors"  # ANIMA 兼容（已验证 qwen_3_06b + qwen_image_vae 通路）

FIGURES = {
    "qiu_suwan": (
        "masterpiece, highres, absurdres, newest, best quality, score_7, "
        "1girl, solo, simple background, white background, "
        "young Chinese woman 23 years old, gentle melancholic smile, closed mouth, "
        "long straight black hair past shoulders, hair between eyes, side-parted bangs, "
        "wearing simple cream-white dress, slender delicate figure, "
        "looking at viewer with soft eyes, upper body, "
        "anime visual novel character portrait"
    ),
    "qiu_suwan_ghost": (
        "masterpiece, highres, absurdres, newest, best quality, score_7, "
        "1girl, solo, dark background, "
        "young Chinese woman 23 years old, "
        "long straight black hair flowing upward, hair between eyes, side-parted bangs, "
        "wearing cream-white dress with dark black stains on hem, "
        "translucent glowing body, glowing silver-blue code patterns in deep dark eyes, "
        "looking at viewer, upper body, mysterious haunting atmosphere, "
        "anime visual novel character portrait"
    ),
    "cafe_boss": (
        "masterpiece, highres, absurdres, newest, best quality, score_7, "
        "1man, solo, simple background, white background, "
        "elderly Chinese man 60+ years old, silver-gray slicked-back hair, "
        "calm wise expression with knowing smile, closed mouth, "
        "wearing white shirt with black vest and dark brown apron, "
        "looking at viewer, upper body, "
        "anime visual novel character portrait"
    ),
}
NEG = "ugly, blurry, low quality, distorted, deformed, watermark, text, multiple people, extra limbs, bad anatomy, missing fingers"

# 1) 健康检查
urllib.request.urlopen(f"{COMFY}/system_stats").read()
print("ComfyUI OK", flush=True)

# 2) 加载模板（原始 {workflow: ...} 结构）
raw = TPL.read_text(encoding="utf-8")
template = json.loads(raw)

def render(pos, neg, w, h, seed, prefix):
    wf = json.loads(json.dumps(template["workflow"]))  # 深拷贝
    wf["1"]["inputs"]["unet_name"] = CKPT
    wf["10"]["inputs"]["text"] = pos
    wf["11"]["inputs"]["text"] = neg
    wf["20"]["inputs"]["width"] = w
    wf["20"]["inputs"]["height"] = h
    wf["30"]["inputs"]["seed"] = seed
    wf["50"]["inputs"]["filename_prefix"] = prefix
    return wf

def submit(wf):
    body = json.dumps({"prompt": wf, "client_id": "webgal-gen"}).encode()
    req = urllib.request.Request(f"{COMFY}/prompt", data=body, headers={"Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req).read())["prompt_id"]
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"submit 400: {e.read().decode('utf-8', 'replace')}")

def poll(pid, timeout=240):
    t0 = time.time()
    while time.time() - t0 < timeout:
        h = json.loads(urllib.request.urlopen(f"{COMFY}/history/{pid}").read())
        if pid in h and h[pid].get("outputs"):
            return h[pid]
        time.sleep(2)
    return None

def download(history, out_dir):
    files = []
    for node_out in history["outputs"].values():
        for img in node_out.get("images", []):
            params = f"filename={img['filename']}&subfolder={img.get('subfolder','')}&type={img.get('type','output')}"
            data = urllib.request.urlopen(f"{COMFY}/view?{params}").read()
            p = Path(out_dir) / img["filename"]
            p.write_bytes(data)
            files.append(p)
    return files

def white_to_alpha(rgb_path, thr=235, soft=10):
    img = Image.open(rgb_path).convert("RGB")
    arr = np.array(img).astype(int)
    lum = arr.mean(axis=2)
    w_score = np.clip((lum - (thr - soft)) / soft, 0, 1)
    alpha = ((1 - w_score) * 255).astype(np.uint8)
    return Image.fromarray(np.dstack([arr.astype(np.uint8), alpha]), mode="RGBA")

print(f"CKPT={CKPT}", flush=True)
for i, (name, pos) in enumerate(FIGURES.items()):
    out = FIG / f"{name}.png"
    seed = (int(time.time() * 1000) + hash(name)) & 0x7fffffff
    print(f"[{i+1}/3] {name} seed={seed}", flush=True)
    pid = submit(render(pos, NEG, 832, 1216, seed, f"fig_{name}_"))
    print(f"  pid={pid}", flush=True)
    res = poll(pid)
    if not res:
        print("  POLL FAIL", flush=True); continue
    files = download(res, GEN)
    png = next((f for f in files if f.suffix == ".png"), None)
    if not png:
        print("  NO PNG", flush=True); continue
    rgba = white_to_alpha(png)
    rgba.save(out, "PNG")
    arr = np.array(rgba)
    print(f"  OK {out.name} {out.stat().st_size//1024}KB transp={(arr[:,:,3]<128).mean():.1%}", flush=True)

print("DONE", flush=True)
