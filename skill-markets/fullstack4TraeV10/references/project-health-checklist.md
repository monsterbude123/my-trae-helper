# Project Health Checklist（V10.9）

> **来源**: `agents/project-health-auditor.md` §检查维度
> **用途**: project-health-auditor 子代理执行自检时的详细检查清单
> **加载时机**: 子代理被委派时自动读取

本文档承载 **4 维度检查的详细命令 + 判定标准 + 证据采集**，agent 文件本身只保留骨架工作流，详情按需查阅本文档。

---

## 维度 1：路径一致性

### 检查项

- [ ] `docs/constitution.md` 存在（V10.8 迁移路径）
- [ ] `docs/ARCHITECTURE.md` 存在
- [ ] `docs/INDEX.md` 存在且格式合规（含 Active Specs / Archived Specs / Module Map / Architecture 4 段）
- [ ] `docs/specs/{feature}/` 目录结构符合规范（plan.md / spec.md / tasks.md / contracts/ / prototypes/）
- [ ] 无相对路径混用（agents 文件路径前缀统一为 `docs/`）

### 检查命令

```bash
ls docs/constitution.md docs/ARCHITECTURE.md docs/INDEX.md docs/specs/
```

### 判定标准

- ✅ **全部存在且格式合规**
- ⚠️ **部分缺失或格式不合规**（列出具体）
- ❌ **严重缺失**（核心路径不存在）

---

## 维度 2：目录树完整性

### 检查项

- [ ] `docs/specs/.state-card.md` 存在且行数 ≤ 80（硬上限）
- [ ] `docs/verifications/tauri/` 存在（全栈项目）
- [ ] `docs/modules/` 存在（全栈/后端项目）
- [ ] `docs/api-endpoints/` / `docs/domain-models/` / `docs/events/` 存在（后端项目）
- [ ] `.trae/hooks.json` 存在（项目级 Hook 配置）

### 检查命令

```bash
ls docs/specs/.state-card.md docs/verifications/tauri/ docs/modules/ .trae/hooks.json
wc -l docs/specs/.state-card.md
```

### 判定标准

- ✅ **全部存在**
- ⚠️ **部分缺失**（列出具体）
- ❌ **严重缺失**（核心目录不存在）

---

## 维度 3：版本残留 + 污染检测

### 检查项

- [ ] 无 V8/V9 残留路径（`.specify/` / `docs/prototypes/`（非 feature 级））
- [ ] 无项目特定路径硬编码到通用文档（如 `aigc-desktop-ui.design/`）
- [ ] 无绝对路径硬编码（如 `d:\workspace\...`）
- [ ] 无旧版 change 目录写法（`specs/changes/{change}/` / `docs/specs/changes/{change}/`）

### 检查命令

```bash
grep -r "\.specify/" docs/
grep -r "docs/prototypes/" docs/    # 排除 feature 级
grep -r "aigc-desktop-ui.design" .
grep -r "d:\\\\" docs/
grep -r "specs/changes/" .
```

### 判定标准

- ✅ **无残留和污染**
- ⚠️ **发现残留或污染**（列出具体文件/行号）
- ❌ **严重污染**（多处硬编码）

---

## 维度 4：文档同步机制（layer 标签）

### 检查项

- [ ] `docs/` 下 .md 文件有 `layer:` frontmatter（fact/process/log）
- [ ] layer 标签覆盖率 ≥ 80%（fact/process/log 分布合理）
- [ ] 索引器白黑名单符合 doc-sync.md 规范（无 `docs/archive/` / `docs/bugs/` 等黑名单路径被索引）

### 检查命令

```bash
find docs/ -name "*.md" -exec grep -l "^layer:" {} \; | wc -l
find docs/ -name "*.md" | wc -l
```

### 判定标准

- ✅ **覆盖率 ≥ 80% 且白黑名单合规**
- ⚠️ **覆盖率 < 80% 或白黑名单不合规**
- ❌ **无 layer 标签或黑名单路径被索引**

---

## 项目类型判定规则

| 项目类型 | 判定条件 | 典型路径特征 |
|----------|---------|-------------|
| **CLI 项目** | 只有 `pyproject.toml` / `Cargo.toml`，无 `package.json` / `tauri.conf.json` | 无前端构建，无 `src-tauri/`，无 `e2e/` |
| **全栈项目** | 同时有 `package.json` + `src-tauri/Cargo.toml` + `tauri.conf.json` | 有前端 + 后端 + Tauri，有 `e2e/` / `docs/verifications/tauri/` |
| **后端项目** | 只有 `src-tauri/Cargo.toml` 或 `pyproject.toml`，无前端 `package.json` | 无前端构建，可能有 `docs/api-endpoints/` / `docs/domain-models/` |
| **纯前端项目** | 只有 `package.json`，无后端配置 | 无 `src-tauri/`，可能有 `docs/prototypes/` |

### 判定命令

```bash
ls pyproject.toml Cargo.toml package.json tauri.conf.json 2>/dev/null
```

---

## 诊断报告格式

子代理必须输出 Markdown 报告，结构如下：

```markdown
# Project Health Report ({YYYY-MM-DD})

## 项目类型判定
- CLI / 全栈 / 后端 / 纯前端

## 4 维度检查结果表

| 维度 | 状态 | 证据 |
|------|:---:|------|
| 1. 路径一致性 | ✅/⚠️/❌ | ls 输出 |
| 2. 目录树完整性 | ✅/⚠️/❌ | ls 输出 |
| 3. 版本残留+污染 | ✅/⚠️/❌ | grep 输出 |
| 4. 文档同步机制 | ✅/⚠️/❌ | find + wc 输出 |

## 不符合项清单
| 维度 | 文件/行号 | 问题 | 改前→改后建议 | 优先级 |
|------|----------|------|---------------|:---:|
| ... | ... | ... | ... | P0/P1/P2 |

## 迁移优先级建议
- P0: 立即修复
- P1: 近期修复
- P2: 可延后
```

---

## 产物路径

- Markdown: `docs/reports/project-health-{YYYY-MM-DD}.md`
- JSON: `docs/reports/project-health-{YYYY-MM-DD}.json`

---

**Created**: 2026-08-07
**Source**: V10.9 agents/project-health-auditor.md
**Purpose**: 外置 4 维度检查详情，让 agent 文件瘦身