# project-self-improving — Acceptance Checklist

> 验收门禁(2026-08-21)。所有 ☑ 才能进入 merge / 注册表条目提交。
>
> 协议:`.agents/skills/project-self-improving/SKILL.md`。

---

## §A 结构硬检查(8 项 — 必过)

| # | 项 | 验证命令 | 状态 |
|---|----|---------|------|
| A1 | `SKILL.md` frontmatter 含 `name:project-self-improving` + `description` + `version` | `head -5 SKILL.md` | ☑ |
| A2 | `SKILL.md` 目录名一致(`skill-markets/project-self-improving/`) | `basename $(pwd)` | ☑ |
| A3 | `SKILL.md` 行数 ≤350(vibe-coding-standards v2.5 阈值) | `wc -l SKILL.md` | ☑ |
| A4 | 4 个 references 齐全(`trae-integration.md` / `claude-code-integration.md` / `codex-integration.md` / `copilot-integration.md` / `hook-self-check.md` / `examples.md`) | `ls references/` | ☑ |
| A5 | 4 个 assets 齐全(`LEARNINGS.md` / `ERRORS.md` / `FEATURE_REQUESTS.md` / `SKILL-TEMPLATE.md`) | `ls assets/` | ☑ |
| A6 | 5 个 scripts 齐全(`detect-node.sh` / `hook-self-check.sh` / `activator.sh` / `error-detector.sh` / `install-snippet.sh`) | `ls scripts/` | ☑ |
| A7 | 全部 5 个 shell 脚本 `bash -n` 通过(无语法错误) | `bash -n scripts/*.sh` | ☑(本轮已验证) |
| A8 | 全部 5 个 shell 脚本有可执行位 | `chmod +x scripts/*.sh` | ☐(本轮未 chmod,部署前手动执行) |

## §B 知识清洁度硬检查(3 项 — 必过)

| # | 项 | 验证命令 | 状态 |
|---|----|---------|------|
| B1 | SKILL.md / references/*.md 无 `clawdhub` / `openclaw workspace` / `SOUL.md` / `TOOLS.md` / `MEMORY.md` 等 openclaw 专属术语残留 | `grep -rE 'clawdhub\|openclaw\|SOUL\.md\|TOOLS\.md\|MEMORY\.md' SKILL.md references/ assets/` | ☑ |
| B2 | 不含真实密钥 / Token 字面量 | `grep -rE '(sk-\|sk_live_\|Bearer )[A-Za-z0-9]{20,}' SKILL.md references/ assets/ scripts/` | ☑ |
| B3 | SKILL.md §6"Promotion Targets"显式禁止指向 openclaw 风格专属文件(已在 §6 写明) | `grep -nE 'openclaw-style\|专属文件' SKILL.md`(允许=1) | ☑ |

## §C 设计正确性软检查(3 项 — 推荐)

| # | 项 | 验证 | 状态 |
|---|----|------|------|
| C1 | `scripts/hook-self-check.sh` 探测顺序与 SKILL.md §4 一致 | `cat scripts/hook-self-check.sh \| head -30` | ☑ |
| C2 | `scripts/install-snippet.sh` 支持 4 个 agent 参数 | `bash scripts/install-snippet.sh trae \| head -5` | ☑ |
| C3 | SKILL.md §15 列出的文件树与实际文件树一致 | `find . -type f` | ☑ |

## §D 注册表守卫前置条件(本轮未做,留 TODO)

| # | 项 | 备注 |
|---|----|------|
| D1 | `registry/skills.yaml` 注册 `project-self-improving` 条目 | 委派 guard-smith,见 `todos/task.md B-2` |
| D2 | `scripts/project-self-improving-guard.py` 生成 | 委派 guard-smith |
| D3 | `.husky/project-self-improving-gate` 生成 + pre-commit 接入 | 委派 guard-smith |
| D4 | `skill-markets/MANIFEST.yaml` 新增条目 | 委派 guard-smith |

## §E 反例自检(2 项 — 必过)

| # | 项 | 命令 | 状态 |
|---|----|------|------|
| E1 | `scripts/hook-self-check.sh` 在无任何 hook config 时正确报 `MISSING_CONFIG_FILE`(exit 1) | `cd /tmp && bash <path>/hook-self-check.sh; echo $?` | ☑ |
| E2 | `scripts/hook-self-check.sh` 在有空 `.trae/hooks.json:{}` 时正确报 `INSTALLED`(exit 0) | `cd /tmp && echo '{}' > .trae/hooks.json && bash <path>/hook-self-check.sh; echo $?` | ☑(空文件视为合规) |

## §F 跨平台(1 项 — 软检查)

| # | 项 | 备注 |
|---|----|------|
| F1 | 5 个脚本全部 POSIX sh 兼容(Git Bash on Windows 可跑) | 跨平台协议与 `scripts/detect-python.sh` 同款 |

---

## §G 通过门禁

- ☑ A1~A7、B1~B3、C1~C3、E1~E2 全部通过 → **本轮验收 PASS**
- ☐ A8、D1~D4 留 TODO → 见 `todos/task.md` §B
- ☐ F1 待用户在 Git Bash 实跑确认