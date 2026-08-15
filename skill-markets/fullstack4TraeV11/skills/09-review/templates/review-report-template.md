# Review Report: {change_id}

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 位置: `docs/specs/changes/{id}/review-report.md`
>
> **V11.6.0 起:AC 核销矩阵是验收判定本体**(跑 [ac-gate.py](../../scripts/ac-gate.py) 机械校验 G1-G5)。4 维明细/评分已废弃为条件触发附加检查,不出现在判定结论。

---

## AC 核销矩阵(验收本体 — 必填)

> 6 列:AC-ID | 类型 | TC-ID | TC结果 | UI证据 | 状态
> 状态仅 ✅ / ❌。下游 [ac-gate.py](../../scripts/ac-gate.py) 的 G1-G5 将断言此表完整性 + 矩阵一致性。

| AC-ID | 类型 | TC-ID | TC结果 | UI证据 | 状态 |
|-------|------|-------|--------|--------|------|
| AC-1 | API | TC-001 | PASS | — | ✅ |
| AC-UI-1 | UIUX | TC-010 | PASS | add-btn.png | ✅ |
| AC-2 | EC | TC-002 | FAIL | — | ❌ |

### 漏核销检索(防 G4 拦)

- spec.md AC 列表: [自动列出,运营人工比对]
- 未在此表中出现 = G4 漏核销 → BLOCK

### 基准来源(Step -2 必列)

- spec.md 路径:`docs/specs/changes/{id}/spec.md`
- ui-ux-logic.md 路径:`docs/specs/changes/{id}/prototypes/ui-ux-logic.md`
- test-plan.md 路径:`docs/specs/changes/{id}/test-plan.md`
- 交互流引用:列出被核销的交互流 ID(AC-UI-N.ui_flow_ref)

---

## 附加检查(条件触发,非判定本体)

仅在下表触发条件命中时填写,不必跑全 4 维。

| 检查 | 触发条件 | 是否执行 | 证据 |
|------|---------|:--------:|------|
| 代码卫生(测试/lint) | 每次必跑(归档用) | ☐ |  |
| 契约对齐 | 本次涉及 contracts/ | ☐ |  |
| UI 状态检查 | ui-ux-logic 错误边界表声明 | ☐ |  |
| GitNexus 边际 4 项 | 公共模块(≥10 下游)变更 | ☐ |  |

---

## 主动证伪(高风险清单)

- [ ] 边界遗漏？ ✅/❌
- [ ] 依赖污染？ ✅/❌
- [ ] 未提交文件？ ✅/❌
- [ ] 隐藏 TODO？ ✅/❌
- [ ] 测试篡改？ ✅/❌

---

## 失败标签(如 BLOCK)

- 标签: MISMATCH / UNDERPERFORM / USER_VIEW_FAIL / TEST_GAP / DRIFT
- 5 字段阻塞报告: [type/description/attempted_solution/time_consumed/attempt_count]

---

## DOC SYNC

- [ ] spec.md INV 全部落地？
- [ ] contracts/ 与代码一致？
- [ ] modules/ 文档更新？

---

## 门禁判定(机械)

```bash
python scripts/ac-gate.py \
  --review-report docs/specs/changes/{id}/review-report.md \
  --spec docs/specs/changes/{id}/spec.md \
  --test-plan docs/specs/changes/{id}/test-plan.md
```

- 脚本 exit 0 → �� GATE PASS
- 脚本 exit 1 → �� GATE BLOCK(详见脚本输出)
- **入营结论唯一权威:脚本输出,人工不能覆盖**

## 结论

[ ] �� GATE PASS(ac-gate.py exit 0)
[ ] �� GATE BLOCK(任一 AC ❌ / 漏核销 / 编造 TC)

## 关联引用

- [SKILL.md](../SKILL.md)
- [acceptance-baseline-extract.md](../workflows/acceptance-baseline-extract.md) — Step -2 验收基准提取
- [ac-gate.py](../../scripts/ac-gate.py) — 机械门禁(G1-G5)
- [skeptical-acceptance.md](../references/skeptical
