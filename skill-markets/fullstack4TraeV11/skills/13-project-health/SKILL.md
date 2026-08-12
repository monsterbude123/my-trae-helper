---
name: project-health
description: "Stage 7 项目健康度自检 — 主动自检 + 4 维度检查 + 优先级分级 + 防失真。 异步支线，可与任一 stage 并行。触发词：project health / 健康度 / 自检 / 诊断。"
stage: 7
parent: fullstack4traev11
depends_on:
  skills: []
  stages: []
  references:
    - ../../references/state-card-protocol.md
    - ../../references/gitnexus-tools.md
    - ./references/gitnexus-impact-audit.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/common-iron-rules.md
  scripts:
    - ../../scripts/proactive-scan.py
    - ../../scripts/self-diagnose.py
---

# Stage 7 Project Health — 项目健康度自检

> 第一性原则：**主动自检是反失真机制**。异步支线，可与任一 stage 并行，不阻塞主流程。

## 铁律（6 条 — V10 project-health-auditor 蒸馏）

```
1. 异步非阻塞   — 不阻塞主流程；可在任一 stage 并行
2. 4 维度检查   — 路径一致性 + 目录树 + 版本残留 + 文档同步
3. 优先级分级   — P0 阻断 / P1 高优 / P2 中优 / P3 低优
4. 防失真机制   — 质疑性校验按 [skeptical-validation-protocol.md](../references/skeptical-validation-protocol.md)
5. 必复盘已分级 — 已分级问题必进入下一轮 health 报告复盘
6. NEVER 静默   — 发现问题必报，不静默归档
7. self-diagnose — Meta 自身失真检测
```

## 骨架流程（4 步）

```
Step 1: 项目类型判定（web/tauri/cli/library/backend）
Step 2: 4 维度检查（路径一致性 / 目录树 / 版本残留 / 文档同步）
Step 3: 优先级分级（P0/P1/P2/P3）
Step 4: 输出 project-health-{date}.md + .json
```

## 4 维度检查

| 维度 | 检测项 |
|------|------|
| **路径一致性** | 文档路径 vs 代码路径是否对齐 |
| **目录树** | 与 ARCHITECTURE.md / INDEX.md 一致 |
| **版本残留** | .bak / .old / 备份文件 / 调试代码 |
| **文档同步** | INDEX.md / API-REFERENCE / 模块文档 |

## 关键产物

| 产物 | 路径 |
|------|------|
| 健康度报告 | `docs/reports/project-health-{date}.md` |
| JSON 数据 | `docs/reports/project-health-{date}.json` |
| 优先级列表 | 含 P0/P1/P2/P3 修复项 |

## 反模式（3 条）

| # | 反例 | 详细 |
|:---:|------|------|
| 1 | 把 project-health 当必走流程 | anti-patterns/01-async-as-sync.md |
| 2 | 修复优先级不分明 | anti-patterns/02-no-priority.md |
| 3 | self-diagnose 未跑 | anti-patterns/03-no-meta-check.md |

## 参考索引

- [README.md](README.md)
- [four-dimension-check.md](references/four-dimension-check.md)
- [anti-distortion.md](references/anti-distortion.md)
- V10 来源参考（开发期，部署前可删）: V10 agents/project-health-auditor.md + references/project-health-checklist.md（已蒸馏到本文档）