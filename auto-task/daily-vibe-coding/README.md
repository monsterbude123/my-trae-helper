# daily-vibe-coding 自动任务

> **自动任务类型**:每日早晨深度调研 + 仓库自检 + 升级建议清单
> **配置位置**:TRAE Work 定时任务(配置后不可修改运行模式)
> **任务定义**:本目录 `prompt.md`(TRAE 复制用)+ `config.yaml`(调度配置)

---

## 用途

把每日"调研 + 自检"流程固化,让 agent 每天 09:00 自动跑一次,产出 5 份 .md 报告 + 1 份 SUGGESTIONS 清单。用户审批后由采纳方填 implementation-log.md。

---

## 工作流(每次运行)

```
1. agent 加载 prompt.md
2. 跑 scripts/daily-vibe-coding/collect-baseline.py  → 生成 logs/<today>/_baseline.json
3. 跑 scripts/daily-vibe-coding/generate-templates.py → 生成 5 份报告骨架
4. agent 按 PART 0/A/B/C/D 顺序填充内容
5. 输出到 logs/daily-vibe-coding/YYYY-MM-DD/ 目录
6. 末尾只输出 SUGGESTIONS.md 的 🟢/🟡/🔴/✋ 4 栏摘要
```

---

## 关键约束(7 条)

1. **严禁修改仓库任何文件** — 只生成 5 份 .md 报告
2. **必须产 SUGGESTIONS.md** — 用户审批入口
3. **必须自我分级 🟢/🟡/🔴** — 不允许"全打 🟢 显得有用"
4. **数字必带证据** — 第 1 轮列清单(AGENTS.md §4.1.1)
5. **不重复调研历史已覆盖方法论** — PART 0.2 幂等
6. **不创建 implementation-log.md 真实条目** — 这是采纳方的工作
7. **末尾不输出"完成报告"** — 只输出建议清单摘要

完整规范见 [skill-markets/daily-vibe-coding/SKILL.md](../../skill-markets/daily-vibe-coding/SKILL.md) v1.1。
