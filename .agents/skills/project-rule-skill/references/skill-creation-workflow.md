---
description: skill 创建/更新/升级的工作流引导 — 协议先行 + 多维度一致。覆盖新建、升级、合并、废弃 4 种场景。覆盖 SKILL/reference/workflow/script/guard/其他引用 6 个维度。必读于任何 skill 变更操作之前。
alwaysApply: false
enabled: true
updatedAt: 2026-08-15
provider:
---

# Skill 创建/更新工作流 — 协议先行 + 多维度一致

> **核心铁律**:任何 skill 创建 / 更新 / 升级 / 合并 / 废弃,必走**协议先行** —— 先文档,后代码;**多维度同步** —— 6 个维度必须引用同一份协议,不留尾巴。
> **失败模式**:做了一半忘了一半 → 后续 agent 接续不上 → 标准漂移 → 用户反复纠正。
> **防失败原则**:**全有或全无**(all-or-nothing) —— 任何一步漏了 = 整体回滚或全部补齐,不做"完成 70%"状态。

---

> **V11.8.0.1 路径迁移通知(2026-08-15 NEW)**:本文件原在 `.agents/rules/skill-creation-workflow.md`,V11.8.0.1 起迁移到 `.agents/skills/project-rule-skill/references/skill-creation-workflow.md`(与 project-rule-skill 同包,作为其 references/)。
> **原因**:让规则文件集中在 skill 入口网关下,避免散落多处。原路径已留 redirect stub。

---

## §1 协议先行(Protocol First)

任何 skill 创建/更新/升级之前,先写**协议规范文件**(`<topic>-protocol.md`),协议规范必须包含:

1. **scope**:适用范围(package / global / workflow / protocol-coverage / catalog-diff)
2. **必填元数据**:对 SKILL 的硬性要求(name + description + frontmatter schema)
3. **结构规则**:行数 / 文件路径 / frontmatter 字段数 / 多维度同步约束
4. **反例库**:AP-{n} 编号,每条带 detect 方法
5. **测试要求**:pytest 用例 / 自验收样例 / CI gate 接入点
6. **协议版本**:V{major.minor} + 更新日志

**禁止**:先写代码再补协议。**先文档,后代码。**

---

## §2 多维度同步(Multi-Dim Sync)

### 2.1 6 个维度

任何 skill 变更必须同步更新下列 6 个维度(缺一项 = 该 skill 视为未完成):

| # | 维度 | 文件位置 | 例 |
|:-:|------|----------|----|
| 1 | SKILL.md 本体 | `skill-markets/<pkg>/SKILL.md` | frontmatter + 骨架流程 |
| 2 | references/ | `skill-markets/<pkg>/references/*.md` | 详细文档 |
| 3 | workflow | `skill-markets/<pkg>/skills/*/workflows/*.md` | 多阶段流程(若有) |
| 4 | script | `skill-markets/<pkg>/scripts/*.py` | 程序化检测(若有) |
| 5 | guard | `scripts/<pkg>-guard.{py,mjs}` 或 `src/guards/*.mjs` | 守卫(若有) |
| 6 | 其他引用 | AGENTS.md / CHANGELOG / SECURITY-MAP / README / `.agents/skills/project-rule-skill/references/*` | 跨文档引用(V11.8.0.1 后原 .agents/rules/ 已迁移) |

### 2.2 6 维度同步约束(强制)

- ✅ **新增**:6 个维度文件同时落地(同一 commit)
- ✅ **修改**:任一维度修改,触发 §2.3 全维度自检
- ✅ **废弃**:6 个维度文件同时清理(同一 commit)
- ❌ **禁止**:只改 1 个维度,其余漏改 = 标准漂移反例 AP-1
- ❌ **禁止**:旧 commit 留尾巴(典型:新协议上线但旧 SKILL 仍引用旧协议)

### 2.3 全维度自检 checklist

每次改动后,跑下列命令全量核对:

```bash
# 1. AGENTS.md / CHANGELOG / README / SECURITY-MAP 是否同步
grep -r "<新协议名>" {AGENTS.md,CHANGELOG.md,README.md,SECURITY-MAP.md} 2>&1

# 2. protocol coverage 自检(若有 protocol 规范)
python scripts/_check_protocol_coverage.py --protocol .agents/skills/project-rule-skill/references/<topic>-protocol.md --scope global --check

# 3. skill catalog 自检(若有 SKILL 变更)
python tests/catalogs/_check_skill_catalog.py --catalog tests/catalogs/skill-catalog.yaml --skills-root skill-markets

# 4. registry/skills.yaml 是否注册(guard/gate)
python -c "import yaml; print('OK' if '<skill>' in yaml.safe_load(open('registry/skills.yaml')) else 'FAIL')"
```

---

## §3 4 种场景的标准流程

### 3.1 新建 skill

1. **协议先行** — 写 `<topic>-protocol.md`(若新类目无协议,新建)
2. **创建目录** — `skill-markets/<name>/` + `SKILL.md` frontmatter(name + description + version)
3. **写 SKILL.md** — frontmatter + 核心铁律 + 骨架流程内联
4. **写 references/** — 详细文档(按需)
5. **写 workflows/** — 多阶段流程(按需)
6. **写 scripts/** — 程序化检测(按需)
7. **写 guard** — `scripts/<name>-guard.{py,mjs}` + registry 注册(按需)
8. **更新多维度** — AGENTS.md §7 / CHANGELOG / SECURITY-MAP / README / `.agents/skills/project-rule-skill/SKILL.md`
9. **pytest** — 至少 3 个用例(必填 + 推荐 + 反例)
10. **CI gate** — `.github/workflows/skill-market-gate.yml` 接入
11. **catalog** — `tests/catalogs/skill-catalog.yaml` 加 SKILL 条目

### 3.2 升级 skill(版本 +1)

1. **读旧协议** — 确认旧 `*-protocol.md` 仍有效(若过期先升协议)
2. **写新 SKILL.md** — frontmatter 加 version + 保留旧 references/ 引用
3. **新增 references/** — 不覆盖旧文件,加 `<feature>.md`(指针引用,避免大改)
4. **更新多维度** — AGENTS.md / CHANGELOG(条目 + version) / SECURITY-MAP(若有新风险)
5. **保持 registry** — `registry/skills.yaml` 不动,只更新 `<pkg>` 的 version 字段
6. **pytest 增量** — 加新用例,旧用例不删
7. **CI gate** — 同步 L3/L4 触发条件

### 3.3 合并 skill(2 → 1)

1. **读两个旧协议** — 确认合并后的协议覆盖双方
2. **新协议** — `<topic>-protocol.md` v{合并后版本}
3. **新 SKILL.md** — 整合双方 frontmatter + 骨架
4. **references/** — 合并,删除重叠(保留指针引用)
5. **scripts/** — 若重复,去重(参考 CAPABILITY-MAP §共享能力)
6. **workflows/** — 合并,删除重复 stage
7. **更新多维度** — AGENTS.md §7 / CHANGELOG / SECURITY-MAP / README
8. **registry** — 旧 entries 删除,新 entry 注册
9. **守卫** — 旧 `<pkg>-guard.*` 删除或合并
10. **CI** — 旧 workflow 移除,新 workflow 接入

### 3.4 废弃 skill

1. **协议标记 DEPRECATED** — `<topic>-protocol.md` 标废弃,指引新协议
2. **移动目录** — `skill-markets/<name>/` → `_archived_<ts>/<name>/`(不进 registry)
3. **references/** — 加 DEPRECATED banner + 新协议引用
4. **更新多维度** — AGENTS.md §7 / CHANGELOG / SECURITY-MAP
5. **registry** — 删除 entry(不留在白名单)
6. **守卫** — `<pkg>-guard.*` 删除 + `<pkg>-gate` 标记 skip
7. **CI** — workflow 移除或跳过

---

## §4 反例库(本协议级)

| AP# | 反例 | 检测 | 修复 |
|-----|------|------|------|
| **AP-1** | 标准漂移 | `git log --oneline -p` 搜 frontmatter 变更 | 多维度同步重跑 §2.3 |
| **AP-2** | 协议先写一半就 commit | `git diff` 看 `<topic>-protocol.md` 完整度 | 补全协议再 commit |
| **AP-3** | SKILL 升级但 registry 漏更新 | `node src/guards/skill-registration-guard.mjs <pkg>` | 更新 registry |
| **AP-4** | pytest 用例低于 3 个 | `python -m pytest tests/unit/test_<pkg>.py --collect-only -q` | 加用例 |
| **AP-5** | CI gate 没接入 | `grep -r "<pkg>" .github/workflows/` | 加 workflow job |
| **AP-6** | SECURITY-MAP 漏评 | `grep -r "<pkg>" SECURITY-MAP.md` | 跑 trae-security-review + 评分 |
| **AP-7** | agent-hints 累积未消费 | `wc -l logs/agent-hints.jsonl` | `self-improving-agent scan-hints` |
| **AP-8** | post-commit 钩子跳过 | `cat .husky/post-commit` | 重启 hook |
| **AP-9** | 主 agent 漏调 signal-detect | 响应缺 `[signal-scanned]` 标记 | 强制 §7.4 标记 |
| **AP-10** | 临时文件未进 logs/ | `find . -newer .gitignore` | 移到 `logs/` 或删除 |
| **AP-11** | protocol 改但 catalog 没改 | `tests/catalogs/_check_skill_catalog.py --strict` | 同步 catalog |
| **AP-12** | "N 个"数字声明不带证据 | ls/glob/Read 精确计数 | 首轮列清单 |
| **AP-13** | 跨平台路径硬编码 | `grep -r "/mnt/c/" scripts/` | 用 detect-python.sh |
| **AP-14** | P0/P1/P2 配硬性条数 | 文档搜 "N 条 P0" | 改"做完或不做" |
| **AP-CAT-1** | skill-catalog required 字段缺失 | catalog V2 实跑 | 批量补或降为 recommended |
| **AP-CAT-2** | recommended 字段被当必填 | catalog V2 --strict | 移除 required |

---

## §5 一句话总结

**协议先行 + 多维度同步 = V11.7.1 整改模式;全有或全无 = V11.8.0 防做一半原则。**

---

## §6 关联

- **本协议程序化配套**:`references/protocol-coverage-protocol.md`(同目录)
- **短细则**:`references/skills-development-rules.md`(同目录,中文转英文后命名)
- **skill 加载入口**:`.agents/skills/project-rule-skill/SKILL.md` Step 5 路由表
- **catalog 配套**:`tests/catalogs/catalog-protocol.md`(skill 元数据校验协议)