# V11 — Fullstack4TraeV11（高内聚专家架构）

> 全栈文档驱动开发技能包 V11.0。V10 思想传承 + 架构升级。

---

## 核心特点

- **高内聚专家架构**: 每个 stage 自包含（SKILL/README/workflows/references/templates/anti-patterns）
- **13 stage 流水线**: Intake → Plan → Test Plan → Spec → Prototype → Contract → Implement → Real Verify → Review → Rot Scan → Accept + Bug Fix + Project Health
- **独立部署**: 不依赖 V10 目录
- **V10 思想完整继承**: 16 Articles 宪法 + 10 项腐化扫描 + 4 维评分 + 5 类项目验证

---

## 目录结构

```
fullstack4TraeV11/
├── SKILL.md              # 总编排器（必读）
├── README.md             # 本文件
├── CHANGELOG.md          # 版本变更
├── references/           # 公共 references（10 个）
├── templates/            # 公共 templates（8 个）
├── scripts/              # 公共脚本（13 个 Python，全部实装）
├── skills/               # 13 stage skill（高内聚）
│   ├── 01-intake/
│   ├── 02-plan/
│   ├── ...
│   └── 13-project-health/
└── V10-distillation-source-map.md  # V10 → V11 蒸馏溯源（开发期）
```

---

## 13 stage 流水线

| Stage | 名称 | SKILL.md |
|:---:|------|----------|
| -1 | Intake | [skills/01-intake/SKILL.md](skills/01-intake/SKILL.md) |
| 0 | Plan | [skills/02-plan/SKILL.md](skills/02-plan/SKILL.md) |
| 0.5 | Test Plan | [skills/03-test-plan/SKILL.md](skills/03-test-plan/SKILL.md) |
| 1 | Spec | [skills/04-spec/SKILL.md](skills/04-spec/SKILL.md) |
| 1.5 | Prototype | [skills/05-prototype/SKILL.md](skills/05-prototype/SKILL.md) |
| 2 | Contract | [skills/06-contract/SKILL.md](skills/06-contract/SKILL.md) |
| 3 | Implement | [skills/07-implement/SKILL.md](skills/07-implement/SKILL.md) |
| 3.5 | Real Verify | [skills/08-real-verify/SKILL.md](skills/08-real-verify/SKILL.md) |
| 4 | Review | [skills/09-review/SKILL.md](skills/09-review/SKILL.md) |
| 4.5 | Rot Scan | [skills/10-rot-scan/SKILL.md](skills/10-rot-scan/SKILL.md) |
| 5 | Accept | [skills/11-accept/SKILL.md](skills/11-accept/SKILL.md) |
| 6 | Bug Fix | [skills/12-bug-fix/SKILL.md](skills/12-bug-fix/SKILL.md) |
| 7 | Project Health | [skills/13-project-health/SKILL.md](skills/13-project-health/SKILL.md) |

---

## 快速开始

### 1. 加载 V11 主 SKILL.md

主上下文收到 "Use Skill: fullstack4traev11" 后必走 §0.5 加载协议：

1. 加载 SKILL.md（含 stage_config）
2. 必读 9 个公共 references（constitution / common-iron-rules / common-anti-patterns / stage-card-protocol / stage-interaction-protocol / dependency-config / document-layer / report-growth / ask-question-anti-patterns）
3. Glob 项目级约定（AGENTS.md / docs/ / .trae/rules/）
4. 3 层依赖合并（项目 > V11 > 全局）
5. 进入 Stage -1 Intake 工作模式

### 2. 委派到 Stage skill

主上下文委派 sub-agent 时，按 stage skill 的 SKILL.md 必走 4 步：

```
[1] 加载 stage skill SKILL.md
[2] 注入上下文（状态卡 + 上游 Completion Report）
[3] 委派 sub-agent-{stage}
[4] 验收（必走 9 CROSS-SESSION VERIFY，亲自跑 evidence 命令）
```

### 3. 公共脚本使用

```bash
# 状态卡门禁
python scripts/stage-gate.py --state-card docs/specs/changes/{id}/.state-card.md

# 全局阶段门禁（V10.11 NEW 含 verify-rot-scan）
python scripts/phase-gate.py --state-card .trae/state-card.md --verify-rot-scan --change-id {id}

# 腐化扫描
python scripts/proactive-scan.py --project-root . --output rot-scan.md --output-fix-list fix-list.json

# 元检测（rot-detector 自身）
python scripts/self-diagnose.py --project-root .

# 4 维评分
python scripts/acceptance-audit.py --review-report docs/specs/changes/{id}/review-report.md
```

---

## 与 V10 关系

V11 是**独立版本**，部署时不依赖 V10 目录。V10 内容已蒸馏进 V11 references/。

V10 → V11 蒸馏溯源见 [references/V10-distillation-source-map.md](references/V10-distillation-source-map.md)。

---

## 部署

```bash
# V11 部署到 ~/.trae-cn/skills/
cp -r skill-markets/fullstack4TraeV11/* ~/.trae-cn/skills/fullstack4TraeV11/

# 验证
ls ~/.trae-cn/skills/fullstack4TraeV11/skills/
ls ~/.trae-cn/skills/fullstack4TraeV11/scripts/

# 部署前可清理（开发期 reference，不依赖运行时）：
rm -rf ~/.trae-cn/skills/fullstack4TraeV11/references/V10-distillation-source-map.md
rm -rf ~/.trae-cn/skills/fullstack4TraeV11/skills/*/anti-patterns/V10-battle-tested.md
```

---

## 关联引用

- [SKILL.md](SKILL.md) — V11 总编排器（V11 入口）
- [CHANGELOG.md](CHANGELOG.md) — 版本变更
- [references/constitution.md](references/constitution.md) — 16 Articles 宪法
- [references/common-iron-rules.md](references/common-iron-rules.md) — 公共铁律
- [references/V10-distillation-source-map.md](references/V10-distillation-source-map.md) — V10 蒸馏溯源