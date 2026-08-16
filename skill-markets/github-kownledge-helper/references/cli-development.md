# 缺失-CLI 走开发的工作流（2026-08-13 新增）

> 核心：**用户给任务 → 查 CLI → 缺失 → 走 TDD 开发 CLI → 再完成任务**。
> 反模式：发现 CLI 不支持就**手动拼凑命令**（裸 git + Edit manifest + 调 python）完成任务。结果下次同类任务又得手搓一遍，命令无法复用，错误也无法兜底。
> 关联：[tdd.md](./tdd.md)（TDD 模板） / [doc-verify.md](./doc-verify.md)（doc manager 验证流程）。

## 触发场景

- 用户说「加个仓库 facebook/react」→ `add` 不存在
- 用户说「验证下 doc manager」→ `verify-docs` 不存在
- 用户说「查 freshness」→ `query` 不存在
- 任何用户给定的指令，CLI 现有子命令覆盖不了

## 协议（5 步强制）

```
Step 1 — 探查现有 CLI
  ├─ pnpm ghh --help / 看 src-cli/bin/cli.ts
  └─ 找到匹配的子命令？
      ├─ 是 → 直接用现有命令完成任务
      └─ 否 → 进入 Step 2

Step 2 — 写测试（红）
  ├─ 在 src-cli/test/<command>.test.ts 或 <command>.e2e.test.ts 写测试
  ├─ 覆盖：正常路径 / 边界 / 错误路径
  └─ pnpm test 看到红（实现文件不存在 / 函数未实现）

Step 3 — 写实现（绿）
  ├─ 在 src-cli/src/commands/<command>.ts 实现
  ├─ 复用现有 lib（git.ts / manifest.ts / paths.ts / time.ts）
  └─ pnpm test 看到绿

Step 4 — 注册到 cli.ts
  ├─ import + program.command(...)
  ├─ pnpm typecheck 0 错
  └─ pnpm ghh <command> 真命令验证

Step 5 — 用新 CLI 重做用户任务
  ├─ 把"先做的工作"回滚（如果手动操作已污染状态）
  └─ 跑新 CLI 完成用户原始任务
```

## 反模式

- ❌ 看到 CLI 没有就「先用 git clone + Edit manifest 凑合」 — 下次又得手搓
- ❌ 跳过测试直接写 .ts — 违反 TDD
- ❌ 实现完不写测试 — 「已跑通」不算交付
- ❌ 注册到 cli.ts 后没跑 `pnpm ghh <command>` 真命令验证 — 编译过 ≠ 跑通
- ❌ 完成用户任务前没回滚手动操作 — 留下脏状态

## 验证

- [ ] 是否有「先红后绿」的 TDD 证据（git log 或 commit message）？
- [ ] `pnpm test` 全绿？
- [ ] `pnpm typecheck` 0 错？
- [ ] `pnpm ghh <command>` 真命令跑通？
- [ ] 用户原始任务是用新 CLI 完成的（不是手动）？

## 已有命令清单（持续维护）

| 任务 | CLI 命令 |
|------|---------|
| 收录新仓库 | `pnpm ghh add <owner/repo 或 https URL>` |
| 同步文档 | `pnpm ghh sync-docs` |
| 重建 manifest | `pnpm ghh sync-manifest` |
| 更新单仓 | `pnpm ghh update <full_name>` |
| 一键全更新 | `pnpm ghh update-all` |
| 验证 doc manager | `pnpm ghh verify-docs` |
| 跑测试 | `pnpm test` |
| 类型检查 | `pnpm typecheck` |

> 缺失的命令 → 触发本协议，不要手动拼凑。
