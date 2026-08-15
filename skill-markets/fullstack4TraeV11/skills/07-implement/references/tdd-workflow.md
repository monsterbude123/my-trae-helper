# TDD 工作流（TDD Workflow）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 3 Implement Step 3 必走。V10 implementer.md 铁律 2 + tdd-workflow.md 蒸馏。

---

## TDD 三步循环

```
🔴 RED: 写失败测试（断言失败，非编译错误）
  ↓
🟢 GREEN: 最简实现，只让当前测试通过
  ↓
♻️ REFACTOR: 优化质量，保持测试通过
  ↓
🔍 DRIFT CHECK: 接口签名/字段类型/错误码 vs contracts/
```

---

## RED 阶段铁律

- **断言失败 ≠ 编译错误**: 测试必能跑起来但断言失败
- **一次只测一件事**: 避免"复合测试"难定位
- **测试命名规范**: `test_{module}_{scenario}_{expected}`

## GREEN 阶段铁律

- **最简实现**: 只让当前 RED 通过，不要"顺便"实现其他功能
- **不优化**: GREEN 阶段不重构，只让测试绿

## REFACTOR 阶段铁律

- **保持测试绿**: 重构时随时跑测试
- **小步前进**: 每次重构后跑一次测试

## DRIFT CHECK 阶段铁律

- 对照 contracts/ 验证：接口签名 / 字段类型 / 错误码 / 必填字段
- 不一致 → 立即报告回流（不静默）

---

## V10 实战反例

### 反例 A：跳过 RED 直接 GREEN

**V10 铁律 8**: 禁止跳过 TDD 🔴 阶段。

实战: implementer 直接写实现 → 测试通过 → 但实际是 GREEN-only（无 RED 验证）→ 测试用例可能永远 GREEN。

### 反例 B：修改测试让用例通过

**V10 铁律 8**: 禁止修改测试让用例通过（虚假绿灯）。

实战: 实现写错了 → implementer 改测试断言 → 测试通过 → 但实际是错的 → 上线后 bug。

### 反例 C：复合测试

实战: 1 个测试函数测 3 个场景 → 失败时不知道哪个场景错。

正确: 拆为 3 个独立测试函数。

---

## 关联引用

- [SKILL.md §铁律 2](../SKILL.md) — TDD 即时 + 红绿重构
- [code-hygiene.md](code-hygiene.md)
- [drift-detect.md](drift-detect.md)
- V10 tdd-workflow.md: `V10 来源` (已蒸馏到本文档)
