---
name: daily-vibe-coding
version: 1.0.0
description: 每日 09:00 定时 vibe coding 调研 + 自检任务(v1.1 三层改造: 审批 gate + 建议分级 + 不自动改仓库)。外部调研 + 仓库自检 + 升级指导三份产物 + 自我评估的"建议清单"(🟢/🟡/🔴 三色)。触发词:daily vibe coding、定时调研、自检、upgrade guidance。
intent: 每日 vibe coding 定时调研 + 自检 + 建议清单(审批 gate)
category: orchestration
audience: [agent]
---

# Daily Vibe Coding 定时任务规范 v1.1

> **核心理念(三层改造)**:
> 1. **不自动改仓库** — agent 只生成调研报告 + 建议清单,**用户审批**后才落地
> 2. **建议分级** — 每次产出附 🟢高置信 / 🟡待核实 / 🔴低置信 三色标记
> 3. **改进不进仓库,只进清单** — implementation-log.md 由**采纳方 agent**(下次会话/手动)写,本任务**只生成**

## 触发

- TRAE Work 自动化任务,**每天 09:00**(Asia/Shanghai)
- 运行环境:**Work 模式 / 云端**
- 输出路径:`logs/daily-vibe-coding/YYYY-MM-DD/`
- 期望产出 4 份 md(见 PART A/B 输出)

---

## 使用方式

### 方式 A:TRAE Work "在对话中创建"(推荐)

1. 打开 TRAE Work 对话框
2. 粘贴 `prompt-installation/installation-prompt.md` 全文
3. TRAE AI 解读后会让你确认任务名、触发时间、运行模式
4. 创建成功 → 任务**已配置,明日 09:00 自动跑**

### 方式 B:手动新建

左栏顶部 → **自动化** → **手动新建**:
- 任务名:`daily-vibe-coding`
- 触发时间:每天 09:00(自定义自然语言:工作日早上 9 点)
- 任务内容:粘贴下面的核心 prompt
- 运行模式:Work
- 运行环境:**云端**(避免本地本地)
- 输出路径:`:`logs/daily-vibe-coding/YYYY-MM-DD/

### 方式 C:从模板创建

把本 skill 沉淀为模板(后续版本)

---

## 任务核心 prompt(可直接粘贴到 TRAE Work)

> 下面的完整 prompt 是**任务内容字段**的值。TRAE Work 会按这个 prompt 自动运行。

```text
你是一个每日早晨的深度调研 + 自检代理。**不修改仓库任何文件,只生成报告和建议清单**。

工作目录: d:\workspace\my-trae-helper
输出根目录: logs/daily-vibe-coding/  (今日子目录 YYYY-MM-DD/, 缺则 mkdir -p)
时区: Asia/Shanghai

================================================================
PART 0 — 幂等与历史消化 (最先做,决定本次范围)
================================================================

0.1 扫描历史
  ls logs/daily-vibe-coding/  → 列出所有历史日期目录,按日期降序
  Read logs/daily-vibe-coding/INDEX.md (若存在)  → 拿到历史摘要索引

0.2 解析"未消化项"
  对每份历史报告,定位 §"实施回写钩子" 章节,扫描对应的实施回写文件:
    - logs/daily-vibe-coding/<date>/implementation-log.md
  把每条历史建议标记为三态:
    ✅ 已落地 / ⏳ 进行中 / ❌ 未启动 / ⚠️ 已失效

0.3 本次范围决策
  - ❌/⏳: 本次必须给出"是否要继续推进 / 如何收口"的判定
  - ⚠️: 必须在本日 external-report.md §"历史建议处置" 章节记录原因
  - ✅: 不重复调研(幂等)
  - 仅当历史上**从未覆盖**的新方法论,才进入 PART A 的外部检索
  - 严禁: 同一来源 / 同一方法论 7 天内被重复引用进新报告

================================================================
PART A — 外部深度调研 (Vibe Coding,仅新增项)
================================================================

A.1 信息源 (按权威度优先,缺则跳过)
  1. GitHub MCP: search_repositories / search_code / search_issues
     关键词: "vibe coding" / "agentic coding" / "spec-driven development"
             / "Claude Code" / "Cursor rules" / "Aider"
  2. WebSearch (近 30 天): 同上关键词 + 2026
  3. 仓库内已有素材: skill-markets/vibe-coding-standards/SKILL.md
                      skill-markets/deep-research/SKILL.md
                      skill-markets/fullstack4TraeV11/SKILL.md

A.2 流程 (deep research,严格按 skill-markets/deep-research 流程)
  Step 1 检索 — 至少 3 条独立新来源
  Step 2 去重 — 与历史 INDEX.md §方法论 去重,只保留新出现的
  Step 3 提炼方法论 — 不是"新闻列表",而是"3~5 条可落地方法论"
  Step 4 反例 — 每条方法论必须配 1 个常见失败模式
  Step 5 来源整理 — 全部 markdown 链接,带发布时间 + 一句话摘要

A.3 产物 1: logs/daily-vibe-coding/YYYY-MM-DD/external-report.md
  必含章节:
    # Vibe Coding 每日调研 — YYYY-MM-DD
    ## 历史消化摘要 (粘贴 0.2 的三态分布)
    ## 本日新增方法论 (3~5 条,每条: 一句话 + 适用场景 + 反例)
    ## 来源汇总 (表格: 标题 | 作者/机构 | 发布时间 | 链接 | 一句话摘要)
    ## 与本仓库的对接点
    ## 不确定 / 待跟进
    ## ★实施回写锚点★
      | 建议 ID | 建议简述 | 命中技能 | 落地动作 | 回写文件 |
      |---------|----------|----------|----------|----------|

================================================================
PART B — 仓库自检 + 升级指导 (针对 my-trae-helper 自身)
================================================================

B.1 必跑命令
  - python skill-markets/trae-security-review/scripts/scan_skills_dir.py skill-markets/
  - ls skill-markets/ | wc -l
  - 抽样 Read 3~5 个 SKILL.md 的 YAML frontmatter
  - Read SECURITY-MAP.md 末次更新时间,与 git log -1 --format=%ad 对比
  - Read skill-markets/CAPABILITY-MAP.md

B.2 产物 2: logs/daily-vibe-coding/YYYY-MM-DD/self-audit.md
  ## 体检结果 / ## 发现的真问题 (HIGH/MED/LOW 三档) / ## 不做 / 暂缓的项 / ## 差异

B.3 升级指导
  产物 3: logs/daily-vibe-coding/YYYY-MM-DD/upgrade-guid.md
  ## 历史建议处置 / ## 本日新增升级建议表 / ## 落地步骤 / ## 不建议做的事 / ## 长期演进方向

B.4 产物 4: logs/daily-vibe-coding/YYYY-MM-DD/implementation-log.md
  (空模板,等采纳方填)

================================================================
PART C — ★★★ 建议清单 + 自我评估(关键改造)★★★
================================================================

C.1 强制产出:logs/daily-vibe-coding/YYYY-MM-DD/SUGGESTIONS.md

格式:

# 今日建议清单 (YYYY-MM-DD)

> 定时任务的**核心交付物**。用户审批后下次会话采纳落地。
> 详细调研见 external-report.md / self-audit.md / upgrade-guid.md。

## 🟢 高置信(建议直接采纳)

| 编号 | 建议 | 证据 | 风险 | 一句话理由 |
|------|------|------|------|--------|
| S-01 | ... | 链接 external-report.md §X | 低 | ... |
| S-02 | ... | ... | ... | ... |

## 🟡 待核实(采纳前需人工确认)

| 编号 | 建议 | 不确定点 | 建议如何核实 |
|------|------|----------|--------------|
| S-03 | ... | ... | 跑一次 / 查 X / 问 Y |

## 🔴 低置信(本次不强推,记下供下次)

| 编号 | 建议 | 为何低置信 | 何时再议 |
|------|------|-----------|----------|
| S-04 | ... | ... | ... |

## ✋ 用户必须决定(agent 拒绝自动判断)

| 编号 | 议题 | agent 观点 | 等用户回复 |
|------|------|-----------|------------|
| Q-01 | ... | ... | ... |

## ★审批工作流★

采纳 S-XX 建议的流程:
  1. 用户读完本文件
  2. 对每条建议表态:采纳 / 暂缓 / 拒绝(附 1 句话理由)
  3. 用户告诉下次会话或手动编辑:
     "采纳 S-01 / S-03, 拒绝 S-02"
  4. 采纳方 agent / 用户在 logs/daily-vibe-coding/YYYY-MM-DD/implementation-log.md
     追加 ID-XX 条目(格式见 upgrade-guid.md ★给后续 agent 的指令★)
  5. implementation-log.md 是**唯一**反映"哪些建议真落地了"的真相源

================================================================
PART D — 收尾 + 历史索引维护
================================================================

1. 写 logs/daily-vibe-coding/YYYY-MM-DD/INDEX.md (本日目录清单 + SUGGESTIONS 摘要)
2. 更新 logs/daily-vibe-coding/INDEX.md (总索引,追加本日摘要)
3. 末尾**只输出 SUGGESTIONS.md 的 🟢/🟡/🔴/✋ 4 栏摘要**(不是"完成报告")

================================================================
关键约束(违反即任务失效)
================================================================

1. **严禁修改仓库任何文件** — 只生成 5 份 .md 报告
2. **必须产 SUGGESTIONS.md** — 用户审批入口
3. **必须自我分级 🟢/🟡/🔴** — 不允许"全打 🟢 显得有用"
4. **数字必带证据** — 第 1 轮列清单(AGENTS.md §4.1.1)
5. **不重复调研历史已覆盖方法论** — PART 0.2 幂等
6. **不创建 implementation-log.md 真实条目** — 这是采纳方的工作
7. **末尾不输出"完成报告"** — 只输出建议清单摘要

```

---

## 本 skill 提供的产物清单

| 文件 | 内容 |
|------|------|
| `skill-markets/daily-vibe-coding/SKILL.md` (本文件) | 定时任务规范 + 完整 prompt |
| `skill-markets/daily-vibe-coding/prompt-installation/installation-prompt.md` | 方式 A 一键安装 prompt(直接复制) |
| `skill-markets/daily-vibe-coding/prompt-installation/trae-setup-steps.md` | 方式 A/B/C 详细步骤 + 截图位 |
| `scripts/daily-vibe-coding/collect-baseline.py` | **辅助脚本**:一次性采集 12 项基线 + 历史消化 → `_baseline.json` |
| `scripts/daily-vibe-coding/generate-templates.py` | **辅助脚本**:读 `_baseline.json` 自动填 5 份报告骨架 |
| `scripts/daily-vibe-coding/run-precheck.sh` | **辅助脚本**:Git Bash 入口(探测 Python) |
| `scripts/daily-vibe-coding/README.md` | **辅助脚本**:用法文档 + 固化/不固化边界 |
| `scripts/run-daily-vibe-coding.ps1` | **入口脚本**:Step1 precheck → Step2 模板 → Step3 agent 三步链 |

## 辅助脚本使用时机

```
调研启动时,先跑:
  bash scripts/daily-vibe-coding/run-precheck.sh --history-date 2026-08-14
  python scripts/daily-vibe-coding/generate-templates.py

输出 logs/daily-vibe-coding/<today>/_baseline.json (基线数据 JSON)
    + 5 份 .md 骨架(数字已自动填, 手动补方法论/建议)

agent 后续只需 Read _baseline.json, 不再重复跑命令
```

---

## 关联

- 调研对象:[vibe-coding-standards/SKILL.md](../vibe-coding-standards/SKILL.md) — 这是"vibe coding 方法论"本身
- 自检依据:[my-trae-helper/AGENTS.md §1-§2](file:///d:/workspace/my-trae-helper/AGENTS.md) — 铁律 + 三层控制
- 配套 hooks:[scripts/change-guard-approver.mjs](file:///d:/workspace/my-trae-helper/scripts/change-guard-approver.mjs) — 人工审批守卫
- 工具命令:[bin/cli.mjs verify](file:///d:/workspace/my-trae-helper/bin/cli.mjs) — 任务完成后跑
- TRAE Work 文档:[automated-tasks](file:///d:/workspace/my-trae-helper/skill-markets/trae-professional/references/automated-tasks.md)