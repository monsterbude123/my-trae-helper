# 2026-08-17 audit cycle — case 2 (desktop-pet) + case 3 (ai-chat-openai-v11) 完整闭环

> **状态**:✅ done(本会话合并:case 2 子代理 self-attest + 主代理硬验收 + case 3 V11 harness 实跑)
> **作用**:把 `case-2-desktop-pet-v11-audit.md` + `audit-fix-2026-08-17.md`(case 2 闭环表) + `audit-fix-2026-08-17-followup.md`(case 3 V11.8.7 自爆盘) 合并为**单一历史证据**,避免散落 .md 误导下游 reader
> **出处文档位置**:`archive/done/2026-08-17-audit-cycle/case-2-desktop-pet-v11-audit.md` + `archive/done/2026-08-17-audit-cycle/audit-fix-2026-08-17.md` + `archive/done/2026-08-17-audit-cycle/audit-fix-2026-08-17-followup.md`

---

## §1 完整闭环总览

| 阶段 | 维度 | case 2 (desktop-pet) | case 3 (ai-chat-openai-v11) | 累计 |
|------|------|----------------------|------------------------------|------|
| **子代理审计** | self-attest 报问题 | 7 个反例 | (主代理直跑) | 7 + 14 |
| **V11.8.7 patch** | 7 项修补 | ✅ 5/7 done(F 留 case-only, G done) | **真验证** + 暴露未修 5 项 | 真验证 |
| **case 3 V11 harness** | 跑 13 项 V11 工具 | (未跑) | **9/13 FAIL**(spec-purge 实跑 6 files 展平 PASS) | 9 项真违反 |
| **V11.8.7 followup** | 自爆盘 | — | 13 个未修/未暴露问题 | 13 |
| **commit-minimum-check** secret check | (无) | (无) | **V11.8.7 NEW — 第 5 项 check** | NEW |

## §2 case 3 V11 harness 9/13 gate FAIL 真实验尸

详细证据在 [audit-cycle-2026-08-17-raw-output.md](audit-cycle-2026-08-17-raw-output.md)(后续补)。
此处浓缩 4 大类:

1. **P0 secret 误写** — `secrets-detector.py` + `commit-minimum-check.py secret check` 拦截,触发 Article XVII §17.5
2. **P0 paths 不符** — V11 `gates.yaml` 期望 V11 扁平(`docs/specs/changes/{id}/spec.md`),我用 V12 物理布局 → 9/13 stage FAIL
3. **P1 hooks/gitnexus 缺** — `.trae/hooks/` + `.husky/` + `.gitnexus/` 全无(V11 §0 §0.5 Layer 2-3 没建立)
4. **P2 prototype 格式** — V11 期望 `design.html`,我给的是 markdown

## §3 V11.8.7 followup 13 问题跟进状态

| # | 问题 | V11.8.7 fix 状态 | 责任方 |
|---|------|------------------|--------|
| 1 | C fix 写 schema.json 但 validator.py 没读 | ❌ 半成品 | **fix** ✓(本期未触,记入 V12 升主版本 §12) |
| 2 | D fix §15 文档写禁硬编码但脚本没动 | ❌ 半成品 | 同上 |
| 3 | E fix 字段写了没消费者 | ❌ 半成品 | 同上 |
| 4 | A fix 枚举但缺 migrate-from-dual | ❌ 半成品 | 同上 |
| 5 | G fix gitignore 模板但 init 不写 | ❌ 半成品 | 同上 |
| 6 | project-rule-skill 命名漂移 | **未暴露** | V12 §12 跟踪 |
| 7 | state-card §9/§5.8/§2.1 health 字段定义混 | **未暴露** | V12 §12 跟踪 |
| 8 | V12 多卡 与 §5.8 主上下文独占冲突 | **未暴露** | V12 §12 跟踪 |
| 9 | case 2 子代理诊断是否每个问题归因到位 | **未审查** | 主代理反思项 |
| 10 | verify-report `model count: 3` 来自外部 service | **未声明** | case 3 followup |
| 11 | `.state-card.md` 没 close 而 change 已 archive | **未追踪** | stage-3 |
| 12 | `tests/unit/test_state_card_validator_extended.py` 232 passed 未跑 | **未验证** | V11.8.5.P1 followup |
| 13 | V11.8.7 patch commit 在 fullstack4TraeV11 主仓库未 commit | **未 commit** | (本期本会话) |

**已修** ✅:

- **commit-minimum-check.py 第 5 项 secret scan**(本期)— 防止 #1-3 类事件再生
- **state-card-protocol.md §10.6 AC 核销矩阵硬约束** — 防止 #7 类事件再生
- **V12-ADR-DRAFT §12 V11 harness 兼容范围声明** — 防止 #4-#6 类事件在 V12 升主版本时再发生
- **prototype-backfill-check.py 兼容 V12 layout** — 防止 #8 类事件再生

## §4 反例索引(不可重复踩)

- **V11 §3.7 #5 反虚假交付**:case 3 自评 13/13 PASS + 10/12 + 9/9 — 全部是"我自己写的测试通过"的循环证明。V11 harness 真跑才能验证
- **Article XVII §17.4 测试用 secret 也不能入 commit + tool log**:case 3 `.env` 已 .gitignore 但 commit message grep key 前缀 — **违反**
- **V12 多卡布局 与 V11 标 gate 期望的不对齐** — 必须升 V12 主版本后,V11 harness 才能识别。本期只在 ADR §12 显式声明

## §5 本会话对 V11 技能的实际修补(真实落地)

| 修补位置 | 修补依据 | 修补方式 |
|---------|----------|---------|
| `scripts/commit-minimum-check.py` | case 3 P0 secret 误写 | 加第 5 项 `check_secret_in_tracked_files`,git ls-files + `sk-[a-zA-Z0-9]{20,}` regex |
| `references/state-card-protocol.md §10.6` | case 3 ac-gate.py G1 BLOCK | 新增"AC 核销矩阵硬约束"段,6 列格式 + 反例 + 自验收 |
| `references/todos/v12-physical-isolation/V12-ADR-DRAFT.md §12` | case 3 9/13 gates FAIL | 新增"V11 harness 兼容范围声明",5 点补救 + 反例 |
| `scripts/prototype-backfill-check.py` | case 3 prototype-backfill FAIL | 加 V12 layout 路径支持 + `detect_ui_involved_v12` |
| `references/todos/audit-cycle-2026-08-17.md`(本文件) | 当前活跃 | 单源闭环报告 |
| `references/todos/README.md` | 更新当前活跃索引 | — |
| `references/todos/P0-v12-physical-rollout.md` | 已 done | 保留作引用证据 |