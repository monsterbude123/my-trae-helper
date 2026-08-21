# 3 子模式 prompt 结构

> REF2V 在 H3 上有 3 类子模式(image_mode 与 prompt 结构各异)。本文给出 reference / first_last_frame / style_transfer 的完整 prompt 结构 + 反例。

---

## §1 reference 模式(默认 + 通用)

### §1.1 适用场景

```
- 多图混合(角色 + 场景 + 美学 + 道具)
- 图 + 视频混合(参考视频学习动作 / 镜头)
- 图 + 视频 + 音频混合(全媒体参考)
- 同一主体多角度(3+ 张图)
```

### §1.2 完整 prompt 结构

```yaml
【平台】MiniMax H3
【模式】reference
【时长】6s(可调)
【分辨率】768P
【画幅】16:9

素材:
  @Image1: <简短描述>
  @Image2: <简短描述>
  ...
  @Video1: <简短描述>
  @Audio1: <简短描述>

# integrated_multimodal_description
<让位语句(可选)>。<主体@Image1>。<服装 / 场景 / 美学 / 动作 / 镜头(各 @素材)>
[Shot 1] <景别 + 主体 + 动作 + 镜头 + 美学>。

# overall_soundscape
<环境音 + 动作触发 + 节奏>

# non_diegetic_music
<配乐 + 节奏 + 卡点 + 淡出>
```

### §1.3 完整示例

```yaml
【平台】MiniMax H3
【模式】reference
【时长】6s
【分辨率】768P
【画幅】16:9

素材:
  @Image1: 主角正面照(红发女生)
  @Image2: 主角侧面照(轮廓补充)
  @Image3: 米色风衣(服装)
  @Image4: 巴黎街景(场景)
  @Image6: 1980s 胶片色调(美学)
  @Video1: 走路动作(节奏参考)
  @Video2: 慢推镜头(机位参考)
  @Audio1: 钢琴配乐(BGM)
  @Audio2: 雨声环境音

# integrated_multimodal_description
@Image1 (red-haired woman, mid-20s) is the protagonist.
@Image2 supplements her side profile for continuity.
She wears the beige trench coat from @Image3, carries the leather satchel
as her key prop.
The scene is set in @Image4's Parisian street, lit by warm afternoon light.
Visual style follows @Image6: Kodak Gold 200 emulation, amber highlights,
soft grain. The motion rhythm follows @Video1's measured pace.
Camera work mirrors @Video2: slow push-in with small amplitude.
[Shot 1] A medium shot establishes her at the corner; the camera pushes
in with small amplitude at slow speed as she steps forward, her eyes
scanning the street. S1 says: "Almost there."

# overall_soundscape
Soft rain on cobblestones. Her footsteps are slow and deliberate.
Distant traffic hum is muted. S1's voice is low, warm.

# non_diegetic_music
@Audio1 is the musical reference: sparse piano notes with warm reverb,
slow tempo, fading gently at end.
```

### §1.4 reference 反例(MUST 避)

| ❌ 反模式 | ✅ 正确做法 |
|---------|----------|
| 上传 5 张图但 prompt 不引用任何 @Image | 至少 N 个 @Image<N> 出现 |
| @Image1 没说是主角 | R1 必加 "is the protagonist" |
| 视频只描述一帧静态画面 | 视频引用动作 / 镜头的**连续性** |
| 多图都给 R1 角色 | R1 唯一性,其余分配 R2 ~ R6 |
| @Image<N> 数字和上传顺序对不上 | @Image1 = 用户第 1 张上传 |

---

## §2 first_last_frame 模式(首尾帧补帧)

### §2.1 适用场景

```
- 视频延长 / 镜头延长 / 状态切换(开 → 关, 出现 → 消失)
```

### §2.2 完整 prompt 结构

```yaml
【平台】MiniMax H3
【模式】first_last_frame
【时长】4-6s(超过 8s 易漂移)
【首帧】@Image1(<起点描述>)
【尾帧】@Image2(<终点描述>)

# integrated_multimodal_description
Starting from the first frame (@Image1), <起点状态>.
Naturally transitioning to the last frame (@Image2), <终点状态>.

Between the first and last frames, <中间过渡:
  摄影机行为(连续 / 不切镜)
  光照一致性
  主角身份一致性
  时间连续性>.

# overall_soundscape
<整段统一音景:连续不间断的环境音>

# non_diegetic_music
<配乐:整段单一音调 / 同一和弦 / 缓慢淡出>
```

### §2.3 完整示例

```yaml
【平台】MiniMax H3
【模式】first_last_frame
【时长】5s
【首帧】@Image1(主角街角回眸)
【尾帧】@Image2(主角走到咖啡店门口,目光向前)

# integrated_multimodal_description
Starting from the first frame (@Image1), the protagonist stands at the
street corner, looking back over her shoulder. She then turns and walks
forward at a steady pace, naturally transitioning to the last frame
(@Image2), where she stands at the café entrance facing the camera.

Between the first and last frames, the camera holds a steady medium shot;
she crosses the cobblestone street in a single continuous motion with no
cuts. The lighting remains consistent throughout: warm golden hour matching
@Image1's amber tones.

# overall_soundscape
Continuous ambient: distant traffic, soft footsteps on cobblestones.
No abrupt transitions.

# non_diegetic_music
A single sustained piano note through the entire transition, fading out
at the very end.
```

### §2.4 first_last_frame 反例

| ❌ 反模式 | ✅ 正确做法 |
|---------|----------|
| 中间过程切镜 / 光照不一致 / 主角换脸 | "no cuts" + "lighting remains consistent" + 维持 R1 |
| 中间过程用"高级感"等抽象词 | 描述具体可见的物理运动(4-6s 黄金长度) |

---

## §3 style_transfer 模式(风格迁移)

### §3.1 适用场景

```
- 产品图 → 复古胶片风 | 真人照 → 动漫 / 油画风 | 场景 → 调色师风格
```

### §3.2 完整 prompt 结构

```yaml
【平台】MiniMax H3
【模式】style_transfer
【主体图】@Image1(<要迁移的图像内容>)
【风格图】@Image2(<目标风格>)

# integrated_multimodal_description
The subject from @Image1 (<主体描述>) is rendered in the visual style
of @Image2 (<风格特征描述>).

<摄影机行为:通常静态 / 慢推 / 不切镜>
<光照:继承 @Image2 的光感>

[Shot 1] <具体镜头描述>.

# overall_soundscape
<与风格匹配的音景>

# non_diegetic_music
<与风格匹配的配乐>
```

### §3.3 完整示例(Sigma 相机复古化)

```yaml
【平台】MiniMax H3
【模式】style_transfer
【主体图】@Image1(Sigma 相机白色背景产品图)
【风格图】@Image2(1980s 胶片色调 + 暖黄高光)

# integrated_multimodal_description
The subject from @Image1 (Sigma camera on white background) is rendered
in the visual style of @Image2: vintage Kodak Gold 200 film emulation
with warm amber highlights, soft grain, and slight vignette.

The camera holds a static close-up. Light glints off the lens with a
subtle warm flare characteristic of @Image2's aesthetic.
[Shot 1] The camera slowly pushes in with small amplitude as highlights
catch the metal surface, revealing the engraved brand mark.

# overall_soundscape
Soft mechanical click of a shutter, no other ambient sound.

# non_diegetic_music
@Audio1 reference: warm analog synth pad at slow tempo, faded out at end.
```

### §3.4 style_transfer 反例

| ❌ 反模式 | ✅ 正确做法 |
|---------|----------|
| 风格图当 R4 / 主体不清晰 / 抽象风格词 / 多张风格图 | 1 张风格图 + 主体含物体 + 具体风格词(例:"Kodak Gold 200 + 暖色高光 + 软颗粒") |

---

## §4 三子模式对比速查

| 维度 | reference | first_last_frame | style_transfer |
|------|-----------|------------------|----------------|
| 图片数 | 1 ~ 9 | 恰好 2 | 通常 2 |
| 视频数 | 0 ~ 3 | 0 | 0 ~ 1(可选) |
| 音频数 | 0 ~ 3 | 0 ~ 1(连续环境音) | 0 ~ 1 |
| image_mode | reference | first_last_frame | reference |
| 关键短语 | "is the protagonist" | "Starting from the first frame... transitions to the last frame" | "is rendered in the visual style of" |
| 主要风险 | 素材冲突 | 中间漂移 | 风格不一致 |

---

## §5 子模式路由决策表

```
用户上传:
  ├─ 2 张图(起点 + 终点)               → first_last_frame
  ├─ 1 主体图 + 1 风格图                 → style_transfer
  ├─ 多图混合(角色 + 场景 + 多角度)      → reference
  ├─ 图 + 视频混合                      → reference(默认)
  ├─ 多音频 + 视频                       → reference
  └─ 其他任意多模态组合                  → reference(兜底)
```

详见 [../SKILL.md §1.2 路由决策](../SKILL.md) — 配合主 skill 路由器使用。
