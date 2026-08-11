---
feature_name: {功能名称}
branch: {###-feature-name}
created: {YYYY-MM-DD}
status: draft | in-review | approved | testing-complete
spec_version: "10.12"
test_plan_version: "1.0"
---

# {功能名称} — Test Plan

> **目的**: 强制将 spec.md 的测试场景映射到具体测试代码，防止"spec 写了但实现漏测"。
> **强约束（V10.12 NEW）**: reviewer §Step 2.5 前置门禁 — 必须先验证本文件存在 + 映射完整，否则 🛑 REJECT。
> **产出时机**: spec-enhancer 阶段（Phase 1）同步产出 spec.md + test-plan.md 两个文件。
> **更新时机**: implementer 必须按本文件实施测试；reviewer 按本文件核验覆盖。

---

## 1. 测试场景清单（从 spec.md 提取）

> 复制 spec.md `## BDD Scenarios` + `## Edge Cases` + `## E2E Scenarios` 的所有场景。
> 每个场景必须分配一个测试类型 + 覆盖优先级。

| 场景 ID | 场景描述（BDD 摘要） | 来源 | 测试类型 | 优先级 | 实施者 |
|---------|------------------|------|---------|--------|--------|
| TS-001 | {Given X, When Y, Then Z} | spec.md §BDD-XXX | unit/e2e/visual/manual | P0/P1/P2 | implementer |
| TS-002 | ... | spec.md §Edge-XX | unit/e2e/manual | P0/P1/P2 | implementer |
| ... | | | | | |

**测试类型说明**:
- **unit**: 单元测试（vitest/pytest/jest），覆盖单个函数/组件
- **e2e**: 端到端测试（Playwright/Cypress），覆盖完整用户旅程
- **visual**: 视觉测试（Playwright 截图 + vision-audit），覆盖 UI 渲染
- **manual**: 手动测试（脚本/录屏），覆盖无法自动化的场景

**优先级说明**:
- **P0**: 必须 100% 覆盖（产品核心功能）
- **P1**: 应该 80%+ 覆盖（重要场景）
- **P2**: 可选 50%+ 覆盖（边缘场景）

---

## 2. 测试覆盖映射表（实施者必填）

> 实施者必须为本表每个场景填上"测试文件:行号 + 状态"。
> **状态**: ✅ 已实现 / ⚠️ 部分实现（说明缺什么）/ ❌ 未实现（说明原因）
> **reviewer 必查**: 任何 ❌ P0/P1 = 🛑 REJECT

| 场景 ID | 测试类型 | 测试文件:行号 | 状态 | 备注 |
|---------|---------|-------------|------|------|
| TS-001 | unit | tests/foo.test.ts:42 | ✅ | — |
| TS-002 | e2e | e2e/bar.spec.ts:15 | ✅ | — |
| TS-003 | visual | docs/verifications/{feature}/empty-state.png | ⚠️ | 缺少 hover 状态截图 |
| TS-004 | manual | docs/manual-test-checklist.md | ❌ | 未执行 |
| ... | | | | |

---

## 3. 未覆盖场景说明（强制透明）

> **诚实声明**: 任何"spec 写了但 test-plan 不覆盖"的场景，必须在此登记。
> reviewer 必须基于本表判断"用户视角的功能缺口"。

| spec 场景 | 为何不覆盖 | 风险等级 | 缓解措施 |
|----------|----------|---------|---------|
| {spec.md §X 写了但本文件 TS 表没有} | {原因} | 🟢/🟡/🔴 | {用户验收/手动测试/降级/P2 延后} |
| {并发删除同模型} | spec 没明确要求 | 🟡 | 已记录到 spec 改进 backlog |
| ... | | | |

**反模式（V10.12 禁止）**:
- ❌ 假装 100% 覆盖（§2 全填 ✅ + §3 空白 + §4.4 空白 = 实施者没想清楚）
- ❌ "自动覆盖" = 想当然，spec 写了的必须显式映射到 §2
- ❌ 全填 ✅ 但 reviewer 跑测试发现某场景没测（造假 = 🛑 REJECT + 计入失败）
- ❌ 全填 🟢 风险等级 = 假装没风险

**§3 与 §Step 2.4.4 关系**（V10.12.1 质疑性修正）:
- §3 空白 ≠ 🛑 REJECT（已取消硬性）
- §3 缺失只是 signal "实施者可能漏想场景"
- reviewer 仍可在 §Step 2.5 产品侧验收时主动询问 "用户看到这个场景会怎么想？"
- 但 §2 出现 🔴 高风险缺口 → 走 reviewer-templates §Step 2.4.7 "退 spec-enhancer" 路径

---

## 4. 测试策略说明（实施者必填）

```markdown
### 4.1 测试金字塔
- 单元测试占比: {X}% （目标 ≥ 60%）
- E2E 测试占比: {Y}% （目标 ≤ 30%）
- 视觉/手动测试占比: {Z}% （剩余）

### 4.2 测试运行环境
- 前置依赖: {数据库容器启动/redis 启动/...}
- 环境变量: {.env 必要变量}
- 端口/路径: {测试用端口 vs 生产端口}

### 4.3 验证命令（reviewer §Step 2.5 必跑）
- 单元测试: `npm run test:unit` 或 `pytest tests/unit/`
- E2E 测试: `npm run test:e2e` 或 `playwright test`
- 视觉测试: `python scripts/visual-content-check.py --feature {feature}`
- 集成测试: `npm run test:integration`

### 4.4 已知测试盲区（诚实声明）
- {并发场景未覆盖：因为自动化复杂度高，本次手动验证}
- {性能压测未覆盖：P2 延后到 V{N+1}}
- {浏览器兼容性未覆盖：默认只测 Chromium}
```

---

## 5. 验收门禁（reviewer §Step 2.4 必查）

```
[ ] §1 测试场景清单 ≥ spec.md BDD Scenarios 数（不能少）
[ ] §2 映射表中 P0 场景 100% ✅，P1 ≥ 80% ✅
[ ] §3 未覆盖场景说明建议登记（非硬性 REJECT — 取消硬性防"全 🟢 造假"）
[ ] §4.3 验证命令可执行（reviewer 实际跑 1+ 个）
[ ] §4.4 已知盲区诚实声明（不假装 100% 覆盖）
[ ] §2 出现 🔴 高风险缺口 → 走 §Step 2.4.7 "退 spec-enhancer" 路径
```

**判定**:
- 全部 ✅ → §Step 2.5 进入产品视角核对
- §2 P0 漏测或 §4.3 不可执行 → 🛑 REJECT + 强制循环（§Step 2.6）
- §3 空白但其他 ✅ → 仅作 signal，不 REJECT（reviewer 在 §Step 2.5 主动询问）

**§3 与 §Step 2.4.4 关系**（V10.12.1 质疑性修正）:
- §3 空白 ≠ 🛑 REJECT（已取消硬性，避免催生"全 🟢"造假）
- 但若 §2 全填 ✅ + §3 空白 + §4.4 空白 → "假装 100% 覆盖"反模式触发 REJECT

---

## 关联

- [spec-template.md](spec-template.md) — spec.md 模板（§BDD Scenarios + §Edge Cases + §E2E Scenarios 是本文件 §1 的源）
- [reviewer-templates.md §Step 2.5](../references/reviewer-templates.md#step-25-产品侧功能有效性验收v1012-new--防货不对版) — 前置门禁
- [agents/spec-enhancer.md](../agents/spec-enhancer.md) — 必填项责任
- [agents/implementer.md](../agents/implementer.md) — §铁律"不量化不验收"