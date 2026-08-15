# 反例 — README.md 详情

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 父文件：[../README.md](../README.md)
> 来源：原 README.md 第 107-148 行（保留信息密度）

---

## 完整反例（4 条）

### 反例 1：无探索直接规划

**现象**: 收到需求立即写 plan.md，不做任何探索。

**根因**: 觉得"用户说啥就是啥"，不假思索。

**教训**: 跳过探索 = 凭空设计 = 后续多次返工。

**正确替代**: Step 3 必走 3 路并行子代理探索。

### 反例 2：GitNexus 可用却用 grep

**现象**: 手动 grep 找代码影响面，忽略 GitNexus MCP 工具。

**根因**: 不熟悉 GitNexus / 觉得 grep 更快。

**教训**: 违反 Article V（GitNexus First）+ 影响面评估不准。

**正确替代**: 使用 GitNexus impact({target}) / context({target}) / query({concept})。

### 反例 3：重构不 purge

**现象**: 用户说"重构 X"，主上下文直接覆盖旧产物。

**根因**: 不知道重构场景需要先 spec-purge。

**教训**: 旧产物污染 + 后续 spec.md 漂移 + 归档不可追溯。

**正确替代**: Step 4 必走 spec-purge.py → 清除旧产物 → 重新探索。

### 反例 4：plan.md 超长

**现象**: plan.md 写到 200+ 行，Capabilities 写到 10+ 项。

**根因**: 把所有细节都塞进 plan.md，不区分规划 vs 实施。

**教训**: plan.md 是规划不是实施，超长 = Stage 1 Spec 失去输入价值。

**正确替代**: plan.md ≤ 80 行 + Capabilities ≤ 5 项 + 细节留给 Stage 1 Spec。

---

## 关联引用

- 父文件：[../README.md](../README.md)
- SKILL.md：[../SKILL.md](../SKILL.md)
