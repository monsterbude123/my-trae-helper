---
name: i2v-seedance-prompt
description: ByteDance Seedance 2.0 / 2.5 图生视频(I2V)提示词专项。当用户要在 Seedance / 即梦 / 豆包 / 字节视频平台上为一张参考图或一组参考素材写 30 秒视频生成 prompt 时加载。覆盖四拍公式(Opening + Progression + Turn + Resolution)、50 槽参考素材预算(@Image / @Video / @Audio / @Clay Render 标签)、电影感运镜、对白双引号、音频节奏。Use when the user needs image-to-video or multi-reference prompts for ByteDance Seedance 2.0/2.5, including 30-second narrative arcs, reference binding, and beat-by-beat directing.
version: 1.0.0
license: MIT
metadata:
  parent-skill: aigc-smart-kit
  platform:
    - doubao-seedance-2-0
    - doubao-seedance-2-0-fast
    - doubao-seedance-2-5
  created: 2026-08-19
---

# i2v-seedance-prompt — ByteDance Seedance I2V 提示词专项

> Seedance 2.0 / 2.5 是字节豆包视频模型,核心差异 = **单片段最长 30s + 50 槽参考素材(30 图 + 10 视频 + 10 音频)**。这两个数字决定 prompt 的"工作单元":不再是单镜头,而是 30 秒的弧线。

## §0 何时加载

```
MUST 加载: 用户问以下任一问题
  - "用 Seedance / 即梦 / 豆包生成视频"
  - "30 秒视频 prompt 怎么写"
  - "Seedance 多模态参考怎么分配"
  - "Seedance @Image @Audio 标签语法"
  - 平台明确为字节豆包视频生态

MUST NOT 加载:
  - H3 / Hailuo → 改去 i2v-h3-prompt
  - 可灵 / Vidu / 万相 → 当前不在本包覆盖范围,告知用户暂未支持
  - 纯文字 T2V(没有图) → 本 skill 仍可加载,公式兼容
```

## §1 四拍公式(30 秒弧线)

> Seedance 2.5 单片段最长 **30 秒**。把 30 秒当完整短片来规划:开场钩子 + 主体动作 + 中段变化 + 证明点 + 最后停留。

### §1.1 四拍结构

| Beat | 时间范围 | 职责 |
|------|----------|------|
| **Opening** | 0-6s | 建立空间 / 主体亮相 / 镜头开局 |
| **Progression** | 6-16s | 节奏推进 / 主体动作展开 / 镜头运动 |
| **Turn** | 16-24s | 转折点 — 场景/情绪的转向(最容易遗漏!) |
| **Resolution** | 24-30s | 收束 / 品牌停留 / 镜头落定 |

### §1.2 冷萃咖啡广告示例

```yaml
overall: 一支 30 秒电影感产品广告(蓝调时刻,室内外切换,30 秒单镜头连续)
opening (0s to 6s):
  咖啡师的手在昏暗的备餐间里,蒸汽,晨光透过半掩的百叶窗,安静
progression (6s to 16s):
  房间开始热闹,节奏提升,同一双手继续工作,镜头开始平移
turn (16s to 24s):
  今天第一位顾客接过杯子,调色转暖,背景音压低,一段音乐进入
resolution (24s to 30s):
  镜头拉远到整家店,品牌围裙入画,最后 2 秒停留
references:
  @Image1 @Image2  → 室内空间 / 调色
  @Image3 @Image4  → 产品造型 + 标签
  @Video1          → 节奏参考
  @Audio1          → 音乐底
```

### §1.3 关键提醒

- ⚠️ **Turn 是最容易跳过的 beat** — 大多数 prompt 直接 Opening → Progression → Resolution,缺 Turn,结果就是 30 秒没有故事弧。
- ⚠️ **不要写成分镜头列表** — Seedance 2.5 不是要 30 个 1 秒镜头,而是要 1 个 30 秒的连续弧线。

## §2 50 槽参考素材预算

> "50 references" 不是 1 个池子里随便填 50 张图,而是 **3 个独立预算**。

| 类型 | 上限 | 用途 |
|------|------|------|
| **图片 (@Image)** | 30 | 角色 / 道具 / 场景 / 风格 / 构图 |
| **视频 (@Video)** | 10 | 动作 / 节奏 / 镜头行为 |
| **音频 (@Audio)** | 10 | 声音 / 音乐 / 节奏 |

### §2.1 参考素材职责分配

```
@Image1   角色正面(身份锁定)
@Image2   角色侧面
@Image3   场景 / 背景
@Image4   美学 / 色调参考
@Image5   道具特写
@Video1   运镜节奏参考(慢推 / 快切)
@Video2   动作节奏参考(连续性)
@Audio1   音乐底
@Audio2   环境音
@ClayRender  3D 几何块(空间结构)
```

## §3 标签语法(@Image / @Video / @Audio / @Clay)

```
@<type><N>  ← 引用第 N 个素材,prompt 中显式出现
```

### §3.1 完整 prompt 示例

```
A 30-second spot for a cold brew brand, one continuous take.

Opening (0s to 6s):
  A barista's hands in a dim prep kitchen before opening. Steam, cold light
  through a half-closed shutter. Quiet.

Progression (6s to 16s):
  The room fills and the pace lifts. Stay inside the same space, the same
  pair of hands keeps working.

Turn (16s to 24s):
  The first customer of the day takes the cup. The grade warms, room noise
  drops behind a single line of music.

Resolution (24s to 30s):
  Wide on the open shop, brand apron in frame, hold on the last two seconds.
  Room and grade from @Image1 @Image2. Product geometry and label from
  @Image3 @Image4. Pacing reference from @Video1. Music bed @Audio1.
```

## §4 运镜 + 对白 + 音频

### §4.1 电影感运镜

```
slow dolly in     缓推近(强调)
pull back          拉远(揭示)
handheld pan       手持摇(纪实)
locked-off / static  锁机位(产品)
low tracking shot  低位跟拍
```

> ⚠️ 每个 beat 一个主运镜 — 不要在 1 秒内堆 3 个相反方向的运镜。

### §4.2 对白(双引号)

```
A barista looks up from the espresso machine and says, "Your oat latte is
ready," then slides the cup toward camera.
```

要点:
- **双引号包裹** — 让模型识别为对白而非画面文字
- **每条短句** — 1-2 句最佳,长段独白会漂
- **注明情绪**:`warm` / `dry` / `whispered` / `urgent`
- **注明语言**(如果不是显然):`in English` / `in Mandarin`

### §4.3 音频节奏

```
声音要素分类:
  对白(双引号 + 情绪 + 语言)
  音效(音源材质 + 行为)
  BGM(音乐底 + 风格 + 起止)

音乐与画面时间点对齐:
  "Cut the edit to the rhythm of @Audio1 with beats landing on the flashes."
```

## §5 Prompt 字符 / 输出规格

| 项 | Seedance 2.5 |
|----|--------------|
| Prompt 字符上限 | **15,000** |
| 单片段时长 | 最长 30 秒 |
| 分辨率 | 480P / 720P(2.5),720P / 1080P(2.0 Pro) |
| 输出格式 | MP4 / MOV |
| 画幅 | 16:9 / 9:16 / 1:1 / 4:3 / 3:4 / 21:9 / 自适应 |

## §6 失败模式速查

| 现象 | 根因 | 修复 |
|------|------|------|
| 30 秒像 30 个随机镜头 | 写成了分镜头列表 | 重写为四拍弧线 + 1 个连续 take |
| Turn 不明显 | 跳过 Turn beat | 显式写 Turn 的情绪 / 调色转向 |
| 角色身份漂移 | 参考图角色没绑定 | `@Image1` 显式引用身份图 |
| 对白长段独白糊 | 单段太长 | 拆成多个 beat,每段 1-2 句 |
| 镜头一直抖 | 用了 handheld 但场景不适合 | 切 locked-off,产品类慎用 |
| 超出预算被截断 | 图片 / 视频 / 音频数量超 | 30/10/10 独立预算,不混算 |
| 音乐卡点错 | 没说时间点 | "beats land on X" 显式锚定 |

详细反例库 → [references/failure-modes.md](references/failure-modes.md)

## §7 输出模板(交付格式)

子 skill 触发后,主代理按此结构产出:

```yaml
【平台】ByteDance Seedance 2.5
【模式】I2V / 多参考(30s 弧线)
【时长】30s  【分辨率】720P  【画幅】16:9

overall: <一句话核心创意>

opening (0s to 6s):
  <主体 + 动作 + 镜头 + 环境 + 音效>
progression (6s to 16s):
  <节奏推进 + 主体动作 + 镜头运动 + 音乐进入时机>
turn (16s to 24s):
  <转折点 + 调色 / 情绪 / 场景转向>
resolution (24s to 30s):
  <收束 + 品牌 / 主体停留 + 结尾镜头>

references:
  @Image1-<N>   <用途>
  @Video<N>     <用途>
  @Audio<N>     <用途>

dialogue: "<对白>" — <角色> — <情绪>
audio: BGM <风格>; SFX <触发时机>
```

## §8 子 skill 自检

- 是否含 4 个 beat(Opening / Progression / Turn / Resolution)
- Turn 是否显式描述了"转向"(情绪 / 调色 / 场景)
- 参考素材总数:30 图 / 10 视频 / 10 音频 内(独立预算)
- 对白是否用双引号 + 情绪标注
- 单 beat 镜头不堆 3 个相反方向

## §9 references

- [references/30s-arc-cheatsheet.md](references/30s-arc-cheatsheet.md) — 四拍 + 时间戳速查
- [references/reference-budget.md](references/reference-budget.md) — 50 槽分配细则
- [references/camera-vocabulary.md](references/camera-vocabulary.md) — 电影感运镜词表
- [references/failure-modes.md](references/failure-modes.md) — 7 类失败模式 + 修复

## §10 来源

- [Seedance 2.5 官方页面(字节)](https://www.seeddance.io/zh/seedance-2-5)
- [CometAPI Seedance 2.5 prompting 指南](https://www.cometapi.com/how-to-prompt-seedance-2-5/)
- [Venice.ai Seedance 2.5 prompt tips](https://venice.ai/blog/seedance-2-5-prompt-tips)
- [Segmind Seedance 2.5 预迁移指南](https://blog.segmind.com/seedance-2-5-prompts-how-to-prep-your-workflow-now/)
- 蒸馏自 [docs/research/2026-08-19-i2v-prompt-skills.md](../../../docs/research/2026-08-19-i2v-prompt-skills.md)