# 40-acceptance / 验证门禁循环（Verification Loop）

> **定位**：验收阶段第二道门禁。命令行级别的自动化验证。
>
> **何时加载**：完成功能或重大代码变更后 / 创建 PR 前 / 重构后。

---

## 一、六阶段验证

### Phase 1: 构建验证

```bash
npm run build 2>&1 | tail -20
```

**构建失败 → STOP，立即修复。**

### Phase 2: 类型检查

```bash
npx tsc --noEmit 2>&1 | head -30
```

报告所有类型错误，修复关键错误。**禁止 `any` 类型绕过。**

### Phase 3: 代码规范检查

```bash
npm run lint 2>&1 | head -30
```

### Phase 4: 测试套件

```bash
npm run test:coverage 2>&1 | tail -50
```

报告：
- 总测试: X
- 通过: X
- 失败: X
- 覆盖率: X%（要求 > 80%，关键路径 100%）

**测试卡住时**：进入 `30-testing/test-partition-runner.md` 分区测试。

### Phase 5: 安全扫描

```bash
# 检查密钥泄露
grep -rn "sk-" --include="*.ts" --include="*.js" . 2>/dev/null | head -10
grep -rn "api_key" --include="*.ts" --include="*.js" . 2>/dev/null | head -10
grep -rn "password\s*=" --include="*.ts" --include="*.js" . 2>/dev/null | head -10

# 检查 console.log
grep -rn "console.log" --include="*.ts" --include="*.tsx" src/ 2>/dev/null | head -10
```

### Phase 6: Diff 审查

```bash
# 显示变更
git diff --stat
git diff HEAD~1 --name-only
```

审查每个变更文件：
- 非预期变更？
- 缺失错误处理？
- 潜在边界情况？
- 死代码清理？

---

## 二、输出格式

```
验证报告
==================

构建:     [通过/失败]
类型:     [通过/失败] (X 个错误)
规范:     [通过/失败] (X 个警告)
测试:     [通过/失败] (X/Y 通过, Z% 覆盖率)
安全:     [通过/失败] (X 个问题)
Diff:     [X 个文件变更]

总体:     [可以提交/不能提交]

待修复问题:
1. ...
2. ...
```

---

## 三、门禁标准

### 可以提交
- 构建通过
- 类型检查 0 错误
- Lint 0 error（warning 可接受）
- 测试 100% 通过，覆盖率 > 80%
- 安全扫描无 HIGH
- 死代码已清理

### 不能提交
- 上述任一不满足

---

## 四、持续模式

长时间会话中，每 15 分钟或重大变更后运行验证：

```markdown
设置检查点：
- 完成每个函数后
- 完成组件后
- 进入下一个任务前

运行: /verify
```

---

## 五、与 code-review 的协作

| 阶段 | 负责人 | 关注点 |
|------|--------|--------|
| code-review（清单审查） | fullstack-reviewer agent | 代码质量、安全、文档一致性（人 + AI 视角） |
| verification-loop（自动化验证） | fullstack-reviewer agent | 构建/类型/Lint/测试/安全扫描（机器视角） |

**两者都必须通过才能批准提交**。

---

## 六、与 Spec 的对齐

验证完成后，检查 Spec 状态：

- [ ] Spec §9 验收标准全部满足
- [ ] Spec 状态更新为 `implemented`
- [ ] `docs/specs/{编号}-{feature}/checklist.md` 全部勾选

详见 `00-product/spec-templates.md` 的 Spec 状态机。
