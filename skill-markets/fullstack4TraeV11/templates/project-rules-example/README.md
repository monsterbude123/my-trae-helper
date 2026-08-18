# 项目级 rules（V11 — 让 agent 按需配置）

> **设计原则**：
> - V11 skill 内部已含的（编码规范、硬编码治理、视觉证据、契约三方同步）→ **绝不复制**
> - 本目录 3 个文件是**项目独有**模板，agent 按项目实际情况配置
> - **不强制**全用：删掉不适用的文件（如 backend 项目可删 stack.md 中的 §5.2 浏览器自动化）
> - 部署位置：项目根目录 `.trae/rules/`

---

## 文件清单（agent 必读）

| 文件 | 何时需要 | 内容 |
|------|---------|------|
| [stack.md](stack.md) | 任何有构建/测试命令的项目 | 构建/测试/lint 命令 + V11 验收 |
| [paths.md](paths.md) | 有 secrets / prod-config / deploy 的项目 | 项目级禁读路径 |
| [git.md](git.md) | 使用 Git 的项目 | 分支策略 + 5 类 stage 标签 + PR 模板 |
| [coding-standards.md](coding-standards.md) | 有项目独有编码规则时 | 桩代码标记 / 数据模型规则 / 命名约定 |

---
## Agent 配置 rules 的 4 步流程

```
Step 1: 读 V11 SKILL.md §0.5 加载协议（确认项目级 rules 必读）
Step 2: Glob 项目根目录，识别：
  - 是否有 package.json / pyproject.toml / Cargo.toml → 必有 stack.md
  - 是否有 deploy/ / secrets/ / prod/ → 必有 paths.md
  - 是否用 Git → 必有 git.md
Step 3: 按项目实际 stack / 团队约定填充占位符
Step 4: 输出到 .trae/rules/
```

## V11.8.7 NEW — 多选+漏选审查+用户通知 三件套（NEW 项目级 rules skill 必读）

Agent 初始化生成 project rules skills 时，**必须**遵循三件套（蒸馏自 `~/.trae-cn/skills/project-rule-skill/SKILL.md` §0）：

```
1. 强制多选          — 一个项目至少包含 2-3 个 rules（如 stack.md + paths.md + git.md），禁止单 rule
2. 强制漏选审查      — 选完后必走 7 维 checklist（paths/code-style/build/git/bug/asset/uncertainty）
                       任一维度 □ 但未加载 → 强制补充,不允许跳过
3. 强制用户通知      — 配置文件清单后必须主动告知用户(场景 + 命中数 + 漏选数 + checklist 命中)
                       就算没选也要说明理由（N/A 描述）
```

**反模式**(任一即 🛑 REJECT):
- ❌ 项目只有 `stack.md` 一个 rule → 缺 git.md（commit 时全乱）
- ❌ 项目只有 `stack.md + git.md` → 漏掉 paths.md（archive/secrets 路径写错）
- ❌ Agent 完成配置后未通知用户（违反铁律 3）
- ❌ 未走 7 维 checklist 自审（违反铁律 2）
- ❌ 单 rule（违反铁律 1）

**7 维 checklist**(agent 必走):

| 维度 | 提问 | 必含 rule |
|------|------|---------|
| **paths / archive** | 项目是否有 secrets/deploy/archive/config 路径? | paths.md |
| **code-style** | 是否有项目独有编码规范(桩代码/命名约定等)? | coding-standards.md |
| **build / dep** | 是否有构建/测试/lint 命令? | stack.md |
| **git / release** | 是否用 Git? | git.md |
| **bug / 反例** | 项目历史是否踩过坑? | anti-patterns.md(从 V11 通用层引用) |
| **asset / 大文件** | 是否有大文件/媒体/二进制管理? | asset-hygiene.md |
| **uncertainty** | 场景模糊或需要兜底? | 全加载 |

## 4 类 agent 行为（按需配置）

### 场景 A：纯净 web 项目（有 Git、有 secrets）— V11.8.7 推荐
```
.trae/rules/
├── stack.md              ← pnpm / vitest / playwright
├── paths.md              ← 必有
└── git.md                ← 必有
```
**触发三件套**:stack.md + paths.md + git.md = 3 rules 命中 ≥2 ✅
**checklist**:paths ☑ / build ☑ / git ☑ / 其余 ☑(N/A 写明)

### 场景 B：CLI 工具（无 secrets、无 Git）— V11.8.7 不推荐
```
.trae/rules/
└── stack.md              ← cargo build / cargo test
```
**⚠️ V11.8.7 反例 B**：只有 1 条 rule 违反强制多选铁律
**修正建议**：补 git.md(即便不常用,也要占位说明 — 后续多场景再用),**或**走"全部加载"兜底

### 场景 C：Library（无 secrets、有 Git）— V11.8.7 推荐
```
.trae/rules/
├── stack.md              ← cargo test / cargo doc
└── git.md                ← 简化版（无 release 分支）
```
**触发三件套**:stack.md + git.md = 2 rules 命中 ≥2 ✅(刚好满足多选)
**checklist**:build ☑ / git ☑

### 场景 D：单文件脚本
```
.trae/rules/             ← 不必有(V11 skill 内部规则已够)
```
**V11.8.7 例外**：单文件脚本 = 0 rules 是合理场景,但 agent 仍要:
1. 走 7 维 checklist 全 N/A
2. **必须告知用户**「单文件脚本场景已判定 = 0 rules,所有维度 N/A」

### V11.8.7 推荐 — 兜底规则（任何场景可触发）

如果项目不能完全套 A/B/C/D,直接给"全加载兜底":

```
.trae/rules/
├── stack.md              ← 构建/测试命令
├── paths.md              ← secrets / archive 禁读
├── git.md                ← 分支策略 + PR 模板
├── coding-standards.md   ← 桩代码标记 / 数据模型 / 命名约定
└── anti-patterns.md      ← 项目踩过的坑(项目级补充,V11 通用层未盖)
```

**完整覆盖 7 维 checklist**,三件套硬约束一次满足。

---

## ❌ 不放在本目录的内容（已在 V11 skill 内）

| 不放 | 在 V11 哪里 |
|------|------------|
| 编码规范（≤800 行/函数 ≤50 行）| `references/common-iron-rules.md` Article I |
| L0-L4 硬编码治理 | `references/dependency-config.md` |
| 视觉证据铁律（≥5KB + ≤7 天）| `skills/08-real-verify/references/visual-evidence.md` |
| 契约三方同步 | `references/document-layer.md` |
| 归档不可变 | `references/common-iron-rules.md` Article VIII |

---

## 关联引用

- [project-agents-example.md](../project-agents-example.md) — AGENTS.md 模板
- [init-from-zero.py](../../scripts/init-from-zero.py) — 仅生成 config + hooks（不生成 rules）