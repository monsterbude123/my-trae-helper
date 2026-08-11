# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 0 Plan 从 V10 `agents/planner.md` + scenarios.md §3 新增功能 + §2 迷雾消除蒸馏实战智慧。

---

## V10 实战反例（4 条）

### 蒸馏 1：3 路并行未并行（V10 planner.md 真实失误）

**实战场景**（V10 planner.md 蒸馏）:
- 主上下文委派子代理 A 文档探索 → 等返回 → 再委派子代理 B 代码 → 等返回 → 再委派子代理 C 依赖
- 串行执行浪费时间（3x 串行 vs 1x 并行）
- 子代理 C 实际未启动（依赖 A 的产出）

**根因**: 不熟悉 Task 工具的并行调用。

**V11 改进**: three-path-exploration.md Step 3 明确"同时委派 3 个 sub-agent（并行）"+ 反模式 B（串行而非并行）。

**V10 源**: agents/planner.md Step 3。

---

### 蒸馏 2：planner 探索跑主上下文（V10 Article IV 违规）

**实战场景**（V10 蒸馏）:
- 主上下文亲自 Read docs/INDEX.md → Read ARCHITECTURE.md → ...
- 上下文击穿（10+ 文件 Read 进入主上下文）

**根因**: 不理解 Article IV 委派纪律 = 主上下文不直行代码。

**V11 改进**: 铁律 2（SUBAGENT ONLY）+ 反例 A（主上下文直行 Read）+ three-path-exploration.md "探索过程不在主上下文进行（防止上下文击穿）"。

**V10 源**: agents/planner.md Step 3 "约束: 探索过程 SHALL NOT 在主上下文中进行"。

---

### 蒸馏 3：SKEPTICAL VALIDATION 缺失（V10.12 NEW）

**实战场景**（V10.12 蒸馏，2026-08-07）:
- planner 接到"重构 X" → 立即进入 3 路探索 → 出 plan.md
- 未质疑"重构"分类是否正确 → 用户实际要的是 Bug 修复或新功能

**根因**: P0/P1 决策前未走 skeptical-validation-protocol。

**V11 改进**: 铁律 7（SKEPTICAL VALIDATION）+ Step 1 意图识别 +4 类意图分支（plan 不处理 Bug 修复和文档更新）。

**V10 源**: agents/planner.md 铁律 6（SKEPTICAL VALIDATION V10.12 NEW）+ references/skeptical-validation-protocol.md。

---

### 蒸馏 4：去重仅按"功能名"对比（V10 实战失误）

**实战场景**（V10 蒸馏）:
- 历史 change: "用户认证"（archive/done/2026-07-15-user-auth/）
- 当前需求: "用户登录"
- 判定："功能不同" → 新建 change
- 实际：Capabilities 重叠 80%（密码哈希 / Token 签发等）

**根因**: 按"功能名"对比粒度太粗，未拆原子能力。

**V11 改进**: 铁律 4（DEDUP BY ATOM）+ references/dedup-by-atom.md（原子级对比算法 + 重叠度计算）+ 反例 A（按功能名对比）。

**V10 源**: agents/planner.md Step 2 + 铁律 4。

---

## V10 实战蒸馏经验（5 条）

| 经验 | V10 来源 | V11 落地位置 |
|------|---------|------------|
| 3 路并行必须并行 | planner.md Step 3 | three-path-exploration.md 反模式 B |
| 探索不在主上下文 | planner.md Step 3 约束 | 铁律 2 + 反例 A |
| SKEPTICAL 必走 | planner.md 铁律 6（V10.12） | 铁律 7 + Step 1 |
| 原子级去重 | planner.md Step 2 + 铁律 4 | references/dedup-by-atom.md + 反例 A |
| 重构先 purge | planner.md Step 4 + 铁律 5 | 铁律 5 + Step 4 + 反例 3 |

---

## V10 来源溯源（开发期，部署前可删）

> ⚠️ 本节记录 V10 来源，仅供 V11 维护者追溯。**V11 部署时不依赖 V10**——V10 内容已蒸馏进 V11 references/anti-patterns。

| V10 来源 | 蒸馏到 V11 位置 |
|---------|---------------|
| V10 planner.md | → 本文档蒸馏 1+2+3+4 + `../../02-plan/SKILL.md` + `workflows/three-path-exploration.md` |
| V10 scenarios.md §3 新增功能完整链 | → 本文档蒸馏 1+2+3+4 |
| V10 sub-agent-rules.md（主上下文必读） | → 主上下文委派纪律 |
| V10 project-structure.md | → 目录结构 / 命名规则 |
| V10 skeptical-validation-protocol.md | → 本文档蒸馏 3 + `../../02-plan/SKILL.md` 铁律 7 |
| V10 acceptance-gates-v10.md | → `../../03-test-plan/references/coverage-rules.md` + `../../09-review/references/four-dimension-scoring.md` |

---

## 关联引用

- [SKILL.md](../SKILL.md) — Stage 0 入口
- [README.md](../README.md) — 阶段元信息
- [three-path-exploration.md](../workflows/three-path-exploration.md) — 3 路探索
- [plan-clarification.md](../workflows/plan-clarification.md) — 计划追问
- 其他反例: [01-no-exploration.md](01-no-exploration.md) / [02-grep-instead-of-gitnexus.md](02-grep-instead-of-gitnexus.md) / [03-refactor-without-purge.md](03-refactor-without-purge.md) / [04-plan-too-long.md](04-plan-too-long.md)
