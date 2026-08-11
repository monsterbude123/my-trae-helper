---
title: 契约先行 + Spec 真相源 + TDD + 文档分层 Mindmap
description: 文档驱动开发 + 契约四件套 + TDD 三步循环 + 文档三层标注
layer: fact
---

# 契约先行 + Spec 真相源 + TDD + 文档分层 Mindmap

> V10 核心立场: **Spec 是真相源，代码为规格服务。变更冲突顺序: Constitution > Spec > Contract > Code > 个人判断**。

## 一、契约先行 (Contract-First) 全景

```mermaid
mindmap
  root((Contract-First<br/>契约先行))
    契约四件套
      1 API 契约
        路径
        方法
        请求/响应
        错误码
      2 领域模型
        实体字段
        类型
        必填
        不变量
      3 事件契约
        发布者
        订阅者
        负载
      4 校验规则
        字段 regex
        长度
        业务规则
    变更流程
      ADDITIVE 兼容
        新增可选字段
        直接添加
        minor 版本
      BREAKING 不兼容
        删字段
        改类型
        改路径
        �� 用户确认
        major 版本
    契约测试骨架
      describe 接口名
      it 场景
      toMatchSnapshot
      Vitest / Jest
      contract-to-implement gate
    路径选择
      docs/specs/feature/contracts/test-skeleton/
      __tests__/contracts/
      phase-gate.py 自动检测
```

## 二、Spec 驱动工件依赖图

```mermaid
graph TB
    Plan[plan.md<br/>Why + Capabilities + Impact]
    Define[define.md<br/>Non-Goals + Out of Scope]
    Spec[spec.md<br/>行为规格 + 验收]
    Design[design.md<br/>技术方案 + 架构]
    Tasks[tasks.md<br/>checkbox 清单]
    Contracts[contracts/<br/>四件套 + 测试骨架]
    Prototype[prototypes/<br/>design-prompt + ui-ux-logic]
    Impl[实现代码 + 测试]
    Review[review-latest.md<br/>4 维验收]

    Plan --> Define
    Plan --> Spec
    Plan --> Design
    Define --> Prototype
    Spec --> Tasks
    Design --> Tasks
    Spec --> Contracts
    Tasks --> Impl
    Contracts --> Impl
    Impl --> Review

    Plan -.->|Enablers<br/>Not Gates| Flex1[可并行]
    Spec -.-> Flex1
    Design -.-> Flex1

    classDef must fill:#ff6b6b,color:#fff
    classDef opt fill:#95e1d3,color:#000
    class Plan,Spec,Contracts,Impl,Review must
    class Define,Design,Tasks,Prototype opt
```

## 三、TDD 工作流三步循环

```mermaid
flowchart LR
    Red[�� RED<br/>编写失败测试]
    Green[�� GREEN<br/>最简实现]
    Refactor[♻️ REFACTOR<br/>优化质量]
    Drift[�� DRIFT CHECK<br/>vs contracts/]

    Red -->|测试 FAIL| Green
    Green -->|测试 PASS| Refactor
    Refactor -->|测试全 PASS| Drift
    Drift -->|无漂移| Next[下一个 Task]
    Drift -->|发现漂移| Report[报告回流<br/>MEDIUM / HIGH]

    Red -.->|禁止跳过| Ban1[��]
    Refactor -.->|禁止修改测试让通过| Ban2[��]

    classDef step fill:#95e1d3,color:#000
    classDef ban fill:#ff6b6b,color:#fff
    classDef report fill:#ffd93d,color:#000
    class Red,Green,Refactor,Drift,Next step
    class Ban1,Ban2 ban
    class Report report
```

## 四、文档三层标注 (layer:)

```mermaid
mindmap
  root((文档分层<br/>layer 标签))
    fact 事实层
      含义: 项目真相源
      子代理: 必读
      复盘: 必读
      文件: contracts/ spec.md
      ARCHITECTURE.md
      modules/ AGENTS.md
    process 过程层
      含义: 过程产物
      子代理: 禁读
      复盘: 可读
      文件: diagnose.md
      fix_result.md
      analysis.md
      evidence JSON
    log 操作日志
      含义: 操作日志
      子代理: 不作验收依据
      复盘: 可读
      文件: changelog
      commit log
      state-card 历史
      review 报告
    默认策略
      无 layer 字段
      默认 process
      防止噪音泄漏
```

## 五、目录 layer 映射表

```mermaid
graph LR
    subgraph fact
        F1[docs/api-endpoints/]
        F2[docs/domain-models/]
        F3[docs/events/]
        F4[docs/contracts/]
        F5[docs/modules/]
        F6[docs/ARCHITECTURE.md]
        F7[AGENTS.md]
    end

    subgraph process
        P1[.state-card.md]
        P2[docs/DECISIONS.md]
        P3[docs/bugs/]
        P4[diagnostic/]
        P5[_invalidated/]
    end

    subgraph log
        L1[docs/history/]
        L2[.history.md]
        L3[docs/reports/]
        L4[docs/archive/]
        L5[docs/specs/archive/]
    end

    classDef factStyle fill:#4ecdc4,color:#fff
    classDef processStyle fill:#ffd93d,color:#000
    classDef logStyle fill:#95e1d3,color:#000
    class F1,F2,F3,F4,F5,F6,F7 factStyle
    class P1,P2,P3,P4,P5 processStyle
    class L1,L2,L3,L4,L5 logStyle
```

## 六、测试层级金字塔

```mermaid
graph TB
    E2E[E2E 测试<br/>端到端<br/>模拟用户操作]
    Int[Integration 测试<br/>模块间协作]
    Contract[Contract 测试<br/>接口契约验证<br/>100% 覆盖]
    Unit[Unit 测试<br/>单个函数/类<br/>≥ 80% 覆盖]

    E2E --> Int
    Int --> Contract
    Contract --> Unit

    classDef layer fill:#95e1d3,color:#000
    class E2E,Int,Contract,Unit layer
```

## 七、测试命名规范

```mermaid
mindmap
  root((test 命名规范))
    格式
      test 行为 条件 预期
    示例
      test create user happy path returns user
      test create user duplicate email returns error
      test payment insufficient balance returns 400
    禁止
      跳过测试写实现
      修改测试让通过
      只写 Happy Path
      断言不明确 expect toBeTruthy
```

## 八、关键引用

- 契约四件套: [contract-first.md](../references/contract-first.md)
- TDD 工作流: [tdd-workflow.md](../references/tdd-workflow.md)
- 文档分层: [artifact-lifecycle.md](../references/artifact-lifecycle.md)
- 工件依赖图: [artifact-schema.md](../references/artifact-schema.md)
- DOC SYNC: [doc-sync.md](../references/doc-sync.md)
- 模板:
  - [api-contracts.md