# Best Practices

> 主入口: [SKILL.md §14](../SKILL.md#14-best-practices)。
> 项目经验沉淀的 10 条操作纪律。

---

## §1 写作纪律

1. **Log immediately** — context is freshest right after the issue.
2. **Be specific** — future agents must understand without original chat.
3. **Include reproduction steps** — especially for errors.
4. **Link related files** — makes fixes easier.
5. **Suggest concrete fixes** — not just "investigate".
6. **Use consistent categories** — enables filtering.

## §2 提升纪律

7. **Promote carefully** — only to files the active agent reads (§6).
8. **Don't bind to a single agent** — `.learnings/` is portable. Only the hook
   snippet is agent-specific.

## §3 运维纪律

9. **Self-check before complaining** — if a hook didn't fire, run
   `scripts/hook-self-check.sh` before assuming the skill is broken.
10. **Review regularly** — stale learnings lose value (see
    [`periodic-review.md`](periodic-review.md)).

## §4 反例(每条都对应 1 个真实 trap)

| # | 反例 | 后果 |
|---|------|------|
| 1 | 不写 `.learnings/` 而直接修改 `AGENTS.md` 灌经验 | `AGENTS.md` 膨胀 + 上下文击穿 |
| 2 | 把 entry 提升到 openclaw 专属 `SOUL.md` / `TOOLS.md` | 知识污染(本 skill 的根因) |
| 3 | 装本 skill 后不跑 `hook-self-check.sh` | hook 配置错 / 路径错时**永远沉默** |
| 4 | `.learnings/` 推到 git 但 `AGENTS.md` 不更新 | team 看不到最新结论 |
| 5 | 3+ `See Also` 但不升级成 rule / skill | 重复犯错不收敛 |
| 6 | hook 装到错的 config 文件(Trae 写到 `.claude/settings.json`) | 永不触发 |
| 7 | `**Status**: promoted` 但不填 `**Promoted**: <file>` | 无法追到目标 |
| 8 | 不写 reproduction 就 `**Status**: resolved` | 下次复发不知如何 repro |
| 9 | 让 `add-all` 顺带把本 skill 装到全局时也启用 hook | 用户没主动启用却被自动启用 |
| 10 | 把别人的 `.learnings/` 抄到自己项目但忘了改 ID 前缀日期 | 历史时间线错乱 |

## §5 See Also

- [SKILL.md §14 Best Practices](../SKILL.md#14-best-practices)
- [SKILL.md §6 Promotion Targets](../SKILL.md#6-promotion-targets)
- [references/periodic-review.md](periodic-review.md)
- [skill-markets/agent-dev-control-kit/references/traps.md](../../agent-dev-control-kit/references/traps.md) — `self-improvement` section 深入反例库