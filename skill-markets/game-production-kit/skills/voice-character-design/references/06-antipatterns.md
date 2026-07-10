# 反模式（必读）

> 5 个最常见错误，每个配 1 个反例 + 1 个修复。

## 反模式 1：单维度描述

### ❌ 反例
```
年轻女性，温柔甜美
```
只有"年龄/性别 + 1 个形容词"。Qwen3-TTS 会随机返回 5 种"年轻女性"。

### ✅ 修复
30-60 词覆盖 5 个维度（年龄/音质/节奏/情绪/特质）。详见 [04-instruct-template.md](04-instruct-template.md)。

---

## 反模式 2：形容词堆砌

### ❌ 反例
```
声音清澈、纯净、空灵、温柔、可爱、甜美、优雅、婉转
```
没有声学特征，全是文学描写。模型不知道该选哪个。

### ✅ 修复
把每个形容词翻译成声学：
- "清澈" → bright, clear
- "空灵" → airy, head voice, ethereal
- "婉转" → pitch undulation, melodic

详见 [02-vocal-range.md](02-vocal-range.md)。

---

## 反模式 3：用错物理维度

### ❌ 反例
```
他的声音非常有磁性
```
"磁性" 是个比喻——形容中低频的胸腔共鸣，**应该写"deep baritone with rich overtones"**。

### ✅ 修复
所有"形容词"都要翻译成**物理可测的声学特征**：
- 磁性 = rich overtones
- 沉稳 = low + slow + flat
- 空灵 = airy + bright + reverb
- 沙哑 = husky, gravelly
- 温柔 = slow + breathy + mid-volume

---

## 反模式 4：忽略情绪维度

### ❌ 反例
```
年轻男声，标准普通话，清晰自然
```
没有情绪。模型返回"中性朗读"。

### ✅ 修复
必须包含**情绪基线 + 音调走势**：
- "introverted, gentle, with slight melancholy"
- "pitch rises on emotional phrases"
- "falling intonation, deliberate"
- "tone adapts to scene mood"

详见 [01-five-axes.md](01-five-axes.md)。

---

## 反模式 5：性别模糊

### ❌ 反例
```
a person, kind, gentle
```
"person" = 性别不明确。Qwen3-TTS 会随机选男/女。

### ✅ 修复
明确写：
- male / female / androgynous
- 或具体：masculine baritone / feminine alto

> 注：Qwen3-TTS 不支持中性性别（默认会偏向一种）。

---

## 反模式 6：中文 instruct

### ❌ 反例
```
年轻女性，温柔甜美，标准普通话。语速适中。
```
中文 instruct 在 Qwen3-TTS 里**效果差 30-50%**（训练数据以英文为主）。

### ✅ 修复
默认用 **英文**写 instruct：
```
A young Chinese female in her early 20s with a gentle mid-range voice. 
Tender and slightly melancholic, with soft, measured pacing. 
Speaks standard Mandarin with natural warmth. 
Pitch gently rises on emotional phrases.
```

详见 [04-instruct-template.md § 中文 vs 英文](04-instruct-template.md)。

---

## 反模式 7：单 seed 用到底

### ❌ 反例
```python
# 所有 voice 共享 seed
seed = 42
```
所有角色听起来一样（或随机漂移）。

### ✅ 修复
**每角色一 seed 跨场景复用**：
```python
CHAR_SEED = {
    "qiu_suwan": 10042,
    "lin_zhiyi": 10043,
    "cafe_boss": 10044,
    "narrator": 10045,
}
```

详见 [03-numeric-params.md § seed](03-numeric-params.md)。

---

## 反模式 8：写"pause" / "silence" 给模型

### ❌ 反例
```
A young female voice with long pauses between sentences.
```
模型会**过度执行**，变成大量静音。

### ✅ 修复
用节奏词：
- "deliberate pacing"（代替 long pauses）
- "measured"（代替 slow）
- "with reflective silence in mind"（隐含而非命令）

---

## 反模式 9：每角色全用同一 prompt 改温度

### ❌ 反例
```python
voices = {
    "qiu_suwan": "年轻女性，温柔甜美" + " (T=0.7)",
    "lin_zhiyi": "年轻女性，温柔甜美" + " (T=0.8)",  # 错误：男性用了女性 prompt
    "cafe_boss": "年轻女性，温柔甜美" + " (T=0.9)",
}
```
prompt 错 + 温度拉不开差异 → 3 个声音基本一样。

### ✅ 修复
每个角色**独立设计 5 维**，**温度只是微调**（0.65-0.85 范围）。

---

## 反模式 10：用 max_new_tokens=2048 解决静音问题

### ❌ 反例
```
max_new_tokens = 4096
```
模型会"想很久再说话"——静音更多。

### ✅ 修复
按文本长度设：
- 单句 < 20 字：`max_new_tokens = 200`
- 单句 20-40 字：`max_new_tokens = 280`
- 单句 40-80 字：`max_new_tokens = 380`

详见 [03-numeric-params.md § 静音问题](03-numeric-params.md)。

---

## 反模式 11：忽视 BGM 频段冲突

### ❌ 反例
紧张 BGM（低频 60-200Hz） + 老者角色（深胸声 80-150Hz）= **听不清对白**。

### ✅ 修复
按场景 BGM 调整角色出场，或在 BGM 高潮期切换角色。

详见 [05-coordination.md](05-coordination.md)。

---

## 速查：一份 voice config 的红线

| 检查项 | 阈值 |
|--------|------|
| instruct 词数 | 30-60 |
| 5 维覆盖 | 全部明确 |
| 数值参数 | 4 个全设置（temp/top_p/rep_penalty/max_new_tokens） |
| seed 锁定 | 跨场景同一 seed |
| 同剧区分 | 至少 3 维差异 |
| 与 BGM 协调 | 频段不冲突 |
| 中文 instruct | 禁止（除非有特殊原因） |
