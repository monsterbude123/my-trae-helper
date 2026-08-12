# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 7 Project Health 从 V10 `agents/project-health-auditor.md` + `references/project-health-checklist.md` 蒸馏实战智慧。

---

## V10 实战反例（3 条，均完全重叠于独立反例文件）

| # | 蒸馏主题 | 反例文件指针 |
|---|---------|------------|
| 蒸馏 1 | 把 project-health 当必走流程（异步支线被当同步阻塞） | → 见 [01-async-as-sync.md](01-async-as-sync.md) |
| 蒸馏 2 | 修复优先级不分明（P0/P1/P2/P3 混在一起） | → 见 [02-no-priority.md](02-no-priority.md) |
| 蒸馏 3 | self-diagnose 未跑（rot-detector 自身腐烂检测缺失） | → 见 [03-no-meta-check.md](03-no-meta-check.md) |

---

## V10 → V11 蒸馏映射

| V10 来源 | V11 蒸馏位置 |
|---------|------------|
| agents/project-health-auditor.md 铁律 | skills/13-project-health/SKILL.md 铁律 1-6 |
| references/project-health-checklist.md | references/four-dimension-check.md |
| scripts/self-diagnose.py | V11 scripts/self-diagnose.py |
| scripts/proactive-scan.py | V11 scripts/proactive-scan.py |

---

## 关联引用

- [skills/13-project-health/SKILL.md](../SKILL.md) — Stage 7 主入口
- [references/gitnexus-tools.md](../../references/gitnexus-tools.md) — gitnexus-impact-audit 4 维度
- [references/report-growth.md](../../references/report-growth.md) — L1-L4 异常分级
- [scripts/proactive-scan.py](../../scripts/proactive-scan.py) — 8 项腐化扫描
- [scripts/self-diagnose.py](../../scripts/self-diagnose.py) — Meta 元检测
