---
description: 协议覆盖度协议 — 定义"一份协议规范必须被哪些维度引用"的标准与检测机制。是 skill-creation-workflow.md §2.2 多维度同步约束的程序化配套。任何创建/修改/升级协议规范前必读。
alwaysApply: false
enabled: true
updatedAt: 2026-08-15
provider:
---

# Protocol Coverage Protocol — 协议覆盖度协议(V11.8.0 NEW,2026-08-15)

> **协议先行 + 多维度一致**理念的**程序化配套**。
> 一份协议规范(`<topic>-protocol.md`)必须被 6 个维度的文件**显式引用**,缺任何维度 = 该协议未完成。

> **V11.8.0.1 路径迁移通知(2026-08-15 NEW)**:本文件原在 `.agents/rules/protocol-coverage-protocol.md`,V11.8.0.1 起迁移到 `.agents/skills/project-rule-skill/references/protocol-coverage-protocol.md`(与 project-rule-skill 同包,作为其 references/)。
> **原因**:与 project-rule-skill 同包统一管理协议文件。原 `.agents/rules/` 路径留 redirect stub。

---

## §0 背景

[skill-creation-workflow.md](skill-creation-workflow.md) §2 提出"多维度同步"约束,但仅在文档层面。
**本协议把这条约束程序化**:`scripts/_check_protocol_coverage.py` + pytest 14 用例 + CI gate(L3/L4)。

**目的**:**避免"做一半"还能过自检** —— 文档层面写了 6 维度,但实际只有 3 维度引用了 → 传统 review 漏掉 → 本协议自动拦截。

---

## §1 协议定位

| 维度 | 详情 |
|------|------|
| **作用域(scope)** | 所有协议规范(包内 + 项目级) |
| **消费者** | CI gate / 主 agent 升级检查 / 新人 onboarding |
| **执行工具** | [scripts/_check_protocol_coverage.py](../../../../scripts/_check_protocol_coverage.py) |
| **测试** | [tests/unit/test_check_protocol_coverage.py](../../../../tests/unit/test_check_protocol_coverage.py)(14 用例) |

> **V11.8.0.1 路径说明**:本文件位置为 `references/protocol-coverage-protocol.md`(.agents/skills/project-rule-skill/references/ 下),与 `scripts/` 和 `tests/unit/` 相对路径深度不同 — 上述链接中的 `../../../../scripts/` 和 `../../../../tests/` 表示从项目根算起需 4 层 `../`。

---

## §2 维度定义(2 种 scope)

### 2.1 `--scope package`(默认,SKILL 包内协议)

适用:位于 `skill-markets/<pkg>/references/<topic>-protocol.md` 或 `skills/<NN>-*/references/<topic>-protocol.md` 的协议。

**6 维度必引**:

| # | 维度 | 路径 glob | 必引用场景 |
|:-:|------|-----------|:---:|
| 1 | **SKILL.md** | `skill-markets/<pkg>/SKILL.md` | ✅ 协议有新增/修改 |
| 2 | **reference** | `skill-markets/<pkg>/references/*.md` | ✅ 协议有新增/修改 |
| 3 | **workflow** | `skill-markets/<pkg>/skills/<NN>-*/workflows/*.md` | ✅ 流程有变 |
| 4 | **script** | `skill-markets/<pkg>/scripts/*.py` | ✅ 行为有变 |
| 5 | **guard** | `scripts/<pkg>-*.{py,mjs}` | ✅ 触发器有变 |
| 6 | **other-refs** | `AGENTS.md` + `CAPABILITY-MAP.md` + `SECURITY-MAP.md` + `README.md` + `CHANGELOG.md` | ✅ 项目级文档有变 |

### 2.2 `--scope global`(项目级规则)

适用:位于 `.agents/rules/<topic>.md` 或 `.trae/rules/<topic>.md` 的全局规则。

**1 维度必引(other-refs)**:

| # | 维度 | 路径 glob |
|:-:|------|-----------|
| 1 | **other-refs** | `AGENTS.md` + `.agents/skills/*/SKILL.md` + `.agents/skills/project-rule-skill/SKILL.md` + `.trae/rules/*.md` + `skill-markets/CAPABILITY-MAP.md` + `SECURITY-MAP.md` + `README.md` + `CHANGELOG.md` |

> **V11.8.0.1 调整说明**:本协议 V11.8.0.1 自身已迁移到 `.agents/skills/project-rule-skill/references/`,但**协议覆盖度的扫描维度仍然认 `.agents/rules/*.md`** —— 协议文档的"位置"与"协议覆盖度作用域"是**两个独立维度**,不要混淆。
> 如果未来项目级协议统一迁移到 `project-rule-skill/references/`,则 `--scope global` 路径 glob 需同步调整(V11.8.2 留待)。

**为什么 scope global 只 1 维度**:全局规则**不是某个 SKILL 包内部协议**,不需要被 skill 包 SKILL.md / workflow 等引用,只需在项目级文档中引用,保证 agent 工作流能发现。

---

## §3 引用检测机制(3 种引用形式)

`_check_protocol_coverage.py` 识别以下 3 种引用形式:

| 形式 | 示例 | 说明 |
|------|------|------|
| **文件名引用** | `见 skill-creation-workflow.md` | 最简洁,推荐 |
| **相对路径引用** | `[规则](skill-creation-workflow.md)` | Markdown 链接 |
| **stem 引用** | `详见 skill-creation-workflow` | 不带 .md 后缀的文本提及 |

**反例**(不识别):

- ❌ 只在 commit message 里提了协议 → 不算引用(commit msg 不在搜索范围)
- ❌ 只在 issue/PR 描述里提了 → 不算引用
- ❌ 文件名相近但不同(如 `skill-creation-workflow-archive.md`)→ 不算引用(stem 严格匹配)

---

## §4 CI 接入(L3/L4 门禁)

[.github/workflows/skill-market-gate.yml](../../../../.github/workflows/skill-market-gate.yml) §5.7 步:

### 4.1 L3 PR merge gate

```
触发条件: PR 改了 (references|skills)/*-protocol.md 或 .agents/rules/*.md 或 .agents/skills/project-rule-skill/references/*.md
行为:
  - 遍历 git diff 检测到的协议/规则文件
  - 按路径自动判 scope(`.agents/rules/` → global,其他 → package)
  - 逐个跑 `python scripts/_check_protocol_coverage.py --protocol <target> --scope <SCOPE> --check`
  - 任一 FAIL → 阻断 PR merge
```

### 4.2 L4 Release gate

```
触发条件: Release 发布
行为:
  - 全量扫描 skill-markets/*/*-protocol.md + .agents/rules/*.md + .agents/skills/project-rule-skill/references/*-protocol.md
  - 全部跑 --check
  - 任一 FAIL → 阻断发布
```

### 4.3 三态自验收(必须)

CI gate 上线前必须固化 3 态样本(同 AGENTS.md §2.4 Gate 自验收强制):

| 样本 | 期望 | 验证命令 |
|------|------|---------|
| **PASS 态** | 6 维度全引用的协议 → exit 0 | pytest `test_check_protocol_coverage.py::TestMainCli::test_global_scope_passes` |
| **FAIL 态** | 未被引用的协议 → exit 1 | `test_global_scope_fails_when_unreferenced` |
| **边界态** | 协议文件不存在 → exit 1 + 报错 | `test_nonexistent_protocol_exits_1` |

---

## §5 自检清单(创建协议后必跑)

```bash
# 1. 协议覆盖度(本协议核心)
python scripts/_check_protocol_coverage.py \
    --protocol <my-protocol>.md \
    --scope {package|global} \
    --check

# 2. pytest 回归
python -m pytest tests/unit/test_check_protocol_coverage.py -v

# 3. CI gate 模拟(L3 步的真实逻辑)
git diff --name-only HEAD~1 HEAD | grep -E '(references|skills)/.*-protocol\.md$'
# 应输出空(本轮无协议变更)或本轮变更的协议路径
```

**全 PASS 才能 commit**。

---

## §6 与现有体系联动

| 联动资源 | 关系 |
|---------|------|
| [skill-creation-workflow.md](skill-creation-workflow.md) §2 | **上游** — 本协议是 §2 多维度同步约束的**程序化** |
| [skill-creation-workflow.md](skill-creation-workflow.md) §7 | **协同** — §7 失败模式自检的"协议规范写了吗?"可由本协议 CI 自动检 |
| [AGENTS.md §1.12](../../../../AGENTS.md) | **协同** — guard/gate 调整 7 步 SOP 中第 6 步"主 agent 自己兜底验证"可纳入本协议 |
| [AGENTS.md §6](../../../../AGENTS.md) | **协同** — 安全审查必走 + 本协议 CI gate 同款 |
| [AGENTS.md §7](../../../../AGENTS.md) §7 | **协同** — 能力地图列了本协议(待补) |
| [tests/catalogs/skill-catalog.yaml](../../../../tests/catalogs/skill-catalog.yaml) | **协同** — catalog 应校验 SKILL 含 references/*-protocol.md(如有) |

---

## §7 反例库(必避免)

| # | 反例 | 后果 | 防范 |
|:-:|------|------|------|
| 1 | 协议只写了一半就 commit,只引了 2 维度 | CI gate FAIL,误以为过自检 | §5 强制跑 `--check` |
| 2 | 改了协议但忘了同步 SKILL.md | CI gate FAIL(reference/workflow 维度未引) | §5 + `skill-creation-workflow.md` §7 |
| 3 | `--scope package` 用在 `.agents/rules/*.md` | 检测 FAIL(维度路径不匹配) | 强制按路径自动判 scope(已在 CI 实现) |
| 4 | `--scope global` 用在 `skill-markets/<pkg>/...` | 漏检 SKILL.md/workflow 维度 | 同上 |
| 5 | 协议引用写到文件名但 `.md` 错(typo) | `--check` 不识别,FAIL 但找不到原因 | §5 + 手工验证 |

---

## §8 自我应用(本协议的协议覆盖度)

本协议本身(`protocol-coverage-protocol.md`)也应被多维度引用,自检:

```bash
python scripts/_check_protocol_coverage.py \
    --protocol .agents/skills/project-rule-skill/references/protocol-coverage-protocol.md \
    --scope global --check
```

**期望**:✅ PASS — 应被 `AGENTS.md` + `README.md` + `SECURITY-MAP.md` 等引用。

如果 FAIL,按 §5 §6 补全引用。

---

## §9 版本与维护

- **初版**:2026-08-15 V1.0.0
- **V11.8.0.1**:2026-08-15 路径迁移至 `.agents/skills/project-rule-skill/references/`
- **维护者**:my-trae-helper team
- **触发更新**:
  - 新增 scope 类型(如 `--scope skill-internal`)时
  - 维度集合变化时(如新增"模板"维度)
  - pytest 14 用例随维度调整

---

## §10 关联资源

- **决策记录**:`references/catalog-coverage-evaluation.md`(V11.8.0 演进数据 + 决策依据)
- **踩坑沉淀**:`references/protocol-first-multi-dim.md`(V11.7.1 整改踩坑过程)
- **V2.1 评估**:`references/v2.1-requires-evaluation.yaml`(requires 字段待办清单)
- **Catalog 校验**:`tests/catalogs/catalog-protocol.md`(skill 元数据校验协议)
- **评估工具**:`scripts/catalog-v21-evaluate-requires.py`(200+ 行 std lib)
- **本 skill 入口**:`../SKILL.md`(.agents/skills/project-rule-skill/SKILL.md)

---

## §11 一句话总结

**协议先行 + 多维度一致 = 文档驱动 + 机械兜底。CI gate + pytest 双保险。**