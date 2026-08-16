# 工作流模式

> 沉淀 ADD / UPDATE / UPDATE-ALL / QUERY 工作流的实战变体与边界处理。
> 完整基线流程见 [workflows-baseline.md](./workflows-baseline.md)（已独立成文件，本文件只记**变体与增强**）。
> 单文件 ≤ 200 行；超长主题已拆分：
> - **基线 4 大工作流(9 步流程 + 决策树)** → [workflows-baseline.md](./workflows-baseline.md)
> - 聚合目录处理 → [workflows-aggregate.md](./workflows-aggregate.md)
> - 探测协议 + 技术栈迁移 → [workflows-protocols.md](./workflows-protocols.md)
> - SYNC-TO 镜像 → [workflows-sync-to.md](./workflows-sync-to.md)

## ADD — 收录新仓库

### 基线（见 [workflows-baseline.md §1](./workflows-baseline.md#1-add--收录新仓库)）

### 变体：monorepo / 大型仓

- 浅克隆后 `docs/` 同步只取顶层文档（README / CHANGELOG / ARCHITECTURE / CONTRIBUTING），不递归子包文档，避免索引爆炸。
- 若顶层无 ARCHITECTURE.md → 检查 `docs/` 子目录，取主架构文档。

### 变体：已存在目录但未登记

```
1. repos/<owner>__<repo> 已存在但 manifest 无记录
2. 不直接覆盖 → 询问用户：
   - A. 重新 clone（删除现有目录）
   - B. 接管现有目录（读 git 状态后补登记）
3. 选 B → 读 git 状态 → 回写 manifest，added_at = now
```

## UPDATE — 更新单个

### 基线（见 [workflows-baseline.md §2](./workflows-baseline.md#2-update--更新单个仓库)）

### 增强：freshness gate

答疑前自动判断是否需要 pull：

```
last_pull_at 距今 > 24h → 自动 UPDATE
< 24h → 跳过 pull，直接查（用户可显式要求强制更新）
```

## UPDATE-ALL — 一键全更新

### 基线（见 [workflows-baseline.md §3](./workflows-baseline.md#3-update-all--一键全更新)）

### 增强：失败隔离

- 单仓失败不阻塞后续仓 → 记录失败列表，最后统一报告。
- 失败仓下次 UPDATE-ALL 优先重试。

## QUERY — 答疑

### 基线（见 [workflows-baseline.md §4](./workflows-baseline.md#4-query--答疑核心场景)）

### 决策增强：概念性问题的双路验证

```
问"XXX 怎么实现"
  → doc-map-manager --grab "XXX"
    ├── 命中且 🟢 → 引用，但若涉及 API/函数名 → git grep 验证存在性
    ├── 命中但 🔴 → 必须 git show / git grep 交叉验证，冲突以代码为准
    └── 未命中 → --fuzzy → 仍未命中 → git grep 源码降级
```

### 4. 跨仓库检索

→「哪些收录的仓库用到了 X」
→ `query-index.py --lookup "X"` 跨 `docs/` 所有子目录检索
→ 输出命中的仓库列表 + 文档路径 + 新鲜度

## 6. TS CLI 工作流（2026-08-13 替代 PowerShell）

所有维护脚本统一为 Node.js/TypeScript，用 pnpm 管理，跨平台统一。

### 文件布局

```
scripts/
├── bin/cli.ts                  # commander 入口
├── src/commands/               # 每个子命令一个文件
│   ├── sync-manifest.ts
│   └── sync-docs.ts
├── src/lib/                    # 基础库
│   ├── paths.ts                # 项目根/REPOS/DOCS/MANIFEST 常量（基于 import.meta.url 推算）
│   ├── git.ts                  # execFileSync('git', args) 封装，失败返回空串
│   ├── manifest.ts             # 读/原子写 manifest（.tmp + rename）
│   └── time.ts                 # ISO 8601 +08:00（不依赖本地时区）
├── package.json                # packageManager + bin + scripts + type: module
├── tsconfig.json               # ES2022 + NodeNext + strict + resolveJsonModule
└── pnpm-workspace.yaml         # allowBuilds + verifyDepsBeforeRun
```

### 跨平台要点

- **路径**：用 `node:path` 的 `join()`，禁硬编码 `\\` 或 `/`。`paths.ts` 用 `fileURLToPath(import.meta.url)` 反推项目根。
- **git 调用**：调系统 `git`（Windows / macOS / Linux 都有），不要用 `isomorphic-git`（重型依赖）。
- **原子写**：先 `writeFileSync(path + '.tmp')`，再 `renameSync` 到正式路径。Node 的 `rename` 在同一文件系统是原子的。
- **时间**：固定输出 `+08:00`（不依赖本地时区），用 `Intl.DateTimeFormat('zh-CN', { timeZone: 'Asia/Shanghai' })` 格式化。
- **类型**：strict + NodeNext 解析，所有跨文件 import 必须带 `.js` 后缀（即使源是 .ts）。

### pnpm v11 配置坑

详见 [pitfalls.md §002](./pitfalls.md#002-pnpm-v11-因-esbuild-build-script-未-approve-永远-exit-1)。

简记：native dep（esbuild / node-sass / sharp 等）必须用 `pnpm-workspace.yaml` 的 `allowBuilds.<pkg>: true`，v11 废弃了 `package.json#pnpm.onlyBuiltDependencies`。

> §9 缺失-CLI 走开发的工作流已独立到 [cli-development.md](./cli-development.md)（避免单文件超 200 行）。
> §10 SYNC-TO 镜像工作流已独立到 [workflows-sync-to.md](./workflows-sync-to.md)。