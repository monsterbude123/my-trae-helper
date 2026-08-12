# Project Rules Skill

> 本目录由 fullstack4TraeV11 init-from-zero.py --rules-as-skill 自动生成。
> 职责:项目级 Rules 强制加载入口。

## 结构

```
project_rules_skills/
├── SKILL.md           ← 路由表 + 强制协议(主入口)
├── README.md          ← 本文件
├── workflows/         ← sub-agent 委派头部模板
│   └── sub-agent-delegate-load.md
└── references/        ← 软链接到 .trae/rules/ 实际 rule 文件
    ├── stack.md       → ../../.trae/rules/stack.md
    ├── governance.md  → ../../.trae/rules/governance.md
    └── ...
```

## 加载方式

```python
Skill(name="project-rules")
```

## 禁止

```
❌ 跳过本 skill 直接 Read .trae/rules/*.md
❌ 用 grep / Glob 搜 rules(必须走 skill 入口)
❌ 加载全部 rules(按 §2 路由表按需加载)
```

详见 [SKILL.md](SKILL.md)。