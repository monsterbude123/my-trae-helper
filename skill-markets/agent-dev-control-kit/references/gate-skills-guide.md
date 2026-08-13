# Gate Skills Guide — 门禁机制详细指南

## 概述

Gate Skills 是一套分层门禁机制，在代码生命周期的关键节点自动执行检查，确保代码质量、安全性和可维护性。

## §1 四层门禁机制

### 1.1 门禁层级总览

```
┌─────────────────────────────────────────────────────────────┐
│ L4 发布前门禁 (Release Gate)                                │
│ ├─ 全量测试 + 性能基准 + 安全扫描 + 验收测试                  │
│ └─ 通过标准：全部通过 + 性能达标 + 无安全漏洞                 │
├─────────────────────────────────────────────────────────────┤
│ L3 合并前门禁 (Merge Gate)                                  │
│ ├─ L2 检查 + 代码审查 + E2E 测试                             │
│ └─ 通过标准：审批通过 + E2E 全绿                             │
├─────────────────────────────────────────────────────────────┤
│ L2 推送前门禁 (Push Gate)                                   │
│ ├─ L1 检查 + 集成测试 + 覆盖率检查                           │
│ └─ 通过标准：零失败 + 覆盖率 ≥ 阈值                          │
├─────────────────────────────────────────────────────────────┤
│ L1 提交前门禁 (Commit Gate)                                 │
│ ├─ Lint + TypeCheck + 单元测试                               │
│ └─ 通过标准：零错误 + 零失败                                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 L1 提交前门禁（Commit Gate）

**触发时机**：`git commit`（通过 husky pre-commit hook）

**检查项**：

| 检查项 | 命令 | 通过标准 | 失败处理 |
|--------|------|---------|---------|
| Lint | `npm run lint` | 零错误 | 阻断提交 |
| TypeCheck | `npm run typecheck` | 零错误 | 阻断提交 |
| 单元测试 | `npm run test:unit` | 零失败 | 阻断提交 |
| 格式化 | `npm run format:check` | 符合规范 | 自动修复或阻断 |

**配置示例**：

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

**husky 配置**：

```bash
npx husky add .husky/pre-commit "npm run lint && npm run typecheck && npm run test:unit"
```

### 1.3 L2 推送前门禁（Push Gate）

**触发时机**：`git push`（通过 husky pre-push hook）

**检查项**：

| 检查项 | 命令 | 通过标准 | 失败处理 |
|--------|------|---------|---------|
| L1 全部检查 | — | L1 通过 | 阻断推送 |
| 集成测试 | `npm run test:integration` | 零失败 | 阻断推送 |
| 覆盖率检查 | `npm run test:coverage` | ≥ 阈值（默认 80%） | 警告或阻断 |
| 构建检查 | `npm run build` | 成功 | 阻断推送 |

**配置示例**：

```json
{
  "scripts": {
    "test:integration": "jest --testPathPattern=integration",
    "test:coverage": "jest --coverage --coverageThreshold='{\"global\":{\"branches\":80,\"functions\":80,\"lines\":80}}'",
    "build": "tsc && vite build"
  }
}
```

**husky 配置**：

```bash
npx husky add .husky/pre-push "npm run test:integration && npm run build"
```

### 1.4 L3 合并前门禁（Merge Gate）

**触发时机**：PR merge（通过 CI workflow）

**检查项**：

| 检查项 | 执行方式 | 通过标准 | 失败处理 |
|--------|---------|---------|---------|
| L2 全部检查 | CI 自动 | L2 通过 | 阻断合并 |
| 代码审查 | 人工审批 | ≥ 1 审批通过 | 阻断合并 |
| E2E 测试 | CI 自动 | 零失败 | 阻断合并 |
| 冲突检查 | CI 自动 | 无冲突 | 阻断合并 |

**GitHub Actions 配置**：

```yaml
name: Merge Gate
on:
  pull_request:
    types: [opened, synchronize, reopened]

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
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run test:unit
      - run: npm run test:integration
      - run: npm run test:e2e
      - run: npm run build
```

**分支保护规则**：

- Require PR before merging
- Require status checks to pass
- Require branch to be up to date
- Require conversation resolution

### 1.5 L4 发布前门禁（Release Gate）

**触发时机**：Release / Deploy（通过 release workflow）

**检查项**：

| 检查项 | 执行方式 | 通过标准 | 失败处理 |
|--------|---------|---------|---------|
| L3 全部检查 | CI 自动 | L3 通过 | 阻断发布 |
| 性能基准 | CI 自动 | 无性能退化 | 阻断发布 |
| 安全扫描 | CI 自动 | 无高危漏洞 | 阻断发布 |
| 验收测试 | CI 自动 | 全量通过 | 阻断发布 |
| 变更日志 | CI 自动 | CHANGELOG 已更新 | 警告或阻断 |
| 版本号检查 | CI 自动 | 符合语义化版本 | 阻断发布 |

**配置示例**：

```yaml
name: Release Gate
on:
  release:
    types: [published]

jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run test:all
      - run: npm run security:audit
      - run: npm run benchmark
      - run: npm run test:acceptance
```

## §2 通过标准详解

### 2.1 零错误标准

- **Lint**：零 error（warning 可配置是否阻断）
- **TypeCheck**：零 error
- **测试**：零 failure（skip 不计入）

### 2.2 覆盖率标准

```json
{
  "coverageThreshold": {
    "global": {
      "branches": 80,
      "functions": 80,
      "lines": 80,
      "statements": 80
    }
  }
}
```

**分级标准**：

| 级别 | 覆盖率要求 | 适用场景 |
|------|-----------|---------|
| 严格 | ≥ 90% | 核心业务逻辑 |
| 标准 | ≥ 80% | 常规模块 |
| 宽松 | ≥ 60% | 工具类 / 配置类 |

### 2.3 性能基准标准

```yaml
performance:
  thresholds:
    build_time: 120s      # 构建时间上限
    bundle_size: 500KB    # 包体积上限
    first_load: 3s        # 首屏加载上限
    api_response: 200ms   # API 响应上限
```

### 2.4 安全扫描标准

```yaml
security:
  block_on:
    - CRITICAL
    - HIGH
  warn_on:
    - MEDIUM
  ignore:
    - LOW  # 仅提示，不阻断
```

## §3 多级门禁设计模式

### 3.1 链式门禁模式

**特点**：检查项按顺序执行，任一失败立即终止

```
检查 A → 检查 B → 检查 C → 检查 D
   ↓ 失败    ↓ 失败    ↓ 失败    ↓ 成功
   阻断      阻断      阻断      通过
```

**配置**：

```yaml
gate:
  mode: chain
  checks:
    - name: lint
      command: npm run lint
      blocking: true
    - name: typecheck
      command: npm run typecheck
      blocking: true
    - name: test
      command: npm run test
      blocking: true
```

### 3.2 并行门禁模式

**特点**：多个检查并行执行，全部通过才算通过

```
┌─ 检查 A ─┐
├─ 检查 B ─┼─ 汇总 → 通过/失败
└─ 检查 C ─┘
```

**配置**：

```yaml
gate:
  mode: parallel
  checks:
    - name: lint
      command: npm run lint
    - name: typecheck
      command: npm run typecheck
    - name: test
      command: npm run test
```

### 3.3 分组门禁模式

**特点**：检查项分组，组内并行，组间串行

```
┌─ 静态检查 ─┐   ┌─ 测试检查 ─┐   ┌─ 构建检查 ─┐
│ lint       │ → │ unit       │ → │ build      │
│ typecheck  │   │ coverage   │   │ bundle     │
└────────────┘   └────────────┘   └────────────┘
```

**配置**：

```yaml
gate:
  mode: grouped
  groups:
    - name: static
      parallel: true
      checks:
        - lint
        - typecheck
    - name: test
      parallel: true
      checks:
        - test:unit
        - test:coverage
    - name: build
      parallel: true
      checks:
        - build
        - bundle:check
```

### 3.4 条件门禁模式

**特点**：根据变更内容动态选择检查项

```
if 变更文件匹配 "*.ts" → 执行 TypeScript 检查
if 变更文件匹配 "*.css" → 执行样式检查
if 变更文件匹配 "package.json" → 执行依赖检查
```

**配置**：

```yaml
gate:
  mode: conditional
  rules:
    - pattern: "**/*.ts"
      checks:
        - lint:ts
        - typecheck
    - pattern: "**/*.css"
      checks:
        - lint:css
    - pattern: "package.json"
      checks:
        - deps:check
```

### 3.5 降级门禁模式

**特点**：主检查失败时执行降级检查

```
主检查 → 失败 → 降级检查 → 通过/失败
```

**配置**：

```yaml
gate:
  mode: fallback
  primary:
    - name: full-test
      command: npm run test:full
  fallback:
    - name: quick-test
      command: npm run test:quick
```

## §4 门禁配置最佳实践

### 4.1 本地开发环境

```bash
npx husky install
npx husky add .husky/pre-commit "npm run gate:commit"
npx husky add .husky/pre-push "npm run gate:push"
```

### 4.2 CI 环境配置

```yaml
name: Gate Checks
on: [push, pull_request]

jobs:
  gate:
    strategy:
      matrix:
        node: [18, 20]
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm ci
      - run: npm run gate:all
```

### 4.3 跳过门禁（仅限紧急情况）

```bash
git commit --no-verify    # 跳过 pre-commit
git push --no-verify      # 跳过 pre-push
```

**警告**：跳过门禁需在 PR 中说明原因，并补充后续修复计划。

### 4.4 门禁报告格式

```
=== Gate Check Report ===
Time: 2026-08-13 14:30:00
Branch: feature/new-feature

[L1 Commit Gate]
  ✅ lint: passed (2s)
  ✅ typecheck: passed (3s)
  ✅ test:unit: passed (5s) - 42 tests

[L2 Push Gate]
  ✅ test:integration: passed (12s) - 8 tests
  ✅ build: passed (15s)
  ⚠️  coverage: 78% (threshold: 80%)

[Result] ⚠️  WARNING - Coverage below threshold
```

## §5 故障排查

### 5.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 门禁超时 | 检查项过多或执行慢 | 拆分检查 / 增加超时时间 |
| 误阻断 | 规则过于严格 | 调整阈值 / 添加例外 |
| 漏检查 | 配置不完整 | 补充检查项 / 审查配置 |
| 本地通过 CI 失败 | 环境差异 | 统一环境 / 使用 Docker |

### 5.2 调试命令

```bash
npm run gate:commit --verbose
npm run gate:push --debug
npm run gate:all --dry-run
```

## §6 参考资料

- [husky 官方文档](https://typicode.github.io/husky/)
- [GitHub Actions 工作流](https://docs.github.com/en/actions)
- [Jest 覆盖率配置](https://jestjs.io/docs/configuration#coveragethreshold-object)