# Seedance 2.5 — 30 秒弧线 + 时间戳速查

> Seedance 2.5 单片段最长 30s。把 30s 当 1 个完整短片来规划,而不是 30 个 1 秒镜头。

## §1 四拍时间预算

| Beat | 时间范围 | 占比 | 核心职责 |
|------|----------|------|----------|
| **Opening** | 0-6s | ~20% | 建立空间 / 主体亮相 / 镜头开局 |
| **Progression** | 6-16s | ~33% | 节奏推进 / 主体动作展开 / 镜头运动 |
| **Turn** | 16-24s | ~27% | **转折点** — 情绪 / 调色 / 场景转向 |
| **Resolution** | 24-30s | ~20% | 收束 / 品牌停留 / 镜头落定 |

> ⚠️ **Turn 不可省** — 大多数失败 prompt 直接 Opening → Progression → Resolution,结果是"30 秒素材"而非"30 秒故事"。

## §2 时间戳写法

```
opening (0s to 6s):
progression (6s to 16s):
turn (16s to 24s):
resolution (24s to 30s):
```

也支持更短的细分:

```
opening (0s to 3s):
opening-pivot (3s to 6s):
progression-rise (6s to 11s):
progression-peak (11s to 16s):
turn (16s to 20s):
turn-reveal (20s to 24s):
resolution (24s to 27s):
resolution-hold (27s to 30s):
```

## §3 各 beat 的 prompt 模板

### §3.1 Opening

```
opening (0s to 6s):
  <主体> + <空间建立> + <镜头开局> + <环境音 / 寂静>
  例: a barista's hands in a dim prep kitchen before opening. Steam,
      cold light through a half-closed shutter. Quiet.
```

### §3.2 Progression

```
progression (6s to 16s):
  <节奏推进> + <主体动作展开> + <镜头运动> + <音乐渐入>
  例: the room fills and the pace lifts. Stay inside the same space, the
      same pair of hands keeps working.
```

### §3.3 Turn

```
turn (16s to 24s):
  <转折事件> + <调色/情绪/场景转向>
  例: the first customer of the day takes the cup. The grade warms,
      room noise drops behind a single line of music.
```

> Turn 的 3 种典型写法:
> - **情绪转向**:紧张 → 平静 / 冷 → 暖
> - **场景转向**:室内 → 室外 / 远景 → 近景
> - **角色转向**:旁观 → 主角 / 主 → 反

### §3.4 Resolution

```
resolution (24s to 30s):
  <收束> + <品牌停留> + <镜头落定>
  例: wide on the open shop, brand apron in frame, hold on the last two
      seconds.
```

## §4 不同长度的拍数分配

| 总时长 | 推荐拍数 | 时间预算 |
|--------|----------|----------|
| 6s | Opening + Resolution(2 拍) | 0-3 / 3-6 |
| 10s | Opening + Progression + Resolution(3 拍) | 0-3 / 3-7 / 7-10 |
| 15s | Opening + Progression + Turn + Resolution(4 拍压缩) | 0-4 / 4-9 / 9-12 / 12-15 |
| 30s | 完整 4 拍 | 0-6 / 6-16 / 16-24 / 24-30 |

## §5 反例(MUST 避免)

### §5.1 写成了分镜头列表

```
❌ Shot 1 (0-1s): ... Shot 2 (1-2s): ... Shot 30 (29-30s): ...
   → Seedance 不会拍 30 个 1 秒镜头,会拍 1 个混乱的 30 秒

✅ opening (0s to 6s): ... progression (6s to 16s): ... turn (16s to 24s):
   resolution (24s to 30s): ...
   → 4 拍弧线 + 1 个连续 take
```

### §5.2 跳过 Turn

```
❌ opening → progression → resolution
   → 30 秒没故事弧

✅ opening → progression → turn → resolution
   → Turn 显式写"情绪 / 调色 / 场景转向"
```

### §5.3 镜头一直在抖

```
❌ 每个 beat 都写 handheld pan
   → 累加效应 = 摇晃 30 秒

✅ Opening 锁定,Progression 缓推,Turn 微抖,Resolution 拉远定格
   → 镜头语言有节奏变化
```

## §6 多段拼接(超过 30s 的内容)

```
Seedance 2.5 单段最长 30s,长内容用多段续写:
  第 1 段:0-30s(完整 4 拍 + 留尾衔接)
  第 2 段:30-60s(从第 1 段尾帧续写)

每段尾帧必须能自然接到下一段。
```

## §7 来源

- [Seedance 2.5 官方页面](https://www.seeddance.io/zh/seedance-2-5)
- [CometAPI Seedance 2.5 prompting 指南](https://www.cometapi.com/how-to-prompt-seedance-2-5/)
- [Segmind Seedance 2.5 prep guide](https://blog.segmind.com/seedance-2-5-prompts-how-to-prep-your-workflow-now/)