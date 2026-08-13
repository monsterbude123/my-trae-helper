# 技能市场三层控制体系

## 快速开始

### 1. 创建新技能

```bash
node bin/cli.mjs create my-new-skill "我的新技能"
```

执行流程: 风险判定 → 前置检查 → 创建 → 结构验证 → 成功提示

### 2. 验证技能

```bash
node bin/cli.mjs verify my-new-skill
```

执行 4 个守卫: 安全 + 结构 + 依赖 + 能力

### 3. 安装技能

```bash
node bin/cli.mjs add my-new-skill -a trae-cn
```

自动执行: 依赖验证 → 冲突检查 → 备份 → 安装 → 审计

## 三层架构

### Execution Layer (执行层)

| 文件 | 功能 |
|------|------|
| [skill-change-control.mjs](./skill-change-control.mjs) | 新建/修改/删除技能 |
| [skill-install-control.mjs](./skill-install-control.mjs) | 安装/卸载技能 |

### Guard Layer (守卫层)

| 文件 | 功能 |
|------|------|
| [../scripts/skill-security-guard.py](../scripts/skill-security-guard.py) | 安全扫描 |
| [../scripts/skill-structure-guard.py](../scripts/skill-structure-guard.py) | 结构检查 |
| [../guards/skill-dependency-guard.mjs](../guards/skill-dependency-guard.mjs) | 依赖检查 |
| [../scripts/skill-capability-guard.py](../scripts/skill-capability-guard.py) | 能力去重 |

### Gate Layer (门禁层)

| 层级 | 触发时机 | 文件 |
|------|---------|------|
| L1 Commit | git commit | [.husky/pre-commit](../../.husky/pre-commit) |
| L2 Push | git push | [.husky/pre-push](../../.husky/pre-push) |
| L3 Merge | PR merge | [.github/workflows/skill-market-gate.yml](../../.github/workflows/skill-market-gate.yml) |
| L4 Publish | Release | [.github/workflows/skill-market-gate.yml](../../.github/workflows/skill-market-gate.yml) |

## 设计文档

- [skill-market-control-design.md](../../skill-markets/fullstack4TraeV11/references/skill-market-control-design.md) — 完整设计
- [skill-market-control-quickref.md](../../skill-markets/fullstack4TraeV11/references/skill-market-control-quickref.md) — 快速参考

## 安全评分

所有新增脚本已通过 `trae-security-review/scan_skills_dir.py` 扫描:

| 脚本 | 风险等级 |
|------|---------|
| src/execution/*.mjs | 🟢 LOW |
| src/guards/*.mjs | 🟢 LOW |
| scripts/skill-security-guard.py | 🟡 MEDIUM (subprocess 业务必需) |
| scripts/skill-structure-guard.py | 🟢 LOW |
| scripts/skill-capability-guard.py | 🟢 LOW |

## 状态

✅ 所有守卫已配置并可用
✅ Git Hooks 已配置 (core.hooksPath=.husky)
✅ CAPABILITY-MAP.md 已同步
✅ SECURITY-MAP.md 已同步
✅ GitHub Actions 已配置