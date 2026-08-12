# Report Growth — 报告分级机制

> V11 Stage 1 Spec / Stage 5 Accept 必读。报告规模分级。

---

## 4 个 Level

### L1 — 简短结论（< 1 屏）

```yaml
用途: Stage 0 Plan 输出
内容: Capability 列表 + Non-Goals + 3 路径评估
受众: 用户快速决策
```

### L2 — 详细计划（1-3 屏）

```yaml
用途: Stage 1 Spec 输出
内容: AC + INV + Edge Cases + 验收标准
受众: 用户 + sub-agent
```

### L3 — 完整文档（3-10 屏）

```yaml
用途: Stage 2 Contract / Stage 4 Review 输出
内容: domain-models + api-contracts + events + validation-rules + 4 维评分
受众: sub-agent 执行
```

### L4 — 归档完整包（10+ 屏）

```yaml
用途: Stage 5 Accept 归档
内容: spec + plan + contracts + review-report + rot-scan + verify-report
受众: 历史追溯 + 知识沉淀
```

---

## 报告增长规则

### 升 L 时机

- 新增独立 Capability → L1 → L2
- 新增 ≥3 个新 API → L2 → L3
- 新增 ≥3 stage 流转 → L3 → L4

### 降 L 时机

- 删除 Capability → L 降 1
- bug 修复（不改 spec）→ 不升 L

---

## 报告 vs 文档

| 维度 | Report | Document |
|------|--------|----------|
| 时效 | 短期（当日） | 长期（永久） |
| 读者 | 用户决策 | sub-agent 执行 |
| 形态 | 紧凑、结论先行 | 完整、可推导 |
| 归档 | 归档入 archive/ | 沉淀入 docs/INDEX.md |

---

## 反例

### 反例 1：L1 报告塞入完整 4 层文档

```
L1 Plan: 完整 4 层 + 4 维评分 + rot-scan  # ❌ 用户看不过来

正确: L1 Plan = 1 段结论 + 1 段 Capability + 1 段 3 路径
```

### 反例 2：L4 报告只写 1 段

```
L4 Archive: 1 段说明  # ❌ 缺失 4 工件

正确: L4 Archive = spec + plan + contracts/ + review + rot-scan + verify
```

---

## 关联引用

- [stage-card-protocol.md](state-card-protocol.md) — 状态卡流转
- [document-layer.md](document-layer.md) — 4 层文档
- V10 来源（开发期，已蒸馏）：见 V11 references 与 anti-patterns