# Step 2 — 声带物理与音域

> **核心原则**：不要凭感觉写"高音/中音/低音"——参考声带物理，给出**具体音高或描述**。

## 音高基频 F0 速查表

> F0 = 声带振动频率，单位 Hz，决定声音"高/低"

| 年龄/性别 | F0 范围 (Hz) | 形容 |
|----------|-------------|------|
| 男童 (5-12) | 250-400 | very high, childlike |
| 女青年 (18-30) | 180-260 | bright, soprano-alto |
| 男青年 (18-30) | 100-160 | tenor, mid-range |
| 中年男 (40-55) | 90-130 | dropping, thicker |
| 老年男 (65+) | 80-110 | gravelly, weak |
| 老年女 (65+) | 150-200 | dropping, breathy |

## Qwen3-TTS 实际输出范围（社区实测）

| 描述 | 模型倾向输出 F0 范围 |
|------|---------------------|
| "soprano" / "high-pitched" | 220-280 Hz |
| "alto" / "mid-range" | 180-220 Hz |
| "tenor" / "natural male" | 120-160 Hz |
| "baritone" / "deep male" | 90-130 Hz |
| "bass" / "very deep" | 70-100 Hz |

> ⚠️ 模型倾向但**不保证**。同一 prompt 多次生成会有 ±15 Hz 漂移——这是为什么需要**单角色锁定 seed**。

## 共鸣位置速查表

| 描述 | 物理位置 | TTS prompt 关键词 |
|------|---------|------------------|
| 头声 | 头/鼻腔 | "head voice", "thin", "bright" |
| 咽声 | 咽部 | "throaty", "constrained" |
| 胸声 | 胸腔 | "chest resonance", "full", "warm" |
| 鼻音 | 鼻腔 | "nasal twang", "pinched" |
| 混合 | 胸+头 | "balanced", "well-rounded" |

## 声音"温度" 速查

| 听起来 | 物理特征 | 关键词 |
|--------|---------|--------|
| 暖 | 低频丰富（< 200Hz） | "warm", "rich", "rounded" |
| 冷 | 高频突出 | "cold", "thin", "metallic" |
| 厚 | 谐波多 | "thick", "dense", "weighty" |
| 薄 | 谐波少 | "thin", "reedy", "light" |
| 暗 | 高频衰减 | "dark", "muffled", "shadowed" |
| 亮 | 高频突出 | "bright", "clear", "brilliant" |

## 为什么这一节重要

**"温柔"和"甜美"是完全不同的声学特征**：
- "温柔"= 慢节奏 + 中等音量 + 气息声多
- "甜美"= 高音 + 起伏大 + 头声多 + 节奏快

把"温柔甜美"写给 TTS，模型会取**所有维度的"中位数"**，得到"普通女声"。

## 落地：把"温柔"翻译成 prompt

| 角色场景 | 写"温柔"的方式 |
|---------|---------------|
| 老者关怀 | "warm chest resonance, slow measured pacing, breathy quality" |
| 少女初恋 | "bright head voice, gentle pacing, soft whispery quality" |
| 中年女性 | "mid-range with warm overtones, deliberate pacing, natural breathiness" |

## 落地：把"低沉"翻译成 prompt

| 角色场景 | 写"低沉"的方式 |
|---------|---------------|
| 年轻男主 | "clear tenor with slight huskiness, mid-low range" |
| 老者 | "deep baritone, gravelly, slow, rich overtones" |
| 旁白 | "professional mid-low male voice, clear but weighty" |

## 反例：用错物理维度

```
❌ "他的声音很低很磁"
   → "很低" = 音高低
   → "很磁" = 谐波丰富
   → 正确: "deep baritone with rich overtones"
```

```
❌ "她的声音很空灵很飘"
   → "空灵" = 高频 + 混响
   → "飘" = 不稳定
   → 正确: "bright ethereal voice with airy breathiness"
```

## 物理 vs 文学

| 文学描述（不要用） | 物理描述（要用） |
|------------------|-----------------|
| 温柔 | slow pacing + breathy + mid-volume |
| 甜美 | bright + head voice + pitch rises |
| 磁性 | rich overtones + chest resonance |
| 空灵 | airy + bright + reverb-y |
| 沉稳 | low + slow + flat intonation |
| 执着 | deliberate + consistent pace + emphasis on key words |
