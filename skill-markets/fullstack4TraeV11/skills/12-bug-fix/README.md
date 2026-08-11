# Stage 6 Bug Fix — 元信息

> 第一性原则：**根因不明不修复，e2e 先行证明 bug 真实存在**。

## 完整骨架（5 步）

```
Step 1: 理解期望
Step 2: e2e 先行（必初始 FAIL）
Step 3: 数据分析（GitNexus impact + 6 层排查）
Step 4: TDD 修复（RED → GREEN → REFACTOR）
Step 5: 验收（回归 + bug 单 CLOSED）
```

## 6 层排查

网络 / 接入 / 应用 / 数据 / 集成 / 客户端

## 反例（4 条 + V10 蒸馏）

详见 [anti-patterns/](anti-patterns/)。
