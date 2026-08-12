# Changelog — V11.0

> V11 独立 skill 版本 changelog。V10 → V11 蒸馏 + 架构升级。

---

## [V11.0.0] — 2026-08-11

### ✨新增（V11 架构升级）

- **架构升级**: 从 V10 agents/ + references/ 分散架构升级为 **高内聚专家 skill** 架构
- **13 stage skill**: 每个 stage 自包含 SKILL/README/workflows/references/templates/anti-patterns
- **公共 references/**: 10 个文档（constitution / common-iron-rules / common-anti-patterns / stage-card-protocol / stage-interaction-protocol / dependency-config / document-layer / report-growth / ask-question-anti-patterns / V10-distillation-source-map）
- **公共 scripts/**: 24 个公共 Python 脚本（全部实装，非占位）
- **公共 templates/**: 8 个模板（含 spec / plan / test-plan / domain-models / api-contracts / events / validation-rules / bug）

### 📦继承（V10.10-10.12 蒸馏）

- **17 Articles 宪法**（Article I-XVII，含 V10.10 新增 XV 障碍诚实 + XVI 质疑性校验 + V11.1 新增 XVII Secret Redaction）
- **13 stage 流水线**（-1 Intake → 0 Plan → 0.5 Test Plan → 1 Spec → 1.5 Prototype → 2 Contract → 3 Implement → 3.5 Real Verify → 4 Review → 4.5 Rot Scan → 5 Accept + 6 Bug Fix + 7 Project Health）
- **10 项腐化扫描**（V10.10 NEW）
- **4 维评分**（代码 25% / API 30% / UIUX 25% / 边际 20%）
- **3 类通过依据**（后端编译 / UI 渲染 / 用户视角）
- **5 类项目启动验证**（Web / Tauri / CLI / Library / Backend）
- **Article XV 5 字段阻塞报告**
- **Article XVI 4 维度质疑性校验**

### 🎯 V11 改进（vs V10）

- **SUITE 减肥**: 每个 skill 文件遵循 ≤10 铁律 + ≤150 行（V10.12 减肥）
- **3 层依赖配置**: 全局（user-level）/ V11 / 项目级
- **独立部署**: V11 不依赖 V10 目录
- **runtime 引用归零**: 全部 66 处 V10 运行时路径已替换为 V11 内部 reference

### 📋 scripts/ 实装清单

| # | 脚本 | 状态 |
|---|------|------|
| 1 | _lib_state_card.py | ✅ 实装（状态卡共享库） |
| 2 | acceptance-audit.py | ✅ 实装 |
| 3 | change-status.py | ✅ 实装 |
| 4 | check_integration_contract.py | ✅ 实装 |
| 5 | code-hygiene.py | ✅ 实装 |
| 6 | dispatch-agent.py | ✅ 实装 |
| 7 | dist-hash-check.py | ✅ 实装 |
| 8 | hooks-fidelity.py | ✅ 实装 |
| 9 | init-from-zero.py | ✅ 实装 |
| 10 | install-hooks.py | ✅ 实装 |
| 11 | orphan-detector.py | ✅ 实装 |
| 12 | phase-gate.py | ✅ 实装 |
| 13 | proactive-scan.py | ✅ 实装（10 项 V10.10） |
| 14 | reason-classifier.py | ✅ 实装（6 类抽象理由） |
| 15 | scan-templates.py | ✅ 实装 |
| 16 | self-diagnose.py | ✅ 实装（6 项元检测） |
| 17 | setup-feature.py | ✅ 实装 |
| 18 | spec-knowledge-extract.py | ✅ 实装 |
| 19 | spec-purge.py | ✅ 实装 |
| 20 | stage-gate.py | ✅ 实装 + Fresh 验证 |
| 21 | state-card-validator.py | ✅ 实装 + Fresh 验证 |
| 22 | sync-after-upgrade.py | ✅ 实装 |
| 23 | upgrade-from-v10.py | ✅ 实装 |
| 24 | visual-content-check.py | ✅ 实装（3 层校验） |

### 📋 13 stage skill 文件清单

| Stage | workflows/ | references/ | templates/ | anti-patterns/ | SKILL | README |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|
| 01-intake | 3 | 3 | 2 | 4 + V10 | ✓ | ✓ |
| 02-plan | 1 | 2 | 1 | 4 + V10 | ✓ | ✓ |
| 03-test-plan | 1 | 1 | 1 | 4 + V10 | ✓ | ✓ |
| 04-spec | 1 | 2 | 1 | 3 + V10 | ✓ | ✓ |
| 05-prototype | 2 | 2 | 1 | 4 + V10 | ✓ | ✓ |
| 06-contract | 1 | 2 | 4 | 4 + V10 | ✓ | ✓ |
| 07-implement | 1 | 3 | 0 | 4 + V10 | ✓ | ✓ |
| 08-real-verify | 1 | 3 | 0 | 3 + V10 | ✓ | ✓ |
| 09-review | 1 | 4 | 1 | 4 + V10 | ✓ | ✓ |
| 10-rot-scan | 1 | 2 | 0 | 3 + V10 | ✓ | ✓ |
| 11-accept | 1 | 2 | 0 | 3 + V10 | ✓ | ✓ |
| 12-bug-fix | 1 | 4 | 0 | 4 + V10 | ✓ | ✓ |
| 13-project-health | 1 | 2 | 0 | 3 + V10 | ✓ | ✓ |

总计：14 workflows + 32 references + 11 templates + 44 anti-patterns + 13 SKILL + 13 README = **127 stage 文件**。

### 🎯 部署清单

```bash
# V11 是独立版本，部署到 ~/.trae-cn/skills/fullstack4TraeV11/
cp -r skill-markets/fullstack4TraeV11/* ~/.trae-cn/skills/fullstack4TraeV11/

# 部署前可清理（开发期 reference，不依赖运行时）：
# - references/V10-distillation-source-map.md
# - skills/*/anti-patterns/V10-battle-tested.md
```

### 关联引用

- [SKILL.md](SKILL.md) — V11 总编排器
- [README.md](README.md) — V11 README
- [references/V10-distillation-source-map.md](references/V10-distillation-source-map.md) — V10 → V11 蒸馏溯源