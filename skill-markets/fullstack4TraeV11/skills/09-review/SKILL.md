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

## 铁律（10 条 — V10 reviewer.md 蒸馏 + V11.2 00-03-diagnostic 蒸馏）

```
1. FAIL IS FAIL            — 不存在"非阻塞 FAIL"
2. SCORING IS DERIVED      — 总分 = Σ(维度分数 × 维度权重) / Σ(维度权重)（加权平均,详见 §4 维评分公式）
3. FOUR DIMENSIONS         — 代码(25%)/API(30%)/UIUX(25%)/边际(20%)，缺一不可
4. NO DOWNGRADE            — 不可验证标 N/A，不设"降级验收"
5. VERIFY UNDERSTANDING    — 机械验证 implementer "理解确认"
6. REVIEWER DOES NOT FIX   — 审查者不修代码，退回实现者
7. FUNCTIONAL CHECK        — 用户视角确认功能可用
8. CROSS-SESSION VERIFY    — 自评=self_attested，主上下文必二次抽检
9. 质疑式验收 SUITE        — ZERO TRUST + EVIDENCE MANDATORY + ACTIVE FALSIFICATION + REQUIREMENT TRACING（V10.12 SUITE）
10. 关键门禁套件           — SKEPTICAL VALIDATION（[protocol](../../references/skeptical-validation-protocol.md)）+ 产品视角 + 自动循环 + Test Plan Gate + 必读 5 件套（[SKILL.md §3.7.3.5](../../SKILL.md) 指针引用 — prototype ↔ implementation 对照表 + fidelity 等级 + 偏离理由 + 评审疏漏二次再犯升级用户）
```

## 骨架流程（V10 reviewer 8 步 + V11 编排器门禁）

```
Step -2: 拆解验收基准（高风险清单）
Step -1: 跨 4 工件一致性分析（spec/contracts/prototypes/plan）

#### Step -1 子段: prototype ↔ implementation 对照(指针 → 总管 §3.7.3)

> Stage 4 review-report.md 必含 `## prototype ↔ implementation 对照表`(字段定义 + fidelity 等级 + 偏离理由 + 工具-人类分层判定 + 视觉差异阈值)完整见 [SKILL.md §3.7.3](../../SKILL.md)。Stage 9 仅强调两点:
> 1. 评审员必亲读 ≥ 2 张 prototype 截图 + 实施截图,**禁止只看实施截图不对比 prototype 截图**
> 2. 视觉差异阈值 **5%**(L1 wireframe ≤50% / L2 mockup ≤30% / L3 pixel-perfect ≤5%)
> **NEVER**:"5 预设可见 + API PASS + 错误态 fallback = Stage 4 PASS"(2026-08-12 canvas-asset-folders Stage 4 Round 1/2 实际给的 PASS)

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

| 产物 | 路径 | 状态卡字段 |
|------|------|----------|
| 4 维评分报告 | `docs/specs/changes/{id}/review-report.md` | `stage_review.review_report_path` 必须指向此文件 |
| 证据链 | file:line + 命令 + 截图 | `stage_review.evidence_paths` 数组 |
| 失败标签(如 REJECT) | `review-report.md` §失败标签 | `stage_review.reject_label` 必填 |

> **MUST**: Stage 4 Review 4 维评分是 Stage 4 **真相源**(Article XII),状态卡 `stage_review.*` 字段必须由主上下文亲自同步自 review-report.md(§5.8 子代理禁直接 Edit)。

## 4 维评分公式

**加权平均公式**: `总分 = Σ(维度分数 × 维度权重) / Σ(维度权重)`

- 维度权重: 代码 25% / API 30% / UIUX 25% / 边际 20%
- 任一维度 0 分 = 🛑 REJECT
- 总分 ≥ 4.0 才 PASS
- N/A 不计入分母(不可验证才标 N/A + 必填理由)
- 完整公式 + 反例 A/B/C 详见 [references/four-dimension-scoring.md](references/four-dimension-scoring.md)

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
