# Anti-patterns — Stage 1.5 Prototype 反例库

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


| # | 反例 | 文件 |
|:---:|------|------|
| 1 | 设计稿与代码脱节 | [01-design-code-mismatch.md](01-design-code-mismatch.md) |
| 2 | 跳过双源校验 | [02-skip-dual-source.md](02-skip-dual-source.md) |
| 3 | prototype 写实现 | [03-prototype-as-impl.md](03-prototype-as-impl.md) |

## 自检清单

```yaml
- [ ] 设计稿 vs 代码原型一致？
- [ ] 每个 UI 元素标注 AC ID？
- [ ] GAP 已列出？
- [ ] prototype 文档产出？
- [ ] 边缘状态(hover / loading / error / empty)已定义？   # V11.2 NEW(蒸馏自 05-prototype 自检报告 §问题 2)
```
