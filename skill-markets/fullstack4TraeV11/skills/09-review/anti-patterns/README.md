# Anti-patterns — Stage 4 Review 反例库

| # | 反例 | V10 来源 |
|:---:|------|---------|
| 1 | "非阻塞 FAIL" 放水 | reviewer 铁律 1 |
| 2 | reviewer 帮忙修代码 | reviewer 铁律 6 |
| 3 | 编造测试覆盖 | V10.12 关键门禁套件 |
| 4 | 自动循环 Round 3+ 继续绕 | V10.12 Step 2.6 |

## 自检清单

```yaml
review_checklist:
  - [ ] 4 维必评（无 N/A 充数）？
  - [ ] 每个维度附 evidence（命令 + 输出 + file:line）？
  - [ ] 主上下文亲自 Read 截图？
  - [ ] 主动证伪（5 项高风险清单）？
  - [ ] 失败标签必填（如 REJECT）？
  - [ ] DOC SYNC 已查？
```
