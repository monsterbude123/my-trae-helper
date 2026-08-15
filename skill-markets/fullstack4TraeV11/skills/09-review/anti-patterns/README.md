# Anti-patterns — Stage 4 Review 反例库

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


| # | 反例 | V10 来源 |
|:---:|------|---------|
| 1 | "非阻塞 FAIL" 放水 | reviewer 铁律 1 |
| 2 | reviewer 帮忙修代码 | reviewer 铁律 6 |
| 3 | 编造测试覆盖 | V10.12 关键门禁套件 |
| 4 | 自动循环 Round 3+ 继续绕 | V10.12 Step 2.6 |

## 自检清单

```yaml
review_checklist:
  # 4 维 + evidence 基线
  - [ ] 4 维必评（无 N/A 充数）？
  - [ ] 每个维度附 evidence（命令 + 输出 + file:line）？
  - [ ] 主上下文亲自 Read 截图？
  - [ ] 主动证伪（5 项高风险清单）？
  - [ ] 失败标签必填（如 REJECT）？
  - [ ] DOC SYNC 已查？
  # 铁律反向检查（防漏）V11.3 NEW
  - [ ] 铁律 5 VERIFY UNDERSTANDING — 机械验证 implementer「理解确认」？
  - [ ] 铁律 6 REVIEWER DOES NOT FIX — reviewer 不动代码？
  - [ ] 铁律 7 FUNCTIONAL CHECK — 用户视角功能可用？
  - [ ] 铁律 10 关键门禁套件 — skeptical-validation-protocol.md 走查？
  - [ ] 铁律 10(指针) 必读 5 件套 — prototype HTML + design-prompt + ui-ux-logic + design.md + HANDOFF-DESIGNER.md 全 Read？
```
