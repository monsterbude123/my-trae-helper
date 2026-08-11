---
title: 5 阶段流水线 + Phase 3.5/4.5 流程图
description: Plan → Spec → Contract → Implement → 真实验证 → Review → Rot Scan 全流程图
layer: fact
---

# 5 阶段流水线 + Phase 3.5/4.5 全流程图

> V10.12 引入 **Phase 3.5 真实验证**（V10.10 NEW）和 **Phase 4.5 腐化扫描**（V10.4 NEW）。
> 铁律: **任一阶段失败 = �� REJECT，必须回退**。

## 一、完整流水线流程图

```mermaid
flowchart TD
    Start([用户提出需求]) --> P0

    P0[Phase 0 Plan<br/>�� 用户确认高风险]
    P1[Phase 1 Spec<br/>�� 用户确认高风险]
    P2[Phase 2 Contract<br/>⚙ 自动低风险]
    P3[Phase 3 Implement<br/>�� 用户确认高风险]
    P35[Phase 3.5 真实验证<br/>�� 5 项必跑]
    P4[Phase 4 Review<br/>⚙ 自动客观判定]
    P45[Phase 4.5 Rot Scan<br/>�� 必跑]
    Accept[Accept 归档]
    Archive[archive/done/<br/>spec-purge.py]

    P0 -->|plan.md + 状态卡| P1
    P1 -->|spec.md + prototypes/| P2
    P2 -->|contracts/ 四件套 + 测试骨架| P3
    P3 -->|代码 + 测试 + 模块文档| P35
    P35 -->|环境 + 迁移 + 测试 + 启动| P4
    P4 -->|四维 + 质疑式验收| P45
    P45 -->|proactive-scan 5 项| Accept
    Accept --> Archive

    P0 -.->|❌ 用户拒绝| Back0[回退 Intake]
    P1 -.->|❌ 用户拒绝| Back1[回退 Plan]
    P3 -.->|❌ 用户拒绝| Back3[回退 Spec]
    P35 -.->|❌ FAIL| Report0[5 字段阻塞报告<br/>Article XV]
    P4 -.->|❌ 4 维非满分| Back31[Round 1-3<br/>Step 2.6 自动循环]
    P45 -.->|❌ FAIL| Back45[修复后重扫]

    classDef block fill:#ff6b6b,color:#fff
    classDef ok fill:#4ecdc4,color:#fff
    classDef back fill:#d3a4ff,color:#000

    class P0,P1,P3,P35,P45,Accept,Back0,Back1,Back3,Report0,Back31,Back45 block
    class P2,P4 ok
    class Back45 back
```

## 二、Phase 3.5 真实验证 5 项硬门禁

```mermaid
mindmap
  root((Phase 3.5<br/>5 项必跑))
    1 环境依赖
      docker compose ps
      postgres / redis Up
      .env 存在
      端口可达
    2 真实验证
      数据库迁移成功
      全量测试 PASS
      tsc --noEmit 0 错误
      开发服务器可启动
    3 启动可见产物 NEW
      Web curl 200 + 截图 ≥5KB
      Tauri dev 存活 + 主窗口截图
      CLI end-to-end ≥10 行
      API 集成测试 + 200
      后端 health + 日志无 ERROR
    4 证据收集
      完整命令日志
      file:line 路径
      evidence_summary
    5 阻塞处理
      5 字段报告
      不可隐藏
      不可跳过
      不可声称完成
```

## 三、Phase 4 Review 评分流程

```mermaid
flowchart LR
    S2[Step -2 拆解验收基准]
    S2a[Step -1 4 工件静态一致性]
    S0[Step 0 硬门禁]
    S05[Step 0.5 索要事实证据]
    S1[Step 1 四维验收]
    S15[Step 1.5 主动证伪]
    S2b[Step 2 功能效果验证]
    S24[Step 2.4 Test Plan Gate]
    S25[Step 2.5 产品侧验收]
    S26[Step 2.6 自动循环]
    S3[Step 3 评分]
    S4[Step 4 DOC SYNC]
    S5[Step 5 知识提取]
    S6[Step 6 归档门禁]
    S7[Step 7 交流判定]

    S2 --> S2a --> S0 --> S05 --> S1 --> S15 --> S2b --> S24 --> S25 --> S26 --> S3 --> S4 --> S5 --> S6 --> S7

    S3 -->|总分 ≥ 4.0| S4
    S3 -->|任何维度 0 分| Reject[�� REJECT]
    S26 -->|Round 1 ❌| Round1[退回 implementer]
    S26 -->|Round 2 ❌| Round2[升级上报用户]
    S26 -->|Round 3+| Round3[rescue hatch<br/>回退 Phase 0]

    classDef step fill:#95e1d3,color:#000
    classDef reject fill:#ff6b6b,color:#fff
    class S2,S2a,S0,S05,S1,S15,S2b,S24,S25,S26,S3,S4,S5,S6,S7 step
    class Reject,Round1,Round2,Round3 reject
```

## 四、四维验收详细评分

```mermaid
graph TB
    subgraph 维度1_代码
        D1[单元测试 全绿]
        D12[Contract 测试 全绿]
        D13[Lint 0 error]
        D14[覆盖率 ≥ 90%]
        D15[无 TODO/FIXME]
        D16[code-hygiene.py 通过]
        D17[理解确认 2 项验证]
    end

    subgraph 维度2_API
        D21[真实端点非 mock]
        D22[接口签名 100%]
        D23[数据模型 100%]
        D24[错误码 100%]
        D25[事件 100%]
    end

    subgraph 维度3_UIUX
        D31[Phase A 视觉一致性]
        D32[Phase B 交互逻辑]
        D33[Phase C UI 细节 6 项]
    end

    subgraph 维度4_边际
        D41[GitNexus impact]
        D42[下游无副作用]
        D43[文档同步]
        D44[扩展点标注]
    end

    D1 --> D12 --> D13 --> D14 --> D15 --> D16 --> D17
    D21 --> D22 --> D23 --> D24 --> D25
    D31 --> D32 --> D33
    D41 --> D42 --> D43 --> D44

    classDef dim fill:#ffd93d,color:#000
    class D1,D12,D13,D14,D15,D16,D17,D21,D22,D23,D24,D25,D31,D32,D33,D41,D42,D43,D44 dim
```

## 五、Phase 4.5 腐化扫描 5 项

```mermaid
graph LR
    Scan[proactive-scan.py<br/>5 项扫描]
    S1[visual-content-check<br/>PIL 解码 + 直方图<br/>腐烂点 9]
    S2[archive-drift<br/>archive 7 天内 mtime<br/>腐烂点 10]
    S3[self-attestation<br/>self_attested 字段<br/>腐烂点 11]
    S4[orphan-test<br/>未引用组件 + 孤儿测试<br/>腐烂点 12]
    S5[dist-hash<br/>binary 内嵌 chunk<br/>腐烂点 13]
    S6[stub-pileup<br/>仅 define.md<br/>腐烂点 17]
    S7[state-card-staleness<br/>mtime > 24h<br/>腐烂点 16]
    S8[self-aggrandizing<br/>self 吹嘘率<br/>腐烂点 15]

    Scan --> S1
    Scan --> S2
    Scan --> S3
    Scan --> S4
    Scan --> S5
    Scan --> S6
    Scan --> S7
    Scan --> S8

    S1 --> Result{PASS / WARN / FAIL}
    S2 --> Result
    S3 --> Result
    S4 --> Result
    S5 --> Result
    S6 --> Result
    S7 --> Result
    S8 --> Result

    Result -->|任一 FAIL| Reject[�� REJECT<br/>NO ROT, NO ACCEPT]
    Result -->|全 PASS| Green[�� Accept]

    classDef fail fill:#ff6b6b,color:#fff
    classDef ok fill:#4ecdc4,color:#fff
    classDef scan fill:#95e1d3,color:#000
    class Reject fail
    class Green ok
    class Scan,S1,S2,S3,S4,S5,S6,S7,S8,Result scan
```

## 六、关键引用

- 流程定义: [SKILL.md §0](../SKILL.md)
- 真实验证清单: [SKILL.md §0.10](../SKILL.md) + [reset-and-verify-protocol.md](../references/reset-and-verify-protocol.md)
- 验收门禁: [acceptance-gates-v10.md](../references/acceptance-gates-v10.md)
- Reviewer 模板: [reviewer-templates.md](../references/reviewer-templates.md)
- 阶段门禁脚本: [phase-gate.py](../scripts/phase-g