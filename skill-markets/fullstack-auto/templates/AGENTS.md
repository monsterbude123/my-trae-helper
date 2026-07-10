# AGENTS

本项目集成四个技能包：**coding-xinfa**（通用编码心法，宪法层）、**fullstack**（DOC FIRST + Contract-First + Spec-Driven + TDD + Prototype-First 五位一体）、**GitNexus**（代码智能）、**ponytail**（反过度工程）。

> coding-xinfa 是宪法层，所有 Agent 在任何阶段都遵循其完成审计协议。goal-mode 是其严格执法模式（`/goal` 触发）。
> 涉及 UI 时 spec-writer 额外产出原型文档，让前端实现"看图说话"而非"凭空猜测"。

---

## 自动加载决策链

```
用户需求
  │
  ├── /goal / 目标追逐 / 严格验收 → goal-mode（严格执法模式）
  │     ├── 三大铁律：NO DONE WITHOUT AUDIT / NO BLOCKED BEFORE 3 / EVIDENCE > MEMORY
  │     └── 六步审计门禁：DERIVE → PRESERVE → IDENTIFY → INSPECT → JUDGE → PROVE
  │
  ├── 简单 bug/调样式/实验原型 → ponytail（轻量快车道）
  │
  ├── 涉及 spec/contract/design/plan 等文档化需求 → fullstack（DOC FIRST 流水线）
  │     ├── 涉及 Reasonix 原生代码？→ 先查 `docs/analyze/CAPABILITY_INDEX.md`，禁止凭记忆
  │     └── 涉及 Git 操作？→ 提示用户手动操作，AI 不 commit
  │
  ├── 理解代码/找符号/查调用链/评估影响面 → GitNexus ONLY（禁止 grep 理解代码）
  │     └── 失败 → 重试 3 次 → 仍失败 → 汇报用户。禁止降级为 grep/glob
  │
  ├── "帮我分析这段代码" / "这个 bug 在哪" → Intake: gitnexus_impact() → debugger
  │     └── 无 spec 但有明确目标 → 简化 debug 流程，不启动 fullstack 全流程
  │
  ├── /task 或 "拆任务" → 仅跑 planner，产出 tasks.md
  │
  ├── "跑测试" / "运行" → 专注执行 + E2E 验证 + 报告
  │
  ├── /doc 或 "整理文档" → doc-updater
  │
  └── "讨论架构" / "技术选型" → 圆桌会议 → planner
```

---

## 技能包速查

### coding-xinfa（通用编码心法 — 宪法层）

> 所有 Agent 在任何阶段都必须遵循的基础协议。凌驾 fullstack / ponytail / GitNexus。

| 协议 | 内容 |
|------|------|
| **§1 Goal Mode 协议** | DERIVE → PRESERVE → IDENTIFY → INSPECT → JUDGE → PROVE（六步完成审计） |
| **§2 阻塞处理** | 同一障碍连续 3 turn 才标记 BLOCKED，不得提前放弃 |
| **§3 表达风格** | 简洁、证据驱动、不猜测。`EVIDENCE > MEMORY`（文件系统是唯一权威） |

**完成审计协议（任何 Agent 声称"完成"时触发）：**

```
1. DERIVE   → 从目标中提取所有具体需求（编号项/产物文件/命令/测试/门禁）
2. PRESERVE → 保持原始范围，不以"已有工作"重新定义成功
3. IDENTIFY → 对每项需求，确定能证明其完成的权威证据类型
4. INSPECT  → 逐项运行验证命令（新鲜运行，禁止缓存/历史结果）
5. JUDGE    → 逐项判定 ✅完成 / ❌矛盾 / ⚠️不完整 / ❓太弱 / 🚫缺失
6. PROVE    → 全部✅才算完成。任一失败 → 回到工作，不得说"部分完成"
```

**证据强度判定：**

| 证据类型 | 强度 | 判定 |
|----------|------|------|
| 针对该需求的测试全部通过 | 强 | ✅ 可靠 |
| 命令输出/运行时行为 | 中 | ✅ 有效 |
| 文件存在 + 内容正确 | 中 | ✅ 有效 |
| 同类需求的其他测试通过 | 弱 | ❓ 不确定 |
| 代码看起来正确 | 无 | 🚫 不是证据 |

### goal-mode（严格执法模式）

> 触发词：`/goal` `目标追逐` `严格验收` `不准偷懒` `进入目标模式`

| 规则 | 内容 |
|------|------|
| **三大铁律** | ① NO DONE WITHOUT AUDIT — 未经六步审计不得声称完成 ② NO BLOCKED BEFORE 3 — 同一障碍连续 3 turn 才标记阻塞 ③ EVIDENCE > MEMORY — 文件系统是唯一权威，历史对话不是 |
| **十大禁止** | 不得说"应该可以了""改动很小不用验"；不得缩小目标范围；不得跳过审计任一步骤；不得用缓存结果替代新鲜运行；不得在含多子任务时只完成部分就声称完成 |

**goal-mode 与 fullstack 的关系：**
- goal-mode 激活时，fullstack 各 Agent 的 AOP 自检升级为六步审计门禁
- 审计 PASS → 允许阶段移交；审计 FAIL → 回到工作，禁止移交
- fullstack 的量化验收（7 维度打分卡）不受影响，goal-mode 只管"是否真的完成了"

### Agent 产出表 — fullstack + coding-xinfa 激活时

> **Agent 协调协议**：主上下文只协调不执行。所有执行通过 Task 委派子代理。详见 `.trae/rules/agent协调协议.md`。

| Agent | 触发条件 | 输入 | 输出 |
|-------|---------|------|------|
| [intake](agents/intake.md) | 任何需求 | 用户描述 + 项目上下文 | 流程定位卡 + 影响面清单 + .state-card.md |
| [proposal-writer](agents/proposal-writer.md) | intake approved | 定位卡 + spec backlog | proposal.md |
| [spec-writer](agents/spec-writer.md) | proposal approved | proposal.md | spec.md + E2E 场景 + prototypes/（涉及 UI 时） |
| [contract-writer](agents/contract-writer.md) | spec approved | spec.md + prototypes/ | contracts/（4 文件）+ contract test 骨架 |
| [doc-updater](agents/doc-updater.md) | 文档触发 + 阶段切换自动触发 | 当前 change 工件 + 模块文档 | DOC SYNC 审计表 + 模块文档更新 |
| [planner](agents/planner.md) | contracts/ approved | contracts/ | design.md + tasks.md |
| [implementer](agents/implementer.md) | tasks.md confirmed | design.md + contracts/ + intake 影响面 | TDD 实现 + 量化汇报 |
| [reviewer](agents/reviewer.md) | implementer 完成 | 代码 + 测试 + 契约 | 7 维度打分卡 + 验收通过/驳回 |
| [acceptance](agents/acceptance.md) | reviewer approved | 全部工件 | E2E + 性能 + 安全验收 |
| [debugger](agents/debugger.md) | Bug 发现 | 复现步骤 + gitnexus context | 根因分析 + TDD 修复 |
| [report-growth](agents/report-growth.md) | 随时触发 | 磕绊/打断/报错/流程优化建议 | report-{0X}.md |

### GitNexus（代码智能）

> 代码分析唯一通道：**GITNEXUS FIRST. GREP NEVER.**
> 详见 `.trae/rules/gitnexus-铁律.md`。

| 操作 | 工具 | 场景 |
|------|------|------|
| 理解代码 | `query` | 功能/概念/流程 |
| 看调用者 | `context` | 符号 360 视图 |
| 评估影响 | `impact` | 修改前必跑 |
| 提交前确认 | `detect_changes` | 阻止意外变更 |

### ponytail（反过度工程）

> 轻量快车道。触发：简单 bug/样式调整/实验原型。详见 skill 文档。

| 阶段 | 关键动作 |
|------|---------|
| 1 能不写吗 | 删掉 |
| 2 标准库能做吗 | 用标准库 |
| 3 已有的能做吗 | 复用 |
| 4 简单实现能做吗 | 写 |
| 5 必须引入新 | 写注释论证 |

---

## 集成门禁（阶段流转规则）

> 当 coding-xinfa 的 Goal Mode 激活时，以下门禁强制执行。未通过 → 🛑 不可进入下一阶段。

### 阶段 -1（任何 Agent 声称"完成"前）
- [ ] ❓ coding-xinfa 六步完成审计 DERIVE→PRESERVE→IDENTIFY→INSPECT→JUDGE→PROVE

### 阶段 0（Intake）
- [ ] ❓ coding-xinfa 完成审计（PROVE：所有需求项有证据）
- [ ] 流程定位卡已输出 + 状态卡已初始化 + 影响面清单已评估

### 阶段 1（Proposal + Spec + Contract）
- [ ] proposal.md：Why + What + Capabilities + Non-Goals 完整体现
- [ ] 涉及 UI → prototypes/ 目录完整（README + 各模块 .md）
- [ ] Spec 已 approved
- [ ] contracts/ 4 文件就位 + contract test 骨架
- [ ] 文档同步度自检完成（哪些文档需要同步、是否已同步）

### 阶段 2（Plan + Implement）
- [ ] DOC SYNC GATE ✅ 通过 — 模块文档 + 产品文档已同步
- [ ] CONTRACT GATE ✅ 通过 — 契约 approved + contract test 就绪
- [ ] TDD：🟡CONTRACT TEST → 🔴RED → 🟢GREEN → 🔍DRIFT CHECK
- [ ] 类型检查 0 errors + 覆盖率 > 80%
- [ ] 量化汇报完整（4 维度自评 + 证据）
- [ ] P0 文档已同步

### 阶段 3（Review + Accept）
- [ ] 7 维度打分卡 ≥ 4.0（安全 ≥ 4.0 一票否决）
- [ ] 契约漂移无严重 + 目标对齐 ≥ 90%
- [ ] E2E + 性能 + 安全验收通过
- [ ] 涉及 UI → 原型 vs 实现一致性：布局❓/交互❓/状态❓/字段❓

---

## 七条元铁律

```
0. NO CLAIM WITHOUT AUDIT                — 任何 Agent 声称"完成"前必须走 coding-xinfa 六步审计（DERIVE→PRESERVE→IDENTIFY→INSPECT→JUDGE→PROVE）。全部✅才算完成。
1. NO CODE WITHOUT IMPACT ANALYSIS     — GitNexus impact() 输出前不编辑
2. NO CODE WITHOUT INTAKE              — intake 流程定位卡输出前不进 proposal
3. NO CODE WITHOUT CONTRACT + SPEC + TDD — 契约 approved + RED 确认前不实现
4. NO APPROVAL WITHOUT QUANTITATIVE SCORE — 7 维度打分卡 ≥ 4.0 才批准
5. NO CODE WITHOUT SIMPLICITY CHECK     — Ponytail 审查通过前不提交
6. NO UI CODE WITHOUT PROTOTYPE        — 涉及 UI 时原型 approved 前不写前端代码
7. NO PHASE TRANSITION WITHOUT DOC SYNC — spec+contract+前端设计 敲定后 / 代码实现后，模块文档 + 产品文档 + 前端设计文档 + 契约文档必须同步才进入下一阶段。禁止猴子掰包谷：知识不能只留在 specs/changes/ 施工图纸里，必须回流到持久化文档
```

---

## 状态卡机制

每个变更目录维护 `.state-card.md`，6 段格式：
- 基本信息（变更名/创建日期/当前阶段）
- 工件进度（proposal/spec/原型/contract/design/tasks/code/review 各项 ✅⏳❌—）
- **文档同步度**（涉及的模块文档 + 产品文档 + 前端设计文档 + 契约文档是否已同步：✅ 已同步 / ⏳ 待同步 / ❌ 缺失）
- 健康度（🟢🟡🔴）
- 下一步（加载哪个 Agent）
- 阻塞（如有）

SessionStart Hook 自动注入状态卡，AI 启动时立即知道自己在哪一步。

---

## 量化验收

reviewer 用 7 维度加权打分卡替代凭直觉审查：

| 维度 | 权重 | 不达标 |
|------|------|--------|
| Spec 对齐 | 20% | < 3.0 不交付 |
| 契约一致 | 20% | < 3.0 不交付 |
| 测试质量 | 20% | < 3.0 不交付 |
| 代码质量 | 15% | < 3.0 不交付 |
| 文档一致 | 10% | < 3.0 不交付 |
| 安全 | 10% | < 4.0 一票否决 |
| 影响面处理 | 5% | < 3.0 不交付 |

**总分 < 4.0 不交付。安全 < 4.0 一票否决。**

implementer 完成时必须输出量化汇报（4 维度自评 + 证据 + 测试结果 + 影响面对照表 + 契约漂移自检），reviewer 不信自评，独立验证重新打分。


#### 禁止行为

- ❌ 绝不跳过 `impact` 分析直接编辑任何符号
- ❌ 绝不忽略 HIGH 或 CRITICAL 风险警告
- ❌ 绝不使用 find-and-replace 重命名符号
- ❌ 绝不 commit 前不运行 `detect_changes`
- ❌ 绝不在索引过期时使用过期数据做决策 

- ❌ 不要使用 `import *`
- ❌ 不要在 SKILL.md 中硬编码路径
- ❌ 不要使用 `except: pass`
- ❌ 单文件不超过 500 行
- ❌ 字符串拼接不要用 `+=`（用 list+join）

#### coding-xinfa 通用禁止（所有 Agent）
- ❌ 声称"应该可以了""看起来没问题""应该完成了"——没有"应该"，只有"已验证"
- ❌ 以"改动很小"为由跳过验证——小改动 = 大盲区
- ❌ 缩小目标范围以适应"已完成的部分"——不允许重新定义成功
- ❌ 用历史对话/记忆替代当前文件系统状态检查
- ❌ 运行了验证命令但未阅读输出——未读输出 = 未运行

#### goal-mode 激活时额外禁止
- ❌ 跳过审计任一步骤（DERIVE → PRESERVE → IDENTIFY → INSPECT → JUDGE → PROVE）
- ❌ 在含多子任务时只完成部分就声称"完成"
- ❌ 因"太慢/太麻烦"而使用缓存结果替代新鲜运行
- ❌ 用更简单/兼容的替代方案偷换原始目标

---

## 项目专属配置区

> ⚠️ **以下内容需按项目实际情况填写。删除不需要的段落，保留与项目相关的。**

### 项目核心思想

<!-- TODO: 填写项目一句话核心思想 -->
<!-- 例如：引擎式驱动亚文化规则，编排角色剧情发展 -->

### 技术栈

<!-- TODO: 填写技术栈 -->
<!-- 例如：Python 3.13 + React + TypeScript + SQLite -->

### 项目专属约束

<!-- TODO: 填写项目特有的硬约束（架构约束/集成方式/命名规范等） -->
<!-- 例如：-->
<!-- - EXTEND NOT REPLACE — 本项目是 XX 平台的扩展，不允许替换原生 UI -->
<!-- - 组件 MUST 在指定容器中渲染 -->
<!-- - 禁止绕过项目自有抽象直接调底层 -->

### 项目专属禁止行为

<!-- TODO: 填写项目特有的禁止行为 -->
<!-- 例如：-->
<!-- - ❌ 不要修改 XX 组件的渲染逻辑 -->
<!-- - ❌ 不要在 XX 层持久化状态 -->
<!-- - ❌ 不要让 A 绕过 B 直接与 C 通信 -->

### 模块文档（docs/modules/）

<!-- TODO: 列出项目模块文档 -->
<!-- 例如：-->
<!-- | 领域 | 文件数 | 文件 | -->
<!-- |------|:---:|------| -->
<!-- | 代码参考 | 2 | x-refs.md, y-refs.md | -->

### 当前项目状态

<!-- TODO: 维护当前活跃变更和已归档项 -->
<!-- 例如：-->
<!-- | 变更 | 阶段 | 说明 | -->
<!-- |------|:---:|------| -->
<!-- | 01-xxx | code | 描述 | -->
<!-- 已归档：docs/archive/ -->

### 废弃目录

<!-- TODO: 列出禁止 Agent 执行的废弃目录 -->
<!-- | 目录 | 状态 | 说明 | -->
<!-- |------|:---:|------| -->
