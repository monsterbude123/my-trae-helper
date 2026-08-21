# project-self-improving — Task Log

> 工作日志 + 开放项。完成项带 ✅,未完成项带 ☐。
> 协议:`.agents/skills/project-self-improving/SKILL.md`(本页是其 todo 实际落点)。

---

## §A 本轮(2026-08-21)已完成

| ID | 任务 | 状态 | 备注 |
|----|------|------|------|
| A1 | 诊断原 `self-improving-agent/` 的 openclaw 习惯与 coding 项目矛盾点(9 处) | ✅ | 见会话对话 |
| A2 | 与用户确认新名 `project-self-improving` + 通用 skills 定位 | ✅ | 用户拍板 |
| A3 | 创建 `skill-markets/project-self-improving/` 骨架(SKILL.md + 5 references + 4 assets + 5 scripts) | ✅ | 本轮 |
| A4 | 写跨平台脚本(hook-self-check / activator / error-detector / install-snippet / detect-node) | ✅ | POSIX sh,无 Python/Node 依赖 |
| A5 | 起草 `scripts/hook-self-check.sh` 必跑协议(§4) | ✅ | 见 SKILL.md §4 |
| A6 | 通用 4 agent 接入(Trae / Claude Code / Codex / Copilot)各自独立 reference | ✅ | references/ |
| A7 | 标记原 `self-improving-agent` 角色为"用户全局陪跑",待后续单独定义 | ✅ → 见 §B-1 | 用户拍板 |

---

## §B 开放项 / TODO

### B-1:原 `self-improving-agent` 的角色定位(用户指示留 TODO,本次不动)

> 用户原话:**"保留原版 self-improving-agent 然后我希望它的角色后续是陪着用户的进行全局的经验提炼,不过不是先现在需要关注的内容,可以标记 todo"**

| 子项 | 描述 | 状态 |
|------|------|------|
| B-1.1 | 在 `skill-markets/self-improving-agent/SKILL.md` 顶部加 deprecated 标识 | ☐ 留待用户后续单独做 |
| B-1.2 | 写"用户全局陪跑"角色说明文档(独立 references/user-companion.md) | ☐ |
| B-1.3 | 决定是否与 `project-self-improving` 二者互斥安装(`.learnings/` 路径冲突) | ☐ |
| B-1.4 | 更新 CAPABILITY-MAP.md 区分"项目级 self-improving" vs "用户全局 self-improving-agent" | ☐ |

### B-2:guard/gate 注册委派(本轮留 TODO)

> 用户原话:**"同步委派 guard-smith 注册 scripts + gate(严格)"** — 因 §1.11 写权范畴,
> 主代理不能直接改 `registry/skills.yaml` / `scripts/<name>-guard.*` / `.husky/<name>-gate`。
> 需要委派 guard-smith sub-agent 执行。

| 子项 | 描述 | 状态 |
|------|------|------|
| B-2.1 | 委派 guard-smith 生成 `scripts/project-self-improving-guard.py`(薄壳 6 项检查) | ☐ 本轮末未委派 |
| B-2.2 | 委派 guard-smith 在 `registry/skills.yaml` 注册 `project-self-improving` 条目 | ☐ |
| B-2.3 | 委派 guard-smith 生成 `.husky/project-self-improving-gate` + pre-commit 接入 | ☐ |
| B-2.4 | 更新 `skill-markets/MANIFEST.yaml` 新增 `project-self-improving` 条目 | ☐ |

### B-3:`skill-acceptance §8 Self-Check Iron Law` 起草

> 用户原话:**"希望这个市场以后所有的 skills 都需要有一个自检的机制,这个放到我们这个市场的通用开发规范里"**

| 子项 | 描述 | 状态 |
|------|------|------|
| B-3.1 | 在 `skill-markets/skill-acceptance/SKILL.md` 新增 §8"通用 Self-Check Iron Law" | ☐ |
| B-3.2 | §8 内容:每个 skill 应自带 `scripts/<name>-self-check.sh`(POSIX sh,无依赖);在 SKILL.md §X 明示触发时机 + 失败 remediation | ☐ |
| B-3.3 | §8 反例库:不写 self-check = 用户永远不会知道 skill 是否生效 / 已 broken | ☐ |
| B-3.4 | §8 与本 skill 的关系:`project-self-improving` 的 `hook-self-check.sh` 即 §8 的第一个标杆实现 | ☐ |

### B-4:`self-improving-agent.mjs`(项目侧 shim)对 `project-self-improving` 的支持

> 现有 `scripts/self-improving-agent.mjs` 是为原 `self-improving-agent` skill 设计的
> 项目侧 shim,与新 skill 不直接冲突,但需要评估:

| 子项 | 描述 | 状态 |
|------|------|------|
| B-4.1 | 评估 `scripts/self-improving-agent.mjs` 的全局路径 `$HOME/.self-improving-agent/.learnings/` 是否仍合理 | ✅ 2026-08-21 完成:shim 默认 home 已迁移到 `$HOME/.user-self-improving/`,旧路径向后兼容,提供 `migrate` 子命令一次性 cp 旧数据(用户已迁移并删除旧路径) |
| B-4.2 | 决定新 skill 的默认 `.learnings/` 路径(项目内 `.learnings/` vs 全局 `~/.project-self-improving/.learnings/`) | ✅ 2026-08-21 确定:`project-self-improving` 默认 `<repo>/.learnings/`;`user-self-improving` 默认 `$HOME/.user-self-improving/.learnings/`。两者互补,不冲突 |

### B-5:`MANIFEST.yaml` 注册前置条件

| 子项 | 描述 | 状态 |
|------|------|------|
| B-5.1 | SKILL.md §15 列出的文件树已实际创建(待主代理自验收) | ✅ 2026-08-21 已通过 guard-smith 委派生成 `scripts/project-self-improving-guard.py` 验证 |
| B-5.2 | 跨平台脚本 `bash -n` 全部通过(2026-08-21 已验证 5 个) | ✅ |

### B-6:全局安装(2026-08-21 完成)

| 子项 | 描述 | 状态 |
|------|------|------|
| B-6.1 | 用 `node bin/cli.mjs add project-self-improving -g -a trae-cn -y` 装到 `~/.trae-cn/skills/` | ✅ |
| B-6.2 | 验证 junction + ReparsePoint 指向 `skill-markets/project-self-improving/` | ✅ |
| B-6.3 | 同时装 `user-self-improving` 到全局(互补,提供 `~/.user-self-improving/` 个人体验 ledger) | ✅ |

---

## §C 关联引用

- [checklist.md](checklist.md) — 验收门禁(8 项硬检查 + 3 项软检查)
- [SKILL.md](../SKILL.md) — 主体文档
- [.agents/rules/learning.md](../../../../../.agents/rules/learning.md) — 本仓库原 `.learnings/` 路由规则(本轮不动,仅作参考)

---

## §D 推迟项(本轮不做 — 留给后续 session)

> 用户明确要求**"所有能后续说的,这次就先不做"**,且担心"实时升级的部分过分设计"。
> 以下7 项已记录为未来工作,本轮不实现。

| # | 推迟项 | 推迟理由 | 后续触发条件 |
|---|--------|---------|------------|
| D-1 | `scripts/review.sh` 自动化 review 工具(扫3+ See Also / 过期 / SOUL.md >50 行) | 过分设计 — 原版只要求人工4 动作 review | 当 `.learnings/` 任意文件 > 50K bytes |
| D-2 | `**Status**: archived` 字段加入 entry schema | 过分设计 — 原版只有 5 状态 | 当任何 entry `**Logged**` 日期 > 6 月 + 仍未 promote |
| D-3 | 立即首次 review `LEARNINGS.md` 32K 内容 | 过分设计 — 数据刚迁移完,本身就是"待 review" | D-1 review 工具就绪后 |
| D-4 | 多层 cadence 定时器(per-session / weekly / monthly / quarterly 自动 cron | 过分设计 — cadence 是"指导原则",不需要自动化执行 | 当人工 cadence 实际 review 太晚才发现过期 |
| D-5 | `add-all` 同时装 `project-self-improving` + `user-self-improving` 是否警告 | 不急 — 当前两 skill 已手动装好 | `add-all` 实测踩到双装冲突时 |
| D-6 | 重命名 shim 文件名 `self-improving-agent.mjs` → `user-self-improving.mjs` | 风险高(可能破坏 `package.json` scripts引用 + `.husky/post-commit` 调用) | 等 `.husky/post-commit` 链路稳定无问题后 |
| D-7 | 彻底废弃 `SELF_IMPROVING_HOME` 旧 env 名 | 当前两 env 名都支持,需 deprecation 周期 | 等所有文档/调用方迁移完成 |

---

## §E 后续 session 入口

> 当用户将来要"整理 `self-improving` 经验"时,按以下顺序:

1. **先 D-1 自动化 review 工具**(`scripts/review.sh` — 先有自动化再人工)
2. **跑一次全量 review**( D-1 跑出来 3+ See Also / 过期 / 重复条目 → 人工决策)
3. **批量 resolve / promote / archive / extract-skill**(一次性消化)
4. **再考虑 D-4 cadence 自动化**(在 review 节奏稳定后)
5. **D-6 是"基础设施升级",与经验整理无关,放最后**(D-7 已完成,移除)

**绝不先做 D-2 字段加法**(否则新 schema 与原版不兼容,破坏数据迁移承诺)。