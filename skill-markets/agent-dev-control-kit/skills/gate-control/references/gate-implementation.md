# Gate 控制实现规范

## §1 L1 提交前门禁

### 1.1 触发时机

`git commit`（通过 husky pre-commit hook）

### 1.2 检查项

| 检查项 | 命令 | 通过标准 | 失败处理 |
|--------|------|---------|---------|
| Lint | `npm run lint` | 零错误 | 阻断提交 |
| TypeCheck | `npm run typecheck` | 零错误 | 阻断提交 |
| 单元测试 | `npm run test:unit` | 零失败 | 阻断提交 |
| 格式化 | `npm run format:check` | 符合规范 | 自动修复或阻断 |

### 1.3 配置示例

```json
{
  "scripts": {
    "lint": "eslint . --ext .ts,.tsx",
    "typecheck": "tsc --noEmit",
    "test:unit": "jest --coverage=false",
    "format:check": "prettier --check ."
  }
}
```

### 1.4 husky 配置

```bash
npx husky add .husky/pre-commit "npm run lint && npm run typecheck && npm run test:unit"
```

## §2 L2 推送前门禁

### 2.1 触发时机

`git push`（通过 husky pre-push hook）

### 2.2 检查项

| 检查项 | 命令 | 通过标准 | 失败处理 |
|--------|------|---------|---------|
| L1 全部检查 | — | L1 通过 | 阻断推送 |
| 集成测试 | `npm run test:integration` | 零失败 | 阻断推送 |
| 覆盖率检查 | `npm run test:coverage` | ≥ 阈值（默认 80%） | 警告或阻断 |
| 构建检查 | `npm run build` | 成功 | 阻断推送 |

### 2.3 配置示例

```json
{
  "scripts": {
    "test:integration": "jest --testPathPattern=integration",
    "test:coverage": "jest --coverage --coverageThreshold='{\"global\":{\"branches\":80,\"functions\":80,\"lines\":80}}'",
    "build": "tsc && vite build"
  }
}
```

### 2.4 husky 配置

```bash
npx husky add .husky/pre-push "npm run test:integration && npm run build"
```

## §3 L3 合并前门禁

### 3.1 触发时机

PR merge（通过 CI workflow）

### 3.2 检查项

| 检查项 | 执行方式 | 通过标准 | 失败处理 |
|--------|---------|---------|---------|
| L2 全部检查 | CI | L2 通过 | 阻断合并 |
| 代码审查 | 人工/自动 | 审批通过 | 阻断合并 |
| E2E 测试 | CI | 全绿 | 阻断合并 |
| 兼容性检查 | CI | 通过 | 警告 |

### 3.3 GitHub Actions 配置

```yaml
name: Merge Gate

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  gate-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install
        run: npm ci
      
      - name: L2 Checks
        run: |
          npm run lint
          npm run typecheck
          npm run test:unit
          npm run test:integration
          npm run build
      
      - name: E2E Tests
        run: npm run test:e2e
      
      - name: Coverage
        run: npm run test:coverage
```

## §4 L4 发布前门禁

### 4.1 触发时机

Release（通过 CI workflow）

### 4.2 检查项

| 检查项 | 执行方式 | 通过标准 | 失败处理 |
|--------|---------|---------|---------|
| 全量测试 | CI | 全绿 | 阻断发布 |
| 性能基准 | CI | 达标 | 阻断发布 |
| 安全扫描 | CI | 无漏洞 | 阻断发布 |
| 验收测试 | 人工 | 通过 | 阻断发布 |

### 4.3 配置示例

```yaml
name: Release Gate

on:
  release:
    types: [created]

jobs:
  gate-check:
    runs-on: ubuntu-latest
    steps:
      - name: Full Test Suite
        run: npm run test:all
      
      - name: Performance Benchmark
        run: npm run benchmark
      
      - name: Security Scan
        run: npm audit
      
      - name: Acceptance Test
        run: npm run test:acceptance
```

## §5 门禁配置文件

### 5.1 gate-config.json

```json
{
  "version": "1.0",
  "gates": {
    "commit": {
      "enabled": true,
      "checks": ["lint", "typecheck", "test:unit"],
      "timeout": 300
    },
    "push": {
      "enabled": true,
      "checks": ["test:integration", "test:coverage", "build"],
      "timeout": 600
    },
    "merge": {
      "enabled": true,
      "checks": ["test:e2e", "code-review"],
      "timeout": 1800
    },
    "release": {
      "enabled": true,
      "checks": ["test:all", "benchmark", "security-scan"],
      "timeout": 3600
    }
  },
  "whitelist": {
    "branches": ["main", "release/*"],
    "paths": ["docs/**", "*.md"]
  }
}
```