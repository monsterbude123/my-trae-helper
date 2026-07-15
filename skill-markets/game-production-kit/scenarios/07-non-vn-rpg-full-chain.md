# 场景 7: 非 VN 游戏完整链 — 2D RPG《勇者的咖啡馆》

## 用户视角

```
用户: "我想做一个 2D RPG《勇者的咖啡馆》，白天经营咖啡馆（模拟经营），
      晚上去地下城打怪（回合制战斗），选什么引擎？"

Agent: 🛩️ Cockpit 驾驶舱启动（references/cockpit.md）
       .project-cockpit.md 初始化，状态卡建立

       ## Phase 0.5 引擎选择（references/engine-decision-guide.md）
       Q1 游戏类型 → 2D RPG + 模拟经营（非 VN）
       Q2 目标平台 → 桌面 + 移动端
       Q3 技术偏好 → 不限

       | 引擎     | 2D渲染 | 回合制战斗 | UI系统 | 学习曲线 | 推荐    |
       |----------|:------:|:---------:|:-----:|:-------:|:-------:|
       | Godot 4  | ✅     | ✅ GDScript | ✅    | 中      | ⭐ 推荐 |
       | Unity    | ✅     | ✅ C#       | ✅    | 高      | 备选    |
       | RPGMaker | ✅     | ✅ 内置     | ✅    | 低      | 限制多   |
       | WebGAL   | ❌     | ❌          | ✅    | 低      | 不支持   |

用户: "选 Godot"

Phase 0.5 确认: engine=godot, version=4.x
```

## 系统内部流程

```
Phase 0: Cockpit 初始化
  .project-cockpit.md 创建 ★ MUST
  引擎字段待填充

Phase 0.5: Engine Confirmation ★ 不可跳过
  加载 engine-decision-guide.md → 游戏类型=2D RPG
  → 决策矩阵匹配: Godot/Unity vs VN引擎排除
  → engine=godot 写入状态卡

Phase 1: Story+Design（引擎无关）
  ├── game-story-design 加载
  │     └── 12 NPC 角色宪法: Want/Fear/弧光 全量落盘
  │         产出: story-design.md
  │
  └── game-design-doc 并行加载 ★ 非 VN 触发
        ├── 核心循环: 经营(制作→销售→进货→升级) ↔ 战斗(探索→遇敌→回合→战利品)
        │   引用: references/02-core-loops.md RPG 模式
        ├── Gameplay 宪法: 角色 HP/ATK/DEF/SPD/技能树/装备槽
        │   追加到 story-design.md 角色段的 `## Gameplay 维度`
        │   引用: 02-character-constitution.md 7 维宪法
        ├── 关卡设计: 5 层地下城 + Boss 参数矩阵
        │   引用: references/04-level-design.md
        ├── 经济系统: 咖啡售价/原料成本/升级费用平衡表
        │   引用: references/03-balance-methods.md §2 经济模型
        └── 产出: game-design-doc.md ★

Phase 2: Asset Pipeline（引擎无关）
  立绘(12角色) + 像素精灵 + BG(咖啡馆+地下城) + BGM + SFX
  → game-asset-pipeline 加载
  产出: asset-manifest.md

Phase 3: Scripting（引擎路由→godot-scripting）
  godot-scripting 加载
  ├── GDScript: class_name 注册 + @export 参数
  ├── 战斗系统: ATK/DEF 公式实现
  ├── 经营逻辑: 订单系统 + 升级链
  ├── Lint: gdlint .  （godot-scripting §代码质量）
  │    Formatter: gdformat --check .
  └── 产出: scene-manifest.json + proof-screenshots/ (≥3)

Phase 4: Quality Gate ★ 阻断检查
  ├── 素材检查: game-quality-gate → RGBA/尺寸/RMS
  ├── 跨引擎契约: scene-manifest.json/asset-references.json/branch-coverage.txt
  │   引用: cross-engine-contract.md
  ├── 游戏逻辑: 战斗公式边界值 / 存档兼容 / 经济通胀
  │   引用: 02-game-logic-checks.md §5 存档兼容
  │   ⚠ 注意: 平衡验证(break-even)引用 03-balance-methods.md §4
  │   但 game-quality-gate 未显式引用 GDD 的平衡方法
  ├── Lint: gdlint 0 error → 不进 Phase 5
  └── 产出: quality-report.md

Phase 5: Build  → godot-engine-build
Phase 6: Deploy → Steam + itch.io
Phase 7: Ops   → game-operations
```

## 关键决策点

| # | 决策点 | 触发条件 | 决策逻辑 |
|---|--------|---------|---------|
| D1 | 引擎选择走对比表 | 非 VN 游戏 | engine-decision-guide.md 2D 游戏矩阵 → 多引擎对比 |
| D2 | GDD 并行加载 | Phase 1 检测非 VN | game-design-doc 与 game-story-design 并行，角色宪法为共同锚点 |
| D3 | Gameplay 宪法追加到角色 | GDD §Gameplay 宪法 | 角色名作为 key，HP/技能/装备槽追加到对应角色段 |
| D4 | 经济平衡验证 | Phase 4 质量门禁 | 用 03-balance-methods.md §4 break-even 公式验证 |
| D5 | gdlint 阻断 | Phase 3/4 lint 检查 | gdlint 非零 → 不进 Phase 5 |

## 发现的问题

| ID | 严重度 | 描述 |
|----|:------:|------|
| I1 | HIGH | **GDD 输出文件名不一致**：SKILL.md §4 委派速查说产出 `game-design-doc.md`，但 game-design-doc SKILL.md 约束说"GDD 写入 `game-design.md`"。cockpit 模板用 `game-design-doc.md`，子技能用 `game-design.md`。需统一。 |
| I2 | HIGH | **State card 命名不一致**：SKILL.md §2.5 用 `.project-cockpit.md`，§6/§8 用 `.project-state-card.md`。cockpit.md 用 `.project-cockpit.md`。同一文件两种名字。 |
| I3 | MEDIUM | **引擎对比表格式缺失**：engine-decision-guide.md 有按游戏类型分类的矩阵，但缺少按引擎×特性（经营/战斗/2D/UI）的交叉对比表。Scenario 中 Agent 需自行构造此表。 |
| I4 | MEDIUM | **Quality Gate 未链接 GDD 平衡方法**：02-game-logic-checks.md 覆盖存档兼容/分支完整性/性能，但 game-quality-gate SKILL.md 的"详细参考"未列出 02-game-logic-checks.md，也未引用 03-balance-methods.md。Phase 4 的 break-even 验证无显式门禁条目。 |
| I5 | LOW | **godot-scripting 中 gdtoolkit 安装说明位置偏后**：`pip install gdtoolkit` 列在"CI 安装"行，但 gdlint 是 Phase 3 内建检查，不是 CI-only。Agent 可能漏装。 |
