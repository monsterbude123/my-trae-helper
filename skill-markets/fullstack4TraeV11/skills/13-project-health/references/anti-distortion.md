# 防失真机制（Anti-Distortion）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 7 Project Health Step 4 必走。V10.10 Article XVI 蒸馏。

---

## 5 大机制

### 1. 质疑性校验

```
project-health 报告必包含质疑段：
"是否有未发现的问题？是否有过度自信？"
```

### 2. 不可证伪理由分类（V10.10 Article XVI）

允许引用的失败归因（[agent-error-diagnosis.md §3 5 模式诊断](../../../references/agent-error-diagnosis.md)）:
- 盲信子代理产物（模式 1）
- 应付性汇报，缺 evidence（模式 2）
- 上下文击穿 + rule 长度超限（模式 3）
- 甩锅用户（模式 4）
- 安全事件，secret 进工具调用（模式 5）

**反模式**: 引用未定义术语、未指明位置的偏差、未量化裁剪、未测量心理负担、未定义的概念迁移等不可证伪术语作为失败归因。

### 3. self-diagnose 元检测

- project-health-auditor 自身是否失真？
- 检查项是否过期？

### 4. 跨会话验证

- 多会话读报告是否一致？
- 状态卡与报告是否一致？

### 5. 用户视角

- 用户角度看项目，哪些最显眼问题？

---

## 关联引用

- [SKILL.md §铁律 4](../SKILL.md) — 防失真
- [four-dimension-check.md](four-dimension-check.md)
- V10 来源: references/skeptical-validation-protocol.md（已蒸馏）
