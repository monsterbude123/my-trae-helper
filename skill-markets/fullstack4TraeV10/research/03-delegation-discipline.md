---
title: 委派纪律 + 子代理铁律 思维导图
description: 主上下文不直行代码、coding-task 强制头部、三层独立验证、视觉验证、破坏性操作红线
layer: fact
---

# 委派纪律 + 子代理铁律 Mindmap

> V10.8 核心: **防止主上下文直行代码、子代理返回虚假 evidence、应付性汇报、破坏性操作**。
> 原则: **主上下文只协调，子代理做执行，主上下文必独立验证三层**。

## 一、委派场景化决策

```mermaid
mindmap
  root((委派类型<br/>决策树))
    exploration-task
      search 子代理
      无 Completion Report
      仅结构化摘要
      例: 代码探索 / 文档勘察
    coding-task
      general_purpose_task
      必有 Completion Report
      4 字段 status / evidence / pass_count / next_hook
      强制头部注入
        MUST-READ
          AGENTS.md
          .trae/rules/
        PIPELINE
          phase: {N}
        DOC_WHITELIST
          白名单路径
        GITNEXUS
          impact 调用
        TASK
          ≤200 字符
        OUTPUT
          4 字段
```

## 二、子代理返回后三层独立验证

```mermaid
flowchart TD
    Return[子代理返回<br/>Completion Report]
    Layer1[Layer 1 evidence 存在性]
    Layer2[Layer 2 pass_count 准确性]
    Layer3[Layer 3 产物存在性]

    Return --> Layer1
    Return --> Layer2
    Return --> Layer3

    Layer1 ->|抽 1 个 evidence| Read[主上下文亲自 Read]
    Layer1 -.->|不匹配| Reject1[�� REJECT<br/>计入失败 1 次]

    Layer2 ->|跑测试命令| Run[主上下文亲自 Run]
    Layer2 -.->|不一致| Reject2[�� REJECT]

    Layer3 ->|Glob / LS 检查| Glob[主上下文亲自 Glob]
    Layer3 -.->|文件不存在| Reject3[�� REJECT]

    Read --> Match{证据匹配?}
    Run --> TestNum{测试数一致?}
    Glob --> Exists{文件存在?}

    Match -->|是| Pass1[✅]
    Match -->|否| Reject1

    TestNum -->|是| Pass2[✅]
    TestNum -->|否| Reject2

    Exists -->|是| Pass3[✅]
    Exists -->|否| Reject3

    Pass1 --> Pass[三层全过<br/>通过]
    Pass2 --> Pass
    Pass3 --> Pass

    Reject1 --> Total[记录失败计数]
    Reject2 --> Total
    Reject3 --> Total

    classDef pass fill:#4ecdc4,color:#fff
    classDef reject fill:#ff6b6b,color:#fff
    classDef layer fill:#95e1d3,color:#000
    class Layer1,Layer2,Layer3,Read,Run,Glob layer
    class Pass1,Pass2,Pass3,Pass pass
    class Reject1,Reject2,Reject3,Total reject
```

## 三、视觉验证增强协议

```mermaid
graph LR
    V1[Step 1 委派前]
    V2[Step 2 子代理返回后]
    V3[Step 3 发现不符]

    V1 --> Read1[主上下文 Read 目标截图]
    Read1 --> Extract[提取 hex 码值]
    Extract --> Inline[inline 进 prompt]

    V2 --> Read2[主上下文亲自 Read 截图]
    Read2 --> Compare{对比 AI 描述 vs 实际像素}

    Compare -->|匹配| Pass[✅]
    Compare -->|不符| V3

    V3 --> Stop[立即停止<br/>不编造事实]

    classDef stop fill:#ff6b6b,color:#fff
    classDef pass fill:#4ecdc4,color:#fff
    classDef step fill:#95e1d3,color:#000
    class V1,V2,V3,Read1,Read2,Compare,Inline,Extract,Stop step
    class Pass pass
    class Stop stop
```

## 四、破坏性操作 4 步强制流程

```mermaid
flowchart TD
    Trigger[触发: rmtree / rm -rf /<br/>大文件 Delete / 跨盘 mv]
    Step1[Step 1 列清单]
    Step2[Step 2 用户确认]
    Step3[Step 3 Trash 兜底]
    Step4[Step 4 跨盘额外校验]

    Trigger --> Step1
    Step1 -->|find / ls / Get-ChildItem | measure| List[清单: 路径 + 字节数]
    List --> Step2
    Step2 -->|客服确认前禁止执行| User[用户确认]
    User --> Step3
    Step3 -->|mv 到 _trash_<ts>/<br/>保留 7 天可恢复| Trash[Mv to Trash]
    Trash --> Step4
    Step4 -->|implementer 报告空目录<br/>主上下文也自己 ls 一次| Cross[跨盘验证]

    classDef forbid fill:#ff6b6b,color:#fff
    classDef step fill:#95e1d3,color:#000
    class Trigger,List,User,Trash,Cross forbid
    class Step1,Step2,Step3,Step4 step
```

## 五、失败处理 5 步升级

```mermaid
graph LR
    F1[失败 1 次: retry]
    F2[失败 2 次: 切 agent 类型]
    F3[失败 5 次: rescue hatch]
    F4[禁止: 应付性汇报]
    F5[禁止: 编造 evidence]

    F1 --> F2
    F2 --> F3
    F3 --> Back[回退 Phase 0 重做需求分析]

    F4 -.->|不说: 我搞错了 /<br/>子代理给虚假内容 /<br/>应该 xxxx| Ban1[��]
    F5 -.->|evidence 必须真实 file:line<br/>主上下文抽检<br/>造假 = REJECT + 计入失败| Ban2[��]

    classDef failclass fill:#ff6b6b,color:#fff
    classDef step fill:#95e1d3,color:#000
    class F1,F2,F3,Back step
    class F4,F5,Ban1,Ban2 failclass
```

## 六、批量并行推进三步流水线

```mermaid
graph TD
    A[Step 1 Exhaustive Gap Sweep]
    B[Step 2 Priority Batching]
    C[Step 3 Batch-Roll-Verify]

    A --> A1[左端读目标参照物]
    A --> A2[右端盘点当前实现]
    A1 --> A3[P0/P1/P2 gap 分级清单]
    A2 --> A3

    A3 --> B
    B --> B1[P0 批次 1]
    B --> B2[P1 批次 2]
    B --> B3[P2 末批]
    B1 -->|每批 ≤ 3 agent<br/>上限 5| B4[并行委派]
    B2 --> B4
    B3 --> B4

    B4 --> C
    C --> C1[全部返回<br/>git diff --stat 逐文件]
    C1 --> C2[死 agent 重委派]
    C2 --> C3[通过后下一批]

    C1 -.->|diff 为空| Dead[标记死 agent<br/>立即重委派]

    classDef forbid fill:#ff6b6b,color:#fff
    classDef step fill:#95e1d3,color:#000
    class A,B,C,A1,A2,A3,B1,B2,B3,B4,C1,C2,C3 step
    class Dead forbid
```

## 七、文档分层判定

```mermaid
mindmap
  root((文档三层<br/>判定))
    fact 事实层
      必读
      任务输入
      子代理依据
      例: contracts/
      spec.md
      ARCHITECTURE.md
      模块文档
    process 过程层
      禁读
      不作验收依据
      主上下文摘要注入
      例: diagnose.md
      fix_result.md
      分析手记
      v1v2v3 修复记录
    log 操作日志
      可看
      不作验收依据
      历史证据
      例: changelog
      commit log
      review 报告
      state-card 历史
```

## 八、关键引用

- 主上下文委派铁律: [sub-agent-rules.md §1-§15](../references/sub-agent-rules.md)
- Agent 完成报告模板: [reviewer-templates.md](../references/reviewer-templates.md)
- 视觉验证协议: [reset-and-verify-protocol.md](../references/reset-and-verify-protocol.md)
- 文档分层: [artifact-lifecycle.md](../references/artifact-lifecycle.md)
