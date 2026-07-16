# 工件职责表 — 一根筋对照

> 每类工件只做一件事。记住这个表，别把 A 的内容写到 B 里。

---

## 内容型工件（承载意图/规格/方案）

| 工件 | 本职工作（只写这个） | 越界（常见污染） |
|------|---------------------|-----------------|
| **proposal.md** | Why + What + Capabilities + Non-Goals | 版本编年史替代 Why 段；30 行 CHANGELOG 占据正文 |
| **spec.md** | BDD 场景 + Invariants + E2E 清单 + Out of Scope | 技术方案细节（那是 design.md）；API 契约正文（那是 contracts/）；tasks 拆分（那是 tasks.md） |
| **prototypes/** | ASCII 低保真原型 + README 索引 | 不用于非 UI 变更；不放高保真设计稿（那是设计工具的事） |
| **contracts/** | API 契约 + 数据模型 + 事件定义 | Review 评分；实现细节；DOC SYNC 时间戳 |
| **design.md** | 技术方案 + 架构决策 + 文档影响清单 | BDD 场景（那是 spec.md）；用户故事（那是 proposal.md）；API 字段明细（那是 contracts/） |

## 追踪型工件（承载进度/状态）

| 工件 | 本职工作（只写这个） | 越界（常见污染） |
|------|---------------------|-----------------|
| **.state-card.md** | 阶段 + 工件进度 + 健康度 + 阻塞 | 决策内容（那是 DECISIONS.md）；bug 描述（那是 buglist.md）；变更说明（那是 proposal.md） |
| **tasks.md** | 可执行任务清单（`[ ]` 条目） | 方案说明（那是 design.md）；验收标准（那是 spec.md） |
| **closure-checklist.md** | Stage 完成状态（`[x]`/`[ ]`） | 闭环描述文字超过一句话（描述放 design.md 或 spec.md） |
| **DECISIONS.md** | 技术决策 + 理由 + 后果 | 任务状态（那是 .state-card.md）；Review 评分 |
| **report-{0X}.md** | 异常描述 + 根因 + 尝试 + 阻塞 | 正常流程总结（那是 Completion Report）；设计讨论（那是 design.md） |
| **buglist.md** | bug 描述 + 严重度 + 状态 | 修复方案（那是 debugger report）；预防措施（那是 retro-spec） |

## 基础设施型工件（跨 change）

| 工件 | 本职工作（只写这个） | 越界（常见污染） |
|------|---------------------|-----------------|
| **modules/{module}.md** | 模块职责 + 接口 + 数据模型 + 依赖 | Review 评分；DOC SYNC 时间戳；实现细节；Bug 修复过程 |
| **.history.md** | change 完工签名（编号 + 决策 + 归档路径） | DOC SYNC 文件清单；Review 逐项评分；测试数 |
| **DOCSMAP.md** | 文档索引（机器管理，不手写） | 不要直接编辑；通过 doc-updater 更新 |

---

## 自检问句

写完任何工件后，对着问：

```
1. 删掉所有越界内容后，本职内容还在吗？
2. 如果有东西应该属于其他工件，我写过一份吗？（没写 → 不管；写了 → 移过去）
3. 这段内容 1 年后还有人需要看吗？（不需要 → 删掉）
```

---

## 追踪型工件最小信息密度

追踪型工件有"不许越界"的禁令，但同样需要"有效"的正向示范。空洞记录 = 浪费上下文。

### report-{0X}.md 最小要求

```
✅ 好的 report:
  ## Problem: spec-writer 产出 BDD 场景缺少 Given 子句（capability: model-import, 场景 3 个）
  ## Attempt: 要求补充 → 新增 2 个 Given 结果："有 3 个 Given 子句了但缺少边界条件"
  ## Blocked: 否，转入 contract-writer 阶段
  ## Evidence: specs/model-import/spec.md#L45-78

❌ 空洞的 report:
  ## Problem: BDD 场景不完整
  ## Attempt: 让他重写了
  ## Blocked: 无
  (6 行，满足 ≤100 行上限，但零信息)
```

### closure-checklist.md 最小要求

每个 `[x]` 必须附带证据引用（文件路径 / diff hash / test run ID），不能只有 `[x] Phase 6 — Code: 已完成`。

格式: `[x] {Stage 名} — 证据: {具体文件路径或 test run ID}`
