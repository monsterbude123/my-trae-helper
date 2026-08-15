# Python Scaffold (V11)

> **V11.7.0+ 脚手架使用须知**:
> - **本目录为参考快照**:V11.7.0 起,初装项目应运行 `python scripts/gate-installer.py --target . --preset python --layers module,app,system` 一键生成 gates/ + .husky/ + hash 锁,不必手抄本目录文件
> - **AC 核销门禁**:Stage 4 Review 走 `scripts/ac-gate.py`,取代 4 维评分
> - **Hash 锁**:每个 gate 文件修改必经贾维斯 `[JARVIS-DELEGATION]` 委派,否则 `--verify` BLOCK

> Python 项目脚手架（V11 全栈流程，支持 FastAPI/Django/Flask）

## 概述

本脚手架为 Python 项目提供符合 V11 协议的初始化结构，包括：

- 🎯 **Gate 映射**：L1 → Stage 1 Spec / L2 → Stage 3.5 Real Verify
- 🔒 **硬化 husky hooks**：`set -euo pipefail` + 工具存在性检查
- 📋 **状态卡模板**：自动追踪 Stage 进展
- 📚 **AGENTS.md 协议**：项目级规则加载

## 使用方法

### CLI 初始化

```bash
node bin/cli.mjs init-from-zero --scaffold python --project-name my-api
```

### 手动应用

```bash
cp -r skill-markets/fullstack4TraeV11/scaffolds/python/files/* /path/to/project/
chmod +x /path/to/project/.husky/*
```

## 包含文件清单

```
files/
├── .husky/
│   ├── pre-commit       # L1 -> Stage 1 Spec 验证
│   └── pre-push         # L2 -> Stage 3.5 Real Verify
├── docs/
│   └── specs/
│       └── .state-card.md   # 状态卡模板
└── AGENTS.md            # 项目级规则
```

### 文件说明

| 文件 | 用途 |
|------|------|
| `.husky/pre-commit` | Stage 1 Spec 验证：ruff + mypy + pytest |
| `.husky/pre-push` | Stage 3.5 Real Verify：pytest + 覆盖率 + 构建 |
| `docs/specs/.state-card.md` | 状态追踪：current_stage / gate_result |
| `AGENTS.md` | 项目级规则加载协议 |

## 硬化特性

### 1. 严格模式

所有 husky hooks 启用 `set -euo pipefail`，任一命令失败立即退出。

### 2. 工具存在性检查

pre-commit 验证：
- `ruff` 已安装
- `mypy` 已安装
- `pytest` 已安装
- `pyproject.toml` 存在
- `docs/specs/.state-card.md` 存在

pre-push 验证：
- `pytest` 已安装
- `pyproject.toml` 存在
- Spec 文件计数

### 3. 占位符检测

扫描 `pyproject.toml` 中的可疑跳过标记：

```toml
[tool.ruff]
skip = true  # ⚠️ 被检测到
```

### 4. 真实执行

必须真实调用工具命令：

```bash
ruff check .
mypy src/
pytest tests/unit -v
```

禁止静默通过或 `echo "skip"`。

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
3. `ruff check .` + `mypy src/` + `pytest tests/unit` 真实执行

**通过条件**：

- 所有检查项通过
- 工具已安装
- 状态卡已创建

### L2 -> Stage 3.5 Real Verify (pre-push)

**触发**：`git push`

**验证内容**：

1. 代码与 Spec 一致性
2. 状态卡 `current_stage >= "3.5-verify"`
3. `pytest` + `pytest --cov` + `python -m build` 真实执行

**通过条件**：

- 所有测试通过
- 覆盖率达标（如有配置）
- 构建产物生成

## 必需工具与文件

脚手架要求以下工具已安装：

| 工具 | 用途 | L1 | L2 |
|------|------|----|----|
| `ruff` | Lint + Format | ✅ | - |
| `mypy` | 类型检查 | ✅ | - |
| `pytest` | 测试框架 | ✅ | ✅ |
| `build` | 构建工具 | - | ✅ |

### 安装命令

```bash
pip install -e '.[dev]'
pip install ruff mypy pytest pytest-cov build
```

### 示例 pyproject.toml

```toml
[project]
name = "my-api"
version = "0.1.0"

[project.optional-dependencies]
dev = ["ruff", "mypy", "pytest", "pytest-cov", "build"]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.mypy]
python_version = "3.10"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
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

## 支持的框架

本脚手架适用于以下 Python 框架：

- **FastAPI**：现代异步 API 框架
- **Django**：全功能 Web 框架
- **Flask**：轻量级 Web 框架
- **CLI Tools**：命令行工具

## 相关文档

- [fullstack4TraeV11 SKILL.md](../SKILL.md) — V11 协议定义
- [scaffolds README](../README.md) — 脚手架总览