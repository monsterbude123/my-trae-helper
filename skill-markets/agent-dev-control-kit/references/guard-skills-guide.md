# Guard Skills 参考指南

> Agent 开发控制套件 — 守门人技能标准规范

---

## 概述

Guard Skills（守门人技能）是 Agent 开发流程中的自动化门禁，在关键节点执行强制性检查，阻止不符合规范的代码/设计进入下一阶段。

**核心设计原则**：
- **禁止性规则优先**：明确列出不允许的行为
- **白名单机制兜底**：为合理例外提供逃生通道
- **失败必须阻断**：检查失败必须停止流程，不允许绕过

---

## §1 五个核心 Guard Skills

### 1.1 API 契约 Guard

**触发时机**：API 定义变更 / 接口发布前

#### 检查内容

| 检查项 | 严重性 | 说明 |
|--------|--------|------|
| 端点命名规范 | HIGH | 必须遵循 RESTful 或项目约定 |
| 请求/响应 Schema 完整性 | HIGH | 必须定义完整的 JSON Schema |
| 版本号管理 | MEDIUM | 新端点必须声明版本 |
| 废弃端点标记 | LOW | 废弃端点必须有 deprecation 标记 |
| 认证要求声明 | HIGH | 每个端点必须声明认证方式 |

#### 禁止规则

```yaml
forbidden:
  - 添加无 Schema 的 API 端点
  - 修改已发布 API 的响应结构（破坏性变更）
  - 跳过版本号递增（major/minor/patch）
  - 移除必需字段而不升级版本
  - 在生产端点使用 mock 数据
  - 端点命名含动态片段多于 2 个
```

#### 白名单机制

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

#### 检查流程

```
1. 解析 API 定义文件（OpenAPI/GraphQL Schema/内部协议）
2. 遍历所有端点，逐项执行检查
3. 对于禁止规则，检查是否存在匹配项
4. 对于匹配项，检查白名单是否覆盖
5. 生成检查报告，标记 PASS/WARN/BLOCK
```

#### 失败处理

| 结果 | 处理 |
|------|------|
| PASS | 继续流程 |
| WARN | 输出警告，允许继续（需人工确认） |
| BLOCK | 终止流程，输出详细错误信息，要求修复 |

**错误输出模板**：

```
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
    - path: "..."
      reason: "..."
      expires: "..."
```

---

### 1.2 架构约束 Guard

**触发时机**：模块划分 / 依赖引入 / 跨层调用前

#### 检查内容

| 检查项 | 严重性 | 说明 |
|--------|--------|------|
| 分层边界遵守 | HIGH | UI/业务/数据层不可越界调用 |
| 依赖方向正确性 | HIGH | 依赖必须单向（外层依赖内层） |
| 循环依赖检测 | HIGH | 禁止模块间循环依赖 |
| 单一职责原则 | MEDIUM | 模块职责是否清晰 |
| 接口隔离原则 | MEDIUM | 接口是否最小化 |

#### 禁止规则

```yaml
forbidden:
  - UI 层直接访问数据库
  - 数据层调用业务服务
  - 模块 A 依赖模块 B，且模块 B 依赖模块 A
  - 跨模块直接访问私有实现
  - 单文件超过 500 行（不含注释）
  - 单函数超过 50 行
  - 单类承担超过 3 个职责
```

#### 白名单机制

```yaml
whitelist:
  - module: "utils/logger"
    reason: "日志工具，全局可访问"
    allowed_from: "*"
  
  - module: "config/*"
    reason: "配置模块，各层可读"
    allowed_from: "*"
  
  - file: "scripts/migration/*.py"
    reason: "迁移脚本，允许跨层操作"
    allowed_from: "scripts"
    conditions:
      - environment: "migration"
  
  - module: "legacy/adapter"
    reason: "遗留系统适配器，过渡期允许"
    expires: "2025-06-30"
    tech_debt: "TI-1234"
```

#### 检查流程

```
1. 构建模块依赖图（从 import/require 语句）
2. 检测循环依赖（DFS + 拓扑排序）
3. 验证分层边界（UI → Service → Repository）
4. 检查文件/函数/类大小
5. 对于违规项，检查白名单覆盖
6. 输出架构健康报告
```

#### 失败处理

```
🛑 架构约束 Guard 阻断

违规类型: [循环依赖/跨层调用/职责过重]
涉及模块: [模块A, 模块B]
违规详情: [依赖链路或调用路径]

修复建议:
1. 引入中介者模式解耦
2. 提取共享接口到独立模块
3. 拆分职责到多个服务

白名单申请（如适用）:
  whitelist:
    - module: "..."
      reason: "..."
      tech_debt: "TI-XXXX"
```

---

### 1.3 测试覆盖 Guard

**触发时机**：代码提交 / PR 合并前

#### 检查内容

| 检查项 | 严重性 | 说明 |
|--------|--------|------|
| 行覆盖率阈值 | HIGH | ≥ 80%（可配置） |
| 分支覆盖率阈值 | HIGH | ≥ 70%（可配置） |
| 核心路径覆盖 | HIGH | 关键业务逻辑必须有测试 |
| 新增代码覆盖 | HIGH | 新增代码覆盖率 ≥ 90% |
| 测试用例质量 | MEDIUM | 断言数量 ≥ 函数参数数 |

#### 禁止规则

```yaml
forbidden:
  - 提交无测试的新功能代码
  - 核心业务逻辑缺失测试用例
  - 测试用例仅有 happy path
  - Mock 外部服务但无集成测试补充
  - 测试文件名不遵循命名规范
  - 跳过测试用例（skip/xskip）无注释说明
```

#### 白名单机制

```yaml
whitelist:
  - path: "generated/*"
    reason: "自动生成代码，无业务逻辑"
    coverage_exempt: true
  
  - path: "config/*"
    reason: "纯配置文件"
    coverage_exempt: true
  
  - path: "legacy/*"
    reason: "遗留代码，暂不纳入覆盖统计"
    coverage_exempt: true
    expires: "2025-03-31"
  
  - file: "utils/constants.py"
    reason: "常量定义文件"
    coverage_exempt: true
  
  - test_case: "test_edge_case_*"
    reason: "边界条件测试，仅文档用例"
    skip_allowed: true
    conditions:
      - has_comment: true
```

#### 检查流程

```
1. 运行测试覆盖率工具（pytest-cov / jest --coverage）
2. 解析覆盖率报告
3. 计算各模块覆盖率
4. 检查新增代码覆盖情况（git diff 识别）
5. 验证核心路径是否有测试
6. 对于不达标项，检查白名单
7. 输出覆盖率报告 + 缺口清单
```

#### 失败处理

```
🛑 测试覆盖 Guard 阻断

当前覆盖率: [XX%]
要求覆盖率: [YY%]
缺口模块:
  - [模块A]: [当前%] → 需增加 [N] 个用例
  - [模块B]: [当前%] → 需增加 [M] 个用例

新增代码覆盖:
  文件: [文件路径]
  新增行数: [N]
  已覆盖行数: [M]
  覆盖率: [XX%] < 要求 [90%]

修复建议:
1. 优先补充核心路径测试
2. 使用参数化测试覆盖边界条件
3. Mock 外部依赖，聚焦业务逻辑

白名单申请（如适用）:
  whitelist:
    - path: "..."
      reason: "..."
      coverage_exempt: true
```

---

### 1.4 安全约束 Guard

**触发时机**：代码提交 / 部署前 / 依赖更新后

#### 检查内容

| 检查项 | 严重性 | 说明 |
|--------|--------|------|
| 敏感信息泄露 | CRITICAL | 硬编码密钥/密码/token |
| SQL 注入风险 | HIGH | 动态拼接 SQL |
| XSS 漏洞 | HIGH | 未转义用户输入 |
| 命令注入风险 | HIGH | 执行用户可控命令 |
| 依赖漏洞 | HIGH | 已知 CVE 漏洞 |
| 权限校验缺失 | HIGH | 敏感操作无权限检查 |

#### 禁止规则

```yaml
forbidden:
  - 硬编码 API Key / Password / Token
  - 日志输出敏感信息
  - 用户输入直接拼接到 SQL/命令
  - 用户输入直接渲染到 HTML
  - 使用已知漏洞版本依赖
  - 敏感端点无认证/授权检查
  - 文件上传无类型/大小校验
  - SSRF 风险（用户可控 URL）
```

#### 白名单机制

```yaml
whitelist:
  - file: "tests/fixtures/*"
    reason: "测试用例，使用测试环境凭证"
    secrets_allowed: true
    conditions:
      - secret_prefix: "TEST_"
  
  - file: "docs/examples/*"
    reason: "示例文档，使用占位符"
    secrets_allowed: true
    conditions:
      - secret_pattern: "your-.*-here"
  
  - dependency: "legacy-lib@1.2.3"
    reason: "遗留系统依赖，过渡期保留"
    cve: "CVE-2024-XXXX"
    expires: "2024-12-31"
    mitigation: "网络隔离 + 访问控制"
  
  - endpoint: "/public/search"
    reason: "公开搜索接口"
    auth_required: false
    rate_limit: "100/minute"
```

#### 检查流程

```
1. 扫描代码库敏感信息（regex + entropy 检测）
2. 静态分析安全漏洞（SQLi/XSS/命令注入）
3. 依赖漏洞扫描（npm audit / pip-audit / SCA 工具）
4. 检查权限配置（路由表 + 认证中间件）
5. 对于违规项，检查白名单覆盖
6. 输出安全报告（按严重性分级）
```

#### 失败处理

```
🛑 安全约束 Guard 阻断

严重性: [CRITICAL/HIGH/MEDIUM]
检查项: [检查名称]
违规位置: [文件路径:行号]
违规类型: [硬编码凭证/SQL注入/XSS/...]

风险说明:
  [详细风险描述]
  [攻击路径说明]
  [潜在影响]

修复建议:
1. 使用环境变量存储敏感信息
2. 使用参数化查询替代字符串拼接
3. 转义所有用户输入
4. 升级依赖版本: [当前版本] → [安全版本]

白名单申请（如适用）:
  whitelist:
    - file: "..."
      reason: "..."
      conditions:
        - secret_prefix: "TEST_"
```

---

### 1.5 性能约束 Guard

**触发时机**：性能敏感代码提交 / 发布前压测

#### 检查内容

| 检查项 | 严重性 | 说明 |
|--------|--------|------|
| 循环复杂度 | MEDIUM | 嵌套层数 ≤ 3 |
| 数据库查询优化 | HIGH | N+1 查询检测 |
| 内存使用峰值 | MEDIUM | 单请求内存 ≤ 阈值 |
| 响应时间阈值 | HIGH | P99 ≤ 配置值 |
| 并发能力 | HIGH | 压测 QPS ≥ 要求值 |

#### 禁止规则

```yaml
forbidden:
  - 循环内执行数据库查询（N+1）
  - 循环内创建大对象
  - 递归无深度限制
  - 同步阻塞 IO 在热路径
  - 无分页的大数据查询
  - 未缓存的重复计算
  - 无超时的外部调用
  - 内存泄漏风险模式
```

#### 白名单机制

```yaml
whitelist:
  - function: "batch_import"
    reason: "批量导入脚本，允许大内存"
    peak_memory: "2GB"
    conditions:
      - environment: "batch"
      - timeout: "1h"
  
  - query: "analytics_report"
    reason: "复杂报表查询，允许较长响应"
    response_time: "30s"
    conditions:
      - cache_ttl: "1h"
      - async: true
  
  - loop: "migration_process"
    reason: "数据迁移，允许批量处理"
    n_plus_1_allowed: true
    conditions:
      - batch_size: 1000
      - progress_log: true
```

#### 检查流程

```
1. 静态分析热点代码（循环/递归/IO）
2. 检测 N+1 查询模式
3. 内存使用分析（profiling）
4. 压力测试（基准性能数据）
5. 对比性能基线
6. 对于超标项，检查白名单
7. 输出性能报告
```

#### 失败处理

```
🛑 性能约束 Guard 阻断

检查项: [检查名称]
当前值: [实际值]
要求值: [阈值]
差距: [百分比/倍数]

性能热点:
  - [位置]: [问题描述] → [影响]
  - [位置]: [问题描述] → [影响]

修复建议:
1. 使用预加载替代循环查询
2. 添加查询结果缓存
3. 异步化非关键路径
4. 分页处理大数据集

白名单申请（如适用）:
  whitelist:
    - function: "..."
      reason: "..."
      conditions:
        - environment: "batch"
```

---

## §2 Guard Skill 通用模板

```yaml
# guard-skill-template.yaml

name: {guard-name}-guard
description: {一句话描述 + 触发时机}
version: 1.0.0
trigger:
  events: [{触发事件列表}]
  conditions: [{触发条件}]

checks:
  - name: {检查项名称}
    severity: {CRITICAL|HIGH|MEDIUM|LOW}
    description: {检查说明}
    check_logic: |
      {检查逻辑伪代码或规则表达式}
    auto_fix: {是否支持自动修复}

forbidden:
  - rule: {禁止规则描述}
    severity: {CRITICAL|HIGH|MEDIUM|LOW}
    rationale: {规则存在原因}
  
  - rule: {另一条禁止规则}
    severity: HIGH
    rationale: {原因说明}

whitelist:
  - target: {匹配目标（path/module/file/function）}
    pattern: {匹配模式（支持 glob/regex）}
    reason: {允许原因}
    expires: {过期时间（可选）}
    conditions: [{附加条件}]
    approved_by: {审批人（可选）}
    approved_at: {审批时间（可选）}

check_flow:
  steps:
    - step: 1
      action: {步骤描述}
      tool: {使用的工具}
    - step: 2
      action: {步骤描述}
      tool: {使用的工具}
  parallel: {是否支持并行检查}

failure_handling:
  PASS:
    action: continue
    output: {输出格式}
  WARN:
    action: confirm_and_continue
    output: {输出格式}
    require: {需要谁确认}
  BLOCK:
    action: stop
    output: {输出格式}
    exit_code: 1

report:
  format: {json|markdown|html}
  include:
    - summary
    - details
    - fix_suggestions
    - whitelist_template
  output_path: {报告输出路径}
```

---

## §3 实现模式

### 3.1 禁止性规则 + 白名单机制

**核心思想**：默认禁止，白名单放行。

```
检查流程:
┌─────────────────┐
│  获取检查目标    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 遍历禁止规则    │
│ 匹配目标特征    │
└────────┬────────┘
         │
    ┌────┴────┐
    │是否匹配? │
    └────┬────┘
         │
    ┌────┼────┐
    │是  │    │否
    ▼    │    ▼
┌───────┴─┐ ┌──────────┐
│检查白名单│ │标记 PASS │
└────┬────┘ └──────────┘
     │
 ┌───┴───┐
 │白名单 │
 │覆盖?  │
 └───┬───┘
     │
┌────┼────┐
│是  │    │否
▼    │    ▼
┌────┴──┐ ┌───────────┐
│WARN   │ │BLOCK      │
│记录豁免│ │输出违规详情│
└───────┘ └───────────┘
```

### 3.2 白名单配置结构

```yaml
# guard-config.yaml

whitelist:
  - id: WL-001
    target:
      type: path  # path | module | file | function | dependency
      pattern: "tests/**"
    reason: "测试代码，豁免生产规范"
    expires: null  # 永久有效
    conditions:
      - type: environment
        value: development
    approved_by: team-lead
    approved_at: 2024-01-15
  
  - id: WL-002
    target:
      type: module
      pattern: "legacy/**"
    reason: "遗留系统，过渡期保留"
    expires: 2025-12-31
    tech_debt_ticket: TI-1234
    conditions: []
    approved_by: architect
    approved_at: 2024-03-20
```

### 3.3 检查结果数据结构

```json
{
  "guard_name": "api-contract-guard",
  "timestamp": "2024-01-15T10:30:00Z",
  "trigger": {
    "event": "pre-commit",
    "files_changed": ["src/api/users.py"]
  },
  "summary": {
    "total_checks": 5,
    "passed": 3,
    "warned": 1,
    "blocked": 1
  },
  "results": [
    {
      "check_name": "endpoint_schema",
      "status": "PASS",
      "target": "src/api/users.py:45",
      "details": "所有端点均有完整 Schema"
    },
    {
      "check_name": "breaking_change",
      "status": "BLOCK",
      "severity": "HIGH",
      "target": "src/api/users.py:52",
      "violated_rule": "修改已发布 API 的响应结构（破坏性变更）",
      "details": "字段 'user_id' 类型从 int 变为 string",
      "fix_suggestions": [
        "新增字段 'user_id_str'，保留原字段",
        "版本号递增: v1 → v2"
      ],
      "whitelist_template": {
        "target": "src/api/users.py",
        "reason": "请填写豁免原因",
        "expires": "YYYY-MM-DD"
      }
    }
  ],
  "exit_code": 1
}
```

### 3.4 与 CI/CD 集成示例

```yaml
# .github/workflows/guard-check.yml

name: Guard Skills Check

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  guard-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: API Contract Guard
        run: |
          python scripts/guards/api_contract_guard.py \
            --config guard-config.yaml \
            --report-format json \
            --report-path reports/api-guard.json
          
      - name: Architecture Guard
        run: |
          python scripts/guards/architecture_guard.py \
            --config guard-config.yaml
      
      - name: Test Coverage Guard
        run: |
          pytest --cov=src --cov-fail-under=80 \
            --cov-report=xml:reports/coverage.xml
          python scripts/guards/coverage_guard.py \
            --report reports/coverage.xml \
            --threshold 80
      
      - name: Security Guard
        run: |
          pip-audit
          python scripts/guards/security_guard.py \
            --config guard-config.yaml
      
      - name: Performance Guard (on release)
        if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/')
        run: |
          python scripts/guards/performance_guard.py \
            --baseline reports/perf-baseline.json
      
      - name: Upload Guard Reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: guard-reports
          path: reports/
```

---

## §4 技能清单

| 技能名称 | 触发时机 | 检查重点 | 严重性范围 |
|----------|----------|----------|------------|
| API 契约 Guard | API 变更/发布前 | Schema 完整性/版本管理/破坏性变更 | HIGH |
| 架构约束 Guard | 模块划分/依赖引入 | 分层边界/循环依赖/职责划分 | HIGH |
| 测试覆盖 Guard | 代码提交/PR 合并 | 覆盖率阈值/核心路径覆盖 | HIGH |
| 安全约束 Guard | 代码提交/部署前 | 敏感信息/注入漏洞/依赖漏洞 | CRITICAL |
| 性能约束 Guard | 性能代码提交/发布压测 | N+1 查询/内存峰值/响应时间 | MEDIUM-HIGH |

---

## §5 最佳实践

### 5.1 Guard Skills 配置原则

1. **渐进式严格**：初期可放宽阈值，逐步收紧
2. **白名单有期限**：所有豁免必须设置 expires，定期清理
3. **白名单有审批**：生产环境豁免需要记录审批人
4. **报告可追溯**：保留历史检查报告，便于回溯

### 5.2 失败处理原则

1. **BLOCK 必须阻断**：不允许绕过，必须修复或申请白名单
2. **WARN 需确认**：人工确认后方可继续，留下记录
3. **自动修复优先**：能自动修复的优先修复，减少人工干预

### 5.3 与开发流程集成

```
开发流程:
┌─────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐
│ 本地开发 │───▶│ pre-commit│───▶│ PR 创建  │───▶│ CI 检查   │
└─────────┘    │ Guard     │    └─────────┘    │ Guard    │
               └──────────┘                    └──────────┘
                    │                               │
               ┌────┴────┐                    ┌────┴────┐
               │BLOCK?   │                    │BLOCK?   │
               └────┬────┘                    └────┬────┘
                    │                               │
               ┌────┼────┐                    ┌────┼────┐
               │是  │    │否                  │是  │    │否
               ▼    │    ▼                    ▼    │    ▼
          ┌───────┐ │  ┌───────┐         ┌───────┐ │  ┌───────┐
          │修复/豁免│ │  │  提交  │         │修复/豁免│ │  │ 合并  │
          └───────┘ │  └───────┘         └───────┘ │  └───────┘
                    │                               │
                    ▼                               ▼
               ┌──────────┐                    ┌──────────┐
               │重新检查   │                    │部署前检查 │
               └──────────┘                    └──────────┘
```

---

## §6 附录

### A. 检查严重性分级

| 级别 | 含义 | 阻断行为 |
|------|------|----------|
| CRITICAL | 严重安全/架构风险 | 立即阻断 |
| HIGH | 重要规范违反 | 阻断直到修复 |
| MEDIUM | 一般规范违反 | 警告 + 人工确认 |
| LOW | 建议/提醒 | 输出建议，不阻断 |

### B. 白名单生命周期

```
白名单生命周期:
┌─────────┐     ┌──────────┐     ┌───────────┐     ┌─────────┐
│ 申请    │────▶│ 审批     │────▶│ 生效      │────▶│ 过期/移除│
└─────────┘     └──────────┘     └───────────┘     └─────────┘
     │               │                 │                 │
     │               │                 │                 │
     ▼               ▼                 ▼                 ▼
填写原因        记录审批人         Guard 检查时         自动清理
设置期限        确认条件           匹配豁免            或人工移除
```

### C. Guard Skill 命名规范

```
{检查领域}-guard

示例:
  - api-contract-guard
  - architecture-guard
  - test-coverage-guard
  - security-guard
  - performance-guard
```

---

> **维护者**: agent-dev-control-kit
> **最后更新**: 2025-08-13
> **版本**: 1.0.0