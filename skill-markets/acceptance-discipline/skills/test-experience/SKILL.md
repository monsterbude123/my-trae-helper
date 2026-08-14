---
name: test-experience
description: DEPRECATED wrapper — 兼容旧触发词"写测试/mock 不生效/补 E2E/测试避坑"。实际逻辑已迁移至 acceptance-discipline（unit-test-agent + integration-test-agent）。本入口仅作向后兼容，加载时跳转到 acceptance-discipline。
status: deprecated
redirect_to: acceptance-discipline
---

# ⚠️ DEPRECATED — 已并入 acceptance-discipline

> 本 skill 是兼容壳，仅为保留旧触发词加载路径。**所有实际逻辑已迁移到 [`acceptance-discipline`](../../SKILL.md)**。
>
> 加载本文件后，请改读：
> - `acceptance-discipline/agents/unit-test-agent.md` — 单元测试验收 + Mock 策略 + Fixture 设计
> - `acceptance-discipline/agents/integration-test-agent.md` — 集成测试 + DB 测试
> - `acceptance-discipline/references/bad-test-cases.md` — 12 类 Bad Test 反模式
>
> 旧触发词映射：
> - "写测试"/"加测试"/"补测试" → `unit-test-agent`
> - "mock 不生效"/"fixture"/"测试报错" → `unit-test-agent` + `bad-test-cases`
> - "补 E2E"/"E2E 测试" → `e2e-audit-agent`（不在本 skill 内）

---

## 兼容性说明

```
2026-08-14 归档
本 skill 原内容（测试避坑经验库 / mock 策略矩阵 / 异步陷阱 / fixture 范式 / bad-test 识别）已整合为：
  - acceptance-discipline/agents/unit-test-agent.md     (核心原则+Mock+异步+Fixture)
  - acceptance-discipline/agents/integration-test-agent.md
  - acceptance-discipline/references/bad-test-cases.md   (12 类反模式案例)
  - acceptance-discipline/references/ai-agent-protocol.md (触发词路由)

请勿再独立维护本目录。新增测试经验请直接写入 acceptance-discipline 的 references/。
```