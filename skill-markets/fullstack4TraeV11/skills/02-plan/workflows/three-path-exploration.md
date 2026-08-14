# Three-Path Exploration — Stage 0 Plan

> Stage 0 Plan 必走。3 路径评估协议。

---

## 3 路径定义

| 路径 | 特征 | 适用 |
|------|------|------|
| **路径 A — 扩展现有** | 复用现有模块 + 新增 capability | 70% case |
| **路径 B — 新建模块** | 创建新模块/服务 | 20% case |
| **路径 C — 引入新依赖** | 引入新库/框架 | 10% case（需 Article XVI 校验）|

---

## 决策算法

```python
def evaluate_paths(requirements: list, existing_modules: list) -> str:
    """返回推荐路径"""

    # 路径 A: 现有模块能否覆盖
    coverage = sum(1 for req in requirements if any(
        module_covers(req, m) for m in existing_modules
    ))
    if coverage >= 0.7 * len(requirements):
        return "A"

    # 路径 C: 是否需要新依赖
    if requires_new_dependency(requirements):
        return "C"

    # 路径 B: 新建模块
    return "B"
```

---

## 决策矩阵

| 评估维度 | 路径 A | 路径 B | 路径 C |
|---------|:---:|:---:|:---:|
| 复用度 | 高 | 中 | 低 |
| 风险 | 低 | 中 | 高 |
| 实施时间 | 短 | 中 | 长 |
| 维护成本 | 低 | 中 | 高 |
| Article XVI 必走？| 否 | 否 | 是 |

---

## 输出格式

```yaml
plan_paths:
  A:
    name: "扩展现有 user 模块"
    capability_changes:
      - "user.add_email_verified"
      - "user.add_avatar_url"
    modules_affected: ["src/auth/user.py"]
    estimated_loc: 50
    risk: "LOW"
    rationale: "现有模块已含 80% 所需"
  B:
    name: "新建 user-profile 模块"
    capability_changes:
      - "user-profile.create / update / delete"
    modules_affected: ["src/user-profile/"]
    estimated_loc: 200
    risk: "MEDIUM"
    rationale: "现有 user 模块职责过重"
  C:
    name: "引入 Pillow 处理头像"
    capability_changes: []
    new_dependencies: ["Pillow>=10.0"]
    risk: "HIGH"
    rationale: "需 L0/L1 硬编码治理"
  decision:
    selected: "A"
    rationale: "复用度最高 + 风险最低"
```

---

## 反例

### 反例 A：跳路径评估直接选 A

```
planner: 立即选 A → 实现  # ❌ 错过 B/C 更优解
正确: 必走 3 路径评估
```

### 反例 B：路径 C 未走 Article XVI

```
planner: 选 C 引入新依赖 → 不论证  # ❌ rot #15
正确: 路径 C 必走 Article XVI 4 维度
```

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [constitution.md](../../../references/constitution.md) — Article XVI
- [stage-interaction-protocol.md](../../../references/stage-interaction-protocol.md)