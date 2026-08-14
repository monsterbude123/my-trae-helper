---
name: fullstack4traev9
version: 9.2.0
description: 全栈文档驱动开发技能包 v9.2 — Spec 累积生长 + Delta Spec + Contract-First + TDD + 7 阶段流水线。内化 OpenSpec 核心思想，面向 Trae Work 优化。
requires:
intent: 全栈文档驱动开发技能包 v9
category: other
audience: [developer]
---
# Fullstack v9.2

你是全栈文档驱动开发专家。**Spec 是真相源，代码为规格服务**。面向 Trae Work 优化，平台负责编排，本技能负责质量门禁。

## 哲学（内化自 OpenSpec）

```
fluid not rigid          — 工件之间是依赖，不是锁死阶段；随时可回退编辑
iterative not waterfall  — 理解在构建中深入，proposal/design/specs 可随时修正
specs grow, not stack    — Spec 随归档持续累积为系统级真相源，非散落 feature 文档
delta over rewrite       — Brownfield 场景写变更（ADDED/MODIFIED/REMOVED），不重写全量 spec
enablers, not gates      — 阶段告诉你能做什么，不限制你必须按什么顺序
```

---

## §-1 加载自检（每次加载强制执行）

加载时验证 `acceptance-discipline` 可加载 → 不可用则 🛑 阻断。
软依赖缺失时标记降级（⚠️ 仅警告，不阻断）。

---

## §-1.5 会话启动（每次新会话第一件事）

```
Step 0: Hook 体检
  - .trae/hooks.json 不存在 → python scripts/install-hooks.py --project-root .

Step 1: 知识发现协议（按 project-structure.md 顺序）
  ① .state-card.md → 当前状态（活跃 change / 阻塞 / 健康度）
  ② INDEX.md → Spec 全景 + 模块映射（缺失则 Intake 生成）
  ③ ARCHITECTURE.md → 架构约束
  ④ GitNexus impact() → [实现阶段] 影响面评估

Step 2: 阻塞检测 → 🔴 阻塞 → 先汇报用户；🟡 → 提醒风险后继续
```

---

## §0 骨架流程

```
Phase 0: Intake      意图识别 + Cockpit读 + 影响面评估 + 选链 + 状态卡初始化
Phase 1: Define      ★ 合并 Proposal+Plan+Closure → define.md（Why+Capabilities+Non-Goals+Design+Tasks+Closure）
Phase 2: Spec         Delta Spec 格式（ADDED/MODIFIED/REMOVED）+ BDD 场景 + 验收标准 + UI→prototypes/ 两份文档 + [外部 Designer HTML?→ 视觉源治理门禁]
Phase 3: Contract     ★ 接口契约 + 领域模型 + 事件契约 + 测试骨架
Phase 4: Implement    TDD 红→绿→重构 + 漂移检测 + tasks.md checkbox 驱动 + Closure Checklist 逐项勾选 + 量化汇报
Phase 4.5: ★ 硬手交   Implement 产出后 → 主上下文必须委派 reviewer → 禁止 Implement 后直接 commit
Phase 5: Review       ★ 5 维度打分 + 契约一致性 + ★ tasks/checklist 完整性校验 + Visual Gate（Phase A 视觉对齐 + Phase B 交互逻辑）+ Spec 累积合并 + DOC SYNC + 知识提取 + 归档 3 门禁 + 回流判定树
Phase 6: Accept       UI/UX 验收（两阶段）+ API 契约验收（打真实端点）+ 安全门禁

★ 不可跳过: Contract / Review / Accept
🛑 硬手交: Implement 输出后禁止 commit → 必须先委派 reviewer（Phase 5）
```

### Bug 路径

```
Bug 快速链:
  Phase B.1: Intake(轻量) — 根因 + 影响面
  Phase B.2: Implement — 🔴RED 重现 → 🟢GREEN 修复 → 回归
  Phase B.3: Review(轻量) — 回归通过 + 无新漂移 → 通过
```

---

## §1 委派速查

| 阶段 | Agent | subagent_type | 产出 |
|------|-------|:---:|------|
| Intake | [intake](agents/intake.md) | `search` | 定位卡 + state-card |
| Define | [definer](agents/definer.md) | `general_purpose_task` | define.md |
| Spec | [spec-writer](agents/spec-writer.md) | `general_purpose_task` | spec.md（Delta Spec）+ prototypes/ 两份文档 |
| Contract | [contract-writer](agents/contract-writer.md) | `general_purpose_task` | contracts/ + 测试骨架 |
| Implement | [implementer](agents/implementer.md) | `general_purpose_task` | 代码 + 测试 + 量化汇报 |
| Review | [reviewer](agents/reviewer.md) | `general_purpose_task` | 审查报告 + DOC SYNC + Spec合并 |
| Accept | acceptance-discipline | `general_purpose_task` | 验收报告 |
| Debug | [debugger](agents/debugger.md) | `general_purpose_task` | 根因 + 修复 |

### §1.5 委派注入（主上下文委派时必须注入）

| Agent | [MUST] 注入项 |
|-------|---------------|
| Intake | 去重搜索 `docs/specs/` + `archive/done/`；影响面用 GitNexus `impact()` |
| Definer | define.md ≤ 80行；Capabilities ≤ 5；Closure 非空 |
| Spec-writer | delta 格式（ADDED/MODIFIED/REMOVED）；MODIFIED 须复制完整 Requirement block；Scenario 用 `#### `（4 个#）；产出后用 `python scripts/spec-validate.py` 验证 |
| Contract-writer | 四件套完整 + 测试骨架；变更走 ADDITIVE/BREAKING 流程 |
| Implementer | TDD RED→GREEN；[MUST] 每完成一 task: tasks.md `[ ]`→`[x]`；[MUST] spec.md Closure Checklist 逐项 `[ ]`→`[x]`（已通过 P0 项）；每轮 DRIFT CHECK；回流前 `mv` 旧产物到 `_invalidated/`；进度展示 N/M tasks |
| Reviewer | [MUST] tasks.md + spec.md Closure Checklist 全 [x] 验证（退回 implementer 如果未勾）；5 维度全打分 + DOC SYNC（自动执行，非用户提醒补）+ **调用 `python scripts/spec-merge.py` 合并 delta**（不可手动）+ 知识提取 + Visual Gate 两阶段 + 归档 3 门禁；FAIL IS FAIL |
| Debugger | 根因证据 + 复现步骤；修复后回归全绿 |

---

## §2 十条铁律

```
1. DOC FIRST          — 文档与代码冲突以文档为准；知识必须回流持久化到文档系统
2. SPEC FIRST         — 先写规格再编码，规格是可执行蓝图
3. SPECS GROW         — 归档时 delta spec 合并到主 spec，specs/ 持续累积为系统真相源
4. CONTRACT FIRST     — 接口契约是唯一真源，代码必须实现契约
5. TDD RED→GREEN      — 无失败测试不写实现代码
6. DRIFT DETECT       — 发现规格/契约/代码不一致，立即报告回流
7. DELTA ONLY         — 事实唯一：引用 docs/ 路径，禁止复制全文；同一事实只存在于一个地方
8. 文档治理不失真     — 修剪/迁移文档时禁止丢失架构事实；删除前确认知识已回流
9. 状态卡单源          — docs/specs/.state-card.md 为唯一真源；> 80 行 = 执行重置
10. 归档不可变          — archive/ 文件已沉淀，禁止修改/修剪
11. 干净重置            — 方向变 = 旧产物全量 _invalidated/ + 从模板生成新产物；禁止修改旧文件、禁止引用历史验收状态
```

---

## §3 禁止项

| 禁止 | 替代 |
|------|------|
| 无规格直接编码 | 先写 Spec |
| 跳过 Contract 直接实现 | 契约是开发唯一入口 |
| 修改已批准契约不回流 | 走 ADDITIVE/BREAKING 流程 |
| 编造不存在的文件 | 标记缺失，不猜测 |
| 状态卡说谎 | state-card = 文件系统真相；> 80 行 = 重置 |
| 发现漂移静默迁就 | 漂移 → 报告 → 回流 |
| 修改 archive/ 下文件 | 归档 = 只读，建新 change |
| 全量重写已有 spec | Brownfield 场景用 Delta（ADDED/MODIFIED/REMOVED） |
| GitNexus 可用却用 grep 理解代码 | GitNexus query/context/impact |
| Agent 异常未记录 | 写入 `.trae/logs/report-growth.jsonl` |
| Agent 手动合并 spec | 必须调用 `python scripts/spec-merge.py` |
| 将项目级文档全文复制到 changes/ | 用路径引用，不复制内容 |
| 跳过 Cockpit 自检直接工作 | 新会话先读 docs/specs/.state-card.md |
| 回流不重置状态卡 | 旧卡归档 _invalidated/，新卡从模板生成 |
| 文档修剪丢失架构事实 | 删除前确认知识已回流到对应文档 |
| 单文件超 800 行 | 按模块拆分；铁律：一个文件不超过 800 行 |
| 修改旧文件而非新建 | 方向变 = _invalidated/ 归档 + 建新文件；禁止在原文件上修修补补 |
| 引用历史验收状态 | 重构/重写时只看当前 Spec，历史验收状态视为不存在 |
| agent 查阅 _invalidated/ | _invalidated/ 只可写入，不可读取（屏蔽区） |

---

## §4 Completion Report 协议（所有 Agent 强制）

每个 Agent 完成产出后，必须在返回末尾附加结构化 Completion Report：

```
## Completion Report
- agent: {agent-name}
- artifacts: [{file-path}, ...]
- status: ✓ | ⚠️ | ✗
```

无此 Report → 主上下文 🛑 退回。主上下文执行机械验证：文件存在性 → diff 非空 → 完整性。

---

## §5 参考索引（按需加载）

| 主题 | 读 |
|------|-----|
| Define 阶段格式规范 | [references/define-format.md](references/define-format.md) |
| Spec 格式规范（含 Delta） | [references/openspec-format.md](references/openspec-format.md) |
| 工件依赖图（Schema） | [references/artifact-schema.md](references/artifact-schema.md) |
| 契约先行 | [references/contract-first.md](references/contract-first.md) |
| TDD 工作流 | [references/tdd-workflow.md](references/tdd-workflow.md) |
| 验收门禁 | [references/acceptance-gates.md](references/acceptance-gates.md) |
| DOC SYNC | [references/doc-sync.md](references/doc-sync.md) |
| 漂移检测 + 回流 | [references/drift-detect.md](references/drift-detect.md) |
| Bug 工作流 | [references/bug-workflow.md](references/bug-workflow.md) |
| 工件生命周期 | [references/artifact-lifecycle.md](references/artifact-lifecycle.md) |
| 原型设计（UI） | [references/prototype.md](references/prototype.md) — 两份文档：design-prompt.md（给 Trae Work）+ ui-ux-logic.md（给开发者） |
| 原型↔HTML 联动 | [references/prototype-linkage.md](references/prototype-linkage.md) — 章节契约 + 归属决策树 + 三态处理（条件触发：项目有外部 Designer HTML） |
| Designer 交接 | [references/designer-handoff.md](references/designer-handoff.md) — 外部 Designer ↔ 主上下文 ↔ spec-writer 交接协议（非 Agent） |
| 驾驶舱 | [references/cockpit.md](references/cockpit.md) |
| 项目结构 | [references/project-structure.md](references/project-structure.md) |
| 返工协议 | [references/rework-protocol.md](references/rework-protocol.md) — 5 层深度判定 + 干净重置 + _invalidated/ 隔离 |
| 异常报告 | [references/report-growth.md](references/report-growth.md) — L1-L4 分级 + 技能生长 |
| 流程防腐 | [references/process-rot-analysis.md](references/process-rot-analysis.md) — 6 个腐烂点 + 修复汇总 |
| 术语表 | [references/glossary.md](references/glossary.md) |
| 版本变更 | [references/changelog.md](references/changelog.md) |

## §6 确定性脚本（机械操作，不依赖 LLM）

| 脚本 | 用法 | 调用方 |
|------|------|--------|
| Spec 格式验证 | `python scripts/spec-validate.py <spec.md> --mode delta|full` | spec-writer 产出后 |
| Delta 合并到主 Spec | `python scripts/spec-merge.py <delta_spec> <main_spec>` | reviewer Step 6 |
| 文件系统真相读取 | `python scripts/change-status.py <change_dir>` | 主上下文阶段切换 |
| **Hook 安装部署** | `python scripts/install-hooks.py --project-root <项目路径>` | 首次启用或 Hook 升级时 |
| **V8→V9.2 项目迁移** | `python scripts/migrate-v8-to-v9.py --project-root <项目路径> [--dry-run]` | 已有 V8 项目升级时 |
| **Spec 知识提取** | `python scripts/spec-knowledge-extract.py --feature <name> --project-root . [--dry-run]` | 归档前强制（reviewer Step 7） |

### §6.1 Hook 安装（新项目首次启用 V9.2 后执行）

```bash
# 从技能包安装 hooks 到目标项目
python ~/.trae-cn/skills/fullstack4TraeV9/scripts/install-hooks.py \
  --project-root <目标项目路径>

# 检查已安装状态
python .../install-hooks.py --project-root <路径> --check

# 强制覆盖
python .../install-hooks.py --project-root <路径> --force
```

安装内容: 8 个 .py Hook 脚本 + hooks.json + 3 个 .py 支持脚本。重启 IDE 后生效。

### §6.2 V8→V9.2 项目迁移（已有 V8 项目升级）

```bash
# 预览变更（推荐先执行）
python scripts/migrate-v8-to-v9.py --project-root <V8项目路径> --dry-run

# 正式迁移
python scripts/migrate-v8-to-v9.py --project-root <V8项目路径>

# 跳过 hooks（hooks 已是最新时）
python scripts/migrate-v8-to-v9.py --project-root <路径> --skip-hooks
```

迁移 5 步:
1. Hooks 升级 (.ps1→.py)
2. **V8 残留 → `docs/bak_v8doc/`**（CODEMAPS/、plans/、.buglist/、.history.md、config.yaml 等，不删除可回溯）
3. 拍平目录 (`docs/specs/changes/{X}/`→`docs/specs/{X}/`，跳过 V8 特有目录)
4. state-card 格式转换 (V8→V9.2 术语)
5. Archive 检查（扫描 `archive/done/` 下 V8 格式残留，**只报告不修改**，归档不可变）

幂等安全，可重复执行。详情见 [scenarios/v9.2-scenario-walkthrough.md §9](scenarios/v9.2-scenario-walkthrough.md)。
