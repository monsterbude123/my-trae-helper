# INDEX — agent-dev-control-kit 资源索引

> **统一入口**：按用途分类列出所有文件与目录,便于快速定位。详细描述参见 [SKILL.md](./SKILL.md) 与 [README.md](./README.md)。

## 入口文件

| 文件 | 用途 |
|------|------|
| [SKILL.md](./SKILL.md) | 技能主文件 — 核心能力定义、触发条件、YAML frontmatter |
| [README.md](./README.md) | 项目导航 — 快速开始、目录结构 |
| [CHANGELOG.md](./CHANGELOG.md) | 版本变更记录 — 按 Keep a Changelog 规范 |
| [INDEX.md](./INDEX.md) | 本文件 — 统一资源索引 |

## 详细指南(references/)

| 文件 | 用途 |
|------|------|
| [execution-skills-guide.md](./references/execution-skills-guide.md) | Execution Skills 完整实施指南 |
| [guard-skills-guide.md](./references/guard-skills-guide.md) | Guard Skills 完整开发指南 |
| [gate-skills-guide.md](./references/gate-skills-guide.md) | Gate Skills 配置与门禁机制指南 |
| [implementation-roadmap.md](./references/implementation-roadmap.md) | 实施路线图 — 分阶段落地计划 |

## 工具脚本(scripts/)

| 脚本 | 用途 |
|------|------|
| `init-control-kit.py` | 初始化控制体系 — 支持 `--stack` / `--interactive` / `--auto-detect` / `--add-stack` 多种选型方式 |
| `validate-execution-skill.py` | 验证 Execution Skill — 检查 YAML frontmatter 与必需字段 |
| `run-all-guards.py` | 批量运行 Guard — 并行执行所有启用的 Guard |
| `gate-check.py` | 门禁检查工具 — 四级门禁统一入口 |
| `generate-skill-from-template.py` | 从模板生成 Skill — 自动化脚手架 |

## 技术栈选型(presets/)

> **预置 + 动态扩展** 的选型系统,支持 4 种内置技术栈,用户可自定义。

| 选型 | 描述 | 检测特征 | 模板 |
|------|------|---------|------|
| `nodejs` | Node.js + JavaScript/TypeScript | `package.json` | ✅ 完整 |
| `python` | Python(FastAPI/Django/Flask) | `pyproject.toml` | ✅ 完整 |
| `go` | Go(Gin/Echo) | `go.mod` | ✅ 完整 |
| `java-maven` | Java(Spring Boot) | `pom.xml` | ✅ 完整 |

**自定义选型**: `~/.agent-dev-control-kit/presets/<your-id>/` 优先级高于内置。

详见 [presets/README.md](./presets/README.md)。

## 子技能拆分(skills/)

| 子技能 | 用途 |
|--------|------|
| `execution-control/` | Execution 控制核心 — 5 个 Execution Skills 模板与实现参考 |
| `guard-control/` | Guard 控制核心 — Guard 模板、配置校验规则 |
| `gate-control/` | Gate 控制核心 — 四级门禁配置、pre-commit/pre-push 钩子 |

## 使用场景(scenarios/)

| 场景 | 用途 |
|------|------|
| `01-new-project-setup.md` | 新项目建立控制体系 |
| `02-add-new-execution-skill.md` | 添加新 Execution Skill |
| `03-customize-guards.md` | 定制 Guard 检查规则 |
| `04-troubleshooting-gate-failure.md` | 门禁失败排查手册 |
| `05-migrate-legacy-project.md` | 遗留项目迁移 |

## 标准模板(templates/)

| 模板 | 用途 |
|------|------|
| `execution-skill-template.md` | Execution Skill 标准模板 |
| `guard-skill-template.md` | Guard Skill 标准模板 |
| `gate-skill-template.md` | Gate Skill 标准模板 |

## 脚手架项目(template-project/)

| 路径 | 用途 |
|------|------|
| `.agents/skills/` | 示例 Execution Skills(config-sync/data-change/doc-sync) |
| `guards/` | 可执行的 Guard 脚本(api-contract/test-coverage)+ 配置文件 |
| `gates/` | 可执行的门禁脚本(pre-commit/pre-push)+ gate-config.json |
| `hooks/` | Git Hooks 安装脚本(支持参数化路径) |
| `scripts/` | 项目级初始化与验证脚本 |
| `tests/` | 测试目录结构(unit/integration/e2e) |
| `docs/` | 项目级使用指南 |
| `src/` | 应用源码示例(展示 config 加载) |
| `.env.example` | 环境变量模板(仅含脚本实际读取的变量) |

## 按任务快速跳转

### 新接触这个技能包
1. [SKILL.md](./SKILL.md) — 了解核心能力
2. [README.md](./README.md) — 快速开始
3. [INDEX.md](./INDEX.md) — 本文件,资源地图

### 我想初始化一个新项目
1. [scenarios/01-new-project-setup.md](./scenarios/01-new-project-setup.md)
2. `template-project/` 脚手架复制 + `scripts/init-project.sh`
3. [references/implementation-roadmap.md](./references/implementation-roadmap.md) — 长期规划

### 我想添加一个 Execution Skill
1. [scenarios/02-add-new-execution-skill.md](./scenarios/02-add-new-execution-skill.md)
2. [references/execution-skills-guide.md](./references/execution-skills-guide.md)
3. [templates/execution-skill-template.md](./templates/execution-skill-template.md)
4. [scripts/generate-skill-from-template.py](./scripts/generate-skill-from-template.py) — 自动化生成

### 我想定制 Guard 规则
1. [scenarios/03-customize-guards.md](./scenarios/03-customize-guards.md)
2. [references/guard-skills-guide.md](./references/guard-skills-guide.md)
3. [skills/guard-control/templates/](./skills/guard-control/templates/) — Guard 模板

### 门禁失败了怎么办
1. [scenarios/04-troubleshooting-gate-failure.md](./scenarios/04-troubleshooting-gate-failure.md)
2. [scripts/gate-check.py](./scripts/gate-check.py) — 单条门禁调试

### 我要把一个老项目迁移过来
1. [scenarios/05-migrate-legacy-project.md](./scenarios/05-migrate-legacy-project.md)
2. [references/implementation-roadmap.md](./references/implementation-roadmap.md)

### 我想升级 Gate 门禁
1. [references/gate-skills-guide.md](./references/gate-skills-guide.md)
2. [skills/gate-control/SKILL.md](./skills/gate-control/SKILL.md)
3. [skills/gate-control/templates/gate-config-template.json](./skills/gate-control/templates/gate-config-template.json)

## 版本

最新版本: **1.2.1** — 详见 [CHANGELOG.md](./CHANGELOG.md)
