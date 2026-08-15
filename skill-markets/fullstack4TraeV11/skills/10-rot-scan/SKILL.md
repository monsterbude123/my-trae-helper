---
name: fullstack-10-rot-scan
description: "Stage 4.5 腐化扫描 — proactive-scan.py 10 项必跑 + 元检测 + 修复。NO ROT NO ACCEPT。触发词：rot scan / 腐化扫描 / proactive-scan / 5 维度扫描。"
stage: 4.5
parent: fullstack4traev11
depends_on:
  skills: [goal-mode]
  stages: [4/review]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/common-iron-rules.md
  scripts:
    - ../../scripts/proactive-scan.py
    - ../../scripts/self-diagnose.py
---

# Stage 4.5 Rot Scan — 腐化扫描

> 第一性原则：**腐化可检测，NO ROT NO ACCEPT**。V10.4 腐化扫描包必跑。

## 铁律（6 条 — V10.4 蒸馏）

```
1. rot-detector 必跑 — Phase 4.5 不可跳过（Article XIV）
2. proactive-scan.py -- 10 项腐化扫描必跑
3. self-diagnose.py — Meta 自我诊断（rot-detector 自身腐烂检测）
4. NO ROT NO ACCEPT — 任一 FAIL = 🛑 REJECT Accept
5. fix-list.json 必产出 — 不可"扫完不改"
6. 归档前必跑 — Accept 前置门禁
```

## 10 项腐化扫描（V10.10 同步 -- 蒸馏自 workflows/rot-detect-and-fix.md）

| # | 检查项 | 检测脚本 |
|:---:|------|---------|
| 1 | 视觉腐烂（截图 ≥5KB + 7 天内）| visual-content-check.py |
| 2 | 归档腐烂（archive/ 不可变）| proactive-scan.py §2 |
| 3 | 自验腐烂（自评 vs 抽检）| proactive-scan.py §3 |
| 4 | 孤儿测试腐烂（rot #12）| orphan-detector.py |
| 5 | 构建腐烂（Bundle Staleness）| dist-hash-check.py |
| 6 | 吹嘘腐烂（state-card vs 实际）| proactive-scan.py §6 |
| 7 | 状态卡腐烂（state-card-staleness）| state-card-validator.py |
| 8 | 骨架腐烂（rot #13 stub 堆积）| proactive-scan.py §8 |
| 9 | 障碍诚实(V10.10 NEW -- Article XV Obstacle Honesty)| proactive-scan.py §9 |
| 10 | 抽象理由检测(V10.10 NEW -- Article XVI Skeptical Validation)| reason-classifier.py |

## 骨架流程（4 步）

```
Step 1: 跑 proactive-scan.py 10 项 → 生成 rot-scan-{date}.md
Step 2: 跑 self-diagnose.py → Meta 自身腐烂检测
Step 3: 输出 fix-list.json（每项含 type/severity/fix_action）
Step 4: 全部 PASS → 进入 Stage 5 Accept；任一 FAIL → 🛑 REJECT
```

## 关键产物

| 产物 | 路径 |
|------|------|
| 扫描报告 | `docs/reports/rot-scan-{date}.md` |
| 修复清单 | `docs/reports/fix-list.json` |
| Meta 元检测 | `docs/reports/self-diagnose-report.json` |

## 反模式（3 条）

| # | 反例 | 详细 |
|:---:|------|------|
| 1 | 跳过 rot-scan 直接 Accept | anti-patterns/01-skip-rot-scan.md |
| 2 | 扫完不改（fix-list.json 空）| anti-patterns/02-fix-list-empty.md |
| 3 | rot-detector 自身腐烂未检测 | anti-patterns/03-rot-detector-rotten.md |

## 参考索引

- [README.md](README.md)
- [rot-classification.md](references/rot-classification.md) — 7 大腐烂分类 + 19 个腐烂点
- [scan-protocol.md](references/scan-protocol.md) — 10 项扫描协议
- V10 rot-detector.md: `V10 来源` (已蒸馏到本文档)
- V10 process-rot-analysis.md: `V10 来源` (已蒸馏到本文档)




