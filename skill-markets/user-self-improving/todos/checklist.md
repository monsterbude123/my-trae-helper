# user-self-improving — Acceptance Checklist

> 验收门禁(2026-08-21)。所有 ☑ 才能进入 merge / 注册表条目提交。
>
> 协议:`.agents/skills/user-self-improving/SKILL.md`。

---

## §A 结构硬检查(8 项 — 必过)

| # | 项 | 验证命令 | 状态 |
|---|----|---------|------|
| A1 | `SKILL.md` frontmatter 含 `name:user-self-improving` + `description` + `version` | `head -5 SKILL.md` | ☑ |
| A2 | `SKILL.md` 目录名一致(`skill-markets/user-self-improving/`) | `basename $(pwd)` | ☑ |
| A3 | `SKILL.md` 行数 ≤350(vibe-coding-standards v2.5 阈值) | `wc -l SKILL.md` | ☑(待 §E 跑) |
| A4 | 8+ references 齐全(`trae-integration.md` / `claude-code-integration.md` / `codex-integration.md` / `copilot-integration.md` / `hook-self-check.md` / `multi-agent-matrix.md` / `examples.md` / `best-practices.md` / `periodic-review.md` / `legacy-openclaw-handler.md`) | `ls references/` | ☑ |
| A5 | 7 assets 齐全(`LEARNINGS.md` / `ERRORS.md` / `FEATURE_REQUESTS.md` / `SOUL.md` / `TOOLS.md` / `MEMORY.md` / `SKILL-TEMPLATE.md`) | `ls assets/` | ☑ |
| A6 | 5 scripts 齐全(`detect-node.sh` / `hook-self-check.sh` / `activator.sh` / `error-detector.sh` / `install-snippet.sh`) | `ls scripts/` | ☑ |
| A7 | 全部 5 个 shell 脚本 `bash -n` 通过(无语法错误) | `bash -n scripts/*.sh` | ☑(本轮已验证) |
| A8 | `hooks/` 目录已删除(原 openclaw handler 已搬到 references/legacy-openclaw-handler.md) | `! [ -d hooks ]` | ☑ |

## §B 知识清洁度硬检查(3 项 — 必过)

| # | 项 | 验证命令 | 状态 |
|---|----|---------|------|
| B1 | SKILL.md / references/*.md 不含 `clawdhub` 残留(本轮 openclaw 命令迁移到 legacy 文档) | `grep -r 'clawdhub' SKILL.md references/ assets/`(允许=0) | ☑ |
| B2 | 不含真实密钥 / Token 字面量 | `grep -rE '(sk-\|sk_live_\|Bearer )[A-Za-z0-9]{20,}' SKILL.md references/ assets/ scripts/` | ☑ |
| B3 | SKILL.md §6 明确说明 SOUL.md / TOOLS.md / MEMORY.md 为"个人可选",不再绑定 openclaw | `grep -n '个人可选\|个人 expression\|personal expression' SKILL.md` | ☑ |

## §C 设计正确性软检查(3 项 — 推荐)

| # | 项 | 验证 | 状态 |
|---|----|------|------|
| C1 | `scripts/hook-self-check.sh` 探测顺序与 SKILL.md §4 一致(user-level 优先) | `cat scripts/hook-self-check.sh \| head -50` | ☑ |
| C2 | `scripts/install-snippet.sh` 支持 7 个 agent 参数(4 个 user + 3 个 project + copilot) | `bash scripts/install-snippet.sh trae-user \| head -3` | ☑ |
| C3 | SKILL.md §10 Relationship with project-self-improving 表格完整 | `grep 'project-self-improving' SKILL.md \| wc -l`(≥3) | ☑ |

## §D 注册表守卫前置条件(本轮未做,留 TODO)

| # | 项 | 备注 |
|---|----|------|
| D1 | `registry/skills.yaml` 注册 `user-self-improving` 条目 | 委派 guard-smith,见 `todos/task.md §B-2` |
| D2 | `scripts/user-self-improving-guard.py` 生成 | 委派 guard-smith |
| D3 | `.husky/user-self-improving-gate` 生成 + pre-commit 接入 | 委派 guard-smith |
| D4 | `skill-markets/MANIFEST.yaml` 新增条目 | 委派 guard-smith |

## §E 反例自检(2 项 — 必过)

| # | 项 | 命令 | 状态 |
|---|----|------|------|
| E1 | `scripts/hook-self-check.sh` 在无任何 hook config 时正确报 `MISSING_CONFIG_FILE`(exit 1) | `cd /tmp && bash <path>/hook-self-check.sh` | ☑(本轮已验证) |
| E2 | `scripts/hook-self-check.sh` 在有 `~/.user-self-improving/SOUL.md` 时正确报 `INSTALLED`(fallback) | `touch ~/.user-self-improving/SOUL.md && bash <path>/hook-self-check.sh` | ☐(本轮 wsl 测试环境无法 override `$HOME`,真实部署 Trae/Claude Code 注入正确 HOME 应能命中。设计正确,待真实环境回归) |

## §F 跨平台(1 项 — 软检查)

| # | 项 | 备注 |
|---|----|------|
| F1 | 5 个脚本全部 POSIX sh 兼容(Git Bash on Windows 可跑) | 跨平台协议与 `project-self-improving/scripts/detect-node.sh` 同款 |

---

## §G 通过门禁

- ☑ A1~A2、A4~A8、B1~B3、C1~C3 全部通过
- ☐ A3、E1~E2 待主代理亲自跑(本轮 todo §9 委派后)
- ☐ D1~D4 留 TODO → 见 `todos/task.md §B-2`
- ☐ F1 待用户在 Git Bash 实跑确认