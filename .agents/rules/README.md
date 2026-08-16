# .agents/rules/ — 项目级规则加载提醒

> **每次 Agent 唤起会话时，必须先加载 project rule skill。**

## 加载协议

```
MUST: 每次会话开始第一步
  → 调用 Skill(name="project-rule-skill")
  → 按 SKILL.md §2 路由表匹配本任务场景
  → 输出 needed_rules 清单
  → 只 Read 清单中的 rules,禁止 Read 未声明的 .agents/rules/*.md 或 references/*.md

MUST NOT:
  → 不调用 project-rule-skill
```

## 本目录结构

```
.agents/rules/
└── README.md          (本文件 — 加载协议)
└── learning.md        (经验沉淀路由表)
└── 项目核心.md         (项目级操作注意)
└── skills开发细则.md   (skills 开发注意)
└── trae-work-mechanics.md  (Trae 四大机制速查:agents/rules/hooks/mcp)
```

> 后续 rules 按需新建:`.agents/rules/<topic>.md`(如 paths.md / git.md / coding-standards.md)。

## 当前 rules 来源

- **本目录** — `.agents/rules/*.md`（按需新建）
- **项目级方法论** — `skill-markets/fullstack4TraeV11/references/*.md`（反例库 / 决策层级 / 路径权限 / 分支规则 / CLI 铁律 / 技能库铁律）

## 一句话铁律

**会话开始 = `Skill(name="project-rule-skill")` 优先,再做事。**
