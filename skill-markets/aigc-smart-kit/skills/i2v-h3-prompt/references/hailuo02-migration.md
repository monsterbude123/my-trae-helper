# Hailuo 02 → H3 迁移对照表

> 旧 Hailuo 02 prompt 写法迁移到 H3 的速查表。H3 弃用了大量 Hailuo 02 约定。

## §0 总览:关键差异

| 维度 | Hailuo 02 | MiniMax H3 |
|------|-----------|------------|
| 运镜语法 | 方括号触发:`[Push in] [Truck left]` | 自然语言句内:`pushes in with small amplitude at slow speed` |
| 提示词结构 | 单段 prompt | 三段式:description + soundscape + music |
| 多模态参考 | `first_frame_image` 单图 | image_mode: `first_last_frame` / `reference` 多模态 |
| 音频 | 需外挂 TTS | 原生立体声生成 |
| 长度上限 | 5 / 10s | 4-15s(整数) |
| 模型 API 标识 | `MiniMax-Hailuo-02` | `MiniMax-H3` |
| 文字渲染 | 易糊 | 显式 `rises verbatim` 更稳 |
| 振幅/速度控制 | 不支持 | 三件套(类型 + 振幅 + 速度) |

## §1 运镜迁移对照

### §1.1 方括号 → 自然语言

| Hailuo 02 | H3 写法 |
|-----------|---------|
| `[推进]` | `The camera pushes in` |
| `[拉远]` | `The camera pulls out` |
| `[左移]` | `The camera trucks left` |
| `[右移]` | `The camera trucks right` |
| `[推进, 拉远]` | `The camera pushes in, then pulls out` |
| `[左摇, 上升]` | `The camera pans left while pedestaling up` |
| `[固定]` | `The camera holds a static shot` |
| `[晃动]` | `The camera shakes slightly` |
| `[跟随]` | `The camera tracks the subject` |
| `[变焦推近]` | `The camera zooms in` |
| `[变焦拉远]` | `The camera zooms out` |

> ⚠️ Hailuo 02 模型(`MiniMax-Hailuo-02` / `-2.3` / `-2.3-Fast`)仍接受方括号;H3 **完全不再支持**。

### §1.2 振幅 / 速度迁移

Hailuo 02 没有振幅 / 速度概念,H3 引入后可微调:

| Hailuo 02(单一) | H3(振幅可选) | H3(速度可选) |
|------------------|--------------|--------------|
| `[推进]` | `pushes in with small amplitude` | `pushes in at slow speed` |
| `[推进]` | `pushes in with large amplitude` | `pushes in at fast speed` |
| `[推进]` | (省略 = 默认 medium) | (省略 = 默认 normal) |

## §2 提示词结构迁移

### §2.1 Hailuo 02 单段 prompt

```
A mouse runs toward the camera, smiling and blinking. [Push in]
```

### §2.2 H3 三段式 prompt

```python
integrated_multimodal_description: [Shot 1] A mouse runs toward the camera,
smiling and blinking. The camera pushes in with small amplitude at slow speed.

overall_soundscape: Soft footsteps on the floor, faint background music.

non_diegetic_music: A playful pizzicato melody at a moderate tempo.
```

## §3 API 参数迁移

### §3.1 Hailuo 02 / 2.3

```
POST /v1/video_generation
{
  "prompt": "...,
  "first_frame_image": "<url>",
  "model": "MiniMax-Hailuo-2.3",
  "duration": 6,
  "resolution": "1080P"
}
```

### §3.2 H3(异步任务)

```
POST /v1/video_generation (异步)
{
  "model": "MiniMax-H3",
  "prompt": "<integrated_multimodal_description 块>",
  "first_frame_image": "<url>",
  "duration": 5..15,
  "resolution": "768P" | "2K"
}
```

> ⚠️ H3 prompt 长度上限 **7000 字符**,相比 Hailuo 02 的 2000 字符放宽。

## §4 反例:不要混用

```
❌ 在 H3 prompt 里写:
   [Push in] [Static shot]
   → H3 完全忽略方括号,只会按"自然语言"理解

❌ 在 Hailuo 02 prompt 里写:
   integrated_multimodal_description: ...
   → Hailuo 02 不识别三段式结构

✅ 模型版本与语法严格匹配:
   - Hailuo 02/2.3 → 方括号运镜 + 单段 prompt
   - H3 → 自然语言三件套 + 三段式 prompt
```

## §5 模型选型速查

| 场景 | 推荐模型 |
|------|----------|
| 短片段(5-10s)+ 原生音频 | MiniMax-H3 |
| 高清 1080P 单图动效 | MiniMax-Hailuo-2.3 |
| 极致速度(批量) | MiniMax-Hailuo-2.3-Fast |
| 多模态参考复杂场景 | MiniMax-H3(参考素材上限更高) |
| 旧工作流不迁移 | MiniMax-Hailuo-02(仍可用) |

## §6 来源

- [Hailuo 图生视频 API(Hailuo 02 语法)](https://platform.minimaxi.com/document/image_to_video)
- [MiniMax H3 视频生成 API](https://platform.minimax.io/docs/guides/video-generation)
- [promptslove H3 generator(Hailuo 02 → H3 迁移)](https://promptslove.com/free-tools/minimax-video-prompt-generator/)