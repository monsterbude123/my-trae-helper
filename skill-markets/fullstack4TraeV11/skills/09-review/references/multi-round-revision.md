# 多轮修订协议（Multi-Round Revision — V11 完整版）

> Stage 4 Review Step 2.6 必走。V10 reviewer Step 2.6 自动循环机制 + V10 multi-round-revision-protocol.md 完整版蒸馏。

---

## §0 三大铁律

```
1. MUST 精确定位修订点
   - 用 Grep 找到具体行号
   - 只动需要改的段落，不动其他内容

2. MUST 追加变更记录
   - 格式：| 日期 | 版本 | 修订内容摘要 |

3. NEVER 重写整个文档
   - 除非用户明确要求"重写"
   - 否则只做增量修订
```

---

## §1 修订流程（5 步 — V10 完整蒸馏）

```
Step 1 — 解析用户反馈
  ├─ 明确点: 表名冲突 → 改表名
  ├─ 模糊点: "感觉不对" → 追问具体哪里不对
  ├─ 冲突点: A 和 B 矛盾 → 汇报用户选择
  └─ 输出: 修订清单（编号 + 具体内容）

Step 2 — 定位修订点
  ├─ 用 Grep 找到相关段落
  │   ├─ 表名冲突 → grep "CREATE TABLE {表名}"
  │   ├─ 字段冲突 → grep "{字段名}"
  │   └─ 流程冲突 → grep "## {章节名}"
  └─ 输出: 修订点行号表

Step 3 — 执行修订
  ├─ 用精确替换工具（Edit/SearchReplace）
  │   ├─ old_str: 包含上下文的完整段落
  │   └─ new_str: 修订后的段落
  └─ 输出: 修订后的文件

Step 4 — 验证修订: Grep 验证新内容存在 + 旧内容不存在

Step 5 — 追加变更记录: | {日期} | v{版本} | {修订内容摘要} |
```

---

## §2 修订清单模板

```markdown
| # | 修订点 | 定位 | 操作 |
|---|--------|------|------|
| 1 | 表名冲突：tags → model_tags | §4.6 L301 | 删除独立主表，改为关联表 |
| 2 | 字段策略：唯一 → 互斥双列 | §4.1 L164 | 新增字段 + CHECK 约束 |
```

---

## §2.5 Round 术语定义（Stage 9 特有）

- **Round 1**: Reviewer 退回 implementer 重做（失败标签必填）
- **Round 2**: Reviewer 升级上报用户（5 字段阻塞报告，Article XV）
- **Round 3+**: rescue hatch — 自动触发回退 Phase 0（Intake）重新审视需求
- **作用域**: 仅 Stage 9 Review 使用，Stage 6 Bug Fix 的 B.1/B.2/B.3 是不同术语（详见 glossary.md §V10.8 bug-workflow）

> ⚠️ Round ≠ Stage 6 bug-workflow 的 B.x — agent 跨 stage 时勿混淆

---

## §3 Round 1: 退回 implementer

```
Reviewer: REJECT + 失败标签
  ↓
Implementer: 重做（按 §1 5 步流程精确定位）
  ↓
Reviewer: 再 Review
  ├─ PASS → 通过
  └─ FAIL → Round 2
```

---

## §4 Round 2: 升级上报用户

```
Reviewer: REJECT + 失败标签 + 5 字段阻塞报告（Article XV）
  ↓
上报用户决策:
  ├─ 用户接受现状 → 显式豁免
  ├─ 用户决策回退上游 Stage → 回退
  └─ 用户要求继续 → Round 3+
```

---

## §5 Round 3+: rescue hatch（回退 Stage 0 Intake）

```
Reviewer: 连续 3 轮失败 → 回退 Stage 0（Intake）重新审视需求
```

---

## §6 失败分类标签

| 标签 | 含义 |
|------|------|
| `MISMATCH` | 货不对版（功能与 spec 不符）|
| `UNDERPERFORM` | 功能不达标 |
| `USER_VIEW_FAIL` | 用户视角 FAIL |
| `TEST_GAP` | 测试覆盖缺口 |
| `DRIFT` | 代码与契约漂移 |
| `SCOPE_CREEP` | 修订范围蔓延（违反 §0.3 不重写）|

---

## 反例

### 反例 A：连续 5 轮小修小补

```
Round 1: 退 → implementer 修补命名
Round 2: 退 → implementer 修补格式
Round 3: 退 → implementer 修补空行
Round 4: 退 → implementer 修补注释
Round 5: 退 → ???  # ❌ 反复反馈升级根因诊断

正确: Round 2 升级用户 → 用户决策回退上游
```

### 反例 B：失败标签缺失

```
Reviewer: REJECT  # ❌ 无失败标签
正确: REJECT + 失败分类标签 + 5 字段阻塞报告
```

### 反例 C：违反 §0.3 重写整个文档

```
现象: implementer "重写整个 spec.md" 加几行修订
根因: 未用 SearchReplace 精确定位
教训: 必用 §1 Step 2 Grep 定位 + Step 3 SearchReplace 增量
```

### 反例 D：违反 §0.2 不追加变更记录

```
现象: 修订后文件没 changelog 行
根因: implementer 跳过 §1 Step 5
教训: 每次修订必追加 | {日期} | v{版本} | {摘要} |
```

---

## 关联引用

- [SKILL.md §铁律 10](../SKILL.md) — 关键门禁套件
- [stage-interaction-protocol.md](../../../references/stage-interaction-protocol.md) — 修订后产物路径
- V10 来源（开发期，已蒸馏）: 见 V11 references 与 anti-patterns（部署时不依赖）references/multi-round-revision-protocol.md`