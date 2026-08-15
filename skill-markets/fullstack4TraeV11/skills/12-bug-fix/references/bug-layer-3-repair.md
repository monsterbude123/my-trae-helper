# Bug 处理分层决策框架 — Layer 3 修复分层

> **V11.8.3 设计原则**：本层回答"如何修复单个 bug"，继承 V10 debugger + V11 e2e 先行 + Ponytail 最小化修复。

---

## 核心思维模型

```
修复分层决策树（单 bug）
├── 根因定位：先定位再动手
│   └── 6 层排查：网络 → 接入 → 应用 → 数据 → 集成 → 客户端
│
├── 修复范围：最小改动原则
│   └── Ponytail 决策阶梯：改 src < 改 skill-markets < 改架构
│
├── 验证策略：e2e 先行
│   └── 必初始 FAIL → 证明 bug 真实存在 → 修后 PASS
│
└── 闭环回写：状态同步
    └── bug 单 + index + state-card 三文件
```

---

## §L3.1 根因定位（6 层排查）

> **铁律**：根因不明不修复。先定位再动手。

| 层 | 检查内容 | 工具 |
|----|---------|------|
| **网络层** | DNS / TLS / proxy / 代理配置 | curl / devtools network |
| **接入层** | API gateway / 路由 / 限流 | devtools / server log |
| **应用层** | 业务逻辑 / 中间件 / 状态 | debugger / log |
| **数据层** | DB schema / 索引 / 事务 | DB client / log |
| **集成层** | 第三方服务 / SDK | vendor log |
| **客户端层** | UI / 缓存 / localStorage | devtools / playwright |

**GitNexus impact**：修复前必跑 impact 分析，了解影响范围。

---

## §L3.2 修复范围决策（Ponytail 最小化）

```
优先级阶梯（最小改动优先）:
  1. 改配置 / 环境变量（最小）
  2. 改单文件代码
  3. 改多文件（同模块）
  4. 改跨模块接口
  5. 改架构（最后手段）

决策铁律:
  IF 改动能解决 → 不改架构
  IF 单文件能解决 → 不改多文件
  IF 同模块能解决 → 不跨模块
```

---

## §L3.3 验证策略（e2e 先行 + TDD）

### 3.3.1 e2e 先行铁律

```
Step 1: 写 e2e 测试（复现 bug）
Step 2: 运行 → 必 FAIL（证明 bug 真实存在）
        IF INITIAL PASS:
            → 不是 bug，回退到 OPEN 状态
            → 重新审视预期
Step 3: 修复代码
Step 4: 运行 → 必 PASS
Step 5: 回归验证（确保无新增 bug）
```

### 3.3.2 TDD 循环

```
RED → 写失败的测试
GREEN → 最小修改让测试通过
REFACTOR → 清理代码（不改变行为）
```

---

## §L3.4 修复后状态同步

| 文件 | 同步内容 | 触发 |
|------|---------|------|
| Bug 单 .md | status: OPEN → FIXED → VERIFIED → CLOSED | 修复完成 |
| index.md | 列表状态更新 | 同步 |
| .state-card.md | 阶段进度 | 同步 |

**脚本化**：`close-bug.sh BUG-NNN <agent-id>` 一键三文件同步。

---

## §L3.5 质疑性校验（P0/P1 bug）

> 参考：[skeptical-validation-protocol.md](../../references/skeptical-validation-protocol.md)

P0/P1 级别 bug 修复后，必须跑质疑性校验：

```
1. 复现场景是否唯一？（是否存在其他触发路径）
2. 边界条件是否覆盖？（空值/极端值/并发）
3. 回归影响是否评估？（GitNexus impact）
4. 是否引入新风险？（依赖变更/性能影响）
```

---

## §L3.6 修复层产出

| 产出 | 用途 | 下一层 |
|------|------|--------|
| 修复代码 | 解决问题 | Layer 4 验收 |
| e2e 测试 | 回归资产 | 持续维护 |
| 根因报告（可选） | 知识沉淀 | 归档 |
| 状态同步 | 进度追踪 | Layer 4 收敛 |

---

## 反模式

| # | 反例 | 问题 |
|:--:|------|------|
| L3-1 | 跳过 e2e 先行直接修 | 无法证明修复有效 |
| L3-2 | 跨层过度修复 | 违反 Ponytail，风险大 |
| L3-3 | 修复未回写 bug 单 | 状态不同步 |
| L3-4 | 根因不明就动手 | 可能修错位置 |

---

## 关联

- 上一步：[bug-layer-2-severity.md](bug-layer-2-severity.md) — 严重性分层
- 下一步：[bug-layer-4-convergence.md](bug-layer-4-convergence.md) — 收敛分层
- 详细：[six-layer-diagnosis.md](six-layer-diagnosis.md) / [cross-layer-fix.md](cross-layer-fix.md)