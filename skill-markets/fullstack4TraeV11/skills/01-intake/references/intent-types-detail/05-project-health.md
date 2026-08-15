# 意图 5：project-health + 速查表 + 模糊处理 — intent-types.md 详情

> 父文件：[../intent-types.md](../intent-types.md)
> 来源：原 intent-types.md 第 158-209 行（保留信息密度）

---

## 意图 5：project-health（项目健康度自检）

**定义**: 异步自检项目状态（路径一致性 / 目录树 / 版本残留 / 文档同步）。

**触发词**:
- "自检" / "健康度" / "诊断"
- "project health" / "audit"

**特点**: 
- 🔀 独立支线（可与任一 stage 并行）
- ⚙ 非阻塞（异步执行）
- 主上下文不等待结果，可继续其他工作

**典型流程**:
```
Stage -1 Intake → Stage 7 Project Health
  → 4 维度检查（路径一致性 / 目录树 / 版本残留 / 文档同步）
  → 输出: project-health-{date}.md + .json
  → 优先级分级（P0/P1/P2/P3）
  → 用户决定何时修复
```

**状态卡**: project 级（不创建新状态卡，使用现有 project 状态卡，更新 stage）

**关键产出**:
- `project-health-{date}.md`
- `project-health-{date}.json`
- 4 维度检查结果
- 优先级修复列表

---

## 意图识别速查表

| 用户输入示例 | 意图 | 触发词 |
|------------|------|--------|
| "初始化这个项目" | project-init | "初始化" |
| "新增一个用户登录功能" | change-start (feature) | "新增" |
| "重构一下 auth 模块" | change-start (refactor) | "重构" |
| "更新 API 文档" | change-start (doc-sync) | "更新文档" |
| "token 刷新报 500" | bug-fix | "报 500" |
| "不工作" | bug-fix | "不工作" |
| "项目健康度怎么样" | project-health | "健康度" |

---

## 模糊意图处理

当触发词不命中或意图不明确时：

**MUST**: AskUserQuestion（5 种意图选项）→ 用户必选

**NEVER**: 经验主义臆断（违反 Article V GitNexus First 精神 / Article XVI §1.4 质疑性校验）

---

## 关联引用

- 父文件：[../intent-types.md](../intent-types.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
