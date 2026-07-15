# 数值平衡方法

> 来源：游戏数值设计方法论（Ernest Adams《Game Mechanics》+ 各引擎文档数值系统章节）
> 关联：game-design-doc SKILL.md §数值平衡

---

## §1 战斗公式

### 1.1 基础伤害公式

```
damage = (baseATK × skillMultiplier) - (targetDEF × defCoefficient)
if damage < 1: damage = 1  # min dmg 铁律
```

参数约定：
- `baseATK`：角色攻击力（含装备/ buff）
- `skillMultiplier`：技能倍率（普通攻击 = 1.0，大招 = 2.5~4.0）
- `targetDEF`：目标防御力
- `defCoefficient`：防御减免系数（推荐 0.3~0.7）

### 1.2 扩展公式（按需选用）

暴击：
```
if random() < critRate:
    damage = damage × (1.5 + critDmgBonus)
```

元素克制：
```
if elementAdvantage(element, targetElement):
    damage = damage × 1.5
elif elementDisadvantage(element, targetElement):
    damage = damage × 0.5
```

等级差修正（防越级）：
```
levelDiff = attackerLevel - targetLevel
if levelDiff > 0:
    damage = damage × (1 + levelDiff × 0.05)
else:
    damage = damage × (1 + levelDiff × 0.03)  # 负等级差惩罚较轻
```

### 1.3 回合数目标

| 战斗类型 | 目标回合数 | DPS 每回合伤害占比 |
|----------|-----------|-------------------|
| 杂兵战 | 2-4 回合 | bossHP × 0.3~0.5 / 回合 |
| Boss 战 | 8-15 回合 | bossHP × 0.08~0.12 / 回合 |
| 精英战 | 5-8 回合 | eliteHP × 0.15~0.2 / 回合 |

---

## §2 经济模型

### 2.1 货币产出-消耗表

| 货币 | 单局产出 | 单局消耗 | 净变化 | 通胀控制 |
|------|----------|----------|--------|----------|
| 金币 | 500 | 800~1000 | -300~-500 | 强化费用递增 15%/级 |
| 钻石 | 10 | 30 | -20 | 固定兑换比，无产出膨胀 |
| 体力 | 120 | 60~120 | 0~60 | 上限 120，溢出归零 |

通胀控制三件套：
1. **产出上限**：每日/每周/每赛季设产出 cap
2. **消耗递增**：强化/升级费用随等级递增（指数或线性 + 阶梯）
3. **回收机制**：限时商店/合成消耗/活动兑换回收冗余资源

### 2.2 付费-免费平衡

付费玩家 = 时间加速（非独占内容）。铁律：
- 非付费可获得全部 gameplay 内容（角色/关卡/剧情）
- 付费缩短获取时间，但不改变数值上限
- 皮肤/装饰 = 付费独占（OK），功能性道具 = 不可付费独占

---

## §3 成长曲线

### 3.1 经验值表

```
EXP_to_next_level(n) = baseEXP × (1 + curveRate)^{n - 1}
```

三种曲线选择：

| 曲线类型 | 公式特征 | 适用场景 |
|----------|----------|----------|
| linear | EXP(n) = a × n + b | 休闲游戏/短周期 |
| exponential | EXP(n) = a × (1 + r)^{n} | 长线养成/RPG/MMO |
| s-curve | 前期缓→中期陡→后期缓 | 教程友好 + 后期不崩 |
| log | 前期快→后期极慢 | 轻度游戏/放置类 |

### 3.2 属性成长

```
ATK(level) = baseATK × (1 + growthRate × (level - 1))
HP(level) = baseHP × (1 + growthRate × (level - 1))
```

### 3.3 等级 Cap

- 软 Cap：超出后经验需求翻倍，属性增长减半
- 硬 Cap：等级上限 99 / 100 / maxLevel
- 建议：Cap 设计为"核心内容完成时的等级 + 20%"，留出溢出版本更新空间

---

## §4 边界值验证

| 验证点 | 规则 | 计算 |
|--------|------|------|
| min dmg | damage ≥ 1（禁止零伤害） | ATK × 0.1 - DEF × 0.7 ≥ 1 |
| max dmg 不秒杀 boss | maxDmg ≤ bossHP × 0.35 | 全 buff 大招伤害 ≤ bossHP × 0.35 |
| break-even | 同等级 DPS vs Tank ≥ 3 回合 | Tank 存活回合 ≥ 3 |

break-even 公式：
```
Tank_survival_rounds = Tank_HP / (DPS_ATK × 1.0 - Tank_DEF × 0.5)
# 必须 ≥ 3，否则 Tank 定位无效
```

---

## §5 概率系统

### 5.1 保底机制（Pity System）

| 保底类型 | 规则 | 适用场景 |
|----------|------|----------|
| 硬保底 | 第 N 次必出 SSR | 抽卡系统 |
| 软保底 | 第 N 次起概率递增 | 抽卡系统 |
| 补偿保底 | 连续未触发后概率翻倍 | 掉落/暴击 |

### 5.2 伪随机分布（PRD）

```
P_actual(n) = P_base × n  # 每次失败后实际概率线性增加
# 防止"连续十次不暴击"的负面体验
```

### 5.3 非独立事件补偿

每次失败增加下次成功率，成功后重置。用于：暴击、闪避、掉落。
公式：`P(n) = min(P_base × n, 1.0)`，n 为连续失败次数。
