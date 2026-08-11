---
title: 腐化防御体系 + 5 项扫描 + 7 大分类 Mindmap
description: rot 7 大分类、19 个腐烂点、5 项腐化扫描、修复原则、反腐烂
layer: fact
---

# 腐化防御体系 + 5 项扫描 + 7 大分类 Mindmap

> **腐烂(Rot)** = 软件/流程/AI 代理在长期运行中**因被动的无序增长(熵增)而逐渐丧失可验证性、可维护性、可信度**的缓慢退化。
> **与 Bug / 技术债的关键区别**: 腐烂是被动积累，常被遗忘，需专门工具检测。
> **铁律**: **NO ROT, NO ACCEPT**（任一 FAIL = �� REJECT）

## 一、腐烂 5 大共性特征

```mermaid
mindmap
  root((Rot 5 大共性))
    渐进性
      缓慢积累
      非突然出现
      时间序列分析
    累积性
      多小问题叠加
      大问题爆发
      N 个 WARN 转 FAIL
    自强化
      破窗效应
      一处腐烂引发更多
      区域聚集
    可检测但需工具
      主观判断漏
      需机械脚本
      rot-detector
    可逆但需主动
      修复成本指数
      放任致命
      主动治理
```

## 二、腐烂 7 大分类

```mermaid
mindmap
  root((7 大腐烂分类))
    1 代码腐烂
      rot #3
      orphan-detector
    2 流程腐烂
      rot #4 #7 #8 #11 #14
      rot-detector 主上下文门禁
    3 文档腐烂
      rot #1 #2 #4 #6 #10
      proactive-scan
      archive-drift
    4 测试腐烂
      rot #5 #12
      proactive-scan
      orphan-tests
    5 视觉腐烂
      rot #9
      proactive-scan
      visual-freshness
    6 构建腐烂
      rot #13
      proactive-scan
      bundle-staleness
    7 代理腐烂
      rot #11 #14
      rot-detector
      注入协议
      Article X
```

## 三、19 个腐烂点全景（V10.8 整理）

```mermaid
graph TB
    subgraph 已解决
        R1[rot #1 _invalidated 盲区<br/>RESOLVED]
        R2[rot #2 change-status 盲区<br/>RESOLVED]
        R3[rot #3 代码残留<br/>RESOLVED]
        R6[rot #6 _invalidated 嵌套膨胀<br/>RESOLVED]
    end

    subgraph 活跃
        R4[rot #4 契约残留<br/>MEDIUM]
        R5[rot #5 孤儿测试文件<br/>LOW]
        R7[rot #7 外部结构冲突<br/>HIGH]
        R8[rot #8 spec-purge 未执行<br/>LOW]
    end

    subgraph V10.4新增
        R9[rot #9 视觉验证假阳性<br/>P0]
        R10[rot #10 Archive 修改无回溯<br/>P0]
        R11[rot #11 自验自签<br/>P0]
        R12[rot #12 过期测试/孤儿组件<br/>P0]
        R13[rot #13 隐式 build 假设<br/>P1]
        R14[rot #14 Agent 不主动诊断<br/>P1]
    end

    subgraph V10.5新增
        R15[rot #15 自我吹嘘<br/>P0]
        R16[rot #16 状态卡陈旧<br/>P1]
        R17[rot #17 骨架堆积<br/>P1]
    end

    subgraph V10.8新增
        R18[rot #18 障碍隐瞒 = 虚假交付<br/>P0]
        R19[rot #19 抽象理由 = 不可证伪<br/>P0]
    end

    classDef resolved fill:#95e1d3,color:#000
    classDef active fill:#4ecdc4,color:#fff
    classDef v104 fill:#ffd93d,color:#000
    classDef v105 fill:#6bcf7f,color:#000
    classDef v108 fill:#ff6b6b,color:#fff
    class R1,R2,R3,R6 resolved
    class R4,R5,R7,R8 active
    class R9,R10,R11,R12,R13,R14 v104
    class R15,R16,R17 v105
    class R18,R19 v108
```

## 四、Phase 4.5 腐化扫描 5 项（当前 V10.12）

```mermaid
flowchart TB
    Scan[proactive-scan.py]

    Scan --> S1[scan-1 visual-freshness<br/>腐烂点 9<br/>PIL 解码 + 直方图 + 4 象限]
    Scan --> S2[scan-2 archive-drift<br/>腐烂点 10<br/>archive mtime 7 天]
    Scan --> S3[scan-3 self-attestation<br/>腐烂点 11<br/>self_attested 字段]
    Scan --> S4[scan-4 orphan-test<br/>腐烂点 12<br/>未引用组件 + 孤儿测试]
    Scan --> S5[scan-5 bundle-staleness<br/>腐烂点 13<br/>binary 内嵌 chunk]

    Scan -.V10.12.-> S6[scan-6 self-aggrandizing<br/>腐烂点 15<br/>self 吹嘘率 > 0.3]
    Scan -.V10.12.-> S7[scan-7 state-card-staleness<br/>腐烂点 16<br/>mtime > 24h]
    Scan -.V10.12.-> S8[scan-8 stub-pileup<br/>腐烂点 17<br/>仅 define.md]

    S1 --> Result{PASS / WARN / FAIL}
    S2 --> Result
    S3 --> Result
    S4 --> Result
    S5 --> Result
    S6 --> Result
    S7 --> Result
    S8 --> Result

    Result -->|任一 FAIL| Reject[�� REJECT<br/>NO ROT, NO ACCEPT]
    Result -->|全 PASS/WARN| Green[�� Accept]

    classDef fail fill:#ff6b6b,color:#fff
    classDef pass fill:#4ecdc4,color:#fff
    classDef scan fill:#95e1d3,color:#000
    class Scan,S1,S2,S3,S4,S5,S6,S7,S8,Result scan
    class Reject fail
    class Green pass
```

## 五、腐烂修复 6 原则

```mermaid
mindmap
  root((腐烂修复 6 原则))
    1 早发现
      主动扫描
      不靠用户问
      Article XIV
    2 早修复
      单个腐烂点立即修
      不等堆积
      破窗效应
    3 机械验证
      脚本检测
      不靠主观
      proactive-scan
    4 阻断流程
      NO ROT, NO ACCEPT
      任一 FAIL = REJECT
      不可手工放过
    5 元检测
      检测器也要被检测
      Phase 4.5.1 self-diagnose
      self-diagnose.py
    6 知识沉淀
      新腐烂点 15+ 写入
      process-rot-analysis.md
      rot-reinforcer 维护
```

## 六、反虚假交付协议（rot #18/#19）

```mermaid
flowchart LR
    Trigger[用户反馈质疑 /<br/>完成声明时]

    Trigger --> X1[Article XV 障碍诚实]
    Trigger --> X2[Article XVI 禁止抽象理由]

    X1 --> Output1[5 字段阻塞报告<br/>类型 / 描述 / 方案 / 耗时 / 尝试次数]
    X1 -.->|必含| M1[完整命令日志<br/>不是 PASS/FAIL 字符串]
    X1 -.->|禁止| F1[隐瞒 / 跳过 / 声称完成]

    X2 --> Output2[我错了 + 具体未执行规则 + 补救]
    X2 -.->|必含| M2[不抽象 / 不可证伪]
    X2 -.->|禁止| F2[理解偏差 / 心理障碍 / 流程裁剪 / 概念漂移 / 上下文丢失 / 权衡取舍]
    X2 -.->|检测| M3[reason-classifier.py<br/>6 类抽象理由]

    classDef reason fill:#ffd93d,color:#000
    classDef forbid fill:#ff6b6b,color:#fff
    classDef must fill:#4ecdc4,color:#fff
    class X1,X2,Output1,Output2 reason
    class M1,M2,M3 must
    class F1,F2 forbid
```

## 七、关键引用

- 腐烂定义与分类: [process-rot-analysis.md §0](../references/process-rot-analysis.md)
- 19 个腐烂点详情: [process-rot-analysis.md §1-§5](../references/process-rot-analysis