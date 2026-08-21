---
name: fullstack4traev11
version: 12.0.0
description: "全栈 V12 流水线 — 启动新功能开发、写代码、改契约、跑 E2E、提交门禁、修 bug 时加载（触发词：全栈/新功能/V11/V12/spec/contract/implement/verify/accept/bug-fix/stage gate）。13 stage 物理隔离 + 强门禁 + qa-loop 反向守门 + bug-in-scope 硬约束。use when: any fullstack development task。"
changelog:
  - version: 12.0.0
    date: 2026-08-16
    note: V12 物理隔离主版本升级(ADR ACCEPTED)
  - version: 11.8.7
    date: 2026-08-18
    note: qa-loop 真闭环 + bug-in-scope 硬约束 + Stage 5 light_mode + build cache + 顶层截图脚本 + common-anti-patterns §22(详见 CHANGELOG.md V11.8.7)
description: 全栈文档驱动开发技能包 v12 — V11.8.6 V12 物理隔离思想累积后**升主版本**(2026-08-16 V12 ADR 用户授权)。V12 默认布局 = fact/ + stage/{N}/ 物理隔离 + handoff-out/handoff-in 桥接 + 状态卡每 stage 独立。V11.8.7.1 起 **V11 扁平布局已彻底废弃**(`--layout` 仅 `v12-preview`,V11 既有项目必须 `--migrate-from-v11` 升级)。**V11.8.7 起加 qa-loop 反向守门 + bug-in-scope + light_mode + build cache + 顶层截图脚本**(主代理会话启动第一步跑 `--intent qa-loop-audit`)。触发词：全栈开发 / spec-kit / 文档驱动 / V12 / 高内聚 / 13 stage / 三层架构 / registry / 状态机 / 门禁程序化 / 物理隔离 / fact / stage / qa-loop / bug-in-scope / light_mode。
requires:
stage_config:
intent: 全栈文档驱动开发技能包 v12 — V11 物理隔离思想落地为标准布局 + V11.8.7 qa-loop 反向守门
category: gate
audience: [developer]
---
# Fullstack v12.0 — V11 物理隔离思想升主版本(2026-08-16 ADR ACCEPTED)

你是全栈文档驱动开发编排专家。**Spec 是真相源，代码为规格服务**。13 个 stage 各由独立专家 skill 负责，编排器只做路由 + 门禁 + 状态卡同步。

> V11 升级核心：从 V10 的 "agents/ + references/" 分散架构升级为 "高内聚专家 skill" 架构 — 每个 stage 自包含骨架/铁律/反例/模板/脚本/依赖声明，像插拔组件一样可独立管理。

---

## 哲学（V10 传承 + V11 升级）

```
复用而非自研      → 优先复用已有模块（不重写已有能力）
质量而非流程      → 测试覆盖率 ≥ 90% + 每个主张附 evidence
验证而非信任      → 主上下文独立抽检 3 层（evidence / pass_count / 产物存在性）
干净而非兼容      → 不为兼容旧行为保留过渡层（L9+ 才考虑）
主动而非被动      → 默认开启 GitNexus / state-card-validator / hooks-fidelity 校验
质疑而非自证      → Article XVI 质疑式校验（不可证伪理由 = 🛑 REJECT）
骨感而非堆积      → skill 文件 ≤ 10 铁律 + ≤ 150 行（Article XI）
分层而非混置      → fact / process / log 三层隔离（sub-agent-rules §1）
高内聚低耦合      → 每个 stage 自包含目录（skills/{NN}-{name}/）
插拔式专家        → stage skill 可独立升级替换
```

> V11 新增最后 2 条：每个 stage 自包含（高内聚）+ stage skill 可独立替换/升级（插拔式）。

**冲突判定顺序**: Constitution > Spec > Contract > Code > 个人判断。
**永不可降级**: 全部 17 Articles（详见 [references/constitution.md](references/constitution.md)，其中 Article XVII Secret Redaction 见 [common-iron-rules.md](references/common-iron-rules.md)）。

---

## §0.5 Skill 加载协议(V12 升级 — 防首次产物偏离)

> **📋 详细协议已迁移到 references**(2026-08-19 瘦身):
>
> | 段 | 内容 | 引用 |
> |----|------|------|
> | §0.5 加载 9 步顺序 | 加载 SKILL.md / 必读 12 references / 调 Skill(name="project-rules") / Glob / 路径核对 / 项目级覆盖 / 反例清单 / Bug 触发词识别 | [references/v11-load-protocol.md](references/v11-load-protocol.md) |
> | §0.5.1 同类约定 10 项 | 截屏/视觉验证/浏览器自动化/UI测试/E2E/录屏/a11y/性能/契约对齐/时间时区 | 同上 |
> | §0.5.2 加载后 3 项验证 | hooks-fidelity.py + LS project-rules SKILL.md + LS state-card | 同上 |
>
> **核心反例**: 只加载 SKILL.md 主文件就立即进入 stage → 不知项目惯例 → 用户 4+ 轮返工

**反例(V12 沿用 V11.1)**: 未列"我不能踩的雷"清单就直接做工作 → 反复踩同一雷 → 见 [unread-rule-pass.md](references/unread-rule-pass.md) §21

---

## §0 三层架构(Gate / Guard / Execution)

> **V12 沿用 V11.7.0 贾维斯体系**: 为防 agent 改标准通过自己,新增 pre-stage 角色贾维斯(jarvis)+ hash 锁机制(详见 [skills/00-boot/SKILL.md](skills/00-boot/SKILL.md))。会话启动必先委派贾维斯铺三层 gate + 签锁;任何 gate 文件改动必经 [JARVIS-DELEGATION] 委派 + gate-integrity-guard.py 机械校验。
>
> **V12 沿用 V11.4**: 从 V11.0 的"门禁链 + Hook 生命周期"两层,升级为三层控制体系(Gate / Guard / Execution),实现"硬化门禁 + 自动化守卫 + 标准化执行"的完整控制闭环。

### §0.0 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                     Gate 层（门禁）                          │
│   Git 操作级阻断（L1-L4）+ Stage 切换级阻断（pre/post-stage）│
│              ↓ PASS（才进入下一层）                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Guard 层（守卫）                          │
│         TRAE IDE event hook + Shell hook 自动化检查          │
│              ↓ PASS（才进入下一层）                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Execution 层（执行）                        │
│              13 stage 流水线标准化执行                       │
└─────────────────────────────────────────────────────────────┘
```

**联动规则（V12 沿用 V11.4 铁律）**：
- Gate PASS → Guard 层启动
- Guard PASS → Execution 层启动
- 任一层 FAIL → 阻断 + 5 字段阻塞报告（见 Article XV）

### §0.0.5 贾维斯分层模型（V12 沿用 V11.7.0 — 防 agent 改标准）

> **📋 详细协议已迁移到 references**(2026-08-19 瘦身):
>
> | 段 | 内容 | 引用 |
> |----|------|------|
> | §0 架构总览 | Gate / Guard / Execution 三层架构图 + 联动规则 | [references/v11-three-layer-control.md](references/v11-three-layer-control.md) |
> | §0.0.5 贾维斯三层防线 | 协议层 / 白名单层 / 机械层 + L-module/L-app/L-system | 同上 |
> | §0.1.1 Git 子层 L1-L4 Gate | 自验收铁律 + 跨 stage gate 路径 | 同上 |
> | §0.1.2 Stage 子层 | 13 stage 入口/出口/门禁/确认级别表 | 同上 |
> | §0.2.1 TRAE IDE event Hook | 5 种 event + SessionStart/PreToolUse/PostToolUse/Stop | 同上 |
> | §0.2.2-§0.2.3 Shell Hook | pre-stage / post-stage / pre-accept + 各 stage 完成 Hook | 同上 |
> | §0.2.4 hooks-fidelity | 4 项检查 + PASS/FAIL/N/A 三态 | 同上 |
> | §0.3 Execution 13 stage 流水线 | 主链路 + 支线 + 不可跳过 | 同上 |
>
> **关键引用**:`scripts/hooks-fidelity.py`(验证脚本)+ `registry/gates.yaml`(flow 层四表)

---

## §1 委派速查

> 完整 stage_config 见 frontmatter。项目级覆盖规则见 [references/dependency-config.md](references/dependency-config.md)。
> **Agent 使用 stage skill 必读**: [references/stage-skill-agent-protocol.md](references/stage-skill-agent-protocol.md)。

**13 stage 委派表(精简)**:

| Stage 范围 | 加载 stage skill | 外部 skill 依赖 | 产出 |
|:---:|------------------|------------------|------|
| -1 ~ 1.5 | `skills/01-intake` ~ `skills/05-prototype` | [gitnexus4Trae] / [ui-ux-pro-max](按需) | 状态卡 → plan.md → test-plan.md → spec.md → prototypes/ |
| 2 ~ 3 | `skills/06-contract` ~ `skills/07-implement` | [frontend-backend-contract-alignment] / [ponytail4Trae, gitnexus4Trae] | contracts/ 四件套 → 代码 + 测试 + 模块文档 |
| 3.5 ~ 4.5 | `skills/08-real-verify` ~ `skills/10-rot-scan` | [visual-evidence-discipline, screenshot, playwright-best-practices] / [acceptance-discipline] / [goal-mode] | verify-report → review-report → rot-scan |
| 5 ~ 7 | `skills/11-accept` ~ `skills/13-project-health` | [doc-map-manager] / [gitnexus4Trae] | archive/done → bug 单 CLOSED → project-health |

> **💡 Stage 3.5 / 4.5 异步性声明(V11.8.4 NEW — 蒸馏自 2026-08-15 merged-commits)**:
> - **commit 准入最小集 ≠ 全量验收**(详见 [references/v11-fidelity-protocol.md](references/v11-fidelity-protocol.md) §3.7.3 + [common-anti-patterns.md §7.3](references/common-anti-patterns.md))
> - Stage 3.5 / 4.5 默认异步、不阻塞 Stage 5 commit;全量视觉证据 / 完整 rot-scan / 完整 vitest → commit 后异步执行

### §1.1 角色(Role)委派列

> 角色体系与 stage **正交**:角色答"谁/职责/权限",stage 答"何时/流程/产物"。8 角色定义见 [skills/00-boot/agents/README.md](skills/00-boot/agents/README.md)(注册表 + 履职矩阵)。

| 角色 id | 履职 stage | 委派时注入头部 |
|---------|-----------|--------------|
| **jarvis** | 全域 gate(时机①~⑥) | `[JARVIS-DELEGATION]`(含 type: gate-design)|
| **product-manager** | -1 / 1 / 4 / 5 | `[PIPELINE]`(产出 uiux 双文档供下游)|
| **tech-planner** | 0 / 1 / 2 | `[PIPELINE]`(可发起 `[JARVIS-DELEGATION]` gate-design)|
| **backend-implementer** | 3 | `[PIPELINE]` + GitNexus 必跑 |
| **frontend-implementer** | 3 | `[PIPELINE]` + GitNexus 必跑 |
| **prototype-designer** | 1.5 / 3 | `[PROTOTYPE-DELEGATION]` |
| **qa-submitter** | 3.5 / 6 | `[QA-SUBMIT-DELEGATION]` |
| **test-expert** | 0.5 / 3.5 / 4 / 6 | `[TEST-EXPERT-DELEGATION]` |

**委派头部协议引用**:
- 13 stage × 角色映射见 [stage-skill-agent-protocol.md §4](references/stage-skill-agent-protocol.md#4)
- 角色专属头部见 [role-protocol.md §4](references/role-protocol.md)
- 子代理通用模板见 [sub-agent-rules.md §7](references/sub-agent-rules.md)
- qa-loop 闭环流程见 [docs/specs/qa-loop.md](docs/specs/qa-loop.md)

### 委派注入头部(coding-task 强制)

```
[MUST-READ] AGENTS.md + .trae/rules/
[PIPELINE] stage: {N}
[DOC_WHITELIST] {whitelist}
[FORBIDDEN] docs/archive/**, .trae/tmp/**, diagnostic/bugs/**
[GITNEXUS] impact()
[TASK] {≤200 chars}
[OUTPUT] 4 字段: status / evidence / pass_count / next_hook
```

### §1.6 主上下文自律条款(V12 沿用 V11.1)

当主上下文决定**不委派** coding-task agent 时,**必须**在 Completion Report 中显式声明:

| 字段 | 内容 |
|------|------|
| `delegation_skipped_reason` | "小任务流线化: ≤6 Task + LOW + 无新 API" 或其他合理理由 |
| `skipped_agents` | 列出跳过的 agent 名称(如 `[planner, spec-enhancer, rot-detector]`)|

任一条款触发时必须声明:
- Article IV 委派纪律
- §0 流水线必走阶段
- Phase 4.5 rot-detector 必跑

跳过且不声明 = 🛑 流程违规。

> **💡 §1.6 视觉验证豁免(V11.8.4 NEW)**: 视觉验证类任务(Stage 3.5 visual-evidence / screenshot)默认异步,**不入流线化判定**;即使 60+ 路由,主代理仍可亲自跑,但必须按 wave 拆分异步推进。详见 [common-anti-patterns.md §7.3](references/common-anti-patterns.md)。

---

## §3 状态卡与阶段交互

> **指针化**: 详细协议已迁移到 references。

- **状态卡**: [state-card-protocol.md](references/state-card-protocol.md)(3 类卡 / 字段定义 / 更新时机 / 交叉验证 / 模板)
- **阶段交互**: [stage-interaction-protocol.md](references/stage-interaction-protocol.md)(标准交接物 4 件套 / 启动前检查 / 异常状态 / 回退路径表 / 产出物层级)

**核心原则**(不外置):
- 状态卡是任务真相源之一(Article XII 文档诚实)
- 新会话激活先读 `docs/specs/.state-card.md` → 30 分钟未产 = 疑似假性完成
- Checkpoint = 每个 stage 门禁 PASS 一次
- 同一 stage 连续回退 3 次 → 升级用户决策

---

## §5 确定性脚本使用时机

> 完整脚本清单 + 用途 + 使用 stage 详见 [scripts/README.md](scripts/README.md)。
> 脚本失败 = 🛑 REJECT,主上下文亲自调用(不委派给子代理,Article IV)。

**核心规则**:
- 主上下文亲自调用(不委派给子代理)
- 脚本输出必须真实保存(不接受口头宣称 PASS)
- 脚本失败 = 🛑 REJECT → 走 Article XV 阻塞报告
- 脚本 N/A → 必须在状态卡标注理由

---

## §6 上下文卫生

**核心原则**:
- **逐阶段加载**: 每个 stage 开始时加载对应 stage skill,完成后卸载
- **文件即状态**: 关键状态不在对话记忆中,会话中断后通过读取文件恢复
- **文档分层**: fact / process / log 三层标注,子代理禁读 process 层

**详细指针**: [stage-interaction-protocol.md §五](references/stage-interaction-protocol.md) + [document-layer.md](references/document-layer.md)

---

## §7 Report Growth(L1-L4 异常分级)

> 详细协议:[references/report-growth.md](references/report-growth.md)

| 等级 | 范围 | 处理 | 重试上限 |
|:---:|------|------|:---:|
| L1 | 文件系统 | Retry 1 次 → 记录 → 继续 | 1 次 |
| L2 | Agent 执行 | 换参数/策略 → 最多 3 次 → 阻塞报告 | 3 次 |
| L3 | 状态不一致 | 汇报用户 → 等待决策 | 不可自动 |
| L4 | 外部依赖 | 降级运行 + 标注风险 → 汇报 | 不可自动 |

**原则**: NEVER SILENT FAIL → RETRY TWICE, STOP → REPORT → STATE CARD SYNC(异常写入 `.trae/logs/report-growth.jsonl`)

---

## §8 Bug 录入触发 + §9 汇报纪律

**触发词**:"报错"/"错误"/"异常" / "不工作"/"失败"/"崩溃" / "应该出现 X 但出现 Y"

**流程**:触发词识别 → 主上下文询问 → 用户拒绝按"一般咨询"处理 / 用户同意走 Stage -1 Intake bug 录入 6 字段 → 路由到 Stage 6 Bug Fix

**MUST**: 询问是否录入 bug 单(不默认创建)。**NEVER**: 用户拒绝时强制创建。

**汇报原则**:
- 状态有变化 → 1 句结论 + 1 句证据
- 状态无变化 → "状态不变,无阻塞"
- 阻塞发生 → 5 字段阻塞报告(3 次失败升级用户)
- 需用户决策 → 列选项 + 推荐方案

**防漂移机制(3 层)**:Layer 1 规则可达性(委派模板强制头部)/ Layer 2 执行保真度(产物验证 + evidence 抽检)/ Layer 3 漂移检测(acceptance-audit + proactive-scan)。

> **📋 详细**: [stage-interaction-protocol.md §异常状态](references/stage-interaction-protocol.md) + [ask-question-anti-patterns.md](references/ask-question-anti-patterns.md)

---

## §10 禁止项(核心 9 条)

> 18 条反例详细:[common-anti-patterns.md](references/common-anti-patterns.md)
> 16 条铁律详细:[common-iron-rules.md](references/common-iron-rules.md)

核心禁止项(任一违反 = 🛑 REJECT):

- 跳过 Stage 0 Plan 直接写 Spec
- 跳过 Stage 2 Contract 直接 Implement
- 修改 archive/ 下文件
- GitNexus 可用却用 grep
- 用后端/编译类验证充当 UI 任务"完成"
- 盲信子代理的"已完成"声明
- 隐瞒阻塞 / 引用不可证伪理由作为失败归因
- 状态卡说谎 / 文档与代码漂移静默迁就
- 跳过 Stage 4.5 Rot Scan

### §3.7 反虚假交付 + §8 fidelity 等级(V12 沿用 V11.3)

> **核心**: 任何"PASS"必附真实证据(command + output + file:line),禁止"看到进程即通过"。
>
> **📋 详细协议已迁移到 references**(2026-08-19 vibe-coding-standards v2.5 瘦身):
>
> | 段 | 内容 | 引用 |
> |----|------|------|
> | §3.7 | 反虚假交付 9 项禁止 + §3.7.2 Article V 强化 + canvas-asset-folders 案例 | [references/v11-fidelity-protocol.md](references/v11-fidelity-protocol.md) |
> | §8 | prototype fidelity 等级 L1/L2/L3 + 偏离理由 + 工具-人类分层判定 | 同上 |
>
> **关键引用**:[agent-error-diagnosis.md](references/agent-error-diagnosis.md) §3 5 模式诊断 + [common-anti-patterns.md §7.3](references/common-anti-patterns.md)(commit 准入最小集 ≠ 全量验收)

---

## §11 AskUserQuestion 反模式

> 详见 [references/ask-question-anti-patterns.md](references/ask-question-anti-patterns.md)。

**核心 2 类**:
- 反模式 1 — 用户没选选项 = 可能在质疑流程本身 → 承认错误 + 根因分析
- 反模式 2 — 用户累计 ≥ 3 次小修请求仍在修补细节 → 反向提示词生成(NEVER + 反例)

**多轮道歉信号**: 主上下文道歉 ≥ 2 次 + 无可观测改进 + 用户在 2 轮内表达 ≥ 3 次否定判断 → 立即停止道歉,列 ✅ 已做 + 📍 证据。

---

## §12 目录结构

详见 [project-structure.md](references/project-structure.md)(含 fullstack4TraeV11/ + 13 个 stage skill 自包含结构 + 各 stage 产物层级)。

---

## §13 参考索引

- **核心 references**:constitution / common-iron-rules / common-anti-patterns / **skeptical-validation-protocol**(7 stage 永久激活)/ stage-interaction-protocol / state-card-protocol / dependency-config / document-layer / report-growth / ask-question-anti-patterns / agent-error-diagnosis / sub-agent-rules / project-structure / gitnexus-tools / gitnexus-retry-protocol / stage-physical-isolation / role-protocol / loop-pass-pattern / secret-in-tool-arg / config-files-glossary / gate-configuration-protocol / skeptical-validation-protocol / stage-card-protocol / stage-skill-agent-protocol / unread-rule-pass / user-orchestration-pattern
- **2026-08-19 瘦身抽出**(`references/v11-*.md`):v11-fidelity-protocol(§3.7+§8)/ v11-three-layer-control(§0)/ v11-project-ecosystem(§14)/ v11-paths-config(§15)
- **glossary.md** — 术语表(V10 完整继承 + V11 新增 5 大类 100+ 术语)
- **templates/**: project-agents-example / project-rules-example / project-rules-skill-template / state-card / hooks/ / constitution-template / ci/ / checklist-template
- **bug-hunt 实战段**: [skills/12-bug-fix/references/bug-hunt-battle-report.md](skills/12-bug-fix/references/bug-hunt-battle-report.md)(V11.8.2 起迁入 stage 12 同包)

---

## §14 项目级生态管理规范(V12.0.0 已授权)

> 任何 stage skill 涉及项目级配置改动(.trae/rules/ / .trae/skills/project_rules_skills/ / .trae/hooks/ / AGENTS.md 等),必走本规范。
>
> **📋 详细协议已迁移到 references**(2026-08-19 vibe-coding-standards v2.5 瘦身):
>
> | 段 | 内容 | 引用 |
> |----|------|------|
> | §14.1 5 项铁律 | 单点入口 / 物理移走 / README 幂等 / 占位模板 / 整合协议 | [references/v11-project-ecosystem.md](references/v11-project-ecosystem.md) |
> | §14.1.1 V11.8.7 三件套 | 强制多选 / 强制漏选审查 / 强制用户通知 | 同上 |
> | §14.2-§14.3 触发词 + 反例 | 改 .trae/ 时必走 | 同上 |
> | §14.5 项目级 vs V12 优先级 | 项目级 rules > V12 通用层 | 同上 |
>
> **必读模板**:`templates/project-rules-skill-template/SKILL.md`(V11.8.7+) + `templates/project-rules-example/README.md`

---

## §15 paths 配置化(V12.0.0 沿用 V11.8.7 — case 2 desktop-pet-v11 audit-fix)

> **来源**:case 2 desktop-pet-v11 audit-fix — AGENTS.md §4.1 提到 `paths.archive` 但脚本路径硬编码分散 5 个文件,产生 3 个不同路径(详见 [trap-instructions.yaml AP-15](references/trap-instructions.yaml))。
>
> **📋 详细协议已迁移到 references**(2026-08-19 瘦身):
>
> | 段 | 内容 | 引用 |
> |----|------|------|
> | §15.1-§15.5 | 必须配置的 4 类路径 + 单一访问源 `_lib_paths.py` + 自验收 3 步 + 反例 | [references/v11-paths-config.md](references/v11-paths-config.md) |
>
> **关键引用**:[scripts/_lib_paths.py](scripts/_lib_paths.py)(路径单源库)+ [config-files-glossary.md](references/config-files-glossary.md)(.trae/fullstack4traev11.config.yaml 字段表)

