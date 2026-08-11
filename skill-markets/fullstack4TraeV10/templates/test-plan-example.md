---
feature_name: example-feature
branch: 123-example-feature
created: 2026-08-10
status: testing-complete
spec_version: "10.12"
test_plan_version: "1.0"
note: 通用示例 — 展示 §1-§5 填写规范；具体任务实施时请替换 feature 名/场景/映射
---

# {功能名称} — Test Plan (Example)

> **本文件是 test-plan.md 模板的实战示例**，演示如何填写 §1-§5 五段。
> 真实任务使用时复制本文件，替换 `{占位符}` 即可。

---

## 1. 测试场景清单（从 spec.md 提取）

| 场景 ID | 场景描述（BDD 摘要） | 来源 | 测试类型 | 优先级 | 实施者 |
|---------|------------------|------|---------|--------|--------|
| TS-001 | Given 有 3 条记录 When 进列表页 Then 显示 3 张卡片 | spec.md §BDD-S1 | e2e | P0 | implementer |
| TS-002 | Given 用户点击删除 When 确认弹窗点确认 Then 卡片消失 + 文件删除 | spec.md §BDD-S2 | e2e + unit | P0 | implementer |
| TS-003 | Given 无记录 When 进列表页 Then 显示"暂无数据"提示 | spec.md §AC-1 | visual | P0 | implementer |
| TS-004 | Given 后端删除失败 When 用户点确认 Then toast 错误 + 卡片保留 | spec.md §AC-3 | e2e | P1 | implementer |
| TS-005 | Given 删除 10GB 大文件 When 用户点确认 Then 按钮 loading + 后端异步删 | spec.md §Edge-1 | manual | P1 | implementer |
| TS-006 | Given 用户点取消 When 确认弹窗打开 Then 弹窗关闭 + 卡片保留 | spec.md §BDD-S2-alt | unit | P1 | implementer |
| TS-007 | Given 同模型被两用户同时删 When 并发请求 Then 不允许重复删 | spec.md §Edge-2 | unit (P2 自动化难度高) | P2 | implementer |

**示例优先级分布**: P0 = 4 条（核心功能 + 空状态 + 失败回滚）/ P1 = 2 条（边界 + 取消）/ P2 = 1 条（并发）
**示例测试类型分布**: unit 1 / e2e 3 / visual 1 / manual 1 / mixed 1

---

## 2. 测试覆盖映射表（实施者必填）

| 场景 ID | 测试类型 | 测试文件:行号 | 状态 | 备注 |
|---------|---------|-------------|------|------|
| TS-001 | e2e | tests/e2e/list.spec.ts:15 | ✅ | Playwright `expect(page.locator('.card')).toHaveCount(3)` |
| TS-002 | e2e | tests/e2e/delete.spec.ts:22 | ✅ | Playwright 删除按钮 + 确认弹窗 + 列表断言 |
| TS-002 | unit | tests/unit/delete-api.test.ts:8 | ✅ | Mock DELETE 200 + 列表更新 |
| TS-003 | visual | docs/verifications/example-feature/2026-08-10-empty.png | ✅ | Playwright 截图归档 ≥5KB |
| TS-004 | e2e | tests/e2e/delete-fail.spec.ts:30 | ✅ | Mock DELETE 500 + toast 断言 |
| TS-005 | manual | docs/manual-test-checklist.md#L5-L12 | ⚠️ | 自动化复杂度高，本轮手动验证（用户签字）|
| TS-006 | unit | tests/unit/cancel-dialog.test.ts:18 | ✅ | — |
| TS-007 | unit | tests/unit/concurrent-delete.test.ts:42 | ❌ | 本轮不实现（P2 延后到 V{N+1}） |

**示例 P0 覆盖**: 4/4 = 100% ✅
**示例 P1 覆盖**: 2/2 = 100% ✅（TS-005 手动验证也算通过）
**示例 P2 覆盖**: 0/1 = 0% ❌（已登记到 §3 未覆盖说明）

---

## 3. 未覆盖场景说明（建议登记）

| spec 场景 | 为何不覆盖 | 风险等级 | 缓解措施 |
|----------|----------|---------|---------|
| TS-007 并发删除同模型 | spec.md §Edge-2 提到但自动化复杂度高 | 🟡 中 | 手动验证 2 浏览器并发删除 + 锁机制测试在 V{N+1} |
| {其他 spec 提到但本文件未列出的场景} | {原因} | 🟢/🟡/🔴 | {缓解} |
| ... | | | |

**反例（V10.12 禁止）**:
- ❌ 假装 100% 覆盖（§2 全填 ✅ + 本段空白 = 实施者没想清楚）
- ❌ 全填 🟢 风险等级 = 假装没风险

---

## 4. 测试策略说明

```markdown
### 4.1 测试金字塔
- 单元测试占比: 40% （覆盖 happy path + 部分边界）
- E2E 测试占比: 50% （覆盖用户视角关键流程）
- 视觉/手动测试占比: 10%

### 4.2 测试运行环境
- 前置依赖: docker compose up postgres（数据库容器）
- 环境变量: APP_DB_URL=postgres://localhost:5432/test
- 端口/路径: dev port 1420（与生产分离）

### 4.3 验证命令（reviewer §Step 2.4 必跑）
- 单元测试: `pnpm test:unit -- --run tests/unit/delete-api.test.ts`
- E2E 测试: `pnpm test:e2e -- tests/e2e/delete.spec.ts`
- 视觉测试: `python scripts/visual-content-check.py --feature example-feature`
- 集成测试: `pnpm test:integration`

### 4.4 已知测试盲区（诚实声明）
- TS-007 并发删除未自动化测试（已登记 §3）
- 性能压测未覆盖（P2 延后到 V{N+1}）
- 浏览器兼容性未覆盖：默认只测 Chromium（用户验收 Firefox/Safari）
- 弱网模拟未覆盖（自动化复杂度高）
```

---

## 5. 验收门禁（reviewer §Step 2.4 必查）

```
[x] §1 测试场景清单 ≥ spec.md BDD Scenarios 数（7 ≥ 7）✅
[x] §2 映射表中 P0 场景 100% ✅（4/4）✅
[x] §2 映射表中 P1 场景 ≥ 80% ✅（2/2 = 100%）✅
[x] §3 未覆盖场景说明登记（TS-007 P2 风险等级 🟡）✅
[x] §4.3 验证命令可执行（reviewer 实际跑过 `pnpm test:unit` + `pnpm test:e2e`）✅
[x] §4.4 已知盲区诚实声明（4 条）✅
```

**判定**: 全部 ✅ → §Step 2.5 进入产品视角核对

---

## 关联

- [spec-template.md](spec-template.md) — spec.md 模板
- [test-plan.md](test-plan.md) — 模板源文件
- [reviewer-templates.md §Step 2.4](../references/reviewer-templates.md#step-24-test-plan-前置门禁v1012-new--防spec-写了但实现漏测) — 前置门禁
- [reviewer-templates.md §Step 2.5](../references/reviewer-templates.md#step-25-产品侧功能有效性验收v1012-new--防货不对版) — 产品侧验收

---

*示例来源: V10.12.1 升级会话蒸馏 — 用户问"是否有必要做测试计划文档防遗忘"，本文件演示了 7 个典型场景 + TS-007 P2 未覆盖案例。*