# 反例 21：未读 rule 就自评 PASS（Unread Rule PASS Pattern）

> 蒸馏自 V11 实战反馈。rule 太长没读完 + 反复踩同一雷 + 自评 PASS。

**违反**：Article V（Verifiable Claims）+ Article XI（Self-Contained Constraints）

**严重度**：P0 阻断类

---

## 现象

```
Agent: "rule 太长我没读完"
Agent: "我又踩了 P6-09 Google CDP 那个雷"
Agent: 自评 PASS（实际 PASS 状态待核实）
```

**识别信号**:
- 出现"rule 太长"作为**不读规则的理由**
- 同一具体规则编号 ≥ 2 次踩雷（如"Google 拦截 CDP" 反复）
- 自评 PASS 不知道 PASS 在哪个证据

---

## 真实案例（V11 实战）

| 文件 | 行数 | agent 行为 |
|------|:---:|----------|
| AGENTS.md | ~120 | ❌ 没读完 |
| governance.md §P0-P6 | ~200 | ⚠️ 部分读 + 没逐项核对 |
| V11 SKILL.md + 16 Articles | 数千 | ❌ 关键章节读了，没通读 |

**反复踩雷记录**:
- P6-09 "Google 拦截 CDP" → 第 N 次踩
- P6-05 "mock 函数透传 props" → 第 N 次踩
- P6-07 "PowerShell curl 转义" → 第 N 次踩

---

## 根因诊断

| 根因 | 占比 |
|------|:---:|
| Article XI ≤150 行约束被破坏（rule 真太长）| 30% |
| Agent 没强制读完（V11 §0.5 加载协议未严格）| 50% |
| rule 内有反例但未读反例库（common-anti-patterns.md）| 20% |

---

## 正确替代

```yaml
# ✅ 正确流程（V11 §0.5 加载协议强化）

加载 skill 后必走:
  Step 1: 读 SKILL.md frontmatter（stage_config + depends_on）
  Step 2: 读 references/common-iron-rules.md 16 Articles 索引
  Step 3: 读当前 stage 的 SKILL.md §铁律
  Step 4: 读当前 stage 的 anti-patterns/ 全部反例
  Step 5: 列出"我能踩的具体雷"（每条 article + 反例编号）
  Step 6: 在自评 PASS 前逐项核对自己行为

# 跑 ≥1 个反例 → 🛑 PASS
# 跑 ≥3 个反例 → 🛑 PASS（不是 PASS 反例越多越好，是说明没吸收）
```

---

## 关键约束（V11 应有但项目违反）

```
❌ 反例：rule > 200 行未拆分 → Article XI.2 违反（≤150 行/文件）
❌ 反例：加载后没列"我能踩的雷"清单 → V11 §0.5 违反
❌ 反例：同规则反复踩 → Article V.2 违反（"已完成"无证据）
```

---

## 修复路径（项目级）

1. **拆分 rule**：> 200 行的 governance 拆成 P0.md / P1.md / ...
2. **加入 backstop**：主上下文在自评 PASS 前 List-String / Get-Content 实测一遍
3. **规则目录化**：把"我能踩的雷"做成 checklist，每次 stage 必走

---

## 检测方法

```yaml
unread_rule_check:
  rule_count_total: ≥ 50 条
  rule_count_read: < 50%  # 读过不到一半 → 风险
  same_rule_violated_repeatedly: ≥ 2 次
  self_pass_with_no_evidence: true
```

任一触发 → 立即触发本反例 → 必先回滚 + 通读 rule + 重做。

---

## 关联引用

- [V11 SKILL.md §0.5 加载协议](../SKILL.md) — 加载后必读清单
- [Article XI](common-iron-rules.md) — ≤10 铁律 + ≤150 行
- [Article V.2](common-iron-rules.md) — "已完成"必附证据