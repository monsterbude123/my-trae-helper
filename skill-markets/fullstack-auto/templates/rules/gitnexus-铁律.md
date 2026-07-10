# GitNexus 铁律 — 代码分析唯一入口

> 触发条件：任何需要理解代码、查找符号、分析调用链、评估影响面的操作。
> 核心原则：**GitNexus 是代码分析的唯一通道。grep/glob 是盲人摸象。**

---

## §0 零号铁律

```
GITNEXUS FIRST. GREP NEVER.

任何代码分析任务：
  第一步 → GitNexus query / context / impact
  失败 → 重试（修正参数），最多 3 次
  仍失败 → 汇报用户，请求人工干预
  绝不 → 降级为 grep / glob
```

**grep/glob 只允许用于：查找文件路径、匹配确切的字符串常量（如 "TODO"、"ponytail:"）、查找配置文件。禁止用于理解代码结构、调用链、影响面。**

---

## §1 工具选择决策树

```
需要做什么？
├── 理解功能/概念/流程 → query({query: "自然语言描述", repo: "YOUR_REPO_PATH"})
├── 查看符号的调用者/被调用者 → context({name: "符号名", repo: "..."})
├── 修改前评估影响面 → impact({target: "符号名", direction: "upstream", repo: "..."})
├── 提交前确认变更范围 → detect_changes({repo: "..."})
├── 重命名符号 → rename(...)（禁止 find-replace）
├── 查看所有可用仓库 → list_repos()
└── 查看仓库状态/路由 → route_map / tool_map
```

---

## §2 正确参数速查（防出错）

> **将 `YOUR_REPO_PATH` 替换为实际仓库路径。** 路径格式取决于操作系统：
> - Windows: `"D:\\workspace\\your-project"`
> - macOS/Linux: `"/home/user/workspace/your-project"`

### query — 概念搜索
```json
{
  "query": "自然语言搜索词（必填！不可为空）",
  "repo": "YOUR_REPO_PATH",
  "limit": 5,
  "task_context": "我正在做XX（可选，帮助排序）",
  "goal": "我想找到YY（可选，帮助排序）"
}
```
- `query` 是必填项，不能为空字符串
- 没有 `query` 参数 → 必定报错 "query parameter is required"

### context — 符号360度视图
```json
{
  "name": "函数名或类名（与 uid 二选一）",
  "uid": "从之前结果中获取的 UID（与 name 二选一）",
  "repo": "YOUR_REPO_PATH",
  "include_content": false
}
```
- 如果符号名有歧义，加 `file_path` 或 `kind` 辅助定位

### impact — 影响面分析
```json
{
  "target": "符号名（必填）",
  "direction": "upstream（必填）",
  "repo": "YOUR_REPO_PATH",
  "maxDepth": 3,
  "summaryOnly": false
}
```
- `target` 和 `direction` 均为必填项

---

## §3 重试协议

GitNexus 调用失败时，执行以下重试策略（最多 3 次）：

| 尝试 | 策略 |
|------|------|
| 第 1 次 | 检查参数是否正确（对照 §2 速查表）→ 修正后重试 |
| 第 2 次 | 换一种方式：query 失败改 context，context 失败改 query |
| 第 3 次 | 先用 `list_repos()` 确认仓库状态，再重试原始调用 |

3 次全部失败 → 🛑 **停止，汇报用户**。禁止降级为 grep/glob。

如果 MCP Server 整体不可用（连续 2 个不同工具都失败），汇报用户并等待修复。

---

## §4 禁止行为清单

| 禁止行为 | 后果 |
|---------|------|
| GitNexus 可用却用 grep 理解代码 | 🛑 停止，回退到 GitNexus query |
| GitNexus 可用却用 glob 找符号 | 🛑 停止，回退到 GitNexus context |
| GitNexus 参数错了 1 次就放弃 | 🛑 强制重试（§3 协议） |
| 修改代码前不跑 impact | 🛑 停止，先跑 impact |
| 提交前不跑 detect_changes | 🛑 阻止提交 |
| 用 find-replace 替代 rename | 🛑 停止，用 gitnexus rename |

---

## §5 grep/glob 白名单（仅限以下用途）

以下场景可以使用 grep/glob，其他一律禁止：

```
✅ glob 查找文件路径         → 例如 "src/components/**/*.tsx"
✅ grep 匹配字符串常量       → 例如 "ponytail:"、"TODO"、"FIXME"
✅ grep 查找配置项           → 例如 "DATABASE_URL" 在 .env 文件
✅ grep 查找 import 语句     → 例如 "from 'lodash'" （配合重命名）
❌ grep 理解代码调用链       → 用 GitNexus context/impact
❌ grep 搜索函数定义         → 用 GitNexus context
❌ glob 查找模块位置         → 用 GitNexus query
❌ grep 评估影响范围         → 用 GitNexus impact
```

**判定原则：如果你在 grep 一个函数名来找"谁调用了它"，你在做 GitNexus 的活。停下，换 GitNexus。**

---

## §6 仓库名映射（项目专属，请替换）

由于存在同名仓库，必须使用完整路径：

```
目标仓库                          GitNexus repo 参数
─────────────────────────────────────────────────────
{YOUR_REPO_PATH}                    → "{YOUR_REPO_PATH}"
```

**请在项目初始化时填写实际仓库路径，删除占位符。**

---

## §7 会话启动检查清单

```
[ ] GitNexus MCP Server 是否可用？→ list_repos() 验证
[ ] 目标仓库是否在列表中？       → 确认路径映射（§6）
[ ] 仓库索引是否过期？           → 检查 staleness，过期先 analyze
```

## 参见

- `strict.md` §GitNexus 规则 — 整体流程门禁
- `AGENTS.md` — 技能包速查
