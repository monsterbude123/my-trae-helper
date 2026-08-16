# P3-6(2026-08-16 抽出独立)

> 本条目从 P3-cross-skill-and-doc.md 抽出独立。原 P0-P1-P2-P3 13 条已 done,2026-08-16 物理归档至 [archive/done/2026-08-16-batch-repair/](archive/done/2026-08-16-batch-repair/P3-cross-skill-and-doc.md)。
>
> **本文件保留原因**:状态仍为 pending,等后续会话或用户明确要求时再修。

---

## P3-6 — §3.7 #10 范围盲目扩大反例无程序化检测

```yaml
---
id: AUDIT-#13
title: scripts/commit-minimum-check.py 实现 commit 准入最小集
status: pending
priority: P3
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: SKILL.md L508 §3.7 #10 commit 准入最小集 ≠ 全量验收
              references/common-anti-patterns.md §7.3
parser_ref: grep `commit.*准入最小集|MINIMUM_COMMIT_CRITERIA` 在 scripts/ 中零命中
fix_path: scripts/commit-minimum-check.py 新建
resolver_sub_agent_exclusion_note: 子代理 2026-08-16 范围排除;本条留待后续会话或用户明确要求时再修
---
```

§3.7 #10 反例只在 md 描述,scripts/ 无任何程序化检测(主上下文自觉)。

修复:scripts/commit-minimum-check.py 校验 `lint pass + 关键 5 路由 spot-check 存在 + admin 探针 200`;Stage 3.5/4.5 默认异步由本脚本显式声明。

---

## 关联引用

- 已完成 commit `39d4f78` "V11.8.x 协议层承诺 → 脚本落地(13/14 done + 1 留置)" — 本条即"1 留置"
- 原 P3 file 位置 [archive/done/2026-08-16-batch-repair/P3-cross-skill-and-doc.md](archive/done/2026-08-16-batch-repair/P3-cross-skill-and-doc.md)(锁定不可改)
