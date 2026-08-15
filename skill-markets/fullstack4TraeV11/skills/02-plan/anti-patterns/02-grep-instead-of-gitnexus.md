# 反例 2：GitNexus 可用却用 grep

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 违反 Article V GitNexus First。手动 grep 找影响面。

## 现象

```
主上下文 / Sub-agent: grep -r "authenticate" src/  # ❌ 违反铁律
```

**识别信号**:
- code_summary.json 含 "grep" 命令而非 gitnexus MCP 调用
- plan.md Impact 段无 risk_level 标注
- 委派 prompt 含 `grep` 字样

## 根因

| 根因 | 占比 |
|------|:---:|
| 不熟悉 GitNexus MCP | 50% |
| 觉得 grep 更快 | 30% |
| 不知道 Article V | 20% |

## 教训

**GitNexus 可用却用 grep = 影响面评估不准 + 违反 Article V 不可降级。**

真实案例:
- 主上下文用 grep 找 UserService.authenticate 调用者 → 找到 12 处
- GitNexus impact() → 找到 28 处（含间接调用）
- 实际影响范围被低估 → 实施时遗漏 16 处测试

## 正确替代

```python
# ✅ 使用 GitNexus MCP
mcp__gitnexus__impact(target="UserService.authenticate", direction="upstream")
mcp__gitnexus__context(name="UserService.authenticate")
mcp__gitnexus__query(query="user authentication")
mcp__gitnexus__detect_changes(scope="compare", base_ref="main")
```

**MUST**: 使用 GitNexus MCP 工具（impact / context / query / detect_changes）。

**NEVER**: 手动 grep / rg / codeseach 替代 GitNexus。

**例外**: GitNexus 不可用（L4 异常）→ 降级 + 标注风险 + 汇报用户。

## 检测方法

```yaml
checklist:
  - [ ] code_summary.json 含 gitnexus_calls 数组？
  - [ ] gitnexus_calls 含至少 4 个不同工具调用？
  - [ ] code_summary.json 无 grep / rg 命令痕迹？
```

任一未勾选 → 触发本反例 → 重跑 Sub-agent B 用 GitNexus。

## 关联引用

- [SKILL.md §铁律 3](../SKILL.md) — IMPACT BY TOOL
- [impact-assessment.md](../references/impact-assessment.md) — 影响面评估
- 公共铁律 Article V: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
