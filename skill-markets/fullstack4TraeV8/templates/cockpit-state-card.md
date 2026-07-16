# 🛩️ 项目驾驶舱

> 项目级 Cockpit 状态卡。Agent 激活时首先读取。主 Agent 在阶段切换时更新。
>
> **编辑安全协议**：
> - 每个 `<!-- SECTION: xxx -->` 是独立编辑单元，Agent 只能修改对应 section
> - Active changes 表行用 SearchReplace 精确匹配，不允许全表重写
> - 两个 Agent 不同时编辑此文件（主上下文串行化 cockpit 写操作）

<!-- SECTION: active-changes -->
## 活跃变更
| # | Change | 阶段 | Agent | 状态 | 最后活动 | 阻塞 |
|---|--------|------|-------|------|---------|------|
| 01 | {change-name} | {phase} | {agent-name} | 🟢/🟡/🔴 | {相对时间} | {阻塞项，无则填"无"} |
<!-- /SECTION: active-changes -->

<!-- SECTION: health -->
## 健康概览
- **活跃 change 数**: {N}
- **阻塞 change 数**: {N}
- **Spec 堆积风险**: 🟢 低（< 3）/ 🟡 中（3-5）/ 🔴 高（> 5）
- **最近完成**: {change-name}（{日期}）
- **文档健康**: 🟢 正常 / 🟡 {N} 个文件接近体积上限 / 🔴 状态卡 > 150 行（见 [artifact-lifecycle.md](../references/artifact-lifecycle.md) §4）
<!-- /SECTION: health -->

<!-- SECTION: artifacts -->
## 项目级工件
- modules/: ✅ 最新 / ⚠️ 待同步
- prototypes/: ✅ 最新 / ⚠️ 待同步 / — 未初始化
- test-plan/: ✅ 已定义 / ⚠️ 待更新 / — 未初始化
- ARCHITECTURE.md: ✅ 最新 / ⚠️ 待更新
- contracts/: ✅ 最新 / ⚠️ 待同步
<!-- /SECTION: artifacts -->

<!-- SECTION: bugs -->
## 🐛 活跃缺陷

> 用户反馈通过 buglist.md 交流，Agent 同步摘要至此。详细对话存 buglist.md。

| # | Bug | 关联模块 | 严重度 | 状态 | 用户反馈 | 发现时间 |
|---|-----|---------|:---:|------|---------|---------|
| — | 无活跃缺陷 | — | — | — | — | — | — |
<!-- /SECTION: bugs -->
