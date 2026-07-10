# 来源与权威

> 本 skill 基于以下公开资源。所有论断都标注了来源。

## 核心来源（强烈推荐读完）

### 1. Qwen3-TTS 官方博客（2025-12-23）
**链接**：https://qwen.ai/blog?id=qwen3-tts-vc-voicedesign

**要点**：
- VoiceDesign 模型支持复杂自然语言指令
- 控制 5 个维度：timbre / prosody / emotion / persona / 节奏
- 10 种语言，中文为母语
- InstructTTSEval 显著优于 GPT-4o-mini-tts 和 Gemini-2.5-pro-preview-tts（角色扮演测试）

**本 skill 引用**：
- [01-five-axes.md](01-five-axes.md) 的 5 维分类
- [04-instruct-template.md](04-instruct-template.md) 的 5 段式结构

### 2. Voice Cloning & Voice Design Guide (ocdevel)
**链接**：https://ocdevel.com/blog/20260302-qwen-tts-voice-cloning

**要点**：
- VoiceDesign vs Base vs CustomVoice 模型选择表
- Instruct 长度 30-60 词最优
- X-Vector mode 不需要 transcript 但质量降低
- 3-15 秒参考音频甜蜜区

**本 skill 引用**：
- [01-five-axes.md](01-five-axes.md) 的"短 prompt 失败"论断
- [04-instruct-template.md](04-instruct-template.md) 的 30-60 词

### 3. How To Design AI Voices (getstream.io)
**链接**：https://getstream.io/blog/qwen3-voice-design/

**要点**：
- 完整的"用自然语言控制声音"实战指南
- 5 个角色设计示例（电影/游戏/多人播客/客服/有声书）
- 强调"prompt 工程"对 TTS 至关重要

**本 skill 引用**：
- [04-instruct-template.md](04-instruct-template.md) 的范例 1-5
- [05-coordination.md](05-coordination.md) 的多角色协调

## 实验性来源（数值参数）

### 4. Faster-Qwen3-TTS 稳定性研究 (NVIDIA forum)
**链接**：https://forums.developer.nvidia.com/t/three-times-voiceclone-voicedesign-customvoice-faster-qwen3-tts-for-nvidia-dgx-spark-gb10/370530/22

**要点**：
- **v5 默认 `temperature=0.8, top_k=50, top_p=0.9`**
- 音频剧建议 `temperature=0.65-0.75, top_p=0.85`
- 关键问题：流式模式（streaming）下 77% 的音频是"free-running" → 漂移
- v5 改用 `non_streaming_mode=True` 修复

**本 skill 引用**：
- [03-numeric-params.md](03-numeric-params.md) 的所有参数推荐值
- [06-antipatterns.md](06-antipatterns.md) 反模式 7

### 5. Qwen3-TTS-VoiceDesign 一文详解 (CSDN)
**链接**：https://blog.csdn.net/weixin_30789053/article/details/157522108

**要点**：
- "声学属性 + 情绪维度 + 多语言适配" 三层
- 8 个实战 prompt 范例（含撒娇萝莉/老年侦探等）

**本 skill 引用**：
- [01-five-axes.md](01-five-axes.md) 的"Want/Fear → 声音"推导
- [04-instruct-template.md](04-instruct-template.md) 范例 1 的来源

## 反例来源

### 6. Realistic Voice Cloning Pitfalls
**多个**社区帖（GitHub Issues / Reddit / 知乎）：

- 声音克隆 `ref_audio` > 30s 会进入死循环
- 跨语言 instruct 容易导致口音混乱
- temperature > 0.9 必崩

**本 skill 引用**：
- [03-numeric-params.md](03-numeric-params.md) 的高温警告

## 本项目实测

「时空里等你」项目（webgal_case02）使用本方法：

| 角色 | instruct 词数 | 效果 |
|------|--------------|------|
| 邱苏晚 | 51 | ⭐⭐⭐⭐ 听得出温柔忧郁 |
| 林之一 | 53 | ⭐⭐⭐⭐ 听得出内敛 |
| 咖啡馆老板 | 51 | ⭐⭐⭐⭐⭐ 老沉看透感强 |
| 旁白 | 48 | ⭐⭐⭐⭐ 文档片风格 |

详见 [examples/qiu-suwan.md](examples/qiu-suwan.md) 和 [examples/role-trio.md](examples/role-trio.md)。

## 引用规范

如果在本 skill 之外引用本方法论：
- 标注 "from voice-character-design skill"
- 链接到本目录
- 不要复制 30+ 词的范例——这是经验调出来的，每个项目要重新设计
