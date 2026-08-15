---
name: fullstack-11-accept
description: "Stage 5 归档门禁 — 归档不可变 + 知识沉淀 + INDEX 更新。归档前必走 spec-purge + spec-knowledge-extract。触发词：accept / 归档 / archive / knowledge extract / 知识沉淀。"
stage: 5
parent: fullstack4traev11
depends_on:
  skills: [doc-map-manager]
  stages: [4.5/rot-scan]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/common-iron-rules.md
  scripts:
    - ../../scripts/stage-gate.py
    - ../../scripts/spec-purge.py
    - ../../scripts/spec-knowledge-extract.py
---

# Stage 5 Accept — 归档门禁

> 第一性原则：**归档是不可逆的终点，归档前必须完成知识沉淀**。

## 铁律（8 条 — V10.5 + V10 artifact-lifecycle 蒸馏）

```
1. 归档不可变       — archive/ 下文件禁止修改（Article VIII）
2. 知识沉淀先于归档 — spec-knowledge-extract.py 必先跑
3. spec-purge       — _invalidated/ 隔离 + archive/done/
4. INDEX 更新       — docs/INDEX.md 必更新
5. CHANGELOG        — docs/CHANGELOG.md 必追加
6. 归档前检查       — 4 工件完整 + 状态卡 archived
7. 状态卡 archived  — current_stage=null, health=🟢
8. NEVER 删归档    — 归档只能新增，不可删除（除非显式豁免）
```

## 骨架流程（5 步）

```
Step 1: 归档前检查（spec.md / contracts/ / review-report.md / rot-scan PASS）
Step 2: spec-knowledge-extract.py → docs/api-endpoints/ + domain-models/ + events/
Step 3: spec-purge.py → _invalidated/ 隔离 → archive/done/
Step 4: docs/INDEX.md + CHANGELOG.md 更新
Step 5: 状态卡 stage_status=archived + health=🟢
```

## 关键产物

| 产物 | 路径 |
|------|------|
| 归档目录 | `docs/archive/done/{change-id}/` |
| 上游交付物 | `docs/reports/rot-scan-{date}.md` + `docs/reports/fix-list.json` |
| 上游归档物 | `docs/specs/changes/{id}/verify-report.md`(随 spec-purge 一同归档)|
| 归档产物 | `ACCEPT_REPORT.md` |
| 知识提取 | `docs/api-endpoints/` + `docs/domain-models/` + `docs/events/` |
| INDEX 更新 | `docs/INDEX.md` |
| CHANGELOG | `docs/CHANGELOG.md` |

## 反模式（3 条）

| # | 反例 | 详细 |
|:---:|------|------|
| 1 | 跳过知识沉淀直接归档 | anti-patterns/01-skip-knowledge-extract.md |
| 2 | 修改归档文件 | anti-patterns/02-modify-archive.md |
| 3 | 删归档目录 | anti-patterns/03-delete-archive.md |

## 参考索引

- [README.md](README.md)
- [archive-protocol.md](references/archive-protocol.md)
- [knowledge-extract.md](references/knowledge-extract.md)
- V10 artifact-lifecycle.md: `V10 来源` (已蒸馏到本文档)
- V10 prd-integration-workflow.md: `V10 来源` (已蒸馏到本文档)
