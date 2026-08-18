# Dependency Config — 3 层优先级依赖配置

> **V12.0.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> V11 project-level skill 依赖配置协议。所有 stage skill 必读。

---

## 3 层优先级

```
┌────────────────────────────────────────────────┐
│ Layer 1: 全局（global）— user-level skill registry │
│ ~/.trae-cn/skills/ — 公共 skills（gitnexus/ponytail）│
├────────────────────────────────────────────────┤
│ Layer 2: V11（orchestrator）— fullstack4TraeV11/ │
│ skill 的 SKILL.md depends_on.skills 字段 │
├────────────────────────────────────────────────┤
│ Layer 3: 项目级（project）— .trae/fullstack4traev11.config.yaml │
│ project 自身的 stage_config 覆盖 │
└────────────────────────────────────────────────┘

优先级: Layer 3 > Layer 2 > Layer 1
```

---

## Layer 1 全局 skills

V11 推荐预装的 user-level skills（git/user 全局）：

| Skill | 用途 | V11 使用 stage |
|-------|------|---------------|
| `gitnexus4Trae` | 代码图谱检索 | Stage 3, 6, 12 |
| `ponytail4Trae` | 懒惰高级开发模式 | Stage 3 |
| `visual-evidence-discipline` | 视觉证据纪律 | Stage 3.5, 4 |
| `screenshot` | Playwright 截图 | Stage 3.5 |
| `playwright-best-practices` | Playwright 最佳实践 | Stage 3.5 |
| `frontend-backend-contract-alignment` | 前后端契约对齐 | Stage 2 |
| `acceptance-discipline` | 验收铁律 | Stage 4 |
| `goal-mode` | 目标追逐模式 | Stage 4.5 |
| `doc-map-manager` | 文档图谱 | Stage 5 |
| `browser-use-cloud` | 浏览器云 | Stage 3.5 |

---

## Layer 2 V11 内置 skills

每个 stage skill 的 SKILL.md `depends_on.skills` 字段：

```yaml
---
name: implement
stage: 3
depends_on:
  skills: [ponytail4Trae, gitnexus4Trae]
  stages: [2/contract]
  references:
    - ../../references/state-card-protocol.md
  scripts:
    - ../../scripts/stage-gate.py
    - ../../scripts/code-hygiene.py
---
```

---

## Layer 3 项目级覆盖

项目级 `.trae/fullstack4traev11.config.yaml`：

```yaml
project:
  name: "{project-name}"
  type: "web" | "tauri" | "cli" | "library" | "backend"
  language: ["python", "typescript", "rust"]

stage_config:
  implement:
    skills: [react-dev-skill, rust-dev-skill]   # 覆盖 Layer 2
  real-verify:
    skills: [visual-evidence-discipline, screenshot, playwright-best-practices, browser-use-cloud]
  bug-fix:
    skills: [gitnexus4Trae, debugger4Trae, type-check-tool]

# 必走 stage 覆盖
required_stages:
  - -1/intake
  - 0/plan
  - 1/spec
  - 3.5/real-verify
  - 4.5/rot-scan

# 上下文保护（路径禁读）
forbidden_paths:
  - docs/archive/**
  - .trae/tmp/**
  - diagnostic/bugs/**
```

---

## 依赖解析算法

```python
def resolve_skills(stage_id, project_config):
    """3 层优先级解析"""
    skills = []

    # Layer 1: 全局（来自 user-level skills 目录）
    skills.extend(load_global_skills())

    # Layer 2: V11 内置（来自 SKILL.md depends_on）
    v11_config = load_v11_stage_config(stage_id)
    skills.extend(v11_config.get("skills", []))

    # Layer 3: 项目级覆盖
    project_overrides = project_config.get("stage_config", {}).get(stage_id, {})
    project_skills = project_overrides.get("skills", [])
    skills = project_skills + skills  # 项目级覆盖优先

    # 去重
    return list(dict.fromkeys(skills))
```

### V11.8.x 实现状态

`scripts/project-priority-resolver.py` 把上述伪代码落地为真实 CLI 接口（取代了原先仅停留在协议层的人肉判断）：

- **接口**: `--stage <id>` 单 stage 解析 / `--check-forbidden` 校验路径禁读 / `--merge-anti-patterns` 输出项目级禁用项
- **自动探测**: 优先读 `project_root/.trae/fullstack4traev11.config.yaml`，缺失则回退到 V11 内置 `SKILL.md depends_on`，再回退到全局 skills 目录（3 层优先级与算法伪代码严格一致）
- **真反例**: 2026-08-16 批修期间，用临时 JSON 输入验证 `resolve_skills` 返回顺序 = `[project, v11, global]`，项目级覆盖生效

```bash
# 单 stage 解析
python scripts/project-priority-resolver.py --stage 3/implement --project-root .

# 校验禁读路径（pre-stage hook 调用）
python scripts/project-priority-resolver.py --check-forbidden --project-root .

# 输出项目级反例合并（CI 集成）
python scripts/project-priority-resolver.py --merge-anti-patterns --json
```

详见 [tests/unit/test_project_priority_resolver.py](../../tests/unit/test_project_priority_resolver.py) — 232 passed 中的 14 条新增覆盖。

---

## 反例（依赖配置陷阱）

### 反例 1：项目级与 V11 冲突

```yaml
# project-level .trae/fullstack4traev11.config.yaml
stage_config:
  implement:
    skills: []  # 清空 → 实现无辅助 skill
```

后果: 实现阶段无 gitnexus / ponytail 辅助 → 违反 Article IV TDD。

正确: 不清空，仅追加或替换具体 skill。

### 反例 2：必需 stage 被禁用

```yaml
# project-level
required_stages: []  # 清空 → 不走任何 stage
```

后果: 违反 Article XII workflow discipline。

正确: 必含 5 个 required_stages（-1/0/1/3.5/4.5）。

### 反例 3：依赖循环

```yaml
stage_config:
  spec:
    scripts: [.../stage-gate.py]
stage_config:
  contract:
    scripts: [.../stage-gate.py]
# 看似 OK 但 spec 需 contract，contract 需 spec → 循环
```

正确: stage 间单向流转，无循环。

---

## 关联引用

- [stage-card-protocol.md](state-card-protocol.md) — 状态卡流转
- [common-iron-rules.md](common-iron-rules.md) — Article XII workflow discipline
- [SKILL.md](../SKILL.md) — 总编排器
- V10 来源（开发期，已蒸馏）：见 V11 references 与 anti-patterns
