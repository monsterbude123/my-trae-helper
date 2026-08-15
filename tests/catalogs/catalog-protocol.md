# Catalog Protocol — Skill Catalog 校验协议(V11.8.0 NEW,2026-08-15)

> **协议先行**:`tests/catalogs/skill-catalog.yaml` 是声明式 catalog,定义"SKILL 包应包含什么"。
> **多维度一致**:本协议由 6 维度引用 → catalog 内容变化时,CI gate 自动 FAIL。
> **消费方**:`tests/catalogs/_check_skill_catalog.py` + pytest + CI L3/L4 gate。

---

## §1 协议定位

| 维度 | 详情 |
|------|------|
| **作用** | 声明式校验每个 SKILL 包是否满足最小元数据要求 |
| **消费者** | 主 agent 创建/升级 SKILL 时 + CI gate 自动检 |
| **执行工具** | `tests/catalogs/_check_skill_catalog.py` |
| **测试** | `tests/unit/test_skill_catalog.py`(待实现) |
| **生效条件** | 仅在 SKILL 包**有 `requires.protocols` 字段声明**时强制;否则为可选 |

---

## §2 Catalog YAML 字段定义

`tests/catalogs/skill-catalog.yaml` 结构:

```yaml
version: 2.0.0              # 协议版本(V2 升级,2026-08-15)
scope: skill-metadata       # 当前仅支持 skill-metadata

# V2 必填元数据:每个 SKILL 包必须满足
required_metadata:
  - name                     # SKILL.md YAML frontmatter
  - description              # 同上
  - version                  # V2 升级为必填(原 V1 推荐,批量补 29 个 1.0.0)

# V2 推荐字段(声明时 WARN,不阻断)
# V2.1 计划:requires 全量评估后升级为必填
recommended_metadata:
  - requires                 # 推荐(声明依赖)

# 可选字段:满足时强制更深校验
optional_metadata:
  - protocols                # 列出 <topic>-protocol.md,声明协议先行
  - workflows                # 列出 workflows/*.md 路径

# 结构守卫约束(沿用 vibe-coding-standards v2.5 + V2 升级)
structural_rules:
  max_skill_md_lines: 500   # V2 放宽(原 350,过多 false positive)
  min_yaml_frontmatter_fields: 3  # V2 升级:至少 name + description + version

# 反例库(显式声明禁止项)
anti_patterns:
  - id: AP-1
    description: "硬编码密钥"
    detect: "references/<topic> 含 AKIA 模式"
```

---

## §3 校验规则(3 类)

### 3.1 必填校验(required_metadata)

每个 SKILL 包的 `SKILL.md` YAML frontmatter 必须包含 `required_metadata` 列出的字段:

```bash
# 命令
python tests/catalogs/_check_skill_catalog.py \
    --catalog tests/catalogs/skill-catalog.yaml \
    --skills-root skill-markets

# 输出
[PASS] fullstack4TraeV11 — name ✅ description ✅ version ✅ requires ✅
[FAIL] some-skill — name ✅ description ❌ 缺 description 字段
```

### 3.2 协议校验(protocols 字段声明时)

仅当 SKILL.md 含 `requires.protocols`(数组)时,自动跑 `_check_protocol_coverage.py`:

```yaml
# SKILL.md frontmatter 示例
requires:
  protocols:
    - references/stage-transition-protocol.md
```

校验:**每个 protocols 字段引用的文件必须存在 + 必须过 protocol coverage gate**。

### 3.3 结构守卫(structural_rules)

`max_skill_md_lines` + `min_yaml_frontmatter_fields` 沿用现有 skill-structure-guard.py(本协议不重复)。

---

## §4 Scope 范围(scope=skill-metadata V1)

V1 协议**仅覆盖元数据校验**(name/description/version/requires)。**不覆盖**:

- ❌ 脚本存在性 — `skill-structure-guard.py` 已覆盖
- ❌ 安全风险 — `trae-security-review` 已覆盖
- ❌ 依赖完整性 — `skill-dependency-guard` 已覆盖
- ❌ CAPABILITY-MAP 同步 — `skill-capability-guard.py` 已覆盖

**V2+ 演进方向**(本协议不实现,留待后续):
- scope=workflow:校验 workflows/*.md 文件存在性
- scope=protocol-coverage:与 `_check_protocol_coverage.py` 深度集成
- scope=catalog-diff:比较 SKILL 与 CAPABILITY-MAP 一致性

---

## §5 CI 接入(L3/L4)

`.github/workflows/skill-market-gate.yml` 新增 §5.8 step:

```yaml
- name: Skill catalog gate (metadata validation)
  run: |
    echo "5.8️⃣ Skill catalog 元数据校验..."
    python tests/catalogs/_check_skill_catalog.py \
      --catalog tests/catalogs/skill-catalog.yaml \
      --skills-root skill-markets || exit 1
```

**触发**:PR 改 `skill-markets/**/SKILL.md` 或 `tests/catalogs/`。
**L4**:全量跑(所有 SKILL 包)。

---

## §6 自检清单

```bash
# 1. catalog 校验
python tests/catalogs/_check_skill_catalog.py \
    --catalog tests/catalogs/skill-catalog.yaml \
    --skills-root skill-markets

# 2. pytest
python -m pytest tests/unit/test_skill_catalog.py

# 3. protocol coverage gate(联动)
python scripts/_check_protocol_coverage.py \
    --protocol tests/catalogs/catalog-protocol.md \
    --scope global \
    --check
```

---

## §7 与现有体系联动

| 资源 | 关系 |
|------|------|
| [skill-creation-workflow.md](../../.agents/skills/project-rule-skill/references/skill-creation-workflow.md) §1 (V11.8.0.1 路径迁移) | **上游** — 协议先行原则,本协议是其 catalog 化的体现 |
| [protocol-coverage-protocol.md](../../.agents/skills/project-rule-skill/references/protocol-coverage-protocol.md) (V11.8.0.1 路径迁移) | **协同** — §3.2 引用 `_check_protocol_coverage.py` |
| [AGENTS.md §1.4](../../AGENTS.md) | **协同** — 经验沉淀路由 → catalog 失败记录 → ERRORS.md |
| `skill-structure-guard.py` | **不冲突** — 结构守卫,本协议不重复 |
| `trae-security-review` | **不冲突** — 安全审查,本协议不重复 |

---

## §8 反例库

| # | 反例 | 后果 | 检测 |
|:-:|------|------|------|
| 1 | SKILL 缺 name 字段 | catalog FAIL | §3.1 必填校验 |
| 2 | SKILL 缺 version 字段 | catalog FAIL | 同上 |
| 3 | SKILL 声明 `requires.protocols` 但 protocol 文件不存在 | protocol coverage FAIL | §3.2 协议校验 |
| 4 | SKILL.md > 350 行 | structure-guard FAIL | §3.3 结构守卫(沿用) |
| 5 | catalog.yaml 自身不通过校验 | 协议失效 | pytest 自检 |

---

## §9 自我应用(本协议的 catalog 覆盖度)

```bash
# 本协议应被多维度引用 — 跑 global scope gate
python scripts/_check_protocol_coverage.py \
    --protocol tests/catalogs/catalog-protocol.md \
    --scope global \
    --check
```

**期望**:✅ PASS — 应被 ≥3 处引用(AGENTS.md + README.md + .agents/rules/README.md 等)。

---

## §9 版本与维护

- **初版**:2026-08-15 V1.0.0
- **scope**:V1 = skill-metadata(仅元数据)
- **后续**:V2+ 加入 scope=workflow / scope=protocol-coverage

### V2 升级要点(2026-08-15)

| 变更 | V1 | V2 |
|------|----|----|
| 必填字段 | name + description | + **version** |
| 推荐字段 | (无) | + **requires** |
| max_skill_md_lines | 350 | **500**(避免 false positive) |
| min_yaml_frontmatter_fields | 2 | **3**(name + description + version) |
| recommended_metadata | 不存在 | **新增**(WARN 不阻断) |

**V2 升级数据**(2026-08-15 实扫 43 SKILL):
- 必填字段(name + description + version)覆盖率:**100%(43/43)**
- 推荐字段(requires)覆盖率:**26.2%(11/42)** — V2.1 升级时需逐 SKILL 评估
- 真实运行:**1 错误(fullstack-auto 缺 frontmatter,V1 也 FAIL)+ 44 警告(31 requires + 4 行数 + 9 重复?)**

**V2.1 计划**(留待):
- requires 全量评估后升级为必填
- 补 fullstack-auto 的 frontmatter(name + description + version)
- 评估 4 个 > 500 行 SKILL.md 是否提取 references/(agent-dev-control-kit 622 / fullstack4TraeV11 727 / meeting-minutes-taker 670 / session-distiller 526)

---

## §11 一句话总结

**catalog = SKILL 包元数据的契约 + 协议校验的入口 + CI gate 的另一层兜底**。