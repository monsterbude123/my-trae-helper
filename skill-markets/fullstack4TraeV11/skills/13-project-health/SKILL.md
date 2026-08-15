---
name: fullstack-13-project-health
description: "Stage 7 项目健康度自检 — 主动自检 + 4 维度检查 + 优先级分级 + 防失真。 异步支线，可与任一 stage 并行。触发词：project health / 健康度 / 自检 / 诊断。"
stage: 7
parent: fullstack4traev11
depends_on:
  skills: []
  # 横向支线(stage 7/health 无 OUTBOUND 上游 stage),可从任意 stage 转入
  # 参见 registry/state-machine.yaml:9/14/19/24/29/34/39/44/49/54 (11 inbound transitions)
  # 与 orchestrator SKILL.md §0.3 L283 "支线(独立): 7 Project Health (异步自检,可与任一 stage 并行)" 一致
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

> **V11.7.0+ 设计入口**:
> - **AC 核销门禁(Stage 4 Review)** → [skills/09-review/SKILL.md](../09-review/SKILL.md) + [acceptance-baseline-extract.md](../09-review/workflows/acceptance-baseline-extract.md)
> - **贾维斯门禁守护(防 agent 改标准)** → [skills/00-boot/SKILL.md](../00-boot/SKILL.md) + [agents/jarvis.md](../00-boot/agents/jarvis.md) + [gate-configuration-protocol.md](../../references/gate-configuration-protocol.md)
> - **变更**: 评分制废除 → 门禁制;4 维详情转附加检查;`registry/gates.yaml` v1.2.0 加 layer 分层字段(docs/module/app/system)

# Stage 7 Project Health — 项目健康度自检

> 第一性原则：**主动自检是反失真机制**。异步支线，可与任一 stage 并行，不阻塞主流程。

## 铁律（7 条 — V10 project-health-auditor 6 条 + V11.4 self-diagnose 蒸馏 1 条）

```
1. 异步非阻塞   — 不阻塞主流程；可在任一 stage 并行
2. 4 维度检查   — 路径一致性 + 目录树 + 版本残留 + 文档同步
3. 优先级分级   — P0 阻断 / P1 高优 / P2 中优 / P3 低优
4. 防失真机制   — 质疑性校验按 [skeptical-validation-protocol.md](../../references/skeptical-validation-protocol.md)
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
| **路径一致性** | 文档路径 vs 代码路径是否对齐 (V11 §1: docs/specs/INDEX.md / docs/specs/changes/{id}/contracts/ 路径基准) |
| **目录树** | 与 docs/specs/INDEX.md 目录树一致 (V11 §1 project-structure.md L29 单源) |
| **版本残留** | .bak / .old / 备份文件 / 调试代码 |
| **文档同步** | docs/specs/INDEX.md / docs/specs/changes/{id}/contracts/api-contracts.md / docs/modules/ |

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