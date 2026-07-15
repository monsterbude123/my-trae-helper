---
name: voice-character-design
description: TTS 音色设计方法论——如何为 VN/AVG 角色设计贴合人设的音色提示词。覆盖 Qwen3-TTS / IndexTTS-2 / F5-TTS / Chatterbox / VibeVoice。原则：Want/Fear 推导出五维声音档案、温度/语速/音调/共鸣/呼吸五轴调参、与 BGM 协调、避免同质化。触发词：TTS 音色设计、角色声音、声音人设、Qwen3-TTS instruct、voice profile、voice design。
user-invocable: true
metadata: {"openclaw":{"emoji":"🎭","os":["darwin","linux","win32"]}}
---

# 角色音色设计 (Voice Character Design)

把**角色人设**翻译成**TTS 提示词**的方法论。**不重复 TTS 调用流程**（那是 `comfyui-voice-pipeline` 的事）。

> 核心问题：**"我有一个角色描述，怎么写出能让 TTS 模型生成对的声音的 instruct？"**
> 核心反模式：**"年轻女性，温柔甜美"** — 这条 prompt 8 个 TTS 模型会给你 8 个完全不同的声音。

## 核心方法论（5 步）

```
角色人设（Want/Fear + 性格 + 外形）
        ↓ Step 1: 提取五维声学特征（年龄/性别/共鸣/语速/音调）
```

> 🛑 硬引用约束（H8 修复）：Step 1 的 Want/Fear 必须机械派生自 story-design.md。
> - 读取 game-story-design 产出的 story-design.md → 定位对应角色 → 提取 Want/Fear
> - 禁止在 voice-card 中独立填写 Want/Fear
> - 若 story-design.md 中的 Want/Fear 变更 → voice-card 中的声学特征需重新推导
> - 在 voice-card 中标注 source: story-design.md@{version} {date}

```
        ↓ Step 2: 选择音域区间（参考声带物理）
        ↓ Step 3: 决定 5 个数值参数（temperature/top_p/repetition_penalty/max_new_tokens/seed）
        ↓ Step 4: 写出 30-60 词的英文 instruct
        ↓ Step 5: 与 BGM 协调 + 与其他角色音色区分度检查
```

## 5 步详解（按需加载）

| 步骤 | 主题 | 文件 |
|------|------|------|
| Step 1 | 提取五维声学特征 | [references/01-five-axes.md](references/01-five-axes.md) |
| Step 2 | 声带物理与音域 | [references/02-vocal-range.md](references/02-vocal-range.md) |
| Step 3 | 数值参数怎么调 | [references/03-numeric-params.md](references/03-numeric-params.md) |
| Step 4 | instruct 写作模板 | [references/04-instruct-template.md](references/04-instruct-template.md) |
| Step 5 | 与 BGM/其他角色协调 | [references/05-coordination.md](references/05-coordination.md) |

## 反模式（必读）

- ❌ "年轻女性，温柔甜美" → 太抽象
- ❌ 一句话讲完所有维度 → 30 词以下必失败
- ❌ 不同角色用相同 prompt 改温度 → 听感雷同
- ❌ 静音问题不会调 max_new_tokens → 看 §3
- ❌ 中文用 "Chinese female" 写 instruct → 写"Chinese **Mandarin** female"

详见 [references/06-antipatterns.md](references/06-antipatterns.md)

## 模板（直接复制改）

- [templates/character-voice-card.md](templates/character-voice-card.md) — 单角色完整配置卡（含人设 + 5 维特征 + 数值 + instruct）
- [templates/voice-config-yaml.md](templates/voice-config-yaml.md) — 批量角色配置 yaml 模板
- [templates/role-design-interview.md](templates/role-design-interview.md) — 面试式提问清单（生成新角色时用）

## 例子

- [examples/qiu-suwan.md](examples/qiu-suwan.md) — 「时空里等你」邱苏晚完整音色设计
- [examples/role-trio.md](examples/role-trio.md) — 三角色对比（少女/大叔/旁白）的设计差异

## 与其他 skill 的协作

- **TTS 调用流程**：`comfyui-api-skills`（音频生成管线）
- **角色设计 Want/Fear 推导**（硬引用）：`game-story-design` — Step 1 禁止独立填写 Want/Fear。必须从 story-design.md 机械读取角色宪法中的 Want/Fear/弧光。voice-card 中标注引用来源 story-design.md@v{N} {date}
- **脚本集成**：`webgal-scripting` 或其他引擎脚本技能（将本 skill 产出的 `voices.json` 注入到场景脚本）

## 检查清单（生成一份角色音色配置后逐项验证）

```
□ [HARD] Want/Fear 来自 story-design.md？不是独立填写的？标注了 source 版本号？
□ 五维特征都明确写了（年龄/性别/共鸣/语速/音调）
□ 数值参数有理由（不是瞎抄 0.7/0.85）
□ 至少 30 词，禁用 2-5 词短 prompt
□ 与同剧其他角色区分度 ≥ 3 个维度
□ BGM 不抢戏（频段错开）
□ 静音占比 < 20%（调整 max_new_tokens + 文本分句）
□ TTS 引擎已在 voice-card 中记录（引擎/版本/种子）？换了引擎必须重新验收声音
```

## 来源与权威

本 skill 基于以下研究（详见 [references/07-sources.md](references/07-sources.md)）：
- [Qwen3-TTS VoiceDesign 官方文档](https://qwen.ai/blog?id=qwen3-tts-vc-voicedesign)
- [Voice Cloning & Voice Design Guide (ocdevel)](https://ocdevel.com/blog/20260302-qwen-tts-voice-cloning)
- [Qwen3-TTS 一文详解 (CSDN)](https://blog.csdn.net/weixin_30789053/article/details/157522108)
- [How To Design AI Voices (getstream.io)](https://getstream.io/blog/qwen3-voice-design/)
- [Faster-Qwen3-TTS 稳定性研究 (NVIDIA forum)](https://forums.developer.nvidia.com/t/three-times-voiceclone-voicedesign-customvoice-faster-qwen3-tts-for-nvidia-dgx-spark-gb10/370530/22)
