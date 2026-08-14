---
name: vibe-coding-standards
description: Vibe Coding 核心组件编写原则 v2.5 — AGENTS.md、Rules、Skills、Subagents 的结构规范、体积弹性范围（100~350 行）和防上下文击穿策略。v2.5 放宽体积阈值 +30%（AGENTS/SKILL/Subagent 100~350、> 350 才拆；Rule ≤ 120），校验脚本同步调整。
triggers: [编写AGENTS.md, 写规则, 编写skill, 写子代理, vibe coding, 防上下文击穿, 体积红线, 子代理设计, 系统提示词, agent prompt, 项目地图, 地图内联, 防机械指针化]
intent: Vibe Coding 核心组件编写原则 v2
category: orchestration
audience: [agent]
---
# Vibe Coding 核心组件编写原则

> 分层治理、按需加载、地图内联（防迷路）+ 规范指针（防击穿）。
> 详细规范见 [references/VibeCodingStandards.md](references/VibeCodingStandards.md)

---

## §1 通用铁律（适用于所有组件类型）

1. **体积弹性范围 100~350 行（v2.5 放宽 +30%）**。< 100 行可能过度拆分导致文件碎片化；> 350 行才考虑提取到 references/。超过 350 行 = 触发"中间遗忘"风险，应拆。
2. **指针优先：** 只放大纲 + 引用路径，禁止内联大段代码或详细说明。
3. **原子化：** 每个文件只做一件事，按需加载，非必需不读取。

### §1.5 地图 vs 规范 — 核心区分（防机械指针化）

> 指针优先不是"全部指针"。agent 不知道项目长什么样就会迷路，迷路后盲搜消耗远大于多内联 30 行。

```
判定口诀: "agent 不知道这个会迷路吗？"

是 → 🗺️ 地图（内联）    否 → 📋 规范（指针）
```

### §1.6 Context Engineering 5 Pillar（参考 GitHub Copilot 2026-06）

> 来源: [external-report 2026-08-14 §M-03](../2026-08-14/external-report.md) + [GitHub Copilot context handling](https://github.blog/ai-and-ml/github-copilot/getting-more-from-each-token-how-copilot-improves-context-handling-and-model-routing/)

**中等 prompt + 优秀 context 几乎总赢过 优秀 prompt + 贫 context**(Copilot 实测 2026-06)。规则文件首次可用率从 40% → 80%+。**前置 30 分钟写好 context 远比调 prompt 划算**。

5 Pillar:
1. **项目结构** — 让 agent 知道"文件在哪、模块怎么分"
2. **代码风格** — 命名 / 缩进 / 错误处理 / 测试约定
3. **领域知识** — 业务术语 / 关键决策 / 历史原因
4. **相关代码示例** — 真实可参考的范例(胜过抽象描述)
5. **反馈循环** — agent 输出错了,怎么纠正(规则补 / 例补 / 排除补)

| 地图（必须内联） | 规范（指针引用） |
|-----------------|----------------|
| 技术栈清单 + 版本 | API 详细文档 |
| 目录结构树（一级） | 鉴权流程完整实现 |
| ASCII 架构拓扑图 | 长代码示例（>10行） |
| 关键入口文件路径 | 配置项完整列表 |
| 启动/构建命令 | 部署运维手册 |
| 核心设计决策（Why，≤3条） | 历史决策记录 |
| 关键命名约定/路径约定 | 各模块内部实现细节 |

**地图的弹性范围 100~350 行（v2.5 放宽）**，但必须满足：每行都是"不知道就会迷路"的内容。> 350 行才考虑提取 references/。

---

## §2 AGENTS.md 编写原则（项目宪法）

```
结构: 项目地图(内联) + Non-negotiables(≤5) + Version + Goal-driven + Surgical changes
       + Persistence + Tool/Failure + Communication + Session hygiene
       + Self-improvement loop + 规范指针
体积: 弹性范围 100~350 行（v2.5）。 含地图 ≤ 350 行（地图弹性放宽），纯铁律 ≤ 200 行
  - < 100 行: 文件碎片化，反而难维护
  - 100~350 行: 最合适
  - > 350 行: 必须提取 references/
地图: 技术栈/目录树/架构拓扑/入口文件/启动命令/设计决策 — agent 不知道就会迷路
规范: 详细文档/长代码示例 → references/ 指针引用
关键模块:
  - Communication: 直接简洁，有歧义就问，小事直接做（减少不必要的 AskUserQuestion）
  - Session hygiene: 上下文稀缺，用子代理探索，不污染主对话
  - Self-improvement loop: 犯错后补充规则，定期修剪。与 Rules 增量迭代呼应
冲突: 用户指令 > AGENTS.md，但必须告知冲突点并征求确认
```

---

## §3 Rules 编写原则（代码法律）

```
分层:
  P0 - 生产阻断级：输入校验、事务必须
  P1 - 架构规范：分层约束
  P2 - 代码风格：行数限制、异常处理、注释规范
  P3 - 参考指针：所有示例指向独立文件，严禁内联

增量: AI 犯一次错加一条规则，必须可验证
```

> 规则编写完整工艺（7要素/无死引用/零概念重叠/决策树4路/异常表规范/自检清单/禁止行为）→ [references/rule-writing-craft.md](references/rule-writing-craft.md)

### §3.1 技能脚本路径解析

> 执行技能包内嵌脚本时的路径搜索链 → [references/skill-script-paths.md](references/skill-script-paths.md)

---

## §4 Skills 编写原则（专业手册）

```
体积: 弹性范围 100~350 行（v2.5）。 纯铁律 ≤ 200 行
  - < 100 行: 过度拆分
  - 100~350 行: 最合适
  - > 350 行: 必须提取 references/errors.md 或 references/*.md
内容: 核心铁律 + 骨架流程（每步一句话引用 references/）
结构: YAML frontmatter → Prerequisites → Core Workflow → Constraints → Quality Checklist
可选增强: [Quick Start] [Examples] [Troubleshooting] — 按需添加，示例比描述管用 10 倍
  若加完后超 350 行 → 把 Troubleshooting 移到 references/errors.md

### §4.1 技能依赖检查（硬性标准）

> **MUST**: 任何有跨技能引用的 Skill 必须声明 `requires` 并在加载时执行依赖检查。
> **禁止**: agent 发现依赖缺失后自行降级 — 必须阻断并提示用户。
> 完整协议 → [references/skill-dependency-check.md](references/skill-dependency-check.md)
目录:
  skill-name/
  ├── SKILL.md          # 核心骨架（必需）
  ├── references/       # 深度资料（按需查阅）
  ├── templates/        # 模板文件
  └── scripts/          # 辅助脚本
```

---

## §5 Subagents 编写原则（外包团队）

```
体积: 弹性范围 100~350 行（v2.5）。 纯铁律 ≤ 200 行
  - < 100 行: 过度拆分
  - 100~350 行: 最合适
  - > 350 行: 必须提取 references/
内联禁令: 严禁把 references/templates 已有内容内联到 agent 文件
组成: 核心铁律(≤10) + 骨架工作流(每步引用 references/) + I/O 骨架 + 异常速查 + 参考链接
通信: 输出必须是结构化 JSON Lines 或 Markdown 表格，严禁大段散文
降级: 超时或连续失败 2 次 → 返回 status: partial → 主代理决策

标准三件套（复杂任务分工防撞车）:
  Explorer(探索者): 只读扫描 → 输出待处理清单 [{file, reason}]
  Worker(执行者):  按文件集分工编辑 → 各干各的不冲突
  Reviewer(审查者): 对抗性验证 Worker 输出 → 通过/不通过 + 问题清单
  铁律: Explorer 不修改，Worker 不自审，Reviewer 不修改不放水
```

---

## §6 跨组件治理

```
冲突裁决: 用户指令 > AGENTS.md > Subagent Prompt > Rules > Skills
索引规范: 项目根维护 REFERENCES_INDEX.md 或极度语义化文件命名
文档自维护: validate_vibe_docs.sh 挂载 CI，校验行数/内联代码块/子代理声明
```

---

## §7 执行流程

1. 判断组件类型（AGENTS.md / Rule / Skill / Subagent）
2. **地图判定：逐行问"agent 不知道这个会迷路吗？"**
   - 是 → 内联（技术栈、目录树、架构图、入口文件、启动命令）
   - 否 → 读取 [references/VibeCodingStandards.md](references/VibeCodingStandards.md) 对应章节，指针引用
3. 按对应结构骨架生成内容
4. 自检：
   - 地图内容是否都在？agent 拿着这个文件能独立找到所有入口吗？
   - 规范内容是否都用指针了？有没有内联了 >10 行的代码块？
   - 行数是否在弹性范围内（v2.5：地图 300 / 纯规范 200）？
