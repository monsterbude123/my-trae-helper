# 踩坑记录

> 沉淀实战中遇到的坑与解法。每条格式：现象 / 根因 / 解法 / 预防。
> 单文件 ≤ 200 行，超出拆分到 `pitfalls-<topic>.md`。

> 当前为骨架，随实战积累追加。

## 模板

### [编号] 标题

- **日期**：YYYY-MM-DD
- **现象**：观察到的错误 / 异常行为
- **根因**：根本原因（可复述）
- **解法**：实际生效的处理
- **预防**：下次如何避免

---

<!-- 实战记录从下方开始追加 -->

### [001] LS 不显示隐藏 .git 目录，聚合内子项目被误判为非 git

- **日期**：2026-08-13
- **现象**：用 LS 扫描 `repos/ai-skills-sets/`，看到 18+ 子目录，认为是"本地资源聚合"。但 `git -C dir config --get remote.origin.url` 测试时发现全是真 git 仓库。
- **根因**：LS 工具默认不输出 `.git` 这类隐藏目录（`Get-ChildItem` 不带 `-Force` 也一样）。子目录本身存在但 `.git` 是隐藏的。
- **解法**：
  ```powershell
  Get-ChildItem -Path "repos" -Directory -Recurse -Force |
    Where-Object { Test-Path (Join-Path $_.FullName ".git") }
  ```
  递归 + Force 扫描 + 直接测试 `.git` 存在。
- **预防**：扫描未知目录结构时，永远用 `-Recurse -Force` + `Test-Path .git` 探测，不用 LS 默认行为。

### [002] pnpm v11 因 esbuild build script 未 approve 永远 exit 1

- **日期**：2026-08-13
- **现象**：`pnpm sync:manifest` 永远 exit 1，提示 `Ignored build scripts: esbuild@0.28.2`。即使 `pnpm install` 成功，下一次 script 跑又失败。
- **根因**：pnpm v11 默认禁止 native dependency 的 postinstall 脚本（安全策略）。每次 `pnpm` 跑命令都先 `runDepsStatusCheck` → 触发 install → 因 build script 未 approve 而 exit 1。
- **解法**：在 `pnpm-workspace.yaml` 显式 allow（不是 `package.json#pnpm`）：
  ```yaml
  packages: []
  allowBuilds:
    esbuild: true
  verifyDepsBeforeRun: false
  ```
  `allowBuilds.<pkg>: true` 才是 v11 approve 机制（v10 用的 `onlyBuiltDependencies` 已被 v11 改名为 `allowBuilds`）。
- **预防**：使用 pnpm v11+ 时，配置文件一律放 `pnpm-workspace.yaml` 而非 `package.json#pnpm`（后者已废弃）。任何含 native dep 的项目（esbuild / node-sass / sharp 等）首次 install 后必须配置 allowBuilds。

### [003] PowerShell 字符串插值显示 `System.Collections.Hashtable.new`

- **日期**：2026-08-13
- **现象**：在 `foreach ($m in $map) { "OK | $old -> $m.new" }` 中输出，`$m.new` 显示为 `System.Collections.Hashtable.new`。
- **根因**：PowerShell 字符串插值 `$obj.prop` 在某些上下文下会把 `$obj` 当作变量名解析为 `$m`（hashtable 本身）然后加字面量 `.new`。
- **解法**：用 `$($m.new)` 强制表达式插值，或用子表达式 `${m}.new`。
- **预防**：字符串内引用对象属性时永远用 `$($obj.prop)`，避免歧义。这是显示问题不是数据问题，操作仍正确（用 `Get-ChildItem` 二次确认即可）。

### [004] 拉取遇 ff-only 失败：本地分叉

- **日期**：2026-08-13
- **现象**：`pnpm ghh update-all` 中 `anymouschina/TapCanvas` 报 `fatal: Not possible to fast-forward, aborting.`。
- **根因**：本地 HEAD 领先 origin/main（可能本地有未推 commit，或 origin main 已被 reset/rebase 推到更前）。ff-only 策略不会自动 merge 或 rebase，强推更不允许。
- **解法**：用户决策——
  1. `git reset --hard origin/main` 追远程（推荐，项目用，仓库内无本地修改）
  2. 保留分叉，手动 rebase
  3. 重新 clone
- **预防**：update 流程设计时**绝不**自动 reset。报告 + 等用户决策。reset 完成后**必须**再跑一次 `update <repo>` 让 manifest 对齐（reset 直接改 HEAD，manifest 不知道）。

### [005] 增量索引 mtime 不更新，sync-docs 后 build-index --incremental 跳过所有文件

- **日期**：2026-08-13
- **现象**：跑 `pnpm sync:docs` 重新覆盖了 121 个文档（多数是 `cp` 覆盖），但 `build-index.py --incremental` 报 `无变更文件，跳过`。
- **根因**：`cp` 覆盖保留原文件 mtime（特别是 GNU `cp` 不带 `--update` 时 Windows `Copy-Item` 也是）。`--incremental` 仅基于 mtime+size 判断。
- **解法**：
  1. 强制全量：`build-index.py`（无 `--incremental`）
  2. 用 `--detect-changes`（基于 git diff，对 `repos/` 适用，但 docs/ 镜像不在 git 里所以可能检测不到）
  3. 摸 `docs/` 文件 mtime 让其反映新内容（sync-docs 用 `cp -u` 或写时显式 `utimes`）
- **预防**：未来 sync-docs 实现可考虑 `fs.copyFileSync` 后用 `fs.utimesSync` 强制更新 mtime，让增量索引生效。或在 update-all 流程里直接强制全量索引。

### [006] pnpm 命令在子目录跑通，移到项目根后用户复现 [ERR_PNPM_NO_PKG_MANIFEST]

- **日期**：2026-08-13
- **现象**：开发时把 `package.json` / `pnpm-workspace.yaml` / `node_modules/` 放在 `scripts/` 子目录，从 `scripts/` 跑 pnpm 完全正常。但用户从项目根执行 `pnpm sync:docs` 报 `[ERR_PNPM_NO_PKG_MANIFEST] No package.json found`。
- **根因**：pnpm 命令必须在含 `package.json` 的目录执行（向上查找 workspace root）。子目录放包虽然开发方便，但用户视角的「主工作目录」是项目根。**我没在用户视角测试**，是设计盲点。
- **解法**：
  1. `package.json` / `pnpm-workspace.yaml` 必须放**项目根**
  2. TS 源码目录改名为 `src-cli/`（避免与 npm `scripts` 概念混淆）
  3. scripts 配置统一用相对路径 `tsx src-cli/bin/cli.ts ...`
  4. typecheck 单独 `-p src-cli/tsconfig.json`
- **预防**：交付 CLI 工具前，**必须在最终用户的工作目录**（项目根）实跑一次所有命令，而不是只在子目录验证。开发期方便 ≠ 用户期方便。

### [007] commander 12 async action 不 await 会提前退出

- **日期**：2026-08-13
- **现象**：`update.ts` 改 async 后，从 `tsx bin/cli.ts` 跑出来只剩 pnpm 自身的输出（`Already up to date`），没有任何 update 阶段日志。
- **根因**：`commander@12.1.0` 的 `program.parse()` **不 await async action**，parse 同步返回后 Node 事件循环空 → process 退出。
- **解法**：用 `await program.parseAsync(process.argv)` 替代 `program.parse()`。文件必须 ESM（`type: module`）且顶层 await 兼容（tsconfig module=NodeNext + target=ES2022）。
- **预防**：任何注册 async action 的 commander 入口都用 parseAsync。typecheck 时检查顶层是否 await。

### [008] tsx + ESM 顶层 await 必须配 NodeNext + ES2022

- **日期**：2026-08-13
- **现象**：把 `await program.parseAsync(argv)` 放顶层后，typecheck 报 `Module 'fs' not found` 或运行报 `Cannot use import statement outside a module`。
- **根因**：`tsx` 默认用 CJS 解析顶层 await 不兼容。需 `tsconfig.json`：
  ```json
  "module": "NodeNext",
  "moduleResolution": "NodeNext",
  "target": "ES2022"
  ```
  且 `package.json` 必须 `"type": "module"`。
- **解法**：`tsconfig.json` 三件套 + `package.json#type: module` + 文件用 `.mts` 或裸 `.ts` + ESM import 路径必须带 `.js` 后缀（即使源是 .ts）。
- **预防**：初始化 TS ESM 项目时，三件套一次配齐。导入路径一律 `.js` 习惯（即使 IDE 会自动加 `.ts` 也别依赖）。

### [009] fetch 进度条刷屏（每个仓库几十行 [remote: Counting objects: x%]）

- **日期**：2026-08-13
- **现象**：`git fetch --progress` 默认把 git 进度条当 stderr 推流，38 个仓 × 多行 = 用户屏被刷爆。
- **根因**：git 自身进度条（`remote: Enumerating objects: 12%`、`Receiving objects:`、`Resolving deltas:`）走 stderr，按行进来。
- **解法**：在 `gitStream` 的 onLine 回调里过滤：
  ```typescript
  function isProgressBar(line: string): boolean {
    return /^[\s]*[\w-]+:.*\d+\%/.test(line)      // remote: Enumerating: 12%
      || /^\s*Receiving objects:/.test(line)
      || /^\s*Resolving deltas:/.test(line);
  }
  ```
  进度条 `return`（静默），错误透出。
- **预防**：所有长过程 git 命令的流式回调，第一道关就是「isProgressBar 过滤」。

### [010] Edit 多文件替换可能残留旧代码（search/replace old_str 未覆盖全部匹配）

- **日期**：2026-08-13
- **现象**：本会话用 `SearchReplace` 多次「删除旧注释行」，每次都正常返回 "file changed"，但下一次 `Read` 时发现残留了两份重复行（第 81-82 行同时有「未来扩展占位（按需实现...）」+「未来扩展占位」）。
- **根因**：search/replace 的 `old_str` 只匹配一次。如果代码里已经存在同一段文字两次（重复），只删一次会留另一份。
- **解法**：
  1. 替换后立即 `Read` 整文件验证
  2. 复杂改动直接 `Write` 整文件（已知完整内容时）
  3. 重复出现的清理用循环：先 `Read` → 写正则删全部匹配 → 写回
- **预防**：search/replace 改完必 `Read` 验证。宁可多一次 `Read` 也不要留垃圾代码。

### [011] git 没有本地 fork 概念，"fork 一个本地路径"靠直接复制 .git

- **日期**：2026-08-13
- **现象**：用户说「先 clone 到 repos，然后干净复制到我指定路径」时，第一反应查 `git fork --local` 是否存在。`git help -a` 中没有 `fork` 子命令，也没有 `local` 子命令。`git worktree` 是同仓库多分支检出，不是 fork。
- **根因**：git 设计上「fork」是托管平台（GitHub / GitLab）概念，不是 git 自身概念。本地想要「同一仓库的多份独立副本」，最直接的方式就是直接复制 `.git` 目录（因为 `.git` 是仓库的完整状态机）。
- **解法**：
  1. 直接用 `robocopy` / `Copy-Item -Recurse` 复制整个 `repos/<owner>__<repo>` 到目标绝对路径（含 `.git`）。
  2. 复制后 `git -C <target> rev-parse HEAD` 验证 sha 一致。
  3. 排除 `.git/objects/pack` 里的临时 `tmp_*.pack`（如有），避免复制中文件被锁。
- **预防**：用户提到「fork」「本地复制」「镜像到某路径」时，**不要**尝试找 `git fork` 命令，直接走「复制 .git 目录」路线，并在执行前向用户确认「目标存在则报错停手（不覆盖）」。详见 [workflows-sync-to.md](./workflows-sync-to.md)。
