# V11 内部 Todos — 当前活跃 + 归档 + 审计索引

> **定位**:V11 自我维护的"**当前活跃待办**"清单。已 done 的事项不留在主目录,物理归档到 [archive/done/](archive/done/),留作不可变历史(Article VIII)。
>
> **与 .trae/tmp/ 或 self-improving-agent 关系**:
> - 本目录存仓库内持久待办(self-improving-agent 走全局 ERR/LEARN/FEATURE_REQUESTS)
> - 两者**不重复**,本仓库内反例 + 协议差距留这里,跨会话经验走 self-improving-agent

---

## §1 目录当前布局

```
references/todos/
├── README.md                                    本文件(当前活跃索引)
├── P0-v12-physical-rollout.md                   V12 物理隔离 V11 范围内渐进落地(in_progress,本会话)
├── archive/                                     已 done 事项的物理归档
│   └── done/
│       ├── 2026-08-16-batch-repair/             单目录批量归档 P0/P1/P2/P3
│       │   ├── P0-protocol-vs-parser.md         2/2 done(整文件归档)
│       │   ├── P1-config-and-state-card.md      3/3 done(整文件归档)
│       │   ├── P2-bug-flow-and-stage-gate.md     3/3 done(整文件归档)
│       │   └── P3-cross-skill-and-doc.md        5/6 done(1 条 P3-6 抽出到根)
│       └── 2026-08-16-batch-repair-2/           P3-6 commit-minimum + Windows PYTHONIOENCODING 兜底归档
│           └── P3-6-commit-minimum.md           P3-6 done(2026-08-16)
├── audit-history/                               审计过程留痕
│   └── 2026-08-16-mentioned-but-not-parsed.md   子代理 B 14 条原始证据 + §5 后续
└── v12-physical-isolation/                      V12 物理隔离迁移检查清单(等 ADR,主版本升级)
    ├── V11.3-fact-stage-rationale.md
    └── migration-checklist.md
```

---

## §2 当前活跃待办(2026-08-16 第五轮蒸馏后)

| ID | 文件 | 优先级 | 状态 | 主题 |
|----|------|--------|------|------|
| audit-fix | [audit-fix-2026-08-16.md](audit-fix-2026-08-16.md) | audit | done(2026-08-16) | guard-smith audit B 方案 3 件系统化缺口修补落地(AGENTS.md §1.11 增补 + guard-gate-smith §1.1.1 + skill-registration-guard.mjs 顶部 docstring) |
| V12-ROOT | [v12-physical-isolation/](v12-physical-isolation/) | 等待 ADR | pending | V12 物理隔离迁移(主版本升级),前置 5 项见 [migration-checklist.md §0](v12-physical-isolation/migration-checklist.md) |
| mentioned-but-not-parsed top 5 | [audit-history/2026-08-16-mentioned-but-not-parsed.md](audit-history/2026-08-16-mentioned-but-not-parsed.md) §2 | top 5 | pending(4 条剩余,#13 已 done) | config.yaml 消费 / state-card 17 字段校验 / repair-flow.yaml Stage 6 接入 / §14.5 项目级 rules 优先解析 |

> **数量**:当前 `2 pending`(V12-ROOT 等 ADR + mentioned-but-not-parsed top 5 4 条剩余)。
> 历史总数:14 项协议层无解析脚本差距,V11.8.x + P3-6 + audit-fix + P0-v12 → **17/17 done**(含本会话两批次 commit)。
> **P0-v12 status:done(已 commit `06269ae`)** — V11.8.6 物理隔离渐进落地 6 步全部完成,本批次已归档至本表首行。

### §2.1 为什么不再按"P0/P1/P2/P3"分文件

2026-08-16 之前,按 priority 分 4 个 P-file 是因为"差距多 + 单文件描述尚可索引"。该批次 13/14 done 后:

- 13 个 done 条目 → 全部归档到单个 batch-repair 目录(按"批次聚合"而非"按优先级散开")
- 仅留 1 个 P3-6 pending 抽出独立文件,不再与 done 混杂
- V12 整套独立(等 ADR),不混入 P3

当未来再有 P4+ 新审计时,**优先按批次聚合**(本目录新增 1 条单独留,或聚合到下一个 batch-repair 目录)。不再按 P-file 散。

---

## §3 处理路由(主上下文 / 子代理怎么读)

```
MUST 主上下文进入 V11 任意会话前:
  → Read references/todos/README.md(本文件,30 行内)
  → 列出 needed_repair 摘要(max 200 字)
  → 由子代理修对应 todo 时,头部注入 [TODO-REPAIR] tag + 限定读本目录单条 .md
  → 修完后状态:
       - 若 done:本文件 move → archive/done/<YYYY-MM-DD-batch-name>/ + index 链接同步
       - 若在修中:main 文件引用前置 P-file 路径即可
```

子代理 `[TODO-REPAIR]` 委派头部格式:

```
[TODO-REPAIR]
target: references/todos/<P-file>.md 中某条(本批次后多在 archive/)
fix_proposal: <1 句修复路径>
forbidden: <不在白名单禁止改>
evidence_required: <跑什么命令证明 PASS>
```

---

## §4 归档批次索引

### 4.1 2026-08-16 协议层批修批次

| 维度 | 数值 |
|------|------|
| 归档目录 | [archive/done/2026-08-16-batch-repair/](archive/done/2026-08-16-batch-repair/) |
| 涵盖 P-file | P0 / P1 / P2 / P3(4 个) |
| 总条目 | 14 → 13 done + 1 pending(P3-6) |
| 触动脚本 | 3 新增 + 9 修改 = 12 个 .py |
| 新增单测 | 9 个 test 文件,79 用例 |
| 主上下文兜底 | pytest 232 passed,真反例 4 件 |
| Commit | `39d4f78` "V11.8.x 协议层承诺 → 脚本落地(13/14 done + 1 留置)" |

详见 commit `39d4f78` 的 `.commit_msg.txt` 完整描述,以及 [CHANGELOG.md V11.8.5 条目](../../CHANGELOG.md)。

---

## §5 关联引用

- [references/config-files-glossary.md](../config-files-glossary.md) — 子代理 A 交付物
- [references/stage-physical-isolation.md](../stage-physical-isolation.md) — V12 提案原文(本目录 v12-physical-isolation/ 是其派生)
- [references/dependency-config.md](../dependency-config.md) — 协议层依赖配置
- [references/state-card-protocol.md](../state-card-protocol.md) — 状态卡 schema
- [references/audit-history/2026-08-16-mentioned-but-not-parsed.md](audit-history/2026-08-16-mentioned-but-not-parsed.md) — 子代理 B 14 条原始审计 + 主上下文接手 + commit 时间表
