# Git — 项目级 Git 工作流（项目独有）

> V11 不约束 Git 工作流（V11 关注 stage 流水线）。本文件定义项目级约定。

---

## 分支策略

```
main (production)
  └── release/v1.x (release)
       ├── feature/{change-id}（开发）
       └── bugfix/{bug-id}（修复）
```

- `main`: 必保护，仅 release branch 可合并（需 2 reviewer + CI pass）
- `release/v1.x`: 当前 release 分支，bugfix 仅可从此分支拉
- `feature/{change-id}`: Stage 0 Plan 创建的 change-id 必含日期（如 `2026-08-11-add-feature`）
- `bugfix/{bug-id}`: 来自 `docs/bugs/{bug-id}.md`

## Commit 规范

```
{stage}/{change-id}: {一句话描述}

- 详细变更 1
- 详细变更 2

Refs: docs/specs/changes/{change-id}/spec.md#AC-{N}
```

**stage 标签**（5 类，按 V11 stage 合并）：

| 标签 | 涵盖 stage | 语义 |
|------|-----------|------|
| `prep/` | -1 Intake / 0 Plan / 0.5 Test Plan | 启动 + 规划 + 测试计划 |
| `design/` | 1 Spec / 1.5 Prototype / 2 Contract | 规格 + 设计 + 契约 |
| `impl/` | 3 Implement | 实施 |
| `verify/` | 3.5 Real Verify / 4 Review / 4.5 Rot Scan / 5 Accept | 验证 + 评审 + 扫描 + 归档 |
| `bug/` | 6 Bug Fix | bug 单修复 |
| `health/` | 7 Project Health | 健康度（异步支线）|

**示例**：
```
prep/2026-08-11-add-feature: 初始化 change + 完成 plan.md + test-plan.md
design/2026-08-11-add-feature: 写 spec.md + prototype + contracts 4 件套
impl/2026-08-11-add-feature: TDD 实现登录接口（RED → GREEN → REFACTOR）
verify/2026-08-11-add-feature: 启动验证 + 4 维评审 + rot-scan PASS + 归档
bug/auth-token-expire: e2e 先行 + 6 层排查 + 修复 + bug 单 CLOSED
health/2026-08-11: 4 维度检查 + 优先级分级
```

## PR 模板

```markdown
## Change

{stage}/{change-id}: {一句话描述}

## Spec

参见: docs/specs/changes/{change-id}/spec.md

## V11 验收（必含）

- [ ] tests/contracts/ PASS
- [ ] 覆盖率 ≥90%（V11 Article I）
- [ ] review-report.md 4 维 ≥4.0
- [ ] rot-scan-{date}.md 10/10 PASS
- [ ] hooks-fidelity.py PASS

## 阻塞报告（如有）

5 字段阻塞报告: docs/specs/changes/{change-id}/.blocker.md
```

## 反例（必走 V11）

- ❌ 直接 push main → 🛑 REJECT（V11 Article XII workflow discipline）
- ❌ commit 信息不含 stage 标签 → 🛑 REJECT
- ❌ PR 未含 V11 验收 checkbox → 🛑 REJECT
- ❌ force push 已推送分支 → 🛑 REJECT（V11 Article VIII 归档不可变）
- ❌ 实施阶段用 verify/ 标签 / 验证阶段用 impl/ 标签 → 标签与 stage 不匹配

---

## 关联引用

- [stack.md](stack.md) — 项目栈命令
- [paths.md](paths.md) — 项目级禁读路径
- [V11 SKILL.md §0.5 加载协议](../../SKILL.md) — stage 流水线定义