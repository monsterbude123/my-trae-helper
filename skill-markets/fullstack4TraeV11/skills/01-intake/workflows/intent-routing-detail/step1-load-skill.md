# Step 1：加载 Skill — intent-routing.md 详情

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 父文件：[../intent-routing.md](../intent-routing.md)
> 来源：原 intent-routing.md 第 35-52 行（保留信息密度）

---

## Step 1：加载 Skill

```python
# 主上下文必走
1. Skill 工具加载 skills/01-intake/SKILL.md
2. 解析 depends_on:
   - skills: []（自身是入口，无外部依赖）
   - stages: []（无前置 stage）
   - references: [4 个 stage 强依赖 references,见 SKILL.md frontmatter]
   - scripts: [stage-gate.py, state-card-validator.py]
3. 按需加载公共 references（来自编排器 §0.5,stage 强依赖已在 frontmatter 声明）
```

**校验**:
- 编排器 stage_config.intake.skills 必须为空 → ✅
- 编排器 stage_config.intake.stages 必须为空 → ✅

---

## 关联引用

- 父文件：[../intent-routing.md](../intent-routing.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
