---
title: fullstack4TraeV10 思想总览
description: 用 mindmap 表达 V10.12 整体哲学 + 5 阶段 + 14 Articles + 16 铁律 + 5 维度硬门禁
layer: fact
---

# Fullstack4TraeV10 思想总览

> V10.12 = "Spec 真相源 + 5 阶段流水线 + 14 Articles 不可降级 + 5 维度硬门禁 + 腐化可检测 + 启证可见产物"。
> 设计哲学: **复用而非自研 / 质量而非流程 / 验证而非信任 / 干净而非兼容 / 主动而非被动 / 诚实而非吹嘘 / 骨感而非堆积 / 分层而非混置**。

## 一、核心哲学 Mindmap

```mermaid
mindmap
  root((Fullstack4TraeV10<br/>V10.12 哲学))
    复用而非自研
      spec-kit 五阶段骨架
      GitNexus 取代 grep
      既存工具合并而非再造
    质量而非流程
      14 Articles 不可降级
      5 维度满分硬门禁
      失败即阻断
    验证而非信任
      mechanical script
      acceptance-audit.py
      proactive-scan.py
      self-diagnose.py
    干净而非兼容
      无 .bak / .old
      archive 不可变
      失败的骨架 2 周冻结
    主动而非被动
      rot-detector 必跑
      质疑式验收 证伪
      主动证据索要
    诚实而非吹嘘
      通过依据 3 类分层
      障碍 5 字段报告
      禁止编造抽象理由
    骨感而非堆积
      Agent 文件 ≤10 条铁律 ≤150 行
      添加必走质疑性校验
      反踩坑 6 条精简
    分层而非混置
      fact / process / log 三层
      DOC_WHITELIST 注入
      layer 标签覆盖率
```

## 二、骨架流程（5 阶段 + Phase 3.5/4.5）

```mermaid
graph LR
    P0[Phase 0<br/>Plan<br/>�� 用户确认]
    P1[Phase 1<br/>Spec<br/>�� 用户确认]
    P2[Phase 2<br/>Contract<br/>⚙ 自动]
    P3[Phase 3<br/>Implement<br/>�� 用户确认]
    P35[Phase 3.5<br/>真实验证<br/>�� 5 项必跑]
    P4[Phase 4<br/>Review<br/>⚙ 自动]
    P45[Phase 4.5<br/>Rot Scan<br/>�� 必跑]

    P0 --> P1 --> P2 --> P3 --> P35 --> P4 --> P45

    classDef userConfirm fill:#ff6b6b,color:#fff
    classDef autoOk fill:#4ecdc4,color:#fff
    class P0,P1,P3,P35,P45 userConfirm
    class P2,P4 autoOk
```

## 三、14 Articles 全景 Mindmap

```mermaid
mindmap
  root((14 Articles<br/>不可降级铁律))
    质量底线
      I TDD 强制
      II 满分硬门禁
      III 零残留迁移
    委派纪律
      IV 主上下文不直行代码
      V GitNexus First
      VI Ponytail First
    真相源
      VII 文档与代码冲突以文档为准
      VIII 归档不可变
    即时同步
      IX TDD 即时
      X 异会话验证
      XI 视觉真实验证
    反腐化
      XII 文档诚实
      XIII 骨架是债
      XIV rot-detector 必跑
    反虚假
      XV 障碍诚实汇报
      XVI 禁止编造抽象理由
```

## 四、5 维度硬门禁

```mermaid
mindmap
  root((5 维度 + 功能效果<br/>任一非满分 = �� REJECT))
    维度 1 代码层 25%
      单元测试全绿
      Contract 测试全绿
      Lint 0 error
      覆盖率 ≥ 90%
      无 TODO/FIXME
      code-hygiene.py 通过
      理解确认 2 项验证
    维度 2 API 层 30%
      真实端点非 mock
      接口签名 100% 一致
      数据模型 100% 一致
      错误码 100% 一致
      事件 100% 一致
    维度 3 UI/UX 层 25%
      Phase A 视觉一致性
      Phase B 交互逻辑
      Phase C UI 细节
      6 项检查清单
    维度 4 模块边际 20%
      GitNexus impact
      下游无副作用
      文档同步
      扩展点标注
    功能效果验证
      用户视角确认
      Closure P0 演示
      用户场景脚本
```

## 五、6 大 Agent 角色

```mermaid
graph TB
    Main[主上下文<br/>协调/不直行代码]

    Main -->|Phase 0| Planner[planner<br/>探索 + 意图识别]
    Main -->|Phase 1| SpecEnhancer[spec-enhancer<br/>增强验收维度]
    Main -->|Phase 2| ContractWriter[contract-writer<br/>契约四件套]
    Main -->|Phase 3| Implementer[implementer<br/>TDD RED→GREEN]
    Main -->|Phase 4| Reviewer[reviewer<br/>质疑式验收官]
    Main -->|Phase 4.5| RotDetector[rot-detector<br/>腐化扫描]
    Main -->|Bug 链| Debugger[debugger<br/>6 层排查]
    Main -->|自检| HealthAuditor[project-health-auditor<br/>4 维度诊断]

    classDef agent fill:#95e1d3,color:#000
    classDef main fill:#f38181,color:#fff
    class Main main
    class Planner,SpecEnhancer,ContractWriter,Implementer,Reviewer,RotDetector,Debugger,HealthAuditor agent
```

## 六、关键引用入口

| 主题 | 核心文件 |
|------|---------|
| 哲学骨架 | [SKILL.md](../SKILL.md) |
| 14 Articles 详情 | [constitution-detail.md](../references/constitution-detail.md) |
| 验收门禁 | [acceptance-gates-v10.md](../references/acceptance-gates-v10.md) |
| 委派铁律 | [sub-agent-rules.md](../references/sub-agent-rules.md) |
| 文档分层 | [artifact-lifecycle.md](../references/artifact-lifecycle.md) |
| 流程腐化 | [process-rot-analysis.md](../references/process-rot-analysis.md) |
| 质疑性校验 | [skeptical-validation-protocol.md](../references/skeptical-validation-protocol.md) |
| 极致优化方法论 | [skill