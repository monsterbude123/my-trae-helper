# 铁律 — README.md 详情

> 父文件：[../README.md](../README.md)
> 来源：原 README.md 第 79-92 行（保留信息密度）

---

## 完整铁律（10 条）

```
1. 意图不明不路由       — 必须识别意图才能路由（5 种意图之一）
2. 未勘察不初始化       — 项目级 AGENTS.md / docs/ / .trae/rules/ 必须先 Glob 1 次
3. 状态卡不立不启动     — 每个 change 必须有状态卡才能进入下一 stage
4. Bug 录入必询问       — 用户反馈问题必问"是否作为 bug 单录入"（不默认创建）
5. 路由决策不臆断       — 模糊意图必 AskUserQuestion（不靠经验猜）
6. 路由必记录           — 路由决策表必须写入状态卡 next_stage
7. 编排器依赖空不空路由 — intake.skills/stages 都是空（自身是入口）
8. NEVER 默认创建 bug 单 — 用户拒绝时绝不强制创建
9. NEVER 跳过状态卡     — change / bug / project 三类必初始化其一
10. NEVER 静默路由      — 路由决策必须有 evidence（触发词 / Glob 命中 / 用户明确）
```

---

## 关联引用

- 父文件：[../README.md](../README.md)
- SKILL.md：[../SKILL.md](../SKILL.md)
