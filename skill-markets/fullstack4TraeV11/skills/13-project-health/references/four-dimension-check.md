# 4 维度检查（Four-Dimension Check）

> Stage 7 Project Health Step 2 必走。V10 project-health-checklist.md 蒸馏。

---

## 维度 1：路径一致性

```yaml
checks:
  - docs/INDEX.md 路径 vs 实际文件
  - docs/api-endpoints/ 路径 vs 代码
  - docs/modules/ 路径 vs 模块
  - ARCHITECTURE.md 引用 vs 实际
```

**工具**: `ls + grep` 路径正则。

## 维度 2：目录树

```yaml
checks:
  - 与 ARCHITECTURE.md 目录树一致
  - 与 INDEX.md 目录树一致
  - 模块边界无循环依赖
```

**工具**: `tree + diff` ARCHITECTURE.md。

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
  - INDEX.md ↔ ARCHITECTURE.md ↔ 模块文档
  - API-REFERENCE ↔ contracts/
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