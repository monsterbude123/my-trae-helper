# 答疑红线(4 条铁律)

> 沉淀自 project-rules.md §6。仓库追踪场景下"回答用户问题"的硬约束。
> 单文件 ≤ 200 行。

## 1. 4 条铁律

### 铁律 1 — 数字/commit/tag/版本号必须实测

```
MUST: 来自本地 git 实测
  git -C <path> rev-parse HEAD
  git -C <path> tag --list "v19*"
  git -C <path> rev-list -n 1 <tag>

MUST NOT:
  - 凭记忆
  - 网络搜索
  - 编造
```

**反例**:用户问「react 最新发了什么」,agent 答「应该是 v19」(没跑 `git log`)。

### 铁律 2 — 来源标注

```
格式:「根据 <来源路径>(<新鲜度 emoji>)...」

示例:
  ✅ 根据 docs/facebook__react/ARCHITECTURE.md(🟢 0.95),react 用 fiber 调度器...
  ✅ 根据 git log 查 commit abc1234,本次修改了 useState hook...
```

**反例**:不带来源的结论(用户无法判断可信度)。

### 铁律 3 — 不盲信文档

```
文档与代码冲突时:
  - 以代码为准(git show / git grep 实测)
  - 报告不一致(「文档说 X,代码实际是 Y」)
  - 标注文档可能过期(建议更新)
```

**反例**:用户问「XXX 函数怎么用」,agent 答「根据文档 X」(没验证文档与代码是否一致)。

### 铁律 4 — 不臆造

```
本地没有的仓库 / 查不到的信息:
  - 直接说「未收录」或「未找到」
  - 不编造可能的内容
  - 不"猜测一个大概对的答案"
```

**反例**:用户问「某某项目有 react-router 吗」,agent 答「应该有吧」(没真查 docs/)。

## 2. 答疑决策树

```
用户问 X →
  ├── 涉及具体数字/commit/tag?
  │   └─ MUST git 实测(铁律 1)
  │
  ├── 涉及概念/原理/怎么用?
  │   ├─ 先 docs/<owner>__<repo>/ 命中?
  │   │   ├─ 🟢 → 直引,标注来源(铁律 2)
  │   │   ├─ 🟡 → 标注「可能过时」,涉及代码用 git 验证(铁律 3)
  │   │   └─ 🔴 → 必须交叉验证,以代码为准
  │   └─ 未命中 → 降级 fuzzy / 源码 git grep,仍未命中说「未找到」(铁律 4)
  │
  └── 涉及跨仓库检索?
      └─ query-index.py --lookup "X" 跨 docs/ 检索
```

详见 [workflows-baseline.md §4 QUERY 决策树](./workflows-baseline.md)

## 3. 反模式

- ❌ "应该是..." / "可能..." / "大概..."(没真查)
- ❌ 直接引用 docs 不标注来源
- ❌ 文档与代码冲突时相信文档
- ❌ "未收录"编造成"未收录但相关内容大概是 X"
- ❌ 用记忆里的版本号/commit 答(违反实测铁律)

## 4. 与其他 references 关系

- `workflows-baseline.md §4` → QUERY 决策树基线
- `doc-map-manager-usage.md §3` → 新鲜度协议
- `reply-conventions.md §1.4` → 数字/commit 实测(更广义的回复规范)
- `pitfalls §010` → Edit 工具残留反例(与"答案残留"对称)