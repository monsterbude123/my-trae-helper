# doc-map-manager 使用规范

> 本文件是仓库追踪场景下,使用 `doc-map-manager` skill 构建/查询 `docs/.docmap/docmap.db` 索引的标准模式。
> 适用于所有用 doc-map-manager 做知识索引的项目。
> 单文件 ≤ 200 行。

## 1. 5 种查询模式(P0 首选)

```bash
# 抓取(语义最强 — 给问题,语义最相关段落)
python "<doc-map-manager-skill>/scripts/query-index.py" --grab "问题"

# 查表(精准 — 关键词表查找)
python "<doc-map-manager-skill>/scripts/query-index.py" --lookup "关键词"

# 模糊(描述性查询)
python "<doc-map-manager-skill>/scripts/query-index.py" --fuzzy "描述性短语"

# 语义向量(需配置 embedding)
python "<doc-map-manager-skill>/scripts/query-index.py" --semantic "自然语言"

# 上下文模式 / 影响分析(给定文件)
python "<doc-map-manager-skill>/scripts/query-index.py" --context-mode <file>
python "<doc-map-manager-skill>/scripts/query-index.py" --impact <file>
```

> `<doc-map-manager-skill>` 默认 `~/.trae-cn/skills/doc-map-manager`,本 skill 推荐通过 `load_env().get('doc_map_scripts')` 取得,**禁止**业务代码硬编码。

## 2. 索引构建

```bash
# 增量(默认,基于 mtime+size)
python "<doc-map-manager-skill>/scripts/build-index.py" --incremental

# 全量(首次 / schema 变更)
python "<doc-map-manager-skill>/scripts/build-index.py"

# 检测变化(基于 git diff,适用于已 git 跟踪的目录)
python "<doc-map-manager-skill>/scripts/build-index.py" --detect-changes
```

## 3. 新鲜度协议(强制)

```
🟢 ≥0.7  → 可直引
🟡 0.3~0.7 → 标注"可能过时",涉及代码实现必须 git show / git grep 验证
🔴 <0.3  → 必须交叉验证,文档与代码冲突时以代码为准并报告不一致
```

**强约束**:引用任何文档前**必须**检查新鲜度,违反 = 经验沉降到 pitfalls §001-§010。

## 4. 索引范围

| 目录 | 是否入索引 | 原因 |
|------|-----------|------|
| `docs/<owner>__<repo>/` | **入** | 知识库主体(README/CHANGELOG/ARCHITECTURE/CONTRIBUTING 等) |
| `repos/<owner>__<repo>/` | **不入** | 源码走 git 命令查,索引会爆 |
| `docs/.docmap/` | **不入**(自排除) | 索引产物本身,索引自己会无限递归 |
| `references/` | **不入**(默认 exclude) | 临时备份/调试目录 |

`docs/.docmap/config.json` 的 `exclude_dirs` 默认排除 `references`、临时备份目录。

## 5. 禁止行为

- ❌ **直接 Read** `docs/.docmap/docmap.db`(SQLite 二进制,必须走 query-index.py)
- ❌ **每次全量重建**(除非首次或 schema 变更)— 浪费 + 索引产物污染 git
- ❌ **在 docs/.docmap/ 写业务文件**(索引产物目录,不是工作区)
- ❌ **索引源码**(`repos/`)— 索引会爆炸,源码查询走 git

## 6. 与 workflows-baseline.md 关系

- `workflows-baseline.md §1 ADD 步骤 8` → 触发增量索引
- `workflows-baseline.md §3 UPDATE-ALL 步骤 4` → 一次性增量索引
- `workflows-baseline.md §4 QUERY 决策树` → 用 grab/lookup/fuzzy
- `doc-verify.md` → 验证索引状态(不在 capture)