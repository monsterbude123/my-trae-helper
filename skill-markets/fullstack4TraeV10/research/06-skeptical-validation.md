---
title: 质疑性校验协议 + 技能优化方法论 + 知识库升级 Mindmap
description: 4 维度 P0/P1 必要性质疑 + 11 铁律 + 6 步流程 + 5 层能力架构
layer: fact
---

# 质疑性校验协议 + 技能优化方法论 + 知识库升级 Mindmap

> V10.12 NEW: **升级前必走质疑性校验** — 防止"看似合理的修复"实际是"矫枉过正"或"重复造轮子"。
> 核心立场: **接受用户/子代理输入前，必须独立校验，不盲信**。

## 一、质疑性校验协议 Mindmap

```mermaid
mindmap
  root((质疑性校验协议<br/>Skeptical Validation))
    触发场景
      升级方案
      P0/P1 缺陷清单
      子代理完成声明
      Agent 决策点
      文档疑似漂移
    不适用
      用户明确按 X 执行
      X 已通过质疑性校验
      纯文本查询
      evidence 已附 file:line
      Read 抽检通过
    §1 P0/P1 4 维度
      1.1 根因验证
        引用章节真实存在
        失效模式有证据
        根因不在更上游
      1.2 责任主体
        改在当前层 vs 上游
        已有 skill 覆盖
        改在错误位置后果
      1.3 重叠校验
        现有规则 grep
        反向提示词覆盖
        差异化论证
      1.4 修复成本
        修复行数
        §11 铁律约束
        替代方案
    §2 通用质疑三层
      2.1 问题层
        真问题还是衍生
        影响面
      2.2 方案层
        业界标准
        复用优先
      2.3 实施层
        实施成本
        风险评估
    §3 强制声明
      升级方案回报前
      含 4 字段
      根因 / 责任 / 重叠 / 成本
    §4 5 反例
      盲信 P0
      责任主体误判
      重叠未检出
      路径漂移盲信
      验收货不对版
```

## 二、4 维度校验流程图

```mermaid
flowchart TD
    Start[接受 P0/P1 主张]
    D1[§1.1 根因验证]
    D2[§1.2 责任主体校验]
    D3[§1.3 与已有规则重叠]
    D4[§1.4 修复成本 vs 价值]

    Start --> D1
    D1 -->|根因真实? + 证据 + 不在上游| D2
    D1 -->|❌ 否| Fix1[修正根因]
    D2 -->|改在正确位置 + 不重复| D3
    D2 -->|❌ 责任主体错| Fix2[重新定位]
    D3 -->|新规则差异化 + 必要补充| D4
    D3 -->|❌ 与已有重叠| Fix3[取消或缩窄]
    D4 -->|成本合理 + 价值高 + 满足 §11| Build[✅ 采纳]
    D4 -->|❌ 成本高 / 价值低 / 替代方案更好| Fix4[取消 / 缩窄 / 替换]

    classDef step fill:#95e1d3,color:#000
    classDef fail fill:#ff6b6b,color:#fff
    classDef pass fill:#4ecdc4,color:#fff
    class Start,D1,D2,D3,D4 step
    class Fix1,Fix2,Fix3,Fix4 fail
    class Build pass
```

## 三、技能优化方法论 11 铁律 + 6 步流程

```mermaid
mindmap
  root((技能优化方法论<br/>skill-optimization-method))
    §0 11 铁律
      1 体积诊断先行
      2 根因分层分析
      3 外部对标必做
      4 方案分级提案
      5 决策点前置
      6 核心价值保底
      7 全量缺口对照
      8 三级缺口分级
      9 最小修复原则
      10 门禁显式化
      11 质疑性校验必走
    §1 6 步流程
      Step 0 质疑性校验
      Step 1 体积诊断
      Step 2 根因分析
      Step 3 外部对标
      Step 4 方案提案
      Step 5 缺口对照 + 修复
    §2 三级缺口
      MUST FIX
        影响核心
        不补不发版
      SHOULD ADD
        提升质量
        可延后
      ACCEPTABLE
        不影响核心
        不补
    §3 反例
      膨胀式吸收经验
      矫枉过正式规则堆砌
      跳过外部对标
```

## 四、外部对标方法论

```mermaid
graph LR
    Step1[Step 1 画出 5 层对照表]
    Step2[Step 2 识别缺失层级 ��]
    Step3[Step 3 按 ROI 排序]

    Step1 --> Step2
    Step2 --> Step3

    Step3 --> Output[输出: 缺失能力 + 优先级]

    classDef step fill:#95e1d3,color:#000
    class Step1,Step2,Step3,Output step
```

## 五、知识库升级 5 层能力架构

```mermaid
graph TB
    L5[L5 验证层<br/>权威度 / 新鲜度 / 漂移检测]
    L4[L4 变更层<br/>detect_changes / impact]
    L3[L3 查询层<br/>query / context / search]
    L2[L2 关系层<br/>链接图谱 / 标签 / 元数据]
    L1[L1 索引层<br/>结构化解析]

    L5 --> L4
    L4 --> L3
    L3 --> L2
    L2 --> L1

    L5 -.->|对标 GitNexus| Goal[业界最佳]
    L4 -.-> Goal
    L3 -.-> Goal
    L2 -.-> Goal
    L1 -.-> Goal

    classDef layer fill:#95e1d3,color:#000
    classDef goal fill:#ffd93d,color:#000
    class L1,L2,L3,L4,L5 layer
    class Goal goal
```

## 六、舍本逐末识别（伪问题 vs 真问题）

```mermaid
mindmap
  root((问题识别))
    伪问题 跳过
      MCP 化
        形式优化
        本质问题未解
      UI 美化
        用户界面
        非召回质量
      性能微调
        毫秒级优化
        非结构性
    真问题 聚焦
      召回质量
        召回率天花板
        误读
      新鲜度
        文档过期
        幻觉
      反幻觉
        盲信文档
        错误答案
    判定方法
      问 解决了什么本质问题
      回答不出 = 跳过
```

## 七、优先级铁律 P0 > P1 > P2

```mermaid
graph TB
    P0[P0 必须做<br/>影响面最大]
    P1[P1 应该做<br/>提升召回质量]
    P2[P2 可选<br/>形式优化]

    P0 --> P1
    P1 --> P2

    P0 -.->|ROI 最高| Most[影响面 + 反幻觉 + 标杆]
    P1 -.->|次高| Some[同义词 + 上下文]
    P2 -.->|可跳过| None[MCP 化 + 边缘场景]

    classDef must fill:#ff6b6b,color:#fff
    classDef should fill:#ffd93d,color:#000
    classDef optional fill:#95e1d3,color:#000
    class P0 must
    class P1 should
    class P2 optional
    class Most,Some,None optional
```

## 八、关键引用

- 质疑性校验协议: [skeptical-validation-protocol.md](../references/skeptical-validation-protocol.md)
- 技能优化方法论: [skill-optimization-method.md](../references/skill-optimization-method.md)
- 知识库升级: [knowledge-system-upgrade.md](../references/knowledge-system-upgrade.md)
- AGENTS.md 引用: [AGENTS.md §项目专属技能](../../../../../AGENTS.md)
- 9