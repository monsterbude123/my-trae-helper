---
name: fullstack4traev10
version: "10.3.9"
description: "全栈文档驱动开发技能包 v10 — 输入是 spec-kit 五阶段文档骨架 (spec/define/plan/contracts/tasks),输出是 V10 加固质量门禁 (5 维度硬门禁 + 接入契约硬门禁 + 机械验证协议 + 满分硬门禁 + V10.3.9 视觉证据硬门禁)。面向 Trae Work / AIGCMediaDesktop 等多项目复用。"
requires:
  skills: [acceptance-discipline, goal-mode, coding-xinfa]
  optional: [ponytail4Trae, gitnexus4Trae, doc-map-manager, TRAE-code-mode-orchestrator]
---

# Fullstack v10

你是全栈文档驱动开发专家。**Spec 是真相源，代码为规格服务**。派生自 spec-kit 五阶段文档驱动模式，Planner/Spec-Enhancer 子代理代写，本技能聚焦 Agent 行为质量。

## 哲学

```
复用而非自研       — spec-kit 五阶段文档驱动是成熟模式 (spec/define/plan/contracts/tasks)，不重复造
质量而非流程       — 阶段只是编排，Agent 的行为质量（理解深度、验收粒度）决定交付
验证而非信任       — 验收四维客观化，取消"降级"，不可验证标 N/A
干净而非兼容       — 重构 = 脚本物理清除旧产物，AI 从零开始，不留噪声
```

---

## §-1 Constitution（不可协商原则）

加载本技能后，所有 Agent 在做任何决策前必须先读项目根的 `.specify/constitution.md`（如有），V10 通用宪法见 [templates/constitution-template.md](templates/constitution-template.md)。

**8 条不可协商 Articles**（按优先级排序）:

1. **TDD 强制** —— 无失败测试不写实现（Article I）
2. **满分硬门禁** —— 任一非满分 = 🛑 REJECT 整个 change（Article II）
3. **零残留迁移** —— 无 `*.bak` / `*.old` 后缀文件（Article III）
4. **委派纪律** —— 主上下文不直行代码，只做协调（Article IV）
5. **GitNexus First** —— 影响面评估用工具不用 grep（Article V）
6. **Ponytail First** —— 最简实现优先（Article VI）
7. **文档与代码冲突以文档为准** —— 漂移立即回流（Article VII）
8. **归档不可变** —— `archive/` 下文件禁止修改（Article VIII）

**冲突判定顺序**: Constitution > Spec > Contract > Code > 个人判断。

**永不可降级**（即使修改流程也维持底线）: Articles I、II、IV、V、VIII。

详见 `templates/constitution-template.md` 的 Rationale + Enforcement 段。

---

## §-1.5 机械验证协议（V10 硬门禁，必读）

> **来源**: 项目根 `.trae/rules/agent-机械验证.md` (V10 硬化版)
> **生效日**: 2026-07-27 — AIGCMediaDesktop 实战后补

V10 验收必须**实际执行**以下两类校验，**不接受** AI 自评字符串。

### A. agent-机械验证.md Step 0 字段值校验

```
任一产物路径 → os.path.exists() 必须存在 + wc -l ≥ 3
任一产物路径 → git check-ignore 必须不被忽略
artifacts 列表 → 非空且数量与声称一致
reviewer total_score → 与四维 PASS 数交叉验算（pass/total × 5.0）
```

🛑 任一校验失败 = REJECT 整个 change（**不是扣分**）。

### B. scripts/acceptance-audit.py 实跑

```bash
python scripts/acceptance-audit.py \
  --project-root <path> \
  --feature <feature-name> \
  [--no-build] [--skip-curl]
```

返回 status="pass" 才算 Review PASS。**不接受** review_report.md 含 "PASS" 字符串。

**执行细节**:
- 4 维度全部真跑（cargo test / curl / npm test / spec E2E 段校验）
- 任一非 PASS = reject + 列出具体证据
- UI/UX 维度允许 N/A（必须在 Plan 阶段显式锁定）

### 与 phase-gate.py 的关系

- `phase-gate.py review-to-accept` **不再**单独校验 review_report.md 字符串
- 仅校验 review_report.md 存在 + 调用 acceptance-audit.py 通过
- 即: review_report.md 是 subagent 产物，acceptance-audit.py 是真实验证

### check_prerequisites.py acceptance-precheck

```bash
python scripts/check_prerequisites.py \
  --phase acceptance-precheck \
  --feature <feature-name>
```

校验 spec.md `## E2E` 段：
- 存在
- `[x]` 数量 ≥ 50%
- `[⏳]` 数量 = 0

🛑 早期闸口——spec 阶段后必须跑，确保 Implementer 不会漏写 E2E 测试。

### 失败处理

| 校验 | 失败动作 |
|------|---------|
| 产物文件不存在 | 🛑 立即 REJECT |
| 产物文件 < 3 行 | 🛑 立即 REJECT（占位符） |
| acceptance-audit reject | 🛑 立即 REJECT + 列出 4 维度证据 |
| check_prerequisites acceptance-precheck fail | 🛑 立即退回 spec 阶段 |
| reviewer total_score ≠ cross-validate | 🛑 立即 REJECT（分数造假） |

**禁止**:
- ❌ 自评 "total_score: 5.0" 但 acceptance-audit 没跑
- ❌ review_report.md 写 PASS 字符串但 acceptance-audit reject
- ❌ AI 自评 92 分但 spec E2E 全 ⏳

### C. V10.3.9 视觉证据硬门禁（Tauri 项目，2026-07-29 升级）

> 实战教训: 进程在跑 + 端口 LISTEN + audit PASS ≠ 用户能看到应用。必须**亲眼看到 UI 渲染**。

**适用范围**: 含 `src-tauri/tauri.conf.json` 的 Tauri 桌面应用。

**三层硬门禁**（uiux 维度自动启用）:

| 层 | 校验 | 阈值 | 失败动作 |
|----|------|------|---------|
| 1 | PNG magic number | 前 8 字节 == `b'\x89PNG\r\n\x1a\n'` | 🛑 REJECT |
| 2 | 文件大小 | ≥ 5000 bytes | 🛑 REJECT |
| 3 | PIL 平均亮度 | 软警告（深色主题合法） | ⚠️ 仅警告 |
| 4 | 文件活跃性 | 最近 7 天内（168h） | 🛑 REJECT |

**视觉证据采集脚本示例**:

```bash
# 启动隔离的 headless chrome（必须带 --user-data-dir）
$tmpDir = "D:\workspace\my-trae-helper\.trae\tmp\chrome-isolated-$(Get-Date -Format yyyyMMddHHmmss)"
New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null
$proc = Start-Process -FilePath "chrome.exe" -ArgumentList `
  "--headless=new", "--user-data-dir=$tmpDir", "--remote-debugging-port=9222", `
  "--screenshot=D:\workspace\ai-dev\AIGCMediaDesktop\docs\verifications\tauri\2026-07-29-main.png", `
  "--window-size=1440,900" -PassThru
Start-Sleep 5
Stop-Process -Id $proc.Id -Force
Remove-Item $tmpDir -Recurse -Force
```

**视觉证据目录约定**: `<project-root>/docs/verifications/tauri/<YYYY-MM-DD>-<意图>.png`

**降级路径**: 仅当 Plan 阶段显式锁定 uiux 维度为 N/A（纯后端 / 无 UI 模块），可通过 `--no-visual` 跳过视觉证据校验。详见 [references/reset-and-verify-protocol.md](references/reset-and-verify-protocol.md) §Stage 1.5。

---

## §0 骨架流程（5 阶段 + 用户确认分级）

```
Phase 0: Plan        ⚙ Planner 子代理代写 plan.md（按 spec-kit plan.md 格式）
                      🛑 用户确认: 必（高风险：影响架构）
Phase 1: Spec        ⚙ Spec-Enhancer 子代理代写 spec.md（按 spec-kit spec.md 格式）
                      🛑 用户确认: 必（高风险：定契约）
Phase 2: Contract    ⚙ Contract-Writer 四件套
                      ⚙ 用户确认: 自动（低风险：契约已在 Spec 中预告）
Phase 3: Implement   ⚙ Implementer + code-hygiene + 阶段门禁
                      🛑 用户确认: 必（高风险：实际改动）
Phase 4: Review      ⚙ 四维验收 + acceptance-audit.py 真跑 + 满分硬门禁 + DOC SYNC
                      ⚙ 用户确认: 自动（验收结果客观判定）
                      🛑 必跑 acceptance-audit.py，AI 自评字符串不算

📦 Accept 合并入 Review 四维验收
🚦 用户确认分级: 3 次必确认（Plan/Spec/Implement） + 2 次自动（Contract/Review）
🚦 满分硬门禁: 任何非满分 = 🛑 REJECT（详见 references/acceptance-gates-v10.md）
```

### Bug 路径

```
Bug 快速链:
  Phase B.1: Plan(轻量) — 根因 + 影响面
  Phase B.2: Implement — 🔴RED 重现 → 🟢GREEN 修复 → 回归
  Phase B.3: Review(轻量) — 回归通过 + 无新漂移
```

---

## §1 委派速查

| 阶段 | Agent | subagent_type | 产出 |
|------|-------|:---:|------|
| Plan | [planner](agents/planner.md) | `general_purpose_task` | plan.md（Trae 格式）+ 状态卡 |
| Spec | [spec-enhancer](agents/spec-enhancer.md) | `general_purpose_task` | spec.md（增强）+ prototypes/ |
| Contract | [contract-writer](agents/contract-writer.md) | `general_purpose_task` | contracts/ + 测试骨架 |
| Implement | [implementer](agents/implementer.md) | `general_purpose_task` | 代码 + 测试 + 模块接入文档 |
| Review | [reviewer](agents/reviewer.md) | `general_purpose_task` | 四维验收报告 + DOC SYNC |
| Debug | [debugger](agents/debugger.md) | `general_purpose_task` | 根因 + 修复 |

### §1.5 委派注入（主上下文委派时必须注入）

| Agent | [MUST] 注入项 |
|-------|---------------|
| Planner | 委派子代理并行探索（文档+代码+依赖）；重构场景先调 spec-purge.py |
| Spec-Enhancer | 补充 Enhanced Acceptance（E2E≥2 + Invariants≥1 + Acceptance≥3）；涉及UI→prototypes/ 两份文档 |
| Contract-Writer | 四件套完整 + 测试骨架；变更走 ADDITIVE/BREAKING 流程 |
| Implementer | 编码前：读 spec+contracts → GitNexus context() 理解符号 → 读模块文档 → 输出"理解确认"；TDD RED→GREEN；每 task 完成 [ ]→[x]；基础模块→ 产出模块接入文档 |
| Reviewer | 四维验收（代码/API/UIUX/边际）；FAIL IS FAIL；对接 acceptance-discipline gate-keeper checklist；DOC SYNC 自动执行 |
| Debugger | 根因证据 + 复现步骤；修复后回归全绿 |

---

## §2 铁律（13 条，按场景分层）

```
【开发时铁律】（Implementer 执行）
  1. TDD RED→GREEN：无失败测试不写实现
  2. DRIFT DETECT：发现不一致立即报告回流
  3. 模块文档：基础模块必须产出接入文档
  4. 代码卫生：单文件 ≤ 800 行，函数 ≤ 50 行

【规划时铁律】（Planner 执行）
  5. EXPLORE FIRST：探索项目现状后再规划，禁止凭空设计
  6. IMPACT BY TOOL：影响面评估用 GitNexus，禁止手动 grep
  7. DEDUP BY ATOM：需求去重，> 50% 重叠合并

【验收时铁律】（Reviewer 执行）
  8. FAIL IS FAIL：不存在"非阻塞 FAIL"
  9. SCORING IS DERIVED：评分从维度刚性计算，禁止手动调分
  10. FOUR DIMENSIONS：验收必须覆盖代码/API/UIUX/边际

【文档时铁律】（全局）
  11. DOC FIRST：文档与代码冲突以文档为准
  12. DELTA ONLY：引用 docs/ 路径，禁止复制全文
  13. 归档不可变：archive/ 文件已沉淀，禁止修改
```

---

## §3 禁止项

| 禁止 | 替代 |
|------|------|
| 无 Plan 直接 Spec | 先走 /plan + Planner 探索 |
| 跳过 Contract 直接实现 | 契约是开发唯一入口 |
| 修改已批准契约不回流 | 走 ADDITIVE/BREAKING 流程 |
| 编造不存在的文件 | 标记缺失，不猜测 |
| 状态卡说谎 | state-card = 文件系统真相；> 80 行 = 重置 |
| 发现漂移静默迁就 | 漂移 → 报告 → 回流 |
| 修改 archive/ 下文件 | 归档 = 只读，建新 change |
| GitNexus 可用却用 grep 理解代码 | GitNexus query/context/impact |
| Agent 异常未记录 | 写入 `.trae/logs/report-growth.jsonl` |
| 将项目级文档全文复制到 changes/ | 用路径引用，不复制内容 |
| 跳过 Cockpit 自检直接工作 | 新会话先读 docs/specs/.state-card.md |
| 回流不重置状态卡 | 旧卡归档，新卡从模板生成 |
| 文档修剪丢失架构事实 | 删除前确认知识已回流到对应文档 |
| 单文件超 800 行 | 按模块拆分 |
| 重构时在旧 spec 上修修补补 | 调 spec-purge.py 清除后从零 Spec |
| 引用历史验收状态 | 重构/重写时只看当前 Spec，历史视为不存在 |
| 用猜测替代验证 | 不可验证的维度标 N/A，不设"降级" |

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

### Reviewer 特化格式

```
## Completion Report
- agent: reviewer
- code_dimension: PASS|FAIL
- api_dimension: PASS|FAIL|N/A
- uiux_dimension: PASS|FAIL|N/A
- boundary_dimension: PASS|FAIL|N/A
- total_score: {X.X}/5.0
- status: ✓ | ⚠️ | ✗
```

---

## §5 参考索引（按需加载）

| 主题 | 读 |
|------|-----|
| 验收门禁（四维） | [references/acceptance-gates-v10.md](references/acceptance-gates-v10.md) |
| 主上下文重置与真实验收 | [references/reset-and-verify-protocol.md](references/reset-and-verify-protocol.md) |
| 工件依赖图 | [references/artifact-schema.md](references/artifact-schema.md) |
| 工件生命周期 | [references/artifact-lifecycle.md](references/artifact-lifecycle.md) |
| 契约先行 | [references/contract-first.md](references/contract-first.md) |
| TDD 工作流 | [references/tdd-workflow.md](references/tdd-workflow.md) |
| DOC SYNC | [references/doc-sync.md](references/doc-sync.md) |
| 漂移检测 + 回流 | [references/drift-detect.md](references/drift-detect.md) |
| Bug 工作流 | [references/bug-workflow.md](references/bug-workflow.md) |
| 原型设计（UI） | [references/prototype.md](references/prototype.md) |
| 原型↔HTML 联动 | [references/prototype-linkage.md](references/prototype-linkage.md) |
| Designer 交接 | [references/designer-handoff.md](references/designer-handoff.md) |
| 驾驶舱 | [references/cockpit.md](references/cockpit.md) |
| 项目结构 | [references/project-structure.md](references/project-structure.md) |
| 异常报告 | [references/report-growth.md](references/report-growth.md) |
| 流程防腐 | [references/process-rot-analysis.md](references/process-rot-analysis.md) |
| 术语表 | [references/glossary.md](references/glossary.md) |
| 版本变更 | [references/changelog.md](references/changelog.md) |

## §6 确定性脚本

| 脚本 | 用法 | 调用方 |
|------|------|--------|
| Spec 清除归档 | `python scripts/spec-purge.py --feature {name} [--dry-run]` | Planner（重构时） |
| 文件系统真相读取 | `python scripts/change-status.py <change_dir>` | 主上下文阶段切换 |
| Hook 安装部署 | `python scripts/install-hooks.py --project-root <项目路径>` | 首次启用或 Hook 升级时 |
| V9→V10 项目迁移 | `python scripts/migrate-v9-to-v10.py --project-root <项目路径> [--dry-run]` | 已有 V9 项目升级时 |
| Spec 知识提取 | `python scripts/spec-knowledge-extract.py --feature <name> --project-root . [--dry-run]` | 归档前强制（reviewer Step 7） |

### §6.1 spec-purge — 重构时机械清除旧 spec

```bash
# 预览变更（推荐先执行）
python scripts/spec-purge.py --feature {feature-name} --dry-run

# 正式清除
python scripts/spec-purge.py --feature {feature-name}

# 批量清除
python scripts/spec-purge.py --all-done --dry-run
```

清除逻辑：
- 已完成 feature → `archive/done/{feature}/`
- 进行中 feature → `archive/out/spec-purge/{feature}-{timestamp}/`
- 删除 `docs/specs/{feature}/` 目录
- 更新 INDEX.md

幂等安全，可重复执行。Agent 禁止读取 `archive/out/spec-purge/` 中任何文件。
