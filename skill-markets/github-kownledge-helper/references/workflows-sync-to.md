# 工作流：SYNC-TO — 镜像到指定路径

> 核心：**把 `repos/<owner>__<repo>` 干净地复制到任意绝对路径**，不改任何文件、不写 manifest、不触发 doc 索引。
> 反模式：复制时顺手改文件 / 同时写 manifest / 把目标路径当 docs/ 索引。
>
> 单文件 ≤ 200 行；从 [workflows.md](./workflows.md) §9 拆出，避免主工作流文档超 200 行。

## 触发场景

- 用户说「把 X 同步到 D:\some\where」
- 用户后续通过本 skill 触发 `同步 <owner/repo> 到 <绝对路径>`

## 协议（5 步强制）

```
Step 1 — 解析仓库标识
  ├─ 接受 owner/repo 或 owner__repo
  ├─ 校验 manifest 中存在（按 full_name）
  └─ 目标源：repos/<owner>__<repo>  或  repos/<group>/<owner>__<repo>

Step 2 — 校验源 + 目标
  ├─ 源目录存在 + 含 .git（git clone 落地物）
  ├─ 目标路径 = 用户给的绝对路径（如 D:\xxx）
  └─ 目标已存在 → 报错停手（绝覆盖）

Step 3 — 复制（含 .git）
  ├─ 因 git 无原生本地 fork 命令 → 直接复制 .git 目录
  ├─ 复制策略：robocopy / MIR（带 .git + 排除 .git/objects/pack）
  └─ 复制后：git fsverify 在目标目录跑一次（确认 .git 可用）

Step 4 — 不写 manifest，不触发索引
  └─ 这是「镜像」不是「收录」。

Step 5 — 回执
  └─ 报告：源 / 目标 / 大小 / commit short
```

## 关键决策（已与用户确认）

| 决策点 | 选择 | 原因 |
|--------|------|------|
| git 是否支持本地 fork | ❌ 无 `fork` 子命令 | 见 [pitfalls.md §011](./pitfalls.md#011-git-没有本地-fork-概念fork-一个本地路径靠直接复制-git) |
| 复制 .git | ✅ 直接复制 .git 目录 | git 无原生本地 fork |
| 目标路径形式 | ✅ 绝对路径（`D:\xxx`） | 与用户视角对齐 |
| 目标已存在 | ✅ 报错停手 | 避免覆盖用户数据 |
| 写 manifest | ❌ 不写 | 镜像 ≠ 收录 |
| 触发 doc-map-manager 索引 | ❌ 不触发 | 同上 |

## 命名规范

- 触发语：`同步 <owner/repo> 到 <绝对路径>`
- 例：`同步 QwenLM/Qwen-MM-Plugins 到 D:\ref\qwen-mm-plugins`
- skill 内部命令：`pnpm ghh sync-to <owner/repo> <绝对路径>`（**已实现**，2026-08-13）
  - 实现：[sync-to.ts](../../../../src-cli/src/commands/sync-to.ts)
  - 测试：[syncTo.test.ts](../../../../src-cli/test/syncTo.test.ts)（6 例）
  - 跨平台：`fs.cpSync` recursive（无 robocopy 依赖，macOS/Linux 也能跑）

## 反例

- ❌ 复制时改文件 / 删 .gitignore / 重命名子目录
- ❌ 复制完成顺手写 manifest（污染事实源）
- ❌ 目标已存在直接覆盖（用户数据丢失）
- ❌ 把 .git 转成相对路径或符号链接（破坏可移植性）

## 验证

- [ ] 目标路径含完整 .git（`git -C <target> rev-parse HEAD` 返回相同 sha）？
- [ ] 目标路径下源码 byte-equal 于源（除 .git/objects/pack 内文件）？
- [ ] manifest.json 未变更？
- [ ] docs/.docmap 未重建？