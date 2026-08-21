---
name: quality-documentation-manager
version: 1.0.0
description: "专业文档管理员(Documentation Steward)方法论 — Diátaxis 四象限信息架构 + SSOT 协议 + Docs-as-Code 工具栈(lychee / Vale / markdownlint-cli2) + 反向引用图谱 + 文档状态机 + 4 层强制链(CI Gate)。当用户需要 'documentation governance'、'doc governance'、'diataxis'、'SSOT'、'ROT audit'、'lychee'、'markdownlint'、'vale'、'文档治理'、'文档管理员'、'信息架构'、'文档腐烂' 时自动加载。本 skill 是元项目方法论沉淀,不针对单一项目。"
triggers: [documentation, documentation governance, doc governance, diataxis, SSOT, ROT, lychee, markdownlint, vale, 文档治理, 文档管理员, 信息架构, 文档腐烂, 反向引用图谱, docs-as-code]
intent: 沉淀专业文档管理员方法论(Documentation Steward) — 信息架构 + SSOT + 工具栈 + 状态机 + 强制链
category: docs
audience: [developer, tech-writer]
requires:
  - skill: doc-map-manager
    note: "软依赖。本 skill 定义方法论,doc-map-manager 提供反向引用图谱 / 影响面 / 新鲜度评分(🟢/🟡/🔴 4 档)。"
  - skill: vibe-coding-standards
    note: "软依赖。SKILL.md 行数 100~350 弹性来自 v2.5 守卫。"
  - skill: skill-acceptance
    note: "软依赖。本 skill 发布前必跑 verify.py 6 项检查 + intent 3 字段。"
  - skill: common-project-coding-conf
    note: "软依赖。cpcc §1 路由表 '文档治理' 行指向 doc-map-manager + docsify-doc-builder,本 skill 补 SSOT/Diátaxis/ROT 维度。"
---

# quality-documentation-manager — 专业文档管理员方法论

> **本 skill 是元项目方法论沉淀,不针对单一项目改造。**
> 来源报告:d:\workplace\code\ai-dev\new-api-monster\docs\research\professional-documentation-management-20260821.md
> 报告 22+ 来源已沉淀为 references/,本 skill 不复述报告原文,只给协议层。
>
> **缩写避坑**:
> - **ROT**(本 skill)= **R**edundant / **O**utdated / **T**rivial 三态文档审计(InstantDocs 框架)
> - **ROT**(fullstack4TraeV11/skills/10-rot-scan)= "腐化扫描"(10 项腐化指标)
> - 同缩写异义,**不重命名**(改名会破坏触发词)。本 skill 用 ROT 时必加 §0 注脚。
> - **SSOT**(本 skill)= Single Source of Truth 文档治理协议(同全行业含义)

---

## §0 定位

```
本 skill = 协议层(方法论沉淀)
├── 信息架构:Diátaxis 四象限(§1)
├── 引用纪律:SSOT 6 条铁律(§2)
├── 工具栈:Docs-as-Code 5 原则 + 3 件套(§3)
├── 反向引用:链接图谱 + 影响面(§4)
├── 生命周期:状态机 + 时限红线(§5)
└── 强制链:4 层(L1 编辑器 → L4 监控)(§6)

不重复造(明确边界):
  doc-map-manager        ← 反向引用 / 新鲜度评分(本 skill 引用其概念,不复制脚本)
  skill-acceptance       ← skill 包元数据准入(本 skill 受其审查)
  vibe-coding-standards  ← SKILL.md 行数弹性 100~350(本 skill 行数遵循)
  common-project-coding-conf ← 路由表"文档治理"行已指向 doc-map-manager + docsify-doc-builder(本 skill 补 SSOT/Diátaxis/ROT 维度)
  fullstack4TraeV11 §14  ← Stage 8 doc-sync + v11-doc-check.yml(本 skill §6 引用其 CI 模式,不复制 yaml)
```

---

## §1 Diátaxis 四象限(信息架构事实标准)

> 来源:[diataxis.fr](https://diataxis.fr/) 已被 Cloudflare / Gatsby / Vonage 等数百项目采用。

按 **实践 / 理论 × 学习 / 工作** 两个维度划分 4 类文档,**一文一目的硬纪律**(DITA topic-based 现代继承者)。

| 象限 | 目的 | 典型例子 | 何时写 | quadrant 字段值 |
|------|------|----------|--------|---------------|
| **Tutorials** 教程 | 入门学习 | "你的第一个 API 调用" | 用户第一次接触 | `tutorial` |
| **How-to Guides** 操作指南 | 解决具体问题 | "如何配置 Stripe 支付" | 用户有明确目标 | `how-to` |
| **Reference** 参考 | 查事实 | API 端点列表 | 用户已知要找什么 | `reference` |
| **Explanation** 阐释 | 理解原理 | "为什么我们用 Channel 亲和性路由" | 用户想深入 | `explanation` |

### §1.1 frontmatter 强制 quadrant 字段

```yaml
---
title: 如何配置 Stripe 支付
quadrant: how-to             # tutorial / how-to / reference / explanation
audience: backend-developer  # 目标读者
last_verified: 2026-08-21    # 末次人工核验日,见 §5 时限红线
---
```

### §1.2 quadrant 判定决策树

```
用户问的是什么？
│
├── "我想学 X" / "新手指引" / "Quickstart"     → tutorial
├── "我要做 X" / "如何配置 / 部署 / 调试"     → how-to
├── "X 的参数列表" / "API 端点" / "命令手册"   → reference
└── "为什么 X 这样设计" / "X 的原理"           → explanation
```

> **冲突仲裁**:同一概念多象限引用 → 写**定义在 explanation,操作在 how-to,事实查 reference**。不复制定义,只放相对引用(见 §2 SSOT)。

详见 [references/diataxis-quadrants.md](references/diataxis-quadrants.md)。

---

## §2 SSOT 协议 6 条铁律

> 来源:[Docsie SSOT](https://www.docsie.io/blog/glossary/single-source-of-truth-ssot/) + TapTap 实战 + DevFlow 反例库。
> **SSOT 不是工具,是协议**。仅"定义唯一"不够,必须用相对引用替代复制粘贴。

```
铁律 1 — 代码是权威(Code as SSOT)
        文档是派生物。冲突时代码赢,永远不反过来。
铁律 2 — 一概念一定义
        同概念多文档定义 → 必触发 ROT R(Redundant)审计。
铁律 3 — 相对引用替代复制粘贴
        [text](relative/path.md) 替代 [text](完整内容)
        任何 markdown 段落复制粘贴到另一文档 = 触发 SSOT 违规。
铁律 4 — 反向引用图谱必构建
        修改前跑 doc-map-manager --impact(见 §4),不知道下游就动手 = 真相污染。
铁律 5 — "真理"四要素必须齐
        数据准确 + 时效 + 完整 + 可追溯
        缺任一要素 → 该文档标 outdated(见 §5 状态机)。
铁律 6 — 副本必须字节一致
        一旦重复存在,所有副本必须字节一致
        否则 = coupled invariant tax(DevFlow 反例库术语)。
```

### §2.1 字段命名避坑(全局 self-improving-agent 冲突)

| ❌ 不用(全局 schema) | ✅ 用(本 skill SSOT 字段) |
|---------------------|------------------------|
| `Logged` | `last_verified`(YYYY-MM-DD) |
| `Priority` | `freshness_tier`(🟢/�/🔴 4 档映射) |
| `Status` | `doc_status`(draft / stable / outdated / deprecated) |
| `Reproducible` | `verify_method`(manual / ci / gitnexus-cross-check) |
| `Related Files` | `backlinks`(由 doc-map-manager --context-mode 自动生成) |

详见 [references/ssot-protocol.md](references/ssot-protocol.md)。

---

## §3 Docs-as-Code 5 原则 + 工具栈

> 来源:[Docuwiz](https://www.docuwiz.io/blog/docs-as-code-the-complete-guide-to-treating-documentation-like-software) + vistadocs/guides(综合 6 大公司实践)+ thedocumentation.org CI 指南。
> 业界共识:GitHub PR + markdownlint + Vale + lychee + CI 是成熟链。

### §3.1 5 条核心原则

```
1. 纯文本创作      Markdown / AsciiDoc / reStructuredText,不用专有格式
2. 版本控制        Git 追踪每一次变更
3. 协作评审        PR/MR 流程
4. 自动化质量检查  CI 跑 linting + 链接检查 + 构建
5. 自动化部署      合并触发构建发布
```

### §3.2 推荐工具栈(2026-08)

| 工具 | 解决 | 版本 | 配置文件 | 业界采纳 |
|------|------|------|---------|---------|
| **lychee** | 链接有效性(死链扫描) | v0.20+ | `lychee.toml` | Red Hat / Kubernetes / Rust |
| **Vale** | 散文风格(术语 / 用词) | v3+ | `.vale.ini` + `styles/` | GitLab / Discord / Docker / Grafana |
| **markdownlint-cli2** | Markdown 语法合规 | v0.13+ | `.markdownlint.yaml` | David Anson,社区标准 |
| **pre-commit** | Git hook 编排 | v3+ | `.pre-commit-config.yaml` | 几乎所有 GitHub 大项目 |
| **GitHub Actions** | CI 编排 | — | `.github/workflows/docs-guard.yml` | Microsoft / Google / UK Home Office |

### §3.3 工具选型决策树

```
需要校验什么？
│
├── 死链(内链 + 外链)
│   └── lychee(Rust 异步,比 linkchecker 快 10 倍+)
├── Markdown 语法
│   └── markdownlint-cli2(50+ 规则)
├── 散文风格(术语统一 / 用词规范)
│   └── Vale(自定义 rules / 共享 styles)
├── Pre-commit hook 编排
│   └── pre-commit v3+(跨平台)
└── CI 阻断
    └── GitHub Actions(lychee-action / markdownlint-cli2-action)
```

详见 [references/docs-as-code-toolchain.md](references/docs-as-code-toolchain.md)(含完整 yml / toml / ini 配置示例)。

---

## §4 反向引用图谱(链接健康 + 影响面)

> **本节是协议层,不重复 doc-map-manager 已有脚本**(build-index.py / query-index.py)。只规定"什么场景调用什么"。

### §4.1 调用映射表

| 场景 | 调用 | 命令 | 输出 |
|------|------|------|------|
| 文档间反向引用 | doc-map-manager | `--context-mode FILE` | 入站 / 出站链接 + 标签 |
| 修改前影响面 | doc-map-manager | `--impact FILE` | 风险等级 + 关联文档列表 |
| 刚才改了哪些文档 | doc-map-manager | `--detect-changes` | 变更清单 + 入站链 |
| 内链死链 | lychee | `lychee --offline docs/` | 内链 100% 必须通过 |
| 外链死链 | lychee | `lychee docs/` | 外链允许 retry × 2 |
| Markdown 段落重复 | grep + 人工 | `grep -l "关键词" docs/**/*.md` | 找 SSOT 违规候选 |

### §4.2 死链处理纪律

```
内链 → 100% 必须通过 → CI 阻断
外链 → 允许 retry × 2 → 仍失败则人工 review 后允许 merge(加 issue 跟踪)
       ↑ 此处与 lychee.toml exclude 配合(排除 GitHub issues 等易误报链接)
```

详见 [references/docs-as-code-toolchain.md §死链治理](references/docs-as-code-toolchain.md)。

---

## §5 文档状态机 + 时限红线

> 来源:Write the Docs WEP + RFC 模式 + DITA 5 态。**业界无标准,但有共识**。

### §5.1 4 态状态机

```
                评审通过
   draft  ─────────────────→  stable
     │                          │
     │ 评审不通过               │ 内容已过时
     ↓                          ↓
   (回炉)                    outdated
                                │
                                │ 时限红线超时(见 §5.2)
                                ↓
                           deprecated
```

| 状态 | 含义 | frontmatter `doc_status` |
|------|------|------------------------|
| **draft** | 草稿,未稳定 | `draft` |
| **stable** | 已发布,当前有效 | `stable` |
| **outdated** | 已知与代码不一致,待修复 | `outdated` |
| **deprecated** | 已废弃,不再维护 | `deprecated` |

### §5.2 outdated 时限红线(P0~P2)

| 优先级 | 模块类型 | 修复时限 | 超时动作 |
|--------|---------|---------|---------|
| **P0** | 计费 / 安全 / 鉴权 | ≤ 24h | 强制降级为 `deprecated` + Slack/Email 告警 |
| **P1** | 核心 API / 架构 | ≤ 7 天 | 升级 P0 跟踪 |
| **P2** | 边缘功能 / 教程 | ≤ 30 天 | 合并到下一季度 ROT 审计 |

### §5.3 freshness 4 档(与 doc-map-manager 对齐)

| 距 last_verified | 评分 | 图标 | doc-map-manager --grab 输出 | 本 skill 动作 |
|-----------------|------|------|------------------------|------------|
| 0~7 天 | 1.0→0.7 | 🟢 | 高置信,可直接引用 | 无 |
| 7~30 天 | 0.7→0.3 | 🟡 | 中置信,标"可能不是最新" | agent 二次验证 |
| 30~90 天 | 0.3→0.1 | 🔴 | 低置信,必须交叉验证 | 触发 ROT O(Outdated)审计 |
| 90+ 天 | ≤0.1 | � | 过时,必须验证 | 强制标 `outdated` + 时限红线启动 |

详见 [references/freshness-state-machine.md](references/freshness-state-machine.md)(含 ROT 季度审计 SOP + 修复时限协议)。

---

## §6 4 层强制链(CI Gate + husky + 编辑器)

> 来源:thedocumentation.org markdownlint-cli CI/CD + Red Hat PR #271 + Vale.sh 用户案例。

```
L1 编辑器        markdownlint 扩展 / Vale VSCode 扩展
        ↓ commit
L2 pre-commit    pre-commit v3+ → lychee / Vale / markdownlint
        ↓ push
L3 CI            GitHub Actions docs-guard.yml
                  ├─ lychee-action v2(fail=true)
                  ├─ markdownlint-cli2-action
                  └─ Vale action
        ↓ 定期
L4 监控          定时任务 + Slack/Email 告警
                  ├─ 每日全量 lychee 外链扫描
                  └─ 每周 freshness 报告(🔴 文档清单)
```

### §6.1 L3 CI 阻断规则

| 检查 | 阻断条件 | 来源 |
|------|---------|------|
| 内链死链 | 100% 必须通过 | lychee |
| 外链死链 | 允许 retry × 2 + issue 跟踪 | lychee |
| Markdown 语法 | error 级必须清零 | markdownlint-cli2 |
| Vale 风格 | error 级必须清零,警告允许 | Vale |
| quadrant 字段缺失 | frontmatter 必含 | 本 skill §1.1 |
| doc_status 缺失 | frontmatter 必含 | 本 skill §5.1 |

详见 [references/ci-gate-stack.md](references/ci-gate-stack.md)(含 4 层完整 yml / toml 示例)。

---

## §7 与已有 skill 的关系

| 已有 skill | 本 skill 关系 | 不重复的内容 |
|-----------|-------------|------------|
| **doc-map-manager** v2 | 引用 | 反向引用脚本(本 skill 不复制 build-index.py / query-index.py)|
| **vibe-coding-standards** v2.5 | 遵循 | 行数守卫 100~350(本 skill SKILL.md 已通过验证)|
| **skill-acceptance** v0.1 | 受审查 | 6 项检查 + intent 3 字段(本 skill 发布前必跑)|
| **common-project-coding-conf** v1.0 | 互补 | cpcc §1 路由表"文档治理"行 → 本 skill 补 SSOT / Diátaxis / ROT |
| **fullstack4TraeV11** V11.8.6 | 引用 | Stage 8 doc-sync + v11-doc-check.yml(本 skill §6 引用其模式,不复制 yaml)|
| **meeting-minutes-taker** v1 | 同 SSOT 注脚 | SSOT 行文用语(本 skill §0 注脚避免冲突)|
| **docsify-doc-builder** | 互补 | UE 风格文档站搭建(本 skill 不涉及前端) |

### §7.1 一句话索引(fullstack4TraeV11 用户)

V11 Stage 8 doc-sync 用 v11-doc-check.yml 跑 lychee + markdownlint → 本 skill §6 提供协议层(为什么这么做 + 4 层强制链含义),V11 提供具体 yaml。

---

## §8 触发词表(≥6 个)

| 触发词 | 命中场景 |
|--------|---------|
| documentation / documentation governance / doc governance | 用户提到"文档治理" |
| diataxis / 信息架构 | 用户提到 Diátaxis 四象限 |
| SSOT / 单一真相源 | 用户提到 SSOT / 去重 |
| ROT / 文档腐烂 | 用户提到文档腐烂 / 季度审计 |
| lychee / markdownlint / vale | 用户提到死链 / Markdown / 风格检查工具 |
| 文档管理员 / documentation steward | 用户提到"文档管理员"角色 |
| 反向引用图谱 / backlinks | 用户提到反向链接 / 影响面 |

> 命中 ≥1 个关键词即自动加载。`triggers` 字段已在 frontmatter 声明。

---

## §9 反例(10 条 → references/trap-instructions.yaml)

详见 [references/trap-instructions.yaml](references/trap-instructions.yaml)(字段命名按 .agents/rules/learning.md §3 铁律:`severity` / `what_is_wrong` / `detect_signal` / `see_also`,**不用全局 schema 命名**)。

摘要:

| # | severity | what_is_wrong |
|---|----------|--------------|
| AP-1 | HIGH | 把 fullstack4TraeV11 的 ROT(腐化扫描)与本 skill ROT(三态文档审计)混淆 |
| AP-2 | HIGH | 把 SSOT 当成"一个数据库",忽略其协议本质 |
| AP-3 | HIGH | 文档中复制粘贴代码片段而非引用源文件,违反 SSOT §铁律 3 |
| AP-4 | HIGH | 改动文档前不跑 doc-map-manager --impact,触发 §铁律 4 |
| AP-5 | HIGH | outdated 文档超过 P0 24h 时限不修复 |
| AP-6 | MEDIUM | frontmatter 缺 quadrant 字段,违反 §1.1 强制纪律 |
| AP-7 | MEDIUM | frontmatter 缺 doc_status,违反 §5.1 状态机 |
| AP-8 | MEDIUM | CI 不区分内链 / 外链阻断规则(全阻断 = 误报多,全放行 = 失防御)|
| AP-9 | MEDIUM | lychee.toml 写死 GitHub issue 链接排除,导致真死链漏报 |
| AP-10 | LOW | 文档作者用绝对路径而非相对路径,违反 SSOT §铁律 3 |

---

*本 skill 是元项目方法论沉淀,不针对单一项目改造。任何项目应用本协议时,**先 Read §1-§6 协议层,再按 references/ 配置文件落地**。*
