# 铁律 — README.md 详情

> 父文件：[../README.md](../README.md)
> 来源：原 README.md 第 91-103 行（保留信息密度）

---

## 完整铁律（10 条）

```
1. EXPLORE FIRST       — 探索项目现状后再规划，禁止凭空设计
2. SUBAGENT ONLY       — 所有探索操作委派子代理，禁止主上下文直行
3. IMPACT BY TOOL      — 影响面评估用 GitNexus impact()，禁止手动 grep
4. DEDUP BY ATOM       — 需求去重，> 50% 重叠 → 合并，< 50% → 新建
5. PURGE ON REFACTOR   — 重构场景先调 spec-purge.py 清除旧产物
6. DUAL SEARCH         — 主上下文不直行代码 = 主上下文不直行探索
7. SKEPTICAL VALIDATION — P0/P1 规划按 [skeptical-validation-protocol.md](../../../references/skeptical-validation-protocol.md) 走质疑性校验（4 维度 + 强制声明格式）
8. PLAN ≤ 80 LINES     — plan.md ≤ 80 行，Capabilities ≤ 5 项
9. CLOSURE ≤ 5 STEPS   — P0 闭环步骤 ≤ 5 步
10. NEVER ACT ON PLAN  — plan.md 是规划不是实施
```

---

## 关联引用

- 父文件：[../README.md](../README.md)
- SKILL.md：[../SKILL.md](../SKILL.md)
