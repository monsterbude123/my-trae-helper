---
name: ref2v-h3-prompt
description: 参考生视频(MiniMax H3)提示词专项。当用户想用多张参考图 + 视频片段 + 音频 + 文本生成视频时加载。覆盖 H3 多模态参考(9 图 + 3 视频 + 3 音频)、素材角色分配、reference vs first_last_frame vs style_transfer 三子模式、冲突解决 4 步法。Use when the user wants reference-to-video prompts for MiniMax H3 with multiple image / video / audio references, including role binding and conflict resolution.
version: 1.0.0
parent-skill: video-prompt-method
platform: [MiniMax-H3]
input-mode: ref2v
material-budget: {images: 9, videos: 3, audio: 3, mixed-total: 12}
created: 2026-08-20
---

# ref2v-h3-prompt — MiniMax H3 参考生视频(REF2V)提示词专项

> 多模态参考生视频 = 多图 + 多视频 + 多音频 + 文本混合输入。每份素材必须**显式分配角色**,否则模型只会用 1 份 + 自己猜其余。

## §0 何时加载

```
MUST 加载: 用户提供多模态素材 + 想生成视频
  - 提供 2 张以上图(角色 + 场景 / 多角度 + 风格参考)
  - 提供 1 段视频 + 1 张图(参考视频 + 角色)
  - 提供图 / 视频 / 音频混合输入
  - 明确说"参考这个风格 / 这段动作 / 这个角色"
  - 需要"首尾帧补帧"或"风格迁移"
  - 用户素材数量触发 H3 多模态通道(>1 份)

MUST NOT 加载:
  - 单图 I2V             → 改去 ../i2v-h3-prompt
  - 纯文本 T2V            → 改去 t2v-h3-prompt
  - 单视频 V2V(无多模态)  → 改去 v2v-h3-prompt
  - Seedance / 可灵 / Vidu → 改去对应 skill
  - 图片生成 / 编辑        → 改去 minimax-multimodal
```

## §1 三大子模式路由

```
                  ┌─────────────────────────────────┐
用户上传多模态      │  你是 ref2v-h3-prompt 路由器   │
  ↓              │                                 │
  ↓              │  判断主子模式:                    │
  ↓              │    reference         (默认)      │
  ↓              │    first_last_frame              │
  ↓              │    style_transfer                │
  ↓              └─────────────────────────────────┘
                  ↓
         进入对应 §3 / §4 / §8 模板
```

### §1.1 三子模式对比

| 模式 | 典型场景 | image_mode | 核心特征 |
|------|---------|------------|---------|
| **reference**(通用) | 角色照搬 + 场景迁移 + 动作学习 | `reference` | 多素材融合,每份都有独立职责 |
| **first_last_frame**(首尾帧) | 视频补帧 / 镜头延长 | `first_last_frame` | 2 张图 = 首 + 尾,模型生成中间过渡 |
| **style_transfer**(风格迁移) | 把参考图风格迁移到目标主体 | `reference` | 风格图 + 主体图,风格优先 |

### §1.2 路由决策表

```
用户上传:
  ├─ 2 张图(起点 + 终点)               → first_last_frame
  ├─ 1 主体图 + 1 风格图                 → style_transfer
  ├─ 同一主体多角度(3+ 张图)            → reference(主体锁定)
  ├─ 主体 + 场景 + 道具 各自独立图        → reference(角色分配)
  ├─ 视频片段 + 主角图                   → reference(动作 / 镜头学习)
  ├─ 多音频 + 视频                       → reference(声学绑定)
  └─ 上述任意组合                         → reference(默认兜底)
```

## §2 素材角色分配协议(REF2V 核心)

> **铁律**:每份上传素材,prompt 里 MUST 显式说**它做什么**(角色 / 场景 / 风格 / 动作 / 镜头 / 声音),否则模型只挑 1 份用。

### §2.1 9 类素材角色分配表

| 角色类别 | @标签示例 | 职责 | 分配禁忌 |
|---------|----------|------|---------|
| **R1 主体身份(面部)** | `@Image1 → 主角面容` | 锁定脸 / 五官 | ❌ 多图同时给 R1 |
| **R2 主体侧面 / 背面** | `@Image2 → 主角侧面参考` | 补充角度,非主面容 | ❌ 误当 R1 |
| **R3 服装 / 造型** | `@Image3 → 主角服装细节` | 服装 / 配饰锁定 | ❌ 没上传图就硬写 |
| **R4 场景 / 背景** | `@Image4 → 场景参考` | 空间 / 地形 / 光照 | ❌ 与 R6 冲突 |
| **R5 道具特写** | `@Image5 → 道具参考` | 武器 / 工具 / 物件 | ❌ 让模型自由想象 |
| **R6 美学 / 调色** | `@Image6 → 美学参考` | 画风 / 色调 / 质感 | ❌ 与 R4 冲突 |
| **M1 动作节奏(视频)** | `@Video1 → 动作参考` | 动作 / 表情节奏 | ❌ 当图片用 |
| **M2 镜头运动(视频)** | `@Video2 → 运镜参考` | 机位 / 节奏 / 切镜 | ❌ 当图片用 |
| **A1 BGM 底色(音频)** | `@Audio1 → BGM 参考` | 配乐 / 旋律 / 节奏 | ❌ 当音效 |
| **A2 环境音(音频)** | `@Audio2 → 环境音` | 脚步 / 风声 / 机械 | ❌ 当对白 |
| **A3 对白 / 关键音** | `@Audio3 → 对白 / SFX` | 台词 / 提示音效 | ❌ 当 BGM |

### §2.2 H3 上限速查

```
图片:   ≤ 9   (image_mode: reference | first_last_frame)
视频:   ≤ 3   (单段 ≤ 15s,总时长 ≤ 15s)
音频:   ≤ 3   (单段 ≤ 15s,总时长 ≤ 15s)
混合总: ≤ 12  文件
图比例:  1:2.5 ~ 2.5:1(其他比例被裁切)
```

完整协议 → [references/material-role-binding.md](references/material-role-binding.md)

## §3 reference 模式 prompt 结构

```
【平台】MiniMax H3
【模式】reference(通用参考)
【时长】6s  【分辨率】768P  【画幅】16:9

# integrated_multimodal_description
@Image1(A young woman with auburn hair and freckles) is the protagonist.
@Image2 shows her in profile for continuity.
She wears the outfit from @Image3: a beige trench coat and leather satchel.
The scene's lighting and palette follow @Image6 (warm amber, soft chiaroscuro).
The motion rhythm matches @Video1: she walks slowly, gaze drifting across
the rain-soaked street.
The camera work mirrors @Video2: a slow push-in with small amplitude.
[Shot 1] A medium shot establishes her at the street corner; the camera pushes
in with small amplitude at slow speed as she lifts her gaze. S1 says: "Almost
there."

# overall_soundscape
Rain patters on cobblestones while distant traffic hums. Her footsteps are
soft on wet pavement. S1's voice is low and unhurried.

# non_diegetic_music
@Audio1 is the musical reference: sparse piano notes with warm reverb,
matching the scene's amber tone.
```

### §3.1 reference 模式要点

```
- 每个 @Image<N> / @Video<N> / @Audio<N> MUST 在 prompt 出现 ≥ 1 次
- @Image1 必为"是主角"或"提供主体"(身份锁定)
- 描述顺序:身份 → 服装 → 场景 → 美学 → 动作 → 镜头 → 声音
- 视频素材只能用 1 帧意图 + 描述连续动作,不能当图片堆叠
- 音频素材引用音色 / 节奏 / 旋律,不引用具体波形
```

## §4 first_last_frame 模式 prompt 结构

```
【平台】MiniMax H3
【模式】first_last_frame(首尾帧补帧)
【时长】6s
【首帧】@Image1(主角在街角回眸)
【尾帧】@Image2(主角走入咖啡店门口,目光向前)

# integrated_multimodal_description
Starting from the first frame (@Image1), the protagonist stands at the
street corner looking back over her shoulder. She then turns and walks
forward at a steady pace, naturally transitioning to the last frame
(@Image2) where she stands at the café entrance facing the camera.

Between the first and last frames, the camera holds a steady medium shot;
she crosses the cobblestone street in a single continuous motion with no
cuts. The ambient lighting remains consistent throughout, with soft golden
hour warmth matching @Image1.

# overall_soundscape
Continuous ambient street sound: distant traffic, soft footsteps on
cobblestones. No abrupt transitions.

# non_diegetic_music
A single sustained piano note through the entire transition, fading out
at the end.
```

### §4.1 first_last_frame 模式要点

```
- 2 张图 = 首帧 + 尾帧,模型生成中间过渡
- "between the first and last frames" 短语 MUST 出现
- 中间过程不要切镜(连续运动)
- 光照 / 色调 / 主角身份在两帧间 MUST 保持一致
- 长度推荐 4~6s(超过 8s 易漂移)
```

## §5 冲突解决 4 步法

> REF2V 最大风险 = **多素材打架**。2 张图都让模型当主角 / 美学词互相矛盾 / BGM 与环境音冲突 — 都得在 prompt 里显式解决。

### §5.1 4 步走流程

```
Step 1:识别冲突(冲突检测)
  - 主角多个?(@Image1 和 @Image3 都看起来像主角)
  - 风格打架?(@Image4 是写实 + @Image6 是赛博朋克)
  - 声音混乱?(@Audio1 BGM 激昂 + @Audio2 环境音安静)
  - 比例失调?(图片比例不一致)

Step 2:优先级排序
  身份(谁) > 美学(长什么样) > 动作(做什么) > 镜头(怎么看) > 声音(听起来怎样)

Step 3:让位(显式声明)
  - "ignore @Image3's background, use @Image5's environment instead"
  - "@Image1 is the priority subject; @Image2 only supplements the side profile"
  - "the camera work follows @Video2; ignore @Video1's motion"

Step 4:在 prompt 标注让位关系
  - 让位语句必须出现在 integrated_multimodal_description 开头,
    让模型有"主从优先级"上下文
```

### §5.2 让位语句模板

```
# 主角优先级
"@Image1 is the primary subject; @Image3 provides only the costume reference."

# 风格优先级
"Ignore @Image4's background style; apply @Image6's color grading throughout."

# 镜头让位
"Camera movement follows @Video2's pattern; @Video1 is for motion timing only."

# 音频让位
"Background score follows @Audio1; @Audio2's ambient sound is muted."
```

完整反例库 → [references/conflict-resolution.md](references/conflict-resolution.md)

## §6 反模式(MUST 避)

| ❌ 反模式 | ✅ 正确做法 |
|---------|----------|
| 上传 9 张图但 prompt 不引用任何 @Image | 至少有 N 个 @Image<N> 出现在 description |
| 多张图都给"主体身份"(R1) | R1 只能有 1 张,其余分配 R2 / R3 |
| 视频当图片用(只取 1 帧描述) | 视频描述动作 / 镜头连续性 |
| 多音频都给"配乐"角色(A1) | BGM / 环境音 / 对白 各 1 类 |
| 图比例超过 1:2.5 / 2.5:1 | 上传前统一裁切至安全比例 |
| 视频总时长 > 15s | 截取关键片段 ≤ 15s |
| 不用 @Image/@Video/@Audio 标签 | H3 必须用 @ 标签识别引用 |
| 冲突素材不让位 | 用 §5.2 让位语句显式声明优先级 |

## §7 子 skill 自检

```
✓ 9 类素材角色分配(§2.1 表)中至少 1 类被使用?
✓ 每个上传素材在 prompt 出现 ≥ 1 次?
✓ R1(主体身份)只分配给 1 张图?
✓ 冲突场景已走 §5 4 步?
✓ 素材总数 ≤ 12(混合)且分类 ≤ 上限(9/3/3)?
✓ 时间切片(继承父级 video-prompt-method §2)按 6s 切 3 段?
✓ 三段式公式(继承自 i2v-h3-prompt §1)顺序正确?
```

## §8 输出模板(交付格式 · style_transfer)

```
【平台】MiniMax H3
【模式】style_transfer(风格迁移)
【主体图】@Image1(Sigma 相机产品图,白色背景)
【风格图】@Image2(1980s 复古胶片色调 + 暖黄高光)
【时长】6s

# integrated_multimodal_description
The subject from @Image1 (Sigma camera product shot) is rendered in the
visual style of @Image2: vintage Kodak Gold 200 film emulation with warm
amber highlights, soft grain, and slight vignette.

The camera holds a static close-up on the product. Light glints off the
lens with a subtle warm flare characteristic of @Image2's aesthetic.
[Shot 1] The camera slowly pushes in with small amplitude, revealing the
lens engraving as warm highlights catch the metal surface.

# overall_soundscape
Soft mechanical click of a shutter, no other ambient sound.

# non_diegetic_music
@Audio1 reference: warm analog synth pad at a slow tempo, faded out at end.
```

## §9 references

- [references/material-role-binding.md](references/material-role-binding.md) — 9 类素材角色分配完整协议
- [references/conflict-resolution.md](references/conflict-resolution.md) — 冲突解决 4 步法 + 让位语句模板
- [references/sub-modes.md](references/sub-modes.md) — 3 子模式 prompt 结构 + 反例
- 父级方法论: [../video-prompt-method/SKILL.md](../video-prompt-method/SKILL.md)(子模式路由 + 时间切片)
- 平台公式: [../i2v-h3-prompt/SKILL.md](../i2v-h3-prompt/SKILL.md)(三段式 + 运镜三件套 + 失败模式)
- 中文笔记法: [../i2v-h3-prompt/references/chinese-prompt-method.md](../i2v-h3-prompt/references/chinese-prompt-method.md)

## §10 来源

- [MiniMax H3 提示词指南(官方)](https://minimaxh3.studio/zh/guide/minimax-h3)
- [MiniMax H3 多模态参考 API](https://platform.minimax.io/docs/guides/video-generation)
- MiniMax H3 platform multimodal budget:images ≤ 9 / videos ≤ 3 / audio ≤ 3 / mixed ≤ 12
