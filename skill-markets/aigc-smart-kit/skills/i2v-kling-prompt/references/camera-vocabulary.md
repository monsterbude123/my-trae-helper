# Kling 3.0 — 镜头词表(中英对照)

> Kling 3.0 不接受方括号运镜语法。运镜必须写进句子里,使用自然英语。本文按"5 大基础动作"分类,列出中文 / 英文 / 适用场景。

## §0 黄金法则

```
❌ 反例(弱 prompt):
  "cinematic shot of a chef plating pasta"

✅ 正例(强 prompt):
  Subject: the chef in the prep kitchen (KEEP IDENTITY LOCKED)
  Movement: he plates the pasta with tongs
  Camera: slow push-in on his hands, shallow depth of field
  Background: warm kitchen light holds
```

> ⚠️ **Camera 与 Movement 必须分句** — 混写时 Kling 难以同时解析动作和镜头。

## §1 推 / 拉 类

| 术语(英文) | 中文 | 适用场景 | 提示 |
|------------|------|----------|------|
| `push-in` / `dolly in` | 推近 | 强调 / 聚焦 / 情绪收紧 | 慢速 push-in 最稳 |
| `slow dolly in` | 缓推近 | 情绪 / 抒情 | 配 BGM 适用 |
| `pull-out` / `dolly out` | 拉远 | 揭示环境 / 收束 | 商业广告常用 |
| `zoom in` | 变焦推近 | 快速聚焦 | 慎用,易出 zoom 感 |
| `zoom out` | 变焦拉远 | 快速揭示 | 同上 |

### §1.1 三件套组合

```
Camera: <类型> with <振幅> at <速度>

例:
  Camera: push-in with small amplitude at slow speed
  Camera: dolly in with large amplitude at normal speed
  Camera: pull-out with medium amplitude at slow speed
```

## §2 摇 / 移 类

| 术语(英文) | 中文 | 适用场景 |
|------------|------|----------|
| `pan left` / `pan right` | 左摇 / 右摇 | 横扫场景 / 跟随主体 |
| `handheld pan` | 手持摇 | 纪实 / 紧张 |
| `smooth pan` | 稳定摇 | 优雅 / 抒情 |
| `track left` / `track right` | 横移 | 平行跟随 |
| `tracking shot` | 跟拍 | 主体保持画幅中 |
| `follow shot` / `chase shot` | 追拍 | 主体运动方向 |

## §3 俯仰 / 升降 类

| 术语(英文) | 中文 | 适用场景 |
|------------|------|----------|
| `tilt up` | 上仰 | 仰望 / 揭示高度 |
| `tilt down` | 下俯 | 俯视 / 揭示低处 |
| `pedestal up` / `crane up` | 升 | 拉升 / 拉开 |
| `pedestal down` / `crane down` | 降 | 下降 / 闭合 |

## §4 环绕 / 弧线 类

| 术语(英文) | 中文 | 适用场景 |
|------------|------|----------|
| `orbit` | 环绕 | 主体居中,360° |
| `arc shot` | 弧线运镜 | 围绕主体做半弧 |
| `360° rotation` | 360° 旋转 | 产品展示 / 角色变身 |

> ⚠️ 360° 旋转 + 角色 → 必须三视图 + LOCKED(否则脸会糊)

## §5 静 止 类

| 术语(英文) | 中文 | 适用场景 |
|------------|------|----------|
| `static shot` | 静止 | 静物 / 风景 / 对话 |
| `locked-off` / `locked off` | 锁机位 | 产品 / 商业广告 |
| `no movement` | 无运镜 | 同上 |

> ⚠️ Kling 默认会微量漂移。要锁定机位,必须显式声明。

## §6 复合 / 高级类

| 术语(英文) | 中文 | 适用场景 |
|------------|------|----------|
| `crane shot` | 摇臂 | 电影感开场 / 收束 |
| `steadicam` | 斯坦尼康 | 流畅跟随 / 长镜头 |
| `handheld` | 手持 | 纪实 / 紧张 / 主观 |
| `whip pan` | 甩摇 | 转场 / 强调节奏 |
| `roll clockwise` / `roll counterclockwise` | 横滚 | 失衡感 / 风格化 |
| `POV shot` | 主观视角 | 第一人称代入 |

## §7 运镜 + 振幅 + 速度 速查

### §7.1 振幅对照

| 振幅 | 英文 | 视觉效果 |
|------|------|----------|
| 小 | `small amplitude` | 微调 / 微妙 |
| 中(默认) | `medium amplitude`(省略) | 标准 |
| 大 | `large amplitude` | 强烈 / 戏剧 |

### §7.2 速度对照

| 速度 | 英文 | 视觉效果 |
|------|------|----------|
| 慢 | `slow speed` | 抒情 / 强调 |
| 中(默认) | `normal speed`(省略) | 标准 |
| 快 | `fast speed` | 紧张 / 节奏 |

### §7.3 三件套组合示例

```
柔美开场:
  Camera: slow dolly in with small amplitude at slow speed

强调焦点:
  Camera: push-in with large amplitude at fast speed

商业广告:
  Camera: pull-out with small amplitude at slow speed

人物对白:
  Camera: static / locked off, medium shot

产品展示:
  Camera: slow orbit, 90 degrees in 10 seconds
```

## §8 反例(必避免)

| ❌ 反模式 | ✅ 正确做法 |
|----------|-----------|
| `[Push in]` 方括号语法 | `Camera: slow push-in` |
| `cinematic shot`(模糊词) | `Camera: dolly in with small amplitude at slow speed` |
| 1 秒内堆 3 个相反方向运镜 | 一个 5 秒片段 1 个主运镜 |
| Camera 与 Movement 写在一句 | 分句:`Movement: ...\n Camera: ...` |
| 锁定意图但写"locked camera"(弱) | 写 `Camera: locked off` / `static` / `no movement` |
| 运镜描述中混入动作描述 | Camera 句只写运镜 + 振幅 + 速度 |

## §9 来源

- [Kling 3.0 I2V 官方实战 — 第 2 节](https://kling3.app/blog/how-to-use-kling-3-0-image-to-video)
- [Kling AI I2V Quickstart](https://kling.ai/quickstart/image-to-video-guide)
- 蒸馏自主 SKILL.md §2.1 + §5.1 镜头三件套