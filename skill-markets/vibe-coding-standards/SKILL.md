---
name: vibe-coding-standards
description: Vibe Coding 核心组件编写原则 v2.3 — AGENTS.md、Rules、Skills、Subagents 的结构规范、体积红线和防上下文击穿策略。v2.3 新增标准三件套模式、Skills 可选增强段、AGENTS.md 扩展模块。适用于编写/审查 AI 代理的提示词、规则、技能和子代理定义。
triggers:
  - "编写AGENTS.md"
  - "写规则"
  - "编写skill"
  - "写子代理"
  - "vibe coding"
  - "防上下文击穿"
  - "体积红线"
  - "子代理设计"
  - "系统提示词"
  - "agent prompt"
  - "项目地图"
  - "地图内联"
  - "防机械指针化"
---

# Vibe Coding 核心组件编写原则

> 分层治理、按需加载、地图内联（防迷路）+ 规范指针（防击穿）。
> 详细规范见 [references/VibeCodingStandards.md](references/VibeCodingStandards.md)

---

## §1 通用铁律（适用于所有组件类型）

1. **体积红线：单文件 ≤ 150 行。** 超过即击穿上下文，触发"中间遗忘"。
2. **指针优先：** 只放大纲 + 引用路径，禁止内联大段代码或详细说明。
3. **原子化：** 每个文件只做一件事，按需加载，非必需不读取。

### §1.5 地图 vs 规范 — 核心区分（防机械指针化）

> 指针优先不是"全部指针"。agent 不知道项目长什么样就会迷路，迷路后盲搜消耗远大于多内联 30 行。

```
判定口诀: "agent 不知道这个会迷路吗？"

是 → 🗺️ 地图（内联）    否 → 📋 规范（指针）
```

| 地图（必须内联） | 规范（指针引用） |
|-----------------|----------------|
| 技术栈清单 + 版本 | API 详细文档 |
| 目录结构树（一级） | 鉴权流程完整实现 |
| ASCII 架构拓扑图 | 长代码示例（>10行） |
| 关键入口文件路径 | 配置项完整列表 |
| 启动/构建命令 | 部署运维手册 |
| 核心设计决策（Why，≤3条） | 历史决策记录 |
| 关键命名约定/路径约定 | 各模块内部实现细节 |

**地图的 150 行上限可以弹性放宽到 ~200 行**，但必须满足：每行都是"不知道就会迷路"的内容。

---

## §2 AGENTS.md 编写原则（项目宪法）

```
结构: 项目地图(内联) + Non-negotiables(≤5) + Version + Goal-driven + Surgical changes
       + Persistence + Tool/Failure + Communication + Session hygiene
       + Self-improvement loop + 规范指针
体积: 含地图 ≤ 200 行（地图弹性），纯铁律 ≤ 150 行
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

---

## §4 Skills 编写原则（专业手册）

```
体积: SKILL.md ≤ 150 行
内容: 核心铁律 + 骨架流程（每步一句话引用 references/）
结构: YAML frontmatter → Prerequisites → Core Workflow → Constraints → Quality Checklist
可选增强: [Quick Start] [Examples] [Troubleshooting] — 按需添加，示例比描述管用 10 倍
  若加完后超 150 行 → 把 Troubleshooting 移到 references/errors.md
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
体积: ≤ 150 行
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
   - 行数是否在弹性范围内（地图 200 / 纯规范 150）？
