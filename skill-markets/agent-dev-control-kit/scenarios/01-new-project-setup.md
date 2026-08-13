# 场景 01：新项目建立控制体系

> 本场景展示如何从零开始为一个新项目建立完整的 Agent 开发控制体系。

---

## 场景描述

**背景**：团队启动了一个新项目，希望从一开始就建立规范化的开发控制体系，确保代码质量和执行过程的可追溯性。

**目标**：
- 建立三层控制体系（Execution、Guard、Gate）
- 配置自动化门禁检查
- 提供团队可复用的控制流程

**预计时间**：1-2 天

---

## 前置条件

### 环境要求

- Node.js ≥ 18
- Git ≥ 2.x
- husky ≥ 8.x（用于 Git Hooks）

### 团队要求

- 至少 1 名熟悉控制体系的负责人
- 团队已了解基本的代码审查流程

### 资源准备

- 已创建 Git 仓库
- 已初始化 package.json

---

## 详细步骤

### Step 1：复制脚手架模板（15 分钟）

#### 1.1 复制模板目录

```bash
cd /path/to/your-project

cp -r skill-markets/agent-dev-control-kit/template-project/.agents .
cp -r skill-markets/agent-dev-control-kit/template-project/gates .
cp -r skill-markets/agent-dev-control-kit/template-project/guards .
cp -r skill-markets/agent-dev-control-kit/template-project/hooks .
cp -r skill-markets/agent-dev-control-kit/template-project/scripts .
```

#### 1.2 目录结构说明

```
your-project/
├── .agents/
│   └── skills/
│       ├── config-sync-control/    # 配置同步控制
│       ├── data-change-control/    # 数据变更控制
│       └── doc-sync-control/       # 文档同步控制
├── gates/
│   ├── gate-config.json            # 门禁配置
│   ├── pre-commit.sh               # 提交前门禁
│   └── pre-push.sh                 # 推送前门禁
├── guards/
│   ├── api-contract-guard.mjs      # API 契约守卫
│   ├── guard-config.json           # 守卫配置
│   └── test-coverage-guard.mjs     # 测试覆盖守卫
├── hooks/
│   ├── hooks-config.json           # Hooks 配置
│   └── install-hooks.sh            # Hooks 安装脚本
└── scripts/
    ├── init-project.sh             # 项目初始化
    ├── run-guards.sh               # 守卫执行
    └── validate-config.sh          # 配置验证
```

---

### Step 2：初始化项目配置（30 分钟）

#### 2.1 运行初始化脚本

```bash
bash scripts/init-project.sh
```

**脚本执行内容**：
- 检查依赖是否安装
- 创建必要的目录结构
- 生成默认配置文件
- 初始化 Git Hooks

#### 2.2 验证配置文件

```bash
bash scripts/validate-config.sh
```

**预期输出**：
```
✓ gate-config.json 格式正确
✓ guard-config.json 格式正确
✓ hooks-config.json 格式正确
✓ 所有 Execution Skills 加载成功
```

---

### Step 3：配置 Execution Skills（1-2 小时）

#### 3.1 数据变更控制配置

编辑 `.agents/skills/data-change-control/SKILL.md`：

```yaml
---
name: data-change-control
description: 数据变更执行控制
version: 1.0.0
triggers:
  - schema_migrate
  - data_import
  - bulk_update
---

## 适用场景

- 数据库 schema 变更
- 批量数据导入/导出
- 数据迁移脚本执行

## 控制点配置

pre_check:
  - impact_assessment
  - backup_required
  
execution:
  - record_timestamp
  - log_operation
  
post_check:
  - verify_result
  - notify_stakeholders
```

#### 3.2 文档同步控制配置

编辑 `.agents/skills/doc-sync-control/SKILL.md`：

```yaml
---
name: doc-sync-control
description: 文档同步执行控制
version: 1.0.0
triggers:
  - api_update
  - spec_change
  - release_note
---

## 适用场景

- API 文档更新
- 规格文档同步
- 发布说明编写

## 控制点配置

pre_check:
  - freshness_score
  
execution:
  - generate_from_code
  - version_tag
  
post_check:
  - notify_team
```

#### 3.3 配置同步控制配置

编辑 `.agents/skills/config-sync-control/SKILL.md`：

```yaml
---
name: config-sync-control
description: 配置同步执行控制
version: 1.0.0
triggers:
  - env_update
  - feature_toggle
  - dependency_upgrade
---

## 适用场景

- 环境变量更新
- 特性开关调整
- 依赖版本升级

## 控制点配置

pre_check:
  - diff_analysis
  
execution:
  - apply_changes
  - validate_syntax
  
post_check:
  - test_integration
  - record_change
```

---

### Step 4：配置 Guard Skills（1 小时）

#### 4.1 编辑守卫配置

编辑 `guards/guard-config.json`：

```json
{
  "guards": [
    {
      "name": "api-contract-guard",
      "enabled": true,
      "severity": "HIGH",
      "checks": [
        "endpoint_schema",
        "version_management",
        "breaking_change"
      ],
      "whitelist": []
    },
    {
      "name": "test-coverage-guard",
      "enabled": true,
      "severity": "HIGH",
      "checks": [
        "line_coverage",
        "branch_coverage",
        "new_code_coverage"
      ],
      "whitelist": [
        {
          "path": "tests/**",
          "reason": "测试文件豁免覆盖率要求"
        }
      ]
    }
  ]
}
```

#### 4.2 添加自定义守卫（可选）

创建 `guards/custom-guard.mjs`：

```javascript
#!/usr/bin/env node

/**
 * 自定义守卫示例：禁止硬编码 IP 地址
 */

const fs = require('fs');
const path = require('path');

const HARDCODED_IP_PATTERN = /\b(?:\d{1,3}\.){3}\d{1,3}\b/g;

function check(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const matches = content.match(HARDCODED_IP_PATTERN);
  
  if (matches) {
    return {
      status: 'BLOCK',
      violations: matches.map(ip => ({
        type: 'hardcoded_ip',
        value: ip,
        message: `发现硬编码 IP: ${ip}`
      }))
    };
  }
  
  return { status: 'PASS' };
}

module.exports = { check };
```

---

### Step 5：配置 Gate Skills（1 小时）

#### 5.1 编辑门禁配置

编辑 `gates/gate-config.json`：

```json
{
  "gates": {
    "pre-commit": {
      "enabled": true,
      "checks": [
        "lint",
        "typecheck",
        "test:unit"
      ],
      "blocking": true,
      "timeout": 300
    },
    "pre-push": {
      "enabled": true,
      "checks": [
        "test:integration",
        "test:coverage",
        "build"
      ],
      "blocking": true,
      "timeout": 600
    }
  }
}
```

#### 5.2 安装 Git Hooks

```bash
bash hooks/install-hooks.sh
```

**预期输出**：
```
✓ husky 已安装
✓ pre-commit hook 已配置
✓ pre-push hook 已配置
✓ hooks 权限已设置
```

---

### Step 6：集成 CI/CD（30 分钟）

#### 6.1 添加 GitHub Actions 配置

创建 `.github/workflows/gate-check.yml`：

```yaml
name: Gate Check

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - run: npm ci
      
      - name: Run Guards
        run: bash scripts/run-guards.sh
      
      - name: Run Tests
        run: npm run test:all
      
      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: gate-reports
          path: reports/
```

#### 6.2 配置分支保护规则

在 GitHub 仓库设置中：

1. 进入 Settings → Branches → Branch protection rules
2. 为 `main` 分支添加规则：
   - Require PR before merging
   - Require status checks to pass
   - Require conversation resolution

---

### Step 7：验证完整流程（30 分钟）

#### 7.1 本地验证

```bash
# 运行所有门禁检查
bash scripts/run-guards.sh

# 运行测试
npm run test:all

# 本地提交测试
git add .
git commit -m "test: verify gate setup"
```

#### 7.2 预期结果

```
[L1 Commit Gate]
  ✓ lint: passed (2s)
  ✓ typecheck: passed (3s)
  ✓ test:unit: passed (5s)

[Guards]
  ✓ api-contract-guard: PASS
  ✓ test-coverage-guard: PASS

[Result] ✓ PASSED - All checks passed
```

---

## 预期结果

### 成功标准

- [ ] 目录结构完整（.agents/、gates/、guards/、hooks/、scripts/）
- [ ] 配置文件格式正确（通过 validate-config.sh）
- [ ] Git Hooks 正常触发（提交和推送时）
- [ ] Guard 检查可执行（至少 2 个守卫）
- [ ] Gate 流程可执行（至少 L1 门禁）
- [ ] CI/CD 集成成功（PR 检查通过）

### 产出物清单

```yaml
新项目控制体系产物:
  目录:
    - .agents/skills/ (3+ Execution Skills)
    - gates/ (门禁配置)
    - guards/ (守卫脚本)
    - hooks/ (Git Hooks)
    - scripts/ (辅助脚本)
  
  配置:
    - gate-config.json
    - guard-config.json
    - hooks-config.json
  
  CI/CD:
    - .github/workflows/gate-check.yml
  
  文档:
    - README.md (控制体系说明)
```

---

## 常见问题

### Q1：husky 安装失败？

**原因**：husky 版本不兼容或 Git 未正确配置。

**解决方案**：
```bash
# 重新安装 husky
npm install husky --save-dev

# 确保 Git 已初始化
git init

# 手动安装 hooks
npx husky install
npx husky add .husky/pre-commit "npm run gate:commit"
```

### Q2：门禁检查超时？

**原因**：检查项过多或测试执行过慢。

**解决方案**：
1. 调整 `gate-config.json` 中的 timeout 值
2. 拆分检查项，采用并行执行
3. 优化测试执行效率

### Q3：Guard 检查误报？

**原因**：规则过于严格或白名单未配置。

**解决方案**：
1. 在 `guard-config.json` 中添加 whitelist
2. 调整检查规则的 severity
3. 提交规则优化 PR 到 agent-dev-control-kit

### Q4：CI 环境与本地结果不一致？

**原因**：环境差异（Node 版本、依赖版本）。

**解决方案**：
1. 使用 `.nvmrc` 锁定 Node 版本
2. 使用 `package-lock.json` 锁定依赖版本
3. 使用 Docker 统一环境

### Q5：如何跳过门禁（紧急情况）？

**警告**：仅在紧急情况下使用，需事后补充修复。

```bash
# 跳过 pre-commit
git commit --no-verify -m "emergency: critical fix"

# 跳过 pre-push
git push --no-verify
```

**要求**：在 PR 中说明跳过原因，并补充后续修复计划。

---

## 后续步骤

1. **团队培训**：组织团队学习控制体系使用方法
2. **规则优化**：根据实际使用情况调整门禁规则
3. **度量监控**：建立门禁通过率、覆盖率等指标的监控看板
4. **持续改进**：定期复盘控制体系的有效性

---

## 相关资源

- [Execution Skills 指南](../references/execution-skills-guide.md)
- [Guard Skills 指南](../references/guard-skills-guide.md)
- [Gate Skills 指南](../references/gate-skills-guide.md)
- [实施路线图](../references/implementation-roadmap.md)

---

> **维护者**：agent-dev-control-kit
> **最后更新**：2025-08-13
> **版本**：1.0.0