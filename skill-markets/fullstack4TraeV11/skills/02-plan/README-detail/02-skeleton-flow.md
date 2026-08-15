# 骨架流程 — README.md 详情

> 父文件：[../README.md](../README.md)
> 来源：原 README.md 第 28-87 行（保留信息密度）

---

## 完整骨架流程（6 步）

```
Step 0: Cockpit 读取
        ├─ 读 {project}/docs/specs/.state-card.md
        ├─ 识别活跃 change（如有 → 🔴 阻塞则先汇报用户）
        └─ 校验 stage=-1/intake completed（前置 stage PASS）

Step 1: 意图识别 + 选链
        ├─ 触发词扫描（"规划"/"设计"/"重构"/"分析"）
        ├─ 意图分类: 新功能 / 重构 / Bug 修复 / 文档更新
        └─ 选链:
            ├─ 新功能 → 完整 13 stage（Plan → Spec → ... → Accept）
            ├─ 重构 → spec-purge → 完整 13 stage
            ├─ Bug 修复 → 不走 Plan，直接 Stage 6 Bug Fix
            └─ 文档更新 → ponytail 直改（跳过 Plan）

Step 2: 去重检查（原子级）
        ├─ 扫描 docs/specs/changes/ 下活跃子目录
        ├─ 扫描 docs/archive/done/ 同名功能
        ├─ 原子级比较（> 50% 重叠 → 合并 / < 50% → 新建）
        └─ 输出: 去重决策表

Step 3: 3 路并行子代理探索（核心）
        ├─ 子代理 A — 文档探索（exploration-task）
        │   ├─ Read docs/INDEX.md → docs/ARCHITECTURE.md → 相关 spec
        │   ├─ Read 模块文档 docs/modules/{affected}/
        │   └─ 产出: docs_summary.json（已有能力 + 架构约束 + 受影响模块）
        │
        ├─ 子代理 B — 代码探索（exploration-task）
        │   ├─ GitNexus impact({target}) → 影响面
        │   ├─ GitNexus context({target}) → 调用链
        │   ├─ GitNexus query({concept}) → 概念相关
        │   └─ 产出: code_summary.json（受影响符号 + 调用链图 + 风险等级）
        │
        └─ 子代理 C — 依赖探索（exploration-task）
            ├─ 检测已有公共模块 / 工具函数 / 可复用组件
            ├─ Read 关键 lib / util / helper
            └─ 产出: deps_summary.json（可复用资源 + 需新建模块）

Step 4: 重构场景 → spec-purge.py（仅重构走此步）
        ├─ python ../../scripts/spec-purge.py --feature {name} [--dry-run]
        ├─ 确认清除成功
        └─ 当成全新需求，重新走 Step 3 探索

Step 5: 产出 plan.md（spec-kit 格式）
        ├─ Why（为什么做）
        ├─ Capabilities（能力清单 ≤ 5 项）
        ├─ Non-Goals（非目标）
        ├─ Tasks（checkbox 清单 ≤ 20 项）
        ├─ Closure（P0 闭环步骤 ≤ 5 步）
        └─ Impact（受影响代码/API/依赖 + 风险等级）

Step 6: 状态卡更新
        ├─ current_stage: 0/plan → completed
        ├─ next_stage: 0.5/test-plan → pending
        ├─ stage_ended_at: now
        └─ state-card-validator.py PASS
```

---

## 关联引用

- 父文件：[../README.md](../README.md)
- SKILL.md：[../SKILL.md](../SKILL.md)
