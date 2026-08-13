# checks.md — 6 项检查规范详解

> 本文件是 `verify.py` 6 项检查的**业务语义规范**，不重复实现细节。实现位置以 `SKILL.md §1` 表中标明。

---

## 1. frontmatter

### 用途
校验 `SKILL.md` YAML frontmatter 的必填字段（`name` / `version` / `description`），确保 Trae IDE 能正确加载并展示。

### 检查什么
- 文件存在 `SKILL.md`
- 首行 `---` 闭合的 YAML 块
- `name` 字段非空 + 等于目录名
- `version` 字段非空
- `description` 字段非空 + 长度 ≥ 30

### 不检查什么
- `requires` / `triggers` 内部 schema（语义层另由 skill 消费方校验）
- 字段值大小写（仅校验存在性 + name 一致）

### 通过标准
无 HIGH 无 MEDIUM（pass）。

### 阻断条件（HIGH）
- `SKILL.md` 不存在
- 缺 frontmatter 分隔符
- 缺 `name` 或 `name` ≠ 目录名
- 缺 `description`

### 警告条件（MEDIUM）
- 缺 `version`
- `description` 长度 < 30

### 示例

| 场景 | 期望 |
|------|------|
| PASS | 全部字段齐全，name 等于目录名 |
| WARN | `version` 缺失，其余合规 |
| BLOCK | `name` 缺失或与目录名不一致 |

### 实现位置
`verify.py::check_frontmatter`

---

## 2. security

### 用途
委托 `trae-security-review/scripts/scan_skills_dir.py` 做静态安全扫描，禁止危险命令 / 动态执行 / 硬编码密钥等 HIGH 风险落地。

### 检查什么
- 危险删除（`rm -rf`）
- 动态代码执行（`eval` / `exec`）
- 硬编码密钥（api_key / token / secret / password / private_key）
- 明文 HTTP 调用
- 弱加密算法引用

### 不检查什么
- 依赖漏洞（`pip-audit` / `npm audit`）— 留给上层 CI 任务
- 运行时权限 — 静态扫描不可见

### 通过标准
findings 中 high=0 且 medium < 3。

### 阻断条件（HIGH）
- 任意 HIGH finding

### 警告条件（MEDIUM）
- 累计 MEDIUM ≥ 3（可叠加跨检查；本项内部 medium ≥ 3 即 WARN）

### 示例

| 场景 | 期望 |
|------|------|
| PASS | 0 high + 0-2 medium |
| WARN | 0 high + ≥ 3 medium |
| BLOCK | 1+ high（任何一项） |

### 实现位置
`verify.py::check_security`（subprocess 调 `scan_skills_dir.py`，解析 stdout JSON）

---

## 3. capability_map

### 用途
校验新 Skill 已登记到 `skill-markets/CAPABILITY-MAP.md`，避免重复造轮子（与现有能力撞车无注册）。

### 检查什么
- `skill-markets/CAPABILITY-MAP.md` 文件存在
- 待验收 skill 的目录名出现在文档正文（精确词边界匹配）

### 不检查什么
- 文档结构合规性（markdown 标题 / 表格 schema）
- 能力摘要的内容深度（仅校验注册项存在）

### 通过标准
注册项存在；`--new-skill` 模式下直接 PASS（仅校验文件存在）。

### 阻断条件（HIGH）
- 未注册 + 非 `--new-skill` 模式
- `CAPABILITY-MAP.md` 整体缺失

### 警告条件
本检查不产生 MEDIUM 警告。

### 示例

| 场景 | 期望 |
|------|------|
| PASS | 目录名命中 `CAPABILITY-MAP.md` |
| PASS（new-skill） | 首次发布，加 `--new-skill` 跳过注册校验 |
| BLOCK | 已发布 Skill 改名后未更新 CAPABILITY-MAP |

### 实现位置
`verify.py::check_capability_map`

---

## 4. scripts_boundary

### 用途
约束 Skill 包脚本规模 + 位置，杜绝单文件超长 + 散落根目录。

### 检查什么
- `scripts/` 子目录存在时，每个 `.py/.sh/.ps1/.mjs/.js/.bat` 文件行数 ≤ 150
- Skill 包根目录（除 `SKILL.md` 外）不得存在脚本文件

### 不检查什么
- scripts/ 内部子目录深度限制（约定 ≤ 2 层）
- 脚本编码规范（lint 另由 IDE 校验）

### 通过标准
无违反 + 无报错。

### 阻断条件（HIGH）
- 单脚本 > 150 行

### 警告条件（MEDIUM）
- 脚本散落根目录（任何 `.py/.sh/.ps1/.mjs/.js/.bat` 在 skill 包根）

### 示例

| 场景 | 期望 |
|------|------|
| PASS | scripts/ 内脚本均 ≤ 150 行，无散落根 |
| WARN | 1 个 `helper.sh` 散落 skill 根目录 |
| BLOCK | `scan.py` 200 行 |

### 实现位置
`verify.py::check_scripts_boundary`

---

## 5. references_size

### 用途
约束 `SKILL.md` 与 `references/` 体积，强制把超长内容下沉到 references（避免 context 击穿）。

### 检查什么
- `SKILL.md` 行数 ≤ 500
- `references/*.md` 总大小 ≤ 200KB

### 不检查什么
- 单个 references 文件的独立上限（依赖总量控制）
- 图片 / 视频 / 二进制文件（这些归 `asset-management-control` 管辖）

### 通过标准
两项均不超阈值。

### 阻断条件（HIGH）
- `SKILL.md` 行数 > 500

### 警告条件（MEDIUM）
- `references/*.md` 总和 > 200KB（提示分散 + 用 `agents/` 拆分）

### 示例

| 场景 | 期望 |
|------|------|
| PASS | SKILL.md 100 行 + references 50KB |
| WARN | references 总和 250KB |
| BLOCK | SKILL.md 600 行 |

### 实现位置
`verify.py::check_references_size`

---

## 6. decision_layer_tag

### 用途
粗粒度检查 `SKILL.md` 是否含项目级方法论关键词（决策层级 / 反例 / 铁律 / references/），作为决策层级标注存在性的最小校验。

### 检查什么
- 4 个关键词命中数：决策层级 / 反例 / 铁律 / `references/`
- 命中 ≥ 2 为佳

### 不检查什么
- 关键词在文档中的位置 / 上下文合理性
- 决策层级是否真落到 L0~L9 完整体系（完整审计留给 `agent-dev-control-kit`）

### 通过标准
命中 ≥ 2 项。

### 阻断条件（HIGH）
- 完全命中 0 项（说明 skill 是单纯操作清单，无决策可追溯）

### 警告条件（MEDIUM）
- 命中 1 项（提示补充决策层级标注）

### 示例

| 场景 | 期望 |
|------|------|
| PASS | 命中 3/4（如含「铁律」「反例」「references/」） |
| WARN | 命中 1/4（仅含「references/」） |
| BLOCK | 命中 0/4（纯操作清单，无决策说明） |

### 实现位置
`verify.py::check_decision_layer_tag`

---

## 汇总

| ID | 阻断条件关键词 | 警告条件关键词 |
|----|----------------|----------------|
| frontmatter | SKILL.md 缺 / name 不一致 / description 缺 | version 缺 / description 短 |
| security | scan_skills_dir high ≥ 1 | medium ≥ 3 |
| capability_map | 未注册（且非 new-skill） | 无 |
| scripts_boundary | 单脚本 > 150 行 | 脚本散落根目录 |
| references_size | SKILL.md > 500 行 | references 总和 > 200KB |
| decision_layer_tag | 关键词命中 = 0 | 关键词命中 = 1 |

**准入逻辑**：6 项中任一 BLOCK → 整体 BLOCK；否则 MEDIUM 累计 ≥ 3 或单项 score < 60 → WARN；其余 PASS。