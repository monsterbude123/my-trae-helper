# Step 1：加载 Skill — intent-routing.md 详情

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
   - references: [9 个公共 references]
   - scripts: [stage-gate.py, state-card-validator.py]
3. 加载 9 个公共 references（来自编排器 §0.5）
```

**校验**:
- 编排器 stage_config.intake.skills 必须为空 → ✅
- 编排器 stage_config.intake.stages 必须为空 → ✅

---

## 关联引用

- 父文件：[../intent-routing.md](../intent-routing.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
