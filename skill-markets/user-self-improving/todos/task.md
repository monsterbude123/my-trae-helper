# user-self-improving — Task Log

> 工作日志 + 开放项。完成项带 ✅,未完成项带 ☐。
> 协议:`.agents/skills/user-self-improving/SKILL.md`(本页是其 todo 实际落点)。

---

## §A 本轮(2026-08-21)已完成

| ID | 任务 | 状态 | 备注 |
|----|------|------|------|
| A1 | 重命名 `self-improving-agent/` → `user-self-improving/`(目录 + SKILL.md frontmatter) | ✅ | 用户拍板新名 |
| A2 | 重写 SKILL.md 为「个人级补充入口」定位(与 `project-self-improving` 互补不重复) | ✅ | 见 SKILL.md §10 |
| A3 | 写 7 个 references(trae / claude-code / codex / copilot 接入 + hook-self-check + multi-agent-matrix + examples + best-practices + periodic-review + legacy-openclaw-handler) | ✅ | |
| A4 | assets/ 7 文件(LEARNINGS / ERRORS / FEATURE_REQUESTS / SOUL / TOOLS / MEMORY / SKILL-TEMPLATE) | ✅ | SOUL/TOOLS/MEMORY 为个人可选模板 |
| A5 | 删除 hooks/openclaw/(原 OpenClaw handler.ts/js/HOOK.md),搬到 references/legacy-openclaw-handler.md 明文 deprecated | ✅ | |
| A6 | scripts/ 写跨平台 POSIX sh(5 个:detect-node / hook-self-check / activator / error-detector / install-snippet) | ✅ | bash -n 全过 |
| A7 | install-snippet.sh 拆分 user-level / project-level + copilot 3 类 | ✅ | 见 SKILL.md §3 |

---

## §B 开放项 / TODO

### B-1:`scripts/self-improving-agent.mjs`(项目侧 shim)路径迁移

> 现有 `scripts/self-improving-agent.mjs` 是为原 `self-improving-agent` skill 设计的
> 项目侧 shim,与新 skill 不直接冲突,但需要评估:

| 子项 | 描述 | 状态 |
|------|------|------|
| B-1.1 | 评估现有 shim 的全局路径 `$HOME/.self-improving-agent/.learnings/` 是否需迁移到 `$HOME/.user-self-improving/.learnings/` | ☐ 留待评估 |
| B-1.2 | 决定新 skill 的默认 home 路径(本 skill SKILL.md §2 暂用 `$HOME/.user-self-improving/`) | ☐ |
| B-1.3 | 项目侧 shim 是否仍需保留(用户已切换 skill,但 shim 是工具而非 skill 本身) | ☐ |

### B-2:registry/skills.yaml 与 guard/gate 注册

| 子项 | 描述 | 状态 |
|------|------|------|
| B-2.1 | 委派 guard-smith 生成 `scripts/user-self-improving-guard.py`(薄壳 5 项检查) | ☐ 本轮末委派 |
| B-2.2 | 委派 guard-smith 在 `registry/skills.yaml` 注册 `user-self-improving` 条目 | ☐ |
| B-2.3 | 委派 guard-smith 生成 `.husky/user-self-improving-gate` + pre-commit 接入 | ☐ |
| B-2.4 | 更新 `skill-markets/MANIFEST.yaml` 新增 `user-self-improving` 条目 | ☐ |

### B-3:`CAPABILITY-MAP.md` 同步

| 子项 | 描述 | 状态 |
|------|------|------|
| B-3.1 | 原 `self-improving-agent` 行改为 `user-self-improving` + 新描述 | ✅ 2026-08-21 已通过 guard-smith 委派完成(CAPABILITY-MAP.md L300-302) |
| B-3.2 | 原 self-improving-agent 条目改为 deprecated,redirect_to: user-self-improving | ✅ 2026-08-21 已在 CAPABILITY-MAP.md 加 ⚠️ DEPRECATED 标注 |

### B-4:与 `project-self-improving` 共存验证

| 子项 | 描述 | 状态 |
|------|------|------|
| B-4.1 | 两个 skill 同时安装时不冲突(独立 home) | ✅ SKILL.md §10 已说明 |
| B-4.2 | `add-all` 同时装两个时是否需要警告 | ☐ 留待评估 |

---

## §C 关联引用

- [checklist.md](checklist.md) — 验收门禁(8 项硬检查 + 3 项软检查)
- [SKILL.md](../SKILL.md) — 主体文档
- [../project-self-improving/SKILL.md](../../project-self-improving/SKILL.md) — 项目内姐妹 skill
- [.trae/rules/learning.md](../../../../.trae/rules/learning.md) — 本仓库原 `.learnings/` 路由规则(本轮不动,仅作参考)