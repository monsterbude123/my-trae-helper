# qa-loop — 提测闭环流程（代码提测 ↔ 测试专家）

> **定位**: 描述 Stage 3.5 / Stage 6 提测态下，**代码提测（qa-submitter）** 与 **测试专家（test-expert）** 之间的循环协作流程。角色定义见 [skills/00-boot/agents/](../skills/00-boot/agents/)；权威源 [references/role-protocol.md §3](../references/role-protocol.md)。
> **核心铁律**: 修代码的不能自证通过；测代码的不能改代码；两者都不能改标准（gate/lock 归贾维斯）；最终裁决权留主上下文 + 用户。

---

## 1. 5 步闭环流程

```
┌────────────────── 代码提测主代理（qa-submitter）─────────────────┐
│ 1. 重启应用（干净构建；记录 进程信息+端口+构建 hash）              │
│ 1.5 委派前自验证: 在本进程先自跑一遍功能点验证（冒烟）             │
│     → 确认通过后再委派——避免把基础性崩溃留给测试专家              │
│       （主上下文抽检前置）                                       │
│ 2. [TEST-EXPERT-DELEGATION] 委派测试专家                         │
│    注入: 进程信息 + 功能点清单(产品策划经理产出)                  │
│         + bug 单目录 + 复测单清单(如有)                          │
│    ┌──────────── 测试专家(子代理) ─────────────┐                 │
│    │ A. 按功能点测试: api/uiux/id级            │                 │
│    │    应用侧 + 用户侧多处校验                │                 │
│    │ B. 新发现 bug → new-bug.sh 建单(OPEN)     │                 │
│    │ C. 复测 FIXED 单 → VERIFIED / REOPENED   │                 │
│    │ D. 过时单 → OBSOLETE(附功能变更引用)      │                 │
│    │ E. 用户反馈单 → 落盘 + 主动验证           │                 │
│    └──────────────────↓ 4字段报告 ─────────────┘                 │
│ 3. 报告含 OPEN/REOPENED → 逐单: 6层排查 + e2e 先行               │
│    (必初始 FAIL) + GitNexus impact/context → 修复                │
│    → bug 单 IN-FIX → FIXED → 回到 1                             │
│ 4. 循环终止: 全功能点 PASS + L1/L2 清零                          │
│    (L3 遗留须列入报告) + 测试专家签字                            │
│ 5. 提测报告 → 主上下文 Article IX 抽检（不盲信签字）              │
│    → 交接 Stage 4 review / Stage 5 accept                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 步骤 1.5 — 委派前自验证（主上下文抽检前置）

> 保证"主代理提交某些验证之后，子代理才在同一个应用进程上做专业测试"，避免把基础性崩溃留给测试专家。

```
MUST: 代码提测在自己启动的应用进程上先自跑一遍功能点验证（冒烟）
  → 覆盖核心功能点/关键路由（登录/主流程/本 change 实施点）
  → 确认冒烟通过后，才可委派测试专家
MUST NOT:
  → 冒烟未过就委派（基础性崩溃甩给测试专家 = 违规）
  → 委派后换了构建/进程（测试专家必须在同一构建上测试）
```

委派头 `[TEST-EXPERT-DELEGATION]` 前必须已完成本步骤；测试专家连接的是**同一个构建**（进程信息 + 端口 + 构建 hash）。

---

## 3. 委派头部引用（[TEST-EXPERT-DELEGATION]）

```
[TEST-EXPERT-DELEGATION] # 代码提测 → 测试专家（qa-loop 第 2 步）
  app_endpoint: <进程信息 + 端口 + 构建 hash>
  feature_scope: <功能点清单（产品策划经理产物）>
  retest_queue: <待复测 FIXED 单列表>
  bug_dir: docs/bugs/{change-id}/
  user_feedback: <本轮需消化的用户反馈（如有）>
  constraints:
    - 只在给定进程上测试，进程异常报告不重启
    - 新 bug 建单必带 source + severity + 复现步骤
    - 应用侧 + 用户侧至少各 1 处校验每功能点
    - 验收必须落 e2e 脚本（VERIFIED/REOPENED 只能来自脚本运行结果）；Playwright MCP 仅限 bug 定位探索，禁止手工点页面出验收结论
  forbidden: src/**（应用代码只读不写）
```

---

## 4. 循环铁律 4 条

```
① 每轮修复后必须重启应用再委派复测
   禁止测试专家在旧进程上验证新代码（HMR 陷阱，对标 12-bug-fix scripts/bug-hunt/ 的 stale 教训）
   定义: VERIFIED 只对"最新重启后的构建"有效；未重启即复测 = VERIFIED 无效

② e2e 先行
   修复者（代码提测）写复现 e2e 必初始 FAIL（证明 bug 真实存在）
   测试专家的验收 e2e 是独立第二套（裁判不复用运动员的卷子）
   测试专家必须写 e2e 脚本执行验收——VERIFIED/REOPENED 结论只能来自 e2e 脚本运行结果
   禁止用 Playwright MCP 手工点页面出验收结论（MCP 交互仅限 bug 定位/复现探索）

③ 循环上限
   同一 bug 复测 REOPENED ≥ 2 次 → 升级主上下文仲裁（5 字段阻塞报告）
   提测循环 ≥ 5 轮仍不收敛 → 升级用户决策

④ 时间预算（对标 12-bug-fix Layer 2 §L2.3）
   提测态发现 20% + 修复 60% + 收敛复测 20%
   预算耗尽即统计上报，不硬撑
```

---

## 5. 反模式（对标 role-protocol.md §8）

| # | 反例 | 角色方 | 处理 |
|:-:|------|-------|------|
| 1 | 代码提测修改测试脚本让测试通过 | qa-submitter | 🛑 REJECT + 修复回退 + 测试脚本恢复 |
| 2 | 测试专家顺手修了应用代码"小问题" | test-expert | 🛑 REJECT（对标 review-agent 先例），改走 bug 单 |
| 3 | 测试专家自行重启应用进程 | test-expert | 违规——进程证据链断裂，本轮测试结论作废 |
| 4 | 同一进程上验证新代码（未重启） | qa-submitter | HMR stale 陷阱，VERIFIED 无效 |
| 5 | 功能变更后旧 bug 单悬空不处理 | test-expert | 违反 OBSOLETE 义务，rot-scan 可扫出 |
| 6 | 测试专家用 Playwright MCP 手工点页面直接下 VERIFIED/REOPENED（无 e2e 脚本） | test-expert | 结论无效——验收必须落 e2e 脚本（可重复执行），MCP 交互仅限 bug 定位 |

---

## 6. 关联引用

- [references/role-protocol.md §3](../references/role-protocol.md) — qa-loop 权威源
- [skills/12-bug-fix/SKILL.md](../skills/12-bug-fix/SKILL.md) — Stage 6 四层框架（qa-loop 第 3 步的修复内核：6 层排查 + e2e 先行 + GitNexus）
- [skills/08-real-verify/SKILL.md](../skills/08-real-verify/SKILL.md) — Stage 3.5 启动可见产物（qa-loop 入口基础）
- [skills/00-boot/agents/qa-submitter.md](../skills/00-boot/agents/qa-submitter.md) + [test-expert.md](../skills/00-boot/agents/test-expert.md) — 角色定义
- [bug-state-machine.md](../skills/12-bug-fix/references/bug-state-machine.md) — OPEN/IN-FIX/FIXED/VERIFIED/REOPENED/OBSOLETE/CLOSED