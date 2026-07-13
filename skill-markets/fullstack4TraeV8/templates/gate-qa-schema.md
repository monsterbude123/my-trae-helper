# Schema QA — 结构化门禁检查模板（V7 NEW）

> 这是 Agent 进行门禁自检和产出验证时的**格式模板**，不是固定检查清单。

---

## 设计动机

传统的审查输出是叙事性的：

```
"我检查了 contracts/ 目录，发现 api-contracts.md 存在但缺少 POST /users 接口的定义，
domain-models.md 已被审批，event-contracts.md 被标记为不适用。建议补充缺少的接口定义后
进入下一阶段。"
```

问题：
- 主 Agent 需要 NLP 解析才能提取结论（"存在""缺少""不适用"）
- 每个检查项消耗大量 token（描述性的段落 vs 结构化的行）
- 升级时需要改 prompt 模板，输出格式可能漂移

Schema QA 用 **Q→A 格式** 替代叙事输出：

```
Q: [GATE][G-01][api-contracts.md 中定义的 POST /users 与 domain-models.md 的 User 实体字段是否一致][一致/不一致/部分不一致][对比两个文件中的字段定义]
A: [G-01][不一致][api-contracts 含 phone 字段但 domain-models 的 User 实体缺少该字段]

Q: [GATE][G-02][api-contracts.md 的 POST /users 响应是否声明了所有可能的错误码][完整/缺失/未声明错误码][检查 4xx/5xx 响应定义]
A: [G-02][缺失][只定义了 201，缺少 400/409/422 错误响应]
```

---

## 核心原则：脚本能做的，不走 LLM

**不是所有检查都值得 LLM 过一遍。** 以下边界必须遵守：

| 检查类型 | 举例 | 执行者 | 输出格式 |
|---------|------|--------|---------|
| **机械检查** | 文件是否存在、目录结构是否正确、文件大小/行数、格式校验 | 本地脚本 | Schema 化（同 Q→A） |
| **逻辑审查** | 两个文件内容一致性、接口设计合理性、错误码完整性、语义冲突 | LLM（Agent） | Schema QA |

**脚本检查的输出也走 Schema 格式**（见下文"脚本 Kit Schema 化输出"），保证所有检查结果统一可消费。

### Kit 复用原则

Agent 在工作过程中发现的**可脚本化的检查**，不要每次都临时写脚本：
1. 将脚本沉淀到 `项目根目录/scripts/debug/` 
2. 在 `scripts/debug/INDEX.md` 中登记脚本用途、输入参数、输出格式
3. 后续同类检查直接调用已有脚本，不重复造轮子
4. 脚本输出统一使用 Schema Q→A 格式，与 LLM 门禁输出兼容

```
scripts/debug/
├── INDEX.md                  # 脚本索引（用途 / 参数 / 输出格式 / 适用场景）
├── check-file-structure.sh   # 检查目录/文件是否存在
├── check-contract-count.sh   # 检查 contracts/ 4 文件是否齐全
├── diff-contracts.sh         # 对比两个 contracts 文件的字段差异（结构化 diff）
└── ...
```

---

## 格式规范

### Q（问题）格式

```
Q: [分类码][编号][检查内容][选项列表][补充提示]
```

| 字段 | 必填 | 说明 | 示例 |
|------|------|------|------|
| 分类码 | ✅ | 标识检查类型 | `GATE` / `DRIFT` / `POST` / `SYNC` / `COCKPIT` / `KIT` |
| 编号 | ✅ | 唯一标识，格式 `{分类码首字母}-{序号}` | `G-01`, `D-03`, `P-02`, `K-01` |
| 检查内容 | ✅ | 简洁的自然语言描述 | `api-contracts 的 User 字段与 domain-models 是否一致` |
| 选项列表 | ✅ | 用 `/` 分隔的互斥选项，覆盖所有可能结果 | `一致/不一致/部分不一致` |
| 补充提示 | — | 给 LLM 或脚本执行者的辅助信息 | `对比两个文件中的字段定义` |

**选项设计原则**：
- 覆盖所有可能结果（包括"不确定""部分满足""不适用"等模糊态）
- 选项互斥（一个 Q 只有一个 A）
- 最后一个选项可以是"其他：{自由描述}"应对未预期的结果

### A（答案）格式

```
A: [编号][选项][备注]
```

| 字段 | 必填 | 说明 |
|------|------|------|
| 编号 | ✅ | 对应 Q 的编号 |
| 选项 | ✅ | 从 Q 的选项列表中选取 |
| 备注 | — | 补充证据、路径、原因等上下文 |

---

## 分类码速查

| 分类码 | 含义 | 使用场景 | 执行者 |
|--------|------|---------|--------|
| `GATE` | 门禁逻辑审查 | DOC SYNC GATE / CONTRACT GATE 中需要 LLM 判断的部分 | LLM |
| `DRIFT` | 漂移检测 | 契约 vs 代码语义一致性 / Spec vs 代码行为一致性 | LLM |
| `COCK` | Cockpit 自检 | 状态卡 vs 文件系统一致性（逻辑层面） | LLM |
| `POST` | 后置自检 | Agent 产出完成后的语义验证 | LLM |
| `PRE` | 前置检查 | Agent 激活时的前置条件验证 | LLM |
| `SYNC` | 同步检查 | 文档同步状态 / 原型回流状态 | LLM |
| `ARCH` | 归档检查 | archive/out/ / archive/done/ 分类合理性验证 | LLM |
| `KIT` | 脚本 Kit 检查 | 机械性检查（文件存在、计数、格式校验等） | 本地脚本 |

> **注意**：`KIT` 分类码的 Q 和 A 都由脚本生成，不走 LLM。Agent 收集脚本输出后合并到自检汇总中。

---

## 使用方式

### Agent 自生成 Q

Agent 根据当前上下文**自己生成 Q**，不是从固定列表复制：

```
Agent 激活时：
1. 识别当前阶段 → 确定需要哪些分类码
2. 区分：哪些是机械检查 → 调已有脚本（KIT）
3. 区分：哪些是逻辑审查 → 自生成 Q（GATE/POST/DRIFT/...）
4. 执行脚本 → 收集 KIT 输出 → 与 LLM 自检结果合并
5. 汇总：所有 A 中是否有非期望选项 → 决定下一步
```

**关键**：Q 是动态的，取决于当前上下文中有什么需要检查的。两个不同的 change 产出的 Q 列表必然不同。

### 自检场景速查

| 场景 | 分类码 | 典型 Q 数量 | 触发者 |
|------|--------|------------|--------|
| 新会话启动 | `COCK`+`KIT` | 每个工件 1 Q | 主 Agent |
| DOC SYNC GATE | `GATE`+`KIT` | KIT 2-3 Q + GATE 2-4 Q | implementer |
| CONTRACT GATE | `GATE`+`KIT` | KIT 1-2 Q + GATE 2-4 Q | implementer |
| Agent 产出完成 | `POST` | 3-8 Q | 当前 Agent（自省） |
| 阶段切换 | `PRE`+`POST`+`KIT` | KIT 1-2 Q + PRE 2-4 Q + POST 3-5 Q | 主 Agent |
| 漂移检测 | `DRIFT` | 每个接口 1 Q | implementer/reviewer |
| 归档验证 | `ARCH`+`KIT` | KIT 2-3 Q + ARCH 2-3 Q | doc-updater |

---

## 示例：DOC SYNC GATE（逻辑审查 + 脚本 Kit 合并）

```
情境: implementer 激活，准备编码前检查文档同步状态

--- 脚本 Kit 检查（Agent 调脚本，不走 LLM）---
Q: [KIT][K-01][contracts/ 目录 4 文件是否齐全][齐全/缺失][check-contract-count.sh]
Q: [KIT][K-02][docs/modules/user.md 是否存在][存在/不存在][check-file-structure.sh --path docs/modules/user.md]

A: [K-01][齐全][api-contracts.md, domain-models.md, event-contracts.md, validation-rules.md 均存在]
A: [K-02][存在][路径: docs/modules/user.md]

--- LLM 逻辑审查（Agent 自生成 Q）---
Q: [GATE][G-01][user.md 的接口契约段与 contracts/api-contracts.md 是否语义一致][一致/不一致/无法判定][对比两个文件的接口定义]
Q: [GATE][G-02][user.md 的 P0 内容（接口契约+数据模型）是否完整覆盖 contracts/ 的声明][完整覆盖/部分覆盖/未覆盖]
Q: [GATE][G-03][contracts/validation-rules.md 中的校验规则是否在 user.md 中有对应说明][全部对应/部分对应/未对应]
Q: [GATE][G-04][如涉及 UI 变更，docs/prototypes/ 的原型与 contracts/api-contracts.md 的接口是否匹配][不涉及/匹配/不匹配]

A: [G-01][不一致][contracts/ 中 POST /users 含 phone 字段，user.md 的接口段未列出 phone]
A: [G-02][部分覆盖][接口契约段存在但缺少 phone 字段，数据模型段已同步]
A: [G-03][部分对应][email 格式校验已对应，phone 校验规则缺失]
A: [G-04][不涉及][本次变更无 UI 变更]

→ 汇总: G-01 不一致 + G-02 部分覆盖 + G-03 部分对应 → 🛑 DOC SYNC GATE 未通过 → 先同步文档
```

---

## 示例：Agent Post-Check 自省（纯 LLM 逻辑审查）

```
情境: proposal-writer 完成 proposal.md，触发后置自检

Q: [POST][P-01][proposal.md 的 Why 段是否建立了清晰的业务动机而非泛泛而谈][清晰/笼统/缺失]
Q: [POST][P-02][Capabilities 声明是否可验证——每个能力是否有明确的完成标准][可验证/部分可验证/不可验证]
Q: [POST][P-03][Non-Goals 是否排除了容易被误解为"遗漏"的内容][是/否/未声明 Non-Goals]
Q: [POST][P-04][每个 Capability 与 specs/ 子目录的映射是否完整且无冗余][完整/有遗漏/有冗余]
Q: [POST][P-05][提案范围是否与分级（简单/中等/复杂）匹配][匹配/偏小/膨胀]

A: [P-01][清晰][引用了用户反馈"注册流程流失率40%"，量化了改进目标]
A: [P-02][可验证][2 个能力均可验证: single-page-register → 注册步骤≤1页，sms-verification → 验证成功率≥95%]
A: [P-03][是][排除了社交登录、密码强度策略变更，避免歧义]
A: [P-04][完整][2 个 Capability → 2 个 specs/ 子目录，无遗漏无冗余]
A: [P-05][匹配][312 词，中等复杂度提案范围合理]

→ 汇总: 全部通过 → 移交 spec-writer
```

---

## 示例：脚本 Kit 的 Schema 化输出

```
情境: Agent 调用 check-contract-count.sh 检查 contracts/ 完整性

脚本 check-contract-count.sh 输出（Schema 格式）:

Q: [KIT][K-01][contracts/ 目录是否存在][存在/不存在]
Q: [KIT][K-02][contracts/ 下 4 个必要文件是否齐全][齐全/缺失N个][api-contracts.md, domain-models.md, event-contracts.md, validation-rules.md]
Q: [KIT][K-03][contracts/ 下是否存在多余文件][无多余/有多余]

A: [K-01][存在][路径: docs/specs/changes/01-user-auth/contracts/]
A: [K-02][齐全][4/4 文件均存在且非空]
A: [K-03][无多余][仅包含必要文件]

→ 脚本退出码 0 → Agent 继续 LLM 逻辑审查
```

**脚本编写规范**：
- 输出严格遵循 Q→A Schema 格式
- 退出码 0 = 全部通过，非 0 = 有失败项（具体看 A 的选项）
- 在 `scripts/debug/INDEX.md` 中登记：脚本名、用途、参数、输出 Q 数量、适用阶段
- Agent 调用脚本后，将 KIT 输出原样合并到自检 QA 汇总中

---

## 与叙事输出的关系

Schema QA **不替代**叙事输出，而是作为叙事的前置过滤：

```
Agent 产出叙事内容（proposal.md / design.md / 代码）
  → 调脚本 Kit → 机械检查通过
  → Agent 自省: 用 Schema QA 快速逐项筛查逻辑问题
  → Q 全部通过 → 叙事内容 + QA 汇总（含 KIT）一起移交
  → Q 有失败项 → 修复 → 重新自省 → 通过后再移交
```

叙事内容回答"怎么做"和"为什么"，Schema QA 回答"做对了没有"，脚本 Kit 回答"东西齐了没有"。

---

## 输出建议

QA 汇总在 Agent 输出末尾附加，KIT 和 LLM 自检合并展示：

```markdown
## 自检 QA 汇总

### 脚本 Kit 检查
| 编号 | 检查项 | 结果 | 备注 |
|------|--------|------|------|
| K-01 | contracts/ 4 文件齐全 | 通过 | 4/4 |
| K-02 | user.md 存在 | 通过 | — |

### LLM 逻辑审查
| 编号 | 检查项 | 结果 | 备注 |
|------|--------|------|------|
| G-01 | 接口契约语义一致 | 未通过 | phone 字段缺失 |
| G-02 | P0 内容覆盖 | 未通过 | 接口契约段不同步 |
| G-03 | 校验规则对应 | 未通过 | phone 校验规则缺失 |

结论: 🛑 KIT 2/2 通过，GATE 0/3 通过 → DOC SYNC GATE 未通过 → 先同步文档
```
