---
title: 全栈 6 大 Agent 角色 Mindmap
description: planner / spec-enhancer / contract-writer / implementer / reviewer / rot-detector / debugger / project-health-auditor
layer: fact
---

# 全栈 6 大 Agent 角色 Mindmap

> V10.12 共 9 个 Agent（agents/ 目录），每个 Agent 4-10 条铁律，文件 ≤150 行。
> 核心原则: **主上下文不直行代码，只做协调；Agent 报告需主上下文质疑性验收**。

## 一、Agent 全景图

```mermaid
graph TB
    Main[主上下文<br/>协调 / 不直行代码<br/>质疑性验收]

    Main -->|Phase 0| P[planner<br/>意图识别 + 探索]
    Main -->|Phase 1| SE[spec-enhancer<br/>增强验收 + 原型]
    Main -->|Phase 1.5| SPE[spec-prototype-enhancer<br/>原型反推]
    Main -->|Phase 2| CW[contract-writer<br/>契约四件套]
    Main -->|Phase 3| IMP[implementer<br/>TDD RED→GREEN]
    Main -->|Phase 4| REV[reviewer<br/>质疑式验收官]
    Main -->|Phase 4.5| ROT[rot-detector<br/>腐化扫描]
    Main -->|Bug 链| DBG[debugger<br/>6 层排查]
    Main -->|自检| PHA[project-health-auditor<br/>4 维度诊断]

    classDef mainClass fill:#f38181,color:#fff
    classDef agentClass fill:#95e1d3,color:#000

    class Main mainClass
    class P,SE,SPE,CW,IMP,REV,ROT,DBG,PHA agentClass
```

## 二、Agent 通用铁律分组

```mermaid
mindmap
  root((Agent 通用铁律分组))
    知识背景
      读 14 Articles
      读项目 constitution.md
      读 spec+contracts
      不读归档
    委派纪律
      走 §0.5 协议
      不直行主上下文任务
      输出 Completion Report
      4 字段 status / evidence / pass_count / next_hook
    质疑性校验
      SKEPTICAL VALIDATION
      升级方案必走 4 维度
      不盲信 P0/P1
      不接受抽象理由
    协作风控
      失败 5 次回退 Phase 0
      禁止编造 evidence
      禁止应付性汇报
      主上下文二次抽检
```

## 三、Agent 详细铁律矩阵

```mermaid
graph TB
    subgraph P[planner]
        P1[1 EXPLORE FIRST]
        P2[2 SUBAGENT ONLY]
        P3[3 IMPACT BY TOOL]
        P4[4 DEDUP BY ATOM]
        P5[5 PURGE ON REFACTOR]
        P6[6 SKEPTICAL VALIDATION]
    end

    subgraph SE[spec-enhancer]
        SE1[ENHANCE NOT REWRITE]
        SE2[E2E MIN 2]
        SE3[INVARIANTS MIN 1]
        SE4[ACCEPTANCE MIN 3]
        SE5[UI TRIGGER PROTO]
        SE6[SKEPTICAL VALIDATION]
        SE7[TEST PLAN GATE]
    end

    subgraph CW[contract-writer]
        CW1[CONTRACT IS IMMUTABLE]
        CW2[DOMAIN FIRST]
        CW3[ORPHAN TEST SWEEP]
        CW4[ADDITIVE OVER BREAKING]
        CW5[DELTA ONLY]
        CW6[CONTRACT DRIVES TEST]
        CW7[NO CODE NO CONTRACT]
        CW8[SKEPTICAL VALIDATION]
    end

    subgraph IMPL[implementer]
        I1[深度理解再编码]
        I2[TDD 即时 + 红绿重构]
        I3[漂移必报告]
        I4[基础模块留文档]
        I5[BUNDLE STALENESS]
        I6[代码卫生]
        I7[量化必汇报]
        I8[禁止虚假绿灯]
        I9[SKEPTICAL + TEST PLAN SUITE]
    end

    subgraph REV[reviewer]
        R1[FAIL IS FAIL]
        R2[SCORING IS DERIVED]
        R3[FOUR DIMENSIONS]
        R4[NO DOWNGRADE]
        R5[VERIFY UNDERSTANDING]
        R6[REVIEWER DOES NOT FIX]
        R7[FUNCTIONAL CHECK]
        R8[CROSS-SESSION VERIFY]
        R9[质疑式验收 SUITE]
        R10[关键门禁套件]
    end

    subgraph ROT[rot-detector]
        RO1[META SELF-DIAG]
        RO2[PROACTIVE SCAN]
        RO3[REPORT ROT 7 类]
        RO4[ACTIONABLE FIX]
        RO5[NO ROT, NO ACCEPT]
        RO6[NEW ROT PR]
        RO7[SKEPTICAL VALIDATION]
    end

    subgraph DBG[debugger]
        D1[NO FIX WITHOUT ROOT CAUSE]
        D2[NO ROOT CAUSE WITHOUT EVIDENCE]
        D3[NO FIX WITHOUT FAILING TEST]
        D4[NO REPRO NO DIAGNOSIS]
        D5[5 轮上限]
        D6[禁止篡改测试用例]
        D7[GitNexus First]
        D8[SKEPTICAL VALIDATION]
    end

    subgraph PHA[project-health-auditor]
        PH1[DYNAMIC ADAPT]
        PH2[MULTI_DIMENSION]
        PH3[EVIDENCE BASED]
        PH4[REPORT STRUCTURE]
        PH5[MANUAL FIX]
        PH6[SKEPTICAL VALIDATION]
    end

    classDef plannerStyle fill:#95e1d3,color:#000
    classDef specStyle fill:#a8e6cf,color:#000
    classDef contractStyle fill:#ffd93d,color:#000
    classDef implStyle fill:#ff8b94,color:#000
    classDef reviewStyle fill:#c7ceea,color:#000
    classDef rotStyle fill:#ffaaa5,color:#000
    classDef debugStyle fill:#b4f8c8,color:#000
    classDef healthStyle fill:#fbe7c6,color:#000

    class P1,P2,P3,P4,P5,P6 plannerStyle
    class SE1,SE2,SE3,SE4,SE5,SE6,SE7 specStyle
    class CW1,CW2,CW3,CW4,CW5,CW6,CW7,CW8 contractStyle
    class I1,I2,I3,I4,I5,I6,I7,I8,I9 implStyle
    class R1,R2,R3,R4,R5,R6,R7,R8,R9,R10 reviewStyle
    class RO1,RO2,RO3,RO4,RO5,RO6,RO7 rotStyle
    class D1,D2,D3,D4,D5,D6,D7,D8 debugStyle
    class PH1,PH2,PH3,PH4,PH5,PH6 healthStyle
```

## 四、Agent 产出对比

```mermaid
graph LR
    subgraph 产出物
        P[plan.md<br/>状态卡]
        SE[spec.md<br/>Enhanced Acceptance<br/>prototypes/<br/>test-plan.md]
        CW[contracts/ 四件套<br/>测试骨架]
        IMPL[代码 + 测试<br/>模块文档]
        REV[review-latest.md<br/>4 维报告<br/>DOC SYNC]
        ROT[腐化扫描报告<br/>fix-list JSON]
        DBG[root-cause.md<br/>修复代码<br/>回归测试]
        PHA[project-health<br/>.md + .json]
    end

    classDef artifact fill:#95e1d3,color:#000
    class P,SE,CW,IMPL,REV,ROT,DBG,PHA artifact
```

## 五、§11 约束 — Agent 文件 ≤ 10 条铁律 ≤ 150 行

```mermaid
mindmap
  root((§11 约束<br/>V10.12.1))
    总约束
      Agent 文件 ≤ 10 条铁律
      Agent 文件 ≤ 150 行
      SKILL.md 不啰嗦
      引用 references 而非内联
    减肥历史
      V10.12 reviewer 16 条 → 10 条
      用 SUITE 模式合并
      6 条 V10.12 → 2 条
      4 条 V10.8 → 1 条
    新增铁律流程
      必走质疑性校验
      §1.4 修复成本
      是否真必要
      否则取消
    产出
      信息密度 ↑ 10/108
      AGENTS.md 不再需要例外
      上下文不击穿
```

## 六、关键引用

- Agent 文件:
  - [planner.md](../agents/planner.md)
  - [spec-enhancer.md](../agents/spec-enhancer.md)
  - [spec-prototype-enhancer.md](../agents/spec-prototype-enhancer.md)
  - [contract-writer.md](../agents/contract-writer.md)
  - [implementer.md](../agents/implementer.md)
  - [reviewer.md](../agents/reviewer.md)
  - [rot-detector.md](../agents/rot-detector.md)
  - [debugger.md](../agents/debugger.md)
  - [project-health-auditor.md](../agents/project-health-auditor.md)
- 委派速查表: [SKILL.md §1](../SKILL.md)
- §11 约束: [AGENTS.md §11](../../../../../AGENTS.md)
