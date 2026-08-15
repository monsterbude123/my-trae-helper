# Events: {change_id}

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 位置: `docs/specs/changes/{id}/contracts/events.md`

---

## Event 1: [Name]

```yaml
- event: {module}.{action}
  publisher: [service]
  subscriber: [service]
  trigger: [condition]
  schema:
    field1: type
    field2: type
  when: [publish on success | failure]
```

## 关联引用

- [domain-models.md](domain-models.md)
- [api-contracts.md](api-contracts.md)
