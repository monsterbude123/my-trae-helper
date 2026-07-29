# 异常报告（Report Growth）

> V8 遗产。Agent 异常处理的结构化分级和技能生长机制。

## L1-L4 异常分级

| 等级 | 范围 | 示例 | 处理 |
|:---:|------|------|------|
| L1 | 文件系统 | 文件缺失、权限不足 | Retry 1 次 → 记录 → 继续 |
| L2 | Agent 执行 | 工具调用失败、解析错误 | 换参数/策略 → 最多 3 次 → 阻塞报告 |
| L3 | 状态不一致 | state-card 与实际不一致、漂移 | 汇报用户 → 等待决策 |
| L4 | 外部依赖 | GitNexus 不可用、API 不可达 | 降级运行 + 标注风险 → 汇报 |

## Report 格式

所有 Agent 异常写入 `.trae/logs/report-growth.jsonl`：

```jsonl
{"timestamp": "2026-07-21T14:30:00", "agent": "implementer", "phase": "TDD-GREEN", "level": "L2", "error": "test_foo(): assertion error", "root_cause": "domain model field type mismatch", "action": "revert to contract definition, fix test expectation"}
```

## 累积升级规则

```
同一 agent 同一 phase 连续 3 次 L2+ 异常
  → 升级到 L3: 汇报用户 + 标记 🔴 高风险
  → 触发 process review: 检查 agent 流程/规则是否需要改进
```

## Agent 异常处理协议

```
异常发生:
  1. 不要静默失败 ← 必须写入 report-growth.jsonl
  2. 不要猜测修复 ← 根因不明确时停止，汇报用户
  3. 不要隐藏异常 ← 在 Completion Report 中标注异常数
  4. 不要无限重试 ← 同一操作最多 3 次，仍失败→阻塞报告
```
