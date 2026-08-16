# manifest.json Schema + 维护规则

> 本文件是仓库追踪场景下「清单文件」的标准规范。沉淀自 AGENT.md §3 + project-rules §3。
> 单文件 ≤ 200 行。

## 1. Schema(v1.0)

```json
{
  "version": "1.0",
  "updated_at": "2026-08-13T10:00:00+08:00",
  "repos": [
    {
      "name": "react",
      "owner": "facebook",
      "full_name": "facebook/react",
      "url": "https://github.com/facebook/react.git",
      "path": "repos/facebook__react",
      "docs_path": "docs/facebook__react",
      "default_branch": "main",
      "added_at": "2026-08-13T10:00:00+08:00",
      "last_pull_at": "2026-08-13T10:00:00+08:00",
      "current_commit": "full-40-char-sha",
      "current_commit_short": "abc1234",
      "current_commit_date": "2026-08-13T09:00:00+00:00",
      "tags": ["frontend", "library"],
      "notes": ""
    }
  ]
}
```

## 2. 必填字段(11 个,缺一即视为脏数据)

| 字段 | 含义 | 校验 |
|------|------|------|
| `name` | repo 名(不含 owner) | 必填 |
| `owner` | 拥有者/组织 | 必填 |
| `full_name` | `owner/name` 格式(GitHub 标准) | 必填,**唯一索引(去重键)** |
| `url` | clone URL | 必填 |
| `path` | 本地仓库路径(`repos/<owner>__<repo>`) | 必填 |
| `default_branch` | 默认分支 | 必填 |
| `added_at` | 加入时间 | 必填,ISO 8601 |
| `last_pull_at` | 最近一次 pull 时间 | 必填,ISO 8601 |
| `current_commit` | HEAD commit 完整 sha(40 字符) | 必填 |
| `current_commit_short` | HEAD commit 短 sha(7 字符) | 必填 |
| `current_commit_date` | HEAD commit 时间 | 必填,ISO 8601 |

可选字段:`tags` / `notes` / `docs_path` / `group`(聚合目录场景)。

## 3. 维护铁律

1. **唯一事实源**:仓库状态以 manifest.json 为准;与本地 git 冲突时以 git 实测为准并**回写修正**
2. **原子写入**:读 → 改 → 写回,禁止半写状态。写前备份到 `manifest.json.bak`,写成功后**立即删除备份**
3. **时间戳**:ISO 8601 带时区,统一 `Asia/Shanghai`(`+08:00`),不依赖本地时区
4. **去重**:按 `full_name` 唯一索引,禁止重复收录
5. **删除**:用户要求移除仓库时,先删 `repos/<path>` 与 `docs/<path>`,再从 manifest 移除条目
6. **必填校验**:读 manifest 后立即校验 11 必填字段,缺一即报告"脏数据"并修复

## 4. 具体项目配置示例(可改)

| 项目 | manifest.json 位置 | 备注 |
|------|-------------------|------|
| 默认实现(本 skill 原项目)| 项目根 `manifest.json` | `load_env.ts` 用 `GITHUB_KNOWLEDGE_HELPER_SPACE` env 指向项目根 |
| 示例变体 1 | `<root>/tracker/manifest.json` | 子目录放清单,manifest `path` 改相对 `tracker/` |
| 示例变体 2 | 数据库 / SQLite | 大规模场景(>1000 仓),仍可保留 manifest.json 作 snapshot |

> **判定原则**:通用约定(去重 / 原子写 / 必填 / 时区)**沉淀到本文件**;具体项目路径或 env 名是**示例**,可改。

## 5. 与其他 references 关系

- `workflows-baseline.md §1 ADD 步骤 7` → 回写 manifest
- `workflows-baseline.md §2 UPDATE 步骤 5` → 比对 current_commit
- `git-workflow-rules.md §3` → 顺序执行保护 manifest 不被并发污染