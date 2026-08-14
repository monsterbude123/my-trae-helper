# Project Convention Survey — Stage -1 Intake

> Stage -1 Intake Step 2 必走。项目惯例勘察协议。

---

## 勘察项（必含）

1. **项目类型**: web / tauri / cli / library / backend
2. **主语言**: python / typescript / rust / go / java
3. **测试框架**: vitest / pytest / cargo test / go test
4. **构建工具**: vite / webpack / next / rollup
5. **目录结构**: src/ + tests/ / docs/ + scripts/
6. **代码规范**: ruff / eslint / clippy / prettier
7. **状态卡位置**: docs/specs/changes/{id}/.state-card.md
8. **变更 ID 规范**: {YYYY-MM-DD}-{slug}

---

## 勘察工具

```bash
# 项目类型
ls -la package.json pyproject.toml Cargo.toml setup.py go.mod 2>/dev/null

# 框架
grep -E '"(react|vue|svelte|next|vite)"' package.json
grep -E '(django|fastapi|flask)' requirements.txt pyproject.toml
grep -E '(actix|axum|tauri)' Cargo.toml

# 测试
ls -la __tests__/ tests/ src/**/__tests__/

# 已有 skills
cat AGENTS.md | head -30
cat .trae/fullstack4traev11.config.yaml 2>/dev/null
```

---

## 输出格式

```yaml
project_convention:
  type: "web"
  language: "typescript"
  framework: "react + vite"
  test_framework: "vitest"
  test_dir: "__tests__/"
  build_tool: "vite"
  linter: "eslint"
  formatter: "prettier"
  state_card_path: "docs/specs/changes/{id}/.state-card.md"
  change_id_format: "{YYYY-MM-DD}-{slug}"
  has_AGENTS_md: true
  has_fullstack_config: true
  notes: |
    - 已有 AGENTS.md，stage 必走路由有定义
    - 测试用 vitest，Stage 3 implement 必用 vitest
```

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [stage-card-protocol.md](../../../references/state-card-protocol.md)