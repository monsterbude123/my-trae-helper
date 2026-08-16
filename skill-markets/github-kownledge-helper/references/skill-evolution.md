# 技能演进协议(skill 升级铁律)

> 沉淀自 AGENT.md §9。完成「大型任务」后必须升级 skill,不升级 = 经验丢失。
> 单文件 ≤ 200 行。
>
> **适用范围**:所有按"经验沉淀库"模式运营的 skill。其他 skill 也可参考。

## 1. 触发条件 — 5 类「大型任务」判定

满足**任一**条件即视为大型任务,触发强制升级:

| 类型 | 触发条件 |
|------|---------|
| **收录类** | 首次跑通 ADD 流程 / 新增仓库类型(monorepo / submodule / 私有仓 / 聚合目录)|
| **查询类** | 答了之前答不了的问题(新查询模式 / 新交叉验证路径)|
| **修复类** | 修复 clone/pull/索引的疑难 bug,且根因可复述 |
| **工作流** | 沉淀了新的可复用工作流模式 / 命令组合 |
| **显式触发** | 用户明确要求「升级 skill」/「记录这次经验」 |

**不触发升级**(避免误升级打断任务流):
- 单纯 `git pull` / 简单答疑(查 commit / tag)
- 文件改名 / 路径调整等纯重构
- 用户在提问「X 该放哪」但没真做任务

## 2. 5 步升级流程

```
大型任务完成 →
  Step 1: 识别可复用资产
    ├─ 新命令模式?(写入 references/commands.md 或 commands-<topic>.md)
    ├─ 新踩坑?(写入 references/pitfalls.md,编号续)
    ├─ 新工作流?(写入 references/workflows.md 或 workflows-<topic>.md)
    ├─ 新基线/Schema?(写入 references/<schema>.md)
    ├─ 新协议/红线?(写入 references/<protocol>.md)
    └─ 新脚本?(放入 skill scripts/ 或 references/scripts/,验证可跑通)

  Step 2: 沉淀写入
    ├─ 文档型 → references/<topic>.md(单文件 ≤ 200 行,超出按主题拆分)
    ├─ 脚本型 → 必须本地实跑通过,禁留报错 / 半成品脚本
    └─ 引用其他 Skill → 只写 Skill 名(如 doc-map-manager),不写绝对路径

  Step 3: 更新 SKILL.md
    ├─ 追加 CHANGELOG 条目(日期 + 任务摘要 + 沉淀位置)
    └─ 若触发条件或能力有变 → 更新 Description / Triggers 段

  Step 4: 双重记录
    ├─ SKILL.md CHANGELOG(必有)
    └─ AGENT.md §9.5 演进日志(必有,本项目专属时)

  Step 5: 清理
    ├─ 任务中的临时脚本 / 半成品 → 删除或归入 skill
    └─ scripts/ 下仅保留可跑通的脚本
```

## 3. 升级红线(必避免)

- ❌ 不复制 AGENT.md / project-rules.md 全文到 skill(单一事实源,skill 只放沉淀增量)
- ❌ 不留报错脚本 / 半成品脚本到 skill
- ❌ 单文件超过 200 行不拆分(具体项目可放宽,但默认按 200 行硬阈值)
- ❌ 升级不写 CHANGELOG = 没升级(双重记录缺失 = 无效升级)
- ❌ 引用其他项目绝对路径(破坏零外部目录依赖)
- ❌ 升级后留临时文件 / 半成品脚本(`scripts/` 下只保留可跑通的)
- ❌ 引用 process.env / os.homedir()(用 load_env 收口,见 env-loadenv.md)

## 4. 与其他 references 关系

- `workflows-baseline.md` → 升级时常新增的"基线工作流"
- `manifest-schema.md` → 升级时常新增的"Schema"
- `git-workflow-rules.md` / `doc-map-manager-usage.md` → 升级时常新增的"硬规则"
- `pitfalls.md` → 升级时常追加的反例库
- AGENT.md §9.5 演进日志 → 项目专属时双重记录