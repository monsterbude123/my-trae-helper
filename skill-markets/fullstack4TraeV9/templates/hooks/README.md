# V9.2 Hooks 配置

> TRAE IDE v3.5.66+ 支持 Hooks 功能。Hook 机制在 AI agent 生命周期的关键节点执行自定义 Python 脚本，实现**确定性的自动化执行**。
> V9.2 升级要点：全部 .ps1→.py 迁移 + `_invalidated_/` 干净重置感知 + 6 层知识发现协议 + Delta Spec 支持 + 双文档原型校验。

## 安装

使用技能自带的安装脚本：

```bash
python ~/.trae-cn/skills/fullstack4TraeV9/scripts/install-hooks.py --project-root .
```

或在 TRAE IDE「设置 → Hooks」中手动配置 `hooks.json`。

## 8 个 Hook 覆盖 5 种事件

| # | Hook | 事件 | 默认 | V9.2 关键能力 |
|---|------|------|:---:|------|
| 1 | **fullstack-project-context** | `SessionStart` | ✅ | 6 层知识发现协议注入 + `_invalidated_/` 检测 + prototypes/ 完整性检查 |
| 2 | **fullstack-complexity-guard** | `UserPromptSubmit` | ❌ | 新增「方向变/重置」(+4) +「UI/UX 重设计」(+3) 信号 |
| 3 | **fullstack-doc-sync-gate** | `PreToolUse` | ✅ | 写 src/ 前校验 DOC SYNC，`_invalidated_/` 存在时警告旧状态已死 |
| 4 | **fullstack-contract-gate** | `PreToolUse` | ✅ | 写代码前检查 contracts/，`_invalidated_/` 存在时区分「重置缺契约」vs「遗漏」 |
| 5 | **fullstack-spec-validate** | `PostToolUse` | ✅ | Delta Spec 格式（ADDED/MODIFIED/REMOVED）+ 双文档原型（design-prompt.md + ui-ux-logic.md）校验 |
| 6 | **fullstack-auto-test** | `PostToolUse` | ✅ | 编码后自动检测 jest/vitest/pytest 并运行（无变化） |
| 7 | **fullstack-drift-detect** | `PostToolUse` | ✅ | 契约漂移检测 + `_invalidated_/` 感知（干净重置后不再误报缺失端点） |
| 8 | **fullstack-tasks-integrity** | `Stop` | ✅ | 任务完成度检查 + 干净重置上下文（区分全新进行中 vs 正常完成） |

## 脚本清单（全部 Python，零依赖）

全部 `.py` 脚本部署到 `.trae/hooks/`：

| 脚本 | V9.2 升级点 |
|------|------|
| `session-start.py` | 6 层知识发现协议（state-card→INDEX→ARCHITECTURE→GitNexus→spec→define）+ `_invalidated_/` 检测 + prototypes 缺失检测与 backfill 路由建议 |
| `complexity-guard.py` | 新增「方向变/重置」信号 (score+4, CRITICAL) +「UI/UX 重设计」信号 (score+3) |
| `doc-sync-gate.py` | `_invalidated_/` 检测 → "旧 DOC SYNC 状态已死" 警告 |
| `contract-gate.py` | `_invalidated_/` 检测 → 区分「干净重置后契约待重建」vs「遗漏 contracts/」 |
| `spec-validate-hook.py` | Delta Spec 格式支持 + 双文档原型（design-prompt.md + ui-ux-logic.md）+ 移除 L0-L4 旧检查 + 模糊词检测 |
| `auto-test.py` | 无变化（已足够通用） |
| `drift-detect.py` | `_invalidated_/` 感知：缺失端点标记为 "ℹ️ (干净重置 — 符合预期)" vs "🔴 契约漂移" |
| `tasks-integrity.py` | 干净重置上下文：`_invalidated_/` 存在时 [x]/[ ] 比率解读不同（全新进行中 vs 完成度不足） |

支持脚本（也在 `.trae/hooks/`）：
| `env-init.py` | 环境检测与自动补全（手动运行） |
| `render-cockpit.py` | cockpit 渲染（session-start 自动调用） |
| `log-agent-prompt.py` | Agent prompt 快照记录器 |

## 触发流程

```
SessionStart → session-start.py
  注入 6 层知识发现协议 + _invalidated_ 检测 + prototypes 完整性

用户 Prompt → complexity-guard.py（若启用）
  含「方向变/重置」→ score+4 CRITICAL
  含「UI/UX 重设计」→ score+3
     ↓
AI Agent 执行任务
     ├── PreToolUse (Write|Edit)
     │     ├── doc-sync-gate.py：DOC SYNC 检查 + _invalidated_ 感知
     │     └── contract-gate.py：contracts/ 检查 + 干净重置区分
     ├── PostToolUse
     │     ├── spec-validate-hook.py：Delta Spec + 双文档原型校验
     │     ├── auto-test.py：自动运行测试
     │     └── drift-detect.py：漂移检测 + _invalidated_ 去误报
     └── Stop → tasks-integrity.py：完成度 + 干净重置上下文
```

## 自定义

- 修改 `.trae/hooks.json` 中的 `enabled` 字段启用/禁用
- 修改 `matcher` 字段限定触发范围
- 编写自己的 Hook 脚本放在 `.trae/hooks/` 目录下

## 参考

- [TRAE 官方文档 - Hooks](https://docs.trae.ai/)
