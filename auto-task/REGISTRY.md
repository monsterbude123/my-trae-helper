# auto-task REGISTRY — 自动任务清单

> 全量索引。新增任务时在本表追加一行,不要修改 `auto-task/README.md`。
>
> 字段:`name` / `path` / `cron` / `tz` / `mode` / `output` / `version` / `status`

| name | path | cron | tz | mode | output | version | status |
|------|------|------|----|------|--------|---------|--------|
| daily-vibe-coding | [daily-vibe-coding/](daily-vibe-coding/) | `0 9 * * *` | Asia/Shanghai | work | `logs/daily-vibe-coding/${date}/` | 1.1.0 | ✅ 已配置 |

---

## 任务详情

### daily-vibe-coding

- **目的**:每日早晨深度调研(Vibe Coding / Agentic Coding 趋势)+ 仓库自检 + 升级建议清单
- **运行时间**:每天 09:00(Asia/Shanghai)
- **运行模式**:Work(云端,不占本地)
- **输出位置**:`logs/daily-vibe-coding/YYYY-MM-DD/`(5 份报告 + 1 份 INDEX + 1 份 SUGGESTIONS)
- **关联脚本**:`scripts/daily-vibe-coding/collect-baseline.py` + `generate-templates.py` + `run-precheck.sh`
- **历史基线**:见 [logs/daily-vibe-coding/INDEX.md](../logs/daily-vibe-coding/INDEX.md)
- **最近运行**:2026-08-15 09:00 — 详见 `logs/daily-vibe-coding/2026-08-15/SUGGESTIONS.md`
- **关键约束**(沿用):
  1. agent 不修改仓库任何文件,只生成报告
  2. 必须产 `SUGGESTIONS.md` 作为用户审批入口
  3. 必须自我分级 🟢/🟡/🔴/✋(不全打 🟢)
  4. 7 天去重(同一方法论 7 天内不重复引用)

