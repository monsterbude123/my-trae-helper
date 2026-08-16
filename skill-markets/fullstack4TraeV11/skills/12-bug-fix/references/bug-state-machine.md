# Bug 单状态机（Bug State Machine）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)
>
> **V11.9+ 扩展**: 对齐 [role-protocol.md §6](../references/role-protocol.md) — 新增 REOPENED / OBSOLETE 状态 + bug 单第 7 字段 source；状态命名统一为 role-protocol 的 `IN-FIX`（原 IN_PROGRESS）。

> Stage 6 Bug Fix Step 5 必走。V10 bug-workflow.md + Intake bug-state-machine.md 蒸馏。

---

## 状态机（7 状态）

```
OPEN ──→ IN-FIX ──→ FIXED ──→ VERIFIED ──→ CLOSED   （现有，保留）
              │
              └──(回退)──→ OPEN        （e2e INITIAL PASS / 修复失败，非 bug）
                     FIXED ──→ REOPENED ──→ IN-FIX   （复测失败回退，NEW）
OPEN / FIXED / VERIFIED ──→ OBSOLETE                 （功能变更致过时，NEW）
```

| 状态 | 含义 | 维护者 |
|------|------|--------|
| **OPEN** | 已录入，待处理 | Intake / 测试专家（new-bug.sh 建单） |
| **IN-FIX** | 6 层排查 + TDD 修复中 | debugger / 代码提测（qa-submitter） |
| **FIXED** | 已修复，待测试专家复测 | 代码提测（qa-submitter，写权） |
| **VERIFIED** | 测试专家复测通过，再观察无 regression | 测试专家（test-expert，裁定权） |
| **REOPENED** | 测试专家复测 FIXED 失败回退 | 测试专家（test-expert） |
| **OBSOLETE** | 功能变更致过时（终态） | 测试专家（test-expert） |
| **CLOSED** | 关闭，归档（终态） | 三方确认（见表下 CLOSED 三方确认） |

> **CLOSED 三方确认**（对齐 role-protocol §5 / §6 + repair-flow.yaml step-4-user-confirm）：
> 代码提测申请 + 测试专家会签 + 用户确认。缺任何一方不得置 CLOSED。

## 转换矩阵

| From → To | 触发 | 必要条件 |
|-----------|------|---------|
| (无) → OPEN | Intake / new-bug.sh 建单 | 7 字段齐全（含 source） |
| OPEN → IN-FIX | debugger / 代码提测启动 | e2e 初始 FAIL + 已填 Description |
| IN-FIX → FIXED | 修复完成 | TDD GREEN + 回归 PASS + 已填 Fix |
| FIXED → VERIFIED | 测试专家复测通过 | 亲自跑 + 截图 + 4 维度观察无 regression |
| FIXED → REOPENED | 测试专家复测失败 | 附复现证据；同一单 REOPENED ≥ 2 次 → 升级仲裁 |
| REOPENED → IN-FIX | 回到修复队列 | 代码提测接手 |
| IN-FIX → OPEN | e2e 初始 PASS | 不是 bug（回退） |
| IN-FIX → OPEN | TDD 修复 FAIL | 重做循环 |
| OPEN/FIXED/VERIFIED → OBSOLETE | 功能变更致过时 | 仅测试专家可标 + 附过时理由 + 功能变更引用（tech-plan/spec diff） |

## bug 单第 7 字段 source（NEW，role-protocol §6）

```
source: qa-found | user-feedback | scan
  qa-found      — 测试专家提测/复测发现
  user-feedback — 用户反馈落盘（测试专家消化后建单）
  scan          — proactive-scan / rot-scan 等自动扫描发现
```

> 用户反馈**不另立目录**，统一走 docs/bugs/ + source 字段，状态机统一管理。测试专家对 user-feedback 单负有"主动验证"义务（先复现再定性，不直接转修复队列）。

## CLOSED 回写模板

```markdown
# Bug 单 CLOSED 回写

## 8.5 关闭记录

- **关闭时间**: YYYY-MM-DD HH:mm
- **关闭人**: debugger
- **根因**: [6 层排查结论 + GitNexus impact]
- **修复文件**: [file:line list]
- **关闭方式**: e2e PASS + 回归 PASS + 测试专家会签 + 用户确认
- **source**: [qa-found | user-feedback | scan]
```

---

## 反例

### 反例 A：跳过 OPEN 直接修

```
debugger: 用户报 bug → 立即修代码 → 没创建 bug 单  # ❌
正确: Intake / new-bug.sh 必先录入 OPEN bug 单（含 source）→ debugger 启动
```

### 反例 B：CLOSED 后又改

```
debugger: 已 CLOSED → 用户反馈 → Edit bug 单 CLOSED 字段  # ❌ Article XII
正确: 新建 bug 单（source: user-feedback）+ 引用原 bug-id
```

### 反例 C：功能变更后旧单悬空不处理

```
test-expert: 功能点改了 → 关联 OPEN/FIXED/VERIFIED 单没标 OBSOLETE  # ❌ 违反 OBSOLETE 义务
正确: 功能变更时清理关联过时单 → OBSOLETE（附功能变更引用），rot-scan 可扫出
```

---

## 关联引用

- [SKILL.md §铁律 7](../SKILL.md)
- [role-protocol.md §6](../references/role-protocol.md) — bug 状态机扩展 + source 字段（权威源）
- [repair-flow.yaml](../registry/repair-flow.yaml) — state_flow / closed_confirmation 程序化消费
- V10 bug-workflow.md: `V10 来源` (已蒸馏到本文档)
- Intake bug-state-machine.md: [../../01-intake/references/bug-state-machine.md](../../01-intake/references/bug-state-machine.md)
