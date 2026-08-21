# Seedance 2.5 — 电影感运镜词表

> Seedance 对方向性电影术语反应良好。用机长能听懂的语言,不要用"cinematic"这种模糊词。

## §0 黄金法则

| 反例(弱 prompt) | 正确(强 prompt) |
|------------------|------------------|
| "cinematic shot of a chef plating pasta" | "medium shot of a chef plating pasta, slow dolly in to the plate, shallow depth of field" |

> ⚠️ 一个 beat 一个主运镜 — 不要在 1 秒内堆 3 个相反方向的运镜。

## §1 推拉类

| 术语 | 中文 | 适用场景 |
|------|------|----------|
| `slow dolly in` | 缓推近 | 强调 / 聚焦 / 情绪收紧 |
| `push in` | 推进 | 主体靠近 |
| `pull back` | 拉远 | 揭示环境 |
| `dolly out` | 后撤 | 拉开距离 |
| `zoom in` | 变焦推近 | 快速聚焦(慎用,易出 zoom 感) |
| `zoom out` | 变焦拉远 | 快速揭示 |

## §2 摇移类

| 术语 | 中文 | 适用场景 |
|------|------|----------|
| `handheld pan left` | 手持左摇 | 纪实感 / 紧张 |
| `handheld pan right` | 手持右摇 | 同上 |
| `smooth pan` | 稳定摇 | 优雅 / 抒情 |
| `whip pan` | 甩镜 | 转折 / 能量爆发(慎用) |

## §3 稳定 / 锁定类

| 术语 | 中文 | 适用场景 |
|------|------|----------|
| `locked-off` | 锁机位 | 产品类 / 对话 |
| `static` | 静态 | 同上 |
| `tripod locked` | 三脚架锁定 | 极致稳定 |

## §4 轨迹类

| 术语 | 中文 | 适用场景 |
|------|------|----------|
| `low tracking shot` | 低位跟拍 | 跟随脚步 / 车轮 |
| `arc shot` | 环绕 | 产品 360° / 角色展示 |
| `crane up` | 摇臂升 | 揭示大场景 |
| `crane down` | 摇臂降 | 落定收束 |
| `steadicam` | 斯坦尼康 | 跟拍主角(平滑感) |

## §5 主观 / 抖动

| 术语 | 中文 | 适用场景 |
|------|------|----------|
| `POV` | 第一人称 | 主观视角 |
| `shake slightly` | 微抖 | 紧张 / 纪实 |
| `handheld` | 手持 | 整体不稳感 |

## §6 30s 内镜头序列范式

### §6.1 30 秒镜头节奏模板(经典)

```
opening (0-6s):     宽景建立 → 缓推
progression (6-16s): 缓推近 → 主体特写
turn (16-24s):       特写 → 拉远 / 转场
resolution (24-30s): 拉远定格 / 收束
```

### §6.2 30 秒镜头节奏模板(产品广告)

```
opening:     locked-off 产品近景
progression: slow dolly in 产品细节
turn:        arc shot 360° 旋转
resolution:  pull back 揭示整体场景
```

### §6.3 30 秒镜头节奏模板(对话 / 表演)

```
opening:     wide shot 场景建立
progression: push in 主对话者
turn:        over-the-shoulder 反打
resolution:  wide shot 揭示新信息
```

## §7 反例(MUST 避免)

### §7.1 单 beat 堆多个运镜

```
❌ "medium shot of the chef plating, slow dolly in, then arc shot, then pull
   back, all in 6 seconds"
   → 6 秒 4 个运镜 = 混乱

✅ 一个 beat 一个主运镜,Sequence 多个 beat
```

### §7.2 全部都用 handheld

```
❌ 全程 handheld + shake
   → 30 秒都在抖,观众累

✅ Opening 锁定 → Progression 缓推 → Turn 微抖 → Resolution 锁定
```

### §7.3 用"cinematic"代替具体描述

```
❌ "cinematic shot"
   → 模型不知道要什么

✅ "medium shot, slow dolly in, shallow depth of field, warm color grading"
```

### §7.4 Turn 用相同运镜

```
❌ Opening 用 push in,Turn 也用 push in
   → 没有转折感

✅ Opening 用 wide → Progression 用 push in → Turn 用 arc / cut → Resolution 用 pull back
```

## §8 来源

- [Venice.ai Seedance 2.5 prompt tips](https://venice.ai/blog/seedance-2-5-prompt-tips)
- [CometAPI Seedance 2.5 prompting](https://www.cometapi.com/how-to-prompt-seedance-2-5/)
- [Seedance 2.5 官方 launch notes](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)