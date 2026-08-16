# 可复用命令模式

> 沉淀 ADD / UPDATE / QUERY 工作流中验证过的 git 命令组合。
> 单文件 ≤ 200 行，超出拆分到 `commands-<topic>.md`。

## 状态读取（一次拉全）

收录 / 更新后回写 manifest 必读的字段，合并成一条命令：

```powershell
# 一次性读取 branch / full sha / short sha / commit date
$repo = "repos/facebook__react"
git -C $repo rev-parse --abbrev-ref HEAD
git -C $repo rev-parse HEAD
git -C $repo rev-parse --short HEAD
git -C $repo log -1 --format=%cI HEAD
```

## 完整克隆（默认策略）

```powershell
# 默认完整克隆（拉全历史，便于 blame / tag / 历史查询）
git clone https://github.com/facebook/react.git repos/facebook__react

# 网络受限场景降级为浅克隆
git clone --depth 1 https://github.com/facebook/react.git repos/facebook__react
```

## ff-only 更新（避免意外 merge commit）

```powershell
git -C repos/facebook__react fetch origin
git -C repos/facebook__react pull --ff-only
# 非快进 → 报告，询问是否 reset --hard origin/<branch>，不强推
```

## 按 tag 查 commit

```powershell
# 列出匹配 tag
git -C repos/facebook__react tag --list "v19*"

# tag → commit sha
git -C repos/facebook__react rev-list -n 1 v19.0.0
```

## 最近 N 个 commit 摘要

```powershell
git -C repos/facebook__react log --oneline -20
```

## PR / merge commit 改动文件

```powershell
# 查看某个 merge commit 改了哪些文件
git -C repos/facebook__react show --stat <merge-sha>

# 列出最近的 merge
git -C repos/facebook__react log --merges --oneline -10
```

## 跨仓库源码搜索

```powershell
# 在本地仓库源码中 grep（docs 索引未命中时降级用）
git -C repos/facebook__react grep -n "useEffect" -- "*.md"
```

## TS CLI 命令（pnpm）

```powershell
# 安装依赖
pnpm install

# 收录新仓库（完整 clone + 同步 docs + doc manager 索引）
pnpm ghh add <owner/repo>          # e.g. pnpm ghh add facebook/react
pnpm ghh add <https URL>           # 接受 https URL，自动推 owner/repo
pnpm ghh add <owner/repo> --group ai-app  # 聚合目录

# 验证 doc manager 索引（每仓 query 一次，汇总 🟢/🟡/🔴/missing）
pnpm ghh verify-docs

# 同步文档（按 manifest 把白名单文档复制到 docs/）
pnpm ghh sync-docs

# 同步 manifest（扫描 repos/ 重建 manifest.json，会重置 added_at/last_pull_at）
pnpm ghh sync-manifest

# 更新单个仓库（full_name / path / name 均可匹配）
pnpm ghh update bytedance/deer-flow

# 一键全量更新（ff-only，顺序拉取，失败隔离）
pnpm ghh update-all

# 通用入口
pnpm ghh <command>

# 跑测试（TDD）
pnpm test                # 一次性
pnpm test:watch          # watch 模式

# 类型检查
pnpm typecheck
```

> 任何用户给的任务，先查这个清单。**缺失的命令不要手动拼凑** — 走 [workflows.md §9 缺失-CLI 开发协议](./workflows.md#9-缺失-cli-走开发的工作流2026-08-13-新增)。

## 镜像到指定路径（sync-to，已实现 CLI，跨平台）

```bash
# 跨平台（Windows / macOS / Linux）
pnpm ghh sync-to <owner/repo> <绝对路径>

# 例：把 QwenLM/Qwen-MM-Plugins 镜像到 D:\ref\qwen-mm-plugins
pnpm ghh sync-to QwenLM/Qwen-MM-Plugins D:\ref\qwen-mm-plugins
```

> 实现：`src-cli/src/commands/sync-to.ts`（fs.cpSync recursive + 含隐藏 .git），跨平台无 robocopy 依赖。
> 完整协议见 [workflows-sync-to.md](./workflows-sync-to.md) + [pitfalls.md §011](./pitfalls.md#011-git-没有本地-fork-概念fork-一个本地路径靠直接复制-git)。
> 测试：6 例（src-cli/test/syncTo.test.ts），含目标已存在停手 / 源不存在 / 源无 .git / 子目录 + 文件树一致 / sha 校验。

## 批量重命名（PowerShell 一次性）

把 `dir` 列表映射到 `<owner>__<repo>` 新名：

```powershell
$map = @(
  @{dir="deer-flow"; new="bytedance__deer-flow"},
  @{dir="free-claude-code"; new="Alishahryar1__free-claude-code"}
  # ...
)
foreach ($m in $map) {
  $old = "d:\workspace\github-kownledge-helper\repos\$($m.dir)"
  if (Test-Path $old) { Rename-Item $old $($m.new) }
}
```

> ⚠️ PowerShell 字符串插值 `$m.new` 显示为 `System.Collections.Hashtable.new`（仅显示问题，实际是 hashtable 字段值）。用 `$($m.new)` 强制表达式插值，或用 `Get-ChildItem` 二次确认操作结果。详见 pitfalls §003。
