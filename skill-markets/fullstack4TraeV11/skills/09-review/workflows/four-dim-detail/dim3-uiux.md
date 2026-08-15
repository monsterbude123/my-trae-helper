# 维度 3：UI/UX 维度（25%）— four-dim-acceptance.md 详情

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 父文件：[../four-dim-acceptance.md](../four-dim-acceptance.md)
> 来源：原 four-dim-acceptance.md 第 7-50 行 + 第 172-198 行（保留信息密度）

---

## UI/UX 维度评分细则

**权重**: 25%

**evidence 字段**:
- `visual_consistency`: 视觉一致性（颜色 / 间距 / 字体）
- `interaction_logic`: 交互逻辑（按钮 / 表单 / 反馈）
- `ui_details_checklist`: 6/6 项细节检查清单（空状态 / 加载状态 / 错误状态 / 边界 / 响应式 / 可访问性）
- `screenshots`: 截图归档路径（`docs/verifications/{id}/default.png`）

**通过判定**:
- score ≥ 4.0 + 6 项 UI 细节检查全 PASS + 截图归档
- 截图缺失 → 维度 score = 0 → 总分 REJECT

**截图归档清单**（UI 任务必含）:
- `docs/verifications/{id}/default.png` — 默认状态
- `docs/verifications/{id}/loading.png` — 加载状态
- `docs/verifications/{id}/error.png` — 错误状态
- `docs/verifications/{id}/empty.png` — 空状态
- `docs/verifications/{id}/responsive-mobile.png` — 移动端响应式
- `docs/verifications/{id}/responsive-tablet.png` — 平板响应式

---

## 输出: review-report.md（UI/UX 部分）

```yaml
# Review Report: {change-id}

## 4 维评分

| 维度 | 权重 | 评分 | evidence |
|------|------|------|----------|
| 代码 | 25% | [0-5] | ... |
| API | 30% | [0-5] | ... |
| UI/UX | 25% | [0-5] | ... |
| 边际 | 20% | [0-5] | detect_changes / impact / 公共模块 / 全量回归 / 模块文档 |

**总分**: [Σ]

## 主动证伪

- [ ] 边界遗漏？
- [ ] 依赖污染？
- [ ] 公共模块副作用？
- ...

## 结论

[ ] PASS（≥4.0 + 4 维全评 + 证据齐全 + 用户签字）
[ ] REJECT（任一 FAIL → 失败标签）
```

---

## 关联引用

- 父文件：[../four-dim-acceptance.md](../four-dim-acceptance.md)
- four-dimension-scoring.md：[../../references/four-dimension-scoring.md](../../references/four-dimension-scoring.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
