# 反例 2：修改归档文件（Stage 5 Accept）

> Stage 5 Accept 后归档不可变（V11 Article VIII + V10 Article VIII）。

## 现象

```
agent: 已 archive/done/{change-id}/ → 修改 spec.md 加一行  # ❌ 违反 Article VIII
```

## 根因

| 根因 | 占比 |
|------|:---:|
| 觉得"小修改不影响" | 60% |
| 不知道归档不可变 | 40% |

## 教训

**V11 Article VIII — Archive Immutable**（蒸馏自 V10）：
```
8.1 归档目录（docs/archive/done/）下文件禁止修改
8.2 归档只能新增，不可删除
8.3 修改归档 = 🛑 REJECT 流程违规
8.4 归档修改必新建 change 重新走流程
```

## 正确替代

```bash
# ❌ 反例
edit docs/specs/archive/done/{change-id}/spec.md  # 改归档

# ✅ 正确
# 如确需修改，必新建 change 走流程
python scripts/setup-feature.py --name {new-change-id}
# 把修改内容写到新 change 的 spec.md，再走 Plan → Spec → Contract ...
```

## 关联引用

- [SKILL.md §铁律 2](../SKILL.md) — 修改归档文件
- [archive-protocol.md](../references/archive-protocol.md) — 归档协议
- V11 Article VIII（铁律不可降级）
- V10 来源（已蒸馏）: 见 V11 references 与 anti-patterns（部署时不依赖）references/artifact-lifecycle.md`