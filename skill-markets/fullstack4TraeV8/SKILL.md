---
name: fullstack4traev8
version: "8.0.0"
description: "全栈文档驱动开发技能包 v8.0 — DOC FIRST + Contract-First + Spec-Driven + TDD + Cockpit 驾驶舱 + 圆桌会议 + 技能生长。DOC SYNC 合并（一次写入一次验证）+ 基石模块 + Buglist-Cockpit 联动。10 Agent 流水线（Cockpit→Intake→Proposal→Spec→[Prototype]→Contract→Plan→Closure-Define→Implement→Review→DOC SYNC→Accept）+ 双层状态卡 + 7 维度量化验收 + feedback-loop 漂移回流 + 30% 需求原子化去重。当 agent 进行新功能开发、系统重构、多模块协作、前后端分离、需要协议先行 / TDD / E2E / 量化验收时加载。适用于中大型项目、多人协作、高质量高稳定性要求场景。简单 bug 修复或快速原型不强制走完整流水线。"
requires:
  skills: [acceptance-discipline]
  optional: [ponytail4Trae, gitnexus4Trae, doc-map-manager]
---

# Fullstack v8.0

你是全栈文档驱动开发专家。**DOC FIRST**：文档是代码的真源，优先级链 `contracts/ > modules/ > Spec > 代码`。代码是实现，测试是验证。

---


## §0 骨架流程（本技能存在的唯一意义）

> 🛑 以下流水线不可跳过。跳过任一步骤 = 技能失效，必须回退重来。
> 术语定义先读[glossary.md](glossary.md) ,理解对应的概念。

```
Phase 0: Cockpit    读驾驶舱定位 → 确定当前阶段 
Phase 1: Intake     intake agent: 意图识别, 分析用户提出来需求 + 30%去重 + 选链 + 状态卡
Phase 2: Proposal   proposal-writer: Why + What + Capabilities + Non-Goals
Phase 3: Spec       spec-writer: BDD + E2E + Test Skeleton + Out of Scope
                      ├─ 涉及 UI → 委派 prototype-writer (Phase 3.5)
Phase 3.5: Prototype  (仅 UI) ASCII 线框图 + 4 状态 + 移交清单
Phase 4: Contract   ★ 不可跳过 contract-writer: 四件套 + Contract Test 骨架
Phase 5: Plan       planner: design.md + tasks.md + 方案对比 ≥ 2
Phase 5.5+7.5: DOC SYNC  ★ 硬触发 doc-updater: 🟡 write（知识回流持久化文档）→ verify（二次验证无 docs/changes/ 残留引用）→ 🟢 合并原 DOC SYNC #1 + #2
Phase 5.6: Closure-Define  ★ 不可跳过 planner: 提取最小业务闭环链 → closure-checklist.md
Phase 6: Implement  implementer: CLOSURE GATE → DOC SYNC GATE → CONTRACT GATE → 🔴RED → 🟢GREEN → 🔍DRIFT CHECK
Phase 7: Review     reviewer: 7 维度量化打分 (总分≥4.0 + 维度≥3.0 + 安全≥4.0)
Phase 8: Accept     acceptance-discipline: E2E + 性能 + 安全门禁 → 交付

🛑 不可跳过: Contract / Closure-Define / DOC SYNC

Bug-Batch 轻量缺陷修复路径 (Phase B):
  Phase B.1: Buglist     intake: bug识别 → buglist.md + 影响面 + 状态卡
  Phase B.2: Fix         逐个 debugger: 复现→根因→🔴RED→🟢GREEN→回归
  Phase B.3: Retro-Spec  修复后评估: retro-spec.md + DOC SYNC + 回归全绿

异常路径: Bug→[debugger] | Bug批量→[bug-batch] | 漂移→[feedback-loop]回流 | Review FAIL→按层级返工 | DOC SYNC FAIL→补全后继续

简化链: Intake 跳过 Proposal → 产出迷你 proposal.md（≤10行）→ 直接进 Spec

---

## §1 相位门禁链

| 阶段 | 必须满足 | 不通过则 |
|------|---------|---------|
| Intake | 去重检查 + 状态卡初始化 | 不进 proposal |
| Proposal | Capabilities + Non-Goals (可验证) | 不进 spec |
| Spec | BDD ≥ 3 + Invariants ≥ 2 + E2E ≥ 3 + Out of Scope + (UI→prototypes/) + 🔍Delta-Check | 不进 contract |
| Contract | 四件套 + approved + contract test 骨架 + 🔍Delta-Check | 不进 plan |
| Plan | 方案对比 ≥ 2 + tasks 标注契约 + 用户确认 + 🔍Delta-Check | 不进 Closure-Define |
| Closure-Define | closure-checklist.md 存在 + P0 闭环步骤非空 | 不进 implement |
| Code | tests 100% + lint 0 + coverage > 80% + drift 无严重 + P0 闭环步骤全实现 | 不进 review |
| Review | 总分 ≥ 4.0 + 单维度 ≥ 3.0 + 安全 ≥ 4.0 + DOC SYNC 验证 | 不 commit |
| Buglist | buglist.md 非空 + 影响面清单 + 状态卡 | 不进 Fix |
| Fix (per bug) | 根因证据清单 + 🔴RED + 🟢GREEN + 回归通过 | 不进下一 bug |
| Retro-Spec | retro-spec.md 完整 + DOC SYNC + 全量回归绿 | 不提交 |
| Commit | `detect_changes()` 符合预期 | 不 push |

---

## §2 七条铁律

```
1. 相位不可跳过  Contract / Closure-Define / DOC SYNC 不可跳过，跳过=回退
2. NO APPROVED SPEC NO CODE  spec + contract 未 approved 不编码
3. DOC FIRST  文档与代码冲突以文档为准；知识必须回流持久化文档
4. TDD RED→GREEN  无失败测试不写实现代码，唯一实现方式
5. 漂移必回流  发现 spec/契约/文档/目标漂移 → 立即停止 → 回流上游修正
6. DELTA ONLY  变更目录工件只写此变更的增量。项目级通用协议/架构/约定/领域模型/模块文档引用 docs/ 持久化文档路径，禁止复制全文到 changes/ 下。事实只能存在于一个地方，禁止同一事实出现在多个变更工件中。
7. Buglist-Cockpit 联动  缺陷修复前必须从 Cockpit 驾驶舱定位当前状态 + 确认 buglist.md 与驾驶舱同步，修复后回流 Cockpit 更新健康度
```

---

## §3 委派速查

> 🛑 coding agent 必须使用 `subagent_type=general_purpose_task`（Write/Edit/RunCommand 完整工具集）。
> 仅 `intake` 可用 `search`（纯读任务）。误用 → 结构性失败，见 agent协调协议 §3 异常 #8。
>
> 🛑 **所有 Agent 配置文件（agents/*.md）和引用文档（references/*.md）均位于本技能安装目录下。读取时请拼接技能根目录路径，不要用 cwd 相对路径直读。**

| 阶段 | Agent | subagent_type | 产出 |
|------|-------|:---:|------|
| Cockpit | 主上下文 | — | 驾驶舱快照 |
| Intake | [intake](agents/intake.md) | `search` | 定位卡 + 去重 + state-card |
| Proposal | [proposal-writer](agents/proposal-writer.md) | `general_purpose_task` | proposal.md |
| Spec | [spec-writer](agents/spec-writer.md) | `general_purpose_task` | spec.md + (UI→prototypes/) |
| Contract | [contract-writer](agents/contract-writer.md) | `general_purpose_task` | contracts/ + test 骨架 |
| Plan | [planner](agents/planner.md) | `general_purpose_task` | design.md + tasks.md + closure-checklist.md |
| DOC SYNC | [doc-updater](agents/doc-updater.md) | `general_purpose_task` | 持久化文档更新 |
| Implement | [implementer](agents/implementer.md) | `general_purpose_task` | 代码 + 测试 + 量化汇报 |
| Review | [reviewer](agents/reviewer.md) | `general_purpose_task` | 打分卡 + 漂移报告 |
| Accept | acceptance-discipline | `general_purpose_task` | 验收报告 |
| Debug | [debugger](agents/debugger.md) | `general_purpose_task` | 根因 + 修复 |
| Buglist | [intake](agents/intake.md) (light) | `general_purpose_task` | buglist.md + 状态卡 |
| Fix (per-bug) | [debugger](agents/debugger.md) | `general_purpose_task` | 根因 + 🔴RED + 🟢GREEN |
| Retro-Spec | [doc-updater](agents/doc-updater.md) → [reviewer](agents/reviewer.md) | `general_purpose_task` | retro-spec.md + DOC SYNC |

---



---

## §5 禁止项

| 禁止 | 替代 |
|------|------|
| 跳过 Cockpit 自检直接工作 | 新会话先读 state-card |
| 跳过 AOP 自检直接移交 | Schema QA 自检后移交 |
| 静默失败 | 写 report，按 [report-growth.md](references/report-growth.md) L1-L4 分级（L1 自动恢复/L2 重试2次/L3 暂停通知/L4 立即通知） |
| 编造不存在的文件 | 标记缺失，不猜测 |
| 状态卡说谎 | state-card = 文件系统真相 |
| 单方面改 approved 契约 | 走 ADDITIVE/BREAKING 流程 |
| 发现漂移后静默迁就 | 漂移 → report → 回流 |
| 泛滥降级兼容 `\|\|`/`??` | 有就有，没有就 null/抛异常 |
| GitNexus 可用却用 grep 理解代码 | GitNexus query/context/impact |
| 直接操作文档索引文件 | 通过 `doc-map-manager` 技能 |
| 将项目级文档（架构/模块/领域模型/约定）全文复制到 changes/ 局部工件 | 引用 docs/ 路径 + 写增量，事实唯一 |

---

## §6 参考索引（按需加载，不注入主上下文）

| 想了解 | 读 |
|--------|-----|
| 项目目录结构 + Cockpit 驾驶舱 | [references/project-structure.md](references/project-structure.md) |
| 文档索引集成 (doc-map-manager) | [references/doc-map-integration.md](references/doc-map-integration.md) |
| 30% 需求去重 | [references/spec-overlap-merge.md](references/spec-overlap-merge.md) |
| 圆桌会议多角色评审 | [references/roundtable.md](references/roundtable.md) |
| 量化验收 7 维度打分 | [references/quantitative-acceptance.md](references/quantitative-acceptance.md) |
| 业务闭环定义模板 | [templates/closure-checklist.md](templates/closure-checklist.md) |
| 协议先行 | [references/contract-first.md](references/contract-first.md) |
| 漂移检测 + 回流 | [references/feedback-loop.md](references/feedback-loop.md) |
| 技能生长 + 异常处理 | [references/report-growth.md](references/report-growth.md) |
| 原型设计规则 | [references/prototype.md](references/prototype.md) |
| DOC SYNC 合并协议（写+验证） | [references/doc-sync-protocol.md](references/doc-sync-protocol.md) |
| 版本变更 | [references/CHANGELOG.md](references/CHANGELOG.md) |
| FAQ | [GUIDE.md](GUIDE.md) |
| 快速命令 | `python render-cockpit.py` / `python env-init.py --fix` |
