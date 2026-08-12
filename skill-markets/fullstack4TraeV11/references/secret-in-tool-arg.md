# 反例 22：Secret 写入工具调用参数（Secret in Tool Argument）

> **V11 Article XVII — Secret Redaction（新增 P0 安全事件）**
> 蒸馏自 V11 实战反馈。Agent 把用户提供的密码 / token 写到工具调用参数 → 工具调用日志 = 日志文件 = 明文泄露。

**违反**：Article XVII（新增 P0 安全）

**严重度**：P0 阻断类

---

## 现象

```python
# ❌ 反例（V11 真实 P0 安全事件）
subagent.run(f"curl -X POST https://api.example.com/login -d '{{\"user\":\"alice\",\"password\":\"wo195271\"}}'")
# password 直接写在工具调用参数里 → tool log → 明文泄露
```

**识别信号**:
- 工具调用参数含 `password=` / `token=` / `api_key=` / `cookie=` / `secret=`
- shell / script 中 `echo $PASSWORD` / `print(token)`
- commit / 截图 / log 文件中出现 secret 字面量

---

## 真实案例（V11 实战）

| 事件 | 后果 |
|------|------|
| 用户贴出"测试可以用"的密码 | agent 没意识到工具调用参数 = 日志文件 = 明文泄露 |
| 写到 curl -d 参数 | 工具调用日志记录了 password 字面量 |
| 用户必须重置密码 | 🛑 P0 安全事件 |

---

## 根因诊断

| 根因 | 占比 |
|------|:---:|
| 没意识到"工具调用参数" = 日志文件 | 50% |
| 没意识到"测试用"也要按生产标准 | 30% |
| 没有 secret 红化硬约束（V11 Article XVII 缺失）| 20% |

---

## 正确替代

```bash
# ✅ 正确：环境变量 + shell 引用 + audit log redacted

# 1. 用户用环境变量注入
export MY_PASSWORD="wo195271"
export MY_TOKEN="sk-..."

# 2. agent 工具调用只用变量名
subagent.run("curl -X POST https://api.example.com/login -d '{\"user\":\"alice\",\"password\":\"$MY_PASSWORD\"}'")
# 参数里只有 $MY_PASSWORD 字符串，运行时由 shell 替换

# 3. audit log 中 redacted
# Tool log: "...password=[REDACTED:env:MY_PASSWORD]..."
```

```python
# ✅ Python
import os
password = os.environ["MY_PASSWORD"]  # 不写入日志
```

```typescript
// ✅ TypeScript / React
const password = process.env.REACT_APP_MY_PASSWORD!;
```

---

## forbidden_paths 强制

```yaml
# .trae/fullstack4traev11.config.yaml
forbidden_paths:
  - .env            # 环境变量文件
  - .env.local
  - .env.production
  - secrets/**
  - credentials/**
```

任何路径匹配 → **必禁读**（V11 Article XVII.3）。

---

## V11 Article XVII 6 条硬约束

```
17.1 用户提供的 secret → 必通过环境变量 / .env 注入，**绝不**写到工具调用参数里
17.2 工具调用参数中出现 secret → 🛑 REJECT + 立即通知用户改密码
17.3 .env / secrets/ / credentials/ → forbidden_paths 强制禁读
17.4 即使"测试用"的 secret 也不写到 commit / tool log / 截图
17.5 secret 误写 → 立即回滚 + 用户重置 + 写入 audit log
17.6 shell / script 中出现的 $PASSWORD / $TOKEN → 必用 ${VAR:-} 形式 + 在 audit log 中 redacted
```

---

## 检测方法

```yaml
secret_leak_check:
  tool_args_contain_literal_password: true
  shell_history_contains: ["password=", "token="]
  commit_diff_contains: ["password=", "api_key=", "token="]
  screenshot_text_ocr_contains: ["password=", "secret="]
```

任一触发 → 🛑 P0 安全事件 → 必回滚 + 通知用户 + audit log。

---

## audit log 模板

```yaml
# docs/audit-logs/secret-incident-{date}.md
---
incident_id: secret-2026-08-11-001
severity: P0
detected_at: 2026-08-11T15:30:00Z
reporter: agent / reviewer / user
secret_type: password
secret_scope: [REDACTED:env:VAR_NAME]
exposure_path: "tool call → tool log → shell history"
containment:
  - [REDACTED:env:VAR_NAME] invalidated: pending user rotation
  - git history purge: pending
  - user notification: 2026-08-11T15:32:00Z
preventive_measures:
  - [x] Article XVII.1 added to common-iron-rules.md
  - [x] secret-in-tool-arg anti-pattern documented
  - [x] forbidden_paths extended
```

---

## 关联引用

- [Article XVII](common-iron-rules.md) — V11 新增 P0 安全条款
- [V11 SKILL.md §0.5](../SKILL.md) — 加载后必读 Article XVII
- [forbidden_paths 配置示例](../templates/project-rules-example/paths.md)