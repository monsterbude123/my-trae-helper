---
title: Bug 录入 + 5 步流水线 + 6 层排查 + 视觉验证 Mindmap
description: 用户反馈 → 6 字段录入 → 5 步流水线 → 6 层根因分析 → bug 单模板
layer: fact
---

# Bug 录入 + 5 步流水线 + 6 层排查 + 视觉验证 Mindmap

> V10.11 NEW: Phase B.0 录入（用户反馈 → bug 单）。
> 核心铁律: **NO FIX WITHOUT ROOT CAUSE / NO REPRO NO DIAGNOSIS / NO FIX WITHOUT FAILING TEST**。

## 一、Bug 完整路径

```mermaid
flowchart TD
    User[用户反馈问题]
    Ask[主上下文询问:<br/>是否作为 bug 单录入?]
    Reject[拒绝 → 一般咨询]
    Accept[同意 → Phase B.0 录入]

    User --> Ask
    Ask -->|用户拒绝| Reject
    Ask -->|用户同意| Accept

    Accept --> B0[Phase B.0 录入<br/>6 字段]
    B0 --> I1[intake<br/>意图 = Bug<br/>路由 debugger]
    I1 --> DBG[debugger agent<br/>5 步流水线]

    DBG --> S1[Step 1 诊断解析]
    DBG --> S2[Step 2 编号 登记<br/>BUG-YYYYMMDD-NNN]
    DBG --> S3[Step 3 复现 截图]
    DBG --> S4[Step 4 根因分析<br/>6 层排查]
    DBG --> S5[Step 5 结构化报告]

    S5 --> Fix[Step 6 修复<br/>TDD �� → ��]
    Fix --> Reg[Step 7 回归验证<br/>全量 + before/after 截图]

    classDef phase fill:#95e1d3,color:#000
    classDef bug fill:#ff6b6b,color:#fff
    classDef path fill:#4ecdc4,color:#fff
    class User,Ask,B0,I1,DBG,S1,S2,S3,S4,S5,Fix,Reg phase
    class Reject bug
    class Accept path
```

## 二、Phase B.0 录入 6 字段

```mermaid
mindmap
  root((Phase B.0<br/>6 字段必填))
    1 用户原话
      必填
      用户原始描述
      不加修饰
    2 用户操作
      必填
      复述步骤
      触发流程
    3 实际效果
      必填
      观察异常
      截图/报错
    4 关联功能文档
      可选
      主上下文搜索
      定位章节
    5 期望
      必填
      用户期望
      应该行为
    6 状态
      必填
      OPEN 新录入
      TRIAGE 待分诊
      ASSIGNED 已分配
```

## 三、Bug 单编号规则

```mermaid
graph LR
    Module[模块] --> Format[格式]
    Seq[序号 3 位左补零] --> Format
    Desc[简述 kebab-case ≤ 30 字符] --> Format

    Format --> Output[例: settings-009-config-key-case-mismatch]

    Module -->|settings/assets/models/queue/diagnostic| M1[5 个模块]
    Seq -->|累计| S1[递增]
    Desc -->|小写 + 连字符| D1[简明确]

    classDef step fill:#95e1d3,color:#000
    class Format,Output step
    class M1,S1,D1 input
```

## 四、Bug 单文档结构

```mermaid
graph TB
    FM[Frontmatter<br/>layer: fact<br/>bug_id<br/>status<br/>severity P1/P2/P3<br/>created_at]

    subgraph H1[Bug 简述]
        H1a[用户原话<br/>用户原始描述]
    end

    subgraph H2[用户操作]
        H2a[1. 步骤 1<br/>2. 步骤 2<br/>3. ...]
    end

    subgraph H3[实际效果]
        H3a[现象<br/>截图/报错链接]
    end

    subgraph H4[期望]
        H4a[用户认为应该]
    end

    subgraph H5[根因分析]
        H5a[GitNexus context/impact<br/>调用链定位]
    end

    subgraph H6[修复]
        H6a[diff ≤ 30 行<br/>回归测试 PASS]
    end

    FM --> H1 --> H2 --> H3 --> H4 --> H5 --> H6

    classDef doc fill:#95e1d3,color:#000
    class FM,H1,H2,H3,H4,H5,H6,H1a,H2a,H3a,H4a,H5a,H6a doc
```

## 五、5 步流水线

```mermaid
flowchart TD
    S1[Step 1 诊断解析]
    S2[Step 2 编号 登记]
    S3[Step 3 复现 截图]
    S4[Step 4 根因分析]
    S5[Step 5 结构化报告]

    S1 --> S2 --> S3 --> S4 --> S5

    S1 --> S1a[提取 error_type]
    S1 --> S1b[stack_trace]
    S1 --> S1c[timestamp]
    S1 --> S1d[method+url]
    S1 --> S1e[status_code]
    S1 --> S1f[user_steps]

    S2 --> S2a[Bug ID = BUG-YYYYMMDD-NNN]
    S2 --> S2b[创建 docs/bugs/BUG-ID/]
    S2 --> S2c[写 reproduction.md]

    S3 --> S3a[必须实际复现]
    S3 --> S3b[禁止仅凭堆栈推测]
    S3 --> S3c[复现失败标注]
    S3 --> S3d[截图正常状态作对比]

    S4 --> S4a[GitNexus context]
    S4 --> S4b[query]
    S4 --> S4c[impact]
    S4 --> S4d[禁止 grep 降级]
    S4 --> S4e[写 root-cause.md]

    S5 --> S5a[report.md]
    S5 --> S5b[Bug ID / 严重级别]
    S5 --> S5c[复现率 / 截图]
    S5 --> S5d[根因 / 建议修复]
    S5 --> S5e[更新 docs/bugs/INDEX.md]

    S1 -.->|�� e2e 先行| Red[初始 test FAIL]
    S5 -.->|�� 写修复代码| Fix[�� GREEN]

    classDef step fill:#95e1d3,color:#000
    classDef detail fill:#ffd93d,color:#000
    class S1,S2,S3,S4,S5 step
    class S1a,S1b,S1c,S1d,S1e,S1f,S2a,S2b,S2c,S3a,S3b,S3c,S3d,S4a,S4b,S4c,S4d,S4e,S5a,S5b,S5c,S5d,S5e detail
```

## 六、6 层排查

```mermaid
graph TB
    L1[1 网络层<br/>DNS / 代理 / CDN]
    L2[2 接入层<br/>网关 / 限流 / WAF]
    L3[3 应用层<br/>业务逻辑 / 状态]
    L4[4 数据层<br/>DB / Cache / 索引]
    L5[5 集成层<br/>第三方 API / SDK]
    L6[6 客户端层<br/>UI / 浏览器 / 设备]

    L1 --> L2 --> L3 --> L4 --> L5 --> L6

    L1 -.->|curl 测连通性?<br/>第三方 API?| Method1[方法 1]
    L2 -.->|网关日志?<br/>HF Model 路由器?| Method2[方法 2]
    L3 -.->|详细 stack trace?<br/>GitNexus context?| Method3[方法 3]
    L4 -.->|SQL 慢查询?<br/>Redis 缓存?| Method4[方法 4]
    L5 -.->|API 状态码?<br/>SDK 错误?| Method5[方法 5]
    L6 -.->|UI 截图?<br/>浏览器控制台?| Method6[方法 6]

    L3 -.->|跨层不得修| Collect[采集 vs 解析<br/>二分判定]
    Collect -.->|e2e 先行| E2E[初始 test FAIL]

    classDef layer fill:#95e1d3,color:#000
    classDef method fill:#ffd93d,color:#000
    classDef core fill:#ff6b6b,color:#fff
    class L1,L2,L3,L4,L5,L6 layer
    class Method1,Method2,Method3,Method4,Method5,Method6 method
    class Collect,E2E core
```

## 七、debugger 铁律矩阵

```mermaid
mindmap
  root((debugger 8 铁律))
    1 NO FIX WITHOUT ROOT CAUSE
      无根因证据
      不写修复代码
    2 NO ROOT CAUSE WITHOUT EVIDENCE
      根因必附日志
      堆栈或复现步骤
    3 NO FIX WITHOUT FAILING TEST
      无失败测试
      不写修复
      e2e 先行
    4 NO REPRO NO DIAGNOSIS
      必须实际复现
      禁止仅凭堆栈推测
    5 5 轮上限
      同一段代码
      5 轮仍失败
      停下汇报换思路
    6 禁止篡改测试
      不可修改断言
      让测试通过
    7 GitNexus First
      impact 评估
      禁止 grep 降级
    8 SKEPTICAL VALIDATION
      4 维度校验
      §1.1 根因验证
      §1.4 成本校验
```

## 八、关键引用

- Bug 工作流: [bug-workflow.md](../references/bug-workflow.md)
- debugger Agent: [debugger.md](../agents/debugger.md)
- 调试方法论: [debugger-methodology.md](../references/debugger-methodology.md)
- Bug 模板: [bug-template.md](../templates/bug-template.md)
- 多轮修订协议: [multi-round-revision-protocol.md](../references/multi-round-revision-prot