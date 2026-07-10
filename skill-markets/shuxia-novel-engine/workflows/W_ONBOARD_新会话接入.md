# W_ONBOARD · 新AI会话接入

> 场景: 新的AI会话打开这个技能，需要快速建立上下文
> 不同于 SKILL.md §0（技能通用启动），这是"项目内使用技能的启动"

---

## 两步启动

### Step 1: 项目上下文（读 3 个文件）

```
1. 创作正文/状态/S00_项目工作台.md → 项目有什么、当前优先级
2. 创作正文/状态/S01_会话上下文.md → 上轮做了什么、新增体系
3. AGENTS.md → 项目特定规则（宪法/角色锚点/术语红线）
```

### Step 2: 技能上下文（读 1-2 个文件）

```
1. SKILL.md §0-§2 → 快速启动 + 触发条件 + 螺旋门禁
2. 如果你这次要做的事属于某个阶段 → 读对应 workflow/
   例: 要写新章节 → workflows/P3_细节降噪.md
   例: 用户给了个新idea → workflows/W_BRAINSTORM_脑暴修正同步.md
```

## 判断当前阶段

```
┌─ 用户说"帮我设计世界观" → P0 → World Architect
├─ 用户说"帮我规划剧情" → P1-P2 → Plot Orchestrator
├─ 用户说"帮我写这段" → P3 → Scene Composer
├─ 用户说"帮我检查" → 门禁 → Consistency Auditor
├─ 用户说"改一下设定" → W_BRAINSTORM → CD + CA
├─ 用户说"重写这一段" → W_REWRITE → Scene Composer
├─ 用户说"吸收归档" → W_ARCHIVE → CD + CA
├─ 用户说"看全局" → Creative Director
└─ 用户说"我刚写了句，有问题吗" → W_QUICKCHECK
```

## 不需要读的文件

- references/ — 需要实现算法时才读，日常操作不需要
- agents/ — SKILL.md §3 已经有摘要，需要做某个阶段时再读对应的 agent
- research/ — 历史档案，不需要
