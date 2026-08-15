# 反例 6：14 模块串行未委派（Stage 6 Bug Fix Phase A）

> **V11.8.2 NEW**（Phase A 批量发现专属）。
>
> Stage 6 Bug Fix & Hunt 铁律 #8：模块数 ≤ 6 主代理亲自；> 6 必拆 sub-agent 并行（V11 §1.6）。
>
> 详见 [../references/bug-hunt-phase-a.md](../references/bug-hunt-phase-a.md) §A.2 + [../references/bug-hunt-battle-report.md §8 反例 2](../references/bug-hunt-battle-report.md)。

## 现象

```
主代理: for module in M1..M14: navigate + visible_text + screenshot  # ❌ 串行
14 × 平均 3 min = 42 min
（应拆 3 sub-agent × ~5 模块 = 15 min，节约 27 min）
```

## 根因

| 根因 | 占比 |
|------|:---:|
| spec 阶段未识别"模块数 = Task 数" | 50% |
| 主代理倾向"先自己跑一两个试试" | 30% |
| sub-agent 委派头部模板未强制要求 >6 拆 sub-agent | 20% |

## 失败案例（2026-08-15）

- **现象**：14 模块全程主代理亲自 navigate，全流程 90 min 中 42 min 浪费在串行
- **位置**：[V11.8.2 实战报告 §8 反例 2](../references/bug-hunt-battle-report.md)
- **影响**：浪费 27 min；主代理被 navigate 操作阻塞，无法同步做 evidence 整理

## 教训

**模块数判定**（V11 §1.6 强制）：

```yaml
≤ 6 模块: 主代理亲自跑（4 维度 × N 模块串行）
> 6 模块: 必拆 sub-agent 并行
14 模块拆 3 sub-agent:
  sub_agent_1: [M1 home, M2 art-style, M3 character, M4 asset, M5 script]
  sub_agent_2: [M6 storyboard, M7 shot, M8 video, M9 voice, M10 music]
  sub_agent_3: [M11 export, M12 publish, M13 analytics, M14 admin]
```

**主代理职责**：
1. 委派 3 sub-agent 后**只监控 + 拼接**，不发散
2. 收齐 3 个 report 后统一 update `docs/bugs/.state-card.md` + `index.md`
3. 跨 sub-agent 重复 bug 合并去重

## 正确替代

每个 sub-agent 必含 `[TOOL-HINTS]` 头部（详见 [../references/bug-hunt-battle-report.md §5](../references/bug-hunt-battle-report.md)）：

```yaml
[TOOL-HINTS]
  真登录: import { test, expect } from 'tests/e2e/fixtures/auth-fixture'
  bug 单: bash scripts/bug-hunt/new-bug.sh <bug_id> <module> <route> [severity] [evidence]
  HMR:   pwsh scripts/bug-hunt/dev-hmr-recovery.ps1 [-DryRun]
  截图:  pwsh scripts/bug-hunt/archive-screenshot.ps1 -Slug <slug> [-SubDir bug-hunt]
```

## 关联引用

- [../references/bug-hunt-phase-a.md](../references/bug-hunt-phase-a.md) — Phase A 3 步流程
- [../references/bug-hunt-battle-report.md §8 反例 2](../references/bug-hunt-battle-report.md) — V11.8.2 实战报告
- [../SKILL.md §铁律 8](../SKILL.md) — 14 模块 ≥ 7 必委派
- V11 SKILL.md §1.6 — 反 AI 自律（≤6 Task + LOW 主代理亲自；>6 必委派）