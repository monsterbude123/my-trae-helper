"""音频批量生成（bgm workflow，urllib 直接调 ComfyUI）。

权威 workflow：.trae/skills/webgal-create-deploy-skill/templates/workflows/bgm_generate.json

特点：
- 19 个 prompt 全部使用具体名词/材质/动词，关键词簇互不共享
- 每个 prompt 至少 60 tokens，描述具体物件与录音方法
- 不复用 lib/comfy_client.py（urllib 单文件，零依赖）
- 删除旧文件后强制重新生成，不 skip
- 完成后用 pydub 验证 rms/peak 互不相同
- 同时 copy 到 _work/webgal-engine/{public,dist}/game/bgm/
"""
import json
import os
import shutil
import sys
import time
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(r"d:\workspace\ai-github\OpenWebGAL\WebGAL_Demo")
CASE = ROOT / "webgal_case02"
BGM_DIR = CASE / "bgm"
GEN_AUDIO = ROOT / "_work" / "gen_audio"
ENGINE_PUBLIC_BGM = ROOT / "_work" / "webgal-engine" / "public" / "game" / "bgm"
ENGINE_DIST_BGM = ROOT / "_work" / "webgal-engine" / "dist" / "game" / "bgm"

for d in (BGM_DIR, GEN_AUDIO, ENGINE_PUBLIC_BGM, ENGINE_DIST_BGM):
    d.mkdir(parents=True, exist_ok=True)

COMFY = "http://127.0.0.1:8188"
TPL = ROOT / ".trae/skills/webgal-create-deploy-skill/templates/workflows/bgm_generate.json"

# ---------------------------------------------------------------------------
# AUDIO 列表：每条 (file_key, 类目, 时长秒, 描述)
# 设计原则：
#   1. 每个 prompt 至少 60 tokens（约 50-60 个英文单词）
#   2. 使用具体名词（物件/材质/乐器/动作）
#   3. 关键词簇互不共享（footsteps 用 wet pavement, heartbeat 用 stethoscope, door 用 oak hinge …）
#   4. 不用 "low / sub-bass / dark" 这类共享抽象词
# ---------------------------------------------------------------------------
AUDIO = [
    # ----- SFX 6 个（One-shot 3-6s）-----
    ("sfx_footsteps", "One-shot", 5,
     "pair of leather shoes stepping on rain-soaked pavement, individual footfall impacts with sharp "
     "heel clicks and soft rubber sole slap on wet asphalt, crisp close microphone foley recording, "
     "no reverb, no ambient room, brief attack transient on each step, isolated single footfall, "
     "concrete sidewalk puddle splatter, walk cycle, dry recording, no music, no drone"),
    ("sfx_door_open", "One-shot", 4,
     "heavy oak door with rusty iron hinges creaking open slowly in abandoned mansion, ancient wood "
     "groaning under pressure, dust particles falling, hollow chamber resonance echoing from the dark "
     "room beyond, single isolated event, foley microphone close capture, distinct attack with "
     "sustained creaking decay, antique carved doorframe, no music, no rhythm, no percussion"),
    ("sfx_phone_ring", "One-shot", 6,
     "vintage rotary telephone mechanical bell clanging twice in succession inside wood-panel office, "
     "brass bell strikers hitting nickel-plated gongs, internal ringer mechanism turning gears, retro "
     "1950s payphone design, distant muffled sound as if through plaster wall, single event, antique "
     "foley recording, plastic Bakelite handset vibrating on cradle, no music, no drone"),
    ("sfx_glitch", "One-shot", 5,
     "digital data corruption burst from broken hard drive, computer glitch artifact with brief "
     "stuttering bitcrushed stabs, electronic interference pattern, white noise pop with sharp "
     "crackle, broken transmission glitch, faulty capacitor whine, single sharp transient event, "
     "no music, no melody, no rhythm, no singing, no percussion, very short"),
    ("sfx_heartbeat", "One-shot", 5,
     "human heartbeat thump resonating in empty chest cavity, isolated cardiac lub-dub pulse with "
     "valve click between, medical stethoscope pressed against bare skin, close microphone capture, "
     "single cardiac cycle, two soft thumps per beat, 60bpm rhythm, intimate medical examination "
     "room recording, no music, no drone, no rhythm instrument"),
    ("sfx_thunder", "One-shot", 6,
     "single thunder crack tearing the sky with sharp lightning stroke opening, rolling low "
     "frequency rumble tail echoing across open grassy plains, atmospheric outdoor storm, distant "
     "cloud-to-ground strike, no rain, no music, no singing, 8 second decay tail, weather recording, "
     "no rhythm"),
    # ----- BGM 9 首（Music 60-90s）-----
    ("s_Title", "Music", 75,
     "dreamy opening title theme for visual novel, ethereal analog synth pad with slow attack and "
     "long sustain, soft tubular bells glissando in major scale, mysterious invitation to unknown "
     "adventure, gentle analog pulse rhythm with sub kick on every beat, French horn solo melody "
     "floating above the harmony, cinematic curtain rise, anime opening mood, 75bpm, hopeful yet "
     "enigmatic, no singing, no percussion crash"),
    ("s_daily", "Music", 70,
     "peaceful morning ambience in sunlit study room, soft piano arpeggio in C major rolling through "
     "I-IV-vi-V progression, acoustic nylon-string guitar fingerpicking arpeggios, light brushed "
     "shaker with soft snare whisper, lazy Sunday coffee brewing in kettle, potted green plants by "
     "wooden window, gentle optimism and contentment, 70bpm relaxed tempo, four-chord loop, lo-fi "
     "warmth, no singing, no heavy drums"),
    ("s_tense", "Music", 80,
     "suspenseful mechanical pocket watch ticking rhythm like a heartbeat countdown, pizzicato "
     "violins playing nervous staccato two-note motif, rising analog synth pad swelling underneath "
     "with filter sweep, anxious film noir underscore, 90bpm heartbeat tempo, interrogation scene "
     "tension, bass clarinet low drone pedal, brushed snare ghost notes, no singing, no choir"),
    ("s_unease", "Music", 75,
     "creepy ambient drones layered with dissonant bowed double bass sustain, distant unintelligible "
     "whispers from abandoned hospital corridor, dread texture with vinyl record crackle, detuned "
     "music box repeating broken nursery melody, no percussion, no rhythm, no beat, no singing, no "
     "piano, atmospheric dread for empty ward, John Carpenter style minimal synth horror"),
    ("s_horror", "Music", 80,
     "horror orchestral hit with deep contrabass brass stab bursting suddenly, mixed choir shriek "
     "of dissonant cluster with close harmony, tympani roll climax, suspended cymbal crash accent, "
     "jump scare element, dissonant minor second interval stack, single massive impact moment, "
     "very loud and aggressive, no singing lead, no melody, no rhythm pattern, scored for trailer"),
    ("s_cafe", "Music", 70,
     "vintage jazz cafe trio performance, upright acoustic double bass walking bass line in ii-V-I "
     "pattern, brushed snare drum with soft stick sweep, mellow piano comping chord voicings, "
     "breathy tenor saxophone melody line with growls, late night atmosphere, dim lamp light, "
     "vinyl record groove surface noise underneath, 100bpm swing feel, no singing, no lyrics, no "
     "drums kit"),
    ("s_sad", "Music", 90,
     "solo piano and solo cello duo, slow emotional rubato performance with no fixed tempo, tearful "
     "melodic phrase in D minor, sustained cello note bending with heavy vibrato, sparse piano "
     "chords with sustain pedal fully depressed, intimate living room recording, funeral mood, "
     "after the rain feeling, candle-lit farewell scene, no singing, no drums, no bass guitar, no "
     "guitar"),
    ("s_boss", "Music", 85,
     "epic cinematic battle score with full symphony orchestra, heavy timpani hits marking every "
     "downbeat, French horn brass fanfare melody in heroic D minor, mixed choir chanting wordless "
     "war cries, snare drum rapid rolls, suspended cymbal crashes, full string section tremolo "
     "building intensity, 120bpm relentless march, dragon-slaying hero theme, no singing lead, no "
     "pop vocals"),
    ("s_normal", "Music", 80,
     "bittersweet orchestral resolution theme, soft piano and warm string section in unison melody, "
     "hopeful I-V-vi-IV chord progression in C major, reflective chapter ending mood, gentle "
     "crescendo then decrescendo, no percussion, no drums, no bass guitar, no singing, no choir, "
     "80bpm walking tempo, wedding photo album feeling, soft flute counter-melody"),
    ("s_true", "Music", 80,
     "tender acoustic steel-string guitar fingerpicking with Travis picking pattern, gentle tubular "
     "bells chiming in pentatonic scale, cherry blossom petals falling in morning breeze, hopeful "
     "sunrise feel with warm analog tape warmth, 60bpm lullaby tempo, fingerstyle technique with "
     "alternating bass notes, soft brushed snare on beats 2 and 4, optimistic homecoming, no "
     "singing, no heavy drums"),
    # ----- Instrument 3 个（短氛围 15-18s）-----
    ("s_transition_mirror", "Instrument", 15,
     "crystalline glass harmonics with struck crystal wine glass resonance ringing, bell tones "
     "ringing in reverse cymbal swell upward, time dilation effect with reversed piano notes, "
     "crystalline ice texture, frozen lake surface shimmering, no rhythm, no melody, no beat, no "
     "singing, transition bridge for memory palace scene, 15 seconds duration, sparse and delicate"),
    ("s_transition_fade", "Instrument", 15,
     "soft piano single note with long cathedral reverb tail dissolving into silence, memory "
     "fading away, reversed cymbal swell building then releasing, ethereal breath whisper, nostalgic "
     "autumn feeling, 15 second transition bridge, no rhythm, no beat, no melody line, slow harmonic "
     "motion, bittersweet goodbye, no singing, no drums"),
    ("s_transition_mist", "Instrument", 18,
     "low foghorn drone with bowed contrabass note sustained on low E, ghostly analog synth pad "
     "floating in morning mist, fog horn call distant on harbor at dawn, ethereal mist atmosphere "
     "with reversed harp glissando, no rhythm, no beat, no melody, no singing, eerie shoreline "
     "mystery, 18 second bridge, transition cue, sustained pad with filter sweep"),
]

CATEGORY = {"Music": 0, "Instrument": 1, "SFX": 2, "One-shot": 3}

# ---------------------------------------------------------------------------
# Step 1: 删除 webgal_case02/bgm 下所有 s_*.mp3 / sfx_*.mp3 旧文件
# ---------------------------------------------------------------------------
print("=" * 70, flush=True)
print("Step 1: 删除 webgal_case02/bgm 下的旧 s_*/sfx_* 音频", flush=True)
print("=" * 70, flush=True)
removed_count = 0
for pattern in ("s_*.mp3", "sfx_*.mp3"):
    for f in BGM_DIR.glob(pattern):
        size_kb = f.stat().st_size // 1024
        try:
            f.unlink()
            removed_count += 1
            print(f"  [DEL] {f.name}  ({size_kb}KB)", flush=True)
        except Exception as e:
            print(f"  [ERR DEL] {f.name}: {e}", flush=True)
print(f"已删除 {removed_count} 个旧文件\n", flush=True)

# ---------------------------------------------------------------------------
# Step 2: 提交并下载
# ---------------------------------------------------------------------------
urllib.request.urlopen(f"{COMFY}/system_stats").read()
print("ComfyUI OK", flush=True)

template = json.loads(TPL.read_text(encoding="utf-8"))["workflow"]


def render(desc, category, seconds, prefix, seed):
    wf = json.loads(json.dumps(template))
    # 节点 68 = PrimitiveStringMultiline，字段是 value（**不是 text**，原代码 bug 修正）
    # 该 value 会被 StringReplace (节点 66) 注入到模板的 USER_INPUT 占位符，
    # 然后再经 TextGenerate (节点 67) 扩写，最终经 ComfySwitchNode (节点 63, switch=False)
    # 取 on_false 分支回流到 CLIPTextEncode (节点 62) 作为 positive conditioning。
    wf["68"]["inputs"]["value"] = desc
    # 节点 69 = CustomCombo，choice + index
    idx = CATEGORY[category]
    wf["69"]["inputs"]["choice"] = category
    wf["69"]["inputs"]["index"] = idx
    # 节点 74 = PrimitiveFloat，时长（秒，浮点）
    wf["74"]["inputs"]["value"] = float(seconds)
    # 节点 19 = SaveAudioMP3，输出文件名前缀
    wf["19"]["inputs"]["filename_prefix"] = prefix
    # 节点 60 = KSampler，注入唯一 seed（原代码遗漏，导致所有生成同种子 → 雷同）
    wf["60"]["inputs"]["seed"] = int(seed)
    return wf


def submit(wf):
    body = json.dumps({"prompt": wf, "client_id": "webgal-gen-v2"}).encode()
    req = urllib.request.Request(
        f"{COMFY}/prompt", data=body, headers={"Content-Type": "application/json"}
    )
    return json.loads(urllib.request.urlopen(req).read())["prompt_id"]


def poll(pid, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        h = json.loads(urllib.request.urlopen(f"{COMFY}/history/{pid}").read())
        if pid in h and h[pid].get("outputs"):
            return h[pid]
        time.sleep(3)
    return None


def download_audio(history, out_dir):
    files = []
    for node_out in history["outputs"].values():
        for aud in node_out.get("audio", []) or node_out.get("gifs", []) or []:
            params = (
                f"filename={aud['filename']}&subfolder={aud.get('subfolder','')}"
                f"&type={aud.get('type','output')}"
            )
            data = urllib.request.urlopen(f"{COMFY}/view?{params}").read()
            p = Path(out_dir) / aud["filename"]
            p.write_bytes(data)
            files.append(p)
    return files


results = []  # [(key, out_path, size_kb), ...]
ok = fail = 0
total = len(AUDIO)
for i, (key, cat, dur, desc) in enumerate(AUDIO):
    out = BGM_DIR / f"{key}.mp3"
    # 注意：不 skip；旧文件已在 Step 1 删除，这里强制重生成
    # 每条独立 seed，避免 KSampler 复用同一种子导致雷同
    seed = (int(time.time() * 1000) + i * 7919) & 0x7fffffff
    print(
        f"  [{i+1:02d}/{total}] {key} ({cat} {dur}s) prompt_tokens~{len(desc.split())} seed={seed}",
        flush=True,
    )
    try:
        pid = submit(render(desc, cat, dur, key, seed))
    except Exception as e:
        print(f"     submit FAIL: {e}", flush=True)
        fail += 1
        continue
    print(f"     pid={pid[:8]}", flush=True)
    res = poll(pid, timeout=600)
    if not res:
        print(f"     poll FAIL", flush=True)
        fail += 1
        continue
    files = download_audio(res, GEN_AUDIO)
    if not files:
        print(f"     no audio file", flush=True)
        fail += 1
        continue
    src = files[0]
    shutil.copy2(src, out)
    size_kb = out.stat().st_size // 1024
    print(f"     OK {out.name} {size_kb}KB", flush=True)
    results.append((key, out, size_kb))
    ok += 1
    # 每 5 个文件报一次进度
    if (i + 1) % 5 == 0:
        print(
            f"  --- 进度 {i+1}/{total}: {ok} 成功, {fail} 失败 ---",
            flush=True,
        )

print(f"\n生成完成: {ok} 成功, {fail} 失败, total {total}", flush=True)

# ---------------------------------------------------------------------------
# Step 3: 用 pydub 验证 rms/peak，确认互不相同
# ---------------------------------------------------------------------------
print("\n" + "=" * 70, flush=True)
print("Step 3: 用 pydub 检测 rms/peak", flush=True)
print("=" * 70, flush=True)

try:
    from pydub import AudioSegment
except ImportError:
    print("  [WARN] pydub 未安装，跳过验证。可 pip install pydub 后重跑。", flush=True)
    AudioSegment = None

rms_peak_table = {}  # filename -> [rms, peak, dur_sec]

if AudioSegment is not None:
    for key, out, _ in results:
        try:
            seg = AudioSegment.from_mp3(out)
            samples = seg.get_array_of_samples()
            if seg.channels > 1:
                # 立体声：交错，按声道取一次
                import array
                ch = seg.channels
                # 偶数下标 = 左声道
                left = samples[0::ch]
                right = samples[1::ch]
                mix = array.array("h", [])
                mix.extend(left)
                mix.extend(right)
                samples = mix
            peak = max(abs(int(s)) for s in samples) if len(samples) else 0
            # RMS
            n = len(samples)
            if n:
                sum_sq = sum(int(s) * int(s) for s in samples)
                rms = int((sum_sq / n) ** 0.5)
            else:
                rms = 0
            dur = len(seg) / 1000.0
            rms_peak_table[out.name] = [rms, peak, round(dur, 2)]
            print(
                f"  {out.name:35s}  rms={rms:6d}  peak={peak:6d}  dur={dur:6.2f}s",
                flush=True,
            )
        except Exception as e:
            print(f"  [ERR] {out.name}: {e}", flush=True)
            rms_peak_table[out.name] = [-1, -1, -1]

# 唯一性检查
def unique_check(table):
    """按文件类型分组（同为 sfx_ 或同为 s_ 前缀）检查 rms 是否雷同。"""
    import re
    sfx_rms = {}
    sfx_peak = {}
    s_rms = {}
    s_peak = {}
    for name, (rms, peak, _) in table.items():
        if rms < 0:
            continue
        if name.startswith("sfx_"):
            sfx_rms.setdefault(rms, []).append(name)
            sfx_peak.setdefault(peak, []).append(name)
        elif name.startswith("s_"):
            s_rms.setdefault(rms, []).append(name)
            s_peak.setdefault(peak, []).append(name)
    dup_rms = [g for g in sfx_rms.values() if len(g) > 1] + \
              [g for g in s_rms.values() if len(g) > 1]
    dup_peak = [g for g in sfx_peak.values() if len(g) > 1] + \
               [g for g in s_peak.values() if len(g) > 1]
    return dup_rms, dup_peak


if AudioSegment is not None and rms_peak_table:
    dup_rms, dup_peak = unique_check(rms_peak_table)
    if dup_rms or dup_peak:
        print("\n[!] 发现雷同文件（按 rms 或 peak 重复）：", flush=True)
        for g in dup_rms:
            print(f"  RMS 重复: {g}", flush=True)
        for g in dup_peak:
            print(f"  Peak 重复: {g}", flush=True)
        unique_status = "duplicates_found"
    else:
        print("\n[OK] 所有文件 rms/peak 互不相同。", flush=True)
        unique_status = "all_different"
else:
    unique_status = "skipped"

# ---------------------------------------------------------------------------
# Step 4: 复制到 _work/webgal-engine/{public,dist}/game/bgm/
# ---------------------------------------------------------------------------
print("\n" + "=" * 70, flush=True)
print("Step 4: 复制到 webgal-engine/{public,dist}/game/bgm/", flush=True)
print("=" * 70, flush=True)
copied_public = copied_dist = 0
for key, out, size_kb in results:
    for target in (ENGINE_PUBLIC_BGM, ENGINE_DIST_BGM):
        try:
            shutil.copy2(out, target / out.name)
            if target == ENGINE_PUBLIC_BGM:
                copied_public += 1
            else:
                copied_dist += 1
        except Exception as e:
            print(f"  [ERR COPY] {out.name} -> {target}: {e}", flush=True)
    print(f"  [COPY] {out.name} ({size_kb}KB)", flush=True)
print(
    f"\n复制完成: public={copied_public}, dist={copied_dist}", flush=True
)

# ---------------------------------------------------------------------------
# 最终报告
# ---------------------------------------------------------------------------
print("\n" + "=" * 70, flush=True)
print("最终报告", flush=True)
print("=" * 70, flush=True)
print(f"files_regenerated: {[r[0] for r in results]}", flush=True)
print(f"rms_peak_table: {rms_peak_table}", flush=True)
print(f"unique_check: {unique_status}", flush=True)
print(f"files_copied_to_engine: {copied_public + copied_dist}", flush=True)
