# Agent 错误诊断手册（V11 — 5 模式根因 → 现有铁律映射）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> V11 实战反馈蒸馏。任何 agent 失败先查此手册，**避免重复创建新铁律**。
> 原则（Article XVI §1.4 重叠校验）：V11 现有 16 + 1 Articles + 22 反例已覆盖常见失败模式，新增铁律必先查此手册。

---

## 失败时必走的 4 步流程

```
Step 1: 失败模式归类（5 模式诊断）
Step 2: 查本文档的"模式 → 现有铁律"映射表
Step 3: 若现有铁律已含 → 不新增铁律，必反思已有铁律遵守
Step 4: 若现有铁律缺失 → 🛑 必新增 Article + 反例（不走 Article XVI §1.5 不重叠论证）
```

---

## 5 模式诊断（来自 V11 实战）

### 模式 1：盲信子代理产物

**症状**：接受子代理"已通过"报告，未亲自抽检

**真实根因**：Article IX.1 自评 = self_attested，必抽检（V11 **已含**）

**反例**：无（应有 P0 §19 循环 PASS 模式）

**修复方向**：不新增铁律，必反思 Article IX.1 遵守 + 反例库强化

---

### 模式 2：应付性汇报（自评 PASS 缺证据）

**症状**：自评 PASS 但实际无 evidence（"3 张截图"=3 张空白页）

**真实根因**：
- Article V.2 "已完成"必附证据（V11 **已含**）
- Article V.5-5.8 GitNexus 必走（V11 **已含**）
- Article XIII.4 主上下文必亲自 Read（V11 **已含**）

**反例**：P0 §2 编造证据

**修复方向**：不新增铁律，必反思 Article V/IX/XIII 遵守

---

### 模式 3：上下文击穿 + rule 长度

**症状**：rule > 200 行没读完 + 反复踩同一雷 + 自评 PASS

**真实根因**：
- Article XI vibe-coding-standards v2.5 弹性 100~350 行（V11 **已含**，2026-08-14 解除硬编码上限）
- 反例库 common-anti-patterns.md 没读（V11 **已含**）

**反例**：新增 P0 §21 未读 rule PASS

**修复方向**：
- 项目级：rule 拆分（>200 行必拆）
- 项目级：V11 §0.5 加载协议强化（必先列"我能踩的雷"）
- agent 必走：列"我能踩的雷" → 自评 PASS 前逐项核对自己

---

### 模式 4：甩锅用户

**症状**：用"你能不能 / 你要不要"代替自己能做的部分

**真实根因**：
- Article IX.1 自评必抽检（V11 **已含**）
- Article XIII.4 主上下文必亲自 Read（V11 **已含**）

**反例**：新增 P0 §20 甩锅用户模式

**修复方向**：
- 不新增铁律
- 必走 "边界判断标准"（主上下文能不能用现有 tool 完成？）

---

### 模式 5：安全事件（secret 进工具调用）

**症状**：用户提供的密码 / token 写到工具调用参数 → 工具调用日志 = 日志文件 = 明文泄露

**真实根因**：V11 16 Articles **完全缺失 secret 红化条款**（V11.1 已补） → 🛑 P0 缺失

**反例**：新增 P0 §22 secret-in-tool-arg

**修复方向**：
- **新增 Article XVII — Secret Redaction（6 条硬约束）**
- forbidden_paths 强制禁读 .env / secrets/ / credentials/
- audit log 模板必含 secret-incident-{date}.md

---

## 模式 → 现有铁律映射表

| 失败模式 | 现有铁律（含 V11）| 是否新增 |
|---------|-----------------|---------|
| 1 盲信子代理 | Article IX.1, IX.2, IX.3, IX.4 | ❌ 不新增，反思遵守 |
| 2 应付性 PASS | Article V.1-5.4, V.5-5.8, XIII.4 | ❌ 不新增，反思遵守 |
| 3 rule太长不读 | Article XI.1, XI.2 | ❌ 不新增，反思遵守 + 项目级拆分 |
| 4 甩锅用户 | Article IX.1, XIII.4 | ❌ 不新增，反思遵守 |
| 5 secret 泄露 | **缺失** | ✅ **新增 Article XVII + 反例 §22** |

**结论**：5 个模式中只有 1 个真正需新增（模式 5），其余 4 个是已含铁律的**遵守问题**，不是新增问题。

---

## 不冗余原则（Article XVI §1.4）

```
新增铁律必走:
  1. 现有 17 Articles + 23 反例是否已含？
  2. 反例库是否已含？
  3. 是否能用现有铁律 + 引用代替？
  4. 修复成本 vs 价值（避免低价值修复）

不通过任一检查 → 不新增
```

**反例（V11 实战）**：
- ❌ 反馈 5 个模式 = 5 个新铁律 → 冗余 80%（4 个已含）
- ✅ 反馈 5 个模式 → 1 个新铁律（Article XVII）+ 4 个反例强化

---

## 5 个新反例 vs 0 个新铁律（V11 应增）

| # | 反例 | 新铁律？ |
|---|------|---------|
| §19 | 循环 PASS 模式 | ❌ 已含 Article V/IX/XV |
| §20 | 甩锅用户模式 | ❌ 已含 Article IX/XIII |
| §21 | 未读 rule PASS | ❌ 已含 Article XI |
| §22 | secret 写入工具参数 | ✅ **新增 Article XVII**（17.1-17.6） |

**唯一新增铁律**：Article XVII — Secret Redaction（V11 安全空白填补）

---

## 主上下文失败后必走的反思清单

```yaml
# 失败后主上下文必填（不替代子代理报告）
self_reflection:
  round: N
  failure_mode: "{5 模式之一}"
  existing_iron_rule: "{Article X.X}"
  why_I_violated: "{具体证据 file:line}"
  preventive_action: "{下次怎么不同}"
  # 必填 4 个字段，禁止空话
```

---

## 关联引用

- [common-iron-rules.md](common-iron-rules.md) — 16 + 1 Articles
- [common-anti-patterns.md](common-anti-patterns.md) — 22 反例
- [Article XVI §1.4](common-iron-rules.md) — 修复成本 vs 价值校验
- V11 实战反馈（开发期）: 见 V11 references 与 anti-patterns（已蒸馏）
