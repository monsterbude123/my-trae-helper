---
name: gitnexus-refactoring
description: "用于安全重命名、提取模块、拆分或重组代码。当用户说\"重命名这个函数\"、\"提取到模块\"、\"重构这个类\"、\"移到新文件\"、\"安全重构\"时加载。任何涉及重命名、提取、拆分或重组代码的任务都应加载。"
---

# GitNexus 安全重构

## 使用场景

- "安全重命名这个函数"
- "把这个提取到模块"
- "拆分这个服务"
- "把这个移到新文件"
- 任何涉及重命名、提取、拆分或重组代码的任务

## 工作流

```
1. impact({target: "X", direction: "upstream"})  → 映射所有依赖者
2. query({query: "X"})                            → 找到涉及 X 的执行流
3. context({name: "X"})                           → 查看所有入向/出向引用
4. 规划更新顺序: 接口 → 实现 → 调用者 → 测试
```

## 检查清单

### 重命名符号

- [ ] `rename({symbol_name: "oldName", new_name: "newName", dry_run: true})` — 预览所有编辑
- [ ] 审查 graph 编辑（高置信度）和 ast_search 编辑（需仔细检查）
- [ ] 确认无误后: `rename({..., dry_run: false})` — 应用编辑
- [ ] `detect_changes()` — 验证只有预期文件被修改
- [ ] 运行受影响流程的测试

### 提取模块

- [ ] `context({name: target})` — 查看所有入向/出向引用
- [ ] `impact({target, direction: "upstream"})` — 找到所有外部调用者
- [ ] 定义新模块接口
- [ ] 提取代码，更新导入
- [ ] `detect_changes()` — 验证影响范围
- [ ] 运行受影响流程的测试

### 拆分函数/服务

- [ ] `context({name: target})` — 了解所有被调用者
- [ ] 按职责分组被调用者
- [ ] `impact({target, direction: "upstream"})` — 映射需要更新的调用者
- [ ] 创建新函数/服务
- [ ] 更新调用者
- [ ] `detect_changes()` — 验证影响范围
- [ ] 运行受影响流程的测试

## TRAE MCP 调用参考

**rename** — 自动多文件重命名：

```
run_mcp({server_name: "gitnexus", tool_name: "rename", args: {symbol_name: "validateUser", new_name: "authenticateUser", dry_run: true}})
→ 12 次编辑, 8 个文件
→ 10 个 graph 编辑 (高置信度), 2 个 ast_search 编辑 (需审查)
→ 变更: [{file_path, edits: [{line, old_text, new_text, confidence}]}]
```

**impact** — 先映射所有依赖者：

```
run_mcp({server_name: "gitnexus", tool_name: "impact", args: {target: "validateUser", direction: "upstream"}})
→ d=1: loginHandler, apiMiddleware, testUtils
→ 受影响流程: LoginFlow, TokenRefresh
```

**detect_changes** — 重构后验证改动：

```
run_mcp({server_name: "gitnexus", tool_name: "detect_changes", args: {scope: "all"}})
→ 变更: 8 文件, 12 符号
→ 受影响流程: LoginFlow, TokenRefresh
→ 风险: MEDIUM
```

**cypher** — 自定义引用查询：

```
run_mcp({server_name: "gitnexus", tool_name: "cypher", args: {query: "MATCH (caller)-[:CodeRelation {type: 'CALLS'}]->(f:Function {name: 'validateUser'}) RETURN caller.name, caller.filePath ORDER BY caller.filePath"}})
```

## 风险规则

| 风险因素 | 缓解措施 |
|---------|---------|
| 调用者多（>5）| 用 `rename` 自动更新 |
| 跨区域引用 | 事后用 `detect_changes` 验证范围 |
| 字符串/动态引用 | 用 `query` 查找 |
| 外部/公开 API | 版本化并正确标记过时 |

## 示例：重命名 `validateUser` → `authenticateUser`

```
1. run_mcp({server_name: "gitnexus", tool_name: "rename", args: {symbol_name: "validateUser", new_name: "authenticateUser", dry_run: true}})
   → 12 次编辑: 10 graph (安全), 2 ast_search (需审查)
   → 文件: validator.ts, login.ts, middleware.ts, config.json...

2. 审查 ast_search 编辑 (config.json: 动态引用!)

3. run_mcp({server_name: "gitnexus", tool_name: "rename", args: {symbol_name: "validateUser", new_name: "authenticateUser", dry_run: false}})
   → 已应用 12 次编辑到 8 个文件

4. run_mcp({server_name: "gitnexus", tool_name: "detect_changes", args: {scope: "all"}})
   → 受影响: LoginFlow, TokenRefresh
   → 风险: MEDIUM — 运行这些流程的测试
```

## 绝对禁止

- 绝对不要用查找替换来重命名 — 用 `rename`，它理解调用图

> 如果索引过时，先在终端运行 `npx gitnexus analyze`。
