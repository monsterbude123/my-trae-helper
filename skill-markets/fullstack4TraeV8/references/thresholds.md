# 阈值配置（Thresholds）

> 所有体积/行数/字符数阈值统一在此。修改后全技能生效。

## 内容型工件父文件

| 工件 | 默认参考 | 浮动 | 校准依据 |
|------|:---:|:---:|------|
| proposal.md 父文件 | 80 行 | ±30% | 7 capability，保留余量 |
| spec.md 父文件 | 80 行 | ±20% | 7 capability + 10 Invariants + 6 E2E  |
| design.md 父文件 | 80 行 | ±30% | 决策数驱动，3-5 决策约 40 行 |
| contracts/api 父文件 | 80 行 | ±30% | 7 端点索引 |
| contracts/domain 父文件 | 80 行 | ±40% | 13 实体索引 |
| contracts/events 父文件 | 80 行 | ±30% | 5 事件组索引  |
| contracts/validation 父文件 | 80 行 | ±30% | 4 校验分组  |

> 父文件体量准则: 以"2 分钟读完能讲清全景"为准，数字是参考不是硬切断。→ [progressive-disclosure.md](progressive-disclosure.md)

## 内容型工件拆分触发

| 触发条件 | 默认值 | 说明 |
|---------|:---:|------|
| proposal 单文件上限 | 150 行 | 超过则拆为父文件+子文件 |
| spec 拆分触发 | — | 场景数量多 / capability 独立复杂 / 多人协作 |
| design 拆分触发 | 决策 > 3 个 | 或涉及多模块 |
| contracts 拆分触发 | API 端点 > 5 或实体 > 5 | 或单文件 > 100 行 |

## 累积型工件硬上限

| 工件 | 硬上限 | 超标动作 |
|------|:---:|------|
| per-change .state-card.md | 80 行 | 不追加，执行重置 |
| Cockpit .state-card.md | 150 行 | 修剪已完成 change 行 |
| DECISIONS.md | 80 行 | 已决议项 → 归档折叠区 |
| report-{0X}.md | 100 行 | 单文件格式固定 |
| closure-checklist.md | 100 行 | 已完成 Stage → 折叠 |
| buglist.md | 100 行 | 已修复 → 折叠区 |
| modules/{module}.md 变更记录表 | 100 行 | 保留最近 30 条 |

> 累积型标准: 单模块不超过 300 行。超标则拆分子文档。→ [artifact-lifecycle.md](artifact-lifecycle.md)

## 委派经济

| 约束 | 默认参考 |
|------|:---:|
| 委派任务描述 | ~200 字符 |
| 委派 prompt 总大小 | ~1KB |
| Completion Report | ~800 字符 |

> → [context-economy.md](context-economy.md)

## Visual Gate

| 约束 | 默认参考 |
|------|:---:|
| 单页面截图 | 含 5 状态（idle/loading/data/empty/error） |
| prototype 比对覆盖率阈值 | ≥ 80% → PASS |
| vision-audit 不可用降级 | AI 直读 PNG，标注"降级验收" |

## 代码质量（非文档）

| 约束 | 默认值 |
|------|:---:|
| 单文件 | 800 行正常 / 1000 行阻断 |
| 函数 | < 80 行 |

> 代码质量不受此配置约束，此处仅为参考汇总。
