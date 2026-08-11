# Plan Template — Stage 0 Plan

> 位置: `docs/specs/changes/{id}/plan.md`

---

```yaml
# Plan: {change-id}

## 1. 概述

{一句话描述 + 关键决策}

## 2. Capabilities (CAP)

### CAP-1: {能力}
  description: "{做什么}"
  satisfies: [AC-1, AC-2]
  modules: [src/auth/login.py, src/auth/token.py]

### CAP-2: {能力}
  ...

## 3. Non-Goals (NG)

- NG-1: {明确不做}
- NG-2: {明确不做}

## 4. 3 路径评估

### 路径 A: 扩展现有
  候选模块: {existing modules}
  复用度: 70%
  风险: LOW
  estimated_loc: 50

### 路径 B: 新建模块
  新模块: {new_module}
  风险: MEDIUM
  estimated_loc: 200

### 路径 C: 引入新依赖
  候选依赖: {lib1, lib2}
  风险: HIGH
  article_xvi_checked: true

### 决策
  selected: "A"
  rationale: "{复用度最高}"

## 5. 任务列表 (Tasks)

### Phase 1: 基础设施
- [ ] T-1: {task}
- [ ] T-2: {task}

### Phase 2: 核心实现
- [ ] T-3: {task}

### Phase 3: 测试
- [ ] T-4: {test_task}

## 6. 风险与依赖

| 风险 | 缓解 |
|------|------|
| {risk1} | {mitigation1} |

## 7. 回退计划

{如果实施失败的回退步骤}

## 8. 验收标准

{与 spec.md AC 对应 + 量化指标}
```

---

## 关联引用

- [Stage 0 Plan](../skills/02-plan/SKILL.md)
- [three-path-exploration.md](../skills/02-plan/workflows/three-path-exploration.md)
- [document-layer.md](../document-layer.md)