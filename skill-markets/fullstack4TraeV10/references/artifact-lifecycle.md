# 工件生命周期

> 文档分层 + 文件体积约束 + 状态卡重置规则。

---

## 文档分层标签（V10.6 — 子代理可机械判定）

> 根因：历史档案/changelog/fix_result 等"过程文档"被当"事实文档"喂给子代理，
> 导致上下文噪音淹没、旧 agent 错误判断成为幻觉种子。
> 治理：显式 `layer:` 标签，子代理按层判定"现在能不能读"。

| layer | 含义 | 典型文档 | 子代理任务执行时 | 复盘时 |
|:-----:|------|---------|:---------------:|:-----:|
| `fact` | 项目真相源 | contracts/、spec.md、ARCHITECTURE.md、模块文档、AGENTS.md | **必读** | 必读 |
| `process` | 过程产物 | diagnose.md、fix_result.md、分析手记、v1v2v3 修复记录、evidence JSON | **禁读** | 可读 |
| `log` | 操作日志 | changelog、commit log、state-card 历史、review 报告 | **不作验收依据** | 可读 |

### 判定规则（子代理执行）

```
子代理启动时:
  1. 主上下文在委派 prompt 中注入 [DOC_WHITELIST]（路径前缀列表）
  2. 子代理只能读白名单内的文件
  3. 白名单只含 layer=fact 的文档
  4. layer=process/log 的文档:
     - 子代理不主动遍历、不主动读
     - 主上下文从中提取"事实摘要"（≤5 行）注入到委派 prompt
     - 子代理拿到的永远是"过滤后的事实点"，不是"历史文件路径"
```

### 分层标签示例

文档头部 YAML frontmatter 加 `layer` 字段：
```yaml
---
layer: fact     # 事实文档 — 任务执行时必读
---
```

无 `layer` 字段的文档默认 `layer: process`（保守策略，防止噪音泄漏）。

### spec 领域 layer 分配（V10.6）

| 文件 | layer | 说明 |
|------|:-----:|------|
| `plan.md` | fact | 意向声明（Why + Capabilities + Impact） |
| `define.md` | fact | 意向边界（Non-Goals + Out of Scope） |
| `spec.md` | fact | 行为规格 + 验收标准 |
| `design.md` | fact | 技术方案 + 架构决策 |
| `contracts/*.md` | fact | 接口契约 + 领域模型 |
| `tasks.md` | fact | 当前实现清单（checkbox） |
| `prototypes/*` | fact | UI 视觉原型 |
| `.state-card.md` | process | 状态快照（阶段性，非真相源） |
| `_invalidated/` | process | 回流隔离旧产物 |
| `docs/reports/review-*.md` | log | 审查报告 |
| `docs/bugs/` | process | Bug 修复记录 |
| `changelog` / `commit log` | log | 操作日志 |

### 目录 layer 映射表（V10.8 NEW — 补全缺漏目录）

> 根因：spec 领域 layer 分配表已覆盖 spec.md/design.md 等，但 docs/ 下多个目录无明文 layer
> → 子代理无法机械判定 → 索引器误扫描（见 doc-sync.md §索引器范围）。
> 治理：补全所有 docs/ 子目录的 layer 标注，无 layer 字段默认 process（保守策略）。

| 目录/文件 | layer | 说明 |
|----------|:-----:|------|
| `docs/api-endpoints/` | fact | API 端点契约（spec-knowledge-extract 产物） |
| `docs/domain-models/` | fact | 领域模型（spec-knowledge-extract 产物） |
| `docs/events/` | fact | 事件定义（spec-knowledge-extract 产物） |
| `docs/contracts/`、`docs/modules/` | fact | 接口契约 / 模块职责 |
| `docs/ARCHITECTURE.md`、`AGENTS.md` | fact | 架构地图 / agent 入口 |
| `docs/history/`、`.history.md` | log | 完工签名薄（Append-Only，见下文 §.history.md） |
| `docs/DECISIONS.md` | process | 决策过程记录 |
| `docs/bugs/` | process | Bug 修复记录 |
| `docs/reports/` | log | Review 报告 |
| `docs/archive/`、`docs/specs/archive/` | log | 归档不可变 |
| `_invalidated/` | process | 回流隔离旧产物（见下文 §物理隔离） |
| `diagnostic/` | process | 诊断手记 |

无 `layer` frontmatter 字段的文档默认 `layer: process`（保守策略，防止噪音泄漏）。

---

## 体积硬上限

| 文件类型 | 上限 | 超出动作 |
|---------|:---:|---------|
| 单源码文件 | 800 行 | 拆分为多文件 |
| 状态卡 (.state-card.md) | 80 行 | 执行重置（从模板重建） |
| Spec 文件 | 200 行 | 拆分为父文件 + 子文件 |
| define.md | 80 行 | 精简 Non-Goals + Out of Scope |
| Contract 单文件 | 200 行 | 拆分为子契约 |

---

## 状态卡四态重置

```
正常 (< 80 行) → 继续使用
接近上限 (70-80 行) → 修剪历史记录
超标 (> 80 行) → 重置：从模板重建，保留 phase/health/blocked
```

---

## 禁止写入状态卡的内容

- 实现细节（放代码注释）
- Review 评分（放审查报告）
- DOC SYNC 时间戳（放 git log）
- Bug 修复过程（放 commit message）

---

## 文档治理原则

- 修剪/迁移文档时，操作前编目事实 → 操作后逐项验证 → 缺失 = 回退
- `archive/` 目录下文件不可修改（归档 = 只读）
- 过程文档（layer=process）不进 `contracts/` 或 `specs/changes/`，放 `docs/bugs/` 或 `docs/reports/`

---

## Single Source of Truth（V10.6）

- 每个知识点只在 1 个文件出现，其他文件只放指针 + 摘要
- state-card.md 是版本号/健康度的唯一权威源，其他文档只引用 state-card 的版本号 + 章节链接
- 禁止在 spec.md / design.md / tasks.md 之间复制粘贴同一段内容

## 事实块沉淀（V10.6）

- MCP 抓取的事实（GitNexus context / Chrome DevTools network / 抽帧数据）必须作为完整段落写进 reference 文件
- 同一 session 内不重复跑同一 MCP 分析——已沉淀的事实直接 Read
- reference 文件 layer: fact，任务执行时可读

---

## .history.md Append-Only 设计规范（V10.8 NEW）

> 根因：.history.md 被 Read 全文（31KB）→ 击穿上下文；被每次 DOC SYNC 写一条 → 文件膨胀。
> 治理：Append-Only 写入 + 禁止 Read 全文 + 顶部索引表 ≤20 行。

### 写入规则

```
1. 一个 change 一生只写一次（Phase 9 Archive 归档时，非每次 DOC SYNC）
2. Add-Content 直接追加，禁止 Read 全文再 Write
3. 单条记录 ≤ 50 行（header + 结果 + 关键决策 ≤3 条 + 归档路径 + 对 agent 的意义 ≤2 行）
4. 顶部索引表 ≤20 行，超出归档最旧 10 条到 archive/history/
```

### 使用规则

| 场景 | 正确操作 | 禁止操作 |
|------|---------|---------|
| "这个 change 做完了吗？" | `grep "NN-name" .history.md` | `Get-Content .history.md` |
| "NN 的决定是什么？" | `grep "NN-name" .history.md` | `Select -Last 50` |
| 写新条目 | `Add-Content -Path .history.md -Value "..."` | `Get-Content → 修改 → Set-Content` |

### 反例

- 现象：doc-updater 用 Read→Modify→Write 更新 .history.md → 31KB 击穿上下文；每个 DOC SYNC 写一条 → 文件膨胀
- 根因：未规定 Append-Only，未规定"一次 change 一条"
- 教训：.history.md = 完工签名薄，Append-Only 写入，禁止 Read 全文

---

## 物理隔离机制（V10.8 NEW — V4+ 重做）

> 根因：change V1-V3 漂移后只重置状态卡未物理隔离旧产物 → implementer glob 捞出大量文件多数是旧产物 → 上下文爆炸。
> 治理：V4+ 重做时必须物理隔离旧产物，不能只重置状态卡。

### 四步流程

```
1. 编目旧产物: ls specs/changes/{NN}/ → 列出 V1-V3 所有文件
2. 创建隔离目录: mkdir _invalidated/v{N}/
3. 移动旧产物: mv specs/changes/{NN}/* → _invalidated/v{N}/
4. 写 REFACTOR_MODE.md: 说明本次重做范围 + 禁止读 _invalidated/
```

### 委派注入声明

```
委派 implementer 时必须注入:
  [DOC_WHITELIST] 禁止读 _invalidated/ 目录
  违反 = 🛑 REJECT
```

### 反例

- 现象：某 change V1-V3 漂移，只重置状态卡未物理隔离 → implementer glob 捞出 38 个文件 30 个是旧产物 → 上下文爆炸
- 根因：只重置状态卡，未物理隔离旧产物，旧产物仍在 specs/changes/{NN}/
- 教训：V4+ 重做必须物理隔离到 _invalidated/v{N}/，不能只重置状态卡
- 来源：absorption-plan §七（物理隔离机制 V4+ 重做）

---

## §Change Lifecycle Ops 速查（V10.8 NEW — 回流自 change-lifecycle-ops）

> 22 个生命周期操作点中的通用项速查（去项目特定端口/路径）。触发：归档/拆分/诊断/验证/完成审计/委派并行。

### [NOW]/[BLOCKED] 任务拆分 / subagent 工具集诊断 / schema 漂移修复

```
[NOW]/[BLOCKED] 拆分: Plan 有外部依赖时 → [NOW]≥70% 立即执行 / [BLOCKED-XX]≤30% 等 Accept
  实施: 先委派 [NOW] 批 → 等 Accept → 委派 [BLOCKED] 批 → 两批完成 → reviewer

subagent 工具集诊断（implementer 失败 ≥2 次）:
  Step 1: 检查 agent 定义 tools 字段 → Step 2: 检查 MCP 状态 ≥1 🟢
  Step 3: 切换工作区模式 → Step 4: 重启 IDE → Step 5: 清理会话状态
  验证: 委派最小任务（5 任务而非 45），确认工具集报告正常

schema 漂移修复: 触发=归档时 contracts/schema 与 migrations/*.sql 不一致
  Step 1: grep CREATE TABLE/ALTER TABLE 对比 → Step 2: 补齐缺失列
  Step 3: 补齐缺失索引（CREATE UNIQUE INDEX IF NOT EXISTS）
  Step 4: grep 验证列名 ≥3 命中（列定义 + 索引 + 引用）
```

### dev service 启动 / Bug 调研 / 完成审计 / 委派并行 / Review 遗漏

```
dev service 联通验证（必须按顺序）:
  1. 后端 API 直接测试（curl 后端端口，不通过前端代理）
  2. 前端调用链追踪（Read api-client / proxy 配置）
  3. 浏览器实测（截图 UI + 检查控制台 API 请求域）
  禁止: 用前端域测试后端 API；只看代码不验证运行时；忽略控制台错误

Bug 调研三阶段（已归档模块/模糊反馈）:
  Phase 0: 驾驶舱定位 → 读状态卡 + 确认阶段 + 识别涉及模块
  Phase 1: 代码分析 → GitNexus query/context/impact + 验证代码存在
  Phase 2: 浏览器实测 → 打开应用 + 截图 + 检查控制台
  根因定位: API 正常+浏览器异常 → 前端调用链；API 异常 → 启动服务
  归档后缺陷 → 创建新 change 走流水线（禁止解封 archive/）

完成审计（commit 前）: P0 bug=端点崩溃 → 🛑 先修；P1=schema 不一致 → 修后 commit
  检查: 全 pass + 文档一致（状态卡 vs 评分卡 vs 报告）
  严格区分: "L{N} 范围内修复完成" ≠ "模块整体可交付"

委派并行: 无依赖 → 并行（doc-updater + implementer）；有依赖 → 串行（implementer → reviewer）
  禁止: 无依赖串行（浪费时间）；有依赖并行（导致失败）

Review 后端验证遗漏: spec 含 API/DB/服务 → 必须审后端源码
  define.md Capabilities 必须覆盖 spec.md 所有后端需求
  状态卡"已完成" → 验证链条完整（contracts/ + 评分卡 + 主 spec 合并）
```

> 来源: example/test-fullstack-init 会话蒸馏，V10.8 通用化回流（去 22 项中的项目特定操作，保留 7 类通用操作点）
