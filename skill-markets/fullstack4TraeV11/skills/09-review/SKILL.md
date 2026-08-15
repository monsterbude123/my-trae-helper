---
name: fullstack-09-review
description: "Stage 4 质疑式验收 — AC 核销门禁(Gate) + 主动证伪 + DOC SYNC。触发词：review / 审查 / 验收 / AC 核销 / 核销矩阵。"
stage: 4
parent: fullstack4traev11
depends_on:
  skills: [gitnexus4Trae, acceptance-discipline]
  stages: [3.5/real-verify]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/common-iron-rules.md
    - ../../references/stage-08-real-verify-battle-report.md
  scripts:
    - ../../scripts/stage-gate.py
    - ../../scripts/ac-gate.py
    - ../../scripts/acceptance-audit.py
    - ../../scripts/code-hygiene.py
    - ../../scripts/orphan-detector.py
    - ../../scripts/dist-hash-check.py
    - ../../scripts/visual-content-check.py
---

# Stage 4 Review — 质疑式验收(AC 核销门禁)

> 第一性原则：**质疑式验收，FAIL IS FAIL**。有罪推定 + 证伪思维 + 证据不全就拦截。
>
> **V11.6.0 起:验收是 Guard/Gate 层的机械门禁,不是评分。** 判定唯一权威源 = [ac-gate.py](../../scripts/ac-gate.py) 的 AC 核销矩阵(G1-G5),评分制已废除(历史文档见 [four-dimension-scoring.md](references/four-dimension-scoring.md) 废弃声明)。

## 立场

```
旧视角（盖章者）: 默认"已完成" → 找证据确认 → 找不到就放过
新视角（质疑式验收官）: 默认"未完成/有隐瞒" → 索要事实证据 → 证据不全就拦截
```

## 铁律（11 条 — V10 reviewer.md 蒸馏 + V11.2 00-03-diagnostic 蒸馏 + V11.6.0 门禁化）

```
1. FAIL IS FAIL            — 不存在"非阻塞 FAIL"
2. GATE NOT SCORE          — 验收 = 逐 AC 核销门禁(任一 ❌ = BLOCK),禁止评分/加权/凑分(V11.6.0)
3. BASELINE FIRST          — 验收基准必从 spec AC + ui-ux-logic 交互流派生(Step -2),无基准 = BLOCK,禁止退回默认清单
4. NO DOWNGRADE            — 不可验证退回上游补基准,不设"N/A 降级/按比例放行"
5. VERIFY UNDERSTANDING    — 机械验证 implementer "理解确认"
6. REVIEWER DOES NOT FIX   — 审查者不修代码，退回实现者
7. FUNCTIONAL CHECK        — 用户视角确认功能可用
8. CROSS-SESSION VERIFY    — 自评=self_attested，主上下文必二次抽检
9. 质疑式验收 SUITE        — ZERO TRUST + EVIDENCE MANDATORY + ACTIVE FALSIFICATION + REQUIREMENT TRACING(V10.12 SUITE)
10. 关键门禁套件           — SKEPTICAL VALIDATION([protocol](../../references/skeptical-validation-protocol.md))+ 产品视角 + 自动循环 + Test Plan Gate + 必读 5 件套([SKILL.md §3.7.3.5](../../SKILL.md) 指针引用 — prototype ↔ implementation 对照表 + fidelity 等级 + 偏离理由 + 评审疏漏二次再犯升级用户)
11. MACHINE GATE           — 判定必跑 ac-gate.py(G1-G5 机械断言),人工只填矩阵不判结论;脚本 exit ≠ 0 = BLOCK,禁止"脚本拦了我放行"
12. **GITNEXUS FIRST（V11.8.5 NEW — 蒸馏自 bug-fix 不使用 gitnexus）** — 验收前必跑 GitNexus detect_changes()/impact() 查本次变更代码范围，禁止只看 git diff 不知道改了什么（Article V 不可降级）
```

## 骨架流程（V10 reviewer 8 步 + V11 编排器门禁）

```
Step -3: GitNexus 变更范围评估（V11.8.5 NEW）— 必跑
   → mcp__gitnexus__detect_changes(scope=compare, base_ref=main) 查本次变更所有符号
   → mcp__gitnexus__impact(target=改动的symbol, direction=upstream) 查上游依赖
   → 禁止"只看 git diff 不知道改了什么"（Article V 不可降级）
Step -2: 拆解验收基准（高风险清单）→ [acceptance-baseline-extract.md](workflows/acceptance-baseline-extract.md)（V11.6.0 落地:spec AC + ui-ux-logic 交互流 + TC 映射 → 基准清单;缺失 = BLOCK）
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
Step 1:  逐 AC 核销（API/UIUX/INV/EC/PERF 分类,TC 结果 + UI 证据填矩阵 — 不打分）
Step 1.5: 主动证伪（高风险清单核查）
Step 2:  功能效果验证 + 需求溯源 + Test Plan 前置门禁
Step 2.5: 产品侧功能有效性验收（V10.12 NEW — 3 问判定）
Step 2.6: 自动循环（Round 1 退回 / Round 2 上报用户 / Round 3+ rescue hatch）
Step 3:  门禁判定 — 跑 ac-gate.py(G1-G5),exit 0 = PASS / exit 1 = BLOCK(无分数,V11.6.0)
Step 4:  DOC SYNC
Step 5:  知识提取（spec-knowledge-extract.py）
```

## 附加检查(条件触发,非判定本体)

原 4 维明细(dim1-dim4)降级为**条件触发的附加检查**,不参与 PASS/FAIL 判定(判定唯一权威 = ac-gate.py):

| 检查 | 触发条件 | 文件 |
|------|---------|------|
| 代码卫生(测试/lint) | 每次必跑,但只作为证据归档(CI 已管) | [dim1-code.md](workflows/four-dim-detail/dim1-code.md) |
| 契约对齐 | 本次变更涉及 contracts/ 时 | [dim2-api.md](workflows/four-dim-detail/dim2-api.md) |
| UI 状态检查 | 仅 ui-ux-logic 错误边界表声明的状态 | [dim3-uiux.md](workflows/four-dim-detail/dim3-uiux.md) |
| GitNexus 边际 4 项 | 公共模块(≥10 下游)变更时 | [dim4-edge.md](workflows/four-dim-detail/dim4-edge.md) |

## 关键产物

| 产物 | 路径 | 状态卡字段 |
|------|------|----------|
| 4 维评分报告 | `docs/specs/changes/{id}/review-report.md` | `stage_review.review_report_path` 必须指向此文件 |
| 证据链 | file:line + 命令 + 截图 | `stage_review.evidence_paths` 数组 |
| 失败标签(如 REJECT) | `review-report.md` §失败标签 | `stage_review.reject_label` 必填 |

> **MUST**: Stage 4 Review 4 维评分是 Stage 4 **真相源**(Article XII),状态卡 `stage_review.*` 字段必须由主上下文亲自同步自 review-report.md(§5.8 子代理禁直接 Edit)。

## 4 维评分公式(已废弃)

> **V11.6.0 起此里程碑/打分/权重体系已废除**,门禁替代见 [acceptance-baseline-extract.md](workflows/acceptance-baseline-extract.md) + [ac-gate.py](../../scripts/ac-gate.py)
> 旧字段(YAML 模板、评分表)保留在 deprecated 子目录供参考,不得再用于判定

## 反例（5 条索引 — 含 V11.6.0 门禁化）

| # | 反例 | V10 来源 |
|:---:|------|---------|
| 1 | "非阻塞 FAIL"放水 | reviewer 铁律 1 |
| 2 | reviewer 帮忙修代码 | reviewer 铁律 6 |
| 3 | 编造测试覆盖 | V10.12 关键门禁套件 |
| 4 | 自动循环 Round 3+ 继续绕 | V10.12 Step 2.6 |
| 5 | 脚本拦了我放行(V11.6.0) | 铁律 11 — ac-gate.py exit ≠ 0 人工必须 BLOCK |

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
