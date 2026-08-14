---
name: guard-approver
version: 1.0.0
description: 保护路径守卫规范 — 防止 agent 任意修改 .husky / .github / scripts / src 核心等关键守卫与 gate 路径。规定 4 Tier 保护 + 3 类身份 + 4 步决策流。触发词:guard 保护、gate 保护、agent 越权、提权保护、change approval、代码评审。
intent: 保护路径守卫(identity / approval / decision / gate)
category: guard
audience: [developer, agent]
---

# Guard Approver 规范 v1.0

> 解决根本问题:**任何 agent 都能直接修改 `.husky/pre-commit` / `scripts/skill-*-guard.py` / `.github/workflows/*` 等关键守卫路径,造成"agent 改守卫自绕过"**
>
> 方案: 4 Tier 保护 + 3 类身份 + 4 步决策流

## 核心原则

1. **关键守卫不允许 agent 自改** — 守卫保护自身
2. **敏感路径必须人工审批** — 不是 agent 自批
3. **审批记录可审计** — 每次决议写 NDJSON,纳入 commit
4. **Tier 4 不可逆** — 任何身份(含 project-owner)都不能改,只能改 Tier 4 清单本身(也需 PR)

## 4 Tier 保护(PRF-001 ~ PRF-004)

| Tier | 含义 | 触发 | 谁可改 |
|------|------|------|--------|
| **Tier 1** | 自由修改 | 无 | contributor+ |
| **Tier 2** | 需同角色审批 (peer-review) | 提交后写 pending,push 前需 resolve | contributor 可改,qa-lead / release-manager / project-owner 可批 |
| **Tier 3** | 需 release-manager 审批 | 同上 | 同上,审批门槛更高 |
| **Tier 4** | 禁止修改 | git hook 物理阻断 | **任何身份不可改** (改 .trae/identity/*.yaml 本身也需 PR) |

### 当前默认保护清单(详见 [protected-paths.yaml](file:///d:/workspace/my-trae-helper/.trae/identity/protected-paths.yaml))

| 路径 | Tier |
|------|------|
| `.husky/_*` `.git/hooks/*` | 4 (禁止) |
| `.trae/identity/*.yaml` | 4 (禁止) |
| `scripts/change-guard-approver.mjs` | 4 (禁止) |
| `.husky/pre-commit` `.husky/pre-push` `.husky/post-commit` | 3 (需 release-manager) |
| `.github/workflows/*.yml` | 3 |
| `scripts/skill-security-guard.py` `scripts/skill-structure-guard.py` `scripts/skill-capability-guard.py` | 3 |
| `scripts/lint.mjs` | 3 |
| `src/install-guards.mjs` `src/bundle.mjs` `src/bundle-helpers.mjs` | 3 |
| `src/execution/*.mjs` `src/guards/*.mjs` `bin/cli.mjs` | 3 |
| `skill-markets/skill-acceptance/checks/*.py` | 2 (需 qa-lead + 同角色 peer) |
| `package.json` | 2 |
| `skill-markets/<pkg>/SKILL.md` | 1 (自由) |
| `src/<module>.mjs` | 1 |

## 3 类身份(identity / roles)

| 角色 | 职责 | 可编辑 | 可审批 |
|------|------|--------|--------|
| `contributor` | 普通贡献者 | Tier 1 | Tier 1, 2 |
| `qa-lead` | QA / 验收负责人 | Tier 1, 2 | Tier 1, 2, 3 |
| `release-manager` | 发布负责人 | Tier 1, 2, 3 | Tier 1, 2, 3 |
| `project-owner` | 项目所有者 | Tier 1, 2, 3 (Tier 4 仍不可) | Tier 1, 2, 3 |

### 身份解析优先级

1. `GIT_AUTHOR_EMAIL` / `GIT_COMMITTER_EMAIL` (commit 时由 git 设置)
2. `.trae/identity/local-override.yaml` (本机覆盖)
3. `$USER` (envvar)
4. `git config user.email` (本机 git 配置)
5. `whoami` (fallback)

→ 然后用 [skill-roles.yaml](file:///d:/workspace/my-trae-helper/.trae/identity/skill-roles.yaml) 映射到角色

## 4 步决策流

```
Step 1: Agent 修改文件
   ↓
Step 2: pre-commit 钩子运行 change-guard-approver check
   - Tier 4 → 🛑 BLOCK (硬阻断)
   - Tier 2/3 → 写 .trae/approvals/<branch>/<commit>.pending.json
   - Tier 1 → ✅ PASS (透明)
   ↓
Step 3: Agent 推 PR
   - pre-push 钩子运行 change-guard-approver gate
   - 读 .trae/approvals/<branch>/<commit>.resolved.json
     - 不存在 → 🛑 BLOCK (需审批)
     - decision=reject → 🛑 BLOCK (被拒)
     - decision=approve 但角色不足 → 🛑 BLOCK (LOWROLE)
     - decision=approve 且角色够 → ✅ PASS
   ↓
Step 4: 高角色(可用 release-manager / project-owner)运行 resolve
   node scripts/change-guard-approver.mjs resolve --decision approve --comment "理由"
   ↓
Step 5: 重试 push → gate PASS
```

## CLI 用法

```bash
# 1. Agent 提交变更(pre-commit 自动调用)
node scripts/change-guard-approver.mjs check --changed <file1> <file2> ...

# 2. 高角色审批(手动执行)
node scripts/change-guard-approver.mjs resolve --decision approve --comment "修复 L1 lint bypass"
node scripts/change-guard-approver.mjs resolve --decision reject  --comment "理由:太危险"

# 3. 推 PR(pre-push 自动调用)
node scripts/change-guard-approver.mjs gate

# 4. 查看当前 pending 状态
node scripts/change-guard-approver.mjs status
# 或:
npm run test:approver:status
```

## 5 个守卫码(PRF-001 ~ PRF-005)

| 守卫码 | 含义 | 级别 |
|--------|------|------|
| **PRF-001** | Tier 1 自由 (仅 INFO) | INFO |
| **PRF-002** | Tier 2 已记录,需同角色审批 | INFO / BLOCK |
| **PRF-003** | Tier 3 已记录,需 release-manager 审批 | INFO / BLOCK |
| **PRF-004** | Tier 4 禁止修改 | BLOCK(硬) |
| **PRF-005** | Tier 5 (预留) | — |
| **PRF-OK / PRF-OK2 / PRF-OK3** | 变更已写入 pending | INFO |
| **PRF-GATE** | push 阶段无 resolved | BLOCK |
| **PRF-REJECTED** | 审批拒绝 | BLOCK |
| **PRF-LOWROLE** | 审批人角色不足 | BLOCK |
| **PRF-NOPEND** | 有 Tier 2/3 修改但无 pending 记录 | BLOCK |

## 退出码契约

| 退出码 | 含义 | Gate 行为 |
|--------|------|----------|
| 0 | PASS | 继续 |
| 4 | BLOCK (Tier 4 / PRF-GATE / PRF-REJECTED / PRF-LOWROLE / PRF-NOPEND) | L1/L2 阻断 |
| 5 | ARG_ERROR | Gate 配置错误,直接失败 |
| 6 | INTERNAL_ERROR | 走 fall-back 流程 |

## 实战拦截场景

### 场景 A: agent 想绕过 L1 lint

```bash
# agent 改 .husky/pre-commit 删掉 npm run lint
git add .husky/pre-commit
git commit -m "speed up"  # pre-commit 触发:
# 🛑 [PRF-004] Tier 4: 等等 → 实际是 Tier 3
# ✅ [PRF-OK3] Tier 3 变更已记录 (你=contributor, 需 release-manager 审批)
# → commit 成功, 但 pending 文件写入
git push  # pre-push 触发:
# 🛑 [PRF-NOPEND] Tier 3 修改 .husky/pre-commit 无 pending 记录
# (实际 pending 已写,需 resolved)
# 若无 resolved: BLOCK
# 若 release-manager resolve approve: PASS
```

### 场景 B: agent 给自己提权

```bash
# agent 改 .trae/identity/skill-roles.yaml
# 把自己的 user 改为 project-owner
git add .trae/identity/skill-roles.yaml
git commit -m "role update"
# 🛑 [PRF-004] Tier 4 禁止修改: .trae/identity/skill-roles.yaml
# 改 .trae/identity/skill-roles.yaml 本身也需 PR(因为是 Tier 4)
```

### 场景 C: 多人合作 — Tier 2 peer review

```bash
# contributor A 改 skill-acceptance/checks/01_frontmatter.py
# 写 pending,等 qa-lead 审批
node scripts/change-guard-approver.mjs check --changed skill-markets/skill-acceptance/checks/01_frontmatter.py
# → ✅ [PRF-OK2] pending 已记录 (需 qa-lead)

# qa-lead B 审批
node scripts/change-guard-approver.mjs resolve --decision approve --user "B@qa" --role qa-lead --comment "lgtm"
# → resolved 写盘

# A 推
git push
# → ✅ [PRF-OK] 已由 B@qa (qa-lead) 审批通过
```

## 接入位置

| Gate | 触发 | 子命令 | 位置 |
|------|------|--------|------|
| L1 Commit | `git commit` | `check` | [.husky/pre-commit](file:///d:/workspace/my-trae-helper/.husky/pre-commit) Step 7 |
| L2 Push | `git push` | `gate` | [.husky/pre-push](file:///d:/workspace/my-trae-helper/.husky/pre-push) Step 5 |
| L3 Merge (CI) | PR merge | `gate` (需扩展) | 建议加到 skill-market-gate.yml |
| 显式 | `npm run test:approver:status` | `status` | 任意时刻 |

## 与项目其他体系的关系

- **AGENTS.md §2.2 Guard 清单**:本规范给所有现有 guard(skill-security / skill-structure / skill-capability / dependency)加了"自身保护" — **本规范是 meta-guard**
- **AGENTS.md §2.3 Gate 层级**:本规范接入 L1 / L2
- **AGENTS.md §2.4 Gate 自验收**:脚本已用 12 个用例自验
- **三层控制**:本规范既是 Guard(运行时检查)也是 Gate(提交/推送拦截)
- **experience-routing(.trae/rules/learning.md)**:任何"agent 绕过守卫"事件应入 trap-instructions.yaml,反馈到本规范的 Tier 调整

## 关联

- [scripts/change-guard-approver.mjs](file:///d:/workspace/my-trae-helper/scripts/change-guard-approver.mjs) — 守卫实现
- [.trae/identity/skill-roles.yaml](file:///d:/workspace/my-trae-helper/.trae/identity/skill-roles.yaml) — 身份 + 角色
- [.trae/identity/protected-paths.yaml](file:///d:/workspace/my-trae-helper/.trae/identity/protected-paths.yaml) — 保护路径
- [.husky/pre-commit](file:///d:/workspace/my-trae-helper/.husky/pre-commit) — L1 接入
- [.husky/pre-push](file:///d:/workspace/my-trae-helper/.husky/pre-push) — L2 接入
- [AGENTS.md §1.2 CLI 拆分](file:///d:/workspace/my-trae-helper/AGENTS.md) — scripts/change-guard-approver.mjs 是符合"≥3 职责的脚本"的拆分

## 自验清单(已通过)

| 用例 | 期望 | 实际 |
|------|------|------|
| `check` 缺 `--changed` | exit 5 | 5 ✅ |
| `check` Tier 1 路径 | exit 0,无 pending | 0 ✅ |
| `check` Tier 3 路径 | exit 0,写 pending | 0,pending ✅ |
| `check` Tier 4 路径 | exit 4,BLOCK | 4 ✅ |
| `check` 改 protected-paths.yaml | exit 4,BLOCK | 4 ✅ |
| `check` 改 guard 自身 | exit 4,BLOCK | 4 ✅ |
| `gate` 无 pending | exit 4 | 4 ✅ |
| `gate` 有 pending 无 resolved | exit 4 | 4 ✅ |
| `gate` 低角色 approve | exit 4 (LOWROLE) | 4 ✅ |
| `gate` 高角色 approve | exit 0 | 0 ✅ |
| `gate` reject | exit 4 | 4 ✅ |
| `resolve` 缺 --decision | exit 5 | 5 ✅ |
| `resolve` 低角色 approve | exit 4 | 4 ✅ |
| `resolve` 高角色 reject | exit 0 | 0 ✅ |
