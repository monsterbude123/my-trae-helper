# 反例 1：跳过知识沉淀直接归档（Stage 5 Accept）

> Stage 5 Accept Step 必走：**先知识沉淀，再归档**。来源：V10 references/prd-integration-workflow.md + agents/spec-knowledge-extract.py。

## 现象

```
agent: Stage 4 Review PASS → 直接 archive/done/  # ❌ 跳了 spec-knowledge-extract
```

## 根因

| 根因 | 占比 |
|------|:---:|
| 觉得"完成了就 OK" | 50% |
| 不知道 spec-knowledge-extract.py | 30% |
| 嫌耗时 | 20% |

## 教训

**知识沉淀 → 归档 顺序不可颠倒**：
1. 跑 spec-knowledge-extract.py → 提取可复用经验到 `docs/knowledge/` 或 docs/modules/
2. 才进 archive/done/

**跳过后果**：
- 团队重复踩同一坑
- spec-purge 后经验丢失
- 后人无法理解设计权衡

## 正确替代

```bash
# ✅ V10 spec-knowledge-extract.py
python scripts/spec-knowledge-extract.py --change {change-id}
# 输出: docs/knowledge/{change-id}-lessons.md + docs/modules/{module}.md 更新

# 然后才归档
mv docs/specs/changes/{change-id}/ docs/specs/archive/done/{change-id}/
```

## 关联引用

- [SKILL.md §铁律 1](../SKILL.md) — 知识沉淀先于归档
- [knowledge-extract.md](../references/knowledge-extract.md) — 知识提取协议
- V10 来源（已蒸馏）: 见 V11 references 与 anti-patterns（部署时不依赖）references/prd-integration-workflow.md`