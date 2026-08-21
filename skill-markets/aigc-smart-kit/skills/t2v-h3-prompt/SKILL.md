---
name: t2v-h3-prompt
description: 纯文字 → MiniMax H3 / Hailuo 视频提示词专项(T2V)。当用户想从一段文字描述(无图)生成 MiniMax H3 或 Hailuo 系列视频时加载。继承爹 skill `video-prompt-method` 的方法论,加 H3 平台特化(三段式 / 运镜三件套)+ T2V 场景特化(主体 / 场景 / 构图全部精确化描述)。Use when the user wants text-to-video prompts for MiniMax H3 / Hailuo without an input image.
version: 1.0.0
license: MIT
metadata:
  parent-skill: video-prompt-method
  sibling-skills:
    - i2v-h3-prompt
  platform:
    - MiniMax-H3
    - MiniMax-Hailuo-2.3
    - MiniMax-Hailuo-02
    - MiniMax-Hailuo-2.3-Fast
  input-mode: t2v
  created: 2026-08-20
---

# t2v-h3-prompt — MiniMax H3 / Hailuo T2V 提示词专项

> T2V(纯文字 → 视频)在 MiniMax H3 上跑偏率高,**根因是抽象 prompt**。本 skill = 爹 `video-prompt-method` 方法论 + H3 三段式 + T2V 7 维度精确化公式。

## §0 何时加载

```
MUST 加载:
  - 用户给一段文字 + 想要 MiniMax H3 / 海螺生成视频
  - "用纯文字描述生成视频,不用图"
  - "T2V / 纯文字 prompt / 无图参考"
  - "写一个 MiniMax T2V prompt"

MUST NOT 加载:
  - 用户有图 → 改去 i2v-h3-prompt
  - 用户已有视频想做图生视频 → 不在本 skill 范围
  - Seedance / 可灵 / Vidu / 万相 → 改去对应 i2v-* / 暂未支持平台
  - 图片生成(T2I) → 改去 minimax-multimodal(image)
```

## §1 T2V vs I2V 关键差异(决定 prompt 必须显式写什么)

| 维度 | I2V(图生视频) | T2V(纯文字) | Prompt 影响 |
|------|------------|-----------|------------|
| 主体来源 | 图已锁定身份 | **文本必须精确化**(年龄/族裔/外貌/服装/配饰) | T2V 失精度 → 模型自创主角 |
| 场景来源 | 图已暗示 | **文本必须精确化**(地点/时段/天气/关键元素) | T2V 失精度 → 场景随意 |
| 构图 | 图已暗示 | **必须显式写景别 / 视角 / 构图方式** | T2V 失精度 → 远全近随机 |
| 镜头运动 | 图已暗示节奏 | 必须显式 + 运镜三件套 | 同 I2V |
| must_not_change | 适用(锁脸/锁物) | **不适用 — 0 → 1 创造** | T2V 不写 must_not_change |
| 抽象→具体 | 需要 | **更关键** | T2V 7 维度清单全命中 |

## §2 7 维度精确化公式(T2V 核心)

> T2V 没有图参考,**prompt 必须是"眼睛就能看到的描述"**。
> 每个维度缺失 → 模型自由发挥 → 跑偏。
> 完整示例 + 反例库 → [references/t2v-precise-formula.md](references/t2v-precise-formula.md)

| # | 维度 | 必含字段 | 反例 → 正例 |
|---|------|---------|------------|
| 1 | **主体** | 年龄 + 族裔 + 外貌 + 服装 + 配饰 + 表情 | ❌"美丽的女子" → ✅"20 岁东方少女,白色一字肩蕾丝连衣裙,白色蝴蝶结发饰,蓝眼睛瓷白肌肤" |
| 2 | **场景** | 地点 + 时段 + 天气 + 关键元素 | ❌"在街上" → ✅"巴黎街角清晨自然光,鹅卵石路面,身后有 19 世纪公寓" |
| 3 | **构图** | 景别 + 视角 + 构图方式 | ❌"好看的构图" → ✅"半身景别,平视视角,黄金分割构图" |
| 4 | **镜头运动** | 类型 + 振幅 + 速度(三件套) | ❌"镜头动一下" → ✅"the camera pushes in with small amplitude at slow speed" |
| 5 | **渲染** | 光照 + 调色 + 质感 | ❌"好看的色调" → ✅"柔和自然光 + 暖色调 + 胶片颗粒感" |
| 6 | **动作** | 每时段独立 + 时序词 | ❌"她走路" → ✅"在 [00:02-00:05] 段缓慢走向橱窗" |
| 7 | **声音** | 每段触发音 + 整体音景 | ❌"加点背景音" → ✅"鹅卵石上的高跟鞋声 + 远处钟声" |

## §3 主角锁定(从 0 创造,比 I2V 更严)

> **T2V 铁律**:prompt 第一句必须显式确定主角。
> 模型不会自动识别主角 — 不显式 = 模型自己挑 = **失控**。

```
主角声明模板(第一句):
  "一名 [年龄] [族裔] [外貌关键词 3-5 个] [服装描述] [配饰] [表情]"

示例:
  ✅ "一名 20 岁东方少女,蓝眼睛瓷白肌肤粉润唇,身穿白色一字肩蕾丝连衣裙,
      头扎白色蝴蝶结发饰与珍珠串,表情温柔微笑"
  ❌ "一个美丽的女孩"(模型选谁?什么族裔?穿什么?全靠猜)
```

**vs I2V 的差异**:I2V 主角来自图片识别(image-report.json → subject.name),T2V 主角**完全靠 prompt 第一句声明**。少一字 → 模型自创。

## §4 三段式公式(H3 官方,继承 i2v §1)

```
必备三段:
  integrated_multimodal_description: [Shot 1] ... [Shot 2] ...
    → 镜头 + 主体 + 动作 + 视觉风格 + 镜头运动 + 对白 + SFX 触发
  overall_soundscape: ... (环境音 / 对白 / 音效 / 静音场景)
  non_diegetic_music: ... (BGM / 配乐 / 留空)

控制部件(写入 integrated_multimodal_description):
  必填: 主体(精确化) + 动作(时序) + 场景(精确化) + 镜头(运镜三件套)
  选填: 渲染风格 / 音频 / 文字渲染
```

完整公式 + 三件套词表 → [references/i2v-h3-prompt/camera-grammar.md](references/i2v-h3-prompt/camera-grammar.md) + [references/i2v-h3-prompt/audio-layers.md](references/i2v-h3-prompt/audio-layers.md)

## §5 时间切片(继承爹 §2 + 中文笔记法 §10)

```
6s 切 3 段:
  [00:00 - 00:02]  Opening(主角第一句锁定 + 出现方式 + 第一动作)
  [00:02 - 00:05]  动作展开(主要动作 + 镜头运动)
  [00:05 - 00:08]  收束(动作到位 + 表情定帧)

T2V 时段内必含:
  - 时间段 [HH:MM-HH:MM]
  - 景别 + 视角 + 构图
  - 主体动作(谁 + 做什么 + 方向)
  - 精确化描述(主角外貌/服装/表情)
  - 镜头运动(独立短句,运镜三件套)

时长调整:
  8s  → 0-2s / 2-5s / 5-8s(标准 3 段)
  5s  → 0-1s / 1-3s / 3-5s(压缩 3 段)
  10s+ → 按事件切 4-5 段,每段 2-3s
```

完整中文笔记法 → [references/i2v-h3-prompt/chinese-prompt-method.md](references/i2v-h3-prompt/chinese-prompt-method.md)

## §6 T2V 特有反模式(MUST 避)

| ❌ 反模式 | ✅ 正确做法 | 根因 |
|---------|----------|------|
| "一个美丽的女子" | 20 岁东方少女 + 蓝眼睛 + 白色蕾丝连衣裙 | 抽象 → 模型选人 |
| "可爱的小孩" | 5 岁金发男孩 + 蓝色 T 恤 + 牛仔短裤 | 缺外貌 → 跑偏 |
| "在街上" | 巴黎街角清晨 + 鹅卵石 + 19 世纪公寓 | 缺场景 → 跑偏 |
| "缓缓走动" | 在 [00:02-00:05] 段向右走向橱窗 | 缺时序 + 方向 |
| "好看的色调" | 柔和自然光 + 暖色调 + 胶片颗粒 | 抽象 → 跑偏 |
| "用 I2V 的图是场景原则" | **T2V 没有图,必须显式描述一切** | 公式误用 |
| 让模型创造主角 | 第一句必须锁定主角全部特征 | 模型自由 → 失控 |
| 用 must_not_change | T2V 是 0→1,无约束 | 反逻辑 |

## §7 输出模板(交付格式)

```yaml
【平台】MiniMax H3
【模式】T2V(纯文字,无图)
【时长】8s  【分辨率】768P  【画幅】3:4

# integrated_multimodal_description  (7 维度精确化 + 时间切片)
[00:00 - 00:02]
<景别>, <主体动作:谁 + 做什么>, <主体位置:谁在哪里 + 出现方式>,
<精确化描述:主角年龄/族裔/外貌/服装/配饰/表情>。
[00:02 - 00:05]
<景别>, <主体动作 + 方向>, <精确化描述 + 镜头运动(三件套)>。
[00:05 - 00:08]
<景别>, <收束动作:动作到位 + 表情定帧>, <镜头收束 + 整体要求>。

整体要求:<主角全程特征锁定 + 全程面部清晰 + 节奏关键词 + 动作连贯性>

# overall_soundscape
<环境音(精确化场景音) + 动作触发 + 节奏>

# non_diegetic_music
<BGM + 节奏 + 卡点 cue + 淡出>
```

## §8 子 skill 自检(必跑)

```
- [ ] 主角在第一句显式锁定(年龄 + 族裔 + 外貌 + 服装 + 配饰 + 表情)
- [ ] 7 维度精确化清单全部命中(主体/场景/构图/镜头/渲染/动作/声音)
- [ ] 每段时间切片独立五件套(景别/动作/位置/精确化/镜头)
- [ ] 场景不抢戏(≤1-2 句承载,主体段先写)
- [ ] 整体要求段含"主角特征全程锁定"
- [ ] 运镜三件套(类型/振幅/速度)全部命中
- [ ] 三段顺序:description → soundscape → music
- [ ] 不含 must_not_change(T2V 无此约束)
```

## §9 references

- [references/t2v-precise-formula.md](references/t2v-precise-formula.md) — 7 维度精确化清单 + 完整示例 + 反例库
- [references/i2v-h3-prompt/camera-grammar.md](references/i2v-h3-prompt/camera-grammar.md) — 运镜三件套词表(继承)
- [references/i2v-h3-prompt/audio-layers.md](references/i2v-h3-prompt/audio-layers.md) — 三层音频分离(继承)
- [references/i2v-h3-prompt/failure-modes.md](references/i2v-h3-prompt/failure-modes.md) — 7 类失败模式 + 修复指令(继承)
- [references/i2v-h3-prompt/chinese-prompt-method.md](references/i2v-h3-prompt/chinese-prompt-method.md) — 中文笔记法完整方法学(继承)
- **爹 skill**:`../video-prompt-method/SKILL.md` — 通用方法论(三段式 / 时序 / 主角锁定 / 抽象→具体)

## §10 边界声明(避免与兄弟 skill 重复)

```
本 skill (t2v-h3-prompt) 特化:
  ✅ T2V(无图)的 7 维度精确化公式
  ✅ 主角从 0 创造的锁定约束(第一句锁定)
  ✅ T2V 特有反模式(抽象词 / 公式误用 / must_not_change)
  ✅ 时间切片在 T2V 下的精确化填空

i2v-h3-prompt 接管:
  → I2V 单图 / 首尾帧 / R2V / 多镜头切镜
  → 参考素材角色分配(图片/视频/音频职责)
  → "图是场景"原则(I2V 默认场景来图)

video-prompt-method(爹)接管:
  → 通用方法论(三段式骨架 / 时序切镜原理 / 主角锁定通用原则)
  → 跨平台方法学(种子 / 可灵 / Vidu 等通用部分)
  → 抽象→具体的通用公式
```

## §11 来源

- [MiniMax H3 提示词指南(官方)](https://minimaxh3.studio/zh/guide/minimax-h3)
- [MiniMax H3 视频生成 API](https://platform.minimax.io/docs/guides/video-generation)
- [海螺文生视频 API](https://platform.minimaxi.com/document/text_to_video)
- [promptslove H3 generator 实战](https://promptslove.com/free-tools/minimax-video-prompt-generator/)
- 爹 skill `video-prompt-method` SKILL.md(同包内,sibling)