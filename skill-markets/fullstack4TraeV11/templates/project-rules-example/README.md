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

## 4 类 agent 行为（按需配置）

### 场景 A：纯净 web 项目（有 Git、有 secrets）
```
.trae/rules/
├── stack.md    ← pnpm / vitest / playwright
├── paths.md    ← 必有
└── git.md      ← 必有
```

### 场景 B：CLI 工具（无 secrets、无 Git）
```
.trae/rules/
└── stack.md    ← cargo build / cargo test
```

### 场景 C：Library（无 secrets、有 Git）
```
.trae/rules/
├── stack.md    ← cargo test / cargo doc
└── git.md      ← 简化版（无 release 分支）
```

### 场景 D：单文件脚本
```
.trae/rules/    ← 不必有（V11 skill 内部规则已够）
```

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