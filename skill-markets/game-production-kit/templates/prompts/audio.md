# 音频提示词模板

## 模板来源

使用缓存的 `bgm_generate.json` 模板（Stable Audio 3 + Qwen3.5 提示词工程）。
**不修改 JSON 参数，只调整 description 和 filename_prefix。**

## 分类策略

| 类型 | 时长 | 用途 | category 参数 |
|------|------|------|---------------|
| Music | 60-120s | 场景循环背景音乐（BGM） | `Music` |
| SFX | 5-15s | 音效（脚步声、开门、雷声…） | `SFX` |
| AMB | 30-120s | 环境音（雨声、城市背景、咖啡馆嘈杂） | `Music` |
| FX | 10-30s | 情感过渡音（闪回、梦境、现实拉回） | `One-shot` |
| One-shot | 3-8s | 短击声音（UI 反馈音） | `One-shot` |
| Instrument | 30-60s | 纯乐器过场 | `Instrument` |

> **声场分层原则**：BGM/SFX/AMB/FX 四层独立生成。参考 04-assets.md §4.6.0。

## Stable Audio 3 提示词避坑

| 目标 | 错误写法 | 正确写法 |
|------|---------|---------|
| 脚步声 | `footsteps, dark, low` | `rain-soaked pavement, single footstep with squelch, wet concrete texture, close microphone` |
| 雷声 | `thunder, low, dark` | `distant thunder rolling over empty valley, deep低频 resonance with 3-second decay, wide stereo field` |
| 心跳 | `heartbeat, tense` | `slow single heartbeat thump, sub-bass impact with immediate decay, isolated and dry, no reverb` |
| 开门 | `door open, creak` | `old wooden door hinge creaking slowly, rusted metal friction, hollow wooden resonance, single event` |

> **核心经验**：不用抽象形容词（low/dark/tense），用具体名词+材质+动词描述物理声音。

## 模板 JSON 修改指南

**只改以下 3 个字段：**
1. `node 68` → `inputs.value` → 音频描述文本
2. `node 19` → `inputs.filename_prefix` → 输出文件名
3. `node 74` → `inputs.value` → 时长（秒）

**不改的有：**
- `node 60` → KSampler 参数（steps=8, cfg=1, sampler=lcm）
- `node 75` → CheckpointLoaderSimple（stable_audio_3_medium）
- `node 76` → CLIPLoader（t5gemma_b_b_ul2）

## BGM 描述示例

```
# 标题画面（120s）
deep ambient electronic drone with distant thunder rumbling, slow ominous bass,
mysterious sci-fi horror atmosphere, building cosmic tension, dark cinematic

# 不安（120s）
subtle uneasy electronic ambient, soft pulsating synth pads, micro-glitch textures,
feeling of something being slightly wrong, minimal percussion, psychological thriller

# 空荡荣耀（120s）
melancholic piano solo with distant orchestral strings swelling,
feeling of empty success and hollow loneliness, beautiful but deeply sad, slow tempo

# 异常升起（120s）
gradually building tension, electronic thriller music, increasingly distorted synth layers,
heartbeat-like bass pulse, unsettling horror atmosphere

# 裂缝恐怖（120s）
deep dark horror ambient, low rumbling bass, dissonant orchestral textures,
cosmic eldritch horror, overwhelming existential dread, Lovecraftian

# 雨声温柔（120s）
gentle piano melody with soft ambient pads, subtle rain in background,
warm nostalgic feeling, emotional resolution, peaceful closure, healing atmosphere
```

## SFX 描述示例

```
# 点击音效（3s）
clean UI click sound, soft digital pop, short attack, crisp transient, dry

# 开门声（5s）
old wooden door creaking open slowly, distant reverb, hollow resonance, eerie

# 雷声（8s）
distant thunder rolling, deep low rumble, wide stereo spread, atmospheric

# 心跳（6s）
slow heartbeat pulse, deep sub-bass thump, tense, isolated, dry
```
