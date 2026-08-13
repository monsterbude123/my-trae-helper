# Guard 控制实现规范

## §1 API 契约 Guard

### 1.1 检查项

| 检查项 | 严重性 | 说明 |
|--------|--------|------|
| 端点命名规范 | HIGH | 必须遵循 RESTful 或项目约定 |
| 请求/响应 Schema 完整性 | HIGH | 必须定义完整的 JSON Schema |
| 版本号管理 | MEDIUM | 新端点必须声明版本 |
| 废弃端点标记 | LOW | 废弃端点必须有 deprecation 标记 |
| 认证要求声明 | HIGH | 每个端点必须声明认证方式 |

### 1.2 禁止规则

```yaml
forbidden:
  - 添加无 Schema 的 API 端点
  - 修改已发布 API 的响应结构（破坏性变更）
  - 跳过版本号递增（major/minor/patch）
  - 移除必需字段而不升级版本
  - 在生产端点使用 mock 数据
  - 端点命名含动态片段多于 2 个
```

### 1.3 白名单机制

```yaml
whitelist:
  - path: "/health"
    reason: "健康检查端点，无需认证"
    expires: "永久"
  
  - path: "/internal/*"
    reason: "内部调试端点，仅限开发环境"
    expires: "按需"
    conditions:
      - environment: "development"
  
  - path: "/legacy/v1/*"
    reason: "遗留系统兼容，维护期内保留"
    expires: "2025-12-31"
    deprecation_notice: "计划下线，请迁移到 v2"
```

### 1.4 检查流程

```
1. 解析 API 定义文件（OpenAPI/GraphQL Schema）
2. 遍历所有端点，逐项执行检查
3. 对于禁止规则，检查是否存在匹配项
4. 对于匹配项，检查白名单是否覆盖
5. 生成检查报告，标记 PASS/WARN/BLOCK
```

### 1.5 失败处理

```bash
# 错误输出模板
🛑 API 契约 Guard 阻断

检查项: [检查名称]
违规位置: [文件路径:行号]
违规内容: [具体内容]
违反规则: [规则描述]

修复建议:
1. [建议1]
2. [建议2]

白名单申请（如适用）:
  在 guard-config.yaml 中添加:
  whitelist:
    - path: "[路径]"
      reason: "[原因]"
      expires: "[过期时间]"
```

## §2 测试覆盖率 Guard

### 2.1 检查项

| 检查项 | 严重性 | 说明 |
|--------|--------|------|
| 全局覆盖率 | HIGH | 必须 ≥ 阈值（默认 80%） |
| 关键路径覆盖 | HIGH | 核心 API 必须有测试 |
| 新增代码覆盖 | MEDIUM | 新增代码必须有测试 |

### 2.2 配置示例

```yaml
coverage:
  global:
    branches: 80
    functions: 80
    lines: 80
    statements: 80
  
  critical_paths:
    - "src/api/**/*.ts"
    - "src/core/**/*.ts"
  
  new_code:
    enabled: true
    threshold: 100
```

### 2.3 检查流程

```bash
# 运行覆盖率检查
npm run test:coverage

# 解析覆盖率报告
# 对比阈值
# 标记 PASS/WARN/BLOCK
```

## §3 依赖安全 Guard

### 3.1 检查项

| 检查项 | 严重性 | 说明 |
|--------|--------|------|
| 已知漏洞 | HIGH | 依赖无已知 CVE 漏洞 |
| 许可证合规 | MEDIUM | 许可证符合项目政策 |
| 过时依赖 | LOW | 提示更新可用依赖 |

### 3.2 配置示例

```yaml
security:
  vulnerabilities:
    level: HIGH
  
  licenses:
    allowed: [MIT, Apache-2.0, BSD-3-Clause]
    forbidden: [GPL-3.0, AGPL-3.0]
  
  outdated:
    enabled: true
    severity_threshold: MAJOR
```

## §4 性能预算 Guard

### 4.1 检查项

| 检查项 | 严重性 | 说明 |
|--------|--------|------|
| 包体积 | HIGH | 不超过阈值 |
| 加载时间 | MEDIUM | 关键路径加载时间 |
| 内存占用 | MEDIUM | 运行时内存占用 |

### 4.2 配置示例

```yaml
performance:
  bundle_size:
    warning: 500KB
    error: 1MB
  
  load_time:
    warning: 3s
    error: 5s
  
  memory:
    warning: 100MB
    error: 200MB
```