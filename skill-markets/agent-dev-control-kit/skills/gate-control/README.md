# gate-control

> Gate 控制核心技能

## 概述

gate-control 是代码生命周期的分层门禁机制，在 commit/push/merge/release 关键节点自动执行检查，确保代码质量、安全性和可维护性。

## 目录结构

```
gate-control/
├── SKILL.md                    # 核心流程和关键控制点
├── README.md                   # 本说明文档
├── references/                 # 详细实现
│   └── gate-implementation.md
└── templates/                  # Gate 模板
    ├── gate-config-template.json
    ├── pre-commit-template.sh
    └── pre-push-template.sh
```

## 使用方式

1. 加载本 skill
2. 配置门禁规则（检查项、阈值）
3. 安装 git hooks
4. 自动触发检查

## 核心能力

- L1 提交前门禁
- L2 推送前门禁
- L3 合并前门禁
- L4 发布前门禁

## 参考文档

- [gate-implementation.md](references/gate-implementation.md) — 详细实现规范
- [../../../references/gate-skills-guide.md](../../../references/gate-skills-guide.md) — 完整参考指南