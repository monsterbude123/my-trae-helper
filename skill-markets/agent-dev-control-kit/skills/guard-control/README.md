# guard-control

> Guard 控制核心技能

## 概述

guard-control 是 Agent 开发流程中的自动化门禁，在关键节点执行强制性检查，阻止不符合规范的代码/设计进入下一阶段。

## 目录结构

```
guard-control/
├── SKILL.md                    # 核心流程和关键控制点
├── README.md                   # 本说明文档
├── references/                 # 详细实现
│   └── guard-implementation.md
└── templates/                  # Guard 模板
    ├── api-contract-guard-template.yaml
    └── test-coverage-guard-template.yaml
```

## 使用方式

1. 加载本 skill
2. 定义禁止规则和白名单
3. 在关键节点触发检查
4. 处理检查结果

## 核心能力

- API 契约 Guard
- 测试覆盖率 Guard
- 依赖安全 Guard
- 性能预算 Guard

## 参考文档

- [guard-implementation.md](references/guard-implementation.md) — 详细实现规范
- [../../../references/guard-skills-guide.md](../../../references/guard-skills-guide.md) — 完整参考指南