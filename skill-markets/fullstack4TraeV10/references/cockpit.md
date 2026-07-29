# Cockpit 驾驶舱

> 项目状态总览 + 知识发现协议。Agent 启动第一站。

---

## 何时更新

| 时机 | 动作 |
|------|------|
| Intake 完成后 | 初始化状态卡 |
| 每次阶段切换 | 更新 phase + health |
| 阻塞发生时 | 记录阻塞原因 + 健康度降级 |
| Review 完成后 | 标记完成 + 健康度恢复 |

---

## 状态卡字段

```yaml
phase: {Intake|Spec|Contract|Implement|Review|Accept}
status: {working|blocked|completed}
health: {🟢 on-track | 🟡 degraded | 🔴 blocked}
blocked_by: {无 | 具体阻塞描述}
next: {下一步动作}
```

---

## 健康度判定

| 状态 | 条件 |
|------|------|
| 🟢 | 按阶段推进，无阻塞 |
| 🟡 | 有已知阻塞但可并行推进其他工作 |
| 🔴 | 当前阶段完全阻塞，无法继续 |

---

## 状态卡约束
- ≤ 40 行
- 一个项目最多 1 个 `.state-card.md`（项目级）+ 每个 feature 1 个（feature 级）
- 项目级记录整体状态，feature 级记录单 feature 状态

---

## 知识发现协议（Agent 启动必须执行）

> 协议定义在 [project-structure.md](project-structure.md) §知识发现协议。

```
1. docs/specs/.state-card.md      → 当前状态
2. docs/INDEX.md                  → Spec 全景 + 模块映射
3. docs/ARCHITECTURE.md           → 架构约束
4. GitNexus impact()              → 影响面评估
5. docs/specs/{feature}/spec.md   → 具体 Spec
6. docs/specs/{feature}/define.md → 任务定义
```

**项目级 `docs/INDEX.md` 缺失时的处理**：
Intake 阶段检测到 INDEX.md 不存在 → 生成初始版本（扫描所有 `docs/specs/*/spec.md` → 填充 Active Specs 表）。INDEX.md 由 reviewer DOC SYNC 维护。
