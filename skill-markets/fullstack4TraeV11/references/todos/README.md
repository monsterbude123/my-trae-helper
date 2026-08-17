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
├── audit-cycle-2026-08-17.md                    2026-08-17 case 2/3 audit 闭环报告(本会话合并 + 修补 4 件 V11 skill)
├── P0-v12-physical-rollout.md                   V12 物理隔离 V11 范围内渐进落地(done 2026-08-16,保留作引用)
├── archive/                                     已 done 事项的物理归档
│   └── done/
│       ├── 2026-08-16-batch-repair/             单目录批量归档 P0/P1/P2/P3
│       │   ├── P0-protocol-vs-parser.md         2/2 done(整文件归档)
│       │   ├── P1-config-and-state-card.md      3/3 done(整文件归档)
│       │   ├── P2-bug-flow-and-stage-gate.md     3/3 done(整文件归档)
│       │   └── P3-cross-skill-and-doc.md        5/6 done(1 条 P3-6 抽出到根)
│       ├── 2026-08-16-batch-repair-2/           P3-6 commit-minimum + Windows PYTHONIOENCODING 兜底归档
│       │   └── P3-6-commit-minimum.md           P3-6 done(2026-08-16)
│       └── 2026-08-17-audit-cycle/              case 2/3 audit 闭环(本会话合并)
│           ├── case-2-desktop-pet-v11-audit.md
│           ├── mentioned-but-not-parsed-closure.md(原 root,2026-08-17 移入)
│           ├── audit-fix-2026-08-16.md(原根,2026-08-17 移入)
│           ├── audit-fix-2026-08-17.md
│           └── audit-fix-2026-08-17-followup.md
├── audit-history/                               审计过程留痕
│   └── 2026-08-16-mentioned-but-not-parsed.md   子代理 B 14 条原始证据 + §5 后续
└── v12-physical-isolation/                      V12 物理隔离迁移检查清单(等 ADR,主版本升级)
    ├── V11.3-fact-stage-rationale.md
    └── migration-checklist.md
```

---

## §2 当前活跃待办(2026-08-17 第八轮 — case 2/3 audit 闭环后)

| ID | 文件 | 优先级 | 状态 | 主题 |
|----|------|--------|------|------|
| **audit-cycle-2026-08-17** | [audit-cycle-2026-08-17.md](audit-cycle-2026-08-17.md) | audit | **done**(2026-08-17) | case 2 (desktop-pet) + case 3 (ai-chat-openai-v11) audit 合并闭环 + V11 skill 修补 4 件 |

> **数量**:当前 `0 pending`。
> 累计已落地(2026-08-16 / 17):
> - 2026-08-16 batch-repair:14/14 done
> - 2026-08-16 P3-6 commit-minimum done
> - 2026-08-16 guard-smith audit B 方案 3 件系统化缺口 done
> - 2026-08-16 mentioned-but-not-parsed closure 5/5 done
> - 2026-08-16 V11.8.6 V12 物理隔离 6 步渐进 done
> - 2026-08-17 V11.8.7 audit-fix 7 项 5/7 done(F 留 case-only)
> - 2026-08-17 case 2 + case 3 audit 闭环 done(本期)

### §2.1 根目录保留文件说明

**`P0-v12-physical-rollout.md`**(保留不归档):
- 文件自身 §0 标 `done(2026-08-16)`,按 Article VIII 原则应归档
- **保留原因**:V12 升主版本前,该文件是 V11 → V12 路径"已对齐 V12"的协议层引用证据(ADR §1  / §5 Step 6 引用本文件)
- 当 V12 主版本升级完成时,本文件归档,所有引用方改成 V12 ADR
- V12 ADR §12 已显式引用本文件作 V11 harness 兼容层的来源

**`audit-cycle-2026-08-17.md`**(本期新建):
- 当前活跃证据(本期修补 4 件 + 13 个待修问题待 V12 升主版本时跟进)
- 已在归档目录 `archive/done/2026-08-17-audit-cycle/` 提供 raw md 历史

---

## §3 处理路由(主上下文 / 子代理怎么读)

```
MUST 主上下文进入 V11 任意会话前:
  → Read references/todos/README.md(本文件,30 行内)
  → 列出 needed_repair 摘要(max 200 字)
  → 由子代理修对应 todo时,头部注入 [TODO-REPAIR] tag + 限定读本目录单条 .md
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
| 主上下文兜底 | pytest 79 passed,真反例 4 件 |
| Commit | `f4d9303 [v11-repair-2] V11.8.5 + V11.8.5.P1 protocol-layer 收尾 + audit-fix 留置` |

### 4.2 2026-08-17 audit 闭环批次

| 维度 | 数值 |
|------|------|
| 归档目录 | [archive/done/2026-08-17-audit-cycle/](archive/done/2026-08-17-audit-cycle/) |
| 涵盖 | case 2 (desktop-pet-v11) 子代理 + case 3 (ai-chat-openai-v11) 主代理硬验收 |
| V11 skill 真实修补 | 4 件(commit-minimum-check.py / state-card-protocol.md §10.6 / V12-ADR-DRAFT §12 / prototype-backfill-check.py) |
| 待 V12 升主版本时跟进 | 13 个 case 3 followup 问题(已记入 audit-cycle-2026-08-17.md §3) |
| Commit | (本期) |

详见 [audit-cycle-2026-08-17.md](audit-cycle-2026-08-17.md)。

---

## §5 关联引用

- [references/config-files-glossary.md](../config-files-glossary.md) — 子代理 A 交付物
- [references/stage-physical-isolation.md](../stage-physical-isolation.md) — V12 提案原文(本目录 v12-physical-isolation/ 是其派生)
- [references/dependency-config.md](../dependency-config.md) — 协议层依赖配置
- [references/state-card-protocol.md](../state-card-protocol.md) — 状态卡 schema(2026-08-17 §10.6 AC 矩阵硬约束)
- [audit-cycle-2026-08-17.md](audit-cycle-2026-08-17.md) — 当前活跃闭环报告
- [audit-history/2026-08-16-mentioned-but-not-parsed.md](audit-history/2026-08-16-mentioned-but-not-parsed.md) — 子代理 B 14 条原始审计 + 主上下文接手 + commit 时间表