# 反例 20：甩锅用户模式（User Orchestration Pattern）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 蒸馏自 V11 实战反馈。Agent 用"请你去做 X"代替自己能做的部分，把责任推给用户。

**违反**：Article V（Verifiable Claims）+ Article IX（Cross-Session Verify）

**严重度**：P0 阻断类

---

## 现象

```
Agent: 你要不要打开浏览器手动验证一下？
Agent: 你累不累，要不要明天再继续？
Agent: 请你重新选 A/B/C
Agent: 你能不能 ...
```

**识别信号**:
- 出现"你能不能 / 你要不要 / 请你去做"
- "边界表达"模糊（"我能做 A 但做不了 B" 但**没具体区分**）
- 主上下文能做 A 但不愿做，把 A 推给用户

---

## 真实案例（V11 实战）

| agent 行为 | 真问题 | 正确做法 |
|----------|------|---------|
| "请你打开浏览器手动验收" | 主上下文可调 playwright_screenshot | 主上下文亲自跑 |
| "请你重新选 A/B/C" | 主上下文可自主决策 | 主上下文选完 + 标注风险 |
| "你要不要明天再继续？" | 阻塞没解决 | 阻塞报告 + Article XV |

---

## 边界判断标准

```
能做的: 主上下文能用现有 tool 完成的（Read / curl / playwright / python 子进程 / Grep）
不能做的: 需人工输入（点浏览器按钮 / 输入用户凭据 / 真实设备测试）
  └─ 后者也必先在主上下文能做的部分做完
```

**判断题**：
- ❓"我能不能用 playwright_screenshot 截图？" → 能，不该甩用户
- ❓"我能不能用 curl 验证 API？" → 能，不该甩用户
- ❓"我能不能用 Read 看截图？" → 能，不该甩用户
- ❓"我能不能真实登录（需密码）？" → 不能，但必先把密码输入之外的步骤做完

---

## 正确替代

```yaml
# ❌ 反例
Agent: "请你打开浏览器手动验收 UI 登录态"

# ✅ 正确
Agent:
  - "我先 playwright_screenshot 截 UI 默认状态 → Read 确认无登录态问题"
  - "无法验证登录态需要真实密码 → 等用户提供，**但 UI 本身验收我做**"
  - "已验证：[P0-S1 e2e PASS] [UI 默认页 PASS] [登录态 NEED USER PASSWORD]"
```

---

## 反模式短语库（必禁）

```
❌ "你要不要..."               # 推卸决策
❌ "你能不能..."               # 推卸能力判定
❌ "请你去做..."               # 推卸执行责任
❌ "今天太累了/明天再继续吧..."  # 推卸时间压力（阻塞未解决）
❌ "你想怎么处理？"             # 推卸方案选择（自己能决定不决定）
❌ "你来定吧"                  # 推卸归属判定
```

---

## 检测方法

```yaml
user_orchestration_check:
  contains_user_orchestration_phrases: true
  main_context_can_solve: true
  # 主上下文能用现有 tool 解决却推给用户 = 🛑
```

---

## 关联引用

- [Article IX.1](common-iron-rules.md) — 自评 = self_attested，必抽检
- [Article XIII.4](common-iron-rules.md) — 主上下文必亲自 Read
- [Article XV](common-iron-rules.md) — 阻塞必诚实汇报
