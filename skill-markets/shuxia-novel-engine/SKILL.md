---
name: subculture-novel-engine
version: 1.0.0
version: 1.0.0
description: "General fiction world-building engine. Use for novel writing, chapter planning,
world-building consistency checks, character arc verification, foreshadow tracking,
plot enumeration, ripple analysis, combat/drama evaluation, and creative workflows.
Triggers on: novel writing, world-building, chapter planning, consistency auditing,
foreshadow management, character design, plot structure, creative pipelines.
intent: General fiction world-building engine
category: gate
audience: [designer]
---
# 亚文化创作引擎 · 薄编排层

> 通用虚构世界创作引擎——约束空间内的可能性管理器
> 版本: v2.0 · 设计: 薄编排层 + 按需加载，防上下文腐烂

---

## §0 快速启动（每个新会话必读）

```
# 第一次用这个技能？按这个顺序读:
1. 本文档 §0-§2 (快速启动 + 触发 + 螺旋门禁)
2. agents/creative_director.md (理解谁是最终裁决者)
3. 你当前阶段的 workflow/ (只读当前需要的)

# 继续上次会话？直接读:
1. S01_会话上下文.md (项目状态)
2. S00_项目工作台.md (当前优先级)
3. 回到上次的阶段继续

# 首次接入项目？
→ 见 workflows/W_INIT_系统初始化.md

# 用户临时说了个新idea？
→ 见 workflows/W_BRAINSTORM_脑暴修正同步.md
```

---

## §1 触发条件

当用户发出以下任一信号时，激活此技能：

| 信号类型 | 示例 |
|---------|------|
| **新建世界** | "我想写一个关于...的小说" / "帮我设计一个世界观" |
| **一致性审查** | "检查一下有没有矛盾" / "这段剧情合理吗" |
| **剧情枚举** | "接下来可以发生什么" / "主角还有别的选择吗" |
| **章节规划** | "这一章怎么安排" / "帮我规划卷结构" |
| **涟漪修复** | "我改了这个设定，会影响什么" |
| **质量评估** | "这段武戏写得好吗" / "情感温度够不够" |
| **设定审查** | "世界观有漏洞吗" / "帮我自检" |
| **审美方向** | "这个场景读起来怎么样" / "节奏对吗" |
| **修订改稿** | "这章重写" / "换一种写法" / "感觉不对" |
| **系统初始化** | "做系统初始化" / "初始化引擎" / "重建基线" |
| **归档吸收** | "吸收到当前项目" / "这些设定是否有必要吸收" / "从底层开始吸收" |

---

## §2 核心工作流 · 螺旋门禁模型

```
┌─────────────────────────────────────────────────────────────────┐
│  P0 沙盒定义 ← 用户种子(梦境/认知/幻想碎片)                       │
│  产出: 宪法公理 + 物理常量 + 势力版图 + 角色种子                    │
│  门禁: 宪法可检测性审查 PASS · 主导: World Architect               │
├─────────────────────────────────────────────────────────────────┤
│  P1 骨架搭建                                                      │
│  产出: 全卷骨架 + 角色弧 + 冲突网络 + 伏笔种子                      │
│  门禁: 角色弧完整性 + 涟漪传播零 BLOCKER · 主导: Plot Orchestrator  │
├─────────────────────────────────────────────────────────────────┤
│  P2 剧情编织                                                      │
│  产出: 章级规划 + 场景分镜 + 可能性枚举                             │
│  门禁: 赢面公式 PASS + 伏笔覆盖度 ≥70%                              │
├─────────────────────────────────────────────────────────────────┤
│  P3 细节降噪                                                      │
│  产出: 场景正文 + 对话 + 描写 · 主导: Scene Composer               │
│  门禁: 六维评估总分 ≥70 + 主题一致性 ≥80                            │
├─────────────────────────────────────────────────────────────────┤
│  P4 全局润色                                                      │
│  产出: 节奏热力图 + 伏笔回收报告 · 主导: Consistency Auditor        │
│  门禁: 伏笔回收率 ≥90% + 无未解决涟漪                                │
└─────────────────────────────────────────────────────────────────┘
```

> **门禁三级制 + Agent 切换协议 + 失败处理** → `references/gate_protocol.md`

---

## §3 文档加载策略（防止上下文腐烂）

> **核心机制**: 只加载当前阶段需要的文档。禁止一次性全吞。

### 按阶段加载

| 当时机 | 加载 | 禁止加载 |
|--------|------|----------|
| Skill 激活时 | 本文档 (§0-§3) + `references/gate_protocol.md` | 不加载 workflows/ |
| 任意阶段·世界观导航 | `../world_index.yaml`（文档索引，由 init_world_index.py 生成） | — |
| 任意阶段·按需加载 | 匹配 `world_index.yaml` 中 `load_on.conditions` 的文档 + 其 `dependencies` 链文档 | 不加载未匹配的文档 |
| P0 沙盒定义 | `workflows/P0_沙盒定义.md` + `agents/world_architect.md` + `references/constitution_guide.md` | 不加载 P1-P4 |
| P1 骨架搭建 | `workflows/P1_骨架搭建.md` + `agents/plot_orchestrator.md` | 不加载 P0/P2-P4 |
| P2 剧情编织 | `workflows/P2_剧情编织.md` + `agents/plot_orchestrator.md` + `references/enumeration_engine.md` | — |
| P3 细节降噪 | `workflows/P3_细节降噪.md` + `agents/scene_composer.md` + 对应模型 reference | — |
| P4 全局润色 | `workflows/P4_全局润色.md` + `agents/consistency_auditor.md` | — |
| 脑暴修正 | `workflows/W_BRAINSTORM_脑暴修正同步.md` | — |
| 归档吸收 | `workflows/W_ARCHIVE_归档材料吸收.md` | — |
| 门禁审查 | `references/gate_protocol.md` + `agents/consistency_auditor.md` | — |
| 改稿/修订 | `workflows/W_REWRITE_改稿.md` 或 `W_REVISION_修订.md` | — |

### 链式思维强制

每个 Agent 在开始工作前必须：
1. 确认当前阶段，加载对应文档
2. 对照 `AGENTS.md` §零 DOC FIRST 铁律 确认文档同步状态
3. 对照 `AGENTS.md` §二·五 任务完成铁律 确认可执行条件
4. 进入下一阶段前完成门禁自检

---

## §4 多 Agent 编排

| Agent | 阶段 | 核心职责 | 调用时机 |
|-------|------|---------|---------|
| **World Architect** | P0 | 宪法设计/物理建模/势力版图/文化层 | 用户提出新世界观 |
| **Plot Orchestrator** | P1-P2 | 骨架搭建/角色弧/冲突网/章节规划 | 骨架设计、剧情枚举 |
| **Scene Composer** | P3 | 场景写作/对话/描写/情感递进 | 写具体场景 |
| **Consistency Auditor** | P0-P4 | 门禁审查/涟漪传播/六维评估/术语合规 | 每个阶段结束时 |
| **Creative Director** | 全局 | 主题一致性/审美方向/节奏把控/最终决策 | 全局审查、方向调整 |

> Agent 定义详见 `agents/` 目录。协作协议 + 切换裁决 → `references/gate_protocol.md`

---

## §5 引擎工具调用速查

| 场景 | 工具 | 参数 | 预期输出 |
|------|------|------|---------|
| 一致性扫描 | `check.py --mode score` | — | 0-100 分 + 分类问题 |
| 涟漪传播 | `ripple.py --change "实体:字段:旧->新"` | 变更描述 | 按严重度分级的受影响实体列表 |
| 可能性枚举 | `enumerate.py --chapter N --count 5` | 章号 | 5 个排序候选 + 评分明细 |
| 六维评估 | `evaluate.py --chapter N --type combat` | 章号 + 类型 | 总分 + 6 维明细 |
| 武戏评分 | `combat_narrative.py --chapter N` | 章号 | 四维分 + 改进建议 |
| 文戏温度 | `drama_narrative.py --chapter N` | 章号 | 温度分 + 组件明细 |
| 主题检查 | `theme_check.py --chapter N` | 章号 | 信号密度 + 偏离报告 |

---

## §6 核心设计原则（AI 必须内化）

### 6.1 艺术种子保护原则
用户的初始灵感（梦境/认知/幻想）是故事 DNA。引擎的职责是保护其光泽，不是"为了合理而合理"。

### 6.2 宪法即类型系统
公理 = TypeScript 类型定义。任何叙事必须在公理的类型边界内。违反 = 编译错误。

### 6.3 涟漪优先于修复
改设定之前，先算影响面。不计算就改 = 制造隐藏的不一致性。

### 6.4 门禁不可跳过
每个阶段的门禁必须 PASS 才能进入下一阶段。跳过门禁 = 技术债务。

### 6.5 引擎建议，作者决策
引擎提供评分、候选、警告。最终选择权永远在作者（用户）手中。

---

## 参考文档索引

| 文档 | 用途 | 何时加载 |
|------|------|----------|
| `references/gate_protocol.md` | 门禁三级制 + Agent 切换协议 + 失败处理 | 门禁审查前 |
| `references/constitution_guide.md` | 宪法公理设计质量检查 | P0 沙盒定义 |
| `references/ripple_engine.md` | 涟漪传播算法 | 任何设定变更时 |
| `references/enumeration_engine.md` | 可能性枚举算法 | P2 剧情编织 |
| `references/six_dim_evaluation.md` | 六维评估引擎 | P3 写作评估 |
| `references/combat_model.md` | 武戏量化模型 | P3 武戏写作 |
| `references/drama_model.md` | 文戏温度模型 | P3 文戏写作 |
| `references/theme_model.md` | 主题一致性检查 | P3 写作评估 |
| `references/config_system.md` | 双层配置体系 (.env/.json) | 需要调整配置时 |
| `../world_index.yaml` | 世界观文档动态索引（自动生成，位于项目根目录） | 任意阶段写作前 |
| `references/architecture.md` | 引擎架构总览 | 首次学习 |
| `references/schema_guide.md` | 数据 Schema 指南 | 索引编制 |

### 脚本文档

| 脚本 | 参考设计 |
|------|---------|
| `check.py` | `references/ripple_engine.md` §评分算法 |
| `ripple.py` | `references/ripple_engine.md` |
| `enumerate.py` | `references/enumeration_engine.md` |
| `evaluate.py` | `references/six_dim_evaluation.md` |
| `combat_narrative.py` | `references/combat_model.md` |
| `drama_narrative.py` | `references/drama_model.md` |
| `theme_check.py` | `references/theme_model.md` |

---

## §7 协议式扩展架构

本 Skill 通过**文件位置约定**实现项目实例化——Skill 定义读取协议，项目在约定路径提供数据。

### check.py 的三层数据源

```
check.py
  │
  ├─ ① S10_概念注册表.yaml  →  项目词典 (废弃术语 + 违规分类 + 严重度)
  │    路径: 创作正文/状态/S10_概念注册表.yaml
  │
  ├─ ② skf.yaml              →  项目配置 (content_root + exclude)
  │    路径: 项目根目录/skf.yaml
  │
  └─ ③ AGENTS.md §八          →  术语红线补充 (纯文本解析)
       路径: 项目根目录/AGENTS.md
```

### 移植到新项目

```
1. 复制 skill-novel-engine/ 到新项目
2. 创建 创作正文/状态/S10_概念注册表.yaml (项目词典)
3. 创建 skf.yaml (content_root + exclude)
4. 创建 AGENTS.md (规则 + 行为锚点)
5. python skill-novel-engine/scripts/check.py --mode score  →  100/100
```

### 世界观文档动态索引

```
创作正文/世界观/           ← 28 份世界观文档（Markdown 权威源）
  │
  └─ skill-novel-engine/scripts/init_world_index.py
       │
       ├─ ① 扫描 创作正文/世界观/ 下所有 .md 文件
       ├─ ② 从 world_index.yaml.example 加载已知文档元数据
       ├─ ③ 对新文档使用关键词启发式推断层级
       └─ ④ 输出 world_index.yaml（四层分类 + 依赖链 + 加载规则）

world_index.yaml
  │
  ├─ layers.foundation    → 底层文档（4份）
  ├─ layers.protocol      → 协议层文档（5份）
  ├─ layers.representation → 表示层文档（12份）
  ├─ layers.session       → 会话层文档（4份）
  ├─ layers.meta_documents → 元文档（2份）
  └─ cross_layer_queries  → 跨层查询模板（6条）
```

---

> **版本**: v2.0 — 薄编排层重构：拆出门禁协议/配置体系为独立参考文档，引入按需加载策略
> **上一版本**: v1.0 — 全量单体 SKILL.md (621行)
