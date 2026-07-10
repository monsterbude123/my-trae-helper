"""单文件：标题图 bg.webp 生成（明快治愈，waiANIMA 1216x832）。
"""
import json, sys, time, urllib.request
from pathlib import Path
from PIL import Image

if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"d:\workspace\ai-github\OpenWebGAL\WebGAL_Demo")
CASE = ROOT / "webgal_case02"
BG = CASE / "background"
GEN = ROOT / "_work" / "gen_figures"
GEN.mkdir(parents=True, exist_ok=True)
BG.mkdir(exist_ok=True)

COMFY = "http://127.0.0.1:8188"
TPL = ROOT / ".trae/skills/webgal-create-deploy-skill/templates/workflows/anima_txt2img.json"
CKPT = "waiANIMA_v10Base10.safetensors"
NEG = "ugly, blurry, low quality, text, watermark, cartoon, deformed, multiple scenes"
POS = (
    "a bright and heartwarming anime visual novel title screen, "
    "cherry blossom petals drifting in gentle wind, golden hour sunlight, "
    "old university library in background, soft dreamy bokeh, "
    "two young people silhouettes facing each other on stone bridge, "
    "warm color palette with pink and gold tones, "
    "optimistic hopeful atmosphere, painterly anime style, masterpiece"
)

urllib.request.urlopen(f"{COMFY}/system_stats").read()
print("ComfyUI OK", flush=True)

out = BG / "bg.webp"
if out.exists():
    print(f"[skip] {out.name} {out.stat().st_size//1024}KB", flush=True)
else:
    template = json.loads(TPL.read_text(encoding="utf-8"))["workflow"]
    wf = json.loads(json.dumps(template))
    wf["1"]["inputs"]["unet_name"] = CKPT
    wf["10"]["inputs"]["text"] = POS
    wf["11"]["inputs"]["text"] = NEG
    wf["20"]["inputs"]["width"] = 1216
    wf["20"]["inputs"]["height"] = 832
    wf["30"]["inputs"]["seed"] = int(time.time()) & 0x7fffffff
    wf["50"]["inputs"]["filename_prefix"] = "title_"
    body = json.dumps({"prompt": wf, "client_id": "webgal-gen"}).encode()
    req = urllib.request.Request(f"{COMFY}/prompt", data=body, headers={"Content-Type": "application/json"})
    pid = json.loads(urllib.request.urlopen(req).read())["prompt_id"]
    print(f"pid={pid}", flush=True)
    t0 = time.time()
    while time.time() - t0 < 180:
        h = json.loads(urllib.request.urlopen(f"{COMFY}/history/{pid}").read())
        if pid in h and h[pid].get("outputs"):
            for node_out in h[pid]["outputs"].values():
                for img in node_out.get("images", []):
                    p = f"filename={img['filename']}&subfolder={img.get('subfolder','')}&type={img.get('type','output')}"
                    data = urllib.request.urlopen(f"{COMFY}/view?{p}").read()
                    tmp = GEN / img["filename"]
                    tmp.write_bytes(data)
                    Image.open(tmp).convert("RGB").save(out, "WEBP", quality=90)
                    print(f"OK {out.name} {out.stat().st_size//1024}KB", flush=True)
            break
        time.sleep(2)
print("DONE", flush=True)
