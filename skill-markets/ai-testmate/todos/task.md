# ai-testmate Skill v1.1 — Task Tracker

> **依据**:`.trae/rules/skills开发细则.md` + V11 `references/skill-creation-workflow.md` §3.1
> **继承**:v1.0 todos 11 步已完成并 commit(暂存,未 commit)
> **本次**:v1.1 — 输入自适应 + 禅道可选化

---

## §0 蒸馏元信息

- **升级触发**:用户 2026-08-20 提问"4 种输入形态(PRD / PRD 树 / PRD+openapi / 仅 openapi)技能能否自适应" + "禅道可选,降级到 `<app-test>/docs/bugs/`"
- **新增能力**:
  1. **4 种输入自适应** — planner 探测后决策模式 A/B/C/D
  2. **openapi 自动提取用例** — 纯 API 模式 / 与 PRD 合并
  3. **禅道可选降级** — 无 zentao 配置时用本地 `<app-test>/docs/bugs/` 管理 bug 生命周期
- **借鉴 V11**:
  - ✅ 借鉴:**7 状态机简化版(OPEN/FIXED/CLOSED)+ source 第 7 字段**
  - ❌ 不借鉴:6 层排查 / 角色矩阵 / IN-FIX/VERIFIED/REOPENED/OBSOLETE(开发流程相关,与测试 agent 自动建单无关)

---

## §1 任务清单(v1.1 增量)

| # | 步骤 | 状态 | 产出文件 |
|:-:|------|:---:|----------|
| v2-0 | todos 契约(task + checklist v2) | ✅ | todos/task.md + checklist.md |
| v2-1 | 协议修改(扩 scope + bug-storage 选项 + V11 借鉴白名单) | ✅ | references/ai-testmate-protocol.md |
| v2-2 | input-router.md 决策矩阵 | ✅ | references/input-router.md |
| v2-3 | openapi-to-testcases.md + openapi-extractor.py | ✅ | references/openapi-to-testcases.md + scripts/openapi-extractor.py |
| v2-4 | v11-bug-flow-borrowed.md + bug-storage.md | ✅ | references/v11-bug-flow-borrowed.md + references/bug-storage.md |
| v2-5 | planner.md §1 自适应 + reporter.md §3.3 双路径 | ✅ | agents/planner.md + agents/reporter.md |
| v2-6 | pytest +6 用例 + 三态自检 + publish-protocol 重跑 | ✅ | tests/unit/test_ai_testmate.py |

---

## §2 关键决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| input 4 模式 | A:PRD单文件 / B:PRD目录树 / C:PRD+openapi / D:仅 openapi | 用户原话列举的 4 种 |
| openapi 解析深度 | 单 operation 1 个正例 + 1 个负例(404/422) | 防用例爆炸,pytest-patterns §5 已约定 |
| 禅道降级触发 | `.env` 缺 `ZENTAO_PRODUCT_ID` 或 zentao-cli 不可用 | 双触发条件,任意满足即降级 |
| bug 状态数 | 简化到 3 个(OPEN/FIXED/CLOSED)+ source 字段 | V11 7 状态机对测试 agent 过重,IN-FIX/VERIFIED 是开发流程 |
| bug 路径 | `<app-test>/docs/bugs/<YYYYMMDD>-<id>.md` | V11 docs/bugs/ 同款命名风格 |
| bug 单字段数 | 7 字段(ID/title/steps/expected/actual/severity/source) | V11 8 字段的简化版(去掉 fix/修复文件等开发字段) |

---

## §3 雷清单(v1.1 增量)

| # | 雷 | 检测 |
|:-:|----|------|
| V2-1 | openapi 解析忽略 `security` 字段(鉴权需求) | openapi-extractor.py 单元测试 |
| V2-2 | 禅道不可用时硬 exit,而不是降级 | reporter pytest mock |
| V2-3 | bug 单 frontmatter 字段不齐 | bug-storage.md 模板 + pytest |
| V2-4 | planner 4 模式没全部产出 source 标签 | input-router.md 测试矩阵 |
| V2-5 | openapi-only 模式还试图读 PRD | planner §1 决策树 |

---

## §4 完成报告占位

- 完成率:v1.1 6/6
- 协议覆盖:11 references 全 PASS(原 8 + 新 3)
- pytest:14 用例(原 8 + 新 6)
- 三态自检:PASS / BLOCK / 边界 全过
- 留置:v1.0 Batch B 暂存 27 文件 commit 待用户授权