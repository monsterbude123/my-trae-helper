# 场景 4: 质量门禁失败回退

> 模拟目标: 验证 Phase 4 gate-standards 三态 verdict（REJECT/CONCERNS/APPROVE）与 reentry-checkpoint 回退路径的一致性。

---

## 用户视角

```
[之前的对话中已完成 Phase 1-3，用户输入:]
用户: "质量检查一下《咖啡馆的猫》"

Agent: 🎯 Phase 4 Quality Gate 启动 — cafe_cat
       审查模式: lean（默认）
       [加载 cross-engine-contract.md + gate-standards.md + asset-manifest.md]

Agent: 交叉验证 Phase 1-3 checkpoint:
       [check] checkpoint 1 ✅ story-design.md v3
       [check] checkpoint 2 ✅ asset-manifest.md（12 素材）
       [check] checkpoint 3 — 文件系统验证:

       跨引擎契约检查:
       [check] scene-manifest.json         ✅ 可解析，10/10 场景已登记
       [check] asset-references.json       ❌ missing: ["bg_library.png"]
              → Phase 2 有 bg_library.png，但 Phase 3 脚本未引用
              → verdict: REJECT（missing 数组非空，跨引擎契约 §门禁整合）
       [check] branch-coverage.txt         ⚠️ 6/10 分支已实现（目标 10/10）
              → verdict: CONCERNS（覆盖不足但非致命，gate-standards §自动化检查项）
       [check] proof-screenshots/          ⚠️ 1 张（需 ≥ 3）
              → verdict: CONCERNS（跨引擎契约 §门禁整合）

Agent: 🛑 Gate 整体判定 — REJECT（任一 REJECT → 阻断）
       按 gate-standards §整体判定规则:
         - 1 REJECT (asset-references missing[] 非空) → 阻断
         - 2 CONCERNS (分支覆盖 + 截图不足) → 一并列出

       回退路径: Phase 4 REJECT → 回退 Phase 3 Scripting（reentry-checkpoint §回退规则）
       保留: scene-manifest.json ✅（已通过项不重做）
       修复:
         1. [REJECT]  补上 bg_library.png 引用到 asset-references.json
         2. [CONCERNS] 补充 4 个缺失分支的场景脚本 → branch_coverage → 10/10
         3. [CONCERNS] 补充 2 张 proof 截图 → proof-screenshots/ ≥ 3

Agent: [L2] 写入 report-02.md（report-growth §L2: Phase 执行异常）
       .project-cockpit.md: phase=4→3, status=🔄回退, 阻塞=asset-references REJECT

用户: "好，修吧"
```

---

## 系统内部流程

```
Phase 4 Quality Gate 启动
  │
  ├── Step 1: 加载 gate-standards + cross-engine-contract
  │
  ├── Step 2: 交叉验证 checkpoint
  │     ├── checkpoint 1 ✅ (story-design.md 存在)
  │     ├── checkpoint 2 ✅ (asset-manifest.md 存在)
  │     └── checkpoint 3 — 文件系统自检
  │           ├── scene-manifest.json ✅
  │           ├── asset-references.json → parse → missing: ["bg_library.png"]
  │           ├── branch-coverage.txt → 6/10
  │           └── proof-screenshots/ → count=1
  │
  ├── Step 3: 逐项 verdict
  │     ├── scene-manifest.json        → APPROVE
  │     ├── asset-references.json      → REJECT  (missing[] 非空)
  │     ├── branch-coverage.txt        → CONCERNS (< target)
  │     └── proof-screenshots/         → CONCERNS (< 3)
  │
  ├── Step 4: 整体判定 (gate-standards §整体判定规则)
  │     └── REJECT (存在 1 个 REJECT)
  │
  ├── Step 5: 回退路由 (reentry-checkpoint §回退规则)
  │     └── Phase 4 REJECT → 回退 Phase 3
  │
  └── Step 6: 状态同步
        ├── report-02.md [L2] 落盘
        └── .project-cockpit.md: phase=3, status=🔄回退

[Phase 3 重新执行]
  webgal-scripting:
    ├── 修复 asset-references.json: {"bg_library.png": {"used_in": ["scene_02_library"]}}
    ├── 编写 scene_07/08/09/10.txt（4 个缺失分支）
    └── 截图 proof-screenshots/scene_03_10.png（2 张新增）

[Phase 4 重跑]
  ├── [check] asset-references.json → APPROVE
  ├── [check] branch-coverage.txt  → 10/10 → APPROVE
  └── [check] proof-screenshots/   → 3 张 → APPROVE

🟢 Gate PASS → .project-cockpit.md: phase=4, status=✅, 阻塞=NULL
```

---

## 关键决策点

### 1. CONCERNS vs REJECT 判定依据
| 检查项 | 失败条件 | verdict | 依据 |
|--------|---------|---------|------|
| asset-references missing[] 非空 | missing 有值 | REJECT | cross-engine-contract §门禁整合 |
| branch-coverage < target | 6/10 < 10/10 | CONCERNS | cross-engine-contract: "覆盖数 < story-design 分支数 → CONCERNS" |
| proof-screenshots < 3 | 1 < 3 | CONCERNS | cross-engine-contract: "< 3 张 → CONCERNS" |

> **设计原则**: REJECT 用于不可逆阻断（引用断裂会导致构建失败）；CONCERNS 用于质量偏差（可后续补救，用户可"接受并继续"）。

### 2. 回退时保留策略
- `scene-manifest.json` — **保留**（verdict APPROVE，结构完整）
- `report-02.md` — **保留**（失败记录不可丢失）
- `proof-screenshots/` 已有 1 张 — **保留**，增量补充
- 已写的 scene_01-06.txt — **保留**，只补充 scene_07-10

### 3. report 等级为何是 L2 而不是 L3
- L3 = 游戏逻辑异常（分支覆盖不足/存档不兼容/性能不达标）
- L2 = Phase 执行异常（构建失败/脚本解析错误/版本冲突）
- 本次 gate FAIL 的**根因**是 asset-references.json 引用断裂（L1）+ Phase 3 产出不完整。整体 gate 失败属于「Phase 执行异常」→ L2
- 分支覆盖不足单独看是 L3，但在此上下文中是 Phase 3 未完成的副产物，不单独升级

---

## 发现的问题

### [ISSUE-04-01] 分支覆盖 verdict 与 L3 分类矛盾
- **位置**: cross-engine-contract.md §门禁整合 + report-growth.md §L3
- **描述**: cross-engine-contract 将 branch-coverage 不足定为 CONCERNS（可接受），但 report-growth 将「分支覆盖不足」归为 L3（游戏逻辑异常，应写入 quality-gate 检查项）。两处语义冲突：如果是不足即 L3，那 gate 应该 REJECT 而非 CONCERNS。
- **建议**: 明确分级 — 覆盖 < 50% → REJECT（L3），50%-100% → CONCERNS（L1）。

### [ISSUE-04-02] CONCERNS 项混入 REJECT 修复清单未询问用户
- **位置**: gate-standards.md §整体判定规则 —「任一 CONCERNS + 零 REJECT → 询问用户」
- **描述**: 本场景中 gate FAIL 由 REJECT 触发，CONCERNS 项被一并列入修复清单，用户说"修吧"相当于接受了全部修复。但按 gate-standards 协议，CONCERNS 项应单独询问「修复 or 接受并继续」——当前流程跳过了此询问。
- **当前做法可接受**: 因为是 lean 模式（聚合询问），且 REJECT 已阻断，修复 CONCERNS 是合理的批量处理。但应在报告中标注「以下 CONCERNS 项一并修复」。

### [ISSUE-04-03] report-02 编号无规范定义
- **描述**: report-growth.md 定义了 report 格式 `report-{0X}.md` 但未定义编号规则（全局递增？per-phase？per-game？）。多个 report 可能编号冲突或顺序混乱。
- **建议**: 明确编号规则 — 建议 `report-{phase}-{seq}.md`（如 `report-04-01.md`）。
