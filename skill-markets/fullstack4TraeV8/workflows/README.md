# Workflows — V7 工作流全景

> 高层工作流概览。每个 Agent 的具体工作流见 `agents/` 目录。

---

## V7 主线流水线（10 步 + feedback-loop + report）

```
                         用户需求
                            │
                            ▼
              ┌──────────────────────────┐
              │  [00-cockpit]            │
              │  项目驾驶舱定位          │  ← V7 NEW
              │  输出: Cockpit 快照      │
              └────────────┬─────────────┘
                           │
                           ▼
              ┌──────────────────────────┐
              │  [00-intake]             │
              │  意图识别 + 30%去重 +    │  ← V7 强化
              │  影响面评估 + 选链 +     │
              │  状态卡初始化            │
              │  输出: 流程定位卡 +      │
              │  去重报告 + 影响面清单 +  │
              │  .state-card.md          │
              └────────────┬─────────────┘
                           │
                           ▼
              ┌──────────────────────────┐
              │  [00-proposal]           │
              │  proposal-writer         │
              │  Why + What +            │
              │  Capabilities + Non-Goals│
              │  输出: proposal.md       │
              └────────────┬─────────────┘
                           │ proposal approved
                           ▼
              ┌──────────────────────────┐
              │  [00-product]            │
              │  spec-writer             │
              │  BDD spec + E2E 场景 +   │
              │  测试骨架 + 原型(UI时)   │
              │  输出: specs/*/spec.md   │
              │  + prototypes/*.md       │
              └────────────┬─────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
         config检查                  specs approved
              │                         │
    roundtable.enabled?                 │
      ├── false ────────────────────────┤
      └── true                         │
              │                         │
              ▼                         │
   ┌──────────────────────┐            │
   │  [00-roundtable]     │  ← V7 NEW  │
   │  主 Agent 启动6子代理 │            │
   │  各角色审 spec →      │            │
   │  meeting-notes 落盘   │            │
   │  用户裁决分歧         │            │
   └──────────┬───────────┘            │
              │                         │
              └─────────┬───────────────┘
                        │
                        ▼
              ┌──────────────────────────┐
              │  [01-contract]           │
              │  contract-writer         │
              │  领域模型 + API 契约 +   │
              │  事件契约 + 验证规则     │
              │  输出: contracts/ 四件套 │
              │  + contract test 骨架    │
              └────────────┬─────────────┘
                           │ contracts approved
                           ▼
              ┌──────────────────────────┐
              │  [10-design]             │
              │  planner                 │
              │  编号决策 D1..Dn +       │
              │  tasks.md（勾选清单）    │
              │  输出: design.md +       │
              │  tasks.md                │
              └────────────┬─────────────┘
                           │ 用户确认方案
                           ▼
              ┌──────────────────────────┐
              │  [20-dev]                │
              │  implementer             │
              │  CONTRACT GATE →         │
              │  DOC SYNC GATE →         │
              │  CONTRACT TEST →         │
              │  RED → GREEN → REFACTOR  │
              │  → DRIFT CHECK           │
              │  输出: 代码 + 测试 +     │
              │  tasks 全部 [x] +        │
              │  量化汇报                │
              └────────────┬─────────────┘
                           │ 全部完成
                           ▼
              ┌──────────────────────────┐
              │  [40-review]             │
              │  reviewer                │
              │  7 维度打分卡 +          │
              │  契约漂移检测 +          │
              │  目标对齐检查            │
              │  输出: 审查报告 +        │
              │  打分卡 + 漂移报告       │
              └────────────┬─────────────┘
                           │ 审查通过 (≥4.0)
                           ▼
              ┌──────────────────────────┐
              │  [40-accept]             │
              │  acceptance-discipline   │
              │  E2E + 性能 + 安全       │
              │  输出: 验收报告 +        │
              │  门禁结果                │
              └──────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
         accept 通过              accept 失败
              │                         │
              ▼                         ▼
         ┌──────────┐          回流到对应阶段
         │ doc-updater│
         │ 归档到     │
         │ archive/   │
         │ done/      │
         └──────────┘
```

---

## 异常分支

```
发现 Bug
  → [50-debug] debugger
  → 根因分析（证据驱动）
  → TDD 修复
  → 移交 reviewer（阶段 0 根因验证）
  → 验收

文档缺失
  → [10-design] planner（迷雾消除）
  → 反推生成模块文档
  → 继续正常流程

架构调整
  → [10-design] planner（架构模式）
  → ADR + 权衡分析
  → 更新 contracts/（如涉及）
  → 继续正常流程

漂移发现
  → [loop] feedback-loop
  → 漂移类型判定（specs/契约/文档/目标）
  → 回流到对应 Agent
  → 修改 specs/契约/代码

Spec 堆积（> 5 个活跃）
  → Cockpit 标记 🔴
  → intake 30% 重叠检查
  → 合并/归档决策

磕绊/打断/报错/AOP自检失败
  → [report] 随时
  → 写 report-{0X}.md（按 L1-L4 分级）
  → 交付时分级汇总（L1+L3 需立即处理）
```

---

## Agent 间移交矩阵

| 从 | 到 | 门禁 | 移交内容 |
|-----|-----|------|---------|
| Cockpit | Intake | — | 项目级 state-card 快照 |
| Intake | Proposal | 流程定位卡已输出 + 去重已完成 | Cockpit 快照 + 去重报告 + 流程定位卡 + 影响面清单 + .state-card.md |
| Proposal | Spec | proposal approved | proposal.md |
| Spec | Roundtable | specs approved + roundtable.enabled=true | proposal + specs |
| Specs/Roundtable | Contract | specs approved + 圆桌收敛 | specs + meeting-notes |
| Contract | Design | contracts approved | contracts/ 四件套 + contract test 骨架 |
| Design | Dev | 用户确认方案 + CONTRACT GATE + DOC SYNC GATE | design.md + tasks.md |
| Dev | Review | tasks 全部 [x] + 量化汇报 | 代码 diff + tasks.md + 量化汇报 |
| Review | Accept | 7 维度总分 ≥ 4.0 + 无严重漂移 + 目标对齐 ≥ 90% | 审查报告 + 打分卡 + 漂移报告 |
| Review | Dev | 审查不通过 | 关键问题清单 |
| Accept | Doc-Updater | 验收通过 | 验收报告 + change 全部工件 |
| Doc-Updater | Cockpit | 归档完成 | Cockpit 更新（移除 change 行） |

---

## 变更生命周期

```
活跃变更: docs/specs/changes/{NN}-{change-name}/
    │
    ├── 被淘汰（30% 合并 / 用户放弃 / 方向变更）
    │     └── doc-updater → archive/out/{change-name}/
    │
    ├── 完成（验收通过 + 合并到 module.md）
    │     └── doc-updater → archive/done/{change-name}/
    │
    └── 中止（未完成，用户取消）
          └── doc-updater → archive/out/{change-name}/
```

---

## Cockpit 驾驶舱生命周期

```
项目初始化
  → 创建 docs/specs/.state-card.md（空）
  → 首个 change 创建 → intake 写入 cockpit 首行
  → 后续 change → 追加行
  → 阶段切换 → 更新对应行
  → change 完成/淘汰 → doc-updater 移除对应行
  → 项目工件更新 → doc-updater 更新工件状态
```

---

## Report 生长生命周期（Try-Catch）

```
触发（打断/报错/磕绊/优化发现/AOP自检FAIL）
  → 写 report-01.md（按 L1-L4 分级）
  → 追加 report-02.md, ...
  → 交付时分级汇总（L1+L3 需立即处理，L2+L4 可延后）
  → 用户处理（勾选 [x]）
  → 技能设计者 review → 决定是否升级技能/AOP/门禁
  → 升级技能 → 跑 evals 验证
```

---

## 与 V5 的核心差异

| 维度 | V5 | V7 |
|------|-----|-----|
| 入口 | intake | **Cockpit** → intake |
| 去重 | 全覆盖/部分覆盖 | **30% 原子化量化** |
| 评审 | — | **圆桌会议**（6 角色） |
| 异常处理 | （无） | **AOP 自检 + report Try-Catch**（L1-L4） |
| 自检 | Cockpit 单一自检 | **Schema QA 门禁 + AOP 后置自检** |
| 交付 | — | **report 分级汇总** |
| 归档 | archive/ 单层 | **archive/out/ + archive/done/** |
| 状态卡 | per-change only | **Cockpit + per-change 双层** |
| 文档同步 | CODEMAP | **CODEMAP + prototypes + archive + test-plan** |
