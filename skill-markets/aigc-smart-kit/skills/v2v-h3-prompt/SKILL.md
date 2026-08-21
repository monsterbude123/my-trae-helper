---
name: v2v-h3-prompt
description: 视频 → 视频(MiniMax H3 / Hailuo 2.3)提示词专项。当用户提供已有视频、想续写 / 拼接 / 风格化 / 元素替换时加载。继承 video-prompt-method 爹 skill 的方法论,加 H3 平台 + V2V 场景特化层(3 大子模式:extend / first-last-frame / edit)。Use when the user wants video-to-video prompts for MiniMax H3 or Hailuo, including extension, first-last-frame interpolation, or editing.
version: 1.0.0
license: MIT
metadata:
  parent-skill: video-prompt-method
  platform:
    - MiniMax-H3
    - MiniMax-Hailuo-2.3
    - MiniMax-Hailuo-2.3-Fast
  input-mode: v2v
  sub-modes: [extend, first-last-frame, edit]
  created: 2026-08-20
---

# v2v-h3-prompt — MiniMax H3 / Hailuo 2.3 V2V 提示词专项

> H3 V2V = **视频连续性不可破**。图生视频的主体来自单帧,V2V 的主体来自 N 帧已发生的剧情;prompt 必须继承而不能改写。

## §0 何时加载

```
MUST:
  - 已有视频 + 续写/延长/拼接/风格化/元素替换 意图
  - 平台为 MiniMax H3 / Hailuo 2.3 的 V2V 调用
MUST NOT:
  - 1 张图 + 想动起来 → i2v-h3-prompt
  - 纯文字 T2V → i2v-h3-prompt §10
  - Seedance / Kling V2V → 对应平台 skill
```

## §1 V2V 三大子模式(按用户意图路由)

### §1.1 extend(视频延长)
```
关键:首帧继承 → 节奏匹配 → 风格延续
MUST: 显式"继续自原视频末帧";不复述原视频已有
适用:剧情续写 / 镜头延展 / 动作尾巴补完
```

### §1.2 first-last-frame(首尾衔接)
```
关键:首帧=A 末帧(已给);尾帧=B 首帧(已给);只描述变化
MUST: 提供 A 末帧 + B 首帧(image_mode=first_last_frame)
适用:转场 / 场景跳转 / 时间跳跃
```

### §1.3 edit(视频编辑)
```
关键:保留原构图/镜头/主体;修改目标明确;不破核心
MUST: 显式"保留 X / 修改 Y"
适用:风格迁移 / 元素替换 / 加滤镜
```

详细 → [references/sub-modes.md](references/sub-modes.md)

## §2 V2V 视频连续性约束(继承爹 + 加严)

```
爹铁律:主角锁定 ≥ 60% 篇幅,场景 ≤ 1-2 句,配角 ≤ 2 个
V2V 加严 3 条:
  1. 主体 LOCKED: prompt 显式 "(KEEP IDENTITY LOCKED)"
  2. 场景继承:不再"创建场景",而是"延续场景"(复用原视频场景词)
  3. 镜头语言继承:运镜写"承接 / 与原视频一致"语义
```

| 检查项 | MUST 标注 | 反例 |
|--------|----------|------|
| 帧间主体(脸/服装/发型) | subject LOCKED | 让主体换脸 ❌ |
| 帧间光线(调色/曝光/暖冷) | color palette HOLD | 续写段突然冷调 ❌ |
| 帧间节奏(快→慢 / 慢→快) | tempo LOCKED | 续写段突然静止 ❌ |

## §3 关键帧分析协议

```
采样:≤6s 抽 5 帧;6~10s 抽 7 帧;>10s 抽 9 帧(每 11%)
每帧分析 3 项:主体动作 / 镜头运动 / 调色光线
送 vision 模型,输出 keyframe_report.json
```

详细 → [references/keyframe-analysis.md](references/keyframe-analysis.md)

## §4 时间切片(继承爹 §2)

```
extend:续写部分独立切段(不再复用原视频时段);
  显式标注"从原视频末帧继续";新视频独立计时 [00:00 - 00:NN]
first-last-frame:中间过渡时长 / N 段 平均分配;
  示例(中间 4s,切 3 段):[00:00-00:01] [00:01-00:02] [00:02-00:04]
edit:与原视频同时长对齐;仅描述"变化点"出现的时间点
```

## §5 反模式(V2V 特有)

| ❌ 反模式 | ✅ 正确做法 |
|----------|------------|
| "把视频变好看"(无具体目标) | 明确"风格化为赛博朋克色调" |
| 让主体换脸 / 变形 | 主体 LOCKED,只改背景 |
| 续写时突然换景别(全身→特写) | 景别承接原视频末帧 |
| 编辑时改掉主体身份 | 保留主体,只改目标元素 |
| 不分析关键帧就写 prompt | 先抽 5 帧 + vision 分析 |
| 描述已经在视频里的内容 | 只描述变化,继承原有 |

## §6 输出模板(3 个子模式)

### §6.1 extend 模式模板

```yaml
【平台】MiniMax H3   【模式】V2V-extend
【输入】原视频末帧 + 续写意图
【输出时长】6s   【分辨率】768P  【画幅】3:4

# integrated_multimodal_description
[00:00 - 00:02] 接续原视频末帧,
  <承接末帧的姿态>,<镜头沿原方向继续>,
  <主体动作延续原剧情 + 明确新动作>(KEEP IDENTITY LOCKED)。
[00:02 - 00:05] <主体动作展开>,
  <镜头沿原节奏继续>,<新增次要元素>。
[00:05 - 00:06] <动作到位>,
  <表情 / 动作定帧>,<收束镜头>。
整体要求:主体 LOCKED + 镜头节奏延续 + 风格一致 + 与原视频无缝衔接。

# overall_soundscape
<承接原视频末尾音 + 续写段环境音 + SFX 触发>
# non_diegetic_music
<BGM 延续 + 卡点 cue + 淡出>
```

### §6.2 first-last-frame 模式模板

```yaml
【平台】MiniMax H3   【模式】V2V-first-last-frame
【输入】视频 A 末帧(首帧) + 视频 B 首帧(尾帧)
【输出时长】4s   【分辨率】768P  【画幅】3:4

# integrated_multimodal_description
[00:00 - 00:01] 从首帧状态过渡到中间态,
  <镜头保持稳定或单一运动>。
[00:01 - 00:02] 中间态深化,
  <光线 / 调色 / 焦点渐变>。
[00:02 - 00:04] 从中间态过渡到尾帧,
  <逐步落位尾帧构图>。
整体要求:首尾平滑衔接 + 不突兀 + 仅描述过渡演化。

# overall_soundscape
<承接首帧的环境音 + 过渡音效 + 尾帧环境的延续音>
# non_diegetic_music
<BGM 保持 + 不做突变>
```

### §6.3 edit 模式模板

```yaml
【平台】MiniMax H3   【模式】V2V-edit
【输入】原视频 + 修改目标
【输出时长】6s(与原视频同)   【分辨率】768P  【画幅】3:4

# integrated_multimodal_description
[00:00 - 00:02] <保持原视频构图 + 主体 KEEP IDENTITY LOCKED>,
  <镜头沿原轨迹>,
  <修改目标元素:色调 / 风格 / 道具>(如有 SFX 触发)。
[00:02 - 00:04] <修改目标深化>,
  <其他元素保持原状>。
[00:04 - 00:06] <修改完成 + 稳定>,
  <其他元素仍与原视频一致>。
整体要求:保留构图 / 主体 / 镜头 + 仅修改目标项 + 不破核心。

# overall_soundscape
<保持原视频音频 + 修改音效触发点>
# non_diegetic_music
<保持原 BGM + 必要时调整>
```

## §7 子 skill 自检

```
- [ ] 3 子模式路由正确
- [ ] 关键帧分析 ≥ 3 帧(按时长 5/7/9 帧)
- [ ] 主角 LOCKED 显式标注
- [ ] 时间切片匹配子模式
- [ ] extend:显式"从末帧继续"
- [ ] first-last-frame:首尾帧均给
- [ ] edit:明确"保留 X / 修改 Y"
- [ ] 不反向引用 I2V / T2V 公式
- [ ] 节奏 / 调色 / 光线 与原视频连续
```

## §8 references

- [sub-modes.md](references/sub-modes.md) — 3 子模式详细协议 + 完整示例
- [keyframe-analysis.md](references/keyframe-analysis.md) — 关键帧抽取 + vision 分析
- 继承爹 video-prompt-method references/(三段式 / 主角锁定 / 中文笔记法)
- 兄弟 i2v-h3-prompt references/camera-grammar.md / audio-layers.md / hailuo02-migration.md

## §9 来源

- H3 提示词指南:https://minimaxh3.studio/zh/guide/minimax-h3
- H3 平台 API:https://platform.minimax.io/docs/guides/video-generation
- 爹 skill:video-prompt-method(本仓内)
