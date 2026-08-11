---
title: V10.x 版本演进时间轴 + 附录索引
description: V10.0 → V10.12.1 演进图 + 引用入口与文件索引
layer: fact
---

# V10.x 版本演进时间轴 + 附录索引

> V10 = "spec-kit 五阶段 + 16 Articles 不可降级 + 5 维度硬门禁 + 腐化可检测 + 启证可见产物"。
> 演进主线: **质量底线 → 腐化可检测 → 文档诚实 → 反虚假交付 → 质疑性校验 → 可见产物**。

## 一、版本演进时间轴

```mermaid
graph LR
    V100[V10.0<br/>基础 5 阶段]
    V101[V10.1<br/>流水线优化]
    V102[V10.2<br/>证据链强化]
    V103[V10.3<br/>视觉验证 3 层]
    V104[V10.4<br/>腐化可检测<br/>IV-XI/XIV]
    V105[V10.5<br/>文档诚实<br/>XII/XIII]
    V106[V10.6<br/>独立抽检<br/>证据链]
    V108[V10.8<br/>反虚假交付<br/>XV/XVI]
    V109[V10.9<br/>项目健康度<br/>防失真 4 大机制]
    V110[V10.10<br/>真实验证<br/>§0.10]
    V111[V10.11<br/>phase-gate 机械门禁<br/>Bug 录入]
    V112[V10.12<br/>同类 10 项<br/>启证可见产物<br/>质疑性校验]
    V1121[V10.12.1<br/>Agent 减肥<br/>§11 恢复]

    V100 --> V101 --> V102 --> V103 --> V104 --> V105 --> V106 --> V108 --> V109 --> V110 --> V111 --> V112 --> V1121

    V104 -.->|新增腐化点 9-14<br/>proactive-scan.py<br/>rot-detector agent| Art1[腐化扫描包]
    V105 -.->|新增腐化点 15-17<br/>文档诚实| Art2[rot-reinforcer]
    V108 -.->|新增腐化点 18-19<br/>障碍诚实<br/>抽象理由| Art3[反虚假交付]
    V110 -.->|§0.10 启动验证<br/>Phase 3.5| Art4[真实验证]
    V111 -.->|Phase 4.5 机械门禁<br/>Bug 录入| Art5[机械化]
    V112 -.->|§0.5.1 10 项清单<br/>§0.10 可见产物<br/>质疑性校验协议| Art6[同类约定]
    V1121 -.->|Agent ≤10 条 ≤150 行<br/>SUITE 模式合并| Art7[减肥]

    classDef ver fill:#95e1d3,color:#000
    classDef art fill:#ffd93d,color:#000
    class V100,V101,V102,V103,V104,V105,V106,V108,V109,V110,V111,V112,V1121 ver
    class Art1,Art2,Art3,Art4,Art5,Art6,Art7 art
```

## 二、版本特性矩阵

```mermaid
graph TB
    subgraph V100_V103[V10.0 - V10.3 基础期]
        F1[5 阶段流水线]
        F2[14 Articles 雏形]
        F3[契约四件套]
        F4[TDD 工作流]
        F5[视觉证据 3 层校验]
    end

    subgraph V104_V106[V10.4 - V10.6 腐化期]
        F6[腐化 7 大分类]
        F7[19 个腐烂点]
        F8[proactive-scan.py 8 项]
        F9[rot-detector agent]
        F10[Evidence 独立抽检]
        F11[文档三分层]
    end

    subgraph V108_V109[V10.8 - V10.9 诚实期]
        F12[障碍诚实汇报]
        F13[禁止抽象理由]
        F14[严重度分层 P0/P1/P2/P4]
        F15[反踩坑 6 条铁律]
        F16[项目健康度 agent]
        F17[防失真 4 大机制]
    end

    subgraph V110_V112[V10.10 - V10.12 验证期]
        F18[Phase 3.5 真实验证]
        F19[启动验证可见产物]
        F20[Bug 录入 6 字段]
        F21[phase-gate 机械门禁]
        F22[§0.5.1 10 项同类清单]
        F23[质疑性校验协议]
        F24[Agent 减肥 ≤10 ≤150]
    end

    classDef base fill:#95e1d3,color:#000
    classDef rot fill:#ffd93d,color:#000
    classDef honest fill:#ff8b94,color:#000
    classDef verify fill:#4ecdc4,color:#fff
    class F1,F2,F3,F4,F5 base
    class F6,F7,F8,F9,F10,F11 rot
    class F12,F13,F14,F15,F16,F17 honest
    class F18,F19,F20,F21,F22,F23,F24 verify
```

## 三、核心概念演进关系

```mermaid
mindmap
  root((V10 核心概念演进))
    真相源
      V10.0 Constitution
      V10.0 Spec > Contract > Code
      V10.7 文档分层
    质量底线
      V10.0 TDD 强制
      V10.0 满分硬门禁
      V10.0 委派纪律
    腐化防护
      V10.4 rot-detector
      V10.4 orphan-detector
      V10.4 dist-hash-check
      V10.4 visual-content-check
      V10.5 self-aggrandizing
      V10.5 state-card-staleness
      V10.5 stub-pileup
    诚实交付
      V10.6 Evidence 抽检
      V10.8 障碍诚实
      V10.8 禁止抽象理由
      V10.8 通过依据 3 类分层
    验证证据
      V10.10 Phase 3.5
      V10.10 启动可见产物
      V10.11 phase-gate.py
      V10.12 §0.10 硬约束
    升级治理
      V10.12 质疑性校验
      V10.12 §0.5.1 10 项
      V10.12.1 Agent 减肥
      V10.12.1 SUITE 模式
```

## 四、附录索引 — 文件清单

### 4.1 主干文件

```mermaid
graph LR
    Skills[SKILL.md<br/>主入口]
    Agents[agents/ 9 子代理]
    Refs[references/ 31 文档]
    Scripts[scripts/ 18 脚本]
    Templates[templates/ 18 模板]
    Hooks[templates/hooks/ 12 hook]

    Skills --> Agents
    Skills --> Refs
    Skills --> Scripts
    Skills --> Templates
    Templates --> Hooks

    classDef main fill:#ff6b6b,color:#fff
    classDef sub fill:#95e1d3,color:#000
    class Skills main
    class Agents,Refs,Scripts,Templates,Hooks sub
```

### 4.2 Agent 文件索引

| Agent | 主方法论 | 关键铁律 |
|-------|---------|---------|
| [planner.md](../agents/planner.md) | 探索 + 意图识别 | 6 条 |
| [spec-enhancer.md](../agents/spec-enhancer.md) | 增强验收 + 原型 | 7 条 |
| [spec-prototype-enhancer.md](../agents/spec-prototype-enhancer.md) | 原型反推 | 7 条 |
| [contract-writer.md](../agents/contract-writer.md) | 契约四件套 | 8 条 |
| [implementer.md](../agents/implementer.md) | TDD RED→GREEN | 9 条 |
| [reviewer.md](../agents/reviewer.md) | 质疑式验收官 | 10 条 |
| [rot-detector.md](../agents/rot-detector.md) | 腐化扫描 | 7 条 |
| [debugger.md](../agents/debugger.md) | 6 层排查 | 8 条 |
| [project-health-auditor.md](../agents/project-health-auditor.md) | 4 维度诊断 | 6 条 |

### 4.3 References 31 文档索引

| 主题 | 文件 |
|------|------|
| 入门流程 | [acceptance-gates-v10.md](../references/acceptance-gates-v10.md) / [artifact-lifecycle.md](../references/artifact-lifecycle.md) |
| 流程定义 | [artifact-schema.md](../references/artifact-schema.md) / [bug-workflow.md](../references/bug-workflow.md) / [cockpit.md](../references/cockpit.md) |
| 流程详情 | [changelog.md](../references/changelog.md) / [clarify-checklist.md](../references/clarify-checklist.md) |
| 宪法 | [constitution-detail.md](../references/constitution-detail.md) / [contract-first.md](../references/contract-first.md) |
| 调试 | [debugger-methodology.md](../references/debugger-methodology.md) / [designer-handoff.md](../references/designer-handoff.md) |
| 文档 | [doc-sync.md](../references/doc-sync.md) / [drift-detect.md](../references/drift-detect.md) / [glossary.md](../references/glossary.md) |
| 知识 | [knowledge-system-upgrade.md](../references/knowledge-system-upgrade.md) / [multi-round-revision-protocol.md](../references/multi-round-revision-protocol.md) |
| 融合 | [multi-source-fusion.md](../references/multi-source-fusion.md) / [prd-integration-workflow.md](../references/prd-integration-workflow.md) |
| 文档 | [process-doc-locations.md](../references/process-doc-locations.md) / [process-rot-analysis.md](../references/process-rot-analysis.md) |
| 健康 | [project-health-checklist.md](../references/project-health-checklist.md) / [project-structure.md](../references/project-structure.md) |
| 原型 | [prototype.md](../references/prototype.md) / [prototype-code-gap-analysis.md](../references/prototype-code-gap-analysis.md) |
| 原型联动 | [prototype-linkage.md](../references/prototype-linkage.md) / [prototype-reverse-spec.md](../references/prototype-reverse-spec.md) |
| 报告 | [report-growth.md](../references/report-growth.md) / [reset-and-verify-protocol.md](../references/reset-and-verify-protocol.md) |
| 评审 | [reviewer-templates.md](../references/reviewer-templates.md) / [skeptical-validation-protocol.md](../references/skeptical-validation-protocol.md) |
| 优化 | [skill-optimization-method.md](../references/skill-optimization-method.md) / [spec-enhancer-templates.md](../references/spec-enhancer-templates.md) |
| 通用 | [sub-agent-rules.md](../references/sub-agent-rules.md) / [tdd-workflow.md](../references/tdd-workflow.md) |

### 4.4 Scripts 18 脚本索引

| 类别 | 脚本 |
|------|------|
| 阶段门禁 | [phase-gate.py](../scripts/phase-gate.py) / [acceptance-audit.py](../scripts/acceptance-audit.py) |
| 腐化扫描 | [proactive-scan.py](../scripts/proactive-scan.py) / [self-diagnose.py](../scripts/self-diagnose.py) |
| 维护 | [change-status.py](../scripts/change-status.py) / [spec-purge.py](../scripts/spec-purge.py) |
| 检查 | [check_integration_contract.py](../scripts/check_integration_contract.py) / [check_prerequisites.py](../scripts/check_prerequisites.py) |
| 卫生 | [code-hygiene.py](../scripts/code-hygiene.py) / [dist-hash-check.py](../scripts/dist-hash-check.py) |
| 验证 | [visual-content-check.py](../scripts/visual-content-check.py) / [orphan-detector.py](../scripts/orphan-detector.py) |
| 工具 | [scan-templates.py](../scripts/scan-templates.py) / [scenario-dispatch.py](../scripts/scenario-dispatch.py) |
| 智能 | [reason-classifier.py](../scripts/reason-classifier.py) / [setup-feature.py](../scripts/setup-feature.py) |
| 迁移 | [migrate-v9-to-v10.py](../scripts/migrate-v9-to-v10.py) / [install-hooks.py](../scripts/install-hooks.py) |
| 提取 | [spec-knowledge-extract.py](../scripts/spec-knowledge-extract.py) / [dispatch-agent.py](../scripts/dispatch-agent.py) |
| 公共 | [common.py](../scripts/common.py) |

## 五、V10 文件清单

```
skill-markets/fullstack4TraeV10/
├── SKILL.md                                 # 主入口（V10.12.0）
├── scenarios.md                             # V10.11 场景演练
├── README.md                                # 项目说明
├── research/                                # �� 本研究目录（Mermaid 表达）
│   ├── 00-overview-mindmap.md               # 总览
│   ├── 01-constitution-mindmap.md           # 14 Articles
│   ├── 02-pipeline-flow-graph.md            # 5 阶段流水线
│   ├── 03-delegation-discipline.md          # 委派纪律
│   ├── 04-spec-driven-mindmap.md            # 契约先行 + TDD
│   ├── 05-rot-detection.md                  # 腐化防御
│   ├── 06-skeptical-validation.md           # 质疑性校验
│   ├── 07-agent-architecture.md             # 9 Agent 角色
│   ├── 08-skill-loading-protocol.md         # §0.5 + §0.10 协议
│   ├── 09-acceptance-gates.md               # 4 维验收 + 视觉证据
│   ├── 10-bug-debug-mindmap.md              # Bug 流水线
│   └── 11-version-evolution-graph.md         # 版本演进 + 索引
├── agents/                                  # 9 个 Agent
│   ├── planner.md
│   ├── spec-enhancer.md
│   ├── spec-prototype-enhancer.md
│   ├── contract-writer.md
│   ├── implementer.md
│   ├── reviewer.md
│   ├── rot-detector.md
│   ├── debugger.md
│   └── project-health-auditor.md
├── references/                              # 31 个文档
│   ├── acceptance-gates-v10.md
│   ├── artifact-lifecycle.md
│   ├── artifact-schema.md
│   ├── bug-workflow.md
│   ├── changelog.md
│   ├── clarify-checklist.md
│   ├── cockpit.md
│   ├── constitution-detail.md
│   ├── contract-first.md
│   ├── debugger-methodology.md
│   ├── designer-handoff.md
│   ├── doc-sync.md
│   ├── drift-detect.md
│   ├── glossary.md
│   ├── knowledge-system-upgrade.md
│   ├── multi-round-revision-protocol.md
│   ├── multi-source-fusion.md
│   ├── prd-integration-workflow.md
│   ├── process-doc-locations.md
│   ├── process-rot-analysis.md
│   ├── project-health-checklist.md
│   ├── project-structure.md
│   ├── prototype-code-gap-analysis.md
│   ├── prototype-linkage.md
│   ├── prototype-reverse-spec.md
│   ├── prototype.md
│   ├── report-growth.md
│   ├── reset-and-verify-protocol.md
│   ├── reviewer-templates.md
│   ├── skeptical-validation-protocol.md
│   ├── skill-optimization-method.md
│   ├── spec-enhancer-templates.md
│   ├── sub-agent-rules.md
│   └── tdd-workflow.md
├── scripts/                                 # 18 个脚本
│   ├── acceptance-audit.py
│   ├── change-status.py
│   ├── check_integration_contract.py
│   ├── check_prerequisites.py
│   ├── code-hygiene.py
│   ├── common.py
│   ├── dispatch-agent.py
│   ├── dist-hash-check.py
│   ├── install-hooks.py
│   ├── migrate-v9-to-v10.py
│   ├── orphan-detector.py
│   ├── phase-gate.py
│   ├── proactive-scan.py
│   ├── reason-classifier.py
│   ├── scenario-dispatch.py
│   ├── self-diagnose.py
│   ├── setup-feature.py
│   ├── spec-knowledge-extract.py
│   ├── spec-purge.py
│   ├── scan-templates.py
│   └── visual-content-check.py
└── templates/                               # 18 个模板
    ├── bug-template.md
    ├── checklist-template.md
    ├── constitution-template.md
    ├── spec-template.md
    ├── state-card.md
    ├── test-plan.md
    ├── test-plan-example.md
    ├── contracts/
    │   ├── api-contracts.md
    │   ├── domain-models.md
    │   ├── events.md
    │   └── validation-rules.md
    ├── hooks/
    │   ├── README.md
    │   ├── auto-test.py
    │   ├── complexity-guard.py
    │   ├── contract-gate.py
    │   ├── doc-sync-gate.py
    │   ├── drift-detect.py
    │   ├── fullstack-hooks.json
    │   ├── gitnexus-session-check.py
    │   ├── gitnexus-session-finalize.py
    │   ├── session-start.py
    │   ├── spec-validate-hook.py
    │   └── tasks-integrity.py
    └── scripts/
        ├── env-init.py
        ├── log-agent-prompt.py
        └── render-cockpit.py
```

## 六、关键引用

- 主入口: [SKILL.md](../SKILL.md)
- 版本历史: [changelog.md](../references/changelog.md)
- 场景演练: [scenarios.md](../scenarios.md)
- 术语表: [glossary.md](../references/glossary.md)
