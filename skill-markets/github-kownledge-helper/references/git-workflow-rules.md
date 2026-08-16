# git 工作流规则(硬约束)

> 沉淀自 project-rules.md §4。仓库追踪场景下"clone / pull"的 5 条铁律。
> 单文件 ≤ 200 行。

## 1. 5 条铁律

| # | 规则 | 反例 |
|---|------|------|
| 1 | **完整克隆默认**:`git clone <url> <path>`,拉取全部历史(用户日常需要 commit / blame / tag 查询) | 浅克隆导致 tag 查询丢失早期版本 |
| 2 | **ff-only**:`git pull --ff-only`,遇非快进不强推,报告并询问是否 `reset --hard origin/<branch>` | 自动 merge / rebase 掩盖本地分叉 |
| 3 | **顺序执行**:UPDATE-ALL 顺序拉取,禁止并发 | 并发拉取打满网络 + 索引产物污染 |
| 4 | **失败不静默**:clone/pull 失败必须报错,不写 manifest,不留半成品目录 | 静默失败导致 manifest 与 git 状态不一致 |
| 5 | **网络降级**:连续失败 2 次降级为 `git clone --depth 1` 重试(仅网络受限场景),仍失败则报告 `[FATAL_ERROR] network` | 直接放弃或无限重试 |

## 2. 状态读取(4 字段一次拉全)

任何 ADD / UPDATE 后,manifest 必须更新这 4 个字段:

```powershell
$repo = "repos/facebook__react"
git -C $repo rev-parse --abbrev-ref HEAD        # default_branch
git -C $repo rev-parse HEAD                     # current_commit (40 字符)
git -C $repo rev-parse --short HEAD             # current_commit_short (7 字符)
git -C $repo log -1 --format=%cI HEAD           # current_commit_date (ISO 8601)
```

## 3. 顺序执行的实现

```typescript
// TS CLI 模式
async function updateAll(repos: Repo[]): Promise<UpdateResult[]> {
  const results: UpdateResult[] = [];
  for (const repo of repos) {                    // for-of 而非 Promise.all
    try {
      const r = await updateOne(repo);
      results.push(r);
    } catch (e) {
      results.push({ repo, status: 'failed', error: String(e) });
      // 不 rethrow,失败隔离不阻塞后续
    }
  }
  return results;
}
```

## 4. ff-only 失败处理(三选一用户决策)

```
❌ fatal: Not possible to fast-forward, aborting.
原因:本地 HEAD 领先 origin/main(本地未推 commit,或 origin main 被 reset/rebase)

用户决策三选一(参考 [reply-conventions.md §1.3](./reply-conventions.md) 失败回复规范):
  1. reset --hard origin/main(推荐,本项目用,仓库内无本地修改)
  2. 保留分叉,手动 rebase
  3. 重新 clone

执行前必须等用户决策。reset 完成后必须再跑一次 update <repo> 让 manifest 对齐
(reset 直接改 HEAD,manifest 不知道,见 pitfalls §004)
```

## 5. 网络降级条件

```typescript
async function cloneWithFallback(url: string, path: string): Promise<void> {
  try {
    await execGit(['clone', url, path]);
  } catch (e) {
    if (e.message.includes('Could not resolve host') ||
        e.message.includes('timeout')) {
      await execGit(['clone', '--depth', '1', url, path]);
    } else {
      throw e;
    }
  }
}
```

## 6. 反模式(必避免)

- ❌ 用 `isomorphic-git`(重型依赖,调系统 git 即可)
- ❌ 自动 reset(违反 §4,需用户决策)
- ❌ UPDATE-ALL 用 Promise.all 并发(违反 §3,顺序拉取)
- ❌ 浅克隆当默认(违反 §1,完整克隆默认)
- ❌ 进度条刷屏(详见 pitfalls §009 — `gitStream` 回调过滤 `isProgressBar`)

## 7. 与其他 references 关系

- `workflows-baseline.md §1 ADD 步骤 4` → 完整克隆默认
- `workflows-baseline.md §2 UPDATE 步骤 3` → ff-only
- `workflows-baseline.md §3 UPDATE-ALL 步骤 2` → 顺序执行
- `manifest-schema.md` → 状态读取后回写
- `pitfalls §004` → ff-only 失败具体案例
- `pitfalls §009` → 进度条刷屏