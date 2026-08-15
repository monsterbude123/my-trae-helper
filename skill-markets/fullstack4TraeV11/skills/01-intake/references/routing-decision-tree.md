# 路由决策树

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage -1 Intake Step 5 路由决策的完整决策树。从用户输入到路由目标的完整映射。

---

## 决策树（ASCII）

```
[用户输入]
  │
  ├─ 触发词命中？
  │   │
  │   ├─ "初始化" / "新项目" / "0→1"
  │   │   └─→ [project-init] → Stage 0 Plan
  │   │
  │   ├─ "新需求" / "新增" / "加个"
  │   │   └─→ [change-start: feature] → Stage 0 Plan
  │   │
  │   ├─ "重构" / "改造" / "重新设计"
  │   │   └─→ [change-start: refactor] → Stage 0 Plan
  │   │
  │   ├─ "文档同步" / "更新文档"
  │   │   └─→ [change-start: doc-sync] → Stage 1 Spec 或 Stage 5 Accept (lite)
  │   │
  │   ├─ "报错" / "错误" / "异常" / "不工作" / "失败" / "崩溃"
  │   │   └─→ [询问 bug 录入] → 用户同意? 
  │   │       ├─ 是 → [bug-fix] → Stage 6 Bug Fix
  │   │       └─ 否 → [一般咨询] → Stage 7 Project Health（异步）
  │   │
  │   ├─ "应该 X 但 Y" / "期望 X 但实际 Y"
  │   │   └─→ [询问 bug 录入] → 同上
  │   │
  │   ├─ "自检" / "健康度" / "诊断"
  │   │   └─→ [project-health] → Stage 7 Project Health（异步）
  │   │
  │   └─ 无触发词命中
  │       └─→ [AskUserQuestion] → 用户选 → 同上分支
  │
  └─ [最终路由] → 状态卡 next_stage 字段
```

---

## 路由决策矩阵

| 输入模式 | 触发词 | 询问 | 路由目标 | 状态卡 |
|---------|--------|------|---------|--------|
| 关键词直连 | "初始化"/"新项目"/"0→1" | 不需要 | Stage 0 Plan | project |
| 关键词直连 | "新增"/"加个 X" | 不需要 | Stage 0 Plan | change |
| 关键词直连 | "重构"/"改造" | 不需要 | Stage 0 Plan | change |
| 关键词直连 | "文档同步" | 不需要 | Stage 1 Spec 或 Stage 5 Accept | change |
| 关键词直连 | "报错"/"错误"/"异常" | **必问** | Stage 6 Bug Fix（同意）/ Stage 7（拒绝）| bug / project |
| 关键词直连 | "不工作"/"失败"/"崩溃" | **必问** | Stage 6 Bug Fix（同意）/ Stage 7（拒绝）| bug / project |
| 关键词直连 | "应该 X 但 Y" | **必问** | Stage 6 Bug Fix（同意）/ Stage 7（拒绝）| bug / project |
| 关键词直连 | "期望 X 但实际 Y" | **必问** | Stage 6 Bug Fix（同意）/ Stage 7（拒绝）| bug / project |
| 关键词直连 | "自检"/"健康度" | 不需要 | Stage 7 Project Health（异步）| project |
| 模糊输入 | 无触发词 | **必问** | AskUserQuestion 5 选 1 | 按选项 |

---

## AskUserQuestion 5 选项模板

```python
AskUserQuestion(
    question="我识别到的意图不明确，请选择您要做的事情：",
    options=[
        {
            "label": "初始化项目（0→1）",
            "description": "从零开始一个新项目"
        },
        {
            "label": "新增功能 / 重构",
            "description": "在现有项目上加新功能或重构现有功能"
        },
        {
            "label": "修复 Bug",
            "description": "用户反馈的报错/不工作问题（含 e2e 先行 + 6 层排查）"
        },
        {
            "label": "文档同步",
            "description": "更新 spec / api 文档 / README"
        },
        {
            "label": "项目健康度自检",
            "description": "异步自检项目状态（4 维度）"
        }
    ]
)
```

---

## Bug 录入询问协议

**触发**: 命中问题类触发词（"报错"/"错误"/"不工作"/"应该 X 但 Y"/"期望 X 但实际 Y"）

**询问模板**:

```
主上下文必问: "看起来像是一个 Bug（命中触发词：'XXX'），是否作为 bug 单录入到 docs/bugs/？

              录入后会由 Stage 6 Bug Fix 专家处理：
              - e2e 先行（必须初始 FAIL 证明 bug 真实存在）
              - 6 层排查（网络/接入/应用/数据/集成/客户端）
              - TDD 修复 + 回归验证
              - bug 单回写 CLOSED

              如果只是想咨询或讨论，请告诉我。"
```

**用户同意**:
1. 进入 Bug 录入 6 字段工作流
2. 收集：症状 / 期望 / 复现步骤 / 影响范围 / 环境信息 / 触发词
3. 创建 Bug 单 + 状态卡
4. 路由: Stage 6 Bug Fix

**用户拒绝**:
1. 状态卡 health = 🟡 degraded
2. notes 标注: "用户拒绝 bug 录入，按一般咨询处理"
3. 路由: Stage 7 Project Health（异步自检，作为后续诊断）

---

## 反例与陷阱

### 反例 1：触发词命中跳过询问

```
用户: "token 报 500"
主上下文: "已识别为 bug-fix，直接创建 bug-001"  # ❌ 违反铁律 4
正确: 必问 → 用户同意 → 创建
```

### 反例 2：模糊输入靠经验猜

```
用户: "这个项目有点问题"  # 模糊
主上下文: "看起来像 bug，我帮你修"  # ❌ 违反铁律 5
正确: AskUserQuestion 5 选 1
```

### 反例 3：路由未记录

```
主上下文: 路由到 Stage 0 Plan，但 next_stage 字段为空  # ❌ 违反铁律 6
正确: next_stage.id + skill_name 必填
```

### 反例 4：跳过状态卡初始化

```
主上下文: 路由到 Stage 0 Plan，但未初始化状态卡  # ❌ 反例 2
正确: Step 6 状态卡初始化必走
```

---

## 路由决策证据链

**MUST**: 路由决策必须可追溯，写入状态卡 notes：

```yaml
notes: |
  路由决策证据:
    触发词命中: "报错" → bug-fix
    用户询问: 同意录入
    6 字段收集: 完整
    Bug 单编号: auth-003-token-refresh-500
    路由目标: Stage 6 Bug Fix
    决策时间: 2026-08-11T14:30:00
```

**NEVER**: 路由无证据（违反铁律 10 NEVER 静默路由）

---

## 关联引用

- [SKILL.md](../SKILL.md) — 阶段入口
- [intent-types.md](intent-types.md) — 5 种意图类型详解
- [intent-routing.md](../workflows/intent-routing.md) — 意图路由工作流
- [bug-intake-flow.md](../workflows/bug-intake-flow.md) — Bug 录入工作流
- [bug-state-machine.md](bug-state-machine.md) — Bug 单状态机
