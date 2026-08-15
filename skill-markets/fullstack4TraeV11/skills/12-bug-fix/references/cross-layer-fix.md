# 跨层修复最小化（Cross-Layer Fix Minimization）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 6 Bug Fix Step 4 必走。V10 debugger-methodology.md 跨层修复最小化范式。

---

## Ponytail bug 修复决策阶梯

```
Step 1: 根因在 1 层 → 改该层（最优）
Step 2: 根因跨 2 层 → 改源头层 + 1 处防御层
Step 3: 根因跨 3+ 层 → 用户决策（这是设计问题，非 bug）
```

## 反模式

### 反例 A：跨层过度修复

```
根因: 应用层业务逻辑错
修复: 应用层 + 数据层 + 集成层（5 文件改动）  # ❌ 过度

正解: 只改应用层（1 文件）  # ✅ 最小修复
```

### 反例 B：治标不治本

```
根因: 第三方 SDK bug
修复: 应用层 try-except 包住  # ❌ 治标

正解: 升级 SDK 版本 或 切换 SDK  # ✅ 治本
```

### 反例 C：单点修复不防御

```
根因: 某 API 返回 null
修复: 加 null check  # ✅ 防御
但: 加日志 + 监控 + 告警  # ✅✅ 更稳
```

---

## 修复决策表

| 根因复杂度 | 推荐修复 |
|-----------|---------|
| 单层 + 单文件 | 改该文件 |
| 单层 + 多文件 | 改源头 + 调用方防御 |
| 跨 2 层 | 改源头 + 1 处防御 + 监控 |
| 跨 3+ 层 | 用户决策 + 设计评审 |

---

## 关联引用

- [SKILL.md §铁律 6](../SKILL.md) — 跨层修复最小化
- [five-step-flow.md](five-step-flow.md)
- V10 debugger-methodology.md: `V10 来源` (已蒸馏到本文档)
