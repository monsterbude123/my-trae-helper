# v11-bug-flow-borrowed — V11 bug 流程借鉴白名单

> v1.1 增量。明确划清 ai-testmate 借鉴 V11 的 bug 流程范围,**不引入**开发流程相关部分。

---

## §1 借鉴白名单(只借鉴这些)

| V11 概念 | ai-testmate 简化版 | 出处 |
|---------|------------------|------|
| **bug 单 frontmatter**(V11 共 8 字段) | **7 字段**(去掉 `fix` / `修复文件`,详见 bug-storage.md) | [V11 bug-state-machine.md §CLOSED 回写模板](file:///d:/workspace/my-trae-helper/skill-markets/fullstack4TraeV11/skills/12-bug-fix/references/bug-state-machine.md) |
| **状态机**(V11 共 7 状态) | **3 状态**:OPEN / FIXED / CLOSED | [V11 bug-state-machine.md §状态机](file:///d:/workspace/my-trae-helper/skill-markets/fullstack4TraeV11/skills/12-bug-fix/references/bug-state-machine.md) |
| **source 第 7 字段** | `qa-found`(测试 agent 自动建单来源) | [V11 bug-state-machine.md §source](file:///d:/workspace/my-trae-helper/skill-markets/fullstack4TraeV11/skills/12-bug-fix/references/bug-state-machine.md) |
| **docs/bugs/ 目录命名** | `<app-test>/docs/bugs/<YYYYMMDD>-<id>.md` | V11 项目惯例 |
| **反例 A**(跳过 OPEN 直接修) | 同样禁止 reporter 直接写 FIXED 状态 | [V11 bug-state-machine.md §反例 A](file:///d:/workspace/my-trae-helper/skill-markets/fullstack4TraeV11/skills/12-bug-fix/references/bug-state-machine.md) |
| **反例 C**(功能变更后旧单悬空) | reporter 不自动标 OBSOLETE(留给开发流人工) | [V11 bug-state-machine.md §反例 C](file:///d:/workspace/my-trae-helper/skill-markets/fullstack4TraeV11/skills/12-bug-fix/references/bug-state-machine.md) |

---

## §2 不借鉴清单(明确边界)

| V11 概念 | 不借鉴原因 |
|---------|----------|
| **IN-FIX / VERIFIED / REOPENED 状态** | 开发流程状态。reporter 自动建单时只有 OPEN,后续状态由开发流人工 |
| **OBSOLETE 状态** | 需要"功能变更引用(tech-plan/spec diff)",reporter 无能力判断 |
| **CLOSED 三方协议**(代码提测 + 测试专家会签 + 用户确认) | reporter 不是任何一方,只能标 CLOSED 候选,真正 CLOSED 由开发流人工 |
| **6 层排查**(L1-L4) | V11 调试专属框架,reporter 自动建单不需要 |
| **role-protocol 角色矩阵**(debugger / code-submitter / test-expert) | V11 流水线角色,本 skill 不引入 |
| **new-bug.sh 建单脚本** | V11 内部脚本,本 skill 用 reporter §3.3 替代 |
| **qa-loop 反向守门** | V11 全栈流程专属 |
| **bug-hunt 专项** | V11 专项,不是测试 agent 日常职责 |

---

## §3 借鉴边界算法(防漂移)

借鉴 ∩ 不借鉴 = 空集(无重叠):
- ✅ reporter 只能建 OPEN 状态 bug 单
- ✅ reporter 只能在 CLOSED 三方确认后才能标 CLOSED(本 skill 默认不标,留给开发流)
- ✅ reporter 标记 FIXED 时必须附"已重跑报告 + 截图证据"(占位要求,真重跑由开发流)
- ❌ reporter 不参与 IN-FIX / VERIFIED / REOPENED / OBSOLETE 流转

---

## §4 命名一致性

| 项 | V11 命名 | ai-testmate 命名 |
|----|---------|----------------|
| bug 目录 | `docs/bugs/` | `<app-test>/docs/bugs/` |
| bug 文件名 | `<YYYYMMDD>-<id>.md` | **保持一致** |
| 状态 | 7 个全大写 | 简化为 3 个(OPEN/FIXED/CLOSED)|
| source 字段 | `qa-found` / `user-feedback` / `scan` | 仅用 `qa-found`(reporter 自动来源)|

---

## §5 与 V11 的同步策略

- V11 主版本升级(13 stage / qa-loop 变更)→ 本文件不需更新(只借鉴稳定的 bug 单结构)
- V11 bug-state-machine.md 7 状态重构(扩到 9 状态等)→ **本 skill 永远不跟进**(测试 agent 简化为 3 状态即可)
- V11 角色矩阵重命名 → 不影响本 skill(不引入角色)

> **铁律**:ai-testmate 借鉴 V11 的"程度"由本 skill 自主决定,**不追 V11 主线版本**。