---
title: 14 Articles 宪法 Mindmap
description: 全栈流程不可降级的 16 条铁律（V10.4-V10.12 演进），按主题分层
layer: fact
---

# 14 Articles 宪法 Mindmap

> 冲突判定顺序: **Constitution > Spec > Contract > Code > 个人判断**。
> 永不可降级: **Articles I、II、IV、V、VIII、IX、XIV、XV、XVI**（即使修改流程也维持底线）。

## 一、Articles 主题地图

```mermaid
mindmap
  root((14 Articles<br/>V10.12 宪法))
    质量底线 三件套
      I TDD 强制
        无失败测试不写实现
        Bug 修复 e2e 先行
        phase-gate.py 验证
      II 满分硬门禁
        任一非满分 = REJECT
        倒逼 Agent 不妥协
        acceptance-audit.py 4 维
      III 零残留迁移
        无 .bak / .old
        Git 已有历史
        phase-gate.py 验证
    委派纪律 三件套
      IV 委派纪律
        主上下文不直行代码
        上下文有限
        禁止 Edit/Write
      V GitNexus First
        impact 评估
        禁止 grep 降级
        call graph 准确
      VI Ponytail First
        最简实现
        单文件 ≤ 800 行
        函数 ≤ 50 行
    真相源 + 不可变 二件套
      VII 文档优先
        漂移回流
        Spec 即真相
        立即修复
      VIII 归档不可变
        archive 只读
        破坏可追溯性
        禁直接编辑
    即时同步 三件套
      IX TDD 即时
        改实现立即改测试
        atomic PR
        orphan-detector 验证
      X 异会话验证
        self_attested ≠ PASS
        主上下文必抽检
        Read file:line
      XI 视觉真实
        PIL 解码
        直方图 ≥ 50 unique
        4 象限亮度
    反腐化 + 反虚假 五件套
      XII 文档诚实
        INV 必落地
        禁止自评完成
        self-aggrandizing 扫描
      XIII 骨架是债
        仅 define.md = 债
        2 周未推进冻结
        stub-pileup 扫描
      XIV rot-detector 必跑
        Phase 4.5 不可跳
        任何 FAIL = REJECT
        proactive-scan.py
      XV 障碍诚实
        5 字段立即输出
        禁止隐瞒
        禁止声称完成
      XVI 禁止抽象理由
        不说理解偏差
        不说心理障碍
        reason-classifier.py
```

## 二、Articles 演进时间轴

```mermaid
graph LR
    V100[V10.0<br/>基础 8 条]
    V104a[V10.4<br/>+腐化相关 5 条]
    V105[V10.5<br/>+文档诚实 2 条]
    V108[V10.8<br/>+诚实相关 2 条]
    V112[V10.12<br/>+质疑性校验]

    V100 --> V104a
    V104a --> V105
    V105 --> V108
    V108 --> V112

    V100 -.包含.-> I
    V100 -.包含.-> II
    V100 -.包含.-> III
    V100 -.包含.-> IV
    V100 -.包含.-> V
    V100 -.包含.-> VI
    V100 -.包含.-> VII
    V100 -.包含.-> VIII
    V104a -.新增.-> IX
    V104a -.新增.-> X
    V104a -.新增.-> XI
    V104a -.新增.-> XIV
    V105 -.新增.-> XII
    V105 -.新增.-> XIII
    V108 -.新增.-> XV
    V108 -.新增.-> XVI
```

## 三、Article 强制执行点矩阵

```mermaid
graph TB
    subgraph 阶段门禁
        P0[Phase 0 Plan]
        P1[Phase 1 Spec]
        P2[Phase 2 Contract]
        P3[Phase 3 Implement]
        P35[Phase 3.5 真实验证]
        P4[Phase 4 Review]
        P45[Phase 4.5 Rot Scan]
    end

    subgraph Articles 作用点
        I2[Article I<br/>TDD 强制]
        II2[Article II<br/>满分硬门禁]
        III2[Article III<br/>零残留]
        IV2[Article IV<br/>委派纪律]
        V2[Article V<br/>GitNexus First]
        VII2[Article VII<br/>文档优先]
        VIII2[Article VIII<br/>归档不可变]
        IX2[Article IX<br/>TDD 即时]
        X2[Article X<br/>异会话验证]
        XI2[Article XI<br/>视觉真实]
        XII2[Article XII<br/>文档诚实]
        XIII2[Article XIII<br/>骨架是债]
        XIV2[Article XIV<br/>rot-detector]
        XV2[Article XV<br/>障碍诚实]
        XVI2[Article XVI<br/>禁抽象理由]
    end

    P3 --> I2
    P4 --> II2
    P4 --> III2
    P0 --> IV2
    P0 --> V2
    P1 --> VII2
    P0 --> VIII2
    P3 --> IX2
    P4 --> X2
    P4 --> XI2
    P45 --> XII2
    P45 --> XIII2
    P45 --> XIV2
    P35 --> XV2
    P0 --> XVI2

    classDef article fill:#ffd93d,color:#000
    classDef phase fill:#6bcf7f,color:#000
    class P0,P1,P2,P3,P35,P4,P45 phase
    class I2,II2,III2,IV2,V2,VII2,VIII2,IX2,X2,XI2,XII2,XIII2,XIV2,XV2,XVI2 article
```

## 四、关键引用

- 主宪法: [SKILL.md §-1](../SKILL.md)
- 详细解释: [constitution-detail.md](../references/constitution-detail.md)
- 验证脚本: [phase-gate.py](../scripts/phase-gate.py) / [acceptance-audit.py](../scripts/acceptance-audit.py) / [proactive-scan.py](../scripts/proactive-scan.py)
