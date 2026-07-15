# 角色音色配置卡

> **用 1 张卡定义 1 个角色**——填好之后就是 voices.json 的 1 条目。
> **填表流程**：先填人设（Want/Fear + 性格）→ 再推 5 维 → 再写数值 → 最后写 instruct。
> 人设来源: story-design.md@v{N} {date}

## 1. 基础信息

| 字段 | 值 |
|------|---|
| 角色 ID（英文/拼音） | qiu_suwan |
| 中文名 | 邱苏晚 |
| 性别 | 女 |
| 年龄 | 23 |
| 身份 | 画家 / 美院研究生 |
| **TTS 引擎** | {QwenTTS \| CosyVoice \| F5-TTS \| IndexTTS-2} |
| **引擎版本** | {version} |
| **种子/参数** | seed={seed}, temperature={temp} |

## 2. 角色人设（驱动声音）

<!-- 🛑 H8 HARD REFERENCE: 以下 Want/Fear 必须从 story-design.md 机械复制，禁止独立填写 -->
<!-- 来源: story-design.md § 人物设计 {角色名} -->

| 字段 | 内容 |
|------|------|
| Want | {从 story-design.md 复制的 Want} |
| Fear | {从 story-design.md 复制的 Fear} |
| 性格 | 温柔、安静、内心有定见、笑着等了三小时雨的人 |
| 外形 | 过肩黑长直，纤细，米白色连衣裙 |
| 关键场景情绪 | 日常（温柔）→ 雾中（神秘+忧郁）→ 真结局（治愈） |

## 3. 五维声学特征

| 维度 | 推断 | 来源 |
|------|------|------|
| **年龄** | early 20s | 声带已成熟但未衰 |
| **性别气质** | female, natural | 无需强调和气质 |
| **共鸣位置** | head + slight chest | 温柔但有内核——不是完全飘的纯头声 |
| **语速/节奏** | 慢 + 停顿多 | 沉静的人不会抢着说话 |
| **音调走势** | 句尾略上扬 | 脆弱感 + 期待感，但不像"撒娇"那样大幅上扬 |

## 4. 数值参数

| 参数 | 值 | 理由 |
|------|------|------|
| `temperature` | 0.75 | 略低保证稳定，少量起伏表现情绪 |
| `top_p` | 0.85 | 标准保守截断 |
| `repetition_penalty` | 1.05 | 默认；防止极少见的复读 |
| `max_new_tokens` | 280 | 单句 < 40 字为主 |
| `seed` | 10042 | **跨场景固定**（见 §seed 规范） |

## 5. Instruct（英文，30-60 词）

```
A young Chinese female in her early 20s with a crystalline, gentle mid-range voice. 
Tender and slightly melancholic, with soft, measured pacing at a moderate tempo. 
Speaks standard Mandarin with natural warmth, and her pitch gently rises on emotional phrases. 
There's a fragile, intimate quality to her delivery, as if every word is precious.
```

**词数检查**：51 词 ✅

## 6. 场景情绪变体（可选）

> 同一角色在不同情绪下用不同 instruct。

| 变体 | 关键词 | 适用场景 |
|------|--------|---------|
| `qiu_suwan_calm` | measured, calm, naturally warm | 日常、雨中等候 |
| `qiu_suwan_melancholy` | tender, fragile, slight tremor | 雾中相遇、回忆 |
| `qiu_suwan_hopeful` | bright, rising, warm | 真结局前夕、告白 |

## 7. 协调

| 对象 | 关系 |
|------|------|
| BGM | s_cafe（咖啡馆）= 完美；s_unease（不安）= ⚠️ 频段略冲突，建议降 BGM 音量 |
| 林之一 | 内敛男声 vs 她 = 区分明显（性别 + 语速） |
| 咖啡馆老板 | 老者深沉 vs 她 = 区分明显（年龄 + 音色） |
| 旁白 | 中性专业 vs 她 = 区分明显（年龄 + 情绪） |

## 8. 第一次测试

- 生成 3 条不同 seed（10042, 10043, 10044）→ 选 1 条最像的
- 听一段 5-10 秒的对白 → 检查：
  - □ 听得出"温柔忧郁少女"
  - □ 音调稳定不漂移
  - □ 静音占比 < 20%
  - □ 与 BGM 共存不冲突
