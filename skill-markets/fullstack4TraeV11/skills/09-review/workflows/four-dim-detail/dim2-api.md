# 维度 2：API 维度（30%）— four-dim-acceptance.md 详情

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 父文件：[../four-dim-acceptance.md](../four-dim-acceptance.md)
> 来源：原 four-dim-acceptance.md 第 7-50 行（保留信息密度 — 评分模板在 dim1-code.md）

---

## API 维度评分细则

**权重**: 30%（最高权重）

**evidence 字段**:
- `endpoints_real`: 端点真实存在（非桩）
- `signature_consistent`: 签名一致（请求 / 响应 / 错误码）
- `data_model_consistent`: 数据模型一致（与 domain-models/ 对齐）
- `error_code_consistent`: 错误码一致（与 contract-errors 对齐）

**通过判定**:
- score ≥ 4.0 + 4 项 evidence 全 PASS
- 任一 evidence FAIL → 维度 score = 0 → 总分 REJECT

**契约对齐核查清单**:
- [ ] `docs/specs/changes/{id}/contracts/api-endpoints.md` 端点清单与代码一致
- [ ] `docs/specs/changes/{id}/contracts/domain-models.md` 字段与 schema 对齐
- [ ] `docs/specs/changes/{id}/contracts/events.md` 事件名/字段与发布/订阅对齐
- [ ] `docs/specs/changes/{id}/contracts/error-codes.md` 错误码表与代码 error code 对齐

---

## 关联引用

- 父文件：[../four-dim-acceptance.md](../four-dim-acceptance.md)
- four-dimension-scoring.md：[../../references/four-dimension-scoring.md](../../references/four-dimension-scoring.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
