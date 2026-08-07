# V10.1 Hooks 配置

> TRAE IDE v3.5.66+ 支持 Hooks 功能。Hook 机制在 AI agent 生命周期的关键节点执行自定义 Python 脚本，实现**确定性的自动化执行**。
> V10.1 升级要点：全部 Hook 适配 V10 满分硬门禁 + spec-purge.py archive/out/ 路径。

## 安装

使用技能自带的安装脚本：

```bash
python ~/.trae-cn/skills/fullstack4TraeV10/scripts/install-hooks.py --project-root .
```

或在 TRAE IDE「设置 → Hooks」中手动配置 `hooks.json`。

## 8 个 Hook 覆盖 5 种事件

| # | Hook | 事件 | 默认 | V10.1 关键能力 |
|---|------|------|:---:|------|
| 1 | **fullstack-project-context** | `SessionStart` | ✅ | 6 层知识发现协议注入 + `docs/constitution.md` v10_simplified 检测 + spec-purge 历史感知 + prototypes/ 完整性检查 |
| 2 | **fullstack-complexity-guard** | `UserPromptSubmit` | ❌ | 新增「方向变/重置」(+4) +「UI/UX 重设计」(+3) + code-hygiene.py 调用结果检测 |
| 3 | **fullstack-doc-sync-gate** | `PreToolUse` | ✅ | 写 src/ 前校验 DOC SYNC，`archive/out/spec-purge/` 存在时警告旧状态已归档 |
| 4 | **fullstack-contract-gate** | `PreToolUse` | ✅ | 写代码前检查 contracts/，spec-purge 历史存在时区分「重置缺契约」vs「遗漏」 |
| 5 | **fullstack-spec-validate** | `PostToolUse` | ✅ | Delta Spec 格式（ADDED/MODIFIED/REMOVED）+ 双文档原型（design-prompt.md + ui-ux-logic.md）+ v10_simplified frontmatter 校验 |
| 6 | **fullstack-auto-test** | `PostToolUse` | ✅ | 编码后自动检测 jest/vitest/pytest 并运行 + spec.md `## Acceptance` 段全 [x] 检测 |
| 7 | **fullstack-drift-detect** | `PostToolUse` | ✅ | 契约漂移检测 + spec-purge 历史感知（归档后不再误报缺失端点） |
| 8 | **fullstack-tasks-integrity** | `Stop` | ✅ | 任务完成度检查 + spec-purge 历史上下文（区分全新进行中 vs 正常完成） |

## 脚本清单（全部 Python，零依赖）

全部 `.py` 脚本部署到 `.trae/hooks/`：

| 脚本 | V10.1 升级点 |
|------|------|
| `session-start.py` | 6 层知识发现协议（state-card→INDEX→ARCHITECTURE→GitNexus→spec→define）+ `docs/constitution.md` v10_simplified 标记检测 + spec-purge 历史检测 + prototypes 缺失检测与 backfill 路由建议 |
| `complexity-guard.py` | 新增「方向变/重置」信号 (score+4, CRITICAL) +「UI/UX 重设计」信号 (score+3) + code-hygiene.py 调用结果检测 |
| `doc-sync-gate.py` | spec-purge 历史检测 → "旧 DOC SYNC 状态已归档" 警告 |
| `contract-gate.py` | spec-purge 历史检测 → 区分「归档后契约待重建」vs「遗漏 contracts/」 |
| `spec-validate-hook.py` | Delta Spec 格式支持 + 双文档原型（design-prompt.md + ui-ux-logic.md）+ v10_simplified frontmatter 校验 + 移除 L0-L4 旧检查 + 模糊词检测 |
| `auto-test.py` | 增加 spec.md `## Acceptance` 段全 [x] 检测（V10 硬门禁） |
| `drift-detect.py` | spec-purge 历史感知：缺失端点标记为 "ℹ️ (spec-purged — 符合预期)" vs "🔴 契约漂移" |
| `tasks-integrity.py` | spec-purge 历史上下文：`archive/out/spec-purge/` 存在时 [x]/[ ] 比率解读不同（全新进行中 vs 完成度不足） |

支持脚本（也在 `.trae/hooks/`）：
| `env-init.py` | 环境检测与自动补全（手动运行） |
| `render-cockpit.py` | cockpit 渲染（session-start 自动调用） |
| `log-agent-prompt.py` | Agent prompt 快照记录器 |

## 触发流程

```
SessionStart → session-start.py
  注入 6 层知识发现协议 + spec-purge 历史检测 + prototypes 完整性

用户 Prompt → complexity-guard.py（若启用）
  含「方向变/重置」→ score+4 CRITICAL
  含「UI/UX 重设计」→ score+3
     ↓
AI Agent 执行任务
     ├── PreToolUse (Write|Edit)
     │     ├── doc-sync-gate.py：DOC SYNC 检查 + spec-purge 感知
     │     └── contract-gate.py：contracts/ 检查 + spec-purge 区分
     ├── PostToolUse
     │     ├── spec-validate-hook.py：Delta Spec + v10_simplified frontmatter + 双文档原型校验
     │     ├── auto-test.py：自动运行测试 + spec.md `## Acceptance` 全 [x] 检测
     │     └── drift-detect.py：漂移检测 + spec-purge 去误报
     └── Stop → tasks-integrity.py：完成度 + spec-purge 上下文
```

## 自定义

- 修改 `.trae/hooks.json` 中的 `enabled` 字段启用/禁用
- 修改 `matcher` 字段限定触发范围
- 编写自己的 Hook 脚本放在 `.trae/hooks/` 目录下

## 参考

- [TRAE 官方文档 - Hooks](https://docs.trae.ai/)
