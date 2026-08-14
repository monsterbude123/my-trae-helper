# Agent Development Control Kit

通用 Agent 开发控制体系技能包 — 从 vvicat AI 影视 Studio 项目提炼的三层控制方法论。

> **核心能力描述与三层控制体系详见 [SKILL.md](./SKILL.md)**。本 README 仅做目录与快速开始导航。

## 快速开始

### 方式一: 使用脚手架初始化新项目(推荐)

```bash
# 1. 显式指定技术栈初始化(把 scaffolds/<stack>/files/ 复制到目标项目)
python scripts/init-control-kit.py \
  --target /path/to/your-project \
  --stack python

# 2. 进入项目目录
cd /path/to/your-project

# 3. 验证 Gate 完整性
python scripts/validate-gate-integrity.py --target .

# 4. 安装 Git Hooks
python scripts/install-husky.py --target .
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
│   ├── implementation-roadmap.md     # 实施路线图
│   ├── traps.md                      # 反例库
│   └── trap-instructions.yaml        # 结构化反例(机器可读)
├── scripts/                          # 可执行工具脚本(10 个业务脚本)
│   ├── init-control-kit.py           # 初始化控制体系
│   ├── validate-execution-skill.py   # 验证 Execution Skill
│   ├── validate-gate-integrity.py    # 检测 Gate 完整性漏洞
│   ├── run-all-guards.py             # 批量运行 Guard
│   ├── gate-check.py                 # 门禁检查工具
│   ├── generate-skill-from-template.py # 从模板生成 Skill
│   ├── catalog-guard.py              # catalog 阻断
│   ├── agent-hint-emit.py            # agent hint 聚合
│   ├── install-husky.py              # 安装 Git Hooks
│   └── migrate-to-layered-structure.py # 旧结构迁移
├── skills/                           # 子技能拆分(5 Execution + 3 控制核心)
│   ├── execution-control/            # Execution 控制核心
│   ├── guard-control/                # Guard 控制核心
│   ├── gate-control/                 # Gate 控制核心
│   ├── asset-management-control/     # 资产管理
│   └── release-process-control/      # 发布流程
├── scaffolds/                        # 脚手架(按技术栈)
│   ├── nodejs/                       # Node.js scaffold
│   ├── python/                       # Python scaffold
│   ├── go/                           # Go scaffold
│   └── java-maven/                   # Java Maven scaffold
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
├── registry/                         # 注册表
│   ├── stacks.yaml                   # 技术栈路由
│   ├── guards.yaml                   # 守卫配置
│   └── gates.yaml                    # 门禁配置
├── presets/                          # 选型元数据
│   ├── _index.yaml
│   ├── nodejs/  python/  go/  java-maven/
└── tests/                            # pytest 测试(102+ 用例,含 catalog 覆盖)
    ├── unit/
    ├── integration/
    └── catalogs/
```

## 相关链接

- [SKILL.md](./SKILL.md) — 核心能力定义与三层控制体系
- [INDEX.md](./INDEX.md) — 统一资源索引(按用途分类)
- [CHANGELOG.md](./CHANGELOG.md) — 版本变更记录

## 来源

本项目从 **vvicat AI 影视 Studio** (ai-short-studio-monster) 提炼而来,该项目展示了工业级的 Agent 开发控制实践:

- **子技能**: 5 个 Execution Skill(数据变更 / 文档同步 / 配置同步 / 资产管理 / 发布流程)+ 3 个控制核心 Skill(execution-control / guard-control / gate-control)
- **脚本**: 10 个业务脚本(初始化 / 验证 / 模板生成 / 守卫运行 / 门禁检查 / 目录守卫 / 提示聚合 / husky 安装等)
- **Husky Hooks**: 多级门禁机制(scaffold 提供)
- **反例库**: AP-1 ~ AP-7 真实蒸馏反例(`references/traps.md` + `trap-instructions.yaml`)

## 许可

MIT License
