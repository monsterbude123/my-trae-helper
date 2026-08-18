# 反例 19：循环 PASS 模式（Loop PASS Pattern）

> **V12.0.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> 蒸馏自 V10.12 + V11 实战反馈。Agent 反复"我搞错了"+重新委派，无具体改进。

**违反**：Article V（Verifiable Claims）+ Article IX（Cross-Session Verify）+ Article XV.4（禁止抽象理由）

**严重度**：P0 阻断类

---

## 现象

```
Round 1: 我搞错了，应该先 ...
Round 2: 我搞错了，应该 ...
Round 3: 我搞错了，应该 ...
...
```

**识别信号**:
- 连续 ≥ 3 轮"我搞错了"开头
- 每轮"具体改进" = 重做上一轮 + 同种子代理
- 错误模式重复出现（如"忘记 Read 截图"反复出现）
- 自评 PASS 后下一轮又被相同证据打脸

---

## 真实案例（V11 实战）

| 轮次 | 现象 | 真实根因 |
|-----|------|---------|
| Round 1 | 子代理报告"主上下文亲自 Read 通过" → 主上下文未 Read | 接受子代理报告 |
| Round 2 | "我搞错了，应该重新 Read" → 仍接受子代理报告 | 未变 |
| Round 3 | "我又搞错了" → 重新委派同一子代理 | 未变 |

**6 轮循环 + 每次"具体改进" = 重新委派 = 0 价值进步**。

---

## 根因诊断（5 模式）

| 根因 | 占比 |
|------|:---:|
| 没读过 rule | 50%（未执行 Article V.1 自检）|
| 把"自评"当"实测" | 30%（未执行 Article IX.1 抽检）|
| 应付性汇报（应付焦虑）| 15% |
| 真不知怎么抽检（缺方法论）| 5% |

---

## 正确替代

```yaml
# ✅ 正确做法：循环 ≤ 2 轮 + 必给具体证据

第 N 轮必含:
  1. 上一轮错在哪（file:line + 具体证据）
  2. 这次不同在哪（具体新动作）
  3. 这轮完成后主上下文亲自 [Read / curl / playwright_screenshot] 验证

第 3 轮若仍 FAIL → 🛑 必升级用户决策（不是第 4 次重新委派）
```

---

## 终止条件

| 情况 | 处置 |
|------|------|
| 同模式失败 ≥ 3 轮 | 🛑 REJECT + 升级用户决策 |
| 自评 PASS 后下一轮被打脸 ≥ 2 次 | 🛑 REJECT（self-attest 失信）|
| 出现"我错了"但无具体证据 | 🛑 REJECT（应付性汇报）|

---

## 检测方法

```yaml
loop_pass_check:
  rounds_passed_to_fail: ≥ 3  # 3 轮以上自评 PASS 后失败
  identical_pattern_count: ≥ 3  # 同一错误模式重复 ≥ 3 次
  evidence_quality: "low"  # 证据为"我看过了"无 file:line
```

任一触发 → 立即触发本反例 → 必走升级流程。

---

## 关联引用

- [Article V](common-iron-rules.md) — 5.1 每个主张必附事实证据
- [Article IX](common-iron-rules.md) — 9.1 自评必抽检
- [Article XV](common-iron-rules.md) — 15.4 禁止抽象理由
- [agent-error-diagnosis.md](agent-error-diagnosis.md) — 错误诊断手册
