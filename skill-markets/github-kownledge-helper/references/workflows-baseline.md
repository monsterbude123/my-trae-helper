# 工作流基线(4 大工作流 9 步详细流程 + 决策树)

> 完整基线流程(2026-08-13 蒸馏)。`workflows.md` 主文件只写变体与增强。
> 单文件 ≤ 200 行。配套:pitfalls.md / commands.md / cli-development.md。
>
> **本文件的角色**:
> - 当用户任务模糊 → 查本文件 §决策树 决定走哪条基线
> - 当 agent 接手一个新仓库类 → 查本文件 §9 步流程 复刻
> - 不要直接复制 AGENT.md 全文 → 单文件源原则,本文件只放沉淀增量

## 1. ADD — 收录新仓库

触发:用户说「加个仓库 facebook/react」或丢一个 GitHub URL。

```
1. 解析输入 → 规范化为 {owner, repo}
   - "facebook/react"                        → owner=facebook, repo=react
   - "https://github.com/facebook/react"     → 同上
   - "https://github.com/facebook/react.git" → 同上
2. 校验 manifest 是否已收录(按 full_name 去重)→ 已存在则提示并退出
3. 目标路径:repos/<owner>__<repo>(双下划线,见 [project-paths.md](./project-paths.md))
   - 若目录已存在但未登记 → 提示冲突,询问处理方式
4. git clone <url> <path>           # 完整克隆(默认策略,见 [git-workflow-rules.md §1](./git-workflow-rules.md))
   - 失败 → 报错,不写 manifest
5. 读取:当前 branch、commit sha(40 字符)、commit date(ISO 8601)
6. 同步关键文档到 docs/<owner>__<repo>/(README/CHANGELOG/ARCHITECTURE/CONTRIBUTING)
7. 回写 manifest.json(追加一条,更新 updated_at)
8. 触发 doc-map-manager 增量索引(见 [doc-map-manager-usage.md](./doc-map-manager-usage.md))
9. 回复:收录成功 + commit 摘要(简表,见 [reply-conventions.md](./reply-conventions.md))
```

## 2. UPDATE — 更新单个仓库

触发:用户说「更新 react」或答疑前自动 freshness check。

```
1. 从 manifest 定位 repo
2. git -C <path> fetch origin
3. git -C <path> pull --ff-only
   - 冲突(非 ff)→ 不强推,报告状态,询问是否 reset --hard origin/<branch>(用户决策三选一,见 pitfalls §004)
4. 读取新 commit sha / date
5. 与 manifest 中 current_commit 比对:
   - 相同 → 无更新,仅刷新 last_pull_at
   - 不同 → 更新 current_commit / date / last_pull_at,记录"有更新"
6. 若有更新 → 同步 docs/ 并增量索引
7. 回复:更新结果(前进 N 个 commit / 已最新)
```

## 3. UPDATE-ALL — 一键全更新

触发:用户说「全部更新到最新」。

```
1. 读 manifest.repos 列表
2. 顺序执行 UPDATE 流程(避免并发拉取打满网络,见 [git-workflow-rules.md §3](./git-workflow-rules.md))
3. 汇总:N 个有更新 / M 个已最新 / K 个失败(失败隔离,不阻塞)
4. 一次性重建 docs/ 索引(build-index --incremental)
5. 输出汇总表
```

## 4. QUERY — 答疑(核心场景)

触发:「react 最新发了什么」「v19 在哪个 commit」「这个 PR 改了哪几个文件」。

### 决策树

```
├── 问"最新发了什么 / 最近更新"
│   → UPDATE(自动 freshness check) → git log --oneline -20 → 摘要回复
│
├── 问"v19 / 某版本 / 某 tag 在哪个 commit"
│   → git rev-list -n 1 <tag>  或  git tag --list
│
├── 问"这个 PR 改了哪几个文件"
│   → git show --stat <merge-sha>  或  git log --merges
│
├── 问"XXX 怎么实现 / XXX 是什么"(概念性)
│   → 先查 docs/ 知识库:query-index.py --grab "XXX"
│   → 命中 → 检查新鲜度(🟢≥0.7 / 🟡0.3~0.7 / 🔴<0.3)→ 涉及代码实现则用 git show 验证
│   → 未命中 → 降级 --fuzzy,或直接 git grep 本地仓库源码
│
└── 问"哪些仓库用到了 X 技术"
    → query-index.py --lookup "X" 跨仓库检索 docs/
```

### 答疑强制协议(来自 doc-map-manager 知识生命周期)

```
1. 引用文档前必须检查新鲜度:🟢 ≥0.7 可直引 / 🟡 0.3~0.7 标注"可能过时" / 🔴 <0.3 必须交叉验证
2. 涉及 API/函数名/配置 → 用 git show / git grep 在本地源码验证,文档与代码冲突时以代码为准并报告不一致
3. 回复附带来源置信度:「根据 docs/facebook__react/ARCHITECTURE.md(🟢 新鲜度 0.95)...」
4. 同一概念多点召回 → 读完所有命中再归纳,不基于单篇下结论
```

## 5. 与 commands.md / cli-development.md 的关系

- 本文件是**基线**(9 步详细流程),任何 agent 接手任务时第一查
- `workflows.md` 主文件是**变体**(monorepo / 聚合目录 / 探测协议 / SYNC-TO 等)
- `cli-development.md` 是**缺失 CLI 时的开发流程**(5 步协议)
- `commands.md` 是**已落地命令的可复用模式**(TS CLI 入口 + git 状态读取命令)