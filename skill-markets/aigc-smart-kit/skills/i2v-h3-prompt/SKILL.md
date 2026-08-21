---
name: i2v-h3-prompt
description: MiniMax H3 / Hailuo 2.3 图生视频(I2V)提示词专项。当用户要在 MiniMax / Hailuo 平台上为一张参考图写视频生成 prompt 时加载。继承父级 skill `video-prompt-method` 通用方法论,加 H3 平台特化(三段式 / 运镜三件套)+ I2V 场景特化(单图 I2V / 首尾帧补帧 / 多镜头切镜)。Use when the user needs image-to-video prompts for MiniMax H3 or Hailuo 2.3, including first/last-frame, reference-to-video, and timed multi-shot cuts.
version: 1.1.0
license: MIT
metadata:
  parent: aigc-smart-kit
  extends: video-prompt-method
  parent-skill: video-prompt-method
  sibling-skills:
    - t2v-h3-prompt
    - v2v-h3-prompt
    - ref2v-h3-prompt
  platform:
    - MiniMax-H3
    - MiniMax-Hailuo-2.3
    - MiniMax-Hailuo-02
    - MiniMax-Hailuo-2.3-Fast
    - I2V-01-Director
    - I2V-01-live
    - I2V-01
  input-mode: i2v
  created: 2026-08-19
  refactored: 2026-08-20
---

# i2v-h3-prompt — MiniMax H3 / Hailuo I2V 提示词专项

> 本 skill 是 `aigc-smart-kit` 下 I2V 模式的**祖传儿子**:继承父级 [`video-prompt-method`](../video-prompt-method/SKILL.md) 的通用方法论,加 H3 平台特化层(三段式 / 运镜三件套)+ I2V 场景特化层(单图 I2V / 首尾帧 / 多镜头切镜)。
>
> **Ref2V**(多模态参考生视频)→ 改去 [`ref2v-h3-prompt`](../ref2v-h3-prompt/SKILL.md)。

## §0 何时加载

```
MUST 加载:
  - 用户提供 1 张图 + 想让 MiniMax H3 / 海螺生成视频
  - "I2V / 图生视频 prompt"
  - 首尾帧补帧(2 张图模式)
  - 多镜头切镜(单图生成 ≤15s 内切镜)
  - "用 MiniMax H3 / 海螺生成视频,prompt 怎么写"

MUST NOT 加载:
  - 多模态素材(>1 图 / 图+视频+音频) → 改去 ref2v-h3-prompt
  - 已有视频续写 / 风格化 → 改去 v2v-h3-prompt
  - 纯文字无图 → 改去 t2v-h3-prompt
  - Seedance → 改去 i2v-seedance-prompt
  - 可灵 / Vidu / 万相 → 当前不在本包覆盖范围
  - 图片生成(T2I) → 改去 minimax-multimodal(image)
```

## §1 三段式公式(MiniMax H3 官方)

```
必备三段:
  integrated_multimodal_description: [Shot 1] ... [Shot 2] ...
    → 镜头 + 主体 + 动作 + 视觉风格 + 镜头运动 + 对白 + SFX 触发
  overall_soundscape: ... (环境音 / 对白 / 音效 / 静音场景)
  non_diegetic_music: ... (BGM / 配乐 / 留空)

控制部件(写入 integrated_multimodal_description):
  必填: 主体 / 动作
  选填: 环境 / 美学风格 / 镜头 / 音频 / 文字渲染
```

通用方法学(具体性 / 主角锁定 / 一个镜头三句话)→ 父级 [§3-§5](../video-prompt-method/SKILL.md)。失败模式 → [references/failure-modes.md](references/failure-modes.md)。

### §1.1 完整示例(单图 I2V)

```python
integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium
close-up frames a barista (S1) opening the shutters of a small street bakery
before sunrise. The camera pushes in with small amplitude at slow speed as
she places a fresh loaf on the counter and says: "First batch of the morning."
[Shot 2] At 00:05.000, the camera cuts to a close-up of steam rising from
the sliced bread.

overall_soundscape: Wooden shutters scrape open over a quiet street as trays
clink softly inside the bakery. The doorbell rings once, followed by light
footsteps and the crisp sound of bread being sliced.

non_diegetic_music: A soft acoustic-guitar pattern at a moderate tempo,
joined by sparse upright-bass notes and a gentle fade at the end.
```

## §2 I2V 视觉连续性约束(从图来的独有)

> I2V 第一帧 = 用户图。**prompt 必须承诺"图到末帧不变",否则模型自由发挥 = 面目全非**。
>
> 通用主角锁定 → 父级 [§3](../video-prompt-method/SKILL.md) + [character-lock.md](../video-prompt-method/references/character-lock.md)。

```
MUST 显式写入 constraints.must_not_change(I2V 模板):
  - subject face identity(主体脸部保持)
  - subject facial expression baseline(基础表情不漂)
  - subject clothing color + 核心配饰(服饰不变)
  - background key anchor(图中关键锚点不消失)
  - color palette + 主光源(图的整体调性)

MUST NOT:
  - 跨段换主体(否则图失去意义)
  - 跨段换景别从全身跳到超特写(破坏图比例)
  - 加 prompt 没提到的"新角色"(模型会自创)
```

## §3 自然语言运镜三件套(Hailuo 02 → H3 迁移要点)

> ⚠️ **必读**:Hailuo 02 的方括号运镜 `[Push in] [Truck left]` 在 H3 上**不再生效**。H3 要求把运镜写进句子里,作为自然英语,三件套 = **运动类型 + 振幅 + 速度**。
>
> 通用镜头公式 → 父级 [§7](../video-prompt-method/SKILL.md)。H3 特有词表 → [references/camera-grammar.md](references/camera-grammar.md)。

### §3.1 三件套结构

| 维度 | 取值 | 默认 | 写法 |
|------|------|------|------|
| **类型** | zoom in/out, push in, pull out, pan left/right, truck left/right, tilt up/down, pedestal up/down, arc shot, tracking shot, static shot, shake slightly/strongly, POV, roll clockwise/counterclockwise | - | "The camera pushes in toward X" |
| **振幅** | small / large | medium(省略) | "with small amplitude" / "with large amplitude" |
| **速度** | slow / fast | normal(省略) | "at slow speed" / "at fast speed" |

### §3.2 "想要稳定"的强制写法

```
H3 默认会漂移。要锁定机位,必须显式说:
  "holds a static shot"
  "the camera stays completely locked off"
  "no camera movement"
```

## §4 首尾帧补帧(I2V 特有 2 张图模式)

```
适用:用户提供 2 张图(开始帧 + 结束帧),要 H3 补中间过程
image_mode: first_last_frame
中间过渡时长 / N 段平均分配:
  4s 中间 → 切 3 段 [00:00-00:01] [00:01-00:02] [00:02-00:04]

prompt 写法:
  [00:00-00:01] 从首帧状态过渡到中间态, <镜头保持稳定或单一运动>。
  [00:01-00:02] 中间态深化, <光线 / 调色 / 焦点渐变>。
  [00:02-00:04] 从中间态过渡到尾帧, <逐步落位尾帧构图>。

MUST:
  - 仅描述过渡演化,不创造新元素
  - 不复述首尾帧(模型已知)
  - 整体要求:首尾平滑衔接 + 不突兀
```

详细 R2V 分配 → [references/](../video-prompt-method/SKILL.md)。多模态复杂场景(>2 图 / 图+视频)→ 改去 [ref2v-h3-prompt](../ref2v-h3-prompt/SKILL.md)。

## §5 多镜头时序切镜(I2V 单图 + ≤15s)

```
[Shot N] At 00:NN.NNN, the camera cuts to ...
```

要点:
- 一个 Shot 一句独立描述(主体/动作/镜头独立完整)
- 时间戳用 5 位小数 `00:05.000` 而非整数
- **切镜判断标准:有新信息到来才切** — 仅距离变化时移动相机而非切镜
- 时段分配 → 父级 [§2](../video-prompt-method/SKILL.md)(5/6/8s 切 3 段 / 10s+ 切 4-5 段)

## §6 输出模板(交付格式 · 时间切片)

子 skill 触发后,主代理按此结构产出(继承父级时间切片 + H3 三段式):

```yaml
【平台】MiniMax H3
【模式】I2V(单张首帧图)
【时长】8s  【分辨率】768P  【画幅】3:4

# integrated_multimodal_description  (视觉连续性 + 时间切片)
[00:00 - 00:02]
<景别>, <主体动作:谁 + 做什么>, <主体位置:谁在哪里 + 出现方式>,
<精确化描述 + 镜头 + 动作>(KEEP IDENTITY LOCKED)。
[00:02 - 00:05]
<...>
[00:05 - 00:08]
<...>

整体要求: <must_not_change 全量 + 全程面部清晰 + 节奏关键词 + 动作连贯性>

# overall_soundscape
<环境音 + 动作触发 + 节奏>

# non_diegetic_music
<BGM + 节奏 + 卡点 cue + 淡出>
```

时间切片填空法 → 父级 [§9 填空法 V2.0](../video-prompt-method/SKILL.md)。具体性反例 → 父级 [§11](../video-prompt-method/SKILL.md)。

## §7 子 skill 自检

```
继承父级(§11 反例速查) + I2V 平台特化项:
- [ ] 三段顺序:description → soundscape → music
- [ ] 运镜必带三件套(类型 / 振幅 / 速度)
- [ ] 多镜头必带时间戳 00:NN.NNN
- [ ] 每个 Shot 含时间分段 [HH:MM-HH:MM]
- [ ] constraints.must_not_change 含 5 项(I2V 特化):脸/表情/服饰/锚点/调色
- [ ] 不跨段换主体 / 不换景别跳变 / 不自创新角色
- [ ] 静态场景显式 "holds a static shot"
```

## §8 references

### 平台特化(本 skill 自带)
- [references/camera-grammar.md](references/camera-grammar.md) — H3 完整运镜三件套词表(95 行)
- [references/audio-layers.md](references/audio-layers.md) — H3 三层音频分离细则(81 行)
- [references/failure-modes.md](references/failure-modes.md) — 7 类失败模式 + 修复指令(209 行,含中文笔记法反例)
- [references/hailuo02-migration.md](references/hailuo02-migration.md) — Hailuo 02 → H3 迁移对照表(96 行)

### 继承父级 skill(通用方法学)
- [../video-prompt-method/SKILL.md](../video-prompt-method/SKILL.md) — 通用方法论(198 行)
- [../video-prompt-method/references/time-segments.md](../video-prompt-method/references/time-segments.md) — 时间切片法
- [../video-prompt-method/references/character-lock.md](../video-prompt-method/references/character-lock.md) — 主角锁定 + 配角限定
- [../video-prompt-method/references/concreteness.md](../video-prompt-method/references/concreteness.md) — 抽象→具体改写
- [../video-prompt-method/references/negative-space.md](../video-prompt-method/references/negative-space.md) — 留白原则
- [../video-prompt-method/references/audio-design.md](../video-prompt-method/references/audio-design.md) — 声音三层设计

### 历史
- ~~references/chinese-prompt-method.md~~ — 已删除(337 行私有内容已上提至父级 skill 5 个 references)

## §9 来源

- [MiniMax H3 提示词指南(官方)](https://minimaxh3.studio/zh/guide/minimax-h3)
- [MiniMax H3 视频生成 API](https://platform.minimax.io/docs/guides/video-generation)
- [海螺图生视频 API(Hailuo 02)](https://platform.minimaxi.com/document/image_to_video)
- [promptslove H3 generator 实战](https://promptslove.com/free-tools/minimax-video-prompt-generator/)
- [ComfyUI H3 教程](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)
- 父级 skill `video-prompt-method` SKILL.md(2026-08-20)