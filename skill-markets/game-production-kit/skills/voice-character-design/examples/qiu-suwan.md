# 例 1：邱苏晚的完整音色设计

> 真实项目：「时空里等你」(webgal_case02)

## 角色卡

| 字段 | 值 |
|------|---|
| 角色 ID | qiu_suwan |
| 中文名 | 邱苏晚 |
| 性别 | 女 |
| 年龄 | 23 |
| 身份 | 画家 / 美院研究生 |

## 推导过程

### 1. 拿到原始人设
```
Want: 想被看见
Fear: 怕自己不值得被记住
性格: 温柔、安静、内心有定见、笑着等三小时雨的人
外形: 过肩黑长直，纤细，米白色连衣裙
```

### 2. 转 5 维声学
| 维度 | 推断 |
|------|------|
| 年龄 | early 20s（声带成熟未衰） |
| 性别 | female（无需强调和气质） |
| 共鸣 | head + slight chest（温柔但有内核） |
| 语速 | 慢 + 停顿多（沉静的人不会抢着说话） |
| 音调 | 句尾略上扬（脆弱感 + 期待感） |

### 3. 数值参数
```yaml
temperature: 0.75
top_p: 0.85
repetition_penalty: 1.05
max_new_tokens: 280
seed: 10042
```

### 4. Instruct
```
A young Chinese female in her early 20s with a crystalline, gentle mid-range voice. 
Tender and slightly melancholic, with soft, measured pacing at a moderate tempo. 
Speaks standard Mandarin with natural warmth, and her pitch gently rises on emotional phrases. 
There's a fragile, intimate quality to her delivery, as if every word is precious.
```

**51 词 ✅**

## 5 段分析

| 段 | 文本 | 包含的声学特征 |
|----|------|---------------|
| [1] 角色设定 | "A young Chinese female in her early 20s with a crystalline, gentle mid-range voice." | 年龄、性别、音质（crystalline 透明感，mid-range 中音域） |
| [2] 音质 | "Tender and slightly melancholic, with soft, measured pacing at a moderate tempo." | 情绪（tender + melancholy）、节奏（measured 中速） |
| [3] 语言 + 音调 | "Speaks standard Mandarin with natural warmth, and her pitch gently rises on emotional phrases." | 语言、音调走势 |
| [4] 特质 | "There's a fragile, intimate quality to her delivery, as if every word is precious." | 整体气质（fragile + intimate） |

## 为什么不写"温柔甜美"

如果写：
```
年轻女性，温柔甜美，标准普通话
```
模型会输出**典型的"客服女声"**——温柔甜美是中位值，没有特征。

加 "crystalline"（透明感）和 "fragile"（脆弱）后，模型会被推到**有质感的少女声**。

## 与 BGM 协调

- **s_cafe**（咖啡馆 BGM）= 完美：jazz + cafe 三重奏的中高频段正好给她让位
- **s_unease**（不安 BGM）= ⚠️ 略有冲突：低频 drone 80-200Hz 接近她的头声基频——对白时 BGM 降 30% 音量
- **s_true**（真结局 BGM）= 完美：acoustic guitar + 钢琴中频段与她的 mid-range 共存

## 同剧对比

| 角色 | 5 维特征 | 区分度 |
|------|---------|--------|
| 邱苏晚 | early 20s, female, head+chest, slow, gentle rise | 基准 |
| 林之一 | early 20s, male, mid, slow, flat | 3 维差异 ✅ |
| 咖啡馆老板 | late 60s, male, deep chest, slow, falling | 4 维差异 ✅ |
| 旁白 | 30s, male, mid, moderate, flat | 3 维差异 ✅ |

## 实测效果

- 单条听感：⭐⭐⭐⭐ "听得出温柔忧郁少女"
- 跨场景稳定：✅ seed 锁定
- 静音占比：~5%（可接受）
- 与 BGM 共存：✅（已做 s_unease 协调）

## 不好的版本（vs 好的版本）

### ❌ 初版（参考 sub-agent 自动生成）
```
年轻女性，温柔甜美，标准普通话。语速适中，声音清晰自然。略带一丝忧郁。
```

→ 19 词。**维度不完整**（没有共鸣位置、没有音调走势）。生成后听感普通，5 个模型会出 5 种声音。

### ✅ 修正后
```
A young Chinese female in her early 20s with a crystalline, gentle mid-range voice. 
Tender and slightly melancholic, with soft, measured pacing at a moderate tempo. 
Speaks standard Mandarin with natural warmth, and her pitch gently rises on emotional phrases. 
There's a fragile, intimate quality to her delivery, as if every word is precious.
```

→ 51 词。5 维全覆盖。生成后**听感稳定**（同样的 seed 会重复同一个声音）。

## 修复后项目表现

| 维度 | 初版 | 修正版 |
|------|------|--------|
| 听感 | 客服女声 | 温柔忧郁少女 |
| 与其他角色区分 | 与旁白撞 | 区分明显 |
| 静音占比 | 15-20% | 5% |
| 跨场景一致 | 漂移 | 锁定 |
