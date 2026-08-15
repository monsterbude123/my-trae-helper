# 4 维度检查（Four-Dimension Check）

> Stage 7 Project Health Step 2 必走。V10 project-health-checklist.md 蒸馏。

---

## 维度 1：路径一致性

```yaml
checks:
  - docs/specs/INDEX.md 路径 vs 实际文件        # V11 §1 project-structure.md L29 (单源 INDEX)
  - docs/specs/changes/{id}/contracts/api-contracts.md 路径 vs 代码   # V11 §1 L41
  - docs/modules/{module}.md 路径 vs 模块        # V11 §1 L49-50
  - docs/specs/INDEX.md 引用 vs 实际             # V11 §1 (无 ARCHITECTURE.md 强制,V11 路径基准)
```

**工具**: `ls + grep` 路径正则。

## 维度 2：目录树

```yaml
checks:
  - 与 docs/specs/INDEX.md 目录树一致           # V11 §1 project-structure.md L29 (无 ARCHITECTURE.md)
  - 与 docs/specs/INDEX.md 目录树一致            # 同上,V11 单源
  - 模块边界无循环依赖
```

**工具**: `tree + diff docs/specs/INDEX.md`(V11 §1 单源 INDEX)。

## 维度 3：版本残留

```yaml
checks:
  - .bak / .old / .tmp / .orig 文件
  - 调试 console.log / debugger
  - TODO / FIXME / XXX
  - 注释代码（# deleted / // removed）
```

**工具**: `ripgrep + 排除 .git`。

## 维度 4：文档同步

```yaml
checks:
  - docs/specs/INDEX.md ↔ docs/modules/{module}.md ↔ 模块文档  # V11 §1
  - docs/specs/changes/{id}/contracts/api-contracts.md ↔ tests/contracts/   # V11 §1
  - CHANGELOG.md 最新条目
```

**工具**: `git log --diff-filter=M docs/`。

## 项目类型判定（Step 1）

| 类型 | 特征 |
|------|------|
| **Web** | package.json + vite/next/react |
| **Tauri** | src-tauri/ + tauri.conf.json |
| **CLI** | bin/ 或 main.rs/entry.py |
| **Library** | lib.rs / __init__.py |
| **Backend** | 后端框架（FastAPI/Express）|

## 关联引用

- [SKILL.md](../SKILL.md)
- [anti-distortion.md](anti-distortion.md)
- V10 来源: agents/project-health-auditor.md（已蒸馏）