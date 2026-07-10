"""单文件：背景批量生成（anima workflow，urllib 直接调 ComfyUI）。
权威来源：comfyui-api-skills/cache/workflows/workflows-txt2img_anima.json
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
CKPT = "waiANIMA_v10Base10.safetensors"  # 基础版更适合场景

BACKGROUNDS = {
    "bedroom_night":      "interior apartment bedroom at 3am, moonlight through curtain, dark moody atmosphere, glowing laptop on messy desk, urban city visible outside, photorealistic, cinematic lighting, horror atmosphere, 4k, masterpiece",
    "bedroom_day":        "interior apartment bedroom during daytime, warm natural sunlight through window, casual messy desk with computer, books and coffee mug, cozy atmospheric, photorealistic, 4k, masterpiece",
    "bedroom_morning":    "interior apartment bedroom at dawn, golden sunrise light through window, dead green plant on windowsill, slightly unsettling atmosphere, photorealistic, cinematic, 4k, masterpiece",
    "city_street":        "shanghai city street intersection, towering skyscrapers, traffic light glowing red, light rain on asphalt reflecting neon, photorealistic urban night, cyberpunk mood, 4k, masterpiece",
    "office":             "modern tech office interior, glass walls, multiple computer screens showing code, dark blue ambient lighting, programmer working late, photorealistic, 4k, masterpiece",
    "ceremony":           "awards ceremony stage, bright spotlights, rows of audience seats in darkness, podium with golden trophy, dramatic spotlight, photorealistic, cinematic, 4k, masterpiece",
    "banquet_hall":       "elegant hotel banquet hall at night, dim warm chandeliers, people in suits mingling, polished marble floor, photorealistic, 4k, masterpiece",
    "livingroom":         "small apartment living room, old sofa, vintage CRT TV showing static, scattered newspapers, dim ambient light, photorealistic, horror atmosphere, 4k, masterpiece",
    "corridor_night":     "empty office building corridor at night, fluorescent lights flickering, long perspective with doors on both sides, dark and unsettling, photorealistic horror, 4k, masterpiece",
    "archive_room":       "old archive room with floor-to-ceiling shelves, dusty old newspapers, single hanging lightbulb, claustrophobic, photorealistic, horror atmosphere, 4k, masterpiece",
    "cinema_rain":        "rainy evening outside old cinema, neon movie poster glowing through rain, wet street with reflections, lonely female silhouette waiting with umbrella, photorealistic romantic noir, 4k, masterpiece",
    "cafe_interior":      "vintage coffee shop interior, warm amber lighting, exposed brick walls, old wooden counter with coffee machine, dusty shelves with antique books, mysterious retro atmosphere, photorealistic, 4k, masterpiece",
    "apartment_art":      "small artist studio apartment, large canvas with unfinished painting of city skyline, paint supplies scattered, easel by window, dust particles in light, photorealistic, 4k, masterpiece",
    "mist_city":          "foggy city street at dawn, ghostly female silhouette in white dress standing in mist, urban buildings fading into fog, ethereal haunting atmosphere, photorealistic horror, 4k, masterpiece",
    "city_destruction":   "shanghai cbd skyline under attack, massive eldritch tentacles rising between skyscrapers, code patterns glowing on skin of tentacles, breaking glass, apocalyptic, photorealistic cinematic horror, 4k, masterpiece",
    "library_rain":       "old university library exterior, stone steps under covered entrance, gentle rain falling, puddles on flagstones, warm light from library windows, peaceful cozy atmosphere, photorealistic, 4k, masterpiece",
}
NEG = "ugly, blurry, low quality, text, watermark, cartoon, anime style, deformed, multiple scenes, busy"

urllib.request.urlopen(f"{COMFY}/system_stats").read()
print("ComfyUI OK", flush=True)

template = json.loads(TPL.read_text(encoding="utf-8"))["workflow"]

def render(pos, neg, w, h, seed, prefix):
    wf = json.loads(json.dumps(template))
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
    return json.loads(urllib.request.urlopen(req).read())["prompt_id"]

def poll(pid, timeout=180):
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

ok = skip = 0
for i, (key, pos) in enumerate(BACKGROUNDS.items()):
    out = BG / f"{key}.webp"
    if out.exists():
        skip += 1
        print(f"  [skip {i+1:02d}/16] {key}.webp", flush=True)
        continue
    seed = (int(time.time() * 1000) + i * 17) & 0x7fffffff
    try:
        pid = submit(render(pos, NEG, 1216, 832, seed, f"bg_{key}_"))
    except Exception as e:
        print(f"  [FAIL {i+1:02d}/16] {key} submit: {e}", flush=True)
        continue
    res = poll(pid)
    if not res:
        print(f"  [FAIL {i+1:02d}/16] {key} poll", flush=True)
        continue
    files = download(res, GEN)
    png = next((f for f in files if f.suffix == ".png"), None)
    if not png:
        print(f"  [FAIL {i+1:02d}/16] {key} no png", flush=True)
        continue
    Image.open(png).convert("RGB").save(out, "WEBP", quality=90)
    print(f"  [OK   {i+1:02d}/16] {key}.webp {out.stat().st_size//1024}KB", flush=True)
    ok += 1

print(f"\nDONE: {ok} ok, {skip} skip", flush=True)
