# 知识索引规则(硬约束)

> 沉淀自 project-rules.md §5。仓库追踪场景下"doc-map-manager 索引"的 6 条铁律。
> 单文件 ≤ 200 行。

## 1. 6 条铁律

| # | 规则 | 反例 |
|---|------|------|
| 1 | **索引目标**:仅 `docs/` 目录,`repos/` 不入索引 | 索引源码导致 docmap.db 爆炸 |
| 2 | **文档同步**:收录/更新仓库时,同步 README / CHANGELOG / ARCHITECTURE / CONTRIBUTING 等顶层文档 | 仅 sync-docs 不索引,导致 freshness 永远 🟡 |
| 3 | **增量优先**:`build-index.py --incremental`,禁止每次全量重建(除首次 / schema 变更) | 全量重建浪费时间 + 索引产物污染 |
| 4 | **查询入口**:必须走 `query-index.py`,禁止直接 Read `docs/.docmap/docmap.db` | 直读 SQLite 二进制破坏索引 |
| 5 | **新鲜度协议**:引用文档前强制检查 🟢/🟡/🔴,涉及代码实现必须用 `git show` / `git grep` 交叉验证 | 引用过期文档导致错误结论 |
| 6 | **exclude_dirs**:`docs/.docmap/config.json` 默认排除 `references`、临时备份目录 | 索引递归自吃 |

## 2. 文档同步策略(收录时)

| 文档类型 | 必同步 | 选同步 | 不同步 |
|---------|-------|-------|-------|
| README.md | ✅ | | |
| CHANGELOG.md | ✅ | | |
| ARCHITECTURE.md | | ✅(若有) | |
| CONTRIBUTING.md | | ✅ | |
| LICENSE | | | ❌(占空间无信息) |
| 源码文件 | | | ❌(`repos/` 已 git) |
| 子包 docs | | | ❌(monorepo 不递归,见 [workflows.md §1](./workflows.md)) |

## 3. 索引命令模式

```bash
# 增量(默认,基于 mtime+size)
python "<doc-map-manager-skill>/scripts/build-index.py" --incremental

# 全量(仅首次 / schema 变更)
python "<doc-map-manager-skill>/scripts/build-index.py"

# 检测变化(基于 git diff,适用已 git 跟踪目录)
python "<doc-map-manager-skill>/scripts/build-index.py" --detect-changes
```

> **mtime 坑**:`cp` / `Copy-Item` 默认保留原 mtime,`--incremental` 会跳过所有"未变"文件。详见 pitfalls §005。

## 4. 查询入口铁律

```
MUST:  python "<skill>/scripts/query-index.py" --grab "问题"
MUST NOT:  Read <root>/docs/.docmap/docmap.db
```

**原因**:
- docmap.db 是 SQLite 二进制,直接 Read 输出乱码
- 直读绕过 freshness 协议(协议在 query-index.py 内实现)
- 直读绕过权限控制(SQLite 文件可能含敏感元数据)

## 5. 新鲜度协议

```
引用前必须 query-index.py 看返回的 freshness 字段:
  🟢 ≥0.7  → 可直引(结论性表述)
  🟡 0.3~0.7 → 标注「可能过时」,涉及代码必须 git show / git grep 验证
  🔴 <0.3  → 必须交叉验证,文档与代码冲突时以代码为准并报告不一致

详见 [doc-map-manager-usage.md §3](./doc-map-manager-usage.md)
```

## 6. exclude_dirs 默认值

`docs/.docmap/config.json`:

```json
{
  "exclude_dirs": [
    "references",         // 临时备份/调试
    "*.bak",              // 备份文件
    ".tmp*"               // 临时目录
  ]
}
```

## 7. 反模式

- ❌ 索引 `repos/`(源码)— docmap.db 会爆炸
- ❌ 每次 UPDATE-ALL 后跑全量(浪费时间)
- ❌ 直读 `docs/.docmap/docmap.db`
- ❌ 跳过新鲜度检查直接引用过期文档
- ❌ 索引递归自吃(不设 exclude_dirs,索引自己会无限递归)

## 8. 与其他 references 关系

- `doc-map-manager-usage.md` → 详细查询/构建命令
- `doc-verify.md` → 验证索引状态(独立 CLI `verify-docs`)
- `workflows-baseline.md §1 ADD 步骤 8` → 触发增量索引
- `pitfalls §005` → mtime 增量索引跳过问题