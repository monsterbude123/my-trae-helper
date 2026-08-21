---
name: aigc-smart-kit
description: AIGC 多模态创意工作台统一入口。当用户需要视频提示词制作(I2V / T2V / V2V / R2V)、画面描述生成、镜头运镜语法咨询、跨模型迁移(H3 / Hailuo / Seedance / Kling 等)时主动加载。**核心场景**:用户上传图片 / 视频 / 音频 / 文本 → 自动分析 + 路由 → 生成影视级视频 prompt。主入口只做路由 — 方法论继承自 video-prompt-method 父级 skill,具体公式按平台 + 输入模式转发到对应子 skill。Use when the user wants video generation prompts (text/image/video/reference to video) across MiniMax H3 / Hailuo / Seedance / Kling 3.0.
version: 2.0.0
license: MIT
metadata:
  author: my-trae-helper
  category: aigc-creative
  platform-coverage:
    - MiniMax-H3
    - MiniMax-Hailuo-2.3
    - ByteDance-Seedance-2.0
    - ByteDance-Seedance-2.5
    - Kling-3.0
    - Kling-V3-Omni
  input-mode-coverage:
    - i2v
    - t2v
    - v2v
    - ref2v
  created: 2026-08-19
  updated: 2026-08-20
---

# AIGC-smart-kit

> 多模态 AIGC 创意工作台统一入口。**V2.0** 升级为「方法学父级 + 8 子 skill」架构:通用方法论归 `video-prompt-method` 父级,4 类视频生成模式(i2v/t2v/v2v/ref2v)× H3 平台 = 4 个儿子 skill,加 seedance / kling 两个 I2V 跨平台兄弟。

## §0 何时加载

```
MUST 加载:
  - 用户上传图片 / 视频 / 音频 → 想生成视频 prompt
  - 用户纯文字描述 → 想生成视频 prompt
  - 用户提到: 图生视频 / I2V / T2V / 视频续写 / 视频转视频 / 参考生视频 / 文生视频
  - 模型关键词: H3 / Hailuo / 海螺 / MiniMax / Seedance / 即梦 / 豆包 / Kling / 可灵

MUST NOT 加载(改去其他 skill):
  - 纯图片生成(T2I) → comfyui-prompt-engineer / minimax-multimodal(image)
  - 视频剪辑 / 后期合成 → comfyui-video-pipeline
  - 视频生产编排 → comfyui-video-production
  - TTS / 配音 → voice-character-design / comfyui-voice-pipeline
```

## §1 架构:父级 + 4 模式 × 1 平台 × 跨平台

```
方法学父级:
  video-prompt-method/          通用视频提示词方法论(时间切片 / 主角锁定 / 抽象具体化 / 声音设计)

输入前置:
  video-input-analyzer/         多模态输入分析(图 / 视频 / 音频 / 文本 → input-report.json)

H3 平台 × 4 输入模式(4 个儿子):
  i2v-h3-prompt/                图生视频(祖传,继承父级)
  t2v-h3-prompt/                文生视频(从 0 创造,7 维度精确化)
  v2v-h3-prompt/                视频转视频(extend / first-last-frame / edit 3 子模式)
  ref2v-h3-prompt/              参考生视频(多模态素材角色分配 + 冲突解决)

跨平台 I2V(2 个兄弟):
  i2v-seedance-prompt/          Seedance 2.0/2.5(30s 四拍)
  i2v-kling-prompt/             Kling 3.0(S/M/B 三段式 + element reference)
```

## §2 子 skill 路由表

| 用户意图 | 加载子 skill | 输入模式 |
|----------|--------------|----------|
| 通用方法论(被儿子引用) | `skills/video-prompt-method/` | (父级) |
| 多模态输入 → 统一报告 | `skills/video-input-analyzer/` | (前置) |
| **图生视频**(默认) | `skills/i2v-h3-prompt/` | i2v |
| **文生视频**(纯文字) | `skills/t2v-h3-prompt/` | t2v |
| **视频续写 / 编辑** | `skills/v2v-h3-prompt/` | v2v |
| **参考生视频**(多图 + 视频 + 音频) | `skills/ref2v-h3-prompt/` | ref2v |
| **Seedance 2.0/2.5**(用户指定平台) | `skills/i2v-seedance-prompt/` | i2v |
| **Kling 3.0**(用户指定平台) | `skills/i2v-kling-prompt/` | i2v |

> 📌 **方法论继承链**:每个儿子 SKILL.md 顶部 `parent-skill: video-prompt-method`,继承通用方法论。
> 📌 **输入前置**:所有儿子共用 `video-input-analyzer/` 多模态前置,产出 input-report.json(替代老的 image-report.json)。
> 📌 **向后兼容**:`i2v-image-analyzer/` 已 deprecated(redirect 到 video-input-analyzer)。

## §3 加载协议(按输入类型分流)

```
场景 A: 用户上传一张图 + 关键词
  → Skill(name="aigc-smart-kit/skills/video-input-analyzer")
  → input_mode = i2v
  → 默认路由 Skill(name="aigc-smart-kit/skills/i2v-h3-prompt")
  → 交付 + 改造钩子(§5)

场景 B: 用户纯文字 + 想生成视频
  → Skill(name="aigc-smart-kit/skills/video-input-analyzer") --text ...
  → input_mode = t2v
  → 路由 Skill(name="aigc-smart-kit/skills/t2v-h3-prompt")

场景 C: 用户上传视频 + 想续写 / 编辑
  → Skill(name="aigc-smart-kit/skills/video-input-analyzer") --video ...
  → input_mode = v2v
  → 路由 Skill(name="aigc-smart-kit/skills/v2v-h3-prompt")
  → 自动判别子模式 extend / first-last-frame / edit

场景 D: 用户多模态素材(图 + 视频 + 音频)+ 想融合
  → Skill(name="aigc-smart-kit/skills/video-input-analyzer") --reference-images ...
  → input_mode = ref2v
  → 路由 Skill(name="aigc-smart-kit/skills/ref2v-h3-prompt")

场景 E: 用户明确指定 Seedance / Kling
  → 跳过 analyzer,直接加载对应平台 skill
  → Skill(name="aigc-smart-kit/skills/i2v-seedance-prompt") 或 i2v-kling-prompt

场景 F: 用户没给输入(纯 prompt 编辑 / 方法论学习)
  → 直接 Skill(name="aigc-smart-kit/skills/video-prompt-method")(父级)
```

## §4 跨模式共识铁律(父级 skill 提炼)

```
所有儿子共享(来自 video-prompt-method):
  1. 时间切片:每段独立五件套(景别 + 主体动作 + 主体位置 + 精确化描述 + 镜头)
  2. 主角锁定:video-prompt-method/references/character-lock.md
  3. 抽象→具体:video-prompt-method/references/concreteness.md
  4. 避免过度指定 + 留白:video-prompt-method/references/negative-space.md
  5. 声音设计三层:video-prompt-method/references/audio-design.md

平台特化(各儿子各自):
  - i2v-h3-prompt:H3 三段式 + 视觉连续性约束
  - t2v-h3-prompt:T2V 7 维度精确化公式
  - v2v-h3-prompt:3 子模式(extend / first-last-frame / edit)
  - ref2v-h3-prompt:多模态素材角色分配 + 冲突解决
```

## §5 改造钩子(i2v-h3-prompt 输出后 MUST 追加)

```
─────────────────────────────────────────
【已生成】MiniMax H3 / I2V / 时间切片 / 中英双语可选

📌 你可以这样改造:
  • "改 Seedance 2.5 版本"  → 路由 i2v-seedance-prompt(30s 四拍)
  • "改 Kling 3.0 版本"     → 路由 i2v-kling-prompt(元素参考 + 锁脸)
  • "改纯文字模式"          → 路由 t2v-h3-prompt(7 维度精确化公式)
  • "改视频续写模式"        → 路由 v2v-h3-prompt(extend 子模式)
  • "改多模态参考模式"      → 路由 ref2v-h3-prompt(素材角色分配)
  • "要更短 / 更长"         → 调整时间切片段数(2 / 3 / 4 段)
  • "加对白"                → description 段加 S1 says: "..."
  • "加 BGM"                → non_diegetic_music 段补充
  • "按笔记法重写"          → 路由 video-prompt-method 父级 skill §1-§11
  • "改成 Hailuo 02 方括号" → references/hailuo02-migration.md 反向
  • "中文输出"              → --language zh 参数
─────────────────────────────────────────
```

## §6 反例(MUST 避免)

| ❌ 反模式 | ✅ 正确做法 |
|----------|-----------|
| 主入口展开任何子 skill 公式 | 只指针到 `skills/<name>/references/` |
| 子 skill 复制父级 skill 的通用方法论 | 直接 `extends: video-prompt-method`,references 指针继承 |
| 上传 1 图却跳过 analyzer | 走 §3 场景 A,先 analyzer → 再 prompt |
| 加载老 skill `i2v-image-analyzer` | 已 deprecated,用 `video-input-analyzer` |
| 在 AIGC-smart-kit 内写 T2I / 视频剪辑 | 路由到对应专业 skill |
| 输出 prompt 后忘给改造钩子 | i2v-h3-prompt 输出 MUST 追加 §5 |

## §7 维护

- 任务跟踪: `todos/task.md`
- 验收清单: `todos/checklist.md`
- 子 skill 全景: `skills/` (1 父级 + 1 analyzer + 4 H3 儿子 + 2 跨平台兄弟 = 8 个)

## §8 来源

- 设计意图蒸馏自 [docs/research/2026-08-19-i2v-prompt-skills.md](../../../docs/research/2026-08-19-i2v-prompt-skills.md)
- 实战笔记: [docs/references/note-video-prompt/](../../../docs/references/note-video-prompt/)(17 张 jpg)
- V2.0 架构升级:2026-08-20 抽 video-prompt-method 父级 + analyzer 升级 + 4 儿子拓展