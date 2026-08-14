# Daily Vibe Coding — 一键安装到 TRAE Work

> 用途: 复制下方**整段**到 TRAE Work 对话框,**按回车发送** → TRAE AI 自动帮你创建定时任务。
> 前提: TRAE Work 客户端已登录,工作目录含 `d:\workspace\my-trae-helper`。

---

## 复制从这里开始 ↓

帮我创建一个定时任务:

**任务名**: daily-vibe-coding

**触发时间**: 每天早上 9:00 (Asia/Shanghai)

**运行模式**: Work

**运行环境**: 云端 (这样不占用我本地电脑)

**输出位置**: 把本次运行的结果保存到 logs/daily-vibe-coding/YYYY-MM-DD/ 目录 (如果当月不存在就 mkdir -p)

**任务内容**: 你是每日早晨的深度调研 + 自检代理。**不修改仓库任何文件,只生成报告和建议清单**。

工作目录: d:\workspace\my-trae-helper
时区: Asia/Shanghai

## 任务执行步骤

### PART 0 — 幂等与历史消化

0.1 扫描历史:
  - ls logs/daily-vibe-coding/  → 列出所有历史日期目录
  - Read logs/daily-vibe-coding/INDEX.md (若存在)  → 拿到历史摘要索引

0.2 解析"未消化项":
  对每份历史报告,定位 §"实施回写钩子" 章节,扫描 implementation-log.md,把每条历史建议标记为:
  ✅ 已落地 / ⏳ 进行中 / ❌ 未启动 / ⚠️ 已失效

0.3 本次范围决策:
  - ❌/⏳: 本次给出"是否要继续推进 / 如何收口"的判定
  - ⚠️: 必须在本日 external-report.md §"历史建议处置" 章节记录原因
  - ✅: 不重复调研(幂等)
  - 严禁同一方法论 7 天内被重复引用进新报告

### PART A — 外部深度调研 (Vibe Coding,仅新增项)

A.1 信息源 (按权威度优先):
  1. WebSearch (近 30 天): "vibe coding" / "agentic coding" / "spec-driven development" + 2026
  2. 仓库内已有素材:
     - skill-markets/vibe-coding-standards/SKILL.md
     - skill-markets/deep-research/SKILL.md
     - skill-markets/fullstack4TraeV11/SKILL.md

A.2 流程:
  Step 1 检索 — 至少 3 条独立新来源
  Step 2 去重 — 与历史 INDEX.md §方法论 去重,只保留新出现的
  Step 3 提炼方法论 — 3~5 条可落地方法论
  Step 4 反例 — 每条方法论必须配 1 个常见失败模式
  Step 5 来源整理 — 全部 markdown 链接

A.3 产物: logs/daily-vibe-coding/YYYY-MM-DD/external-report.md
  必含章节:
  - # Vibe Coding 每日调研 — YYYY-MM-DD
  - ## 历史消化摘要
  - ## 本日新增方法论 (3~5 条)
  - ## 来源汇总 (表格)
  - ## 与本仓库的对接点
  - ## 不确定 / 待跟进
  - ## ★实施回写锚点★ (table)

### PART B — 仓库自检 + 升级指导

B.1 必跑命令:
  - python skill-markets/trae-security-review/scripts/scan_skills_dir.py skill-markets/
  - ls skill-markets/ | wc -l
  - 抽样 Read 3~5 个 SKILL.md 的 YAML frontmatter
  - Read SECURITY-MAP.md 末次更新时间
  - Read skill-markets/CAPABILITY-MAP.md

B.2 产物: logs/daily-vibe-coding/YYYY-MM-DD/self-audit.md
  ## 体检结果 / ## 发现的真问题 (HIGH/MED/LOW 三档) / ## 不做 / 暂缓的项 / ## 差异

B.3 产物: logs/daily-vibe-coding/YYYY-MM-DD/upgrade-guid.md
  ## 历史建议处置 / ## 本日新增升级建议表 / ## 落地步骤 / ## 不建议做的事 / ## 长期演进方向

B.4 产物: logs/daily-vibe-coding/YYYY-MM-DD/implementation-log.md
  空模板,等采纳方填

### PART C — ★★★ 建议清单 + 自我评估(关键)★★★

产物: logs/daily-vibe-coding/YYYY-MM-DD/SUGGESTIONS.md

# 今日建议清单 (YYYY-MM-DD)

> 用户的**核心审批入口**。每条建议必须自我评估置信度。

## 🟢 高置信(建议直接采纳)

| 编号 | 建议 | 证据 | 风险 | 一句话理由 |
|------|------|------|------|--------|
| S-01 | ... | 链接 | 低 | ... |

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

1. 用户读完 SUGGESTIONS.md
2. 对每条建议表态:采纳 / 暂缓 / 拒绝 (附 1 句话理由)
3. 用户告诉下次会话或手动编辑: "采纳 S-01 / S-03, 拒绝 S-02"
4. 采纳方在 implementation-log.md 追加 ID-XX 条目
5. implementation-log.md 是**唯一**反映"哪些建议真落地了"的真相源

### PART D — 收尾

1. 写 logs/daily-vibe-coding/YYYY-MM-DD/INDEX.md (本日目录清单 + SUGGESTIONS 摘要)
2. 更新 logs/daily-vibe-coding/INDEX.md (总索引)
3. 末尾**只输出 SUGGESTIONS.md 的 🟢/🟡/🔴/✋ 4 栏摘要**(不是"完成报告")

## ★关键约束(违反即任务失效)★

1. **严禁修改仓库任何文件** — 只生成 5 份 .md 报告
2. **必须产 SUGGESTIONS.md** — 用户审批入口
3. **必须自我分级 🟢/🟡/🔴** — 不允许"全打 🟢 显得有用"
4. **数字必带证据** — 第 1 轮列清单(AGENTS.md §4.1.1)
5. **不重复调研历史已覆盖方法论** — PART 0.2 幂等
6. **不创建 implementation-log.md 真实条目** — 这是采纳方的工作
7. **末尾不输出"完成报告"** — 只输出建议清单摘要

## 复制到这里结束 ↑