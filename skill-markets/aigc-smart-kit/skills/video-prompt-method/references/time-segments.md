# 时间切片法(Video Prompting · Time Segments)

> **定位**:`video-prompt-method/SKILL.md §2` 时间截法的细则。
> **不重复**:SKILL.md §2 的时段切分原则;本文给反例库 + 跨平台时段长度对照 + 多镜头切镜时序。

## §0 何时加载

```
MUST 加载: 主 Agent 处理 5s+ 视频,需要规划时段 / 写多镜头切镜 prompt / 调时段长度
MUST NOT: 单镜头短 prompt,不需要切镜 — 直接写一句话即可
```

## §1 必填元素(每时段独立写完)

```
每时段 MUST 独立含:
  1. 主体(谁)
  2. 动作(做什么)
  3. 场景(在哪)
  4. 镜头(怎么拍)
  5. STYLE 锚

不跨段共享 — 不允许"前段写了主体后段省略"
```

### §1.1 反例

```
❌ "[00:00-00:03] 一片森林,主角走入。
   [00:03-00:06] 她停下脚步,镜头推近。"
   → 后段没复述主体 / 场景 / STYLE

✅ "[00:00-00:03] 中景, 20 岁东方少女走入古老红杉林,
                苔藓覆盖地面, 镜头缓推, 1920s Art Deco。
   [00:03-00:06] 同 Art Deco 风格, 中近景, 少女 A 停下脚步,
                镜头 push in, 阳光透过树冠形成光柱。"
   → 每段独立含 5 要素
```

## §2 时段长度对照(跨平台)

| 总时长 | 段数 | 时段切法 | 适用场景 |
|--------|------|----------|----------|
| **5s**  | 3 段 | `[0-1] / [1-3] / [3-5]` | 短视频 / 头像动效 |
| **6s**  | 3 段 | `[0-2] / [2-4] / [4-6]` | 标准短视频 |
| **8s**  | 3 段 | `[0-2] / [2-5] / [5-8]` | H3 默认时长 |
| **10s** | 4-5 段 | `[0-2] / [2-4] / [4-7] / [7-10]` | Seedance 标准 |
| **15s** | 5 段 | `[0-3] / [3-6] / [6-9] / [9-12] / [12-15]` | 长镜头 / 多事件 |
| **30s** | 6-8 段 | 每段 3-5s | Seedance 四拍 / 广告片 |

> **注意**:不同平台时长上限不同(H3 ≤ 10s,Seedance 2.5 可 30s,Kling 3.0 可 10s)。
> 时段切分必须先确认平台时长上限。

## §3 切镜时序(Multi-Shot,跨平台通用)

```
[Shot N] At 00:NN.NNN, the camera cuts to ...

要点:
  - 一个 Shot 一句独立描述(主体 / 动作 / 镜头独立完整)
  - 时间戳用 5 位小数 `00:05.000` 而非整数
  - 切镜的判断标准:有新信息到来才切 — 仅距离变化时移动相机而非切镜
```

### §3.1 何时切镜

```
✅ 切:
  - 主体切换(从主角 → 配角 / 反派)
  - 视角切换(室内 → 室外 / 远景 → 近景)
  - 时序跳跃(白天 → 夜晚)
  - 事件转换(对话 → 动作 / 静态 → 动态)

❌ 不切(用相机运动):
  - 距离变化(wide → close-up,直接 dolly in)
  - 视角微调(eye-level → slight low-angle,直接 tilt)
  - 同一主体同场景的持续观察
```

### §3.2 切镜时序示例(H3)

```
[Shot 1] Live-action, cinematic, a medium close-up frames a barista (S1)
opening the shutters of a small street bakery before sunrise. The camera
pushes in with small amplitude at slow speed as she places a fresh loaf
on the counter and says: "First batch of the morning."

[Shot 2] At 00:05.000, the camera cuts to a close-up of steam rising
from the sliced bread.
```

## §4 反例速查

| ❌ 反模式 | ✅ 正确做法 |
|---------|----------|
| 一段连写 6s 全部内容 | 按 `[HH:MM-HH:MM]` 三段切片 |
| 时段长短不一(1s / 3s / 1s) | 均衡切分(每段 2-3s) |
| 切镜无时间戳 | `[Shot N] At 00:NN.NNN, ...` |
| 跨段省略主体 / 场景 / STYLE | 每段首句复述身份 + 场景 + STYLE |
| 按"画面数量"切 | 按"前因后果"切(登场 → 展开 → 收束) |
| 按"音乐节拍"切 | 按"事件"切(音画同步交给声音层) |

## §5 来源

- 蒸馏自 `i2v-h3-prompt/references/chinese-prompt-method.md §1, §3.1, §10`
- 跨平台验证:H3 / Seedance 2.5 / 可灵 3.0
- 用户实战笔记:`docs/references/note-video-prompt/`(17 张 jpg,2026-08)
