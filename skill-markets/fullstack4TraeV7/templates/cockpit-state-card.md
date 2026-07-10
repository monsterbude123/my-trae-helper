# 🛩️ 项目驾驶舱

> 项目级 Cockpit 状态卡。Agent 激活时首先读取。主 Agent 在阶段切换时更新。

## 活跃变更
| # | Change | 阶段 | Agent | 状态 | 最后活动 | 阻塞 |
|---|--------|------|-------|------|---------|------|
| 01 | {change-name} | {intake/proposal/specs/contract/design/dev/review/accept} | {agent-name} | 🟢/🟡/🔴 | {相对时间} | {阻塞项，无则填"无"} |

## 健康概览
- **活跃 change 数**: {N}
- **阻塞 change 数**: {N}
- **Spec 堆积风险**: 🟢 低（< 3）/ 🟡 中（3-5）/ 🔴 高（> 5）
- **最近完成**: {change-name}（{日期}）

## 项目级工件
- modules/: ✅ 最新 / ⚠️ 待同步
- prototypes/: ✅ 最新 / ⚠️ 待同步 / — 未初始化
- test-plan/: ✅ 已定义 / ⚠️ 待更新 / — 未初始化
- ARCHITECTURE.md: ✅ 最新 / ⚠️ 待更新
- contracts/: ✅ 最新 / ⚠️ 待同步

## 🐛 活跃缺陷

> 用户反馈通过 buglist.md 交流，Agent 同步摘要至此。详细对话存 buglist.md。

| # | Bug | 关联模块 | 严重度 | 状态 | 用户反馈 | 发现时间 |
|---|-----|---------|:---:|------|---------|---------|
| — | 无活跃缺陷 | — | — | — | — | — | —
