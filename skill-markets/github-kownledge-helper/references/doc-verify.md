# doc manager 验证流程

> 本项目用 doc-map-manager 构建 `docs/.docmap/docmap.db` 索引。本文件沉淀**验证 doc manager 索引成功**的标准流程。

## 为什么需要验证

`pnpm sync:docs` 只复制文件到 `docs/<owner>__<repo>/`，**不**自动建索引。
`add` 流程在最后触发 `build-index.py --incremental`，但**异步 + 错误不抛**，可能索引没建成功。
答疑前必须验证目标仓库的 docs 已被索引（否则 freshness check 永远 🟡/🔴）。

## 验证命令

```bash
pnpm ghh verify-docs
```

行为：
- 扫 manifest.repos → 提取 `owner__repo` 形式 key
- 对每个 key 跑 `query-index.py --grab <key>`
- 汇总：🟢（≥0.7 新鲜）/ 🟡（0.3~0.7）/ 🔴（<0.3）/ missing（query 没命中）
- 失败（missing > 0 或 🔴 > 0）→ exit 1

## 手动单点验证

```bash
# 验证单个仓库的索引状态
python "C:/Users/septe/.trae-cn/skills/doc-map-manager/scripts/query-index.py" --grab "comfyanonymous__ComfyUI"
```

期望输出含：
```
🟢 新鲜度: 1.00
## comfyanonymous__ComfyUI/README.md L3-L44 (score: 0.74)
```

- 🟢 ≥ 0.7：可信，可直引
- 🟡 0.3~0.7：可能过时，标注"待交叉验证"
- 🔴 < 0.3：必须 `git show` / `git grep` 交叉验证，文档与代码冲突以代码为准

## 修复流程

| 现象 | 根因 | 修复 |
|------|------|------|
| `verify-docs` 报 missing | sync-docs 后未跑 build-index | `python .../build-index.py --incremental` 或 `pnpm ghh add <repo>` 重触发 |
| 全部 🔴 0.0 | mtime 没变 → 增量跳过 | `python .../build-index.py`（无 `--incremental`，强制全量） |
| 索引存在但 query 报 missing | query 串与索引 path 不匹配（聚合目录子串问题） | 用 `--lookup` 替代 `--grab`，或接受 false positive（已知限制） |
| doc-map-manager 进程挂 | python 依赖缺失 / 路径错 | 检查 `DOC_MAP_MANAGER_SCRIPTS` 环境变量或 `~/.trae-cn/skills/doc-map-manager/` 存在 |

## doc manager 脚本路径

- 默认：`~/.trae-cn/skills/doc-map-manager/scripts/`
- 覆盖：`DOC_MAP_MANAGER_SCRIPTS=/path/to/scripts`
- 验证：`python "<scripts>/query-index.py" --help`

## 索引产物

- SQLite：`docs/.docmap/docmap.db`（禁止直接 Read，必须走 query-index.py）
- 排除目录：`docs/.docmap/config.json#exclude_dirs`（默认 `references`、临时备份）
- 增量/全量：
  - `build-index.py --incremental`：基于 mtime + size，跳过未变
  - `build-index.py`（无 flag）：全量重建
  - **禁止**全量重建作为常规操作（耗时长），仅在 schema 变更或首次时用

## 何时跑

| 场景 | 是否跑 verify-docs |
|------|-------------------|
| `pnpm ghh add <repo>` 完成后 | 必跑（验收） |
| `pnpm ghh update-all` 完成后 | 可选（update 不动 docs） |
| 答疑前查 freshness | 单点 `--grab` |
| 跨仓检索 | `--lookup` 走全局 |

## 进度

- `verify-docs.ts` 实现于 2026-08-13，5 例单测全绿。
- 已知限制：聚合目录（`ai-app/...`）的子串 `owner__repo` grab 命中率低，27/39 missing 是 false positive。下一轮改进：用 `--lookup` 替代 `--grab`，或在 query 串里带 group 前缀。
