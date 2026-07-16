# 回流重构协议（Refactor Protocol）

> **核心铁律**：回流 = 废除旧世界。旧报告是噪声源，不是参考物。Agent 的职责是实现新 spec，不是核对旧 report。
> **根因**：DOC SYNC #1 在回流场景下不清理旧产物 → implementer 读到旧 report 中的"已完成"标记 → 上下文被比较新旧差异拖垮 → 零行实现代码。

---

## §1 问题链路

```
用户: "全是 mock，重做"
  ↓
spec-writer 重写 spec.md  ✅
planner 重写 design.md + tasks.md  ✅
doc-updater DOC SYNC #1
  ❌ 写 modules/ 新内容
  ❌ 但 changes/ 下旧 report 纹丝不动
    ├── implementation-report-v1.md  → "Feature X 已完成 ✅"
    ├── review-report-v1.md          → "评分 4.0 ✅"
    └── tasks-v1.md                  → 80% [x]
  ↓
implementer 进入
  glob "docs/changes/{id}/**/*.md"  → 捞出 15+ 文件
  🌪️ 开始死亡螺旋:
    读旧 report（"已完成"）→ 读新 spec（"重做"）→ 对比差异
    → 上下文爆炸 → 整天核对文档 → 零行实现代码
```

---

## §2 三层防御体系

| 层 | 手段 | 执行者 | 时机 | 防什么 |
|:---:|------|--------|------|--------|
| **L1** | 物理隔离 — 旧产物移入 `_invalidated/` | doc-updater (DOC SYNC #1 回流模式) | planner 完成后、implementer 进入前 | agent 读到旧报告产生认知偏差 |
| **L2** | 委派注入 — REFACTOR MODE 指令 | 主上下文 | 委派 implementer 时 | agent "核对差异"而非"从零实现" |
| **L3** | 归档门禁 — GATE 5 mock + GATE 2 V2标记 | 主上下文 | Review 阶段 | mock 伪装成完成 |

---

## §3 L1: 物理隔离（DOC SYNC #1 回流模式）

### 3.1 触发条件

```
DOC SYNC #1 执行时检测:
  changes/{id}/ 下存在以下任一旧产物 → 触发回流模式:
    - *_report*.md       (implementation-report / review-report)
    - *_v1*.md           (版本号后缀的任务/设计/规格)
    - completion-report*.md
    - 任何 .md 文件的 mtime 早于当前 spec.md 的 mtime 超过 5 分钟
```

### 3.2 执行步骤

```
Step 1 — 编目旧产物:
  ls -la docs/changes/{id}/*.md → 列出所有 .md 文件

Step 2 — 识别需隔离的文件:
  跳过: spec.md, design.md, tasks.md（planner 刚生成的新版）
  跳过: contracts/ 目录（contract-writer 刚生成）
  跳过: prototypes/ 目录（原型设计产物）
  其余全部 .md 文件 → 标记为旧产物

Step 3 — 创建隔离目录:
  NINVALIDATED_DIR = {id}/_invalidated/v{N}/
  N = 该目录下已有 _invalidated/v* 的数量 + 1
  示例: _invalidated/v2/

Step 4 — 移动旧产物:
  mv implementation-report-v1.md → _invalidated/v1/
  mv review-report-v1.md         → _invalidated/v1/
  mv tasks-v1.md                 → _invalidated/v1/
  mv completion-report-v1.md     → _invalidated/v1/
  ... (所有非核心旧产物)

Step 5 — 写入标记文件:
  在 changes/{id}/REFACTOR_MODE.md 写入:
    回流次数: N
    回流原因: spec 重构
    旧产物路径: _invalidated/v{N}/
    当前版本: v{N+1}
    生成时间: {timestamp}

Step 6 — 写 modules/ 新内容（正常 DOC SYNC #1 流程）
```

### 3.3 效果

```
回流前:
  docs/changes/09-model-management/
    ├── spec.md (v2)
    ├── design.md
    ├── tasks.md
    ├── implementation-report-v1.md   ← 噪声
    ├── review-report-v1.md           ← 噪声
    ├── contracts/model-api-v1.md     ← 噪声
    └── ...

回流后 DOC SYNC #1:
  docs/changes/09-model-management/
    ├── REFACTOR_MODE.md              ← 标记
    ├── spec.md                       ← planner 新生成
    ├── design.md                     ← planner 新生成
    ├── tasks.md                      ← planner 新生成（全部 [ ]）
    ├── contracts/                    ← contract-writer 新生成
    └── _invalidated/
        └── v1/
            ├── implementation-report-v1.md
            ├── review-report-v1.md
            ├── contracts/model-api-v1.md
            └── tasks-v1.md
```

---

## §4 L2: 委派注入模板

> 主上下文委派 implementer 时，若检测到 `REFACTOR_MODE.md` 存在，必须在 prompt 末尾注入以下内容。

### 注入内容

```
⚠️ REFACTOR MODE — 此 change 已回流 v{N} 次，需从头重做

工作目录: docs/changes/{id}/
当前权威文件（只需读这些）:
  - spec.md           ← 最新权威规格
  - design.md         ← 最新设计方案
  - tasks.md          ← 全部 [ ]，需从头实现
  - contracts/        ← 最新接口契约
  - closure-checklist.md ← 闭环清单

🛑 禁止:
  - 禁止进入 _invalidated/ 目录
  - 禁止读取任何带 "v1"、"old"、"report"、"review"、"completion-report" 的文件
  - 禁止对比新旧差异 — 这次是实现新 spec，不是审查变更
  - 禁止假定 "以前做过" — tasks.md 中 [ ] = 从未做过

MUST:
  - 按 tasks.md 从第一条到最后一条，逐项 TDD 实现
  - 每个任务: 🔴写测试 → 🟢写实现 → 跑测试 → 下一个 → 不跳任务
  - 完成后输出 Completion Report，列出每个任务的实现证据
```

### 注入时机

```
主上下文委派 implementer:
  1. 检查 docs/changes/{id}/REFACTOR_MODE.md 是否存在
  2. 存在 → 组装标准委派 prompt + 追加本注入模板
  3. 不存在 → 正常委派
```

---

## §5 完整回流流程（场景重定义）

```
    用户: "全 mock，重做"
        │
        ▼
  ┌─ spec-writer ──────────┐
  │ 重写 spec.md            │  ✅
  │ 版本号递增              │
  └─────────┬───────────────┘
            │
            ▼
  ┌─ contract-writer ──────┐
  │ 重新生成 contracts/     │  ✅
  └─────────┬───────────────┘
            │
            ▼
  ┌─ planner ──────────────┐
  │ 重写 design.md          │  ✅
  │ 重新生成 tasks.md (全[ ])│  ✅
  └─────────┬───────────────┘
            │
            ▼
  ┌─ doc-updater ──────────┐
  │ ★ 回流模式 DOC SYNC #1  │  🆕
  │   1. 编目旧产物          │
  │   2. 移入 _invalidated/  │
  │   3. 写入 REFACTOR_MODE  │
  │   4. 写 modules/ 新内容  │
  └─────────┬───────────────┘
            │
            ▼
  ┌─ 主上下文 ──────────────┐
  │ 检测 REFACTOR_MODE.md   │  🆕
  │ 组装委派 + 注入 L2 模板  │
  └─────────┬───────────────┘
            │
            ▼
  ┌─ implementer ──────────┐
  │ 只读当前 5 个权威文件    │  ✅
  │ TDD 逐条实现 tasks.md   │  ✅
  │ 不读 _invalidated/      │  🆕
  └─────────┬───────────────┘
            │
            ▼
  ┌─ reviewer ─────────────┐
  │ 7 维度打分              │
  │ GATE 5 mock 检测        │  ✅
  │ GATE 2 V2 标记审计      │  ✅
  └─────────────────────────┘
```

---

## §6 禁止行为

| 禁止 | 后果 | 替代 |
|------|------|------|
| 回流后 DOC SYNC #1 不清理旧产物 | implementer 读到旧 report 产生认知偏差 | §3 L1 物理隔离 |
| implementer 读 _invalidated/ 旧报告 | 上下文被新旧对比拖垮 | REFACTOR_MODE 禁止指令 |
| implementer 对比新旧 spec 差异 | 消耗 token 做 diff 而非写代码 | 只读当前权威文件 |
| 用户要求重做但 agent 只改文档不改代码 | mock 继续存在 | 回流必须重走 entire 实现链 |
| REFACTOR_MODE 注入后仍用 mock 糊弄 | 第二次白白回流 | GATE 5 mock 密度 > 3 即 WARN |
