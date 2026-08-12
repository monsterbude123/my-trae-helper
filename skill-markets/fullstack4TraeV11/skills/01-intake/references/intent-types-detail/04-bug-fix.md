# 意图 4：bug-fix — intent-types.md 详情

> 父文件：[../intent-types.md](../intent-types.md)
> 来源：原 intent-types.md 第 122-154 行（保留信息密度）

---

## 意图 4：bug-fix（Bug 修复）

**定义**: 修复用户反馈的 bug（含报错 / 不工作 / 期望不一致）。

**触发词**:
- "报错" / "错误" / "异常" / "不工作" / "失败" / "崩溃"
- "应该出现 X 但出现 Y" / "期望 X 但实际 Y"

**关键判断**: ⚠️ 必须先询问用户"是否作为 bug 单录入？" → 用户同意才创建。

**典型流程**:
```
Stage -1 Intake（Bug 录入 6 字段）
  → Stage 6 Bug Fix（独立支线，含 5 步精简流程）
    → Phase B.0 录入（Intake 已完成）
    → Phase B.1 e2e 先行（必须初始 FAIL）
    → Phase B.2 6 层排查
    → Phase B.3 TDD 修复
    → Phase B.4 回归验证
    → Phase B.5 Bug 单回写 CLOSED
```

**状态卡**: bug 级（位置 `docs/bugs/{bug-id}/.state-card.md`）

**bug-id 规则**: `{module}-{NNN}-{slug}`（如 `settings-009-config-key-case`）

**关键产出**:
- `docs/bugs/{bug-id}.md`（Bug 单）
- `docs/bugs/{bug-id}/.state-card.md`（状态卡）
- 修复代码 + 回归测试
- bug 单 CLOSED 回写

**详细 Bug 录入流程**: [../../workflows/bug-intake-flow.md](../../workflows/bug-intake-flow.md)
**详细 Bug 状态机**: [../bug-state-machine.md](../bug-state-machine.md)

---

## 关联引用

- 父文件：[../intent-types.md](../intent-types.md)
- bug-intake-flow.md：[../../workflows/bug-intake-flow.md](../../workflows/bug-intake-flow.md)
- bug-state-machine.md：[../bug-state-machine.md](../bug-state-machine.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
