# V10 实战蒸馏（Battle-Tested Patterns）

> Stage 4.5 Rot Scan 从 V10 agents/rot-detector.md + process-rot-analysis.md + proactive-scan.py 蒸馏。

## V10 实战反例（3 条，均完全重叠于独立反例文件）

| # | 蒸馏主题 | 反例文件指针 |
|---|---------|------------|
| 蒸馏 1 | 跳过 rot-detector 直接 Accept（Article XIV 违规） | → 见 [01-skip-rot-scan.md](01-skip-rot-scan.md) |
| 蒸馏 2 | fix-list.json 空（扫完不改） | → 见 [02-fix-list-empty.md](02-fix-list-empty.md) |
| 蒸馏 3 | rot-detector 自身腐烂（rot #15 配置腐烂，self-diagnose 未跑） | → 见 [03-rot-detector-rotten.md](03-rot-detector-rotten.md) |

## V10 实战蒸馏经验（3 条）

| 经验 | V10 来源 | V11 落地位置 |
|------|---------|------------|
| rot-detector 不可跳 | Article XIV | 铁律 1 |
| fix-list.json 必产 | rot-detector.md Step 3 | 铁律 5 |
| rot-detector 自身腐烂检测 | process-rot-analysis.md rot #15 | 铁律 3 |

## V10 来源溯源（开发期，部署前可删）

> ⚠️ 本节记录 V10 来源，仅供 V11 维护者追溯。**V11 部署时不依赖 V10**——V10 内容已蒸馏进 V11 references/anti-patterns。

| V10 来源 | 蒸馏到 V11 位置 |
|---------|---------------|
| V10 rot-detector.md | → `../../10-rot-scan/SKILL.md` 铁律 1-6 |
| V10 process-rot-analysis.md | → `../../10-rot-scan/references/rot-classification.md` |
| V10 proactive-scan.py | → V11 `scripts/proactive-scan.py`（重写） |
| V10 self-diagnose.py | → V11 `scripts/self-diagnose.py`（重写） |

## 关联引用

[SKILL.md](../SKILL.md) | [rot-classification.md](../references/rot-classification.md) | [scan-protocol.md](../references/scan-protocol.md)
