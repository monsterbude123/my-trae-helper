# 声音设计三层(Video Prompting · Audio Design)

> **定位**:`video-prompt-method/SKILL.md §8` 声音设计的细则。
> **不重复**:SKILL.md §8 的三层映射表;本文给节拍卡点 + 情绪节奏 + 平台特化字段名指针。

## §0 何时加载

```
MUST 加载: 主 Agent 处理音频 / BGM / 对白 / 音效 / 节奏 / 卡点
MUST NOT: 纯视觉描述,无音频需求
```

## §1 三层映射(重申)

```
BGM 氛围       →  non_diegetic_music     (剧情外音乐)
音效节拍       →  overall_soundscape     (动作触发 + 环境)
情绪节奏 / 对白  →  description 内的对白 / SFX 触发
```

## §2 各层职责详解

### §2.1 non_diegetic_music(剧情外音乐 / BGM)

```
职责:
  - 整体情绪锚(epic / romantic / tense / playful)
  - 节奏骨架(快 / 中 / 慢 + 节拍)
  - 起始 / 结束 / 渐变(淡入淡出 / 静音 / 突止)

写法:
  - 乐器 + 风格 + 节奏 + 特殊处理
  - 例:"A soft 1920s-style piano pattern at moderate tempo,
         joined by a single muted trumpet at the spin's peak,
         with a gentle fade on the final frame."

留空策略:
  - 不需要音乐的场景(纪实 / 静音 / 紧张对峙) → 留空
  - "留空" 比 "填一首糟糕的 BGM" 更好
```

### §2.2 overall_soundscape(整体音景)

```
职责:
  - 环境音(街道 / 森林 / 室内 / 海滩)
  - 动作触发的音效(脚步 / 门铃 / 切菜 / 雨声)
  - 节奏标记(对白 / 关键 SFX)
  - 静音场景的底噪(空调嗡鸣 / 远处脚步)

写法:
  - 环境 + 触发动作 + 节奏关键词
  - 例:"Wooden shutters scrape open over a quiet street as trays
         clink softly inside the bakery. The doorbell rings once,
         followed by light footsteps and the crisp sound of bread
         being sliced."
```

### §2.3 description 内的音频触发

```
职责:
  - 对白(S1 says: "...")
  - 关键 SFX(动作触发的具体音效)
  - 与视觉动作同步的音频事件

写法:
  - 与主体动作同句处理,不单独列
  - 例:"The camera pushes in as she places a fresh loaf on the
         counter and says: 'First batch of the morning.'"

标签:
  - [S1] 对白
  - [FX] 单独音效
  - [SFX] 触发音效
```

## §3 中文需求 → 英文音频字段转写

### §3.1 完整示例

```
"配轻快的钢琴曲,在主角走入走廊时铃响一下"
  ↓
non_diegetic_music: A light piano pattern at a moderate tempo with gentle fade.
overall_soundscape: A small bell rings once as she enters the hallway, with
  soft ambient indoor air conditioning hum and distant footsteps.

动作触发 SFX MUST 在 description 写:
  [S1] "The bell rings once"   ← 与对白同句处理
  [FX] "a crisp slice sound"   ← 单独音效标签
```

### §3.2 常见中文音频词 → 英文映射

| 中文 | 英文 |
|------|------|
| 配轻快的钢琴曲 | `A light piano pattern at moderate tempo` |
| 紧张的低音 | `Deep sustained bass with low rumble` |
| 温暖的弦乐 | `Warm string ensemble, legato` |
| 寂静 | `Silence with faint ambient hum` |
| 突然静音 | `Sudden cut to silence` |
| 渐强 | `Gradual crescendo` |
| 渐弱 | `Gentle fade out` |
| 突然停止 | `Abrupt stop on final frame` |
| 铃响 | `Bell rings once` |
| 脚步声 | `Light footsteps on marble` |
| 风声 | `Wind howls softly` |
| 雨声 | `Steady rainfall, distant thunder` |

## §4 节拍卡点

### §4.1 音频节奏 = 视频呼吸

```
慢节奏 + 长镜头 / 推镜头
  → BGM 缓,description 内动作少,soundscape 环境音为主

快节奏 + 切镜 / 主体运动
  → BGM 节奏快,description 内动作密集,soundscape SFX 多

静默 + 单音 = 紧张 / 期待
  → non_diegetic_music 留空或单音,soundscape 极简

BGM 留白 = 模型自由发挥(慎用)
  → 仅在 description 内有明确 SFX 节奏时考虑
```

### §4.2 卡点技巧

```
1. BGM 节拍与切镜时间戳对齐
   - 切镜发生在 BGM 重拍上 = 视觉节奏感强
   - 切镜发生在 BGM 弱拍上 = 视觉节奏感弱(适合过渡)

2. 主动作结束 = 音频事件触发
   - 主角放下茶杯 → description:"sets down the cup" + soundscape:"ceramic clink on saucer"

3. 收束 = 音频渐弱
   - 动作完成 → music:"gentle fade on final frame" / soundscape:"silence"
```

## §5 情绪节奏

### §5.1 情绪曲线设计

```
完整视频情绪曲线:
  [00:00] 平静(establish)
  [00:02] 紧张升温(rising action)
  [00:05] 高潮(climax)
  [00:08] 释放 / 收束(resolution)

音频配合:
  平静:  BGM 留空 / 单音,soundscape 环境音轻
  紧张:  BGM 低频持续,soundscape 动作 SFX 渐多
  高潮:  BGM 强拍,soundscape SFX 密集
  释放:  BGM 渐弱,soundscape 单音 → 静音
```

### §5.2 情绪关键词(供 BGM 风格选择)

| 情绪族 | BGM 风格 |
|--------|----------|
| **平静 / contemplative** | ambient / soft piano / drone |
| **温暖 / warm** | acoustic guitar / strings |
| **紧张 / tense** | sustained bass / minor key / heartbeat |
| **欢快 / playful** | upbeat piano / pizzicato strings |
| **忧伤 / melancholic** | cello solo / slow strings |
| **史诗 / epic** | full orchestra / brass / timpani |
| **神秘 / mysterious** | synth pad / reversed sounds |
| **浪漫 / romantic** | soft strings / French horn |

## §6 平台特化字段名(指针到儿子 skill)

```
H3 / Hailuo:    integrated_multimodal_description + overall_soundscape + non_diegetic_music
Seedance 2.5:  description + (音效字段视版本而定)
可灵 3.0:      description + element reference(可带音频元素)
Vidu:          description + audio(若有)
万相:          description + audio(若有)

完整细则 → 儿子 skill 的 references/audio-layers.md
  - H3:   i2v-h3-prompt/references/audio-layers.md
  - 各平台:待创建
```

## §7 反例速查

| ❌ 反模式 | ✅ 正确做法 |
|---------|----------|
| BGM 风格与情绪不匹配(紧张场景配欢快 BGM) | 情绪族对应(§5.2 表) |
| 三层顺序错(description → music → soundscape) | 必须 description → soundscape → music |
| 没有 soundscape(只写 BGM) | 必有环境音 + 动作触发 SFX |
| 没有对白标签(S1 没标) | 加 `S1 says: "..."` |
| BGM 永远不渐变(突然开始突然结束) | 起始淡入 / 结束渐弱 |
| 音画不同步(主动作结束没 SFX) | 主动作 = 音频事件触发 |
| 写 BGM 但情绪族空泛("唯美 BGM") | 具体乐器 + 风格 + 节奏 |

## §8 来源

- 蒸馏自 `i2v-h3-prompt/references/chinese-prompt-method.md §8`
- 用户实战笔记:`docs/references/note-video-prompt/` §8
- 创建日期:2026-08-20
