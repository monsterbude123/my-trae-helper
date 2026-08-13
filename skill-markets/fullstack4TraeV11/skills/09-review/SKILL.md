---
name: fullstack-09-review
description: "Stage 4 质疑式验收 — FAIL IS FAIL + 4 维评分 + 主动证伪 + DOC SYNC。触发词：review / 审查 / 验收 / scorecard / 4 维评分。"
stage: 4
parent: fullstack4traev11
depends_on:
  skills: [acceptance-discipline]
  stages: [3.5/real-verify]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/common-iron-rules.md
  scripts:
    - ../../scripts/stage-gate.py
    - ../../scripts/acceptance-audit.py
    - ../../scripts/code-hygiene.py
    - ../../scripts/orphan-detector.py
    - ../../scripts/dist-hash-check.py
    - ../../scripts/visual-content-check.py
---

# Stage 4 Review — 质疑式验收

> 第一性原则：**质疑式验收，FAIL IS FAIL**。有罪推定 + 证伪思维 + 证据不全就拦截。

## 立场

```
旧视角（盖章者）: 默认"已完成" → 找证据确认 → 找不到就放过
新视角（质疑式验收官）: 默认"未完成/有隐瞒" → 索要事实证据 → 证据不全就拦截
```

## 铁律（11 条 — V10 reviewer.md 蒸馏 + V11.2 00-03-diagnostic 蒸馏）

```
1. FAIL IS FAIL            — 不存在"非阻塞 FAIL"
2. SCORING IS DERIVED      — 总分 = (通过维度 / 适用维度) × 5.0
3. FOUR DIMENSIONS         — 代码(25%)/API(30%)/UIUX(25%)/边际(20%)，缺一不可
4. NO DOWNGRADE            — 不可验证标 N/A，不设"降级验收"
5. VERIFY UNDERSTANDING    — 机械验证 implementer "理解确认"
6. REVIEWER DOES NOT FIX   — 审查者不修代码，退回实现者
7. FUNCTIONAL CHECK        — 用户视角确认功能可用
8. CROSS-SESSION VERIFY    — 自评=self_attested，主上下文必二次抽检
9. 质疑式验收 SUITE        — ZERO TRUST + EVIDENCE MANDATORY + ACTIVE FALSIFICATION + REQUIREMENT TRACING（V10.12 SUITE）
10. 关键门禁套件           — SKEPTICAL VALIDATION（[protocol](../../references/skeptical-validation-protocol.md)）+ 产品视角 + 自动循环 + Test Plan Gate
11. 必读 5 件套(V11.2.1 NEW — 蒸馏自 V10 prototype-linkage.md)  Stage 9 Review 验收前必读:
    1. {原型 HTML 路径(如 docs/specs/changes/{id}/prototypes/design.{html,png,fig} 或项目原型目录)}
    2. docs/specs/changes/{id}/prototypes/design-prompt.md(布局骨架 + 组件清单 + 5 状态)
    3. docs/specs/changes/{id}/prototypes/ui-ux-logic.md(交互流 + 状态管理 + 错误边界)
    4. docs/specs/changes/{id}/design.md(如有,列 D-N 决策)
    5. docs/HANDOFF-DESIGNER.md(项目级 HANDOFF 索引,验证 HTML ↔ spec 双向映射无缺失)
  无 5 件套 → 不允许声称 ACCEPT
  反例: 2026-08-12 00-03-diagnostic 主上下文自评 ACCEPT 5.0/5.0,无 5 件套阅读
```

## 骨架流程（V10 reviewer 8 步 + V11 编排器门禁）

```
Step -2: 拆解验收基准（高风险清单）
Step -1: 跨 4 工件一致性分析（spec/contracts/prototypes/plan）

#### Step -1 子段:强制 prototype 对照表 + 必亲读 prototype 截图(V11.2.1 NEW — 蒸馏自 canvas-asset-folders Stage 4 Round 1/2 失败,V11.3 强化)

> **MUST**: Stage 4 review-report.md 必含 `## prototype ↔ implementation 对照表`,每行含:
> - spec AC(来自 spec.md §AC)
> - prototype 行号(design-prompt.md / ui-ux-logic.md / HTML prototype 行号)
> - 实施 file:line(实际代码位置)
> - 截图路径(实施后截图 vs prototype 截图)
> - 是否对齐(✅ / ⚠️ / ❌)
> - **fidelity 等级**(L1 wireframe / L2 mockup / L3 pixel-perfect,见 [SKILL.md §3.7.3 §8.1](../../SKILL.md))
> - **偏离理由**(如 ⚠️ 或 ❌,必填,见 [SKILL.md §3.7.3 §8.3](../../SKILL.md))
>
> **MUST**: 评审员必亲读 ≥ 2 张 prototype 截图(项目级指定,常见:prototype-overview.png / delete-block-modal.png / 等关键页面),**禁止只看实施截图不对比 prototype 截图**。
>
> **工具-人类分层判定(V11.3 NEW — 人工判定覆盖)**:
> - 工具检测(如 visual-content-check.py / vision-audit)反馈 PASS → **直接标记通过**
> - 工具检测 FAIL → **不阻塞**,仅作"提示"交给 agent 决策
> - agent 可酌情 PASS / FAIL,但必写理由([SKILL.md §3.7.3 §8.3](../../SKILL.md) 偏离理由)
> - **NEVER**:偏离理由空洞(如 "差不多"/"看起来对"/"感觉 OK")= 无证据放行
>
> **视觉差异阈值(V11.3 NEW — 人工判定覆盖)**:
> - 工具提示阈值:**5%**(从 V11.2 的 20% 收紧 4 倍)
> - L1 wireframe → 差异 ≤ 50% 可接受(仅布局 + 组件 + 5 状态对齐)
> - L2 mockup → 差异 ≤ 30% 可接受
> - L3 pixel-perfect → 差异 ≤ 5% 才 PASS
>
> **NEVER**:
> - "5 预设可见 + API PASS + 错误态 fallback = Stage 4 PASS"(2026-08-12 canvas-asset-folders Stage 4 Round 1/2 实际给的 PASS)
> - "Stage 1.5 prototype 已经验证过了,Stage 4 不需要再对照"
> - review-report.md 不含对照表 + 不亲读 prototype 截图
> - 偏离理由空洞("差不多"/"看起来对" 等不可证伪短语)

参见 [铁律 11 必读 5 件套](#)（含 design-prompt.md + ui-ux-logic.md + HTML + HANDOFF + design.md）。

Step 0:  硬门禁（测试 100% + 理解确认 + code-hygiene + contracts 稳定）
Step 0.5: 索要事实证据（双轨制）
  Step 0.5.1 必读 4 件套(V11.2 NEW — 蒸馏自 00-03-diagnostic)
    - 主上下文验收前必 Read 4 件套(详见铁律 11)
    - 缺 1 件 → 标记 FAIL,禁止声称 ACCEPT
    - 4 件齐全 → 继续 4 维评分
Step 1:  4 维验收（代码/API/UIUX/边际）
Step 1.5: 主动证伪（高风险清单核查）
Step 2:  功能效果验证 + 需求溯源 + Test Plan 前置门禁
Step 2.5: 产品侧功能有效性验收（V10.12 NEW — 3 问判定）
Step 2.6: 自动循环（Round 1 退回 / Round 2 上报用户 / Round 3+ rescue hatch）
Step 3:  评分（≥ 4.0 + 任一维度 0 分 = REJECT）
Step 4:  DOC SYNC
Step 5:  知识提取（spec-knowledge-extract.py）
```

## 关键产物

| 产物 | 路径 |
|------|------|
| 4 维评分报告 | `docs/specs/changes/{id}/review-report.md` |
| 证据链 | file:line + 命令 + 截图 |

## 4 维评分公式

```
总分 = (通过维度 / 适用维度) × 5.0
- 任一维度 0 分 = 🛑 REJECT
- 总分 ≥ 4.0 才 PASS
```

## 反例（4 条索引）

| # | 反例 | V10 来源 |
|:---:|------|---------|
| 1 | "非阻塞 FAIL"放水 | reviewer 铁律 1 |
| 2 | reviewer 帮忙修代码 | reviewer 铁律 6 |
| 3 | 编造测试覆盖 | V10.12 关键门禁套件 |
| 4 | 自动循环 Round 3+ 继续绕 | V10.12 Step 2.6 |

## 参考索引

- [README.md](README.md)
- [four-dimension-scoring.md](references/four-dimension-scoring.md)
- [evidence-3-layer.md](references/evidence-3-layer.md)
- [skeptical-acceptance.md](references/skeptical-acceptance.md)
- [multi-round-revision.md](references/multi-round-revision.md)
- [review-report-template.md](templates/review-report-template.md)
- V10 reviewer.md: `V10 来源` (已蒸馏到本文档)
- V10 reviewer-templates.md: `V10 来源` (已蒸馏到本文档)
- V10 acceptance-gates-v10.md: `V10 来源` (已蒸馏到本文档)
