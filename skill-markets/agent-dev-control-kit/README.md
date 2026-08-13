# Agent Development Control Kit

通用 Agent 开发控制体系技能包 — 从 vvicat AI 影视 Studio 项目提炼的三层控制方法论。

> **核心能力描述与三层控制体系详见 [SKILL.md](./SKILL.md)**。本 README 仅做目录与快速开始导航。

## 快速开始

### 方式一: 使用脚手架初始化新项目(推荐)

```bash
# 1. 复制脚手架到目标项目
cp -r skill-markets/agent-dev-control-kit/template-project /path/to/your-project

# 2. 进入项目目录
cd /path/to/your-project

# 3. 初始化项目
bash scripts/init-project.sh

# 4. 验证配置
bash scripts/validate-config.sh

# 5. 安装 Git Hooks
bash hooks/install-hooks.sh
```

### 方式二: 手动应用模板

1. **识别场景**: 确定当前任务属于哪类控制场景
2. **选择技能**: 根据场景选择对应的 Execution/Guard/Gate Skill
3. **应用模板**: 使用 `templates/` 下的标准模板
4. **执行流程**: 按照 `references/` 中的指南执行
5. **验证结果**: 通过门禁检查确认质量

## 文件结构

```
agent-dev-control-kit/
├── SKILL.md                          # 技能主文件 — 核心能力定义
├── README.md                         # 本文件 — 目录与导航
├── CHANGELOG.md                      # 版本变更记录
├── INDEX.md                          # 统一资源索引 ⭐ NEW
├── references/                       # 详细指南
│   ├── execution-skills-guide.md     # Execution Skills 完整指南
│   ├── guard-skills-guide.md         # Guard Skills 完整指南
│   ├── gate-skills-guide.md          # Gate Skills 完整指南
│   └── implementation-roadmap.md     # 实施路线图
├── scripts/                          # 可执行工具脚本
│   ├── init-control-kit.py           # 初始化控制体系
│   ├── validate-execution-skill.py   # 验证 Execution Skill
│   ├── run-all-guards.py             # 批量运行 Guard
│   ├── gate-check.py                 # 门禁检查工具
│   └── generate-skill-from-template.py # 从模板生成 Skill
├── skills/                           # 子技能拆分
│   ├── execution-control/            # Execution 控制核心
│   ├── guard-control/                # Guard 控制核心
│   └── gate-control/                 # Gate 控制核心
├── scenarios/                        # 典型使用场景
│   ├── 01-new-project-setup.md       # 新项目建立控制体系
│   ├── 02-add-new-execution-skill.md # 添加新 Execution Skill
│   ├── 03-customize-guards.md        # 定制 Guard 检查规则
│   ├── 04-troubleshooting-gate-failure.md # 门禁失败排查
│   └── 05-migrate-legacy-project.md  # 遗留项目迁移
├── templates/                        # 标准模板
│   ├── execution-skill-template.md   # Execution Skill 模板
│   ├── guard-skill-template.md       # Guard Skill 模板
│   └── gate-skill-template.md        # Gate Skill 模板
└── template-project/                 # 脚手架项目
    ├── .agents/skills/               # 示例 Execution Skills
    ├── guards/                       # 可执行的 Guard 脚本
    ├── gates/                        # 可执行的门禁脚本
    ├── hooks/                        # Git Hooks 安装脚本
    ├── scripts/                      # 初始化和验证脚本
    ├── tests/                        # 测试目录结构
    ├── docs/                         # 使用指南
    └── README.md                     # 项目说明
```

## 相关链接

- [SKILL.md](./SKILL.md) — 核心能力定义与三层控制体系
- [INDEX.md](./INDEX.md) — 统一资源索引(按用途分类)
- [CHANGELOG.md](./CHANGELOG.md) — 版本变更记录

## 来源

本项目从 **vvicat AI 影视 Studio** (ai-short-studio-monster) 提炼而来,该项目展示了工业级的 Agent 开发控制实践:

- **Agent Skills**: 6 个标准化开发流程
- **Guard Scripts**: 30+ 个契约检查脚本
- **Husky Hooks**: 多级门禁机制
- **Requirements Matrix**: 需求追踪矩阵

## 许可

MIT License
