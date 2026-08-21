# Diátaxis 四象限 — 详细协议

> 来源:[diataxis.fr](https://diataxis.fr/) + Cloudflare / Gatsby / Vonage 采纳证据。
> SKILL.md §1 摘要 + 决策树。本文件给完整四象限定义 + quadrant 字段 schema + 误用案例。

---

## §1 四象限定义(完整版)

按 **实践(Doing) / 理论(Understanding) × 学习(Acquiring skill) / 工作(Applying skill)** 两个维度划分 4 类文档。

```
                学习(Acquiring skill)        工作(Applying skill)
                ─────────────────────        ─────────────────────
实践(Doing)     │  TUTORIALS  教程    │       │  HOW-TO GUIDES 操作 │
                │  ──────────────     │       │  ────────────────── │
                │  入门引导           │       │  解决具体问题         │
                │  "你的第一个 ..."   │       │  "如何配置 X"        │
                ─────────────────────────────────────────────────────
理论(Under-     │  EXPLANATION 阐释   │       │  REFERENCE 参考      │
 standing)      │  ──────────────     │       │  ────────────────── │
                │  理解原理           │       │  查事实              │
                │  "为什么这样设计"   │       │  "API 端点列表"      │
                ─────────────────────────────────────────────────────
```

---

## §2 quadrant 字段 schema(frontmatter 强制)

### §2.1 必填字段

```yaml
---
title: 如何配置 Stripe 支付
quadrant: how-to             # 必填: tutorial / how-to / reference / explanation
audience: backend-developer  # 必填: 目标读者
last_verified: 2026-08-21    # 必填: 末次人工核验日
doc_status: stable           # 必填: draft / stable / outdated / deprecated(见 SKILL.md §5)
---
```

### §2.2 quadrant 取值枚举

| 值 | 含义 | frontmatter 示例 |
|----|------|----------------|
| `tutorial` | 入门引导 | `quadrant: tutorial` |
| `how-to` | 操作指南 | `quadrant: how-to` |
| `reference` | 参考手册 | `quadrant: reference` |
| `explanation` | 阐释原理 | `quadrant: explanation` |

### §2.3 校验规则(L3 CI 阻断)

```bash
# markdownlint 自定义规则:frontmatter 必含 quadrant
# 或者 CI 用 grep + yq 校验:
yq '.quadrant' docs/**/*.md | grep -vE "^(tutorial|how-to|reference|explanation)$"
# 非空且非四值之一 → exit 1 → CI 阻断
```

---

## §3 quadrant 判定决策树(完整版)

```
用户/作者问的是什么？
│
├── "新用户怎么入门？""Quickstart""Step-by-step""你的第一个 ..."
│   └── TUTORIAL
│       ├── 必须是线性序列(Step 1 → Step 2 → ...)
│       ├── 必须保证成功(作者跑过 + 验证过)
│       └── 不解释原理 / 不列完整选项
│
├── "用户有具体任务要完成？""如何 X""配置 / 部署 / 调试 ..."
│   └── HOW-TO
│       ├── 假设用户已具备基础(不重述 tutorial 内容)
│       ├── 聚焦"完成目标"的最短路径
│       └── 不展开背景(想了解原理 → 跳 explanation)
│
├── "用户已知要找什么？""API 端点""命令参数""字段类型 ..."
│   └── REFERENCE
│       ├── 信息结构化 + 可机器读
│       ├── 完整列举(不挑选"最重要的")
│       └── 无叙事 / 无评价
│
└── "用户想理解原理？""为什么这样设计""权衡""历史 ..."
    └── EXPLANATION
        ├── 讨论 + 权衡 + 历史 + 替代方案
        ├── 不给操作步骤(想动手 → 跳 how-to)
        └── 可表达观点(其他象限不行)
```

---

## §4 同概念多象限引用 — SSOT 协作模式

> **冲突仲裁**:同一概念多象限引用 → **定义在 explanation,操作在 how-to,事实查 reference**。不复制定义,只放相对引用。

### §4.1 反例(混象限)

```markdown
❌ how-to 文档中大段讲原理
"## 如何配置 Redis"
  Step 1: ...
  Step 2: ...
  ## Redis 的历史和 CAP 定理 ← 混了 explanation,违反一文一目的硬纪律
  ...
```

### §4.2 正例(SSOT 协作)

```markdown
✅ how-to 文档引用 explanation 相对路径
"## 如何配置 Redis"
  Step 1: ...
  Step 2: ...
  > 想了解 Redis 为什么这样选型 → [Redis 选型原理](../explanation/redis-choice.md)
  ...
```

```
explanation/redis-choice.md  ← 唯一定义点(SSOT)
how-to/configure-redis.md     ← 引用,不复制
reference/redis-commands.md   ← 引用,不复制
```

---

## §5 业界采纳证据

| 项目 | 采纳证据 |
|------|---------|
| **Cloudflare developer docs** | "Diátaxis 是我们信息架构的北极星"(Adam Schwartz) |
| **Gatsby 开源文档** | "四个象限帮助我们优先考虑每类文档的用户目标"(Megan Sullivan) |
| **Vonage** | "用 Diátaxis 建立了高质量内部文档"(Greg Frileux) |
| **Rust 生态** | Diátaxis + mdbook 标准化文档体系 |
| **Discord** | Vale 风格规则按 quadrant 区分检查级别 |

---

## §6 DITA 三类主题(参考而非采用)

> DITA(Darwin Information Typing Architecture,OASIS 标准)三类主题:
> - **Concept**(概念)
> - **Task**(任务)
> - **Reference**(参考)

**核心思想**(与 Diátaxis 同源):**一个文档 = 一个目的**,避免一篇文章做多件事。

**为什么现在不直接采用 DITA**:
- XML 标记重
- 技术写作工具链贵(Oxygen XML 等)

**但其精神(topic-based)被 Diátaxis 继承,对 Markdown 同样适用**。

---

## §7 误用案例(7 类)

| # | 误用 | 正确做法 |
|---|------|---------|
| 1 | how-to 文档中讲原理 | 引用 explanation |
| 2 | tutorial 列完整 API | 跳 reference |
| 3 | reference 表达观点("推荐用法") | 放 explanation |
| 4 | explanation 给操作步骤 | 跳 how-to |
| 5 | 同一文档同时是 tutorial + how-to | 拆 2 篇 |
| 6 | frontmatter 缺 quadrant | L3 CI 阻断 |
| 7 | quadrant 标签与正文内容不符 | 标 draft,重写或拆分 |

---

*完整规范见 [SKILL.md §1](../SKILL.md) 摘要;配置落地见 [docs-as-code-toolchain.md](docs-as-code-toolchain.md)。*
