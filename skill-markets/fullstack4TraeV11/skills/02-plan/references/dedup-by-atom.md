# 原子级去重（DEDUP BY ATOM）

> Stage 0 Plan Step 2 必走。需求去重在原子级，避免功能重复实施。

---

## 核心理念

```
需求 → 拆解为原子能力 → 原子级对比 → 合并 / 新建
```

不是按"功能名"对比（如"用户认证" vs "用户登录"），而是按"原子能力"对比（如"密码哈希" + "Token 签发" vs "OAuth 回调处理"）。

---

## 去重流程

```
Step 1: 收集待去重需求（当前 change + 历史 change）
  ├─ 当前: docs/specs/changes/{current-id}/intent.md 或用户原话
  ├─ 历史: docs/specs/changes/{prev-id}/plan.md（活跃）
  └─ 归档: docs/archive/done/{prev-id}/plan.md

Step 2: 拆解为原子能力
  ├─ 读取每个需求的 Capabilities 列表
  ├─ 把每个 Capability 拆成原子（如"用户登录" → "密码校验" + "Token 签发" + "会话管理"）
  └─ 输出: 原子能力清单

Step 3: 原子级对比
  ├─ 计算当前需求原子集合 A
  ├─ 计算历史需求原子集合 B（每个历史需求）
  ├─ 重叠度 = |A ∩ B| / |A|
  └─ 阈值判断:
      ├─ > 50% → 建议合并
      ├─ 30-50% → 标注 + 询问用户
      └─ < 30% → 新建

Step 4: 输出决策
  ├─ 合并: 引用历史 change，扩展 Capabilities
  ├─ 新建: 创建新 change-id
  └─ 部分合并: 拆分原子，部分合并部分新建
```

---

## 重叠度算法

```
overlap = matched_atoms / total_atoms_of_new_requirement

示例:
  历史 Capabilities: [密码哈希, Token 签发, 会话管理, OAuth 回调]
  当前 Capabilities: [密码哈希, Token 签发, 验证码]

  matched_atoms = 2 (密码哈希, Token 签发)
  total_atoms = 3 (当前需求)

  overlap = 2/3 = 66.7% > 50% → 建议合并
```

---

## 决策矩阵

| 重叠度 | 处置 | 用户确认 |
|:---:|------|:---:|
| **> 50%** | 合并到历史 change | 🛑 必问 |
| **30-50%** | 部分合并（拆分原子） | 🛑 必问 |
| **< 30%** | 新建独立 change | ⚙ 可省 |
| **= 0%** | 全新功能，直接新建 | ⚙ 可省 |

---

## 合并 vs 新建 决策树

```
重叠度 > 50%?
  ├─ 是 → 历史 change 还在 active?
  │   ├─ 是 → 合并（用户确认）
  │   └─ 否 → 复活历史 change 或新建（询问用户）
  └─ 否 → 重叠度 > 30%?
      ├─ 是 → 拆分原子，部分合并部分新建（用户确认）
      └─ 否 → 新建独立 change
```

---

## 实施步骤

```python
# 主上下文亲自执行（不委派）
import os
import json

def scan_active_changes():
    changes_dir = "docs/specs/changes"
    return [d for d in os.listdir(changes_dir)
            if os.path.isdir(f"{changes_dir}/{d}")
            and not d.startswith(".")
            and d != "archive"]

def scan_done_changes():
    done_dir = "docs/archive/done"
    if not os.path.exists(done_dir):
        return []
    return [d for d in os.listdir(done_dir) if os.path.isdir(f"{done_dir}/{d}")]

def read_capabilities(change_path):
    plan_path = f"{change_path}/plan.md"
    if not os.path.exists(plan_path):
        return []
    # 解析 plan.md 中的 Capabilities 列表
    # ...（实现略）
    return capabilities

def dedup_by_atom(new_capabilities, history_changes):
    for hist in history_changes:
        hist_caps = read_capabilities(hist["path"])
        overlap = calculate_overlap(new_capabilities, hist_caps)
        if overlap > 0.5:
            return {"action": "merge", "target": hist, "overlap": overlap}
        elif overlap > 0.3:
            return {"action": "partial_merge", "target": hist, "overlap": overlap}
    return {"action": "new", "overlap": 0}
```

---

## 反例

### 反例 A：按功能名对比（粒度太粗）

```
历史: "用户认证"
当前: "用户登录"
判定: "功能不同" → 新建  # ❌ 实际有大量重叠原子
正确: 拆解为原子 → 密码哈希/Token 签发等 → 计算重叠度
```

### 反例 B：跳过归档扫描

```
扫描: docs/specs/changes/ 活跃子目录  # ❌ 漏了 archive/done/
正确: 同时扫描 docs/archive/done/
```

### 反例 C：合并时未保留历史 plan

```
合并后: 历史 plan.md 被覆盖  # ❌ 丢失历史 evidence
正确: 合并到历史 plan.md（追加 Capabilities，不删历史）
```

---

## 关联引用

- [SKILL.md §铁律 4](../SKILL.md) — DEDUP BY ATOM
- [README.md §完整骨架 Step 2](../README.md) — 去重检查
- [impact-assessment.md](impact-assessment.md) — 影响面评估（去重后做 impact）
- 公共铁律 Article VI Ponytail First: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
