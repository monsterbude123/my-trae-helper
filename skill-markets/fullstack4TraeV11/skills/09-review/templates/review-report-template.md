# Review Report: {change_id}

> 位置: `docs/specs/changes/{id}/review-report.md`

---

## 4 维评分

| 维度 | 权重 | 评分 | evidence |
|------|:---:|:---:|----------|
| 代码 | 25% | [0-5] | [test pass/total + coverage + lint] |
| API | 30% | [0-5] | [真实端点 + 签名一致 + 错误码] |
| UI/UX | 25% | [0-5] | [截图 + 交互验证] |
| 边际 | 20% | [0-5] | [GitNexus impact + 文档同步] |

**总分**: [(通过维度 / 适用维度) × 5.0]

---

## 通过依据 3 类分层

### [1] 后端/编译类
- ✅/⚠️ [evidence]

### [2] UI 渲染类
- ✅/⚠️ [evidence]

### [3] 用户视角类
- ⏳ [待办]

---

## 主动证伪（高风险清单）

- [ ] 边界遗漏？ ✅/❌
- [ ] 依赖污染？ ✅/❌
- [ ] 未提交文件？ ✅/❌
- [ ] 隐藏 TODO？ ✅/❌
- [ ] 测试篡改？ ✅/❌

---

## 失败标签（如 REJECT）

- 标签: MISMATCH / UNDERPERFORM / USER_VIEW_FAIL / TEST_GAP / DRIFT
- 5 字段阻塞报告: [type/description/attempted_solution/time_consumed/attempt_count]

---

## DOC SYNC

- [ ] spec.md INV 全部落地？
- [ ] contracts/ 与代码一致？
- [ ] modules/ 文档更新？

---

## 结论

[ ] PASS（≥4.0 分 + 4 维全评 + 证据齐全 + 用户签字）
[ ] REJECT（任一 FAIL → 退回 + 失败标签）

## 关联引用

- [SKILL.md](../SKILL.md)
- [four-dimension-scoring.md](../references/four-dimension-scoring.md)
- [evidence-3-layer.md](../references/evidence-3-layer.md)
- [skeptical-acceptance.md](../references/skeptical-acceptance.md)
- [multi-round-revision.md](../references/multi-round-revision.md)
