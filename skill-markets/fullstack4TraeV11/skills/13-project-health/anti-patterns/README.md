# Anti-patterns — Stage 7 Project Health 反例库

| # | 反例 | 文件 |
|:---:|------|------|
| 1 | 把 project-health 当必走流程 | [01-async-as-sync.md](01-async-as-sync.md) |
| 2 | 修复优先级不分明 | [02-no-priority.md](02-no-priority.md) |
| 3 | self-diagnose 未跑 | [03-no-meta-check.md](03-no-meta-check.md) |

---

## 反例自检清单（V11.4 NEW — 蒸馏自 13-project-health 自检报告）

```yaml
anti_patterns_checklist:
  Stage 13 Specific:
    - [ ] project-health 不阻塞主流程? (反例 01-async-as-sync)
    - [ ] 4 维度检查齐全(路径/目录树/版本残留/文档同步)? (SKILL.md §4 维度)
    - [ ] P0/P1/P2/P3 优先级分明? (反例 02-no-priority)
    - [ ] self-diagnose.py 必跑(Meta 元检测)? (反例 03-no-meta-check)
    - [ ] gitnexus 5 调用必走 (impact + 2xquery + detect_changes + impact)? (references/anti-distortion.md L86-87)
```

**反例与铁律反向检查**（避免反例成为"陈述性警告"）:

| 铁律 | 反向检查 |
|------|---------|
| 铁律 1 异步非阻塞 | project-health 不在主流程 stage-gate.py BLOCK 路径中 (gates.yaml L118 fail_action: WARN) |
| 铁律 2 4 维度检查 | four-dimension-check.md 4 维度都列具体路径 (V11 §1 同步) |
| 铁律 3 优先级分级 | project-health-{date}.md 必含 P0/P1/P2/P3 计数 (anti-distortion.md L82-85) |
| 铁律 4 防失真机制 | skeptical-validation-protocol.md 4 维度质疑 P0/P1 修复 |
| 铁律 5 必复盘已分级 | 已分级问题必进入下一轮 health 报告 |
| 铁律 6 NEVER 静默 | project-health-{date}.md 必报所有问题, 不静默归档 |
| 铁律 7 self-diagnose | self-diagnose.py 必跑, 输出 self-diagnose-report.json |

---

## 关联引用

- [SKILL.md §铁律](../SKILL.md)
- [anti-distortion.md §2 self-diagnose 元检测](../references/anti-distortion.md)
- [common-anti-patterns.md §反例自检清单](../../../references/common-anti-patterns.md)
