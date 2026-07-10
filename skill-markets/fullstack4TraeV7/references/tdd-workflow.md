# 20-development / TDD 工作流（轴心流程 v5.0）

> **定位**：DOC SYNC GATE + CONTRACT GATE 通过后的开发轴心。所有生产代码必须由先失败后通过的测试驱动。V5.0 升级为**契约驱动 TDD**。
>
> **上游**：`20-development/doc-sync-protocol.md`（P0 文档同步完成）+ `01-contract/contract-first.md`（契约 approved + contract test 骨架就绪）
> **下游**：`30-testing/`（测试阶段）或 `40-acceptance/`（验收阶段）+ `feedback-loop.md`（漂移回流）

---

## V5.0 核心变化

```
V4 TDD 循环:  RED → GREEN → REFACTOR
V5 TDD 循环:  CONTRACT TEST → RED → GREEN → REFACTOR → DRIFT CHECK
                ↑                              ↑
                来自 fullstack-contract-writer           接 feedback-loop
                的 contract test 骨架          的漂移回流
```

| 维度 | V4 | V5 |
|------|----|----|
| TDD 起点 | 从零写测试 | fullstack-contract-writer 预生成 contract test 骨架 |
| 测试依据 | 仅 spec 场景 | spec 场景 + contracts/ 双重来源 |
| 循环环节 | RED-GREEN-REFACTOR | CONTRACT TEST-RED-GREEN-REFACTOR-DRIFT CHECK |
| 编码后自检 | 无 | 强制 DRIFT CHECK（契约 vs 代码） |
| 漂移处理 | 无 | 发现漂移 → 强制回流（feedback-loop） |
| 可见性 | RED/GREEN/REFACTOR | + CONTRACT TEST + DRIFT CHECK 5 个标记 |
| 心理成本 | "猜"测试名/断言 | 骨架已就绪，填断言即可 |

---

## 一、铁律（The Iron Law）

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST           │
│                                                             │
│   先写测试，看到失败，再写实现                               │
│                                                             │
│   V5 增强: 契约测试骨架必须先填，业务测试才能开始            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**违反这条规则就是违反 TDD 的精神。**

如果你先写了实现代码，**必须删除**，不能保留作为"参考"。
- ❌ 不要"保留作为参考"
- ❌ 不要"边写测试边适配现有代码"
- ❌ 不要"先看看现有代码"
- ❌ 不要"契约先放一边，我先把功能跑通"（V5 NEW）
- ✅ Delete means delete，重新从测试开始

---

## 二、核心原则

### V5 TDD 循环：CONTRACT TEST → RED → GREEN → REFACTOR → DRIFT CHECK

```
🟡 CONTRACT TEST (填契约测试骨架) → 🔴 RED (业务测试失败)
   → 🟢 GREEN (最简实现) → ♻️ REFACTOR (重构)
   → 🔍 DRIFT CHECK (契约 vs 代码自检)
```

### TDD 是轴心，不是步骤

```
❌ 误解：TDD 是开发流程中的一个步骤（可以跳过）
✅ 正确：TDD 是开发流程的轴心（所有代码围绕它展开）
```

**开发和修复的每一行生产代码，都必须由一个先失败后通过的测试驱动。**

### V5 新增：契约是 TDD 的脚手架

```
V4 痛点：fullstack-implementer 进来时，测试从零开始写
        → AI "猜"测试名、猜断言、猜边界
        → TDD 心理成本高 → 被静默跳过

V5 解药：fullstack-contract-writer 已生成 contract test 骨架
        → 测试名已定、断言框架已搭、fixtures 已备
        → fullstack-implementer 只需"填断言" → TDD 心理成本骤降
```

### 为什么顺序很重要

**"我先写代码，再补测试来验证"**

后写的测试立即通过，这证明不了什么：
- 可能测试的是错误的东西
- 可能测试的是实现细节，而非行为
- 可能遗漏了你忘记的边界条件
- 你从未看到它捕获 bug

**先写测试强制你看到它失败，证明它确实在测试某些东西。**

---

## 三、契约驱动 TDD 可见性规则（强制）

> **没有可见性输出 = 没有执行 TDD。**
>
> 这是防止"静默跳过 TDD"的核心机制。V5 新增 CONTRACT TEST 和 DRIFT CHECK 两个标记。

### 🟡 CONTRACT TEST 标记（V5 NEW，每个契约任务必须输出）

```
🟡 CONTRACT TEST 确认
├── 测试文件: {path}
├── 测试名称: {test name}
├── 对应契约: contracts/api-contracts.md#{接口名}
├── 骨架来源: fullstack-contract-writer 已预生成
└── 状态: ✅ 骨架已填，断言已补全
```

**铁律**：对应契约的任务必须先输出 CONTRACT TEST 确认，才能进入 RED。没有契约对应的任务跳过此步。

### 🔴 RED 标记（每次 RED 必须输出）

```
🔴 RED 确认
├── 测试文件: {path}
├── 测试名称: {test name}
├── 失败原因: {failure message}
├── 对应 Spec Scenario: {spec.md#scenario}（业务测试时）
└── 状态: ✅ 正确失败，可以进入 GREEN
```

### 🟢 GREEN 标记（每次 GREEN 必须输出）

```
🟢 GREEN 确认
├── 实现文件: {path}
├── 测试名称: {test name}
├── 通过状态: ✅ 所有测试通过
├── 实现方式: {最简实现描述}
└── 契约一致: ✅ 实现严格遵循 contracts/（V5 NEW）
```

### ♻️ REFACTOR 标记（每次 REFACTOR 必须输出）

```
♻️ REFACTOR 确认
├── 重构文件: {path}
├── 重构内容: {描述}
├── 测试状态: ✅ 仍然全部通过
└── 改进点: {可读性/重复消除/命名等}
```

### 🔍 DRIFT CHECK 标记（V5 NEW，每个任务完成后必须输出）

```
🔍 DRIFT CHECK 确认
├── 任务: {tasks.md 项}
├── 对比项:
│   ├── 接口路径: contracts/api-contracts.md vs 代码 ✅/❌
│   ├── 请求字段: api-contracts.md Body vs 代码 DTO ✅/❌
│   ├── 响应字段: api-contracts.md Response vs 代码返回 ✅/❌
│   ├── 错误码: api-contracts.md code vs 代码抛出 ✅/❌
│   ├── 字段类型: domain-models.md vs 代码类型 ✅/❌
│   └── 验证规则: validation-rules.md vs 代码校验 ✅/❌
├── 漂移结果: 🟢无漂移 / 🟡轻微 / 🔴严重
└── 行动: 继续 / 输出漂移报告回流（详见 feedback-loop.md）
```

**5 个标记的强制顺序**：
```
🟡 CONTRACT TEST → 🔴 RED → 🟢 GREEN → ♻️ REFACTOR → 🔍 DRIFT CHECK
```

- 🟡 CONTRACT TEST 没输出（对应契约任务时）= 不能写业务测试
- 🔴 RED 没输出 = 不能写实现代码
- 🟢 GREEN 没输出 = 不能声称完成
- 🔍 DRIFT CHECK 没输出 = 不能标记 tasks.md [x]
- 发现漂移不报告 = 违反铁律

---

## 四、契约驱动 TDD 速查流程（V5 完整版）

```
0. SPIKE（涉及未知 API 时）
   scripts/debug/ 创建联调脚本 → 沉淀为接口契约补充

1. 🟡 CONTRACT TEST：填契约测试骨架（V5 NEW，对应契约的任务）
   - 读取 fullstack-contract-writer 预生成的 tests/contracts/*.contract.test.ts
   - 补全断言（基于 contracts/api-contracts.md 的 fixtures）
   - npx vitest path/to/contract.test.ts → 看到失败（实现还未写）
   - 输出 🟡 CONTRACT TEST 确认

2. 🔴 RED：编写失败业务测试
   - 测试名称清晰描述行为（参考 fullstack-spec-writer 的 Test Skeleton Mapping）
   - 测试基于 spec.md 的 Scenario
   - npx vitest path/to/test.test.ts → 必须看到失败（报错不是失败！）
   - 输出 🔴 RED 确认：{测试文件} + {测试名称} + {失败原因} + {Spec Scenario}

3. 编译验证（强制 — 跑测试前必过）
   npx tsc --noEmit → 0 errors

4. 🟢 GREEN：最简实现
   - 只让测试通过，不添加功能、不重构其他代码
   - 实现严格遵循 contracts/ 不发明接口（V5 NEW）
   - npx vitest path/to/test.test.ts → 全部通过
   - 输出 🟢 GREEN 确认 + 契约一致性确认

5. ♻️ REFACTOR：消除重复/改善命名，测试保持通过

6. 🔍 DRIFT CHECK：编码后自检契约 vs 代码（V5 NEW）
   - 6 项对比（接口路径/请求字段/响应字段/错误码/字段类型/验证规则）
   - 不一致 → 🛑 输出漂移报告，触发 feedback-loop
   - 输出 🔍 DRIFT CHECK 确认

7. 标记 tasks.md: [x] 该任务 → 继续下一个 [ ] 任务

8. 覆盖率：>80%，关键路径 100%
```

---

## 五、与 fullstack-contract-writer 的衔接

### fullstack-contract-writer 提供什么

fullstack-contract-writer 在 V5 阶段产出以下供 fullstack-implementer 使用：

```
contracts/
├── domain-models.md       # 类型契约（fullstack-implementer 实现时遵循）
├── api-contracts.md       # 接口契约（fullstack-implementer 实现路由时遵循）
├── event-contracts.md     # 事件契约（如适用）
└── validation-rules.md    # 验证规则（fullstack-implementer 实现校验时遵循）

tests/contracts/           # contract test 骨架（fullstack-implementer 进来时已就绪）
├── create-user.contract.test.ts
├── user-login.contract.test.ts
└── ...
```

### fullstack-implementer 如何使用

```
1. 读取 contracts/ 理解契约不变量
2. 读取 tests/contracts/*.contract.test.ts 获取骨架
3. 每个 tasks.md 任务对应一个契约时：
   - 先填契约测试骨架（CONTRACT TEST 步骤）
   - 再写业务测试（RED 步骤）
   - 实现严格遵循契约（GREEN 步骤）
   - 编码后对比契约（DRIFT CHECK 步骤）
```

### contract test 骨架示例

fullstack-contract-writer 产出的骨架（fullstack-implementer 填断言）：

```typescript
// tests/contracts/create-user.contract.test.ts
// 来源: contracts/api-contracts.md#POST /api/v1/users
// 骨架由 fullstack-contract-writer 生成，断言由 fullstack-implementer 补全

import { describe, it, expect } from 'vitest';
import { contract } from './fixtures/create-user';

describe('Contract: POST /api/v1/users', () => {
  it('201 - 创建成功', async () => {
    // fullstack-implementer 填：基于 contract.fixtures.validRequest
    const res = await fetch('/api/v1/users', {
      method: 'POST',
      body: JSON.stringify(contract.fixtures.validRequest)
    });
    expect(res.status).toBe(201);
    expect(await res.json()).toMatchObject(contract.schemas.response);
  });

  it('40400 - 参数校验失败', async () => {
    // fullstack-implementer 填：基于 contract.fixtures.invalidEmail
  });

  it('40911 - 邮箱冲突', async () => {
    // fullstack-implementer 填：基于 contract.fixtures.duplicateEmail
  });
});
```

---

## 六、与 fullstack-spec-writer 的衔接

fullstack-spec-writer 在 spec.md 末尾输出 **Test Skeleton Mapping**，fullstack-implementer 据此命名业务测试：

```markdown
| Requirement | Scenario | 测试类型 | 测试名 | 测试文件 |
|------------|----------|---------|--------|---------|
| 用户注册 | Happy path | unit | test_register_returns_user | __tests__/UserService.test.ts |
| 用户注册 | Happy path | contract | test_create_user_happy_path | __tests__/contracts/users.test.ts |
| 用户注册 | Happy path | e2e | E2E-001 用户成功注册 | e2e/register.spec.ts |
```

fullstack-implementer 拿到这个映射后：
- 测试名已定 → 不用"猜"
- 测试文件路径已定 → 不用纠结位置
- 每个 Scenario 至少有 1 unit + 1 contract test → 覆盖完整

---

## 七、与 feedback-loop 的衔接

DRIFT CHECK 发现漂移时，强制触发 feedback-loop：

```
🔍 DRIFT CHECK 发现漂移
    ↓
判断漂移等级
    │
    ├── 🟢 无漂移 → 继续
    ├── 🟡 轻微 → 警告但继续，登记技术债
    └── 🔴 严重 → 🛑 停下，触发 feedback-loop
                ↓
            输出 Spec Drift Report（详见 feedback-loop.md）
                ↓
            回流到对应 Agent：
            ├── spec 错了 → 回流 fullstack-spec-writer
            ├── 契约错了 → 回流 fullstack-contract-writer
            ├── 代码错了 → 回流 fullstack-implementer（自己修）
            └── 目标错了 → 回流 fullstack-proposal-writer
                ↓
            BREAKING 变更需用户确认
                ↓
            修复后重新跑 DRIFT CHECK
```

**契约漂移自检触发词**（编码中遇到立即自检）：

| 触发情况 | 自问 | 行动 |
|---------|------|------|
| 写代码时发现契约与 spec 冲突 | "契约和 spec 谁对？" | 🛑 输出漂移报告 |
| 写代码时发现契约字段缺失 | "契约漏了还是我猜？" | 🛑 输出漂移报告，不猜 |
| 写代码时发现契约错误码不全 | "新增错误码走 ADDITIVE 流程？" | 🛑 输出漂移报告 |
| 测试时发现实现无法满足契约 | "契约错了还是实现错了？" | 🛑 输出漂移报告 |
| 连续打补丁超过 3 次 | "是不是根因没找对？契约漏了什么？" | 🛑 回流 fullstack-contract-writer |

---

## 八、TDD 循环守卫

在每次写实现代码前自问：

| 自问 | NO 的行动 |
|------|---------|
| 该任务对应契约吗？contract test 骨架已填？ | 🛑 先填契约测试骨架 |
| 已输出 🔴 RED 确认？ | 🛑 先写失败测试 |
| 在写实现而不是测试？ | 🛑 先写测试 |
| 实现的接口与 contracts/ 一致？ | 🛑 输出漂移报告 |

### 常见借口反驳表

| 借口 | 反驳 |
|------|------|
| "太简单不需要测试" | 简单代码也会坏，30 秒写出测试 |
| "先写代码再补测试" | 后补测试立即通过，证明不了什么 |
| "TDD 会拖慢我" | TDD 比调试快 |
| "bug 太简单不需要测试" | 简单 bug 也会回归 |
| "契约先放一边，我先把功能跑通"（V5 NEW） | 没契约的实现是猜，必漂移 |
| "DRIFT CHECK 太麻烦，编码完一起查"（V5 NEW） | 一起查 = 永远不查 |
| "契约好像不对，我先按我的来"（V5 NEW） | 违反铁律，必须先输出漂移报告 |
| "紧急情况没时间" | 不测的修复制造更多紧急 |

---

## 九、测试文件位置约定

| 测试类型 | 文件位置 | 来源 |
|----------|---------|------|
| 契约测试 | `tests/contracts/*.contract.test.ts` | fullstack-contract-writer 预生成骨架（V5 NEW） |
| 单元测试 | `src/**/__tests__/*.test.ts` | fullstack-implementer RED 时写 |
| 组件/UI 测试 | `src/components/**/__tests__/*.test.tsx` | fullstack-implementer RED 时写 |
| API 测试 | `src/app/api/**/__tests__/*.test.ts` | fullstack-implementer RED 时写 |
| 集成测试 | `tests/integration/**/*.test.ts` | fullstack-implementer RED 时写 |
| E2E 测试 | `e2e/*.spec.ts` | fullstack-implementer 或 acceptance-discipline 写 |

**🚨 前端 UI 修改必须写 UI 测试，只写后端测试 = ❌ 未完成**

---

## 十、Bug 修复的 TDD 流程（V5 升级）

```
1. 读取 fullstack-debugger 输出的根因证据清单
2. 检查根因是否涉及契约（V5 NEW）：
   ├── 涉及契约 → 先走契约变更流程（ADDITIVE / BREAKING）
   │              → 回流 fullstack-contract-writer 更新契约
   │              → 重新生成 contract test 骨架
   │              → 再进入 TDD
   └── 不涉及契约 → 直接 TDD
3. 编写重现 Bug 的失败测试 → 🔴 RED
4. 看到它失败 → 输出 🔴 RED 确认标记
5. 修复代码让测试通过 → 🟢 GREEN
6. 确认修复并防止回归 → 输出 🟢 GREEN 确认标记
7. 🔍 DRIFT CHECK：确认修复未引入新漂移（V5 NEW）
```

---

## 十一、检查清单

**每个 TDD 循环**：
- [ ] 契约测试骨架已填（如对应契约）（V5 NEW）
- [ ] 先写业务测试
- [ ] 确认 RED 失败
- [ ] RED 标记已输出
- [ ] 实现最小化
- [ ] 实现严格遵循 contracts/（V5 NEW）
- [ ] `tsc --noEmit` 通过
- [ ] 所有测试通过
- [ ] GREEN 标记已输出
- [ ] DRIFT CHECK 已执行（V5 NEW）
- [ ] DRIFT CHECK 标记已输出（V5 NEW）
- [ ] 覆盖率 > 80%
- [ ] 更新 tasks.md 标记 [x]

**整个开发周期**：
- [ ] DOC SYNC GATE 已通过（P0 同步完成）
- [ ] CONTRACT GATE 已通过（契约 approved）（V5 NEW）
- [ ] contract test 骨架已从 fullstack-contract-writer 接收（V5 NEW）
- [ ] 所有 TDD 循环可见性输出完整（5 个标记）
- [ ] 关键路径测试覆盖率 100%
- [ ] 契约漂移报告已处理（如有）（V5 NEW）
- [ ] 影响面已对照处理（V5 NEW）
- [ ] 文档已更新（接口/数据模型/变更记录）

---

## 十二、红旗信号 - 立即停止

- "先快速修复，以后再调查"
- "我已经花了 X 小时，删除是浪费"
- "TDD 是教条，我在务实"
- "契约先放一边，功能优先"（V5 NEW）
- "DRIFT CHECK 跳过，编码完一起查"（V5 NEW）
- "契约好像不太对，我先按我的来"（V5 NEW）
- "影响面我跳过验证了，应该没事"（V5 NEW）

**所有这些意味着：删除代码，用 TDD 重新开始，或回流 fullstack-contract-writer。**

---

## 参考

- [协议先行方法论](contract-first.md)
- [反馈回流方法论](feedback-loop.md)
- [状态卡方法论](state-card.md)
- [量化验收方法论](quantitative-acceptance.md)
- [fullstack-implementer Agent](../agents/fullstack-implementer.md)
- [fullstack-contract-writer Agent](../agents/fullstack-contract-writer.md)
- [fullstack-spec-writer Agent](../agents/fullstack-spec-writer.md)
