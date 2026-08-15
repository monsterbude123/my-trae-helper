# Node.js Scaffold (V11)

> **V11.7.0+ 脚手架使用须知**:
> - **本目录为参考快照**:V11.7.0 起,初装项目应运行 `python scripts/gate-installer.py --target . --preset nodejs --layers module,app,system` 一键生成 gates/ + .husky/ + hash 锁,不必手抄本目录文件
> - **AC 核销门禁**:Stage 4 Review 走 `scripts/ac-gate.py`,取代 4 维评分
> - **Hash 锁**:每个 gate 文件修改必经贾维斯 `[JARVIS-DELEGATION]` 委派,否则 `--verify` BLOCK

> Node.js + JavaScript/TypeScript 项目脚手架（V11 全栈流程）

## 概述

本脚手架为 Node.js 项目提供符合 V11 协议的初始化结构，包括：

- 🎯 **Gate 映射**：L1 → Stage 1 Spec / L2 → Stage 3.5 Real Verify / L3 → Stage 2·4·4.5 归并 / L4 → Stage 5 Accept
- ⚙️ **四档门禁配置**：`gates/gate-config.json` 声明式定义 L1-L4 档位（单一权威源）
- 🔒 **硬化 husky hooks**：`set -euo pipefail` + 文件存在性检查
- 📚 **AGENTS.md 协议**：项目级规则加载

## 使用方法

### CLI 初始化

```bash
node bin/cli.mjs init-from-zero --scaffold nodejs --project-name my-app
```

### 手动应用

```bash
cp -r skill-markets/fullstack4TraeV11/scaffolds/nodejs/files/* /path/to/project/
chmod +x /path/to/project/.husky/*
```

## 包含文件清单

```
files/
├── .husky/
│   ├── pre-commit       # L1 -> Stage 1 Spec 验证
│   └── pre-push         # L2 -> Stage 3.5 Real Verify
├── gates/
│   └── gate-config.json # L1-L4 四档门禁声明（流程层单一权威源）
├── scripts/
│   └── run-gate-level.py# 按档位消费 gate-config.json 的执行器（CI 用）
├── docs/
│   └── specs/
│       └── .state-card.md   # 状态卡模板
└── AGENTS.md            # 项目级规则
```

### 文件说明

| 文件 | 用途 |
|------|------|
| `.husky/pre-commit` | Stage 1 Spec 验证：lint + typecheck + test:unit |
| `.husky/pre-push` | Stage 3.5 Real Verify：集成测试 + 覆盖率 + 构建 |
| `gates/gate-config.json` | L1-L4 四档门禁声明（checks / gates / timeout / blocking） |
| `scripts/run-gate-level.py` | 读 gate-config.json，按 `--level` 执行该档检查（CI 集成） |
| `docs/specs/.state-card.md` | 状态追踪：current_stage / gate_result |
| `AGENTS.md` | 项目级规则加载协议 |

## 硬化特性

### 1. 严格模式

所有 husky hooks 启用 `set -euo pipefail`，任一命令失败立即退出。

### 2. 文件存在性检查

pre-commit 验证：
- `package.json` 必须存在
- `docs/specs/.state-card.md` 必须存在

pre-push 验证：
- 同上 + Spec 文件计数

### 3. 占位符检测

拒绝以下占位符模式：

```json
{
  "scripts": {
    "lint": "echo \"skipping lint\"",
    "typecheck": "echo \"skip\""
  }
}
```

Gate 会扫描并拒绝这类占位符。

### 4. 真实执行

必须真实调用 `npm run <script>`，禁止静默通过。

### 5. Gate 结果同步

成功通过后自动更新 `.state-card.md`：

```yaml
gate_result: PASS
last_gate_time: 2026-08-14T10:30:00Z
```

## Gate 映射协议

### L1 -> Stage 1 Spec (pre-commit)

**触发**：`git commit`

**验证内容**：

1. Spec 文件完整性（`docs/specs/*.md`）
2. 状态卡 `current_stage = "1-spec"`
3. `lint` + `typecheck` + `test:unit` 真实执行

**通过条件**：

- 所有检查项通过
- 无占位符脚本
- 状态卡已创建

### L2 -> Stage 3.5 Real Verify (pre-push)

**触发**：`git push`

**验证内容**：

1. 代码与 Spec 一致性
2. 状态卡 `current_stage >= "3.5-verify"`
3. `test:integration` + `test:coverage` + `build` 真实执行

**通过条件**：

- 所有测试通过
- 覆盖率达标（如有配置）
- 构建产物生成

### L3 -> Stage 2/4/4.5 归并（GitHub Actions PR merge）

**触发**：`pull_request`（合并前）

**验证内容**（`gates/gate-config.json` 的 L3 档 + `scripts/run-gate-level.py`）：

1. npm scripts：`test:e2e` 真实执行
2. V11 stage 门禁（若项目内嵌 `gates/gates.yaml`）：`stage-contract` / `stage-review` / `stage-rot-scan`，脚本存在则跑，缺失则 SKIP（不阻断）

**通过条件**：

- 所有 checks 通过
- 无占位符脚本
- gate 脚本缺失仅 WARN，不 BLOCK

### L4 -> Stage 5 Accept（GitHub Actions Release）

**触发**：`release` / `push tag v*`

**验证内容**（`gates/gate-config.json` 的 L4 档）：

1. npm scripts：`test:all` + `security-scan` 真实执行
2. V11 stage 门禁（若内嵌）：`stage-accept`

**通过条件**：

- 全量测试通过
- 安全审计无 HIGH 阻断
- 缺失 gate 脚本仅 WARN

## 必需脚本

脚手架要求以下脚本在 `package.json` 中定义：

| 脚本 | 用途 | L1 | L2 |
|------|------|----|----|
| `lint` | 代码风格检查 | ✅ | - |
| `typecheck` | 类型检查 | ✅ | - |
| `test:unit` | 单元测试 | ✅ | - |
| `test:integration` | 集成测试 | - | ✅ |
| `test:coverage` | 覆盖率测试 | - | ✅ |
| `build` | 构建产物 | - | ✅ |

### 示例 package.json

```json
{
  "scripts": {
    "lint": "eslint src/",
    "typecheck": "tsc --noEmit",
    "test:unit": "vitest run tests/unit",
    "test:integration": "vitest run tests/integration",
    "test:coverage": "vitest run --coverage",
    "build": "tsc -p tsconfig.build.json"
  }
}
```

## 状态卡字段

`.state-card.md` 包含以下关键字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `card_type` | string | 固定值 `state-card` |
| `card_id` | string | 唯一标识 `<project>-state` |
| `current_stage` | string | 当前 Stage（1-spec ~ 5-release） |
| `gate_result` | string | 最近 Gate 结果（PENDING / PASS / FAIL） |
| `last_gate_time` | string | ISO 8601 时间戳 |

## 相关文档

- [fullstack4TraeV11 SKILL.md](../SKILL.md) — V11 协议定义
- [scaffolds README](../README.md) — 脚手架总览