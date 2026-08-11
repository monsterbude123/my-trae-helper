# 5 种意图类型详解

> Stage -1 Intake 的核心分类。所有用户输入必归类到这 5 种意图之一。

---

## 意图总览

| # | 意图 | 路由目标 | 状态卡类型 | 用户确认 |
|:---:|------|---------|-----------|:---:|
| 1 | **project-init** | Stage 0 Plan → Stage 5 Accept | project | 🛑 |
| 2 | **change-start** (feature/refactor) | Stage 0 Plan → Stage 5 Accept | change | 🛑 |
| 3 | **change-start** (doc-sync) | Stage 1 Spec → Stage 5 Accept (lite) | change | ⚙ |
| 4 | **bug-fix** | Stage 6 Bug Fix（独立支线）| bug | 🛑 |
| 5 | **project-health** | Stage 7 Project Health（异步自检）| project | ⚙ |

---

## 意图 1：project-init（项目 0→1 初始化）

**定义**: 从零开始一个新项目，包含目录结构 + 基础配置文件 + spec 骨架。

**触发词**:
- "初始化" / "新项目" / "项目 0→1"
- "create new project" / "scaffold project"

**典型流程**:
```
Stage -1 Intake → Stage 0 Plan（项目级 plan.md）
  → Stage 1 Spec（项目级 spec.md + 子 spec 骨架）
  → Stage 2 Contract（项目级 contract 骨架）
  → Stage 3 Implement（基础设施代码）
  → Stage 3.5 Real Verify（启动验证）
  → Stage 4 Review
  → Stage 4.5 Rot Scan
  → Stage 5 Accept
```

**状态卡**: project 级（位置 `{project}/.trae/state-card.md`）

**子意图**（可选分类）:
- `cli-tool` — 命令行工具
- `web-app` — Web 应用（含前端 + 后端）
- `tauri-app` — Tauri 桌面应用
- `backend-only` — 纯后端 API 服务
- `library` — 库/包开发

**关键产出**:
- `AGENTS.md` — 项目入口
- `docs/constitution.md` — 项目宪法（可继承 V11 16 Articles）
- `.trae/rules/*.md` — 项目级规则
- `.trae/fullstack4traev11.config.yaml` — stage_config 覆盖

---

## 意图 2：change-start（feature / refactor）

**定义**: 在现有项目上新增功能或重构现有功能。

**触发词**:
- "新需求" / "新增功能" / "加个 X" / "增加 Y 功能"
- "重构" / "改造" / "重新设计" / "优化"

**子意图**:
- `feature` — 新增功能（如"加个用户登录"）
- `refactor` — 重构现有功能（如"把 X 拆成 Y"）
- `enhancement` — 增强现有功能（如"加个筛选"）
- `migration` — 数据迁移 / 版本升级（如"从 V1 升到 V2"）

**典型流程**:
```
Stage -1 Intake → Stage 0 Plan（change 级 plan.md）
  → Stage 0.5 Test Plan（验收维度 → 测试用例）
  → Stage 1 Spec（change 级 spec.md）
  → Stage 1.5 Prototype（如有 UI 改动）
  → Stage 2 Contract（change 级 contracts/）
  → Stage 3 Implement（change 级代码 + 测试）
  → Stage 3.5 Real Verify
  → Stage 4 Review
  → Stage 4.5 Rot Scan
  → Stage 5 Accept
```

**状态卡**: change 级（位置 `docs/specs/changes/{change-id}/.state-card.md`）

**change-id 规则**: `{YYYY-MM-DD}-{slug}`（如 `2026-08-11-add-user-auth`）

**关键产出**:
- `docs/specs/changes/{change-id}/plan.md`
- `docs/specs/changes/{change-id}/spec.md`
- `docs/specs/changes/{change-id}/contracts/`（四件套）
- 代码改动 + 测试 + 模块文档

---

## 意图 3：change-start (doc-sync)（文档同步）

**定义**: 同步文档与代码（drift 修复 / 归档后文档更新 / API 文档增量更新）。

**触发词**:
- "文档同步" / "更新文档" / "同步 spec"
- "doc sync" / "update README"

**典型流程**:
```
Stage -1 Intake → Stage 1 Spec（更新 spec.md）
  → Stage 5 Accept (lite) — 直接归档
  （可选 Stage 2 Contract 增量更新）
```

**状态卡**: change 级

**change-id 规则**: `{YYYY-MM-DD}-doc-sync-{slug}`（如 `2026-08-11-doc-sync-api-ref`）

**关键产出**:
- `docs/specs/changes/{change-id}/spec.md`（更新后的）
- 更新后的 docs/api-endpoints/ / domain-models/ / events/

---

## 意图 4：bug-fix（Bug 修复）

**定义**: 修复用户反馈的 bug（含报错 / 不工作 / 期望不一致）。

**触发词**:
- "报错" / "错误" / "异常" / "不工作" / "失败" / "崩溃"
- "应该出现 X 但出现 Y" / "期望 X 但实际 Y"

**关键判断**: ⚠️ 必须先询问用户"是否作为 bug 单录入？" → 用户同意才创建。

**典型流程**:
```
Stage -1 Intake（Bug 录入 6 字段）
  → Stage 6 Bug Fix（独立支线，含 5 步精简流程）
    → Phase B.0 录入（Intake 已完成）
    → Phase B.1 e2e 先行（必须初始 FAIL）
    → Phase B.2 6 层排查
    → Phase B.3 TDD 修复
    → Phase B.4 回归验证
    → Phase B.5 Bug 单回写 CLOSED
```

**状态卡**: bug 级（位置 `docs/bugs/{bug-id}/.state-card.md`）

**bug-id 规则**: `{module}-{NNN}-{slug}`（如 `settings-009-config-key-case`）

**关键产出**:
- `docs/bugs/{bug-id}.md`（Bug 单）
- `docs/bugs/{bug-id}/.state-card.md`（状态卡）
- 修复代码 + 回归测试
- bug 单 CLOSED 回写

**详细 Bug 录入流程**: [../workflows/bug-intake-flow.md](../workflows/bug-intake-flow.md)
**详细 Bug 状态机**: [bug-state-machine.md](bug-state-machine.md)

---

## 意图 5：project-health（项目健康度自检）

**定义**: 异步自检项目状态（路径一致性 / 目录树 / 版本残留 / 文档同步）。

**触发词**:
- "自检" / "健康度" / "诊断"
- "project health" / "audit"

**特点**: 
- 🔀 独立支线（可与任一 stage 并行）
- ⚙ 非阻塞（异步执行）
- 主上下文不等待结果，可继续其他工作

**典型流程**:
```
Stage -1 Intake → Stage 7 Project Health
  → 4 维度检查（路径一致性 / 目录树 / 版本残留 / 文档同步）
  → 输出: project-health-{date}.md + .json
  → 优先级分级（P0/P1/P2/P3）
  → 用户决定何时修复
```

**状态卡**: project 级（不创建新状态卡，使用现有 project 状态卡，更新 stage）

**关键产出**:
- `project-health-{date}.md`
- `project-health-{date}.json`
- 4 维度检查结果
- 优先级修复列表

---

## 意图识别速查表

| 用户输入示例 | 意图 | 触发词 |
|------------|------|--------|
| "初始化这个项目" | project-init | "初始化" |
| "新增一个用户登录功能" | change-start (feature) | "新增" |
| "重构一下 auth 模块" | change-start (refactor) | "重构" |
| "更新 API 文档" | change-start (doc-sync) | "更新文档" |
| "token 刷新报 500" | bug-fix | "报 500" |
| "不工作" | bug-fix | "不工作" |
| "项目健康度怎么样" | project-health | "健康度" |

---

## 模糊意图处理

当触发词不命中或意图不明确时：

**MUST**: AskUserQuestion（5 种意图选项）→ 用户必选

**NEVER**: 经验主义臆断（违反 Article V GitNexus First 精神 / V10.16 禁止编造抽象理由）

---

## 关联引用

- [SKILL.md](../SKILL.md) — 阶段入口
- [intent-routing.md](../workflows/intent-routing.md) — 意图路由工作流
- [routing-decision-tree.md](routing-decision-tree.md) — 路由决策树
- [bug-state-machine.md](bug-state-machine.md) — Bug 单状态机
- [bug-intake-flow.md](../workflows/bug-intake-flow.md) — Bug 录入工作流
