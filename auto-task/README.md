# auto-task — 项目自动任务管理机制

> **定位**:项目级"定时/周期自动任务"统一管理目录。**不是 Skill,不修改 agent 行为**;
> 仅作为**手动配置/重放**入口,配合外部调度器(TRAE Work / cron / GitHub Actions)使用。
>
> **使用场景**:把需要每天/每周/每月跑一次的"调研 + 自检 + 报告生成"类任务,
> 固化为可重放的提示词 + 运行配置。agent 跑完仍只生成报告,不修改仓库任何文件。

---

## §1 设计原则(5 条)

1. **不创建 Skill** — auto-task 不在 `skill-markets/` 下,不进 CAPABILITY-MAP.md,**仅作为提示词仓库**
2. **零外部依赖** — 一个任务 = 一个文件夹,自包含 `prompt.md`(TRAE 复制用) + `config.yaml`(调度配置) + `README.md`(说明)
3. **路径相对化** — 所有 `prompt.md` 内**禁止绝对路径**,一律用 `${WORKSPACE}` 或相对路径(由调度器运行时注入)
4. **幂等输出** — 输出到 `logs/<task-name>/<date>/`,由 agent 按日期归档
5. **可扩展** — 新加一个自动任务 = `auto-task/<new-task>/` 三个文件,不修改其他目录

---

## §2 目录结构

```
auto-task/
├── README.md                       # 本文件(机制说明)
├── REGISTRY.md                     # 自动任务清单(全量索引)
└── <task-name>/                    # 每个自动任务一个子目录
    ├── README.md                   # 任务说明(给阅读者)
    ├── prompt.md                   # ★ TRAE Work 复制用提示词(唯一必需文件)
    └── config.yaml                 # 调度配置(cron / 时区 / 输出路径)
```

### 2.1 字段约定(`config.yaml`)

```yaml
name: daily-vibe-coding          # 任务名(必须与目录名一致)
schedule: "0 9 * * *"            # 标准 5 字段 cron
timezone: Asia/Shanghai
run_mode: work                    # work / ide / api
output_dir: logs/${name}/${date}   # 相对路径,运行时拼接
prompt_file: prompt.md             # 默认
version: 1.1.0
owner: my-trae-helper
```

### 2.2 prompt.md 编写规范(7 条)

- ✅ **禁止绝对路径**:不写 `d:\workspace\...`,用 `${WORKSPACE}/` 或纯相对路径
- ✅ **运行时变量**:`${WORKSPACE}` / `${DATE}` / `${TASK_NAME}` 由调度器替换
- ✅ **保留原任务逻辑**:PART A/B/C/D 结构、关键约束、SUGGESTIONS 分级 **不动**
- ✅ **末尾声明"agent 不修改仓库"**:防止被错误调用时失控
- ✅ **不写密钥/敏感信息**:沿用仓库铁律
- ✅ **不创建 skill**:本目录禁止升级为 skill
- ✅ **数字必带证据**:沿用 AGENTS.md §4.1.1

---

## §3 当前任务清单

详见 [REGISTRY.md](REGISTRY.md)。当前已有:

| 任务名 | 路径 | cron | 用途 | 状态 |
|--------|------|------|------|------|
| daily-vibe-coding | [daily-vibe-coding/](daily-vibe-coding/) | `0 9 * * *` | 每日早晨深度调研 + 自检 + 建议清单 | ✅ 已配置 |

---

## §4 如何添加新自动任务(3 步)

```bash
# 1. 创建任务目录
mkdir -p auto-task/<new-task>

# 2. 写 3 个文件(自包含)
touch auto-task/<new-task>/README.md
touch auto-task/<new-task>/prompt.md
touch auto-task/<new-task>/config.yaml

# 3. 在 REGISTRY.md 追加一行
#    不要改其他任何目录,不要建 skill
```

### 反例(禁止做的事)

- ❌ 把 `auto-task/<task>/` 升级到 `skill-markets/` → 本机制不是 skill
- ❌ 在 `auto-task/<task>/prompt.md` 里写绝对路径 → 跨机器不可移植
- ❌ 创建 `auto-task/<task>/scripts/` 子目录 → 本机制不写代码,只装提示词
- ❌ 修改 `AGENTS.md` / `CAPABILITY-MAP.md` / `SECURITY-MAP.md` → auto-task 不进项目治理体系

---

## §5 与其他目录的关系

| 目录 | 关系 |
|------|------|
| `skill-markets/` | auto-task **不是** skill,不进 CAPABILITY-MAP.md |
| `scripts/` | auto-task **不写** 脚本(运行脚本仍放 `scripts/<task>/`) |
| `logs/` | auto-task **输出** 到 `logs/<task-name>/<date>/` |
| `AGENTS.md` | auto-task **不修改** 铁律;若需新增硬约束,改 §1 后通知用户决策 |

---

## §6 版本演进

| 版本 | 日期 | 改动 | 作者 |
|------|------|------|------|
| 1.0.0 | 2026-08-15 | 初版:从 `skill-markets/daily-vibe-coding/prompt-installation/` 抽出,路径相对化 | — |

