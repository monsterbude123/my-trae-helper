# H3 三层音频分离细则

> H3 原生立体声(32 kHz / 24fps),音频与视频同 pass 生成。三层音频是控制混音不乱的关键。

## §0 三层定义

| 层 | 写入字段 | 含义 | 触发词 |
|----|---------|------|--------|
| **diegetic**(剧情内) | `integrated_multimodal_description` + `overall_soundscape` | 画面内可见源 | "says", "footsteps", "cup placed" |
| **ambient**(环境音) | `overall_soundscape` | 场景氛围 | "wind", "crowd murmur", "rain" |
| **score**(配乐) | `non_diegetic_music` | 剧情外音乐 | "acoustic guitar", "full orchestra" |

## §1 overall_soundscape 写法

```
overall_soundscape = 动作触发的具体声音 + 持续的环境音 + 节奏变化点
```

### §1.1 示例

```
Wooden shutters scrape open over a quiet street as trays clink softly inside
the bakery. The doorbell rings once, followed by light footsteps and the
crisp sound of bread being sliced.
```

要点:
- **动作触发**:"shutters scrape open" / "doorbell rings" — 与视觉同步
- **持续背景**:"quiet street" / "soft inside" — 营造氛围
- **节奏**:"once, followed by" — 控制时序

### §1.2 反例

```
❌ "The bakery is loud."
   → 太抽象,模型没法生成具体声音

❌ "Music plays in the background."
   → 错层(应放 non_diegetic_music)

✅ "Wooden shutters scrape open, trays clink softly, the doorbell rings once."
   → 具体的、可触发的声音
```

## §2 non_diegetic_music 写法

```
non_diegetic_music = 风格 + 情绪/节奏 + 起止
```

### §2.1 示例

```
A soft acoustic-guitar pattern at a moderate tempo, joined by sparse
upright-bass notes and a gentle fade at the end.
```

要点:
- **风格具体**:乐器 / 流派 / 节奏词
- **情绪 / 节奏**:moderate tempo / sparse / gentle
- **起止**:gentle fade / build to crescendo / sudden stop

### §2.2 留空写法

```
如果不要 BGM:
non_diegetic_music: (留空 / 不写)
```

不要写 "no music" — H3 留空默认即无音乐。

## §3 对白 / 旁白

```
S1 says: "First batch of the morning."   ← 在 integrated_multimodal_description 写
```

### §3.1 多角色

```
S1 (主角色): "First batch of the morning."
S2 (顾客): "Two croissants, please."
```

### §3.2 多语言

H3 支持 11 种语言口型同步。写明语言:

```
S1 says in French: "Bonjour, comment allez-vous?"
```

## §4 文字渲染(屏幕文字 / 海报 / 标语)

```
"renders verbatim: 'OPEN 24H'"    ← 海报 / 招牌
"subtitle: 'Welcome back'"        ← 字幕
```

文字与图像结合时,必须显式标注 verbatim,否则 H3 自由发挥会糊。

## §5 反例

| ❌ 反模式 | ✅ 正确写法 |
|----------|-----------|
| 三层混合写在 soundscape | 拆三段,各管各的 |
| "music plays" | 写乐器 + 风格 + 起止 |
| SFX 不写动作 | 写动作触发的具体声音 |
| 没标注对白语言 | 显式标注"in English" / "in French" |
| 字幕没 verbatim | 显式 verbatim |

## §6 来源

- [MiniMax H3 官方提示词指南 §1.1](https://minimaxh3.studio/zh/guide/minimax-h3)
- [promptslove H3 三段式示例](https://promptslove.com/free-tools/minimax-video-prompt-generator/)