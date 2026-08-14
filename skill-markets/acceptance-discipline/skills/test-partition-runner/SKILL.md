---
name: test-partition-runner
description: DEPRECATED wrapper — 兼容旧触发词"测试卡住/测试阻塞/分区测试/坏测试识别"。实际逻辑已迁移至 acceptance-discipline（blockage-resolver-agent）。本入口仅作向后兼容，加载时跳转到 acceptance-discipline。
status: deprecated
redirect_to: acceptance-discipline
---

# ⚠️ DEPRECATED — 已并入 acceptance-discipline

> 本 skill 是兼容壳，仅为保留旧触发词加载路径。**所有实际逻辑已迁移到 [`acceptance-discipline`](../../SKILL.md)**。
>
> 加载本文件后，请改读：
> - `acceptance-discipline/agents/blockage-resolver-agent.md` — 测试阻塞应急 + 分区定位
> - `acceptance-discipline/references/bad-test-cases.md` — 坏测试识别（12 类反模式）
>
> 旧触发词映射：
> - "测试卡住"/"测试阻塞"/"测试挂起" → `blockage-resolver-agent`
> - "分区测试"/"partition test" → `blockage-resolver-agent`（按目录分区）
> - "坏测试"/"bad test" → `blockage-resolver-agent` + `bad-test-cases`

---

## 兼容性说明

```
2026-08-14 归档
本 skill 原内容（分区测试 + 4 类阻塞模式 + 坏测试识别 + 4 类修复方案 + 反馈模板 + 决策树）已整合为：
  - acceptance-discipline/agents/blockage-resolver-agent.md  (核心响应 + 分区协议)
  - acceptance-discipline/references/bad-test-cases.md        (12 类 Bad Test 案例)

按 TS/JSX 测试栈特有的 fix 示例（ReadableStream/async generator）保留在本目录原 .md 中供查阅，但加载本 skill 应改走 acceptance-discipline。
```