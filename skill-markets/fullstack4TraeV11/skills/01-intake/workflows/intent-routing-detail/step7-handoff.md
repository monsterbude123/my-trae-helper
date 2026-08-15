# Step 7：交接下一 stage — intent-routing.md 详情

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 父文件：[../intent-routing.md](../intent-routing.md)
> 来源：原 intent-routing.md 第 265-279 行（保留信息密度）

---

## Step 7：交接下一 stage

```
[ ] state-card-validator.py PASS（状态卡字段完整 + 文件存在）
[ ] stage-gate.py PASS（路由切换确认）
[ ] next_stage 字段已填写
[ ] blocked_by = null
[ ] 主上下文向用户汇报："已路由到 {next_stage.skill_name}，预计 X 分钟"
```

**禁止**:
- ❌ 主上下文 Edit/Write 代码（Article IV）
- ❌ 跳过 stage-gate.py 直接交接
- ❌ 状态卡说谎（Article XII 文档诚实）

---

## 关联引用

- 父文件：[../intent-routing.md](../intent-routing.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
