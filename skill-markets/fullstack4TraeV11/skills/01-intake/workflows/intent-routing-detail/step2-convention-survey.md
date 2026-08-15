# Step 2：项目惯例勘察 — intent-routing.md 详情

> 父文件：[../intent-routing.md](../intent-routing.md)
> 来源：原 intent-routing.md 第 54-83 行（保留信息密度）

---

## Step 2：项目惯例勘察（Glob 1 次）

```bash
# 主上下文亲自执行（Article IV 委派纪律）
Glob patterns:
  - {project}/AGENTS.md
  - {project}/docs/constitution.md
  - {project}/docs/INDEX.md
  - {project}/.trae/rules/*.md
  - {project}/.trae/fullstack4traev11.config.yaml
```

**输出**: 项目惯例表

```yaml
project_conventions:
  naming:
    change_id_format: "{YYYY-MM-DD}-{slug}"  # 例: 2026-08-11-add-user-auth（V11 全局规范,见 project-iron-laws.md §D）
    bug_id_format: "{module}-{number}-{slug}"  # 例: settings-009-config-key
  custom_rules:
    - .trae/rules/coding-standards.md
    - .trae/rules/归档路径防护.md
  stage_config_override:
    # 项目级 stage_config 覆盖（V11 dependency-config §3 层优先级）
  forbidden_paths:
    - docs/archive/**
    - .trae/tmp/**
```

**详细工作流**: [../project-convention-survey.md](../project-convention-survey.md)

---

## 关联引用

- 父文件：[../intent-routing.md](../intent-routing.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
