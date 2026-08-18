# V11 项目根 .gitignore 推荐模板(V11.8.7 NEW — case 2 蒸馏 fix _invalidated 入 commit)

> **来源**:case 2 (desktop-pet-v11) audit-fix — `spec-purge.py` 中转层 `docs/specs/_invalidated/{ts}-{id}/` 入了 commit,违反 V11 协议 — VCS 临时层应在 archive 完成前自动清空,不参与版本控制。
>
> **本节附在 AGENTS.md 末尾,与 `.gitignore` 文件的内容不重复(后者是实际 gitignore 模式,本文件是协议说明)。

## 必含 .gitignore 模式

```gitignore
# V11 spec-purge 中转层(V11.8.7 NEW — 临时层不入 commit)
docs/specs/_invalidated/**

# V11 V12 临时层(project-rule-skill 注入层,本地缓存)
.trae/skills/_cache/**

# GitNexus 索引本地缓存(重新 analyze 时可重建)
.gitnexus/cache/**

# 启动截图(本地调试,可选择性提交)
logs/screenshot-*.png
```

## 反例(违反任一 = REJECT)

| 反例 | 后果 |
|------|------|
| `docs/specs/_invalidated/` 入 commit | 中转层永久化,污染 history |
| `.trae/skills/_cache/` 入 commit | 缓存私有配置泄露 |
| `.gitnexus/cache/` 入 commit | 索引污染跨机器 |
| **反模式**:把所有 `docs/` 入 gitignore | 真实归档也进不了 commit,违反 Article VIII 不可变要求 |

## 自验收

```bash
# _invalidated 不应被 git 跟踪
git check-ignore docs/specs/_invalidated/test-dir/foo.md
# → 期望 hit
