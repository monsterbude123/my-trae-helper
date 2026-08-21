---
name: video-prompt-method
description: 视频提示词通用方法论 — 时间切片 / 主角锁定 / 抽象具体化 / 声音设计 / 留白原则。适配任何视频生成场景: t2v / i2v / v2v / ref2v / multi-media-to-v 等。本 skill 是 aigc-smart-kit 的"方法学爹",所有视频 prompt 儿子都应继承此处方法论 + 加平台 / 场景特化层。Use when the user wants to learn or apply general video prompting methodology, or build platform-specific video prompt skills.
version: 1.0.0
parent: aigc-smart-kit
role: method-father
license: MIT
created: 2026-08-20
---

# video-prompt-method — 视频提示词方法学(爹 skill)

> 本 skill 是 `aigc-smart-kit` 下所有"视频 prompt 儿子"的**方法学来源**。不写平台特化(H3 / Seedance / 可灵 / Vidu / 万相),只沉淀**通用规律**。平台特化放在儿子 skill(`i2v-h3-prompt` / `i2v-seedance-prompt` / `t2v-h3-prompt` / `v2v-h3-prompt` / `ref2v-h3-prompt`)里。
>
> **蒸馏来源**:`i2v-h3-prompt/references/chinese-prompt-method.md`(2026-08-19 用户实战笔记 17 张)— 抽取为通用方法,删除 H3 特有内容。

## §0 何时加载

```
MUST 加载: 用户问视频提示词通用方法 / 时间切片 / 主角锁定 / 镜头运镜公式 / 中文笔记法描述;
          视频 prompt 儿子 skill 创建 / 升级;5~15s 短视频需要多时段拆镜
MUST NOT:  T2I 改去 comfyui-prompt-engineer;视频剪辑 → comfyui-video-pipeline;
          平台特化问题("H3 怎么写")→ 直接加载儿子 skill
```

## §1 核心公式

```
视频 = 时间切片(when) + 主角(who) + 镜头视角(how to see) + 声音层(hear)
       §2             §3             §7                §8
       + §4 具体性 + §6 留白 + §5 一个镜头·三句话

四要素缺一不可: 没时间切片 → 主体漂移;没主角 → 没视觉焦点;没镜头三件套 → 模型困惑;没声音层 → 音画不同步
```

## §2 时间截法(必填)

```
[时间段] + [主体 + 动作 + 场景 + 镜头] + [STYLE 锚]
格式: [00:00-00:03] | 必填四要素: 主体/动作/场景/镜头(每时段独立写完) | STYLE 锚: 同上一段(SAME ART STYLE)
```

### §2.1 切分原则 — 按"前因后果"

```
三段弧线(6~8s):  登场 [00:00-00:02] → 展开 [00:02-00:05] → 收束 [00:05-00:08]
四段弧线(10s+):  登场 [00-3s] → 展开 [3-8s] → 收束 [8-10s] → 特写 [12-15s]

❌ 反例: 按"画面数量"切 / 按"音乐节拍"切 / 一段连写 6s 全部内容
```

### §2.2 时段长度对照(详细见 [references/time-segments.md](references/time-segments.md))

| 总时长 | 段数 | 切法 |
|--------|------|------|
| 5/6/8s | 3 段 | `[0-1/0-2] / [1-3/2-4/2-5] / [3-5/4-6/5-8]` |
| 10s+   | 4-5 段 | 按事件切,每段 2-3s |

## §3 主角锁定原则

```
MUST:     镜头语言围绕一个主角塑造 — 不要给 6 个主体平均用力
MUST NOT: 主角淹没在场景描写 / 主角设定模糊("年轻貌美女郎") / 配角抢戏

4 步: 1. 识别主角 → analyzer subject.name / 首帧图 C 位
     2. 镜头围绕主角塑造
     3. 锁定"前因后果"镜头(登场→展开→收束)
     4. 配角最多 2 个,每个 1-2 句话

5 要素(可自由替换): 主体 + 动作 + 场景 + 镜头视角 + 镜头运动 + 艺术风格(替换 3 要素即可生成新场景,身份一致性保留)

锁定约束: must_not_change 含主体脸部/表情/核心外貌;MUST NOT 跨段改变服饰颜色(除非剧情)/身份线索/主场景锚点
```
完整细则 + 反例 → [references/character-lock.md](references/character-lock.md)

## §4 具体性原则

```
三层具体: 1. 年龄/身份(20 岁东方少女)  2. 外貌可数特征(一字肩蕾丝/蝴蝶结/珍珠串)  3. 装饰/细节(大珍珠耳环/水晶手镯/蓝眼睛/瓷白肌肤)
改写流程: 找抽象词 → 问"眼睛能看见的具体物件"→ 列 3-5 个具体物件/动作/颜色/材质 → 替换 → 朗读检验"闭上眼能想象出画面"

❌ "年轻貌美的女郎穿过走廊"   ✅ "20 岁东方少女,白色一字肩蕾丝连衣裙,白色蝴蝶结,大珍珠耳环,蓝眼睛瓷白肌肤"
❌ "一片美丽的森林"           ✅ "古老红杉林,阳光透过树冠形成光柱,苔藓覆盖地面直径 2 米的圆形巨石"
```
完整细则 + 反例 → [references/concreteness.md](references/concreteness.md)

## §5 一个镜头 · 三句话公式

```
句 1: 景别 + 主体动作(谁 + 做什么)
句 2: 主体位置(谁在哪里 / 出现方式)
句 3: 镜头推进过程中主体的精确化描述(景别 + 镜头 + 动作)

模板: [景别] [主体] [动作], 在 [位置] 出现, 镜头 [类型] with [振幅] at [速度] [方向].
例:   A medium shot of a 20-year-old eastern girl walking into the frame, appearing at the center of a dim hallway, the camera pushes in with small amplitude at slow speed toward her face.

边界: 单时段 5s 内 ✅ 三句话 / ❌ 5~7 句 → 主体漂移;多镜头切镜: 每个 Shot 独立三句话,Shot 2 用 [At 00:05.000, the camera cuts to ...] 衔接
```

## §6 避免过度指定 + 留白

```
留空原则: 负面约束 "no X" 比正面"完美细节"更生效;关键三处必须写(主体/主动作/主光源);装饰元素留 1 句话带过或省略

❌ "每一颗雪花都不同、夕阳融进霜雪、海面倒映出 12 种渐变色彩"   → 模型无法理解 + 互相矛盾
✅ "夕阳倒映在冰封的海面,形成一条橙色光带"
```

| 级别 | 内容 | 必填? |
|------|------|-------|
| **MUST 具体** | 主体身份 / 主动作 / 主光源 / 主要道具 | ✅ |
| **SHOULD 具体** | 主场景(一句话)+ 美学风格(STYLE 锚) | ⚠️ |
| **留白 OK** | 背景杂物 / 路人表情 / 装饰纹理 / 边角物件 | - |
| **留白 MUST** | 倒数第二句之后的内容(给模型发挥空间) | - |

完整细则 → [references/negative-space.md](references/negative-space.md)

## §7 镜头三件套(视角 + 运动 + 构图)

```
三件套: 视角 CAMERA ANGLE(站哪看) / 运动 CAMERA MOTION(机位怎么动)/ 构图 COMPOSITION(东西怎么摆)
视角(8): 平视 eye-level / 仰拍 low-angle / 俯拍 high-angle / 过高 over-the-head / 第一人称 POV / 航拍 aerial-shot / 俯冲 dive-shot / 低角度仰拍 low-angle-uphold
运动(6): 变焦 zoom in/out / 推 push in / 升降 pedestal+tilt / 平移 pan+truck / 拉远 pull out / 环绕 arc shot
构图(4): 三分法 rule-of-thirds / 居中 center-frame / 极简 minimalist / 对角线 diagonal

组合: [景别] shot, [视角], the camera [运动] with [振幅] at [速度], [构图], [主体 + 动作], [场景], [STYLE].
```

> 平台特化 → 儿子 skill 的 `references/camera-grammar.md`(例:`i2v-h3-prompt/references/camera-grammar.md`)。

## §8 声音设计三层

```
BGM 氛围       →  non_diegetic_music     (剧情外音乐)
音效节拍       →  overall_soundscape     (动作触发 + 环境)
情绪节奏 / 对白  →  description 内的对白 / SFX 触发

中文→英文: "配轻快的钢琴曲,在主角走入走廊时铃响一下"  ↓
non_diegetic_music: A light piano pattern at a moderate tempo with gentle fade.
overall_soundscape: A small bell rings once as she enters the hallway, with soft ambient indoor air conditioning hum and distant footsteps.
SFX MUST 在 description 写: [S1] "The bell rings once"(与对白同句)/ [FX] "a crisp slice sound"(单独音效)
```

平台特化 → 儿子 skill 的 `references/audio-layers.md`。完整细则 → [references/audio-design.md](references/audio-design.md)

## §9 填空法 V2.0 模板

```
[景别 + 主体(维持谁/调用谁) + 动作 + 场景(在此刻 + 渲染 X 效果)] + STYLE
填空位: 景别: medium/close-up/wide/extreme close-up | 主体: 维持/调用 | 动作: 主动作+次动作二选一 | 场景: 在此刻+渲染 X 效果 | STYLE: 同上一段(SAME ART STYLE)

完整填空示例(6s · 3 段):
[00:00-00:02] 中近景, 女生 A 转头看向镜头, 站在街角咖啡店门前, 20 岁 + 浅色风衣 + 围巾 + 微微笑容。
[00:02-00:05] 中近景, 女生 A 抬手指向橱窗, 镜头推进, 手指指向橱窗的同时目光跟随。
[00:05-00:08] 中近景, 女生 A 转头面向镜头微笑, 镜头拉远, 收束于笑容定帧。
```

## §10 主体运动跨时段细分模板

| 时段 | 阶段 | 主体 | 动作 | 场景 | 镜头 |
|------|------|------|------|------|------|
| [00-3s]   | 登场 establish | 调用新主体,身份+外貌+服饰 | 入画/起身/睁眼 | 主场景第一次亮相 | 中景/远景,运镜轻推 |
| [3-8s]    | 展开 develop   | 维持 | 主动作+次动作(≤2) | 主场景延续 | 中景/近景,运镜跟拍 |
| [8-10s]   | 收束 resolve   | 维持 | 主动作完成/表情凝固 | 主场景收束/切到象征物 | 中近景,运镜缓推或静止 |
| [12-15s]  | 特写 climax    | 维持 | 表情细节/道具特写 | 极简背景或虚化 | extreme close-up,微动或静止 |

跨时段一致性 MUST: SAME ART STYLE 每段重复 / 主体身份(姓名/服饰/核心外貌)每段首句复述 / 镜头编号或时间戳不冲突 / MUST NOT 跨段改变主体服饰颜色(除非剧情)

## §11 反例速查(9 类)

| ❌ | ✅ |
|----|---|
| 一段连写 6s 全部内容 | 按 `[HH:MM-HH:MM]` 时间切片(§2) |
| 主角淹没在场景描写 | 主体段先写,场景 1-2 句承载(§3) |
| 6 个主体平均用力 | 主角 60%+ 配角 ≤ 2 个(§3) |
| 没有"前因后果"结构 | Opening → 展开 → 收束(§2.1) |
| 镜头语言与主体动作混写 | 三层独立:景别 + 镜头 + 主体动作 各占一短句(§5) |
| 抽象词("高级感 / 震撼 / 大片感") | 替换为具体可见词(§4 / §5) |
| 过度指定(12 种渐变 / 每一颗雪花都不同) | 负面约束 + 留白(§6) |
| 没有 STYLE 锚 / 跨段 STYLE 漂移 | 同上一段 STYLE 锚(SAME ART STYLE)复述 |
| 配角色彩过浓抢戏 | 配角只 1-2 句话提到(§3) |

## §12 继承协议 & references

每个儿子 skill MUST: frontmatter metadata.parent = aigc-smart-kit;metadata.extends = video-prompt-method;SKILL.md §0 引用本 skill 方法论;章节指针到本 skill references/(不复制内容);自带独立 references/(camera-grammar / audio-layers 等平台特化)

references(从 i2v-h3-prompt/references/chinese-prompt-method.md 提炼,删除 H3 特有内容):
- [time-segments.md](references/time-segments.md) — 时间切片法 + 切分原则 + 反例
- [character-lock.md](references/character-lock.md) — 主角锁定 + 配角限定 + 反例
- [concreteness.md](references/concreteness.md) — 具体性原则 + 化抽象为具体 + 反例
- [negative-space.md](references/negative-space.md) — 避免过度指定 + 留白 + 反例
- [audio-design.md](references/audio-design.md) — 声音三层设计 + 节拍卡点

references/ 责任分工: 本 skill (爹) → 通用方法论;儿子 skill (H3 等) → 平台特化(三段式 / Hailuo02 迁移 / R2V 分配) + 英文运镜词表 / 平台原生失败模式

## §13 来源

来源: 用户实战笔记 `docs/references/note-video-prompt/`(17 张 jpg, 2026-08 蒸馏) + MiniMax H3 / Seedance 2.5 / 可灵 3.0 / Vidu Q3 / 万相 2.7 跨平台验证。创建日期:2026-08-20。
