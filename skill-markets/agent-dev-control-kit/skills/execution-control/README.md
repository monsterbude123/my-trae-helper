# execution-control

> Execution 控制核心技能

## 概述

execution-control 是 Agent 执行过程的控制层方法论，用于规范化高风险操作，提供可审计的执行轨迹，确保跨会话一致性。

## 目录结构

```
execution-control/
├── SKILL.md                    # 核心流程和关键控制点
├── README.md                   # 本说明文档
├── references/                 # 详细实现
│   └── execution-implementation.md
└── templates/                  # Execution 模板
    ├── data-change-template.md
    ├── doc-sync-template.md
    └── config-sync-template.md
```

## 使用方式

1. 加载本 skill
2. 执行操作前进行影响评估
3. 按风险等级执行对应控制点
4. 记录执行轨迹

## 核心能力

- 数据变更控制
- 文档同步控制
- 配置同步控制
- 资产管理控制
- 发布流程控制

## 参考文档

- [execution-implementation.md](references/execution-implementation.md) — 详细实现规范
- [../../../references/execution-skills-guide.md](../../../references/execution-skills-guide.md) — 完整参考指南