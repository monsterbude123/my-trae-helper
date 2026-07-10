# Step 4 — Instruct 写作模板

> **核心原则**：instruct 是"导演给演员的剧本提示"，**5 段式结构**最稳定。

## 5 段式结构

```
[1] 一句话角色设定（年龄/性别/核心气质）
[2] 音质描述（共鸣/音色温度/厚度）
[3] 节奏与停顿（语速/停顿位置）
[4] 情绪与音调走势
[5] 补充特质（个人习惯/弱点/感染力来源）
```

总长 **30-60 词**。少于 30 词随机性大；多于 60 词模型会"忘记"前段。

## 模板（直接填）

```markdown
A [age] [gender] in [era] with a [resonance] voice. [Quality adjectives in pairs]. 
[Rhythm description], with [pause pattern]. Speaks [language/dialect] with [emotional tone]. 
[Pitch direction] on [specific phrase type]. [Final character touch].
```

## 5 个不同角色范例

### 范例 1：少女初恋
```
A young Chinese female in her early 20s with a crystalline, gentle mid-range voice. 
Tender and slightly melancholic, with soft, measured pacing at a moderate tempo. 
Speaks standard Mandarin with natural warmth, and her pitch gently rises on emotional phrases. 
There's a fragile, intimate quality to her delivery, as if every word is precious.
```
- 5 段全覆盖
- 关键词：crystalline / measured / rises on emotional phrases / fragile

### 范例 2：老者看透一切
```
An elderly Chinese male in his late 60s with a deep, gravelly baritone voice. 
Calm, knowing, and measured, with slow, deliberate pacing. 
Speaks standard Mandarin with an unhurried, philosophical quality. 
Each sentence carries the weight of experience, with rich overtones and a slight roughness that hints at decades of smoking and wisdom.
```
- 5 段全覆盖
- 关键词：gravelly baritone / deliberate / unhurried / weight of experience

### 范例 3：执着的男主
```
A young Chinese male in his mid-20s with a clear, slightly husky tenor voice. 
Introverted yet quietly determined, with measured pacing and a gentle, conversational tone. 
Speaks standard Mandarin at a moderate speed, often pausing briefly before key words for emphasis. 
His delivery feels like an inner monologue — intimate and reflective, with subtle determination beneath the calm.
```
- 5 段全覆盖
- 关键词：husky tenor / pausing before key words / intimate and reflective

### 范例 4：反派紧张
```
A middle-aged Chinese male in his 40s with a cold, sharp baritone. 
Aggressive, calculating, with clipped, rapid delivery and no wasted breath. 
Speaks standard Mandarin with clipped consonants and rising intonation when cornered. 
His voice carries restrained menace, and there is a metallic edge that suggests barely concealed hostility.
```
- 5 段全覆盖
- 关键词：clipped rapid / rising when cornered / metallic edge

### 范例 5：旁白
```
A neutral Chinese male narrator in his 30s with a clear, professional voice. 
Calm, balanced, and atmospheric, with a moderate pace and subtle emotional coloring. 
Speaks standard Mandarin with the gravitas of a documentary narrator, neither too fast nor too slow. 
Tone adapts slightly to scene mood: mysterious for tense moments, warm for tender scenes.
```
- 5 段全覆盖
- 关键词：atmospheric / documentary narrator / adapts to scene

## 写作时的检查清单

```
□ 5 段都写到（年龄/音质/节奏/情绪/特质）
□ 30-60 词
□ 至少 2 个声学关键词（共鸣/音调/语速）
□ 至少 1 个情绪相关描述
□ 不要用"好听/漂亮/独特"等无意义形容词
□ 不要写 "pause" "silence" "slow down" 等指令——模型会过度执行
□ 用英文写 instruct（Qwen3-TTS 训练数据以英文为主，中文 instruct 效果差）
```

## 中文 vs 英文 instruct

| 维度 | 英文 instruct | 中文 instruct |
|------|--------------|--------------|
| Qwen3-TTS 训练覆盖 | ✅ 充分 | ⚠️ 弱 |
| 平均生成质量 | 8/10 | 6/10 |
| 词数容忍度 | 60+ | 30+ |
| 推荐 | **默认用英文** | 仅在英文无法表达的中文声学特征 |

> 反例：有人用中文写"声音里要带点沙哑的磁性"，模型经常返回"普通男声"。
> 正解：用英文"voice with slight huskiness and rich overtones"。

## 高级技巧：同一角色多情绪版本

不要试图一条 prompt 表达所有情绪——而是创建**多个 instruct 变体**：

```python
VOICES = {
    "qiu_suwan_calm": "A young ... measured pacing ... naturally warm.",
    "qiu_suwan_panic": "A young ... rapid breathless delivery ... pitch wavering.",
    "qiu_suwan_hopeful": "A young ... bright hopeful quality ... pitch rising on positive phrases.",
}
```

剧情脚本里根据场景情绪选择：

```python
if scene.emotion == "calm": voice = "qiu_suwan_calm"
if scene.emotion == "panic": voice = "qiu_suwan_panic"
```

## 高级技巧：跨语言 instruct

如果游戏要支持日文/英文，要为每种语言各写一条：

```
# 中文 instruct（用英文写）
"A young Chinese female ... Speaks standard Mandarin with natural warmth."

# 日文 instruct
"A young Japanese female ... Speaks standard Tokyo Japanese with soft politeness."
```

注意**语调习惯不同**——中文温柔 = 中等音调起伏，日文温柔 = 句尾下沉。
