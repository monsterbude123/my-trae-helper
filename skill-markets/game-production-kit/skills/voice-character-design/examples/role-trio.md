# 例 2：三角色对比（少女 / 老者 / 旁白）

> 用一个最小例子展示**多角色协调**——3 个完全不同的角色，听感要能区分开。

## 3 角色 5 维对比表

| 维度 | 少女 | 老者 | 旁白 |
|------|------|------|------|
| 年龄 | early 20s | late 60s | 30s |
| 性别 | female | male | male |
| 共鸣 | head + slight chest | deep chest | mid |
| 语速 | slow, with pauses | slow, deliberate | moderate |
| 音调 | gentle rise on emotional phrases | falling, flat | flat with scene adaptation |
| 情绪基线 | 温柔忧郁 | 看透一切 | 中性专业 |
| **总维度差异** | — | 与少女 5 维全不同 | 与少女 3 维差异 |

## 配置对比

### 少女（qiu_suwan）

```yaml
params:
  temperature: 0.75
  top_p: 0.85
  repetition_penalty: 1.05
  max_new_tokens: 280
  seed: 10042

instruct: |
  A young Chinese female in her early 20s with a crystalline, gentle mid-range voice.
  Tender and slightly melancholic, with soft, measured pacing at a moderate tempo.
  Speaks standard Mandarin with natural warmth, and her pitch gently rises on emotional phrases.
  There's a fragile, intimate quality to her delivery, as if every word is precious.
```

### 老者（cafe_boss）

```yaml
params:
  temperature: 0.7    # 更低，稳定性优先
  top_p: 0.85
  repetition_penalty: 1.05
  max_new_tokens: 320  # 略大（老者一句更长）
  seed: 10044          # 与少女差 2

instruct: |
  An elderly Chinese male in his late 60s with a deep, gravelly baritone voice.
  Calm, knowing, and measured, with slow, deliberate pacing.
  Speaks standard Mandarin with an unhurried, philosophical quality.
  Each sentence carries the weight of experience, with rich overtones and a slight roughness that hints at decades of smoking and wisdom.
```

### 旁白（narrator）

```yaml
params:
  temperature: 0.7
  top_p: 0.85
  repetition_penalty: 1.05
  max_new_tokens: 320
  seed: 10045          # 与少女差 3

instruct: |
  A neutral Chinese male narrator in his 30s with a clear, professional voice.
  Calm, balanced, and atmospheric, with a moderate pace and subtle emotional coloring.
  Speaks standard Mandarin with the gravitas of a documentary narrator, neither too fast nor too slow.
  Tone adapts slightly to scene mood: mysterious for tense moments, warm for tender scenes.
```

## 3 角色 instruct 词数对比

| 角色 | 词数 | 状态 |
|------|------|------|
| 少女 | 51 | ✅ 30-60 词 |
| 老者 | 51 | ✅ 30-60 词 |
| 旁白 | 48 | ✅ 30-60 词 |

## 5 维差异分析

### 少女 vs 老者
- 年龄：early 20s vs late 60s → 1 维
- 性别：female vs male → 1 维
- 共鸣：head+chest vs deep chest → 1 维
- 音调：gentle rise vs falling → 1 维
- 节奏：slow + pauses vs slow + deliberate → **几乎相同** → 0 维

**总差异 4 维** ✅——但语速相同。**为什么 OK**？因为其他 4 维差异足够大（性别 + 年龄 + 共鸣 + 音调）。

### 少女 vs 旁白
- 年龄：early 20s vs 30s → 略同
- 性别：female vs male → 1 维
- 共鸣：head+chest vs mid → 略同
- 语速：slow vs moderate → 1 维
- 音调：gentle rise vs flat → 1 维
- 情绪：tender melancholy vs neutral professional → 1 维

**总差异 3 维** ✅——刚好够。

### 老者 vs 旁白
- 年龄：late 60s vs 30s → 1 维
- 性别：male vs male → 0 维
- 共鸣：deep chest vs mid → 1 维
- 语速：slow vs moderate → 1 维
- 音调：falling vs flat → 略同
- 情绪：knowing vs neutral → 略同

**总差异 3 维** ✅——但因为是同性别，必须靠**共鸣位置**和**节奏**做最大区分。

## 实测"听感"评分

| 对比 | 听感清晰度 | 备注 |
|------|----------|------|
| 少女 vs 老者 | ⭐⭐⭐⭐⭐ | 完全分得开 |
| 少女 vs 旁白 | ⭐⭐⭐⭐ | 性别区分，OK |
| 老者 vs 旁白 | ⭐⭐⭐⭐ | 靠共鸣区分，OK |

## 修复方案：如果 2 角色撞车

假设少女和另一个少女角色（叫小雨）撞车了：

| 维度 | 邱苏晚 | 小雨 |
|------|--------|------|
| 年龄 | early 20s | early 20s |
| 性别 | female | female |
| 共鸣 | head+chest | chest-heavy |
| 语速 | slow | rapid |
| 音调 | gentle rise | falling, flat |
| 情绪 | tender melancholy | energetic hopeful |

→ **3 维差异**（共鸣 + 语速 + 音调 + 情绪）→ 听感明显不同。

## 配置经验总结

1. **同性别必须靠共鸣 + 语速做差异**（音色温度）
2. **同年龄必须靠语速 + 音调做差异**（情绪）
3. **同情绪必须靠共鸣 + 音调做差异**（气质）
4. **seed 间隔 1-2**（避免偶然撞音色）
5. **旁白 vs 主角** → 旁白用 mid，性别与主角不同
6. **主角无对白** → 第一人称 VN 旁白替代
