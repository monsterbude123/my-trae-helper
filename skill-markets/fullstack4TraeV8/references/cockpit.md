# Cockpit 驾驶舱（V7 NEW）

> 解决"Agent 假性完成 + 用户看不出进度 + spec 爆炸性增长"三大痛点。

---

## 设计动机

来自实战教训：

- **假性完成**：Agent 中途停止，state-card 显示 ✅ 但实际无产出。用户看不出问题，以为做完了。
- **Spec 爆炸**：用户在不同会话提类似需求，不同 Agent 建了 50+ 个 change，多数是重复的半成品。
- **重入困难**：用户断连后重新连接，Agent 不知道"上次做到哪了"，从头推理浪费 token。

Cockpit 通过**双层状态卡**和**新会话自检**解决这三个问题。

---

## 双层状态卡架构

```
docs/specs/.state-card.md          # 项目级 Cockpit：全局视图
docs/specs/changes/{change}/.state-card.md  # per-change：单变更视图
```

### 项目级 Cockpit

**内容**：所有活跃 change 的概况（各自阶段、最后活动时间、阻塞项）+ 项目级工件状态。

**更新者**：主 Agent，在阶段切换时更新。doc-updater 在同步项目级工件后更新对应条目。

**格式**：

```markdown
# 🛩️ 项目驾驶舱

## 活跃变更
| # | Change | 阶段 | 状态 | 最后活动 | 阻塞 |
|---|--------|------|------|---------|------|
| 01 | user-auth | design | 🟡 | 10min ago | 无 |
| 02 | payment | spec | 🟢 | 2h ago | 等待用户确认 |

## 健康概览
- **活跃 change 数**: 2
- **阻塞 change 数**: 1
- **Spec 堆积风险**: 🟢 低（< 3）/ 🟡 中（3-5）/ 🔴 高（> 5）
- **最近完成**: change-00-init（2026-06-28）

## 项目级工件
- modules/: ✅ 最新 / ⚠️ 待同步
- prototypes/: ✅ 最新 / ⚠️ 待同步 / — 未初始化
- test-plan/: ✅ 已定义 / ⚠️ 待更新 / — 未初始化
- ARCHITECTURE.md: ✅ 最新 / ⚠️ 待更新
- contracts/: ✅ 最新 / ⚠️ 待同步
- integration-manuals/: ✅ 最新 / ⚠️ 待生成 / — 暂无基石模块
```

## 🐛 活跃缺陷段（V8 NEW — 预警信号直入驾驶舱）

Intake 在 Bug-Batch Phase B.1 创建 buglist 时，同步更新 Cockpit 的此段。
Doc-updater 在 Retro-Spec 完成时清除已修复的 bug 条目。

```markdown
## 🐛 活跃缺陷
| # | Bug | 关联模块 | 严重度 | 状态 | 用户反馈 | 发现时间 |
|---|-----|---------|:---:|------|---------|---------|
| B1 | 登录超时未重试 | auth | 🔴 P0 | 🔍 调查中 | 超时后偶现 | 2026-07-10 |
| B2 | 列表分页偏移错误 | list | 🟡 P2 | ✅ 已修复 | — | 2026-07-09 |
```

- P0: 阻塞核心流程，需立即修复
- P1: 影响用户体验，应在当前迭代修复
- P2: 边缘情况，可排入 backlog

### 新会话重入协议（V9 NEW）

> buglist 是用户与 Agent 跨会话的**反馈交流媒介**。Agent 在任何新窗口/新会话中，
> 必须先读 Cockpit → 发现 🐛段 → 加载 buglist.md 完整内容 → 恢复交流上下文。

```
任意会话启动
    ↓
intake 步骤 0: 读 Cockpit
    ↓
发现 🐛段有 P0/P1（状态 ≠ ✅已修复）
    ↓
步骤 0.05: 提示用户 "有 N 个未解决 bug，是否先处理？"
    │
    ├── 是 → 读 buglist.md 完整内容
    │     → 输出: "Bug B{N} 当前状态 + 上次交流摘要"
    │     → 用户选择: 继续调查 / 更新反馈 / 标记已修复
    │
    └── 否 → 继续新需求 → but bug 信号保留在 Cockpit
```

**反馈交流机制**：
- 用户在对话中说 "这个 bug 应该是 XX 原因" → Agent 写入 buglist.md 的"用户反馈"列 + 交流历史
- 用户说 "修复的不对，应该..." → Agent 标记状态回退 🔍 + 追加交流历史
- 所有反馈变更 → 同步写 Cockpit 🐛段（更新"状态"和"用户反馈"列）
- 详细对话历史 → 仅存 buglist.md（不在 Cockpit 中展开，避免 Cockpit 膨胀）

**Spec 堆积风险阈值**：
- 🟢 < 3 个活跃 → 健康
- 🟡 3-5 个活跃 → 警告，建议整合
- 🔴 > 5 个活跃 → 危险，强制 30% 重叠检查并合并

### per-change 状态卡（≤ 30 行）

**内容**：单 change 的工件进度、健康度、下一步、阻塞项。

**V7 新增字段 `最后产出时间`**：Agent 每次更新状态卡时记录当前时间。新会话自检时，如果最后产出时间 > 30 分钟且无新文件产出 → 标记为 🛑 疑似假性完成。

---

## 新会话自检流程（STATE CARD ALWAYS HONEST）

```
Agent 在新会话激活时，执行自检：

1. 读项目级 Cockpit
   → 输出全局状态快照

2. 文档索引新鲜度检测（V8 NEW）
   → python build-index.py --git-diff          ← 推荐：Git diff，自动提示 DOC SYNC 缺口
   → 回退 python build-index.py --diff         ← 轻量：mtime 检测
   → 文档索引不存在 → 🛑 提示先初始化索引
   → 无变化 → 跳过文档审计
   → 有 MODIFIED/DELETED → 标记 ⚠️ 文档过时，触发 DOC SYNC
   → ⚠️ DOC SYNC 缺口提示 → 触发 DOC SYNC

3. 对 Cockpit 中每个活跃 change：
   a. 读其 .state-card.md
   b. 对照文件系统验证每个工件的实际状态
   c. 如果 state-card 声称 ✅ 但文件不存在/为空
      → 标记 ⚠️ 状态失真
      → 回溯到上一个真实状态
   d. 如果最后产出时间 > 30 分钟
      → 检查这期间是否有新文件产出
      → 如果没有 → 🛑 疑似假性完成，询问用户

4. V8 增强：内容级交叉验证（不只是文件存在）
   a. 如果 Cockpit 声称 modules/: ✅ 最新
      → 抽样检查模块文档中的关键数据（能力列表/数据模型/状态机）
      → 与 per-change 最新契约/代码对比
      → 不一致 → 标记 ⚠️ 过时，触发 DOC SYNC
   b. 扫描项目级持久化文档是否引用 docs/specs/changes/ 路径
      → 发现引用 → 标记 🔴 违反铁律#6，触发 doc-updater 修复
   c. 验证 DOC SYNC 审计段是否存在
      → per-change state-card 缺少 "文档同步度" 段落 → 标记 ⚠️ 模板不完整

5. 如果 Cockpit 本身不存在
   → 说明项目尚未初始化全栈工作区
   → 引导用户初始化
```

---

## 状态卡生命周期

```
intake 创建 → 各 Agent 更新 → change 完成 → doc-updater 归档 → Cockpit 移除
```

- 创建：intake 步骤 4
- 更新：每个 Agent 激活时更新状态卡中的工件进度 + 最后产出时间
- 阶段切换：更新阶段号 + 阶段名
- 漂移修复：更新健康度
- 完成归档：doc-updater 从 Cockpit 移除 + 移动到 archive/done/
- 淘汰归档：doc-updater 从 Cockpit 移除 + 移动到 archive/out/

---

## 与 SKILL.md 的集成

SKILL.md 中的执行原则 3-4：

```
3. Cockpit 先读取：Agent 激活时先输出项目级 Cockpit
4. 状态卡永真：新会话必须自检文件系统 vs 状态卡声称的状态
```

---

## 参考模板

- 项目级 Cockpit：`templates/cockpit-state-card.md`
- per-change 状态卡：`templates/state-card.md`

---

## 脚本驱动渲染（V7.1 NEW）

> 驾驶舱的输出不由 LLM 生成，而是由脚本 `render-cockpit.ps1` 渲染。保证格式一致、内容可靠、0 token 浪费。

### 三个核心脚本

| 脚本 | 路径 | 用途 |
|------|------|------|
| **render-cockpit.py** | `templates/scripts/render-cockpit.py` | 读取状态卡 -> 渲染 Markdown 驾驶舱 |
| **log-agent-prompt.py** | `templates/scripts/log-agent-prompt.py` | 子 Agent 启动时落盘提示词到 `./llm-prompts/` |
| **env-init.py** | `templates/scripts/env-init.py` | 环境检测 + 自动补全 hook/脚本/配置 |

### render-cockpit.py 渲染内容

```
🛩️ V7 驾驶舱
├── 活跃变更表（阶段 + Agent + 状态 + 阻塞）
├── 健康概览
├── 流水线进度（当前阶段 **[标注]**）
├── per-change 详情（阶段/Agent/提示词/下一步/阻塞）
│   ├── 工件进度
│   ├── 活跃文件引用
│   └── 健康度
├── 最近 Agent 调用（来自 llm-prompts/INDEX.md）
└── 项目级工件状态
```

### log-agent-prompt.py 机制

```
主 Agent 启动子 Agent 时：
  → 调用 log-agent-prompt.py --agent-name "spec-writer" --prompt "..." --change "user-auth"
  → 落盘 ./llm-prompts/2026-06-29-143000-spec-writer.md
  → 更新 ./llm-prompts/INDEX.md
  → 重入时可通过 INDEX.md 回溯"上次 spec-writer 收到了什么"
```

### env-init.py 检测项

```
目录: docs/specs, modules, prototypes, test-plan, CODEMAPS, contracts, archive/out, archive/done
配置: config.yaml, .state-card.md
Hooks: .trae/hooks.json + 8 个 .ps1 脚本
脚本: scripts/debug/
快照: llm-prompts/
```

运行 `python env-init.py --fix` 自动补全缺失项。

---

## 附录：Intake Agent 专用快照模板（精简版）

> intake Agent 步骤 0 读取 Cockpit 后输出的对话快照格式：

```markdown
# 🛩️ Cockpit 快照

## 当前全局状态
- **活跃 change**: {N} 个
- **阻塞 change**: {N} 个
- **Spec 堆积风险**: 🟢/🟡/🔴

## 已有 change 列表
| # | Change | 阶段 | 阻断 |
|---|--------|------|------|
| 01 | xxx | spec | 无 |

## 🐛 活跃缺陷
| # | Bug | 关联模块 | 严重度 | 状态 |
|---|-----|---------|:---:|------|
| — | 无活跃缺陷 | — | — | — |
```

> ⚠️ Bug 优先原则：如果 🐛段有未解决的 P0/P1 bug，在输出快照后立即执行步骤 0.05 Bug 信号检查。
