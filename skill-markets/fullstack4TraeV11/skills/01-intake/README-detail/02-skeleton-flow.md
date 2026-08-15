# 骨架流程 — README.md 详情

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 父文件：[../README.md](../README.md)
> 来源：原 README.md 第 37-76 行（保留信息密度）

---

## 完整骨架流程

```
Step 1: 加载本 skill + 解析 depends_on
        ├─ 加载 4 个 stage 强依赖 references（state-card-protocol / stage-interaction-protocol / dependency-config / document-layer,见 SKILL.md frontmatter）
        ├─ 按需加载公共 references（constitution / iron-rules / anti-patterns / report-growth / ask-question-anti-patterns 等,来自编排器 §0.5）
        └─ 校验编排器 stage_config.intake 字段（空依赖符合预期）

Step 2: 项目惯例勘察（Glob 1 次）
        ├─ Glob: AGENTS.md / docs/constitution.md / docs/INDEX.md
        ├─ Glob: .trae/rules/*.md / .trae/fullstack4traev11.config.yaml
        └─ 输出: 项目惯例表（命名规则 / 铁律 / 自定义 stage_config / 反模式）

Step 3: 意图识别（5 种类型）
        ├─ 触发词命中 → 直接分类
        └─ 不命中 → AskUserQuestion（5 种意图选项）

Step 4: Bug 录入触发词判断（仅问题类触发词走此步）
        ├─ 命中 → 询问"是否作为 bug 单录入？"
        │   ├─ 用户同意 → 走 Step 5(bug-fix)
        │   └─ 用户拒绝 → 按"一般咨询"处理 + 状态卡 health=🟡 degraded
        └─ 未命中 → 跳过

Step 5: 路由决策
        ├─ project-init → Stage 0 Plan
        ├─ change-start（新功能/重构）→ Stage 0 Plan
        ├─ change-start（doc-sync）→ Stage 1 Spec 或 Stage 5 Accept（lite）
        ├─ bug-fix → Stage 6 Bug Fix（独立支线）
        └─ project-health → Stage 7 Project Health（异步自检）

Step 6: 初始化状态卡（3 类选其一）
        ├─ project 级 → {project}/docs/specs/.state-card.md
        ├─ change 级 → docs/specs/changes/{id}/.state-card.md
        └─ bug 级 → docs/bugs/{id}.md（Bug 单）+ docs/bugs/{id}/.state-card.md（Bug 状态卡）

Step 7: 交接下一 stage
        ├─ 状态卡 next_stage 字段填写
        ├─ state-card-validator.py 校验 PASS
        └─ stage-gate.py 切换确认
```

---

## 关联引用

- 父文件：[../README.md](../README.md)
- SKILL.md：[../SKILL.md](../SKILL.md)
