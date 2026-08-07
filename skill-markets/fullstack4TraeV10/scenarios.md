# V10.9 SDD 场景模拟演练

> **与 V9.2 场景对标**，逐场景展示 V10 流程优化 + 14 Articles 铁律 + 5 阶段硬门禁 + 机械验证协议 + 5 维度腐化扫描 + 项目健康度自检 agent。
>
> **每场景演练起点**：SKILL.md §0.5（V10.9 NEW — Skill 加载协议），主上下文必读 references + Glob 项目惯例。

---

## V10.9 演练边界：Agent vs 脚本

> **关键区分**（V10.9 举一反三）：每个场景中"委派"与"执行脚本"边界明确。

| 类型 | 角色 | 典型用例 | 错误代价 |
|------|------|---------|---------|
| **Agent** | 编排 + 决策 + Completion Report | planner / spec-enhancer / implementer / reviewer / debugger / project-health-auditor | agent 报告需主上下文质疑性验收 |
| **脚本** | 确定性操作 + 返回 JSON | setup-feature.py / spec-merge.py / spec-purge.py / migrate-v9-to-v10 / proactive-scan / rot-detector | 脚本失败 = �� REJECT |

**判别口诀**：
- "这一步需要推理判断吗？" → 是 → Agent
- "这一步是确定性操作吗？" → 是 → 脚本

## 目录

| # | 场景 | 对标 V9.2 | 关键优化 |
|---|------|---------|---------|
| 1 | 项目 0→1 初始化 | 1. 项目 0→1 初始化 | setup-feature.py + 14 Articles 铁律 |
| 2 | 已有代码迷雾消除 | 2. 已有代码迷雾消除 | intake 自主探索 + project-health-auditor 自检 |
| 3 | 新增功能完整链 | 3. 新增功能完整链 | 5 阶段流水线 + 14 Articles + 5 维度硬门禁 |
| 4 | Spec 累积生长 | 4. Spec 累积生长 | rotation 流程 + sessions 控制 |
| 5 | Bug 修复快捷链 | 5. Bug 修复快捷链 | debugger agent + 6 层排查 |
| 6 | 审核不通过返工 | 6. 审核不通过返工 | 腐化扫描 + rot-detector 必跑 |
| 7 | Spec 回流重构 | 7. Spec 回流重构 | _invalidated/ 隔离 + spec-purge |
| 8 | 反复反馈升级 | 8. 反复反馈升级 | clarifier 反模式 + ≥2 轮根因诊断（NEW）|
| 9 | V9.2 项目迁移到 V10.9 | 9. V8→V9.2 迁移 | migrate-v9-to-v10.py 一键迁移 |
| 10 | **项目健康度自检（V10.9 NEW）** | — | project-health-auditor 4 维度检查 |

---

## 场景 1：项目 0→1 初始化

**V9.2 流程**：intake agent 创建 docs/specs/ 目录 + 初始 .state-card.md

**V10.9 流程**：

```
用户: "初始化这个项目"
  ↓
主上下文（必走 §0.5 协议）:
  Step 1: 加载 fullstack4TraeV10 skill
  Step 2: 必读 references/project-structure.md + sub-agent-rules.md + artifact-lifecycle.md + acceptance-gates-v10.md
  Step 3: Glob 项目 docs/ + AGENTS.md（项目惯例勘察）
  Step 4: 检测项目类型（[references/project-health-checklist.md §项目类型判定规则](references/project-health-checklist.md)）:
    - ✅ CLI 项目: 只有 pyproject.toml / Cargo.toml
    - ✅ 全栈项目: package.json + src-tauri/Cargo.toml + tauri.conf.json
    - ✅ 后端项目: src-tauri/Cargo.toml 或 pyproject.toml，无 frontend
    - ✅ 纯前端项目: 只有 package.json
  Step 5: 如有冲突 → 询问用户
  Step 6: 才进入工作模式
  ↓
setup-feature.py 调用模板覆盖机制（3 层栈，V10.9 NEW）:
  Layer 1: resolve_template --type {project_type} --feature 00-01-init-scaffold
    → 查找 templates/init-scaffold/{project_type}.md
  Layer 2: 若项目自定义 templates/init-scaffold/{project_type}.md → 优先使用
  Layer 3: 若项目有 .trae/templates/ → 覆盖项目级
  Layer 4: 终极 fallback → skill 内置模板
  python scripts/setup-feature.py --name 00-01-init-scaffold --print-template-path  # 验证模板覆盖
  ↓
执行脚本 setup-feature.py（确定性脚本，非 agent）:
  python scripts/setup-feature.py --name 00-01-init-scaffold
  → 创建 docs/specs/00-01-init-scaffold/
    ├── spec.md          (含 14 Articles 引言 + 项目类型适配)
    ├── tasks.md
    ├── contracts/
    ├── prototypes/
    └── .state-card.md
  ↓
setup-feature 注入 Article XIV（rot-detector 必跑）:
  → Phase 4.5 必须跑 proactive-scan.py
  → 任一 FAIL = �� REJECT
  ↓
主上下文验证:
  ls docs/specs/00-01-init-scaffold/
  → 全部存在 ✅
  python scripts/setup-feature.py --check-article-xiv  # 验证 Article XIV 已注入
```

**V9.2→V10.9 优化**：

| 项目 | V9.2 | V10.9 |
|------|------|-------|
| 初始化入口 | intake agent | setup-feature.py（确定性脚本） |
| 项目类型检测 | 0 | 4 种类型（CLI/全栈/后端/纯前端）|
| 模板覆盖 | 单一内置 | 3 层栈（项目 > skill > fallback）|
| 铁律 | 软约束 | 14 Articles 不可降级 |
| 自检 | 0 | rot-detector 必跑（Article XIV） |
| 必读清单 | 0 references | §0.5 Skill 加载协议 4 个必读 |

---

## 场景 2：已有代码迷雾消除

**V9.2 流程**：intake agent 探索 src/ → 输出模块边界报告 → 写入 ARCHITECTURE.md

**V10.9 流程**：

```
主上下文（§0.5 已执行）:
  ↓
委派 project-health-auditor（4 维度诊断）:
  python scripts/setup-feature.py --print-template-path  # 验证模板覆盖
  ↓
  委派 exploration-task:
    搜索 agents/project-health-auditor.md
    检 4 维度:
      1. 路径一致性 → docs/constitution.md / docs/ARCHITECTURE.md / docs/INDEX.md 存在性
      2. 目录树完整性 → docs/specs/.state-card.md ≤ 80 行
      3. 版本残留 + 污染 → grep .specify/ / docs/prototypes/ / aigc-desktop-ui.design /
      4. 文档同步机制 → layer: 标签覆盖率 ≥ 80%
  ↓
  输出: docs/reports/project-health-{date}.md + .json
  ↓
主上下文阅读报告 → 决策手动/批量修复
```

**V9.2→V10.9 优化**：

| 项目 | V9.2 | V10.9 |
|------|------|-------|
| 迷雾消除方式 | intake agent 探索 | project-health-auditor 4 维度诊断 |
| 产物 | 模块边界报告 | 结构化报告（md + json） |
| 自动修复 | 无 | 手动（agent 不自动修改） |
| 适用场景 | 全新项目 | 已存在项目自检 |

---

## 场景 3：新增功能完整链（**核心场景**）

**V9.2 流程**：intake → Define → Spec → Contract → Implement → Review

**V10.9 流程**：

```
用户: "增加用户登录功能，支持 JWT + 刷新令牌"
  ↓
主上下文（§0.5 已执行）:
  ↓
Step 1: planner agent
  → 读 state-card.md → 项目当前状态
  → 3 个子代理并行探索:
    - AGENTS.md（项目惯例）
    - docs/specs/changes/（现有命名）
    - GitNexus impact("auth")
  → 产出 plan.md (含追问点)
  ↓
Step 2: spec-enhancer agent
  → 读 plan.md
  → 应用 [clarify-checklist.md §7](references/clarify-checklist.md) 反复返工根因诊断
  → 产出 spec.md（Enhanced Acceptance）
  → 添加 prototypes/ 2 份文档（UI 触发）
  ↓
Step 3: contract-writer agent
  → 读 spec.md + plan.md
  → 产出 contracts/ 四件套 + 测试骨架
  → 实施 Article I TDD 强制（先写测试）
  ↓
Step 4: implementer agent
  → 实施 Article IX TDD 即时（改实现必同步改测试）
  → 实施 Article IV 委派纪律
  → TDD 三步循环 RED → GREEN → REFACTOR
  → 产出 代码 + 测试 + 模块接入文档
  ↓
Step 5: reviewer agent（质疑式验收官）
  → Step -2 验收基准拆解
  → Step -1 4 工件静态一致性分析
  → Step 0 5 维度打分
  → Step 0.5 证据索要（防应付性汇报）
  → Step 1.5 主动证伪
  → Step 5 DOC SYNC
  ↓
★ Phase 4.5 rot-detector 必跑（Article XIV）:
  python scripts/proactive-scan.py
  → FAIL/WARN 必须处理
  ↓
Accept: 归档
```

**V9.2→V10.9 优化**：

| 项目 | V9.2 | V10.9 |
|------|------|-------|
| 阶段数 | 7 | 5 + Phase 4.5 |
| 必读清单 | 0 | §0.5 Skill 加载协议 |
| 铁律 | 软约束 | 14 Articles 不可降级 |
| 腐化扫描 | 0 | Article XIV 必跑 |
| 验收 | 5 维度 | 5 维度 + 质疑式验收 |

---

## 场景 4：Spec 累积生长

**V9.2 流程**：spec-merge.py ADDED/MODIFIED/REMOVED

**V10.9 流程**：

```
主上下文（§0.5 已执行）:
  ↓
触发 implementer agent（轻量 merge 模式）:
  Step 1: 读上一版 spec.md（主 spec）+ 增量 spec.md（Delta）
  Step 2: 内部判定 ADDED/MODIFIED/REMOVED 段
  ↓
implementer agent 委派 spec-merge.py 脚本（确定性合并）:
  python scripts/spec-merge.py \
    docs/specs/{feature}/spec.md \
    docs/specs/{feature}/spec.md
  → 脚本按 Delta 段合并 → 写入主 spec
  → 返回 {"ok": true, "applied": {"added": N, "modified": N, "removed": N}}
  ↓
implementer agent（合并后）:
  Step 3: 检查 `[ ]` 任务是否更新到 .state-card.md
  Step 4: 应用 acceptance-rotate 流程（如 Spec 涉及新增 Acceptance）
  → 触发 reviewer agent 验证 acceptance gate完整性
  Step 5: 触发 spec-purge.py 路径检查（如有旧产物需隔离）
  → 脚本执行 + implementer agent 验证
  ↓
implementer agent → 主上下文 Completion Report
```

**V9.2→V10.9 优化**：

| 项目 | V9.2 | V10.9 |
|------|------|-------|
| 累积合并 | spec-merge.py 脚本 | implementer agent + spec-merge.py |
| 状态卡 | 手动更新 | implementer agent + .state-card.md 同步 |
| 隔离机制 | _invalidated/ | spec-purge.py 自动 |

**关键边界**：
- **脚本**：`spec-merge.py` / `spec-purge.py`（确定性操作）
- **agent**：implementer agent（编排 + 验证 + Completion Report）

---

## 场景 5：Bug 修复快捷链

**V9.2 流程**：intake → debugger → implementer 轻量 → 轻量 review

**V10.9 流程**：

```
用户: "并发刷新 token 时报 500"
  ↓
主上下文（§0.5 已执行）:
  ↓
intake agent:
  Step 1: 意图 = Bug → 路由: debugger agent
  ↓
debugger agent (V10.9 5 步流水 + 6 层排查):
  Step 1: 复现 → docs/bugs/BUG-YYYYMMDD-NNN/reproduction.md
  Step 2: 根因 → root-cause.md
  Step 3: 修复（不直接修改代码，由 implementer 做）
  Step 4: 回归测试
  Step 5: before/after 证据截图 + 报告
  ↓
implementer agent（轻量 TDD RED → GREEN）:
  → 红: test_concurrent_refresh.py → FAIL
  → 绿: 加 SELECT FOR UPDATE → PASS
  ↓
reviewer (轻量):
  → 验证回归 + 无新漂移
  → 通过
  ↓
  ⚠️ Phase 4.5 rot-detector 必跑（Article XIV）
```

**V9.2→V10.9 优化**：

| 项目 | V9.2 | V10.9 |
|------|------|-------|
| Bug 路径 | 3 步 | 5 步（debugger 拆细） |
| 文档 | 0 | docs/bugs/{num}/ + INDEX.md |
| 6 层排查 | 0 | GitNexus First → 6 层逐层排除 |
| 腐化扫描 | 0 | 必跑 |

---

## 场景 6：审核不通过返工

**V9.2 流程**：5 维度打分 → 回流判定树

**V10.9 流程**：

```
reviewer agent (V9.2 流程) + V10.9 增强:
  → 5 维度打分后:
    ├─ 5.0 全满分 → 通过
    ├─ 4.5-4.9 → 警告 → 1 轮回流
    ├─ < 4.5 → �� REJECT → 3 层回流
  → 同步触发 rot-detector:
    ├─ 烂点 16（state-card-staleness）→ 警告
    ├─ 烂点 17（stub-pileup）→ 警告
    └─ 任意 FAIL → �� REJECT
  → 写入 docs/reports/腐化扫描-{date}.md
```

**V9.2→V10.9 优化**：

| 项目 | V9.2 | V10.9 |
|------|------|-------|
| 评分 | 5 维度 | 同 + 满分硬门禁（任何 < 满分算 FAIL） |
| 回流 | 3 层 | 3 层 + rot-detector 联动 |
| 报告 | 1 份 | 2 份（review + rot） |

---

## 场景 7：Spec 回流重构

**V9.2 流程**：implementer → mkdir _invalidated/v1/ → mv 旧产物 → 重新开始

**V10.9 流程**：

```
主上下文（§0.5 已执行）:
  ↓
触发 implementer agent（重构模式）:
  Step R1: 委派 spec-purge.py 脚本（自动隔离）
    python scripts/spec-purge.py --feature {feature}
    → 旧定义/spec/contracts/tasks → docs/archive/done/{feature} 或 archive/out/spec-purge/{feature}-{ts}
    → 脚本更新 INDEX.md
  Step R2: implementer agent 写 REFACTOR_MODE.md（说明 + 禁读 _invalidated/）
  Step R3: implementer agent 重新开始（只读 define.md）
    → 委派 spec-writer agent → spec-validate 验证
    → 委派 contract-writer agent → 测试骨架
    → 委派 implementer agent 主线程 → TDD 重头
  Step R4: 委派 spec-knowledge-extract.py 脚本（归档前合并到项目级知识库）
    python scripts/spec-knowledge-extract.py --feature {feature}
    → 写入 docs/api-endpoints/ + docs/domain-models/ + docs/events/
  ↓
主上下文验收:
  → ls docs/archive/done/{feature}/ → 旧产物完整 ✅
  → ls docs/api-endpoints/ → 知识沉淀 ✅
  → implementer agent Completion Report
```

**V9.2→V10.9 优化**：

| 项目 | V9.2 | V10.9 |
|------|------|-------|
| 隔离 | 手动 mv | spec-purge.py 脚本（implementer 委派）|
| 知识沉淀 | 主 spec | spec-knowledge-extract.py 脚本 |
| 状态卡 | 手动更新 | implementer agent 自动 |
| 文档链 | 重新开始 | spec-writer → contract-writer → implementer |

**关键边界**：
- **脚本**：`spec-purge.py`（隔离）/`spec-knowledge-extract.py`（知识沉淀）/`spec-validate.py`（验证）
- **agent**：implementer agent（编排）/ spec-writer agent / contract-writer agent

---

## 场景 8：反复反馈升级（V10.9 特别强化）

**V9.2 流程**：3 轮反馈 → 演变报告

**V10.9 流程**：

```
触发: 用户对同一类问题反馈 ≥ 2 轮
  ↓
触发 [clarify-checklist.md §7](references/clarify-checklist.md) 反复返工根因诊断协议:
  Step 1: 停止继续返工 — 不再修补当前产物
  Step 2: 列出 N 轮反馈的全部症状
  Step 3: 提炼共同根因
  Step 4: 定位方法论盲区
  Step 5: 沉淀为反向提示词（NEVER + 反例）
  Step 6: 写会话蒸馏报告
  ↓
触发 [SKILL.md §7.5](SKILL.md) AskUserQuestion 反模式检查:
  - 用户没选选项 = 可能在质疑流程本身
  - 正确反应: 停下来承认错误 + 根因分析 + 解决路径
  ↓
触发 [process-rot-analysis.md §5.5](references/process-rot-analysis.md) rot 检测:
  - rot #21: Skill 加载即工作
  - rot #22: ≥2 轮同类返工不诊断
  - rot #23: 委派"完成"未质疑性验收
  ↓
★ 步骤 7: 集中反馈机制（V10.9 NEW — 举一反三）:
  在 6 步根因诊断完成后，触发 session-distiller 集中反馈:
  
  Step 7a: 委派 session-distiller 技能（蒸馏整个会话）:
    Use Skill: session-distiller
    → 接收用户原文 + 决定 + 失真 + 反向提示词
    → 蒸馏出: §0.5 协议 + 4 条 NEVER 反例 + rot #21/22/23
    → 输出: 反馈报告（含失真路径 + 修复建议）
  ↓
  Step 7b: 反馈分层处理（V10.9 内部循环）:
    PFC 内部循环（修复派）:
      - user 反馈 → 提炼规范 → 更新 references/ + SKILL.md
      - 例如: SKILL.md §0.5/§7.5/§0 是 V10.9 反馈的产物
    Skill 升级循环（升级派）:
      - 反馈到技能开发者 → 升级 skill 包
      - 例如: process-rot-analysis.md §5.5 rot #21/22/23 是升级产物
    项目级循环（项目派）:
      - 反馈到项目 .trae/rules/ → 项目级规则
      - 例如: rot-detector 第 8 项 check stub-pileup 是项目腐烂点发现
  ↓
  Step 7c: 闭环验证：
    - 重新跑 4 维度自检 → 失真应消除
    - 重新演练 scenarios → 通过
    - 重新跑 proactive-scan.py → 不再 WARN
  ↓
★ 防止失真的 4 大机制（V10.9 核心）:
  1. §0.5 Skill 加载协议
  2. §7.5 AskUserQuestion 反模式
  3. clarify-checklist.md §7 反复返工根因诊断
  4. process-rot-analysis.md §5.5 rot #21/22/23
  →
  加上 集中反馈机制（Step 7），成为 V10.9 第 5 大防失真机制
```

**V9.2→V10.9 优化**：

| 项目 | V9.2 | V10.9 |
|------|------|-------|
| 反馈机制 | 演变报告 | 根因诊断协议 + 反向提示词 |
| rot 项 | 0 | 3 项（rot #21/22/23） |
| 蒸馏 | 0 | session-distiller 反馈 |

---

## 场景 9：V9.2 项目迁移到 V10.9（**新增**）

**策略**：V9.2 残留 → `docs/bak_v9doc/`（不删除可回溯），只迁移 V10.9 关心的内容。

**场景**：已有 V9.2 项目使用了一段时间。

```
主上下文（§0.5 已执行）:
  ↓
Step 0: 项目类型判定（[references/project-health-checklist.md §项目类型判定规则](references/project-health-checklist.md)）:
  ls pyproject.toml Cargo.toml package.json tauri.conf.json 2>/dev/null
  → 判定 为: CLI / 全栈 / 后端 / 纯前端
  → 迁移策略随项目类型调整:
    - CLI 项目: 跳过后端/API 契约迁移
    - 全栈项目: 全量迁移 + src-tauri/ 适配
    - 后端项目: 重点迁移 API 契约 + domain models
    - 纯前端项目: 跳过 prototype-code-gap-analysis，迁移 components
  ↓
执行迁移脚本（确定性脚本，非 agent）:
  python scripts/migrate-v9-to-v10.py --project-root . --project-type {type} --dry-run

  输出:
    V9.2 → V10.9 迁移 (DRY-RUN)
    项目: <project-root>
    类型: {project_type}

    ## Step 1 — V9.2 残留 → bak_v9doc/
      - V8 格式残留迁移到位
      - V9.2 特有工件归档

    ## Step 2 — constitution 迁移
      - 合并到 14 Articles
      - 移除 V9.2 旧措辞

    ## Step 3 — 14 Articles 升级
      - Article XIV rot-detector 必跑（新增）

    ## Step 4 — 文档 layer 标签化
      - 添加 frontmatter layer: fact/process/log

    ## Step 5 — Archive 检查
      - archive/done/ 只读，不修改

    ## Step 6 — 项目类型适配（V10.9 NEW）
      - 根据判定类型跳过/包含特定迁移
      - 报告: type-adaptive-migration.json

确认无误后正式执行:
  python scripts/migrate-v9-to-v10.py --project-root . --project-type {type}

  输出:
    V9.2 → V10.9 迁移完成
    下一步:
      1. 验证 docs/constitution.md 含 14 Articles
      2. 运行 project-health-auditor 4 维度自检（含项目类型维度）
      3. 触发 Phase 4.5 rot-detector
```

**迁移后项目结构**：

```
docs/
  bak_v9doc/                   ← V9.2 残留归档
  archive/done/                ← 只读归档
  constitution.md              ← V10 必填（14 Articles）
  ARCHITECTURE.md / INDEX.md
  specs/
    .state-card.md             ≤ 80 行
    {feature}/
      spec.md / tasks.md / contracts/ / prototypes/
  modules/
  reports/
.trae/
  hooks/                       ← V10 8 个 .py hook
  hooks.json
  logs/
```

---

## 场景 10：项目健康度自检（V10.9 NEW）

**场景**：用户怀疑项目滞后或要做迁移。

**V10.9 流程**：

```
用户: "自检项目"
  ↓
主上下文（§0.5 已执行）:
  Step 1: 加载 V10.9 skill
  Step 2: 触发 §1 委派速查表 → Project Health | project-health-auditor
  ↓
Step 2: 委派 project-health-auditor (search):
  → 读 references/project-health-checklist.md
  → Step 1: 项目类型判定（CLI/全栈/后端/纯前端）
  → Step 2: 4 维度检查
  → Step 3: 输出 doc/reports/project-health-{date}.md + .json
  ↓
Step 3: 主上下文审计报告
  → 优先级分级:
    P0: 立即修复（如无 docs/constitution.md）
    P1: 近期修复（如 layer 标签覆盖率 < 80%）
    P2: 可延后
  ↓
Step 4: 手动修正（不自动）
```

**V10.9 独有**：这是 V10.9 唯一一个**主动反失真**机制。

---

## V9.2 → V10.9 优化总览

```
                   V9.2                   V10.9
                  ─────                  ─────
阶段数              7                    5 + Phase 4.5
Article 铁律        软约束               14 Articles 不可降级
腐化扫描            0                     8 项 check
文档同步            1 层                  3 层（layer 标签 + 白名单 + 索引器）
Skill 加载协议      无                    §0.5 必读清单
腐化检测 agent      无                    rot-detector（Article XIV）
项目健康度自检       无                    project-health-auditor（4 维度）
反向提示词          无                    4 条 NEVER（rot #21/22/23）
```

### 核心变化一句话

```
V9.2: "真相源是 spec，文档同步是回流"
V10.9: "真相源是 spec + 14 Articles 不可降级 + 腐化是可检测的"
```

---

## 防止失真的 4 大机制（V10.9 核心）

1. **§0.5 Skill 加载协议** — 主上下文必读 4 references + Glob 项目惯例
2. **§7.5 AskUserQuestion 反模式** — 用户没选选项 = 可能在质疑流程
3. **clarify-checklist.md §7** — ≥2 轮同类问题必触发根因诊断
4. **process-rot-analysis.md §5.5** — rot #21/22/23 三类代理腐烂检测

---

> 基于 V9.2 `sc