---
project: {project_name}
spec_version: "10.1"
last_updated: {ISO_8601}
total_changes: {N}
phases: [Plan, Spec, Contract, Implement, Review]
---

phase: {当前阶段}
status: {working | blocked | completed}
health: {🟢 | 🟡 | 🔴}

# 状态卡

## 当前阶段
{阶段名称}

## 阶段进度
| 阶段 | 状态 | 4维满分 | 备注 |
|------|------|--------|------|
| Plan | {✅ | ⏳ | ❌} | __ / 5.0 | |
| Spec | {✅ | ⏳ | ❌} | __ / 5.0 | |
| Contract | {✅ | ⏳ | ❌} | __ / 5.0 | |
| Implement | {✅ | ⏳ | ❌} | __ / 5.0 | |
| Review | {✅ | ⏳ | ❌} | __ / 5.0 | |

## 工件
| 工件 | 状态 |
|------|------|
| spec.md | {✅ | ⏳ | ❌} |
| contracts/ | {✅ | ⏳ | ❌} |
| 代码 | {✅ | ⏳ | ❌} |
| 测试 | {✅ | ⏳ | ❌} |

## 健康度
{健康状态描述}

## 阻塞
{阻塞描述，无则填"无"}

## 下一步
{下一步行动}

## 当前腐化状态（V10.4 新增）
- last_rot_scan: {date or "未跑"}
- rot_finds: {N} (PASS: {X}, WARN: {Y}, FAIL: {Z})
- rot_p0_ids: [...]      # 腐烂点 ID 列表（fail 项）
- rot_p1_ids: [...]      # 腐烂点 ID 列表（warn 项）
- rot_scanner: rot-detector | manual

> 触发条件: Phase 4 (Review) 末尾 + Accept 之前由 rot-detector 强制调用 proactive-scan.py

---

## 体积上限治理（V10.8 NEW）

> 根因：状态卡无限膨胀 → 上下文击穿；PowerShell `.Count` 含 BOM 元数据 → 行数统计不准。
> 治理：体积上限 + 正确统计方法 + 超标归档流程。

| 状态卡类型 | 上限 | 超标动作 |
|-----------|:---:|---------|
| per-change (.state-card.md) | 80 行 | 归档到 `_invalidated/v{N}/` → 从模板重建 |
| Cockpit 状态卡 | 150 行 | 归档旧卡 → 生成新卡 |

### 行数统计（PowerShell）

```powershell
# 正确：Measure-Object -Line（不计 BOM）
(Get-Content .state-card.md | Measure-Object -Line).Lines
# 错误：(Get-Content .state-card.md).Count  # 含 BOM 元数据，统计不准
```

### 超标归档流程

```
1. mv .state-card.md → _invalidated/v{N}/.state-card.md
2. 从 templates/state-card.md 复制新卡
3. 保留 phase/health/blocked 字段（手动回填）
4. 不保留历史记录段（已归档）
```

### 反例

- 现象：状态卡膨胀到 150 行 → agent 读取后上下文击穿，关键信息被淹没
- 根因：无体积上限，历史记录段不断累积
- 教训：状态卡 ≤80 行，超标归档到 `_invalidated/v{N}/`
- 来源：absorption-plan §七（状态卡体积上限治理）
