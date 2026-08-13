# 场景 03：定制 Guard 检查规则

> 本场景展示如何定制 Guard Skills 的检查规则，包括白名单配置、自定义守卫脚本和规则优化。

---

## 场景描述

**背景**：项目使用了 Guard Skills 控制质量，但默认规则过于严格或不够严格，需要根据项目实际情况调整。

**目标**：
- 理解 Guard 配置机制
- 配置合理的白名单
- 编写自定义守卫规则

**预计时间**：1-2 小时

---

## 前置条件

### 环境要求

- 已完成场景 01（项目控制体系已建立）
- 熟悉 Guard Skills 规范（已阅读 `references/guard-skills-guide.md`）

### 评估定制需求

```
需要定制 Guard 的信号：
✓ 守卫检查频繁误报（误报率 > 10%）
✓ 合理操作被阻断（团队频繁申请豁免）
✓ 新增业务规则（现有守卫未覆盖）
✓ 安全要求变更（需要加强或放宽检查）
```

---

## 详细步骤

### Step 1：分析现有守卫行为（15 分钟）

#### 1.1 查看守卫执行日志

```bash
# 查看最近的守卫执行记录
ls -lt reports/guard-*.json | head -5

# 查看具体报告
cat reports/guard-20250813-143000.json | jq '.results[] | select(.status == "BLOCK")'
```

#### 1.2 统计误报情况

```bash
# 统计阻断次数
grep -r "BLOCK" reports/guard-*.json | wc -l

# 统计误报次数（已申请白名单）
grep -r "whitelist" guard-config.json | wc -l
```

#### 1.3 识别定制需求

```yaml
定制需求分析:
  高频误报规则:
    - rule: "hardcoded_ip"
      reason: "内网 IP 地址合法"
      count: 15 次/周
  
  过于严格规则:
    - rule: "coverage_threshold"
      reason: "新模块覆盖率要求过高"
      current: 90%
      expected: 80%
  
  缺失规则:
    - rule: "custom_api_version"
      reason: "项目特有的 API 版本规范"
      status: "待实现"
```

---

### Step 2：配置白名单（30 分钟）

#### 2.1 理解白名单机制

Guard Skills 的核心原则：**默认禁止，白名单放行**。

```yaml
白名单生命周期:
  1. 申请 → 填写原因、设置期限
  2. 审批 → 记录审批人、确认条件
  3. 生效 → Guard 检查时匹配豁免
  4. 过期 → 自动清理或人工移除
```

#### 2.2 配置 API 契约 Guard 白名单

编辑 `guards/guard-config.json`：

```json
{
  "guards": [
    {
      "name": "api-contract-guard",
      "enabled": true,
      "severity": "HIGH",
      "whitelist": [
        {
          "id": "WL-API-001",
          "target": {
            "type": "path",
            "pattern": "/internal/*"
          },
          "reason": "内部调试端点，仅限开发环境",
          "expires": "2025-12-31",
          "conditions": [
            {
              "type": "environment",
              "value": "development"
            }
          ],
          "approved_by": "architect",
          "approved_at": "2025-08-13"
        },
        {
          "id": "WL-API-002",
          "target": {
            "type": "path",
            "pattern": "/health"
          },
          "reason": "健康检查端点，无需认证",
          "expires": null,
          "approved_by": "team-lead",
          "approved_at": "2025-08-10"
        }
      ]
    }
  ]
}
```

#### 2.3 配置测试覆盖 Guard 白名单

```json
{
  "guards": [
    {
      "name": "test-coverage-guard",
      "enabled": true,
      "severity": "HIGH",
      "whitelist": [
        {
          "id": "WL-COV-001",
          "target": {
            "type": "path",
            "pattern": "generated/**"
          },
          "reason": "自动生成代码，无业务逻辑",
          "coverage_exempt": true,
          "approved_by": "tech-lead"
        },
        {
          "id": "WL-COV-002",
          "target": {
            "type": "path",
            "pattern": "legacy/**"
          },
          "reason": "遗留代码，暂不纳入覆盖统计",
          "coverage_exempt": true,
          "expires": "2025-06-30",
          "tech_debt": "TI-1234"
        }
      ]
    }
  ]
}
```

#### 2.4 配置安全约束 Guard 白名单

```json
{
  "guards": [
    {
      "name": "security-guard",
      "enabled": true,
      "severity": "CRITICAL",
      "whitelist": [
        {
          "id": "WL-SEC-001",
          "target": {
            "type": "file",
            "pattern": "tests/fixtures/**"
          },
          "reason": "测试用例，使用测试环境凭证",
          "secrets_allowed": true,
          "conditions": [
            {
              "type": "secret_prefix",
              "value": "TEST_"
            }
          ]
        },
        {
          "id": "WL-SEC-002",
          "target": {
            "type": "dependency",
            "pattern": "legacy-lib@1.2.3"
          },
          "reason": "遗留系统依赖，过渡期保留",
          "cve": "CVE-2024-XXXX",
          "expires": "2024-12-31",
          "mitigation": "网络隔离 + 访问控制"
        }
      ]
    }
  ]
}
```

---

### Step 3：编写自定义守卫脚本（45 分钟）

#### 3.1 确定自定义需求

以"禁止硬编码内网 IP"为例：

```yaml
自定义守卫需求:
  名称: internal-ip-guard
  目的: 防止硬编码内网 IP 地址
  触发: pre-commit / pre-push
  检查: 代码中是否包含内网 IP 模式
  白名单: 允许测试文件和配置文件
```

#### 3.2 创建守卫脚本

创建 `guards/internal-ip-guard.mjs`：

```javascript
#!/usr/bin/env node

/**
 * 内网 IP 守卫 - 检查硬编码的内网 IP 地址
 * 
 * 禁止规则：
 *   - 禁止在源代码中硬编码内网 IP
 *   - 允许：配置文件、测试文件、文档
 */

import fs from 'fs';
import path from 'path';

const INTERNAL_IP_PATTERN = /\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b/g;

const ALLOWED_PATTERNS = [
  /^tests\//,
  /^test\//,
  /^spec\//,
  /^__tests__\//,
  /\.config\.(js|ts|mjs|json)$/,
  /\.env\./,
  /README\.md$/,
  /docs\//
];

/**
 * 检查单个文件
 */
function checkFile(filePath) {
  const relativePath = filePath.replace(process.cwd() + path.sep, '');
  
  // 检查是否在白名单中
  const isAllowed = ALLOWED_PATTERNS.some(pattern => pattern.test(relativePath));
  if (isAllowed) {
    return { status: 'SKIP', reason: 'Allowed pattern' };
  }
  
  const content = fs.readFileSync(filePath, 'utf-8');
  const matches = content.match(INTERNAL_IP_PATTERN);
  
  if (matches) {
    return {
      status: 'BLOCK',
      violations: matches.map(ip => ({
        type: 'internal_ip',
        value: ip,
        message: `发现硬编码内网 IP: ${ip}`,
        file: relativePath
      }))
    };
  }
  
  return { status: 'PASS' };
}

/**
 * 检查目录
 */
function checkDirectory(dir, results = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    
    if (entry.isDirectory()) {
      // 跳过 node_modules 和 .git
      if (['node_modules', '.git', 'dist', 'build'].includes(entry.name)) {
        continue;
      }
      checkDirectory(fullPath, results);
    } else if (entry.isFile()) {
      // 只检查源代码文件
      if (/\.(js|ts|mjs|jsx|tsx|py|java|go)$/.test(entry.name)) {
        const result = checkFile(fullPath);
        if (result.status !== 'SKIP') {
          results.push({
            file: fullPath.replace(process.cwd() + path.sep, ''),
            ...result
          });
        }
      }
    }
  }
  
  return results;
}

/**
 * 生成报告
 */
function generateReport(results) {
  const summary = {
    total: results.length,
    passed: results.filter(r => r.status === 'PASS').length,
    blocked: results.filter(r => r.status === 'BLOCK').length
  };
  
  const report = {
    guard_name: 'internal-ip-guard',
    timestamp: new Date().toISOString(),
    summary,
    results: results.filter(r => r.status === 'BLOCK'),
    exit_code: summary.blocked > 0 ? 1 : 0
  };
  
  return report;
}

// CLI 入口
const args = process.argv.slice(2);
const targetPath = args[0] || process.cwd();

console.log(`🛡️  Internal IP Guard 检查中...`);
console.log(`目标路径: ${targetPath}\n`);

const results = checkDirectory(targetPath);
const report = generateReport(results);

console.log(`\n=== Guard Report ===`);
console.log(`检查文件: ${report.summary.total}`);
console.log(`通过: ${report.summary.passed}`);
console.log(`阻断: ${report.summary.blocked}`);

if (report.summary.blocked > 0) {
  console.log(`\n🛑 阻断详情:\n`);
  for (const result of report.results) {
    console.log(`文件: ${result.file}`);
    for (const v of result.violations) {
      console.log(`  - ${v.message}`);
    }
    console.log(`\n修复建议:`);
    console.log(`1. 将 IP 地址移到配置文件或环境变量`);
    console.log(`2. 或在 guard-config.json 中添加白名单:\n`);
    console.log(`   whitelist:`);
    console.log(`     - id: WL-IP-XXX`);
    console.log(`       target:`);
    console.log(`         type: file`);
    console.log(`         pattern: "${result.file}"`);
    console.log(`       reason: "请填写豁免原因"`);
    console.log(`       expires: "YYYY-MM-DD"\n`);
  }
}

process.exit(report.exit_code);
```

#### 3.3 注册守卫

编辑 `guards/guard-config.json`：

```json
{
  "guards": [
    {
      "name": "internal-ip-guard",
      "enabled": true,
      "severity": "HIGH",
      "command": "node guards/internal-ip-guard.mjs",
      "whitelist": []
    }
  ]
}
```

#### 3.4 添加到执行脚本

编辑 `scripts/run-guards.sh`：

```bash
#!/bin/bash

echo "🛡️  Running Guards..."

# API Contract Guard
node guards/api-contract-guard.mjs

# Test Coverage Guard
node guards/test-coverage-guard.mjs

# Internal IP Guard (NEW)
node guards/internal-ip-guard.mjs

echo "✅ All guards passed"
```

---

### Step 4：调整守卫严重性（15 分钟）

#### 4.1 理解严重性分级

| 级别 | 含义 | 阻断行为 |
|------|------|----------|
| CRITICAL | 严重安全/架构风险 | 立即阻断 |
| HIGH | 重要规范违反 | 阻断直到修复 |
| MEDIUM | 一般规范违反 | 警告 + 人工确认 |
| LOW | 建议/提醒 | 输出建议，不阻断 |

#### 4.2 调整示例

```json
{
  "guards": [
    {
      "name": "test-coverage-guard",
      "severity": "MEDIUM",  // 从 HIGH 调整为 MEDIUM
      "reason": "新项目初期，覆盖率要求适当放宽"
    }
  ]
}
```

---

### Step 5：验证定制效果（15 分钟）

#### 5.1 本地测试

```bash
# 运行所有守卫
bash scripts/run-guards.sh

# 运行单个守卫
node guards/internal-ip-guard.mjs src/
```

#### 5.2 预期结果

```
🛡️  Internal IP Guard 检查中...
目标路径: /path/to/project/src

=== Guard Report ===
检查文件: 45
通过: 43
阻断: 2

🛑 阻断详情:

文件: src/config/database.js
  - 发现硬编码内网 IP: 192.168.1.100

修复建议:
1. 将 IP 地址移到配置文件或环境变量
2. 或在 guard-config.json 中添加白名单:
   ...
```

#### 5.3 CI 集成测试

提交代码，观察 CI 执行结果：

```bash
git add .
git commit -m "test: guard customization"
git push
```

---

## 预期结果

### 成功标准

- [ ] 白名单配置有效（豁免规则生效）
- [ ] 自定义守卫可执行（无语法错误）
- [ ] 严重性调整生效（阻断/警告行为符合预期）
- [ ] 误报率降低（≤ 10%）
- [ ] 文档已更新（记录定制原因）

### 产出物清单

```yaml
定制 Guard 产物:
  配置文件:
    - guard-config.json（更新）
  
  守卫脚本:
    - guards/internal-ip-guard.mjs（新建）
  
  执行脚本:
    - scripts/run-guards.sh（更新）
  
  文档:
    - 定制说明（在项目 README 中记录）
```

---

## 常见问题

### Q1：白名单过多会有什么问题？

**风险**：
- 安全规则失效
- 守卫失去约束力
- 技术债务累积

**建议**：
```yaml
白名单管理原则:
  1. 每个白名单必须有明确的 reason
  2. 每个白名单必须有 expires（除永久豁免）
  3. 每个白名单必须有 approved_by
  4. 定期（每月）审查白名单有效性
  5. 白名单数量建议控制在总规则的 10% 以内
```

### Q2：如何处理守卫性能问题？

**优化策略**：

```yaml
性能优化:
  1. 文件过滤:
     - 只检查变更文件（git diff）
     - 跳过 node_modules、dist 等
  
  2. 并行执行:
     - 多个守卫并行运行
     - 使用 Promise.all
  
  3. 缓存结果:
     - 缓存检查结果（基于文件哈希）
     - 未变更文件跳过检查
  
  4. 增量检查:
     - pre-commit 只检查暂存文件
     - CI 只检查 PR 变更文件
```

### Q3：如何平衡严格度和开发效率？

**分阶段策略**：

```
Phase 1（项目启动）:
  - 规则宽松，允许适度例外
  - 重点：建立控制体系骨架

Phase 2（稳定期）:
  - 逐步收紧规则
  - 减少例外，增加自动化

Phase 3（成熟期）:
  - 全面严格，例外需特批
  - 重点：持续优化规则质量
```

**度量驱动**：

```yaml
监控指标:
  - 门禁通过率 ≥ 90%（低于则说明规则过严）
  - 误报率 ≤ 10%（高于则说明规则需优化）
  - 白名单数量 ≤ 总规则的 10%
```

### Q4：守卫规则冲突如何处理？

**冲突类型**：

| 冲突类型 | 解决原则 |
|---------|---------|
| Guard vs Guard | 安全 > 业务 > 便捷 |
| Guard vs Gate | 禁止性规则优先 |
| Gate vs Gate | 上游门禁优先 |

**解决流程**：

```
发现冲突 → 记录冲突详情 → 上报技术负责人 → 集体决策 → 显式声明解决方案
```

### Q5：如何处理紧急绕过？

**紧急绕过流程**：

```bash
# 方式 1：临时禁用守卫（仅限本地）
export SKIP_GUARDS=true
git commit -m "emergency: critical fix"

# 方式 2：跳过 Git Hooks（不推荐）
git commit --no-verify -m "emergency: critical fix"
```

**后续要求**：

```yaml
紧急绕过后续:
  必须:
    - 在 PR 中说明绕过原因
    - 提供后续修复计划
    - 补充测试用例
  
  时间限制:
    - 绕过后 24 小时内补充说明
    - 绕过后 1 周内完成修复
```

---

## 后续步骤

1. **监控误报率**：建立误报率监控看板
2. **定期审查白名单**：每月审查白名单有效性
3. **规则优化迭代**：根据使用反馈优化规则
4. **团队培训**：组织团队学习守卫规则

---

## 相关资源

- [Guard Skills 指南](../references/guard-skills-guide.md)
- [Guard Skill 模板](../templates/guard-skill-template.md)
- [实施路线图](../references/implementation-roadmap.md)

---

> **维护者**：agent-dev-control-kit
> **最后更新**：2025-08-13
> **版本**：1.0.0