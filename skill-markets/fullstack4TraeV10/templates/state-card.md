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
