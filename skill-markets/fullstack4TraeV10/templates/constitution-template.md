# Project Constitution — V10 不可协商原则

> 借鉴 spec-kit Constitution 模式。本文件定义项目级"宪法"，所有 Agent / Spec / Contract / Review 必须遵守。
> 修改本文件需要走 BREAKING 流程（见 §Governance），任何 Article 不可静默删改。

---

## Preamble（前言）

Constitution 是项目的**最高原则集合**，优先级高于：
- 单个 Spec 的需求
- 单个 Agent 的习惯
- 单次任务的"效率权衡"
- "特殊情况下"的灵活处理

任何冲突场景的判定顺序：**Constitution > Spec > Contract > Code > 个人判断**。

---

## Article I — TDD 强制（Test-First, NON-NEGOTIABLE）

**Rationale**: 没有失败测试的"实现"是不可验证的黑盒。V10 满分硬门禁要求代码维度 7/7 勾选，单元测试和 Contract 测试全绿是基础。无 RED 步骤的 GREEN 是伪实现。

**Enforcement**:
- Implementer 编码前必须先写失败测试（🔴 RED 阶段）
- 不允许"先写实现再补测试"或"实现和测试同步写"
- 任何 `implementation` commit 必须在 `test` commit 之后
- 测试覆盖率 < 90% = 维度 1 自动 REJECT

**禁止例外**: 无。Bug 修复亦先写重现测试。

---

## Article II — 满分硬门禁（Full-Score Gate, NON-NEGOTIABLE）

**Rationale**: V9 引入"非阻塞 P1"、"降级验收"等灰色术语导致质量底线失守。V10 取消灰色：满分 = PASS，任一非满分 = 🛑 REJECT 整个 change。

**Enforcement**:
- 验收四维（代码/API/UIUX/边际）任一非满分 → 整个 change REJECT
- N/A 必须在 Plan 阶段显式锁定，Review 阶段不再二次判定
- 不存在"先合并后修补"，修补需要走新 change
- 不存在"非阻塞 P1"分类

**禁止例外**: 无。N/A 已锁定的不适用维度除外。

---

## Article III — 零残留迁移（Zero Residue, NON-NEGOTIABLE）

**Rationale**: 重构留下的 `*.bak` / `*.old` / `~` / `recovered.*` 临时文件是技术债，会在数月后突然"复活"造成事故。V10 要求物理清除而非注释式废弃。

**Enforcement**:
- 重构/迁移后必须无 `*.bak` / `*.old` / `*.recovered` 后缀文件
- 删除必须用物理命令（`git rm`），不靠 `.gitignore` 屏蔽
- 迁移脚本（migrate-*.py）完成后自删除或归档到 `archive/`
- 归档前必须跑 `spec-knowledge-extract.py` 提取知识

**禁止例外**: 无。临时调试脚本若需保留，标记 `ponytail:` 并通过审查。

---

## Article IV — 委派纪律（Delegation Discipline, NON-NEGOTIABLE）

**Rationale**: 主上下文（Coordinator）直接执行代码 = 双重身份冲突——既是裁判又是运动员。V10 强制主上下文只做协调（路由/读结果/状态同步/用户沟通），所有代码/测试/构建委派给 coding agent。

**Enforcement**:
- 主上下文禁止直接 `Read/Write/Edit` 源码文件
- 主上下文禁止直接写 Spec/Plan/Contract
- 主上下文禁止直接跑测试/构建/lint
- 委派 coding agent 必须用 `subagent_type=general_purpose_task`（禁止 `search` —— 无写入工具）
- 委派时必须注入对应 Agent 的 [MUST] 项（见 SKILL.md §1.5）

**禁止例外**: 状态卡更新、用户沟通、门禁判定、调度决策（不可委派的元操作）。

---

## Article V — GitNexus First（Code Intelligence First, NON-NEGOTIABLE）

**Rationale**: grep/glob 是盲人摸象，无法构建调用链和影响面图谱。V10 强制修改前用 GitNexus `impact()`、理解用 `query/context`、提交前用 `detect_changes()`。

**Enforcement**:
- 修改任何函数/类/方法前必须跑 `impact(target, direction="upstream")` 并汇报风险等级
- HIGH/CRITICAL 风险必须停止，汇报用户，等待确认
- 提交前必须跑 `detect_changes()` 确认变更范围
- 3 次 GitNexus 重试失败 → 🛑 汇报用户，禁止降级为 grep
- 跨包依赖必须在 SKILL.md YAML frontmatter 的 `requires` 字段声明

**禁止例外**: 纯文档任务（无代码改动）不强制；纯新文件创建（无既有调用链）简化跑 impact。

---

## Article VI — Ponytail First（Simplest First, NON-NEGOTIABLE）

**Rationale**: 过度工程是 Agent 时代的常见反模式——Agent 倾向于生成"看起来专业"的抽象层，但实际增加了维护成本。V10 强制懒人开发：能不写就不写，能用标准库就不造轮子。

**Enforcement**:
- 决策阶梯（从上往下）：
  1. 能不写吗？→ 删掉
  2. 标准库能做吗？→ 用标准库
  3. 已有模块能做吗？→ 复用
  4. 简单实现能做吗？→ 写
  5. 必须引入新依赖/模式？→ 写注释论证为什么（`ponytail:` 标记）
- 单文件 ≤ 800 行，单函数 ≤ 50 行，圈复杂度 ≤ 15
- 引入新依赖前必须查 `skill-markets/CAPABILITY-MAP.md` 共享能力注册表

**禁止例外**: 性能关键路径可突破，但必须用数据论证。

---

## Article VII — 文档与代码冲突以文档为准（Doc Wins, NON-NEGOTIABLE）

**Rationale**: 文档是"为什么做"的真相源，代码是"如何做"的实现。冲突时通常是代码偏离了设计意图。V10 强制回流而不是"代码改对了就合并"。

**Enforcement**:
- 发现代码与 Spec/Contract 不一致 → 立即回流（drift-detect）
- 不允许"代码改对了，文档后续再补"
- 文档更新必须先于代码合并（DOC SYNC GATE）
- 删除文档段落前必须确认知识已回流到对应文档
- `archive/` 下文件已沉淀，禁止修改（建新 change）

**禁止例外**: 无。紧急 hotfix 可后置文档，但 hotfix commit 必须引用未更新文档路径。

---

## Article VIII — 归档不可变（Archive Immutability, NON-NEGOTIABLE）

**Rationale**: 归档 = 历史快照。修改归档会让"以前发生过什么"变得不可信，未来 review 和事故复盘失去基线。V10 强制归档后只能新建 change 不能改旧。

**Enforcement**:
- `archive/done/` 和 `archive/out/` 下任何文件禁止修改
- 重构/重写时只看当前 Spec，历史视为不存在
- 归档脚本（spec-purge.py / spec-knowledge-extract.py）执行后产出物只读
- Agent 禁止读取 `archive/out/spec-purge/` 中任何文件（噪声屏蔽）

**禁止例外**: 无。即使发现归档中的事实错误，也只能在新 change 中注释"archive/{path} 已被新事实取代"。

---

## Governance（治理）

### 修改流程

Constitution 任何 Article 的修改必须：

1. **提案**: 在新 change 中写明修改 Article 编号、Before/After 对比、影响面评估
2. **GitNexus 验证**: 修改 Article II/V/VII 涉及验收逻辑必须 `impact()` 列出所有受影响的 Agent/Script
3. **用户审批**: Constitution 变更必须用户显式确认（"高风险：影响所有项目行为"）
4. **版本号**: 修改后必须更新 `version` 字段（语义化版本）
5. **影响通知**: CHANGELOG.md 必须记录"Breaking Change to Constitution"

### 合规验证

- 所有 Spec/Contract/Code 评审时，Reviewer 必须勾选"符合 Constitution"（详见 references/acceptance-gates-v10.md）
- 任何 Article 违反 = 整个 change REJECT，无论其他维度是否满分
- 主上下文每阶段切换执行"Constitution Compliance"自检（见 agent-机械验证.md）

### 不可降级条款

以下条款**永不可降级**（即使走修改流程也必须维持底线）：

- TDD 强制（Article I）
- 满分硬门禁（Article II）
- 委派纪律（Article IV）
- GitNexus First（Article V）
- 归档不可变（Article VIII）

**降级禁止**: 任何提案试图废除或弱化上述 5 条 = 🛑 立即拒绝。

---

## Article IX — TDD 即时（Test-Update-Atomic, NON-NEGOTIABLE）

> **V10.4 新增（2026-07-30，腐烂点 12 修复）**

**Rationale**: 改实现不立即同步改测试 = 死测试复活。V10.4 强制改/删组件 → 立即改/删测试,同 PR atomic,禁止"先合实现后续 cleanup"。实战教训: 00-04-system-settings 替代了 SettingsPage,但 SettingsPage.test.tsx + SettingsPage.tsx 都没即时清除,9 failed 测试持续 1 周。

**Enforcement**:
- Implementer 改实现 / 删组件 / 改接口 → 必须在同一 commit 修改对应测试
- Implementer 删除组件文件 → 必须删除对应测试文件(物理删除,非注释)
- Contract-Writer 改契约 → 必须更新 contract test 骨架
- `scripts/orphan-detector.py` 在 Phase 2/3/4.5 必跑,发现孤儿 = 🛑 REJECT

**禁止例外**: 无。"先合实现后续 cleanup" = 禁止模式。

---

## Article X — 异会话验证（Cross-Session Verification, NON-NEGOTIABLE）

> **V10.4 新增（2026-07-30，腐烂点 11 修复）**

**Rationale**: 同 session 自评自签 = 自我背书,无独立验证 = 无意义。V10.4 强制异 session 验证或主上下文二次抽检。实战教训: 主上下文自己当 reviewer,自己写 review-latest.md,自己 PASS,无任何独立验证。

**Enforcement**:
- Reviewer Completion Report 必须含 `session_id` + `self_attested` 字段
- `self_attested: true` 时必须填 `independently_verified_by`(其他 session uuid)
- 主上下文对 self_attested=true 必做二次抽检(独立命令验证至少 1 个核心断言)
- 抽检失败 = 🛑 REJECT

**禁止例外**: 无。异 session 验证是质量底线。

---

## Article XI — 视觉真实验证（Real Visual Verification, NON-NEGOTIABLE）

> **V10.4 新增（2026-07-30，腐烂点 9 修复）**

**Rationale**: PNG magic + 文件大小 = 弱校验,布局错乱也 PASS。V10.4 强制视觉证据 PIL 解码 + 颜色直方图 + 关键区域采样。实战教训: V10.3.9 三层校验全过但实际布局错乱(双齿轮 + TabBar 出现系统设置 + 三层标题)。

**Enforcement**:
- 视觉证据必须 PIL 完整解码(无 truncated)
- 颜色直方图唯一色数 ≥ 50(避免单色破图)
- 关键区域非空采样(避免整页同色/全黑,4 象限亮度极差 ≥ 5)
- 任一不通过 = 🛑 REJECT,不允许 `--no-visual` 绕过

**禁止例外**: 仅当 Plan 阶段显式锁定 uiux 维度为 N/A 时可跳过。

---

**Version**: 1.1.0 | **Ratified**: 2026-07-27 | **Last Amended**: 2026-07-30 (V10.4: +Articles IX/X/XI)
