# 经验沉淀路由 (.learnings / LEARNING / ERROR)

> **定位**：本文件是仓库内经验沉淀的**路由决策表**，规定"什么经验写哪里"，避免与全局 `self-improving-agent` 重复维护。
>
>
> **决策生效日**：2026-08-14（会话蒸馏结论）

---

## §1 永久决策

| 决策项 | 结论 | 依据 |
|--------|------|------|
| 仓库内 `.learnings/` 目录 | **不建** | 全局 `self-improving-agent` 已覆盖同类能力 |
| 仓库内反例 / 修复指令 | 写到 `skill-markets/<pkg>/references/trap-instructions.yaml` | 仓库内自包含 + 程序可断言 |
| 跨会话经验 / 命令失败 / 用户反馈 | 写入全局 `self-improving-agent` 的 `LEARNING/ERROR/FEATURE_REQUESTS` | 用户全局已装，避免双源 |
| 临时 pytest hint | 写入 `logs/agent-hints.jsonl` | conftest 可清空，非持久经验 |
| 版本变更 | 写入 `CHANGELOG.md` | 语义化版本日志 |

> ⚠️ **权威源**：跨会话经验以**全局 `self-improving-agent`** 为唯一权威源，仓库内任何反例不得复制粘贴全局内容。

---

## §2 路由表（场景 → 目的地）

| 场景 | 目的地 | 备注 |
|------|--------|------|
| 反例 / 修复指令 / 字段映射 | `skill-markets/<pkg>/references/trap-instructions.yaml` | 字段刻意避开全局 schema 命名 |
| 跨会话经验 / 命令失败 / 用户反馈 | 全局 `self-improving-agent` | LEARNING / ERROR / FEATURE_REQUESTS |
| 运行时 pytest 失败 hint | `logs/agent-hints.jsonl` | 临时，conftest 可清空 |
| 版本变更 | `CHANGELOG.md` | 语义化版本 |
| 安全审计报告 | `SECURITY-MAP.md` | 量化评分已存在 |
| 能力去重 / 共享脚本索引 | `skill-markets/CAPABILITY-MAP.md` | 加新脚本前必查 |

---

## §3 字段命名铁律

`trap-instructions.yaml` 的字段**不得**用全局 `self-improving-agent` 的 schema 命名，避免冲突：

| ❌ 不用（全局 schema） | ✅ 用（仓库内 trap） | 备注 |
|----------------------|---------------------|------|
| `Logged` | （无对应） | 经验走全局，不需时间戳 |
| `Priority` | `severity` | 已在用 |
| `Status` | （无对应） | trap 是静态声明，无 lifecycle |
| `Reproducible` | `what_is_wrong` + `detect_signal` | 组合表达 |
| `Related Files` | `see_also` | 文本引用 |
| `Source` | （无对应） | 来源用全局 |

---

## §4 反例新增流程

```
仓库内反例（"程序可断言"）
  → 写到 skill-markets/<pkg>/references/trap-instructions.yaml
  → 同时 pytest trap 测试用本文件校验字段

跨会话经验（"用户反馈 / 命令失败 / 流程决策"）
  → 写到全局 self-improving-agent
  → 不复制进仓库
```

两者**不重复**，以全局为权威源。

---

## §5 让 agent **自动**调用 self-improving-agent

> 这是本次润色重点。Trae 体系下，agent 启动 = `Skill(name="project-rule-skill")` 第一动作。本节规定经验沉淀如何**自动**贯穿会话。

### 5.1 三阶段触发点

| 阶段 | 触发条件 | 自动动作 | 写入位置 |
|------|----------|----------|----------|
| **会话启动** | 任意任务开始 | `Skill(name="self-improving-agent")` 注入会话级 hint（只读加载，不写盘） | 仅上下文，不写盘 |
| **会话中（错误）** | 工具调用失败 / 守卫阻断 / 用户纠正 | 自动 append `ERROR` 条目 | 全局 LEARNING/ERROR |
| **会话结束** | 任务完成 / 用户表态"完成" / 失败上报 | 自动 append `LEARNING` + 可选 `FEATURE_REQUESTS` | 全局 LEARNING/ERROR/FEATURE_REQUESTS |

### 5.2 自动化路径（4 选 1，按落地难度升序）

#### 路径 A：project-rule-skill 网关注入（**推荐**）

**原理**：在 `project-rule-skill` 的 §1 Step 1 之后增加 Step 1.5，强制加载 `self-improving-agent`。

```yaml
# .agents/skills/project-rule-skill/SKILL.md §1 新增
Step 1.5 — 加载经验沉淀 skill
  → Skill(name="self-improving-agent")   # 注入经验上下文
  → 失败也不阻断会话（不致命）
  → 输出 loaded_skills += ["self-improving-agent"]
```

**优点**：复用现有强制协议，零侵入。
**缺点**：依赖用户机器已装 self-improving-agent；未装则降级为 skip。

#### 路径 B：Trae IDE 钩子（Hook 机制）

**原理**：配置 Trae 会话生命周期钩子（`session-start` / `session-end`），分别触发 `self-improving-agent`。

```jsonc
// .trae/hooks/session.json   (本地钩子配置 — 不提交)
{
  "session-start":  ["self-improving-agent load"],
  "session-end":    ["self-improving-agent reflect --auto"]
}
```

**优点**：宿主级自动化，与具体 skill 解耦。
**缺点**：依赖 Trae IDE 版本支持；当前版本未确认。

#### 路径 C：自检脚本（CI / Gate 层）

**原理**：在 `.husky/post-commit` / GitHub Actions 跑 `self-improving-agent reflect`，把上一会话未持久化的经验落盘。

```bash
# .husky/post-commit
self-improving-agent reflect --since last-commit --auto
```

**优点**：不依赖会话内行为，靠 Git 钩子兜底。
**缺点**：会延迟一拍（commit 之后才落盘），不适合"实时纠正"。

#### 路径 D：MCP Server 形式

**原理**：把 self-improving-agent 暴露成 MCP 工具，主 agent 在每次工具失败时自动调用 `log_error` / `log_learning`。

```yaml
# .trae/mcp.json   (本地 MCP 配置 — 不提交)
{ "self-improving-agent": { "command": "...", "auto_invoke_on_error": true } }
```

**优点**：最自动化，但 MCP 宿主支持度参差。

### 5.3 推荐组合

```
路径 A（启动注入） + 路径 C（commit 兜底） = 零侵入 + 必兜底
```

- **A** 解决"会话中实时调用"
- **C** 解决"会话结束经验可能丢失"

路径 B/D 待 Trae 宿主能力升级后再启用。

### 5.4 失败降级

```
MUST: self-improving-agent 不可用时
  → 不阻断会话
  → 在响应开头标注: "[learning-skip] self-improving-agent 未加载,本次经验未沉淀"
  → 用户全局装好后自动恢复
```

### 5.5 不自动沉淀的内容

| 内容 | 不沉淀原因 |
|------|-----------|
| 临时调试日志 | `logs/` 已存 |
| 一次性命令输出 | 无复用价值 |
| 用户明确说"别记这个" | 用户意图优先 |
| 涉及密钥 / PII | 安全红线 |

---

## §6 何时复核本决策

| 触发 | 复核项 |
|------|--------|
| 用户升级 `self-improving-agent` 改变能力边界 | 重新评估 §1 决策 + §5 自动路径 |
| 用户新增 skill 且必然需要仓库内 `.learnings/`（如 audit 报告） | 解除 §1 "不建" 决策 |
| 用户明确给出 `.learnings/` 应建指令 | 同上 |
| Trae IDE 钩子机制稳定 | 启用路径 B |

---

## §7 与 AGENTS.md 引用对齐

AGENTS.md §1.4 引用路径 `.trae/rules/learning.md`（单数）已迁移到 `.agents/rules/learning.md`。**已对齐**：

```
✓ AGENTS.md §1.4 引用 .agents/rules/learning.md
✓ 本文件位于 .agents/rules/learning.md
```
