
> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)

---
bug_id: {{bug_id}}
layer: fact
status: OPEN
created_at: {{created_at}}
created_by: 主上下文
---

# Bug 单: {{bug_id}}

## 1. 症状（Symptom）

{{symptom}}

> 例: "并发刷新 token 时报 500 错误"

## 2. 期望（Expected）

{{expected}}

> 例: "并发刷新应正常返回新 token，无 500"

## 3. 复现步骤（Reproduction Steps）

{{reproduction_steps}}

> 例:
> 1. 打开浏览器 A 登录同一账号
> 2. 打开浏览器 B 登录同一账号
> 3. 在 A 中点击刷新 token
> 4. 同步在 B 中点击刷新 token
> 5. A 或 B 出现 500

## 4. 影响范围（Impact）

- **模块**: {{module}}
- **严重度**: {{severity}}（P0 / P1 / P2）
- **影响用户**: {{affected_users}}
- **影响功能**: {{affected_features}}

## 5. 环境信息（Environment）

{{environment}}

> 例:
> - OS: macOS 14.5
> - 浏览器: Chrome 126
> - 前端: Tauri 2.0 + React 18
> - 后端: Python 3.11 + FastAPI 0.111
> - 部署: dev 模式

## 6. 触发词（Trigger Phrase）

{{trigger_phrase}}

> 例: "期望 X 但实际 Y"

## 7. 元数据

- **录入 stage**: -1/intake
- **录入人**: 主上下文
- **录入时间**: {{created_at}}
- **关联 change**: {{related_change}}（如适用）
- **关联 commits**: {{related_commits}}（如适用）

## 8. Stage 6 处理记录（debugger 填写）

### 8.1 e2e 先行验证

```
测试文件: {{e2e_test_file}}
初始状态: ❌ FAIL（必填，证明 bug 真实存在）
时间: {{e2e_verified_at}}
```

### 8.2 6 层排查

```
[ ] 网络层: ...
[ ] 接入层: ...
[ ] 应用层: ...
[ ] 数据层: ...
[ ] 集成层: ...
[ ] 客户端层: ...
```

### 8.3 根因分析

```
根因: {{root_cause}}
影响面: {{impact_scope}}
修复策略: {{fix_strategy}}
```

### 8.4 TDD 修复

```
RED:   {{red_test}}
GREEN: {{green_impl}}
REFACTOR: {{refactor_changes}}
```

### 8.5 回归验证

```
全量测试: {{regression_test_result}}
用户验收: {{user_acceptance}}
```

## 9. 关闭记录

- **关闭时间**: {{closed_at}}
- **关闭人**: {{closed_by}}
- **关闭方式**: {{close_method}}（e2e PASS + 回归 PASS + 用户签字）

---

## 关联引用

- [bug-state-machine.md](../references/bug-state-machine.md) — Bug 单状态机
- [bug-intake-flow.md](../workflows/bug-intake-flow.md) — Bug 录入工作流
- Stage 6 Bug Fix: [../../12-bug-fix/SKILL.md](../../12-bug-fix/SKILL.md)
- 状态卡路径: `docs/bugs/{{bug_id}}/.state-card.md`
