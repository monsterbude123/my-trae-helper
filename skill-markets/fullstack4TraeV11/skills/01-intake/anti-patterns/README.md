# Anti-patterns — Stage -1 Intake 反例库

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 4 条核心反例，每条含：现象 + 根因 + 教训 + 正确替代。

---

## 反例索引

| # | 反例 | 文件 |
|:---:|------|------|
| 1 | 无意图识别直接动手 | [01-no-intent-recognition.md](01-no-intent-recognition.md) |
| 2 | 跳过状态卡初始化 | [02-skip-state-card.md](02-skip-state-card.md) |
| 3 | 强制创建 bug 单 | [03-force-create-bug.md](03-force-create-bug.md) |
| 4 | 未勘察项目惯例 | [04-no-convention-survey.md](04-no-convention-survey.md) |

---

## 4 行结构（每条反例必含）

每条反例文档严格遵循以下结构：

```
## 现象
[具体场景描述 + 识别信号]

## 根因
[根因 + 占比 + 说明]

## 教训
[为什么错 + 真实案例 + 量化后果]

## 正确替代
[MUST 列表 + NEVER 列表 + 完整步骤]
```

---

## 与公共反例的边界

| 本目录（Stage -1 Intake 反例） | 公共反例（common-anti-patterns.md）|
|----------------------------|----------------------------|
| Intake 阶段特有 | 跨阶段通用 |
| 涉及意图识别 / 状态卡 / Bug 录入 / 项目惯例 | 涉及流程 / 委派 / 验收 / 文档 / 反虚假交付 |
| 4 条 | 18 条 |

**判定规则**:
- 仅 Intake 阶段触发 → 本目录
- 跨阶段通用 → 公共反例

---

## 主上下文自检清单（必走）

每收到用户输入时必查：

```yaml
intake_checklist:
  意图识别:
    - [ ] 触发词命中或 AskUserQuestion 已用？
    - [ ] 5 种意图之一已确定？
  项目惯例:
    - [ ] Glob 4 类文件已执行？
    - [ ] 项目惯例表写入状态卡 notes？
  状态卡:
    - [ ] 3 类状态卡（project/change/bug）之一已初始化？
    - [ ] state-card-validator.py PASS？
  Bug 录入:
    - [ ] 问题类触发词命中 → 已询问"是否录入 bug 单？"？
    - [ ] 用户拒绝时 health = 🟡 + 路由到 Stage 7？
```

---

## 关联引用

- [SKILL.md](../SKILL.md) — Stage -1 入口
- [README.md](../README.md) — 阶段元信息
- [公共反例](../../../references/common-anti-patterns.md) — 18 条跨阶段公共反例
- [公共铁律](../../../references/common-iron-rules.md) — 17 跨阶段铁律（Article XVII Secret Redaction,见 common-iron-rules.md）
