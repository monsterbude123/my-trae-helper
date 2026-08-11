# 归档不可变协议（Archive Protocol）

> Stage 5 Accept Step 1+3 必走。V10 Article VIII + artifact-lifecycle.md 蒸馏。

---

## spec-purge.py 流程

```bash
# Dry-run 验证
python ../../scripts/spec-purge.py --change-id {id} --dry-run

# 实际归档
python ../../scripts/spec-purge.py --change-id {id}

# 输出：
# - _invalidated/{timestamp}-{change-id}/ 隔离旧产物
# - archive/done/{change-id}/ 归档当前 change
```

## 归档目录结构

```
docs/archive/done/{change-id}/
├── plan.md
├── spec.md
├── contracts/
│   ├── domain-models.md
│   ├── api-contracts.md
│   ├── events.md
│   └── validation-rules.md
├── review-report.md
├── rot-scan-{date}.md
└── verify-report.md
```

## 归档不可变铁律（Article VIII）

- 归档目录下文件禁止修改
- 归档目录不可删除（除非显式豁免）
- 修改归档 = 🛑 REJECT 流程违规

---

## 反例

### 反例 A：跳过 spec-purge 直接归档

```
主上下文: review PASS → 直接 mv 到 archive/  # ❌
正确: spec-purge.py 隔离 _invalidated/ → archive/done/
```

### 反例 B：修改归档

```
主上下文: "归档里有错" → Edit archive/done/{id}/spec.md  # ❌
正确: 新建 change → 从归档复制起点 → 重新走流程
```

---

## 关联引用

- [SKILL.md §铁律 1](../SKILL.md)
- [knowledge-extract.md](knowledge-extract.md)
- V10 artifact-lifecycle.md: `V10 来源` (已蒸馏到本文档)
