# 工件生命周期协议（Artifact Lifecycle）

> **核心铁律**：每个工件有体积硬上限。达到上限不追加——执行重置。回流 = 旧版隔离 + 新版重置。
> **根因**：状态卡、DECISIONS、report、buglist 等累积型工件无上限无重置，多次回流/反馈后膨胀至不可用。

---

## §1 累积型工件全景

```
docs/changes/{id}/
  ├── .state-card.md         # 每次阶段切换追加 → 膨胀
  ├── tasks.md               # 回流时 planner 重写（✅ 已处理）
  ├── DECISIONS.md           # 决策累积 → 膨胀
  ├── report-{0X}.md         # 异常报告累积 → 膨胀
  ├── closure-checklist.md   # Stage 条目累积 → 膨胀
  ├── buglist.md             # Bug 累积 → 膨胀
  └── REFACTOR_MODE.md       # 回流标记（✅ 已处理）

docs/specs/
  └── .state-card.md         # Cockpit — active changes + bugs 行累积

modules/{module}.md
  └── 变更记录表             # append-only → 膨胀
```

---

## §2 工件体积硬上限

> 阈值来源 → [thresholds.md §累积型工件硬上限](thresholds.md#累积型工件硬上限)

| 工件 | 上限 | 超标检测 | 超标动作 |
|------|:---:|------|---------|
| per-change .state-card.md | **80 行** | 阶段切换时自检 `wc -l` | 🛑 不追加，执行重置（§3） |
| Cockpit .state-card.md | **150 行** | SessionStart / 阶段切换时检测 | ⚠️ 修剪已完成 change 行 → 移到 `<!-- 已完成变更 -->` 折叠区 |
| DECISIONS.md | **80 行** | 写入新决策前检测 | 已决议项 → 移至 `<!-- 已决议（归档） -->` 折叠区 |
| report-{0X}.md | **单个 100 行** | 写入时自检 | 无（单文件格式固定）；总数量 ≤ 10 个 |
| closure-checklist.md | **100 行** | 回流前检测 | 已完成 Stage → 折叠；全 Stage 完成 → 重置为空模板 |
| buglist.md | **100 行** | 写新 bug 前检测 | 已修复 bug → 移至 `<!-- 已修复历史 -->` 折叠区 |
| modules/{module}.md 变更记录表 | **100 行** | DOC SYNC #2 写变更记录时检测 | 保留最近 30 条 + `<!-- 完整历史见 git log -->` |

> **proposal.md / spec.md / design.md 不在此表**：这些是内容型工件（承载用户意图/规格/方案），不是累积型工件。它们的约束是**纯粹性**（见 §12），不是体积。

---

## §3 状态卡四态生命周期

```
状态卡生命周期:
  
  CREATE (Intake Phase 1)
    ↓
  UPDATE (每次阶段切换)
    ↓
  ├─ 正常路径 → ARCHIVE（Change 归档时）
    │             状态卡随 change 移入 archive/done/{id}/
    │
  └─ 回流路径 → RESET（Refactor Protocol 触发）
                 1. 旧状态卡 → _invalidated/v{N}/.state-card.md
                 2. 创建新状态卡（阶段重置为 Intake，工件全 ❌）
                 3. 清除旧阻塞/反馈/健康度数据
                 4. 版本号递增 v{N} → v{N+1}
```

### 3.1 重置规则（Refactor Protocol §3 已定义，此处细化状态卡部分）

```
Refactor Protocol 触发时，doc-updater 回流模式 DOC SYNC #1 追加:

Step 2.5 — 重置状态卡:
  检测 per-change .state-card.md:
    ├── 存在 → mv → _invalidated/v{N}/.state-card.md
    └── 不存在 → 跳过
  
Step 2.6 — 创建新状态卡:
  从模板 [templates/state-card.md](../templates/state-card.md) 生成:
    变更: {id}（不变）
    当前阶段: Intake
    工件进度: 全部 ❌ 或 —（等待 planner 重新生成后更新）
    健康度: 全重置为 🟢 未知（等待后续阶段填充）
    阻塞: 无
```

---

## §4 Cockpit 状态卡修剪规则

```
Cockpit 自检（SessionStart / 阶段切换时）:

  1. wc -l docs/specs/.state-card.md
     ├── ≤ 150 行 → 正常
     └── > 150 行 → 触发修剪

  2. 修剪操作:
     a. 扫描 active-changes 表:
        - 标记为 "✅ 已完成" 且归档时间 > 24h → 移除
        - 标记为 🔴 阻塞且阻塞时间 > 7d → 保留（不修剪）
     b. 扫描 bugs 表:
        - 状态为 ✅已修复 且 > 7d → 移至折叠区
     c. 重新计算 health 段
     d. 输出: "Cockpit 已修剪: 移除 {N} 个已归档 change, {M} 个已修复 bug"
```

---

## §5 DECISIONS.md 生命周期

```
DECISIONS.md:

  CREATE (Plan 阶段)
    ↓
  APPEND (每次新决策)
    ↓
  回流路径:
    1. 旧 DECISIONS → _invalidated/v{N}/DECISIONS.md
    2. 创建空 DECISIONS.md（只留 header + "## 开放决策" + "## 历史决策见 _invalidated/v{N}/"）
    3. 新决策从空开始

  非回流路径 — 体积超标:
    wc -l DECISIONS.md > 80:
    → 已 [x] 决议 → 移至 `<!-- 已决议（归档于 {date}）-->` 折叠区
    → 未决议 [ ] 保留在原表
```

---

## §6 report-{0X}.md 生命周期

```
report-{0X}.md:

  CREATE (异常发生时)
    ↓
  ARCHIVE (Change 归档时)
    所有 report 随 change 移入 archive/

  回流路径:
    1. 旧 report → _invalidated/v{N}/report-*.md
    2. 编号从 report-01.md 重新开始
    3. 每个 report 限 100 行，超出则拆分

  数量上限:
    总数 > 10 → ⚠️ 警告 "异常报告过多，建议排查系统性原因"
```

---

## §7 closure-checklist.md 生命周期

```
closure-checklist.md:

  CREATE (Plan 阶段)
    ↓
  UPDATE (Implement 阶段逐 Stage)
    ↓
  回流路径:
    1. 旧 checklist → _invalidated/v{N}/closure-checklist.md
    2. 创建空白 checklist（只留表头，Stage 1-5 全 [ ]）
    3. 标注: "此 checklist 对应 v{N+1}，v{N} 历史见 _invalidated/"

  非回流路径:
    全部 Stage [x] → DOC SYNC #2 后保留（归档时随 change 移走）
```

---

## §8 buglist.md 生命周期

```
buglist.md:

  CREATE (Intake 检测到 bug)
    ↓
  APPEND (每次新 bug)
    ↓
  RESOLVE (bug 修复 + Retro-Spec 通过)
    标记 [x] + 修复日期
    ↓
  体积超标 (wc -l > 100):
    → 已 [x] + 确认 > 7d → 移至 `<!-- 已修复历史 -->` 折叠区
    → 未修复保留

  非 bug 场景不创建 buglist.md
```

---

## §9 modules/{module}.md 变更记录表

```
modules/{module}.md 的 "变更记录" 段:

  APPEND (每次 DOC SYNC #2)
    ↓
  行数 > 100:
    → 保留最近 30 条记录
    → 其余替换为: `<!-- 完整历史见 git log: docs/modules/{module}.md -->`
    
  目的: 文档是知识来源，不是 git 日志。变更历史用 git log 查更快。
```

---

## §10 与 Refactor Protocol 的联动

> **proposal.md 特殊性**：回流时 proposal.md 不在 §3.2 Step 2 跳过列表中（不同于 spec/design/tasks 会被 planner 重新生成），因此旧 proposal 会按 §3.2 Step 4 移入 `_invalidated/`。新 proposal 由 proposal-writer 重新生成，内容从头写，不引用旧版本。

```
Refactor Protocol 触发（用户/Review: "全是 mock，重做"）
  ↓
DOC SYNC #1 回流模式执行（原有 6 步）:
  Step 1: 编目旧产物
  Step 2: 识别需隔离文件
    🆕 追加: .state-card.md, DECISIONS.md, closure-checklist.md,
             report-*.md, buglist.md 全部纳入隔离范围
  Step 3: 创建 _invalidated/v{N}/
  Step 4: mv 旧产物 → _invalidated/v{N}/
  Step 5: 写入 REFACTOR_MODE.md
  Step 6: 正常 DOC SYNC #1（写 modules/）
  🆕 Step 7: 重置状态卡 + DECISIONS + closure-checklist 为空模板

完成后:
  changes/{id}/
    ├── REFACTOR_MODE.md
    ├── .state-card.md           ← 全新，Intake 阶段，全工件 ❌
    ├── spec.md                  ← planner 新生成
    ├── design.md                ← planner 新生成
    ├── tasks.md                 ← planner 新生成（全 [ ]）
    ├── DECISIONS.md             ← 空模板（旧决策历史在 _invalidated/）
    ├── closure-checklist.md     ← 空模板（全 Stage [ ]）
    ├── contracts/               ← contract-writer 新生成
    └── _invalidated/
        └── v1/
            ├── .state-card.md
            ├── DECISIONS.md
            ├── closure-checklist.md
            ├── report-01.md
            ├── buglist.md
            └── ...
```

---

## §11 禁止行为

| 禁止 | 后果 | 替代 |
|------|------|------|
| 状态卡 > 80 行仍继续追加 | 上下文膨胀，Agent 读卡时迷失 | 🛑 执行重置 |
| 回流时不重置状态卡 | 旧状态数据误导新版本 | 回流 = 全重置 |
| Cockpit > 150 行不修剪 | Cockpit 读取 OOM | SessionStart 强制修剪 |
| 变更记录表无上限追加 | 模块文档膨胀 | 最近 30 条 + git log |
| 回流后保留旧 DECISIONS | 已废弃决策干扰新方案 | 归档到 _invalidated/ |
| 回流后不重置 closure-checklist | Stage 状态混乱 | 重置为空模板 |

---

## §12 工件纯粹性规则

> **一根筋原则**：每个工件只做一件事。内容跨工件泄漏 = 污染。宁可留白，不写不属于自己的内容。

### 12.1 工件本职表

> 工件本职与越界完整表 → [artifact-responsibilities.md](artifact-responsibilities.md)。生命周期文件只管理体积上限和重置规则。

### 12.2 污染判定

```
读到工件内容 → 对照 §12.1 本职列:
  ├── 属于本职 → ✅ 保留
  ├── 属于其他工件的本职 → 🚫 删除（或移到正确工件）
  └── 不确定 → 问：这段内容 1 年后对理解系统还有价值吗？
       ├── 有 → 移到对应工件
       └── 没有 → 删除
```

### 12.3 proposal.md 特殊保护

> proposal.md 是用户原始意图的唯一载体。spec-writer、contract-writer、implementer 都从它派生。**proposal 失真 = 整个 change 偏航**。

```
核心四段（必须完整，不限长度）:
  ✅ Why — 动机和根因
  ✅ What Changes — 具体模块和变更
  ✅ Capabilities — 能力声明
  ✅ Non-Goals — 明确边界

版本附注（可选，≤10 行，放末尾）:
  ✅ 顶部 2-3 行版本状态标记（如 "> **V4 状态**: APPROVED"）
  ✅ 末尾简洁变更记录（≤3 行，日期+一句话）
  ✅ V4 起点验证表（确认核心段完整性）

不可接受（版本信息挤掉核心段）:
  🚫 用 50 行版本变更编年史替代 Why 段
  🚫 "CHANGELOG" 段展开成 30 行占据正文
  🚫 "本提案 V1→V2→V3→V4 演变历程" 长篇替代 What 段

判定标准: 删除所有版本附注后，核心四段是否仍然完整可读？
```
