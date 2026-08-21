# H3 自然语言运镜三件套完整词表

> MiniMax H3 不再接受 Hailuo 02 的方括号运镜。运镜必须写进句子里: **运动类型 + 振幅 + 速度**。

## §1 运动类型(Motion Type)

### §1.1 推拉类

| 英文 | 中文 | 典型场景 |
|------|------|----------|
| zoom in | 拉近 | 强调细节 / 表情 |
| zoom out | 拉远 | 揭示环境 / 收束 |
| push in | 推进 | 主体靠近,情绪收紧 |
| pull out | 后撤 | 主体远离,场景展开 |

### §1.2 摇移类

| 英文 | 中文 | 典型场景 |
|------|------|----------|
| pan left | 左摇 | 横向扫视 |
| pan right | 右摇 | 横向扫视 |
| truck left | 左移 | 机位平移,主体在画面里 |
| truck right | 右移 | 机位平移,主体在画面里 |
| tilt up | 上摇 | 仰视 / 抬头 |
| tilt down | 下摇 | 俯视 / 低头 |
| pedestal up | 上升 | 机位升高 |
| pedestal down | 下降 | 机位降低 |

### §1.3 轨迹类

| 英文 | 中文 | 典型场景 |
|------|------|----------|
| arc shot | 环绕 | 主体不动,机位绕一圈 |
| tracking shot | 跟拍 | 机位跟随主体移动 |
| dolly in / out | 推 / 拉(轨) | 摄影车推拉,空间感强 |

### §1.4 锁定 / 稳定类

| 英文 | 中文 | 典型场景 |
|------|------|----------|
| static shot | 固定机位 | 静帧感的稳定镜头 |
| locked-off | 锁机位 | 同 static,但更强调"无任何漂移" |
| locked tripod | 三脚架锁定 | 极端稳定,产品类 |

### §1.5 抖动 / 主观

| 英文 | 中文 | 典型场景 |
|------|------|----------|
| shake slightly | 微抖 | 纪实感 / 紧张 |
| shake strongly | 强抖 | 动作片 / 灾难 |
| handheld | 手持 | 纪录片感 |
| POV | 主观视角 | 第一人称 |

### §1.6 旋转

| 英文 | 中文 | 典型场景 |
|------|------|----------|
| roll clockwise | 顺时针旋转 | 失重 / 迷幻 |
| roll counterclockwise | 逆时针旋转 | 失重 / 迷幻 |

## §2 振幅(Amplitude)

| 取值 | 含义 | 适用 |
|------|------|------|
| `with small amplitude` | 振幅小 | 微动 / 静态场景的暗示 |
| (省略) | 振幅中等(默认) | 通用 |
| `with large amplitude` | 振幅大 | 强调 / 戏剧性 |

## §3 速度(Speed)

| 取值 | 含义 | 适用 |
|------|------|------|
| `at slow speed` | 慢速 | 庄严 / 沉思 |
| (省略) | 正常速度(默认) | 通用 |
| `at fast speed` | 快速 | 紧张 / 追逐 / 能量 |

## §4 三件套组合公式

```
The camera <类型> [with <振幅>] [at <速度>] toward / as / while <主体动作>.
```

### §4.1 6 种典型组合

```
1. 缓推近(电影感):
   "The camera pushes in with small amplitude at slow speed toward her face."

2. 快速摇移(动态):
   "The camera pans right with large amplitude at fast speed across the crowd."

3. 稳定机位(产品):
   "The camera holds a static shot. No camera movement."

4. 环绕(产品展示):
   "The camera arcs around the watch with small amplitude at slow speed."

5. 跟拍(运动):
   "The camera tracks the runner with small amplitude at normal speed."

6. 主观 + 抖动(紧张):
   "POV camera shake slightly as the character runs through the alley."
```

## §5 反例(MUST 避免)

| ❌ 反模式 | ✅ 正确写法 |
|----------|-----------|
| `[Push in] [Static shot]` | `The camera pushes in with small amplitude at slow speed, then holds a static shot.` |
| `slowly push in` | `pushes in at slow speed` |
| `static` (单形容词) | `holds a static shot` / `camera stays locked off` |
| 三件套堆叠 4 个运镜 | 每个 beat 一个主运镜,Sequence 多个 beat |
| 用方括号触发运镜 | 写进英文句子里 |

## §6 时序 + 镜头切换

```
切镜判断: 仅在「有新信息到来」时切 — 距离变化用运镜,场景变化用 cut。

[Shot 1] ...镜头缓推...
[Shot 2] At 00:05.000, the camera cuts to a close-up of ...
[Shot 3] At 00:09.500, the camera cuts to ...
```

## §7 来源

- [MiniMax H3 官方提示词指南](https://minimaxh3.studio/zh/guide/minimax-h3)
- [promptslove H3 自然语言运镜](https://promptslove.com/free-tools/minimax-video-prompt-generator/)
- [ComfyUI H3 教程](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)