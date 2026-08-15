# Catalog Coverage Evaluation — Skill Catalog 演进记录(V2.0,2026-08-15)

> **V11.8.0 NEW** — 本文档沉淀 Catalog 从 V1 → V2 进阶的全过程,作为未来 V2.1/V3 升级的可复用模板。

---

## §1 背景

V11.7.0 评分制废除 → V11.7.0 门禁制 + V11.8.0 协议先行 + 多维度一致(2026-08-15)。
但**协议先行理念**需要在**新建/升级 skill** 的工作流中落地。最初设计是简单"加几行 MUST",
2026-08-15 三轮蒸馏后,沉淀为 `tests/catalogs/catalog-protocol.md` + `tests/catalogs/skill-catalog.yaml` + `_check_skill_catalog.py`。

**本文档**记录演进过程 + 决策 + 留给 V2.1 的待办。

---

## §2 V1 → V2 演进数据基础(43 SKILL)

| 字段 | V1 覆盖率 | 升级后(V2) |
|------|:---:|:---:|
| `name` | 100% (42/42) | 100%(frontmatter 必填) |
| `description` | 100% (42/42) | 100%(frontmatter 必填) |
| `version` | 31.0% (13/42) | **100%(42/42)**(V2 必填 + 批量补 29 个) |
| `requires` | 26.2% (11/42) | **31.0% (13/42)**(V2 推荐 + auto-fill 2 个) |
| 4 字段全齐 | 19.0% (8/42) | **31.0% (13/42)** |
| 有 frontmatter | 42/43 (97.7%) | **43/43 (100%)**(fullstack-auto 已补) |

---

## §3 三轮决策

### 3.1 第一轮:V1 渐进式(report-only)

- 必填:`name` + `description`(AGENTS.md §1.1 铁律 #1)
- 全部 V1 catalog 工具:`tests/catalogs/catalog-protocol.md` + `_check_skill_catalog.py`
- 默认 exit 0(report-only),`--strict` 才 exit 1

**理由**:34 SKILL 缺 version/requires,直接必填 CI 会全红。**渐进式**是数据驱动决策。

### 3.2 第二轮:V2 进阶(version 必填 + requires 推荐)

- 必填 +1:**`version`**(可批量补 29 个 1.0.0)
- 新增 `recommended_metadata: requires`(WARN 不阻断)
- max_skill_md_lines 350 → 500(避免 false positive)
- min_yaml_frontmatter_fields 2 → 3

**理由**:version 是数值字段,无歧义,29 SKILL 一键补;requires 语义复杂(每个 SKILL 依赖关系不同),需人工 review。

### 3.3 第三轮:V2.1 准备(requires 评估清单)

- 新建 `logs/catalog-v21-evaluate-requires.py`(200+ 行)
- 跨 SKILL 引用扫描(17 个 pattern × 31 SKILL × 全文搜索)
- 自动评估 + 自动填 HIGH 置信度(2/31)+ 评估清单(31 个 YAML 条目)
- 实测:requires 覆盖率从 26.2% → 31.0%(13/42)

---

## §4 关键设计决策(为什么这样选)

### 4.1 为什么 V1 默认 report-only 而不是 fail?

**反例**:直接升级为必填 → 34 SKILL FAIL → CI 全红 → 用户无法 merge PR → 工作流崩溃。

**正解**:先暴露问题(报告),再分阶段补字段(批量 + 人工),最后才升级必填。
**这是 protocol-first 思想的体现** —— **协议先行,但执行要尊重存量**。

### 4.2 为什么 version 必填 + requires 推荐?

| 字段 | 升级理由 |
|------|---------|
| `version` | 数值字段,无歧义,29 SKILL 一键补;`--auto-fill` 类操作风险低 |
| `requires` | 语义依赖每个 SKILL 的具体功能(如 trae-security-review 依赖 guard-approver);批量填风险高 |

**这是"哪类必填可批量,哪类必填需人工"的判断依据**。

### 4.3 为什么把 scripts/catalog-coverage-stats.py 升 references/?

| 来源 | 性质 | 留哪 |
|------|------|------|
| `logs/v11-7-1-closeout.md` | V11.7.1 整改踩坑过程 + 教训 | **升 references/protocol-first-multi-dim.md**(方法论) |
| `logs/catalog-coverage-stats.py` | V2 进阶的数据基础 | **升 references/catalog-coverage-evaluation.md**(决策记录) |
| `logs/v2.1-requires-evaluation.yaml` | V2.1 待办清单 | **升 references/v2.1-requires-evaluation.yaml**(评估产出) |
| `logs/catalog-v2-batch-fill.py` | 一次性工具(已用完) | **留 logs/**(历史脚本,不再用) |
| `logs/catalog-v21-evaluate-requires.py` | V2.1 评估工具 | **升 scripts/**(进项目侧,与 _check_protocol_coverage.py 同级) |

**为什么升**:用户说"事情都做完"+"防止做一半",意味着这些产物是**正式方法论**,不是临时记录。
**为什么不升**:一次性脚本用完即可,留 logs/ 作为时间线。

---

## §5 V2.1 → V3 演进路径(留给后人)

### V2.1 计划(2026-Q3 评估)

- [ ] 评估 29 个 MEDIUM/LOW 置信度 SKILL 的 requires(每个打开看 depends_on)
- [ ] 评估 4 个 > 500 行 SKILL.md 是否提取 references/(agent-dev-control-kit 622 / fullstack4TraeV11 727 / meeting-minutes-taker 670 / session-distiller 526)
- [ ] 升级 requires 必填(全量评估后)
- [ ] catalog V2.1 release notes

### V3 演进方向(2026-Q4 评估)

- [ ] `scope: workflow` — 校验 workflows/*.md 文件存在性
- [ ] `scope: protocol-coverage` — 与 `_check_protocol_coverage.py` 深度集成
- [ ] `scope: catalog-diff` — 比较 SKILL 与 CAPABILITY-MAP 一致性
- [ ] 与 registry/skills.yaml 联动(每个 SKILL 必注册)
- [ ] 与 SECURITY-MAP 联动(每个 SKILL 必评分)

---

## §6 V11.8.0 累计产出(2026-08-15)

### 新增(7 文件)

- `.agents/skills/project-rule-skill/references/skill-creation-workflow.md`(V11.8.0.1 路径迁移,12.9 KB,9 章节)
- `.agents/skills/project-rule-skill/references/protocol-coverage-protocol.md`(V11.8.0.1 路径迁移,10 章节)
- `tests/catalogs/catalog-protocol.md`(11 章节)
- `scripts/_check_protocol_coverage.py`(200+ 行,std lib + argparse)
- `tests/catalogs/_check_skill_catalog.py`(200+ 行)
- `tests/catalogs/skill-catalog.schema.json`
- `tests/catalogs/skill-catalog.yaml`
- `tests/catalogs/README.md`

### 测试(25 用例)

- `tests/unit/test_check_protocol_coverage.py`(14 用例)
- `tests/unit/test_skill_catalog.py`(14 用例)

### 更新(11 文件)

- 29 个 SKILL.md 加 `version: 1.0.0`(批量补)
- 1 个 SKILL.md 加完整 frontmatter(fullstack-auto)
- `AGENTS.md`(§1.3 + §7 多处)
- `CHANGELOG.md`(Unreleased Added 多条目)
- `SECURITY-MAP.md`
- `README.md`(协议先行章节)
- `.agents/rules/README.md`(目录结构)
- `.agents/skills/project-rule-skill/references/skills-development-rules.md`(V11.8.0.1 路径迁移 + 改名,MUST 引用)
- `.agents/skills/project-rule-skill/SKILL.md`(路由表)
- `.github/workflows/skill-market-gate.yml`(L3 §5.7/§5.8 + L4 全量)

### 实扫数据

- trae-security-review: .agents 24 文件 = 0 新命中 ✅
- V11 pytest 49/49 全过 ✅
- catalog 实跑 43 SKILL = 0 错误 + 44 警告 ✅

---

## §7 一句话总结

**Protocol-first + Multi-dim + Catalog V2 = V11.8.0 流程层门禁 + 元数据契约 + 渐进式收紧**。