---
name: guard-gate-smith
version: 1.0.0
description: Guard & Gate 路由锻造者 — registry/skills.yaml 中央注册表的唯一维护者。负责把每个 skill 在 registry/skills.yaml 注册同名 guard + gate 路由，强制 scripts/<name>-guard.* 自治（项目侧而非 skill 子目录），并在 .husky/<name>-gate 落地门禁。是 guard-approver 的 guard/gate 路由特化版本，遵循 4 Tier 保护 + release-manager/project-owner 审批流程。触发词:guard-smith、guard 路由、gate 路由、skill 注册表、注册表守卫、guard 自治。
intent: Guard & Gate 路由锻造者 — 唯一可维护 registry/skills.yaml + scripts/<name>-guard.* + .husky/<name>-gate 的 agent
category: guard
audience: [agent]
requires:
  skills: [guard-approver]
---

# GuardSmith — Guard & Gate 路由锻造者

> **核心理念**：每个 skill 必须自己带 guard，guard 路由必须在中央注册表注册，**只有 guard-smith agent 能改这三类文件**。

---

## §0 背景（2026-08-14 蒸馏）

### 0.1 问题
- 原方案 3 个共享 guard 脚本（`scripts/skill-{security,structure,capability}-guard.py`）被全市场 43 个 skill 复用
- 任何 sub-agent 都能 Edit 这些 .py → 形成"agent 改守卫自绕过"漏洞
- L1/L2/L3/L4 gate 散落在 `.husky/` + `.github/workflows/`，没有统一路由表

### 0.2 方案 A（用户拍板）
- 每个 skill 在 `registry/skills.yaml` 注册同名 guard + gate 路由
- 每个 skill 必带 `scripts/<name>-guard.<ext>`（项目侧，非 skill 子目录）
- **只有 guard-smith agent** 能改 `registry/skills.yaml` / `scripts/<name>-guard.*` / `.husky/<name>-gate` / `.github/workflows/skill-market-gate.yml`
- 写权通过 `guard-approver` skill 的 4 Tier 保护机制兜底（Tier 3 需 release-manager/project-owner 审批）

### 0.3 与 guard-approver 的关系

| 维度 | guard-approver | **guard-gate-smith（本）** |
|------|----------------|----------------------------|
| 范围 | 全仓库 4 Tier 路径保护 | guard/gate 注册表 + 自治 guard 脚本 |
| 谁可改 | contributor+ 按 tier 自由 | **仅 guard-smith agent**（白名单机制） |
| 审批 | 4 Tier + role 审批 | guard-approver Tier 3 + 写权白名单 |
| 路由表 | `.trae/identity/protected-paths.yaml` | `registry/skills.yaml` |
| 兜底守卫 | `change-guard-approver.mjs` | `skill-registration-guard.mjs` |

**本质**：guard-smith = guard-approver 的"guard/gate 路由"特化。 凡是改 registry / scripts/<name>-guard.* / .husky/<name>-gate 的请求，都委派给 guard-smith sub-agent 执行。

---

## §1 GuardSmith 的 4 大职责

### 1.1 维护 `registry/skills.yaml` 中央注册表

每个 skill 必须按同名条目注册：

```yaml
- skill: <kebab-case>
  status: active | deprecated | archived
  guards:
    - { id: <name>-<aspect>, category: <structure|security|capability|registration>, script: scripts/<name>-guard.<ext>, triggers: [pre-commit, pre-push, L3] }
  gates:
    - { id: <name>-<aspect>, level: L1|L2|L3|L4, hooks: [.husky/pre-commit], runs_guards: [<guard-id>] }
  maintainer: guard-smith   # 唯一白名单
```

### 1.2 拆分 / 新建 `scripts/<name>-guard.<ext>`

按 skill 名独立自治（脱离共享脚本）。每个 guard 脚本：
- 接收 1 个参数：skill 名（或 skill 路径）
- exit 0=PASS / 1=BLOCK / 2=WARN
- 必须是项目侧路径，**禁止** 放 `skill-markets/<name>/scripts/`

**实施工具**：`scripts/forge-skill-guard.py <name>...` 一键生成 wrapper，杜绝 47 份风格漂移。
**实施案例**（2026-08-14）：47 个 skill 全部已通过 forge-skill-guard.py 生成 wrapper + 通过 guard-router --all 回归（38 PASS / 9 FAIL = 9 个预先存在 SKILL.md 缺 frontmatter 问题）。

### 1.3 维护 `.husky/<name>-gate` 门禁路由

每个 skill 的 gate 必须挂到正确的 husky hook 或 workflow，不允许 inline 在共享脚本里堆砌。

### 1.4 注册表守卫自举

`src/guards/skill-registration-guard.mjs` 是注册表守卫本体，guard-smith 维护它。

---

## §2 GuardSmith sub-agent 协议

### 2.1 sub-agent 触发条件

| 主 agent 想做的事 | 应该 |
|-------------------|-------|
| 改 `registry/skills.yaml` | 委派 guard-smith |
| 改 `scripts/<name>-guard.*`（新建/拆分/重构） | 委派 guard-smith |
| 改 `.husky/pre-commit` / `pre-push` / `<name>-gate` | 委派 guard-smith |
| 改 `.github/workflows/skill-market-gate.yml` | 委派 guard-smith |
| 改 `src/guards/skill-registration-guard.mjs` | 委派 guard-smith |
| 改 `scripts/guard-router.mjs` | 委派 guard-smith |
| 改其他普通 skill 文件（SKILL.md / references/） | **不**委派 guard-smith |

### 2.2 委派头部（主 agent 强制注入）

```
[GUARD-SMITH-DELEGATION]
  任务: <具体改的路径 + 改的内容>
  上下文: <为什么改>
  约束:
    - 仅改白名单内的路径（registry/skills.yaml + scripts/<name>-guard.* + .husky/<name>-gate + src/guards/skill-registration-guard.mjs）
    - 改完必须跑 node src/guards/skill-registration-guard.mjs 验证
    - 改完必须更新本 skill (如影响职责清单)
    - 严禁修改其他 skill 文件 / 普通 src/ / 普通 scripts/
```

### 2.3 guard-smith 收到任务后的 5 步流程（被调方响应）

```
1. 读 AGENTS.md §1 §3 铁律
2. 读 .trae/identity/protected-paths.yaml 确认改动路径属于 Tier 3
3. 执行改动（仅限白名单路径）
4. 跑 node src/guards/skill-registration-guard.mjs → 期望 PASS（自身条目）
5. 跑 node scripts/guard-router.mjs --all → 期望 PASS（不影响其他 skill）
```

### 2.4 通用 SOP：任何 agent 想调整 guard / gate 的完整 7 步

> 这是面向**调用方**（任意 agent,包括主 agent 和其他 sub-agent）的标准流程。
> guard-smith 是这个流程的第 4 步的执行者,但**整个流程的责任主体是发起调整的 agent**,不是 guard-smith。

```
┌──────────────────────────────────────────────────────────────────────┐
│ Step 1. 识别需求                                                       │
│   现象: pre-commit / pre-push / CI / verify 报错,或新场景需要新 guard │
│   触发源:                                                             │
│     - 用户显式要求:"给 xxx skill 加 security guard"                   │
│     - 守卫自检失败:tests/unit/test_*.py 报 BLOCK                       │
│     - 注册表守卫 BLOCK:node src/guards/skill-registration-guard.mjs   │
│     - 新建 skill:bin/cli.mjs create <name>                              │
│   输出: 一句话描述 "要改什么 + 为什么"                                 │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ Step 2. 自我判定 — 我能直接改吗?                                        │
│   查 §2.1 表:                                                         │
│     目标路径 ∈ 白名单(registry / scripts/<name>-guard.* / .husky/<name>-gate│
│       / scripts/guard-router.mjs / src/guards/* / gate workflow)       │
│         → 进入 Step 3 (委派 guard-smith)                              │
│     目标路径 ∉ 白名单 (普通 skill SKILL.md / src/*.mjs / package.json) │
│         → 我可以自己改,但如触发 §1.11 铁律 11 提到 guard/gate 联动,    │
│           仍需 Step 3 委派(因为白名单路径是另一份改动)                  │
│     目标路径 = Tier 4 路径(.husky/_* / .trae/identity/* /              │
│       scripts/change-guard-approver.mjs)                               │
│         → 🛑 终止:任何身份都不能改(包括 guard-smith),需提 Tier 4 清单  │
│           修订 PR(走 §2 铁律流程)                                        │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ Step 3. 准备委派上下文                                                  │
│   把 §2.2 的 [GUARD-SMITH-DELEGATION] 头部完整填好:                     │
│     任务: <具体改的路径 + 改的内容 + 影响哪些 skill>                    │
│     上下文: <现象 + 复现命令 + 期望结果>                               │
│     约束: <影响范围 + 不许动的边界 + 验证标准>                          │
│   关键: 不要省略影响范围!guard-smith 需要知道这个改动会让哪些           │
│   skill 的 wrapper 重新生成,才能选 aspects(structure/security/capability)│
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ Step 4. 委派 Task(subagent_type="general-purpose")                       │
│   选 sub-agent 而非自己动手的原因:                                      │
│     - guard-smith 的职责是"唯一改 guard/gate",体现 AGENTS.md §1.11     │
│       铁律 11 的白名单语义                                              │
│     - 隔离上下文:sub-agent 不会被其他任务的噪声污染                     │
│     - 审计清晰:每个 guard/gate 改动都有独立 sub-agent 记录             │
│   在响应里明确: Task(description="guard-smith: <任务>", ...)            │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ Step 5. 等待 sub-agent 报告 + 验收                                      │
│   sub-agent 必须按 §2.3 的 5 步流程:                                    │
│     1-3 读铁律 + 读 protected-paths + 改白名单路径                      │
│     4 跑 node src/guards/skill-registration-guard.mjs (期望 PASS)        │
│     5 跑 node scripts/guard-router.mjs --all (期望 PASS,或说明已知 fail)│
│   主 agent 验收:                                                        │
│     - 检查 sub-agent 是否真改了白名单路径(无越界)                       │
│     - 检查测试输出(PASS / BLOCK 是否合理)                              │
│     - 如失败 → 重新 Step 3 委派,或自行修问题再委派                      │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ Step 6. 主 agent 自己兜底验证(关键 — 不能信 sub-agent 一面之词)          │
│   亲自跑:                                                               │
│     - node src/guards/skill-registration-guard.mjs                      │
│     - node scripts/guard-router.mjs <changed-skill>                     │
│     - node tests/unit/test_guard_router.mjs                            │
│     - python tests/unit/test_registration_guard.py                       │
│     - npm run lint                                                       │
│   任何一项 fail → 回到 Step 3 重派                                      │
└──────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────┐
│ Step 7. commit + 文档同步 + 监控后续                                    │
│   - git add + commit -F .commit_msg.txt(中文多行用 -F 文件,见 §4.1.2)  │
│   - 同步 SECURITY-MAP.md + CAPABILITY-MAP.md(本次新增条目)              │
│   - 如改了本 SKILL.md 职责清单,确认自更新                              │
│   - commit 通过 gate 后,留意下一个 L3 PR / L4 release 是否有回归         │
└──────────────────────────────────────────────────────────────────────┘
```

**反模式**（必须避免）:
- ❌ 直接 Edit `scripts/<name>-guard.py` 绕过 guard-smith —— 违反 §1.11 铁律 11
- ❌ 跳过 Step 6 主 agent 自己验证 —— 等于信 sub-agent 自检,违反 §2.4 防假通过
- ❌ 不填 §2.2 头部就委派 —— guard-smith 不知道上下文,会写出错的 wrapper
- ❌ 改动影响范围超出"白名单路径" —— guard-smith 会立刻 refuse,但浪费了一次 round-trip
- ❌ 跳过文档同步 —— 下次 guard-smith 接手时无历史参考,易重复造轮子

**示例**（常见场景对照表）:

| 场景 | 调用方 agent 应该 |
|------|------------------|
| 用户:"想给 trae-security-review 加 security 扫描"| 主 agent → Step 2 查表(security-guard.py 是共享脚本,guard-smith 维护) → Step 3-4 委派 |
| 用户:"新 skill `my-foo`,请接入"| 主 agent → Step 2 查表(bin/cli.mjs create 自动调用 guard-smith 委派),所以**主 agent 跑 `bin/cli.mjs create my-foo`** 即可,CLI 内部按 §4.2 流程 |
| pre-commit BLOCK: "skill-markets/my-foo/ 未在 registry 注册"| 调用方 agent → 直接跑 `node src/guards/skill-registration-guard.mjs` 看完整错误 → Step 1 锁定是"新 skill 缺注册" → Step 2 判定(新建注册条目是 guard-smith 职责) → Step 3-4 委派 |
| CI L3 fail: `fullstack4TraeV9-capability` 在注册表但 script 不存在 | 调用方 agent → Step 1 锁定是"注册了但 wrapper 缺失" → Step 2(是白名单路径改动) → Step 3-4 委派 |
| 我(主 agent)只是想改 `skill-markets/coding-xinfa/SKILL.md` 的拼写错误 | 调用方 agent → Step 2 查表(普通 skill 文件,不在白名单) → **不**需要 guard-smith 委派 → 自己 Edit + commit |

---

## §3 注册表守卫（自举）

### 3.1 触发时机

- L1 commit gate：pre-commit step 0
- L2 push gate：pre-push step 0
- L3 PR merge gate：skill-market-gate.yml step 0
- L4 release gate：skill-market-gate.yml step 0

### 3.2 BLOCK 条件（任一即阻断）

```
- skill-markets/<x>/ 存在但 registry/skills.yaml 未注册
- 注册表条目指向不存在的 skill 目录
- 注册条目缺 guards 或 gates
- guards[].script 指向的文件不存在
- gates[].hooks 中任一文件不存在
- gates[].level 不是 L1/L2/L3/L4 之一
- maintainer 字段不是 guard-smith
```

### 3.3 反例（必须 BLOCK）

```
❌ 新建 skill-markets/my-foo/ 但未在 registry/skills.yaml 注册 → BLOCK
❌ 修改 scripts/skill-security-guard.py 但未通过 guard-smith agent → guard-approver Tier 3 BLOCK
❌ 删除 .husky/pre-commit → guard-approver Tier 4 物理 BLOCK
❌ guards[].script: scripts/<name>-guard.py 但文件不存在 → BLOCK
```

---

## §4 兼容性策略（迁移期 2026-08-14 ~ 后续 L3）

### 4.1 存量 43 个 skill
- 全部已注册（见 registry/skills.yaml）
- guards[].script 暂指向共享的 3 个 python 脚本（过渡期）
- guard-smith 后续按 skill 拆分专属 `<name>-guard.*`，仅改注册表即可生效

### 4.2 新建 skill
- `node bin/cli.mjs create <name>` → 自动在 registry/skills.yaml 追加条目 + 自动生成 `scripts/<name>-guard.py` 模板
- 模板文件含基础 frontmatter + `if __name__ == '__main__': sys.exit(0)` 占位 PASS

---

## §5 自我维护清单（guard-smith 必须知道）

- [ ] registry/skills.yaml 的 schema（§1.1）
- [ ] 兜底守卫本体位置（`src/guards/skill-registration-guard.mjs`）
- [ ] 路由器本体位置（`scripts/guard-router.mjs`）
- [ ] 3 个共享过渡脚本（`scripts/skill-{security,structure,capability}-guard.py`）
- [ ] L1/L2/L3/L4 gate 入口（`.husky/pre-{commit,push}` + `.github/workflows/skill-market-gate.yml`）
- [ ] guard-approver 写权边界（`.trae/identity/protected-paths.yaml`）

---

## §6 不做的事

- ❌ 修改普通 skill 文件（SKILL.md / references/）
- ❌ 修改 `bin/cli.mjs` / `src/*.mjs`（除 guards/）
- ❌ 修改 `package.json` / `tests/`
- ❌ 修改 `examples/` / `auto_reports/` / `logs/`
- ❌ 写 README / 文档（除非本 SKILL.md）

如收到此类任务 → 一律 refuse 并指回主 agent。