---
name: voice-acting-skill
description: 中文配音剧本自动化注音工具。将 Markdown 格式的剧本自动解析、分配方言音色、切分 15 秒批次、生成 QwenTTS / CosyVoice / OmniVoice 三引擎注音规则，并可执行配音合成。用于剧本→TTS 配音的完整管线。
user-invocable: true
metadata: {"openclaw":{"emoji":"🎙️","os":["darwin","linux","win32"],"primaryEnv":"VAS_OUTPUT_DIR"}}
---

# 配音剧本注音技能包

本技能包是 **编排器（orchestrator）**：将一个完整的"剧本→配音"管线拆成 5 个子技能，按用户需求路由到对应子技能或一次性串起全部。

## 启动协议

加载本技能后，先读取 `references/ENVIRONMENT.md` 确认运行环境就绪，再读 `references/ARCHITECTURE.md` 了解整体架构与数据流（`raw → parsed → analyzed → annotated → audio`），最后根据用户意图走下方路由表。

## 路由表

| 用户意图关键词 | 路由目标 | 子技能入口 |
|----------------|----------|------------|
| 解析剧本 / 剧本格式 / Markdown 表格 / 分镜 | 剧本解析 | `../voice-acting-script-parser/SKILL.md` |
| 角色音色 / 方言 / QwenTTS 音色 / 角色映射 | 音色分配 | `../voice-acting-voice-assigner/SKILL.md` |
| 批次切分 / 15 秒 / 批次大小 / tilt / 倾斜 | 批次管理 | `../voice-acting-batch-manager/SKILL.md` |
| 注音生成 / QwenTTS 情感标签 / CosyVoice 指令 / OmniVoice 拼音 / TTS 规则 | 注音生成 | `../voice-acting-annotation-generator/SKILL.md` |
| 配音合成 / TTS 引擎 / Gradio / HTTP / 声音 | 合成执行 | `../voice-acting-tts-synthesizer/SKILL.md` |
| 完整流程 / 一站式 / 全流程 / 端到端 | **全部串行** | 5 个子技能全部加载 |

> 路径说明(2026-08-14 拆扁): 5 个子 skill 原嵌套在 `skills/skills/<sub>/` 下,
> 按 BND-005 单层协议拆扁到 `game-production-kit/skills/voice-acting-<sub>/` 平铺。
> 从本 SKILL.md 看是 `../voice-acting-<sub>/` (因为 voice-acting-skill 自己也是
> game-production-kit 的子 skill)。

## 快速使用

```bash
# 1. 安装依赖
pip install -e .

# 2. 解析 + 分析 + 注音（生成三引擎规则剧本）
vas analyze raw/zpishow剧本AIGC指导版本.md -o output

# 3. 检查产物（parsed/ analyzed/ annotated/）
ls output/annotated/

# 4. 实际合成（需先启动 CosyVoice Gradio 服务）
vas synthesize -o output --cosyvoice-url http://127.0.0.1:50000

# 5. 查看工程文件（timeline / voice-map / comparison）
ls output/project/
```

## 输出结构

```
output/
├── parsed/script.json                    # 解析后的剧本
├── analyzed/script-analysis.json         # 角色→音色映射
├── analyzed/batch-plan.json              # 13 秒批次计划
├── annotated/qwen-tts.json + .md         # QwenTTS 注音
├── annotated/cosyvoice.json + .md        # CosyVoice 注音
├── annotated/omnivoice.json + .md        # OmniVoice 注音
├── annotated/all-engines.md              # 三引擎并排审核报告
├── audio/cosyvoice/*.wav                 # 合成音频（synthesize）
├── audio/omnivoice/*.wav                 # 合成音频（synthesize）
└── project/{timeline,voice-map,comparison}.json
```

## 方言音色速查

| 方言 | 音色 |
|------|------|
| 渝普 / 川渝 | Sunny |
| 东北口音 | Ethan |
| 沪普 | Jada |
| 北京口音 / 天津口音 | Dylan |

## 重要参考

- 架构全景：`references/ARCHITECTURE.md`
- 决策日志：`references/DECISIONS.md`
- 铁律约束：`references/CONSTRAINTS.md`
- 模块详解：`references/modules/{script-parser,voice-assigner,batch-manager,annotation-generator}.md`

## 数据流铁律

`raw/*.md` → `parsed/script.json` → `analyzed/{script-analysis,batch-plan}.json` → `annotated/*.{json,md}` → `audio/*/*.wav`

单向流动，禁止反向依赖。每个子技能只读上一阶段的 JSON 产物，不耦合实现细节。

## 子技能依赖关系

```
script-parser ──┐
                ├──▶ voice-assigner ──┐
                │                      ├──▶ batch-manager ──┐
                │                      │                     ├──▶ annotation-generator ──▶ tts-synthesizer
                └──────────────────────┘                     │
                                                              ▼
                                              analyzed/batch-plan.json
```

数据流单向、阶段性落盘；任意一阶段失败可重跑，不影响上游。

## 加载方式

Trae IDE 启动后，对话中提到以下任意关键词即可触发本技能：

- "配音剧本"、"TTS 注音"、"QwenTTS 注音"、"CosyVoice 注音"
- "剧本→配音"、"中文配音"、"AI 配音"
- "raw/zpishow 剧本"（示例文件路径）

加载后根据用户在对话中的具体诉求（解析 / 分配音色 / 切批 / 注音 / 合成 / 全流程）自动路由到对应子技能。

## 典型工作流（端到端示例）

1. **解析剧本**：调用 `script-parser` 把 `raw/zpishow剧本AIGC指导版本.md` 转成 `output/parsed/script.json`
2. **分配音色**：调用 `voice-assigner` 生成 `output/analyzed/script-analysis.json`
3. **切分批次**：调用 `batch-manager` 生成 `output/analyzed/batch-plan.json`
4. **生成注音**：调用 `annotation-generator` 产出三引擎 JSON + Markdown 审核报告
5. **人工审核**：打开 `output/annotated/all-engines.md` 检查角色、情感、注音是否合理
6. **执行合成**：启动 CosyVoice / OmniVoice 服务，调用 `tts-synthesizer` 输出音频
7. **导出工程**：使用 `project/{timeline,voice-map,comparison}.json` 进入剪辑流程

## 错误处理

- 任一阶段产物缺失 → 报错并提示重跑上游
- 三引擎中某引擎服务未启动 → 跳过该引擎继续其他引擎
- 倾斜 > 20% → 在 `annotated/all-engines.md` 异常清单中标红，但不阻断流程
- 多音字未消歧 → 同上，标黄警告

## 版本

`v0.1.0`（beta）— 2026-05-05

- 状态：5 个子技能全部可用
- 待办：QwenTTS 商业 API 接入、Web 端 UI、自动化音色微调代理（`agents/` 当前为空）
- 测试：`scripts/tests/test_core.py` 35 个 pytest 用例覆盖核心管线

