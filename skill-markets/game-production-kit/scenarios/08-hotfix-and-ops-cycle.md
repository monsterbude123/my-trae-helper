# 场景 8: Hotfix + 运营迭代周期 —《勇者的咖啡馆》

## 用户视角

```
[Day 1 — 上线后，Phase 7 运行中]

Agent: Phase 7 Operations 激活（game-operations）
       数据看板: DAU 1,200, 付费转化 3.2%
       引用: references/03-analytics.md 核心指标

用户: "玩家反馈咖啡馆升级到 Lv.5 后配方列表不刷新"

Agent: 🐛 Bug 登记 #B1: 配方列表 Lv.5 未刷新
       影响: 核心经营循环（无法制作新配方 → 卡进度）
       严重度判定 → P1（功能损坏）→ S1 Hotfix
       引用: game-hotfix SKILL.md §S1/S2 分级

       🛩️ game-hotfix 启动
       ├── Assess: S1 → Record: hotfix-0714-B1.md → Branch
       ├── Implement: scene_cafe.gd upgrade_level() 添加 refresh_recipes()
       │    ⚠ 工作流无 TDD 步骤，Scenario 注入: 🔴RED → 🟢GREEN
       ├── Approvals: 三方并行 (lead-programmer/qa-tester/producer) ✅
       ├── QA Gate: targeted QA
       └── Deploy: v1.0.1

Agent: Hotfix v1.0.1 部署完成
       Report: [L3] 游戏逻辑异常 — 配方刷新
       引用: references/report-growth.md L3 分级
       更新 .project-cockpit.md: ops 🔄 活跃

[Week 2 — 运营内容更新]

用户: "下个月万圣节，做个限时活动"

Agent: game-operations → 活动模板
       引用: references/04-live-ops.md §4 活动运营模板

       活动设计:
       ├── 限时配方: 南瓜拿铁（10/25-10/31）
       ├── 地下城: 万圣节主题层（换皮+Boss特殊掉落）
       └── Battle Pass: 免费30层+付费50层

       Content Update v1.1:
       ├── 素材: bg_cafe_halloween.png, enemy_ghost.png
       ├── 脚本: event_halloween.gd
       ├── Lint: gdlint 0 error （godot-scripting §代码质量）
       ├── 存档兼容: v1.0.x 存档正常加载 ✅
       │   引用: 02-game-logic-checks.md §5
       └── 埋点: event_halloween_started/purchased

Agent: v1.1 部署完成
       数据看板: Halloween Funnel 追踪已启用

[Month 2 — 赛季切换]

Agent: 赛季 1 "秋日咖啡馆" → 赛季 2 "冬日暖炉"
       ├── Battle Pass 奖励轮换
       ├── 旧 BP 奖励入永久商店（04-live-ops.md §2 衔接检查）
       ├── 排名数据归档: S1 参与率 68%, 付费率 12%
       └── 新赛季内容预载 + 倒计时 UI

       .project-cockpit.md: ops 阶段持续 🔄
```

## 系统内部流程

```
Phase 7 Operations（持续）
  │
  ├── [线上] 数据看板收集 → analytics events
  │
  ├── [Hotfix 触发] 玩家反馈 Bug
  │     ├── gate: S1/S2? → 是 → game-hotfix 加载
  │     ├── S3? → 否 → 回正常 Phase 4 回退
  │     │
  │     ├── game-hotfix 7 阶段:
  │     │   1. Assess → 2. Record → 3. Branch
  │     │   → 4. Implement → 5. Approvals(三方并行)
  │     │   → 6. QA Gate → 7. Deploy
  │     │   ⚠ 步骤 4 无 TDD 子步骤（RED→GREEN 由 Scenario 注入）
  │     │
  │     └── 产出: hotfix-{date}-{id}.md
  │         版本: v{X}.{Y}.{Z+1}
  │
  ├── [Content Update] 活动/赛季
  │     ├── game-operations 加载
  │     ├── 活动模板: references/04-live-ops.md §4
  │     ├── 内容脚本 + Lint + 存档兼容测试
  │     └── 产出: 活动配置 + 埋点事件
  │         版本: v{X}.{Y+1}.0
  │
  └── [Season Switch]
        ├── BP 奖励轮换 → 旧奖励入永久商店
        ├── 赛季数据归档 → analytics dashboard
        └── 版本: v{X+1}.0.0
```

## 关键决策点

| # | 决策点 | 触发条件 | 决策逻辑 |
|---|--------|---------|---------|
| D1 | Hotfix vs Content Update 判定 | 线上问题报告 | Hotfix = 功能修复 + 修订号+1 / Content = 新内容 + 副版本号+1 |
| D2 | S1/S2 vs S3 分级 | Bug 发现 | 核心功能损坏/数据丢失/安全 → S1/S2 走 hotfix；UI 小问题 → S3 走正常回退 |
| D3 | 旧 BP 奖励处理 | 赛季切换 | 入永久商店（04-live-ops.md §2 衔接检查第 5 项） |
| D4 | 存档兼容性测试 | 每个新版本 | 读取 N-1 版本存档（game-operations 铁律 #2） |
| D5 | TDD 注入 | Hotfix 流程 | game-hotfix 工作流无显式 RED/GREEN 步骤，Scenario 自行注入 |

## 发现的问题

| ID | 严重度 | 描述 |
|----|:------:|------|
| I6 | MEDIUM | **game-hotfix 无 TDD 步骤**：工作流为 Assess→Implement→Approvals。Implement 之后直接进 Approvals，缺少 🔴RED（复现测试）→ 🟢GREEN（修复验证）的 TDD 子步骤。Scenario 自行注入了此模式，但实际技能定义中不存在。 |
| I7 | MEDIUM | **game-operations 热修复边界模糊**：game-operations SKILL.md 说"运营变更也走 hotfix 分级"，但未区分"内容更新(活动/赛季)"和"紧急修复(Bug)"。当前措辞可能让 Agent 误将限时活动也送入 game-hotfix 流程。Scenario 通过版本号语义（修订号 vs 副版本号）区分，但 skill 本身未定义。 |
| I8 | LOW | **Hotfix report 命名无规范**：game-hotfix 记录为 `hotfix-{date}-{编号}.md`，但 report-growth.md 定义的 report 文件（如 `report-03.md`）与 hotfix 记录之间无关联约定。Scenario 中"report-03.md [L3]"与 hotfix 记录是分开的。 |
| I9 | LOW | **02-game-logic-checks.md 未被 game-quality-gate 显式引用**：见 Scenario 7 I4。存档兼容测试（§5）在 game-operations 和 game-quality-gate 之间无统一入口。game-operations 铁律 #2 要求存档兼容测试，但 game-quality-gate SKILL.md 的"详细参考"未列出 02-game-logic-checks.md。 |
