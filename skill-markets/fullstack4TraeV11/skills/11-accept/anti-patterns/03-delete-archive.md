# 反例 3：删归档目录（Stage 5 Accept）

> Stage 5 Accept 后归档目录不可删除。来源：V11 Article VIII + V10 反例 §3。

## 现象

```
agent: archive/done/{change-id}/ 占用空间 → 直接 rmtree  # ❌ 违反 Article VIII + 破坏可追溯性
```

## 根因

| 根因 | 占比 |
|------|:---:|
| 觉得归档占空间 | 50% |
| 不知道归档不可删 | 50% |

## 教训

**V11 Article VIII.2**：归档只能新增，不可删除。

**后果**：
- 失去可追溯性（违反 Article VIII 永不可降级）
- 破坏 git history 对应关系
- 后续 reviewer 无法对照历史

## 正确替代

```bash
# ❌ 反例
rmtree docs/specs/archive/done/{change-id}/
git rm -r docs/specs/archive/done/{change-id}/

# ✅ 正确：归档目录永不删
# 如需清理 → 走 spec-purge（移到 archive/out/spec-purge/）而非删
python scripts/spec-purge.py --feature {change-id}
# 把过期的 spec 移到 archive/out/spec-purge/，但 archive/done/ 永不动
```

## 关联引用

- [SKILL.md §铁律 3](../SKILL.md) — 删归档目录
- [archive-protocol.md](../references/archive-protocol.md) — 归档协议
- V11 Article VIII（铁律不可降级）
- V10 来源（已蒸馏）: 见 V11 references 与 anti-patterns（部署时不依赖）references/artifact-lifecycle.md`