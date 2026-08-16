# 项目路径约定(硬规则,优先级高于 SKILL.md)

> 沉淀自 project-rules.md §1。仓库追踪场景下"哪里放什么"的硬约定。
> 单文件 ≤ 200 行。
>
> **判定原则**:路径**模式**(`repos/<owner>__<repo>/` 双下划线分隔)是通用约定 → 沉淀;
> 具体路径前缀(如 `D:\workspace\xxx`)是项目专属配置 → 只作示例。

## 1. 路径约定表

| 用途 | 路径模式 | 说明 |
|------|---------|------|
| 仓库 clone 落地 | `<project_root>/repos/<owner>__<repo>/` | 双下划线分隔,避免同名冲突 |
| 文档镜像 | `<project_root>/docs/<owner>__<repo>/` | 与 repos 一一对应 |
| 仓库清单 | `<project_root>/manifest.json` | **唯一事实源** |
| Agent 指令 | `<project_root>/AGENT.md` | 项目根(本项目专属) |
| 项目规则 | `<project_root>/.trae/rules/project-rules.md` | 硬规则,优先级最高 |
| 知识索引缓存 | `<project_root>/docs/.docmap/` | doc-map-manager 产物,部分 gitignore |
| 维护脚本 | `<project_root>/scripts/` 或 `<project_root>/src-cli/` | 按需实现,仅保留可跑通的 |
| Skill 沉淀 | `<project_root>/.trae/skills/<name>/` | 项目专属 skill(本项目用 `.trae/skills/github-kownledge-helper/`) |

## 2. 命名规范

- **仓库目录**:`<owner>__<repo>`,全小写,owner/repo 原样保留(含连字符)
  - 例:`facebook__react`、`microsoft__vscode`、`torvalds__linux`
  - **双下划线**是因为不同 owner 下可能有同名 repo,单下划线会被解析成 owner 的一部分
- **manifest full_name**:必须是 `owner/repo` 格式(GitHub 标准,与目录命名不同)
- **文档文件名**:保留源仓库原命名(`README.md` / `CHANGELOG.md` / `ARCHITECTURE.md`),不重命名
- **聚合目录**(可选):`<project_root>/repos/<group>/<owner>__<repo>/`,用 `group` 字段标识

## 3. 硬约束(必避免)

```
MUST NOT:
  - 在项目根之外(具体由 load_env().get('project_root') 决定)写任何文件
  - 把第三方仓库内容提交到本项目的 git(repos/ 入 .gitignore)
  - 把 manifest.json 放到项目根之外
  - 把 docs/ 镜像放到项目根之外
```

## 4. 具体项目配置示例(可改)

| 项目 | project_root | 备注 |
|------|--------------|------|
| 本 skill 原项目 | `D:\workspace\github-kownledge-helper` | 通过 `GITHUB_KNOWLEDGE_HELPER_SPACE` env 指向 |
| 跨平台变体 | `~/projects/my-tracker` | macOS/Linux 路径 |

> 具体路径前缀是**示例**,复制本文件时按实际项目路径调整。`load_env().get('project_root')` 是推荐方式。

## 5. 与其他 references 关系

- `manifest-schema.md §4` → 具体项目配置示例(manifest 位置)
- `env-loadenv.md` → 怎么读 project_root(env 收口)
- `safety-cleanup.md §4` → repos/ 入 gitignore
- `workflows-baseline.md` → ADD 步骤 3 用 `<owner>__<repo>` 命名