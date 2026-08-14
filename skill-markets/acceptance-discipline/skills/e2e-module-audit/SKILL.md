---
name: e2e-module-audit
description: DEPRECATED wrapper — 兼容旧触发词"跑 E2E/全量/回归/CI/发版/页面有问题"。实际逻辑已迁移至 acceptance-discipline（e2e-audit-agent 双工作流）。本入口仅作向后兼容，加载时跳转到 acceptance-discipline。
status: deprecated
redirect_to: acceptance-discipline
---

# ⚠️ DEPRECATED — 已并入 acceptance-discipline

> 本 skill 是兼容壳，仅为保留旧触发词加载路径。**所有实际逻辑已迁移到 [`acceptance-discipline`](../../SKILL.md)**。
>
> 加载本文件后，请改读：
> - `acceptance-discipline/agents/e2e-audit-agent.md` — E2E 双工作流（Workflow A 批量验收 + Workflow B 即时诊断）
> - `acceptance-discipline/references/ai-agent-protocol.md` — AI Agent 行为契约
>
> 旧触发词映射：
> - "跑 E2E"/"全量"/"回归"/"CI"/"发版" → Workflow A（e2e-audit-agent）
> - "XX 页面有问题"/"修一下"/"帮我看看" → Workflow B（即时诊断）
> - 视觉验收 → `vision-audit/scripts/vision-audit.mjs`

---

## 兼容性说明

```
2026-08-14 归档
本 skill 原内容（双工作流 + 截图组织 + 日志关联 + 诊断推理引擎 + 视觉验收集成）已整合为：
  - acceptance-discipline/agents/e2e-audit-agent.md   (双工作流 + 6 步即时诊断闭环)
  - acceptance-discipline/references/ai-agent-protocol.md (决策树)

辅助脚本继续保留在原目录（e2e-module-audit/scripts/*），但主调用方应为 acceptance-discipline。
```

## 历史文件保留

`workflow-a-batch.md` / `workflow-b-instant.md` / `infra-shared.md` / `conventions.md` 等历史参考文档保留在原 `e2e-module-audit/` 根目录供查阅，不再独立加载。