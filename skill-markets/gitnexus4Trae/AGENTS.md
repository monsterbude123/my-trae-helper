# gitnexus4Trae — GitNexus 代码智能 for TRAE IDE

> 此文件是给 AI 代理（TRAE）的使用说明书。告诉你在什么情况下应该加载哪个 GitNexus skill。
> **前提条件：需要先安装 GitNexus MCP Server 并运行 `npx gitnexus analyze` 构建项目索引。**

---

## 安装

将技能安装到 Trae 全局技能目录：

```powershell
# 安装所有 gitnexus4Trae 技能
Copy-Item -Recurse "d:\workspace\my-trae-helper\gitnexus4Trae\skills\*" "$env:USERPROFILE\.trae-cn\builtin_skills\"

# 验证安装
Get-ChildItem -Directory "$env:USERPROFILE\.trae-cn\builtin_skills\" | Where-Object { $_.Name -like "gitnexus-*" } | Select-Object Name
```

安装后需**重启 TRAE IDE**，技能才能被 `/` 命令和自然语言触发识别。

---

## 可用 Skills 总览

| Skill | 用途 | 触发词 |
|-------|------|--------|
| `gitnexus-guide` | GitNexus 工具、资源、图模式速查 | "GitNexus 怎么用"、"有哪些工具" |
| `gitnexus-cli` | 索引、状态、清理、wiki 命令 | "索引这个项目"、"重新分析"、"clean 索引" |
| `gitnexus-exploring` | 理解架构、探索代码、追踪执行流 | "X 怎么工作"、"谁调用了这个函数"、"认证流程" |
| `gitnexus-debugging` | 追踪 bug、定位错误来源 | "为什么 X 失败了"、"这个错误从哪来"、"追踪 bug" |
| `gitnexus-impact-analysis` | 爆炸半径分析、修改前安全检查 | "改 X 会影响什么"、"依赖了什么"、"安全吗" |
| `gitnexus-refactoring` | 安全重命名、提取模块、拆分重构 | "重命名"、"提取到模块"、"安全重构" |

---

## 何时加载哪个 Skill

### 场景一：用户想了解 GitNexus 本身

```
用户说：                              → 你应该：

"GitNexus 有哪些工具"                  → 加载 gitnexus-guide
"GitNexus 怎么用"                      → 加载 gitnexus-guide
"GitNexus 的工具参考"                  → 加载 gitnexus-guide
"什么是 GitNexus"                      → 加载 gitnexus-guide
```

### 场景二：用户需要索引/管理项目

```
用户说：                              → 你应该：

"索引这个项目"                         → 加载 gitnexus-cli
"重新分析代码库"                       → 加载 gitnexus-cli
"生成 wiki"                           → 加载 gitnexus-cli
"清理 GitNexus 索引"                  → 加载 gitnexus-cli
"检查索引状态"                         → 加载 gitnexus-cli
```

### 场景三：用户想理解代码

```
用户说：                              → 你应该：

"认证是怎么工作的"                     → 加载 gitnexus-exploring
"这个项目的架构是什么"                 → 加载 gitnexus-exploring
"谁调用了这个函数"                     → 加载 gitnexus-exploring
"支付流程怎么走"                       → 加载 gitnexus-exploring
"数据库逻辑在哪"                       → 加载 gitnexus-exploring
```

### 场景四：用户在调试

```
用户说：                              → 你应该：

"这个函数为什么失败了"                 → 加载 gitnexus-debugging
"追踪这个错误从哪来的"                 → 加载 gitnexus-debugging
"谁调用了这个方法"                     → 加载 gitnexus-debugging
"这个接口返回 500"                     → 加载 gitnexus-debugging
```

### 场景五：用户要修改代码前

```
用户说：                              → 你应该：

"改这个安全吗"                         → 加载 gitnexus-impact-analysis
"改 X 会破坏什么"                      → 加载 gitnexus-impact-analysis
"这个函数的爆炸半径"                   → 加载 gitnexus-impact-analysis
"谁在用这段代码"                       → 加载 gitnexus-impact-analysis
"提交前检查影响范围"                   → 加载 gitnexus-impact-analysis
```

### 场景六：用户要重构

```
用户说：                              → 你应该：

"重命名这个函数"                       → 加载 gitnexus-refactoring
"把这个提取出来"                       → 加载 gitnexus-refactoring
"拆分这个服务"                         → 加载 gitnexus-refactoring
"把这个移到新文件"                     → 加载 gitnexus-refactoring
"重构这个模块"                         → 加载 gitnexus-refactoring
```

---

## Skill 组合使用指南

### 工作流一：安全修改代码

```
1. 用户："把 validateUser 重命名为 authenticateUser"
2. 加载 gitnexus-refactoring → 先用 impact 分析爆炸半径 → 再用 rename
3. 完成后 → detect_changes 验证影响范围
```

### 工作流二：理解 + 调试

```
1. 用户："支付功能偶发 500，帮我看看"
2. 加载 gitnexus-debugging → query 定位相关流程 → context 深入分析
3. 如需理解架构 → 加载 gitnexus-exploring → 追踪完整执行流
```

### 工作流三：重构前安全评估

```
1. 用户："我想重构整个 auth 模块"
2. 加载 gitnexus-impact-analysis → 分析所有受影响符号和流程
3. 评估风险等级 → 通知用户 → 再进入重构
```

---

## 自动加载判断逻辑

```
1. 话语包含 "GitNexus"、"gitnexus"、"索引"、"analyze"、"知识图谱"、"代码图"？
   └─ 判断具体任务 → 加载对应 skill

2. 话语包含 "怎么工作"、"架构"、"执行流"、"谁调用"、"追踪流程"？
   └─ 加载 gitnexus-exploring

3. 话语包含 "为什么失败"、"错误追踪"、"bug"、"500"、"报错"？
   └─ 加载 gitnexus-debugging

4. 话语包含 "影响什么"、"安全吗"、"爆炸半径"、"依赖"、"会破坏"、"blast radius"？
   └─ 加载 gitnexus-impact-analysis

5. 话语包含 "重命名"、"提取"、"拆分"、"重构"、"移到"？
   └─ 加载 gitnexus-refactoring

6. 话语包含 "索引"、"analyze"、"status"、"clean"、"wiki"、"npx gitnexus"？
   └─ 加载 gitnexus-cli

7. 话语包含 "工具"、"资源"、"schema"、"MCP"、"参考"、"guide"？
   └─ 加载 gitnexus-guide
```

---

## GitNexus MCP 调用规范（TRAE 专用）

在 TRAE IDE 中，GitNexus MCP 工具通过 `run_mcp` 调用：

```
run_mcp({server_name: "gitnexus", tool_name: "query",          args: {query: "认证流程"}})
run_mcp({server_name: "gitnexus", tool_name: "context",        args: {name: "validateUser"}})
run_mcp({server_name: "gitnexus", tool_name: "impact",         args: {target: "validateUser", direction: "upstream"}})
run_mcp({server_name: "gitnexus", tool_name: "detect_changes", args: {}})
run_mcp({server_name: "gitnexus", tool_name: "rename",         args: {symbol_name: "oldName", new_name: "newName", dry_run: true}})
run_mcp({server_name: "gitnexus", tool_name: "cypher",         args: {query: "MATCH ..."}})
run_mcp({server_name: "gitnexus", tool_name: "list_repos",     args: {}})
```

**索引陈旧处理**：如果任何工具返回索引过时警告，先在终端运行 `npx gitnexus analyze`。

---

## 重要原则

1. **修改前必做影响分析**：修改任何函数/类/方法前，先用 `gitnexus-impact-analysis` 检查爆炸半径
2. **重命名用 GitNexus**：不要用查找替换，用 `gitnexus-refactoring` 的 `rename` 工具
3. **提交前验证**：提交前运行 `detect_changes` 确认影响范围
4. **高风险必通知**：影响分析返回 HIGH/CRITICAL 时必须告知用户
5. **探索代码首选 GitNexus**：不要用 grep 盲目搜索，用 `query` 找执行流

---

## Hook 自动化配置

Hook 是 Trae v3.5.66+ 新增的自动化机制，在智能体生命周期事件节点自动执行 Shell 命令。gitnexus4Trae 提供了示例 Hook 配置，实现索引状态检查、修改前影响分析提醒、会话结束变更验证。

### 配置文件

示例配置位于 `example/hooks/` 目录：

```
example/hooks/
├── gitnexus-hooks.json   # Hook 配置文件（复制到 .trae/hooks.json）
├── index-check.ps1       # SessionStart: 索引状态检查
├── impact-gate.ps1       # PreToolUse: 修改前影响分析提醒
└── changes-verify.ps1    # Stop: 会话结束变更验证
```

### 三个 Hook 的作用

| Hook | 事件 | 作用 |
|------|------|------|
| `gitnexus-index-check` | SessionStart | 会话开始时检查索引是否存在和新鲜，过时则提示 `npx gitnexus analyze` |
| `gitnexus-impact-gate` | PreToolUse (Write\|Edit) | 修改源代码前提醒先做影响分析，不阻断执行 |
| `gitnexus-changes-verify` | Stop | 会话结束时检查 git 变更，建议运行 `detect_changes` 验证 |

### 安装到项目

```powershell
# 1. 复制 Hook 配置到项目
Copy-Item "d:\workspace\my-trae-helper\skill-markets\gitnexus4Trae\example\hooks\gitnexus-hooks.json" ".trae\hooks.json"

# 2. 复制 Hook 脚本到项目
New-Item -ItemType Directory -Path ".trae\hooks" -Force
Copy-Item "d:\workspace\my-trae-helper\skill-markets\gitnexus4Trae\example\hooks\*.ps1" ".trae\hooks\"

# 3. 重启 TRAE IDE 使 Hook 生效
```

> **注意**：Hook 以提醒模式运行（不阻断工具执行）。如需严格门禁模式（修改前必须通过影响分析），可将脚本中的 `exit 0` 改为 `exit 1`。
