# tests/catalogs/ — Skill Catalog 校验目录

> **V11.8.0 NEW**(2026-08-15) — 协议先行 + 多维度一致的 catalog 校验工具集。

---

## 目录结构

```
tests/catalogs/
├── README.md                     (本文件)
├── catalog-protocol.md           (协议规范 — 11 章节)
├── skill-catalog.schema.json     (JSON Schema)
├── skill-catalog.yaml            (catalog 声明 — V1 必填只 2 项)
└── _check_skill_catalog.py       (校验脚本 — std lib + argparse)
```

---

## 快速开始

```bash
# 校验 skill-markets/ 所有 SKILL 满足 catalog
python tests/catalogs/_check_skill_catalog.py \
    --catalog tests/catalogs/skill-catalog.yaml \
    --skills-root skill-markets

# 严格模式 — 任一 FAIL 即 exit 1
python tests/catalogs/_check_skill_catalog.py \
    --catalog tests/catalogs/skill-catalog.yaml \
    --skills-root skill-markets \
    --strict
```

---

## V1 设计要点

| 维度 | 决策 |
|------|------|
| **scope** | skill-metadata(仅元数据,不检内容) |
| **必填字段** | `name` + `description`(AGENTS.md §1.1 铁律 #1) |
| **可选字段** | version / requires / protocols / workflows |
| **结构守卫** | max_skill_md_lines=500 + min_yaml_frontmatter_fields=2 |
| **退出码** | V1 report-only(默认 exit 0) + `--strict` 才 exit 1 |
| **理由** | 渐进式 — 不强制全填避免大面积 FAIL,后续 V2+ 调严 |

---

## 联动资源

- [`.agents/skills/project-rule-skill/references/skill-creation-workflow.md`](../../.agents/skills/project-rule-skill/references/skill-creation-workflow.md) (V11.8.0.1 路径迁移) §1 — 协议先行原则
- [`.agents/skills/project-rule-skill/references/protocol-coverage-protocol.md`](../../.agents/skills/project-rule-skill/references/protocol-coverage-protocol.md) (V11.8.0.1 路径迁移) §3.2 — protocol coverage 联动
- [`.github/workflows/skill-market-gate.yml`](../../.github/workflows/skill-market-gate.yml) §5.8 — CI gate
- [AGENTS.md §7](../../AGENTS.md) — 能力地图