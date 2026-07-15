---
name: game-design-doc
description: 游戏设计文档 GDD — 引擎无关。覆盖核心循环/Gameplay 宪法/关卡设计/数值平衡/经济系统。触发词：GDD、游戏设计文档、game design doc、核心玩法、gameplay、关卡设计、数值策划。
user-invocable: true
---

# 游戏设计文档 (GDD)

> 引擎无关的游戏机制设计。与 game-story-design 并行：叙事维度走 story-design，Gameplay 维度走 GDD。

## 前置条件

- Phase 0 引擎已确认
- game-story-design 已完成（角色宪法、剧情树已建立）
- game-production-kit 编排器已加载

## 骨架流程

1. 核心循环定义 → 输出 Core Loop 三阶段公式，落盘 GDD §1
2. Gameplay 宪法 → 扩展角色宪法，追加 HP/攻击/技能/成长曲线等 gameplay 维度
3. 关卡设计 → 关卡流程图 + 逐关卡参数矩阵
4. 数值平衡 → 战斗公式 + 经济模型 + 成长曲线 + 边界值验证

## 与 game-story-design 的关系

```
game-story-design                  game-design-doc
├── Want / Fear / 弧光             ├── HP / ATK / DEF / 技能
├── 剧情树 / 分支 / 结局            ├── 关卡流程图 / 难度曲线
├── 伏笔矩阵 / 恐怖陷阱             ├── 战斗公式 / 经济模型
├── 对话 / 场景 / 环境叙事           ├── 核心循环 / 概率系统
└── 写入 story-design.md           └── 写入 game-design-doc.md
```

GDD 不替代 story-design.md：叙事维度和 Gameplay 维度分开存储，通过角色名互相关联。

## 核心循环（Core Loop）

核心循环 = 玩家反复执行的最基础行动序列。格式：

```
{Action} → {Reward} → {Growth} → 回到 {Action}
```

每种游戏类型有特定循环模式（见 references/02-core-loops.md）：

| 类型 | Action | Reward | Growth | 参考游戏 |
|------|--------|--------|--------|----------|
| VN | 阅读/选择 | 新信息/好感度 | 剧情推进/分支解锁 | DDLC, Steins;Gate |
| RPG | 战斗 | 经验/掉落 | 升级/新技能 | Final Fantasy, Persona |
| 策略 | 规划 | 回合结果 | 解锁新单位/科技 | Civ, XCOM |
| Roguelike | 探索 | 道具/货币 | 局外永久升级 | Hades, Dead Cells |

技能池 > 8 种经典循环模式，详见 references/02-core-loops.md。

## Gameplay 宪法

在 story-design.md 角色段尾追加 `## Gameplay 维度` 段落，每个 playable 角色定义：

| 字段 | 类型 | 说明 |
|------|------|------|
| HP | number | 基础生命值（含成长公式） |
| ATK | number | 基础攻击力（含成长公式） |
| DEF | number | 基础防御力（含成长公式） |
| SPD | number | 速度/行动顺序 |
| 技能列表 | Skill[] | 每个技能：名称/效果/冷却/解锁条件 |
| 成长曲线类型 | enum | linear / s-curve / log-curve / flat |
| 可用装备槽 | enum[] | weapon / armor / accessory / none |

铁律：
- 所有数值必须有公式，不写"大概"或"适中"
- 角色定位必须填：Tank / DPS / Support / Control / Hybrid
- 技能效果必须可量化（伤害值/持续回合/触发概率）

## 数值平衡

必须产出的 3 张核心表（详见 references/03-balance-methods.md）：

1. **战斗公式**：伤害 = ATK × 倍率 - DEF × 系数（或等效公式），含暴击率/元素克制/等级差修正
2. **经济模型**：货币产出-消耗表 + 通胀控制策略（产出上限/消耗递增/回收机制）
3. **成长曲线**：经验值表 + 属性成长公式（每级 HP = baseHP × (1 + growthRate × level)）

边界值验证：
- min dmg = 1（禁止零伤害）
- max dmg ≤ bossHP × 0.35（防止秒杀 boss）
- break-even：同等级 DPS vs Tank 交互回合数 ≥ 3

## 约束

- GDD 写入 `game-design-doc.md`，不修改 `story-design.md`
- 数值设计必须有公式，且在边界值验证通过后方可进入 Phase 3
- 引擎特定实现走 Phase 3 路由（如 godot-scripting / unity-scripting）
- 版本号与 story-design.md 对齐（v1, v2, v3 ... 同步递增）

## 质量清单

- [ ] 核心循环完整且可玩性可论证
- [ ] 角色 Gameplay 维度覆盖全部 playable 角色
- [ ] 战斗/经济公式有边界值计算（min/max/break-even）
- [ ] 关卡参数矩阵覆盖全关卡
- [ ] 经济系统有通胀控制策略
- [ ] 成长曲线有明确 Cap 定义
- [ ] 概率系统有保底/补偿机制（如有抽卡/掉落）

## 详细参考

- GDD 结构模板与章节：`references/01-gdd-template.md`
- 游戏核心循环模式库：`references/02-core-loops.md`
- 数值平衡方法：`references/03-balance-methods.md`
- 关卡设计参数矩阵：`references/04-level-design.md`
