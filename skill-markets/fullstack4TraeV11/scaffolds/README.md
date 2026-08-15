# fullstack4TraeV11 Scaffolds

> V11 全栈文档驱动开发脚手架模板集

## 概述

本目录提供 `fullstack4TraeV11` 的项目脚手架模板，用于快速初始化符合 V11 协议的项目结构。

**核心特性**：

- 🎯 **Gate 映射**：L1 → Stage 1 Spec / L2 → Stage 3.5 Real Verify
- 🔒 **硬化逻辑**：`set -euo pipefail` + 文件存在性检查 + 真实执行
- 📋 **状态卡模板**：内置 `.state-card.md` 模板，支持 Stage 追踪
- 📚 **AGENTS.md 协议**：自动注入项目级规则加载协议

## 可用脚手架

| ID | 名称 | 技术栈 | Gate 映射 |
|----|------|--------|----------|
| `nodejs` | Node.js | JavaScript/TypeScript | L1 → Stage 1 / L2 → Stage 3.5 |
| `python` | Python | Python 3.10+ | L1 → Stage 1 / L2 → Stage 3.5 |

## 使用方法

### 通过 CLI 初始化

```bash
node bin/cli.mjs init-from-zero --scaffold nodejs --project-name my-app
node bin/cli.mjs init-from-zero --scaffold python --project-name my-api
```

### 手动应用

```bash
cp -r skill-markets/fullstack4TraeV11/scaffolds/nodejs/files/* /path/to/project/
chmod +x /path/to/project/.husky/*
```

## 目录结构

```
scaffolds/
├── README.md                    (本文件)
├── nodejs/                      (Node.js 脚手架)
│   ├── scaffold.yaml
│   ├── README.md
│   └── files/
│       ├── .husky/
│       │   ├── pre-commit       (Stage 1 Spec 验证)
│       │   └── pre-push         (Stage 3.5 Real Verify)
│       ├── docs/
│       │   └── specs/
│       │       └── .state-card.md
│       └── AGENTS.md
└── python/                      (Python 脚手架)
    ├── scaffold.yaml
    ├── README.md
    └── files/
        ├── .husky/
        │   ├── pre-commit
        │   └── pre-push
        ├── docs/
        │   └── specs/
        │       └── .state-card.md
        └── AGENTS.md
```

## Gate 映射协议

### L1 → Stage 1 Spec (pre-commit)

- **触发时机**：`git commit`
- **验证内容**：
  - Spec 文档完整性（docs/specs/*.md）
  - 状态卡 current_stage = "1-spec"
  - 基础 lint + typecheck

### L2 → Stage 3.5 Real Verify (pre-push)

- **触发时机**：`git push`
- **验证内容**：
  - 代码与 Spec 一致性
  - 状态卡 current_stage = "3.5-verify"
  - 全量测试 + 覆盖率
  - 构建产物验证

## 硬化特性

所有 husky hooks 内置以下硬化逻辑：

1. **`set -euo pipefail`**：严格模式，任一失败立即退出
2. **文件存在性检查**：验证 `package.json` / `pyproject.toml` 存在
3. **占位符检测**：拒绝 `echo "skip"` 类占位脚本
4. **真实执行**：必须调用真实命令，禁止静默通过
5. **Gate 结果同步**：自动更新 `.state-card.md` 的 `gate_result`

## 与 agent-dev-control-kit 的区别

| 特性 | fullstack4TraeV11 | agent-dev-control-kit |
|------|-------------------|-----------------------|
| Gate 映射 | Stage-based (V11) | Level-based (L1-L4) |
| 状态卡 | ✅ `.state-card.md` | ❌ 无 |
| AGENTS.md | ✅ 项目级规则注入 | ❌ 无 |
| Guards | 简化（仅 Gate） | 完整 Guard 层 |

## 扩展指南

### 添加新脚手架

1. 创建 `scaffolds/<new-stack>/` 目录
2. 编写 `scaffold.yaml`（定义 `scaffold_id` / `required_scripts` / `gate_mapping`）
3. 编写 husky hooks（参考 nodejs/python 的硬化模式）
4. 编写 `.state-card.md` 模板
5. 编写脚手架 README.md
6. 更新本文件的"可用脚手架"表格

## 相关文档

- [fullstack4TraeV11 SKILL.md](../SKILL.md) — V11 协议完整定义
- [agent-dev-control-kit scaffolds](../../agent-dev-control-kit/scaffolds/README.md) — 参考