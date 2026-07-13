# fullstack Hooks 配置（可选）

> TRAE IDE v3.5.66+ 支持 Hooks 功能，可在「设置」-「Hooks」中配置。
> Hook 机制允许开发者在 AI agent 生命周期的关键节点执行自定义 Shell 脚本，实现**确定性的自动化执行**，而非依赖 AI "记住"执行。

## 安装

将 `templates/hooks/fullstack-hooks.json` 复制到项目的 `.trae/hooks.json`：

```powershell
Copy-Item "tools\fullstack4TraeV4\templates\hooks\fullstack-hooks.json" ".trae\hooks.json"
```

在 TRAE IDE 中打开「设置」-「Hooks」，即可看到已配置的 Hook 列表。

### 在 settings 中启用/禁用

各 Hook 有 `enabled` 开关：
- **默认启用**（推荐）: `session-start`（注入上下文）、`spec-validate`（写 spec 后自动校验）、`tasks-integrity`（Stop 时检查完整性）
- **可选启用**: `doc-sync-gate`（写代码前检查文档同步）、`auto-test`（写代码后自动跑测试）、`complexity-guard`（提示复杂度评估）

## 自定义

用户可根据项目需要：
- 修改 `fullstack-hooks.json` 中的 `enabled` 字段
- 修改 `matcher` 字段以限定触发范围
- 编写自己的 Hook 脚本放在 `.trae/hooks/` 目录下

详情见 `templates/hooks/README.md`。

---

# fullstack Hooks — 可选配置

> TRAE IDE v3.5.66+ 支持 **Hook 功能**，让你在AI Agent 生命周期关键节点执行**自定义脚本**，实现确定性自动化闭环。

## 6 个 Hook 覆盖 5 种事件

| # | Hook名 | 事件 | 默认 | 用途 |
|---|--------|------|------|------|
| 1 | **fullstack-project-context** | `SessionStart` | ✅ 启用 | 会话启动时注入项目上下文（活跃变更、模块文档索引），减少"项目是什么"的来回沟通 |
| 2 | **fullstack-spec-validate** | `PostToolUse` (matcher: `Write`) | ✅ 启用 | 写 spec.md 后自动校验 BDD 格式 |
| 3 | **fullstack-tasks-integrity** | `Stop` | ✅ 启用 | 任务结束时检查 tasks.md 完整性 |
| 4 | **fullstack-doc-sync-gate** | `PreToolUse` (matcher: `Write\|Edit`) | ❌ 默认关闭 | 写代码前检查模块文档是否同步 |
| 5 | **fullstack-auto-test** | `PostToolUse` (matcher: `Edit\|Write`) | ❌ 默认关闭 | 写代码后自动跑相关测试 |
| 6 | **fullstack-complexity-guard** | `UserPromptSubmit` | ❌ 默认关闭 | 用户输入后评估复杂度（建议是否需要走 fullstack 流程） |

## 脚本

所有 Hook 的 PowerShell 脚本放在 `.trae/hooks/` 目录下：

| 脚本 | 说明 |
|------|------|
| `session-start.ps1` | 检测活跃变更 + 模块文档 + CODEMAPS + 配置 + 测试框架 |
| `spec-validate-hook.ps1` | 检查 WHEN/THEN/SHALL/Requirement（非阻断） |
| `tasks-integrity.ps1` | 检查 [x]/[ ] 完成度（仅警告） |
| `doc-sync-gate.ps1` | 检查未完成任务是否标注 DOC SYNC（仅警告） |
| `auto-test.ps1` | 自动检测测试框架并运行（阻断） |
| `complexity-guard.ps1` | 关键词评分 + 信号 → 建议（不阻断） |
| `render-cockpit.py` | **V7.1** 渲染驾驶舱（由 session-start 自动调用） |
| `log-agent-prompt.py` | **V7.1** 子 Agent 启动时落盘提示词到 `./llm-prompts/` |
| `env-init.py` | **V7.1** 环境检测与自动补全（手动运行） |

## 使用方式

1. 复制 `templates/hooks/fullstack-hooks.json` → `.trae/hooks.json`
2. 复制所有 `.ps1` 脚本 → `.trae/hooks/` 目录
3. 在 TRAE IDE 设置 → Hooks 中按需启用/禁用

### 触发流程

```
用户 Prompt → complexity-guard（若 score ≥ 3 建议走 fullstack）
       → AI Agent 执行任务
              → PreToolUse: doc-sync-gate 检查
              → Write/Edit 工具执行
              → PostToolUse: spec-validate 校验 spec 格式
              → PostToolUse: auto-test 自动跑测试（阻断）
              → Stop: tasks-integrity 检查 tasks.md
```

## 参考

- [TRAE 官方文档 - Hooks](https://docs.trae.ai/)
- [OODER A2UI 团队实测文章](https://juejin.cn/post/7651167251026853924)（掘金）
