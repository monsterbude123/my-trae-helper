# Step 1 — 提取五维声学特征

> **核心原则**：先把角色的"声音画像"用 5 个轴表达清楚，再翻译成 TTS prompt。

## 五维声学特征

| 维度 | 问自己 | 决定了什么 | 错误示例 | 正确示例 |
|------|--------|----------|---------|---------|
| **年龄** | 声带成熟度 | 基频 F0 范围 | "年轻人" | "early 20s" / "late 60s" / "pre-teen" |
| **性别/性别气质** | 声带长度/厚度 | F0 + 谐波 | "女性" | "soft androgynous" / "masculine baritone" / "tomboyish alto" |
| **共鸣位置** | 胸/咽/头/鼻 | 音色"温度" | "声音好听" | "warm chest resonance" / "head-voice thin" / "nasal twang" |
| **语速/节奏** | 字符/秒 | 节奏感 + 句间停顿 | "语速适中" | "deliberately slow, 3.5 chars/sec, with reflective pauses" |
| **音调走势** | 平/升/降/起伏 | 情绪表达 | "有感情" | "pitch rises on emotional phrases" / "monotone, flat" |

## 推导流程

```
角色 Want/Fear → 性格 → 情绪基调 → 节奏 + 音调
角色年龄/性别/外形 → 声带物理 → 音域 + 共鸣
```

### 例：邱苏晚

```
Want: 想被看见
Fear: 怕自己不值得被记住
性格: 温柔、安静、内心有定见、笑着等三小时雨的人
外形: 过肩黑长直，纤细，米白色连衣裙
年龄: 23
```

推导：
- **年龄**: early 20s（声带已成熟但未衰）
- **性别气质**: female（无需强调和气质，自然即可）
- **共鸣位置**: head + slight chest（温柔但有内核——不是完全飘的纯头声）
- **语速/节奏**: 慢+停顿多（沉静的人不会抢着说话）
- **音调走势**: 句尾略上扬（脆弱感 + 期待感），但不像"撒娇"那样大幅上扬

→ 落到英文 prompt：

```
A young Chinese female in her early 20s with a crystalline, gentle mid-range voice.
Tender and slightly melancholic, with soft, measured pacing at a moderate tempo.
Speaks standard Mandarin with natural warmth, and her pitch gently rises on emotional phrases.
There's a fragile, intimate quality to her delivery, as if every word is precious.
```

> 30-60 词。5 个维度全覆盖。**没有任何"好听/漂亮"等无意义形容词**。

## 反例：5 个常见错误

### ❌ 错误 1：太短
```
年轻女性，温柔甜美，标准普通话
```
→ 8 个词。Qwen3-TTS 会随机返回一种"年轻女性"。

### ❌ 错误 2：形容词堆砌
```
声音清澈、纯净、空灵、温柔、可爱、甜美、优雅……
```
→ 没有声学特征，全是文学描写。

### ❌ 错误 3：用错维度
```
他的声音非常有磁性
```
→ "磁性" 形容的是中低频的胸腔共鸣，**应该写"deep chest resonance, low overtones"**。

### ❌ 错误 4：忽略情绪
```
年轻男声，标准普通话，清晰自然
```
→ 没有情绪维度，生成的声音是"中性朗读"。

### ❌ 错误 5：性别模糊
```
a person, kind, gentle
```
→ Qwen3-TTS 会随机选男/女。

## 模板：5 维特征速查表

| 维度 | 关键词库（英文） |
|------|------------------|
| 年龄 | in their early/late 20s/30s/60s, pre-teen, adolescent, middle-aged, elderly |
| 性别 | male, female, androgynous, tomboyish alto, feminine tenor, deep contralto |
| 共鸣 | chest resonance, head voice, nasal twang, bright, dark, warm, bright thin, hollow |
| 语速 | deliberate, measured, rapid, slow, hesitant, flowing, staccato, legato |
| 音调 | pitch rises on questions, falling intonation, monotone, expressive swings, gentle undulation |

## 进阶：从 Want/Fear 推到声音

| 性格特征 | 声学表现 |
|----------|---------|
| 内向、想被看见但不敢说 | 慢节奏 + 句尾轻微上扬 + 中等音量 |
| 执拗、控制欲强 | 节奏稳定 + 音调低 + 不轻易起伏 |
| 绝望但仍有希望 | 沙哑 + 偶尔迸发高亮 + 慢 |
| 老年人、看透一切 | 慢 + 厚重胸声 + 频繁停顿 |
| 少女、初恋 | 轻 + 头声 + 节奏快 + 音调起伏大 |
