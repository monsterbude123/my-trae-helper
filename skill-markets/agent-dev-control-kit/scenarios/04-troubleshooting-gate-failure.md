# 场景 04：门禁失败排查流程

> 本场景展示如何系统性排查门禁检查失败，提供诊断流程、常见问题和解决方案。

---

## 场景描述

**背景**：开发过程中遇到门禁检查失败，需要快速定位原因并修复。

**目标**：
- 理解门禁失败类型
- 掌握系统化排查流程
- 快速恢复开发流程

**预计时间**：30 分钟 - 1 小时

---

## 前置条件

### 环境要求

- 项目控制体系已建立
- 具备基本的问题排查能力

### 排查心态

```
门禁失败不是坏事：
✓ 它是质量问题的早期预警
✓ 帮助团队在合并前发现问题
✓ 避免问题流入生产环境

排查原则：
1. 不慌张：失败是正常的质量保护机制
2. 不绕过：除非紧急情况，不允许跳过门禁
3. 不隐藏：记录失败原因，避免重复发生
```

---

## 门禁失败类型总览

### 按层级分类

```
L1 提交前门禁失败:
  ├─ lint 错误
  ├─ typecheck 错误
  └─ 单元测试失败

L2 推送前门禁失败:
  ├─ 集成测试失败
  ├─ 覆盖率不达标
  └─ 构建失败

L3 合并前门禁失败:
  ├─ E2E 测试失败
  ├─ 代码审查未通过
  └─ 冲突未解决

L4 发布前门禁失败:
  ├─ 安全漏洞
  ├─ 性能退化
  └─ 验收测试失败
```

### 按来源分类

| 失败来源 | 典型表现 | 影响范围 |
|---------|---------|---------|
| Execution Skill 执行失败 | 数据变更失败、文档同步失败 | 单次执行 |
| Guard 检查阻断 | 安全规则违反、覆盖率不足 | 提交/推送 |
| Gate 流程阻断 | 门禁检查超时、依赖服务不可用 | 合并/发布 |

---

## 详细排查步骤

### Step 1：读取失败报告（5 分钟）

#### 1.1 查看本地失败输出

```bash
# 查看最近的门禁执行日志
ls -lt reports/gate-*.json | head -1

# 查看详细报告
cat reports/gate-20250813-143000.json | jq '.'
```

#### 1.2 查看失败摘要

```bash
# 提取失败项
cat reports/gate-20250813-143000.json | jq '.results[] | select(.status == "FAIL" or .status == "BLOCK")'
```

#### 1.3 查看 CI 失败日志

如果是 CI 环境失败：

1. 打开 GitHub Actions / GitLab CI 页面
2. 找到失败的 workflow
3. 查看详细日志
4. 下载 artifacts（如有报告文件）

---

### Step 2：定位失败根因（15 分钟）

#### 2.1 使用决策树快速定位

```
门禁失败排查决策树:

失败发生在哪一层？
├─ L1 (commit)
│   ├─ lint 失败 → 查看错误信息 → 修复代码风格
│   ├─ typecheck 失败 → 查看类型错误 → 补充类型定义
│   └─ 单元测试失败 → 查看失败用例 → 修复逻辑或测试
│
├─ L2 (push)
│   ├─ 集成测试失败 → 检查集成环境 → 修复集成问题
│   ├─ 覆盖率不足 → 查看覆盖率报告 → 补充测试
│   └─ 构建失败 → 检查构建配置 → 修复构建脚本
│
├─ L3 (merge)
│   ├─ E2E 测试失败 → 查看 E2E 日志 → 修复端到端问题
│   ├─ 代码审查未通过 → 查看审查意见 → 修改代码
│   └─ 冲突未解决 → 拉取最新代码 → 解决冲突
│
└─ L4 (release)
    ├─ 安全漏洞 → 查看漏洞详情 → 升级依赖/修复代码
    ├─ 性能退化 → 查看性能对比 → 优化性能
    └─ 验收测试失败 → 查看验收标准 → 补全验收项
```

#### 2.2 使用调试命令

```bash
# 本地复现失败
npm run gate:commit --verbose
npm run gate:push --debug

# 运行单个检查
npm run lint --fix
npm run typecheck
npm run test:unit --verbose

# 运行单个守卫
node guards/api-contract-guard.mjs --debug
node guards/test-coverage-guard.mjs --verbose
```

#### 2.3 分析失败原因

常见失败原因分析：

| 失败类型 | 根因分析 | 检查方法 |
|---------|---------|---------|
| Lint 错误 | 代码风格不符合规范 | `npm run lint` |
| TypeCheck 错误 | 类型定义缺失或错误 | `npm run typecheck` |
| 单元测试失败 | 逻辑错误或测试过时 | `npm run test:unit --verbose` |
| 覆盖率不足 | 测试覆盖不完整 | `npm run test:coverage` |
| 守卫阻断 | 违反禁止规则 | 查看守卫报告 |
| 门禁超时 | 检查项过多或执行慢 | 查看执行时间日志 |

---

### Step 3：执行修复策略（15-30 分钟）

#### 3.1 L1 门禁失败修复

**Lint 错误修复**：

```bash
# 自动修复
npm run lint --fix

# 手动修复（如自动修复无法处理）
# 根据错误信息逐个修复
```

**TypeCheck 错误修复**：

```bash
# 查看详细错误
npm run typecheck -- --noEmit

# 常见修复方法：
# 1. 补充类型定义
# 2. 修复类型错误
# 3. 使用 @ts-ignore（谨慎使用）
```

**单元测试失败修复**：

```bash
# 运行失败测试
npm run test:unit -- --onlyFailures

# 查看失败原因
npm run test:unit -- --verbose

# 常见修复方法：
# 1. 修复业务逻辑
# 2. 更新测试用例（如需求变更）
# 3. Mock 外部依赖
```

#### 3.2 L2 门禁失败修复

**集成测试失败修复**：

```bash
# 运行集成测试
npm run test:integration --verbose

# 检查集成环境
# 1. 数据库连接
# 2. 外部服务可用性
# 3. 环境变量配置
```

**覆盖率不足修复**：

```bash
# 查看覆盖率报告
npm run test:coverage -- --open

# 补充测试
# 1. 找到覆盖率低的模块
# 2. 补充测试用例
# 3. 覆盖边界条件
```

**构建失败修复**：

```bash
# 查看构建错误
npm run build -- --debug

# 常见修复方法：
# 1. 检查依赖版本
# 2. 检查构建配置
# 3. 检查环境变量
```

#### 3.3 L3/L4 门禁失败修复

**E2E 测试失败修复**：

```bash
# 本地运行 E2E 测试
npm run test:e2e -- --headed

# 查看 E2E 日志
ls -lt e2e-results/

# 常见修复方法：
# 1. 修复前端组件
# 2. 修复 API 响应
# 3. 更新测试脚本
```

**安全漏洞修复**：

```bash
# 查看漏洞详情
npm audit

# 升级依赖
npm audit fix

# 手动升级（如 audit fix 无法处理）
npm install package@safe-version
```

#### 3.4 Guard 阻断处理

**禁止规则违反**：

```bash
# 查看阻断详情
cat reports/guard-*.json | jq '.results[] | select(.status == "BLOCK")'

# 修复方案：
# 方案 1：修复代码（推荐）
# 方案 2：申请白名单（有充分理由时）
```

**白名单申请流程**：

```yaml
白名单申请:
  步骤:
    1. 确认无法修复（或修复成本过高）
    2. 填写白名单配置:
       - id: WL-XXX
       - target: {匹配目标}
       - reason: {充分理由}
       - expires: {过期时间}
       - approved_by: {审批人}
    3. 提交 PR 说明
    4. 团队评审
    5. 合并后生效
  
  注意:
    - 白名单必须有期限
    - 白名单必须有审批人
    - 白名单必须定期审查
```

---

### Step 4：验证修复效果（10 分钟）

#### 4.1 本地验证

```bash
# 运行完整门禁流程
npm run gate:all

# 预期输出
[L1 Commit Gate]
  ✓ lint: passed (2s)
  ✓ typecheck: passed (3s)
  ✓ test:unit: passed (5s)

[L2 Push Gate]
  ✓ test:integration: passed (12s)
  ✓ test:coverage: 85% (threshold: 80%)
  ✓ build: passed (15s)

[Guards]
  ✓ api-contract-guard: PASS
  ✓ test-coverage-guard: PASS

[Result] ✓ PASSED
```

#### 4.2 CI 验证

```bash
# 提交修复
git add .
git commit -m "fix: resolve gate failure"
git push

# 观察 CI 执行
# 打开 PR 页面，查看 status checks
```

---

### Step 5：记录和预防（5 分钟）

#### 5.1 记录失败原因

创建 `docs/failure-log.md`：

```markdown
## 门禁失败记录

### 2025-08-13 14:30 - L1 Lint 失败

**失败原因**：使用了未声明的变量

**修复方法**：补充变量声明

**预防措施**：
- IDE 启用 lint 插件
- 提交前本地运行 `npm run lint`

**影响范围**：单次提交

**修复时间**：5 分钟
```

#### 5.2 更新团队文档

如果是常见失败，更新团队开发指南：

```markdown
## 开发流程

提交前检查清单：
- [ ] 运行 `npm run lint`
- [ ] 运行 `npm run typecheck`
- [ ] 运行 `npm run test:unit`
- [ ] 查看覆盖率报告
```

---

## 常见问题和解决方案

### Q1：Lint 错误过多，如何快速修复？

**方案**：

```bash
# 方式 1：自动修复
npm run lint --fix

# 方式 2：忽略特定规则（在 .eslintrc 中配置）
{
  "rules": {
    "no-console": "off"  // 允许 console
  }
}

# 方式 3：临时跳过（不推荐）
// eslint-disable-next-line
console.log('debug info');
```

### Q2：测试覆盖率不达标，如何快速提升？

**策略**：

```yaml
覆盖率提升策略:
  优先级排序:
    1. 核心业务逻辑（必须覆盖）
    2. 高频使用工具函数（重点覆盖）
    3. 边界条件（适度覆盖）
    4. 简单 getter/setter（可豁免）
  
  快速提升方法:
    - 参数化测试（减少重复代码）
    - Mock 外部依赖（聚焦内部逻辑）
    - 覆盖异常路径（提升分支覆盖率）
  
  避免方法:
    - 不写无意义测试（如只调用函数）
    - 不为测试而测试（为了覆盖率）
```

### Q3：守卫检查误报，如何处理？

**处理流程**：

```
1. 确认是否为误报
   - 检查规则是否适用当前场景
   - 检查是否在白名单中应豁免

2. 如确认误报：
   - 在 guard-config.json 中添加白名单
   - 填写豁免原因和期限
   - 提交 PR 说明

3. 如规则本身问题：
   - 提交 Issue 到 agent-dev-control-kit
   - 说明规则缺陷和改进建议
   - 参与规则优化讨论
```

### Q4：门禁超时，如何优化？

**优化方案**：

```yaml
性能优化:
  1. 拆分检查:
     - L1 只检查变更文件
     - L2 运行完整检查
  
  2. 并行执行:
     - 多个守卫并行运行
     - 测试用例并行执行
  
  3. 缓存结果:
     - 缓存 lint/typecheck 结果
     - 未变更文件跳过检查
  
  4. 增量检查:
     - 使用 git diff 识别变更
     - 只检查变更相关文件
```

### Q5：CI 环境失败，本地成功，如何排查？

**排查步骤**：

```
1. 环境差异排查:
   - Node 版本是否一致（检查 .nvmrc）
   - 依赖版本是否一致（检查 package-lock.json）
   - 环境变量是否一致（检查 .env.example）

2. 使用 Docker 复现:
   - 使用 CI 镜像本地运行
   - 确保环境一致性

3. 日志对比:
   - 对比本地和 CI 日志
   - 找到差异点

4. 网络问题排查:
   - CI 网络限制
   - 外部服务可达性
```

---

## 回退策略

### 紧急回退

当门禁失败严重影响开发进度时：

#### 方式 1：临时跳过（仅限紧急）

```bash
# 跳过 pre-commit
git commit --no-verify -m "emergency: critical hotfix"

# 跳过 pre-push
git push --no-verify
```

**要求**：
- PR 中必须说明跳过原因
- 24 小时内补充修复
- 记录在 failure-log.md 中

#### 方式 2：禁用特定守卫

编辑 `guard-config.json`：

```json
{
  "guards": [
    {
      "name": "test-coverage-guard",
      "enabled": false,  // 临时禁用
      "reason": "紧急发布，后续补充测试"
    }
  ]
}
```

**要求**：
- 必须设置 re-enable 时间
- 必须通知技术负责人
- 必须记录技术债务

#### 方式 3：申请白名单

针对特定文件或规则：

```json
{
  "whitelist": [
    {
      "id": "WL-EMERGENCY-001",
      "target": { "pattern": "emergency-file.js" },
      "reason": "紧急修复，后续重构",
      "expires": "2025-08-20",
      "approved_by": "tech-lead"
    }
  ]
}
```

---

## 预防措施

### 开发阶段预防

```yaml
IDE 配置:
  - 启用 ESLint 插件（实时提示）
  - 启用 TypeScript 检查
  - 配置保存时自动修复

提交前检查:
  - 运行 `npm run gate:commit`
  - 检查覆盖率报告
  - 查看变更文件

开发习惯:
  - 小步提交（减少失败影响范围）
  - 本地测试通过后再推送
  - 及时拉取最新代码（减少冲突）
```

### 团队层面预防

```yaml
团队规范:
  - 定期审查门禁规则（每月）
  - 维护失败日志（避免重复）
  - 分享排查经验（团队学习）

培训计划:
  - 新成员入职培训（包含门禁使用）
  - 定期复盘（分析失败模式）
  - 规则优化讨论（集体决策）
```

---

## 相关资源

- [Gate Skills 指南](../references/gate-skills-guide.md)
- [Guard Skills 指南](../references/guard-skills-guide.md)
- [实施路线图](../references/implementation-roadmap.md)

---

> **维护者**：agent-dev-control-kit
> **最后更新**：2025-08-13
> **版本**：1.0.0