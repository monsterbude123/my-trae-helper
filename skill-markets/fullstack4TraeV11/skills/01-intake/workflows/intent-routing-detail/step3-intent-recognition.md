# Step 3：意图识别 — intent-routing.md 详情

> 父文件：[../intent-routing.md](../intent-routing.md)
> 来源：原 intent-routing.md 第 87-118 行（保留信息密度）

---

## Step 3：意图识别（5 种类型）

### 3.1 触发词命中（直接分类）

| 触发词 | 意图类型 | 路由目标 |
|--------|---------|---------|
| "初始化" / "新项目" / "项目 0→1" | project-init | Stage 0 Plan |
| "新需求" / "新增功能" / "加个 X" | change-start (feature) | Stage 0 Plan |
| "重构" / "改造" / "重新设计" | change-start (refactor) | Stage 0 Plan |
| "文档同步" / "更新文档" | change-start (doc-sync) | Stage 1 Spec 或 Stage 5 Accept (lite) |
| "报错" / "错误" / "异常" | 触发 Bug 录入判断 → bug-fix | Stage 6 Bug Fix |
| "不工作" / "失败" / "崩溃" | 触发 Bug 录入判断 → bug-fix | Stage 6 Bug Fix |
| "应该出现 X 但出现 Y" | 触发 Bug 录入判断 → bug-fix | Stage 6 Bug Fix |
| "期望 X 但实际 Y" | 触发 Bug 录入判断 → bug-fix | Stage 6 Bug Fix |
| "自检" / "健康度" / "诊断" | project-health | Stage 7 Project Health |

### 3.2 触发词不命中（AskUserQuestion）

```python
# 反模式: 经验主义臆断意图（Article V 违反）
# 正确: AskUserQuestion 列出 5 种意图
AskUserQuestion(
  question="我识别到的意图不明确，请选择您要做的事情：",
  options=[
    {"label": "初始化项目（0→1）", "description": "从零开始一个新项目"},
    {"label": "新增功能 / 重构", "description": "在现有项目上加新功能或重构"},
    {"label": "修复 Bug", "description": "用户反馈的报错/不工作问题"},
    {"label": "文档同步", "description": "更新 spec / api 文档"},
    {"label": "项目健康度自检", "description": "异步自检项目状态"}
  ]
)
```

---

## 关联引用

- 父文件：[../intent-routing.md](../intent-routing.md)
- intent-types.md：[../../references/intent-types.md](../../references/intent-types.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
