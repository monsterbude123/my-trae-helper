# V10.1 Hooks 配置

> TRAE IDE v3.5.66+ 支持 Hooks 功能。Hook 机制在 AI agent 生命周期的关键节点执行自定义 Python 脚本，实现**确定性的自动化执行**。
> V10.1 升级要点：全部 Hook 适配 V10 满分硬门禁 + spec-purge.py archive/out/ 路径。

## 安装

使用技能自带的安装脚本：

```bash
python ~/.trae-cn/skills/fullstack4TraeV10/scripts/install-hooks.py --project-root .
```

或在 TRAE IDE「设置 → Hooks」中手动配置 `hooks.json`。

## 10 个 Hook 覆盖 7 种事件（V10.10 NEW: +GitNexus SessionStart/Stop 双端）

| # | Hook | 事件 | 默认 | 关键能力 |
|---|------|------|:---:|------|
| 1 | **fullstack-gitnexus-session-check** | `SessionStart` | ✅ | **V10.10 新** GitNexus 索引 staleness 检测，HEAD != meta.lastCommit 时后台触发 `gitnexus analyze`（DETACHED_PROCESS + analyze.log），保证本次会话用最新知识图谱 |
| 2 | **fullstack-project-context** | `SessionStart` | ✅ | 6 层知识发现协议注入 + `docs/constitution.md` v10_simplified 检测 + spec-purge 历史感知 + prototypes/ 完整性检查 |
| 3 | **fullstack-complexity-guard** | `UserPromptSubmit` | ❌ | 新增「方向变/重置」(+4) +「UI/UX 重设计」(+3) + code-hygiene.py 调用结果检测 |
| 4 | **fullstack-doc-sync-gate** | `PreToolUse` | ✅ | 写 src/ 前校验 DOC SYNC，`archive/out/spec-purge/` 存在时警告旧状态已归档 |
| 5 | **fullstack-contract-gate** | `PreToolUse` | ✅ | 写代码前检查 contracts/，spec-purge 历史存在时区分「重置缺契约」vs「遗漏」 |
| 6 | **fullstack-spec-validate** | `PostToolUse` | ✅ | Delta Spec 格式（ADDED/MODIFIED/REMOVED）+ 双文档原型（design-prompt.md + ui-ux-logic.md）+ v10_simplified frontmatter 校验 |
| 7 | **fullstack-auto-test** | `PostToolUse` | ✅ | 编码后自动检测 jest/vitest/pytest 并运行 + spec.md `## Acceptance` 段全 [x] 检测 |
| 8 | **fullstack-drift-detect** | `PostToolUse` | ✅ | 契约漂移检测 + spec-purge 历史感知（归档后不再误报缺失端点） |
| 9 | **fullstack-tasks-integrity** | `Stop` | ✅ | 任务完成度检查 + spec-purge 历史上下文（区分全新进行中 vs 正常完成） |
| 10 | **fullstack-gitnexus-session-finalize** | `Stop` | ✅ | **V10.10 新** GitNexus 索引后台刷新：会话结束前若 HEAD != meta.lastCommit 则后台触发 analyze，与 #1 配对使用（写端） |

## 脚本清单（全部 Python，零依赖）

全部 `.py` 脚本部署到 `.trae/hooks/`：

| 脚本 | 关键能力 |
|------|------|
| `gitnexus-session-check.py` | **V10.10 新** SessionStart 端：HEAD vs `.gitnexus/meta.json:lastCommit` 比对 → 过期/缺失则后台触发 analyze（DETACHED_PROCESS + analyze.log）。可关闭：`GITNEXUS_AUTO_ANALYZE=0` |
| `session-start.py` | 6 层知识发现协议（state-card→INDEX→ARCHITECTURE→GitNexus→spec→define）+ `docs/constitution.md` v10_simplified 标记检测 + spec-purge 历史检测 + prototypes 缺失检测与 backfill 路由建议 |
| `complexity-guard.py` | 新增「方向变/重置」信号 (score+4, CRITICAL) +「UI/UX 重设计」信号 (score+3) + code-hygiene.py 调用结果检测 |
| `doc-sync-gate.py` | spec-purge 历史检测 → "旧 DOC SYNC 状态已归档" 警告 |
| `contract-gate.py` | spec-purge 历史检测 → 区分「归档后契约待重建」vs「遗漏 contracts/」 |
| `spec-validate-hook.py` | Delta Spec 格式支持 + 双文档原型（design-prompt.md + ui-ux-logic.md）+ v10_simplified frontmatter 校验 + 移除 L0-L4 旧检查 + 模糊词检测 |
| `auto-test.py` | 增加 spec.md `## Acceptance` 段全 [x] 检测（V10 硬门禁） |
| `drift-detect.py` | spec-purge 历史感知：缺失端点标记为 "ℹ️ (spec-purged — 符合预期)" vs "🔴 契约漂移" |
| `tasks-integrity.py` | spec-purge 历史上下文：`archive/out/spec-purge/` 存在时 [x]/[ ] 比率解读不同（全新进行中 vs 完成度不足） |
| `gitnexus-session-finalize.py` | **V10.10 新** Stop 端：会话结束前若 HEAD != meta.lastCommit 则后台触发 analyze，与 `gitnexus-session-check.py` 配对使用（写端）。跑前检测避免空跑 |

支持脚本（也在 `.trae/hooks/`）：
| `env-init.py` | 环境检测与自动补全（手动运行） |
| `render-cockpit.py` | cockpit 渲染（session-start 自动调用） |
| `log-agent-prompt.py` | Agent prompt 快照记录器 |

## 触发流程

```
SessionStart
  ├─ ① gitnexus-session-check.py：HEAD vs meta.json 比对 → 后台 analyze（如过期）
  └─ ② session-start.py：注入 6 层知识发现协议 + spec-purge 历史检测 + prototypes 完整性
       （注: GitNexus 索引已由 ① 自动后台刷新，无需手动跑）

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
     └── Stop
           ├─ tasks-integrity.py：完成度 + spec-purge 上下文
           └─ gitnexus-session-finalize.py：后台触发 analyze（保证下次会话用最新图谱）
```

## GitNexus 索引管理（V10.10 NEW）

| 端 | Hook | 职责 |
|----|------|------|
| 读（SessionStart） | `gitnexus-session-check.py` | 检测 staleness → 后台刷新 |
| 写（Stop） | `gitnexus-session-finalize.py` | 写新 HEAD → 后台刷新 |

**关键设计**:
- 用 `git rev-parse --show-toplevel` 找逻辑项目根（避免 `.trae` 软链跟随）
- 后台用 `subprocess.Popen + DETACHED_PROCESS + CREATE_NEW_PROCESS_GROUP`（Windows 必须，hook退出后子进程存活）
- 跑前 HEAD 比对：lastCommit == HEAD 时跳过，避免空跑
- `GITNEXUS_AUTO_ANALYZE=0` 关闭（CI/调试场景）
- 日志写 `.gitnexus/analyze.log` 失败可追
- **禁止手动跑 analyze**（与后台 analyze 撞写竞争）

## 自定义

- 修改 `.trae/hooks.json` 中的 `enabled` 字段启用/禁用
- 修改 `matcher` 字段限定触发范围
- 编写自己的 Hook 脚本放在 `.trae/hooks/` 目录下

## 参考

- [TRAE 官方文档 - Hooks](https://docs.trae.ai/)
