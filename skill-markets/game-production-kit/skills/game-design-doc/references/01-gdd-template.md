# GDD 结构模板

> 来源：通用游戏设计行业标准（Stone Librande One-Page GDD + 网易/米哈游内部模板综合）
> 关联：game-design-doc SKILL.md §骨架流程

---

## §1 GDD 标准章节

| # | 章节 | 用途 | 产出格式 |
|---|------|------|----------|
| 1 | Elevator Pitch | 2 句话概括游戏：谁/做什么/为什么有趣 | 纯文本 |
| 2 | Core Loop | 核心循环 Action→Reward→Growth 三阶段 | 流程图 + 公式 |
| 3 | Gameplay Pillars | 3 个设计支柱（如：探索/战斗/叙事），每个 1 句话 | 列表 |
| 4 | Character Roster | playable 角色 gameplay 维度（HP/ATK/DEF/技能/定位） | 表 |
| 5 | Level Flow | 关卡流程图（线型/分支/开放）+ 难度曲线 | 流程图 + 参数表 |
| 6 | Economy | 货币种类/产出渠道/消耗渠道/通胀控制 | 产出-消耗表 |
| 7 | Progression | 成长曲线公式 + 等级 cap + 解锁节奏 | 公式 + 表 |
| 8 | UI/UX Mockup | 主界面线框图（HUD/菜单/战斗界面） | ASCII 线框图 |
| 9 | Monetization | 付费点设计（如有）/ 广告 / DLC 规划 | 列表 |
| 10 | Tech Specs | 目标帧率/分辨率/平台/引擎/多人架构 | 键值对 |

## §2 各章节详细说明

### 2.1 Elevator Pitch

2 句话：第 1 句说玩法（"玩家做什么"），第 2 句说趣味（"为什么好玩"）。

```
"玩家在随机生成的地牢中探索、战斗、收集遗物，每次死亡后永久升级基地。
核心趣味在于'高风险决策'——每次选择都可能让你离通关更近或直接死亡。"
```

### 2.2 Core Loop

格式：Action → Reward → Growth。产出 1 张流程图 + 1 句话解释每个阶段。

```
[探索] → [战斗] → [掉落] → [升级] → 回到[探索]
   │        │        │        │
   └─ 风险 ─┴─ 消耗 ─┴─ 随机 ─┘
```

### 2.3 Gameplay Pillars

3 个支柱，不多不少。每个支柱对应一个核心情感体验：

| 支柱 | 核心体验 | 实现方式 |
|------|----------|----------|
| 探索 | 好奇心驱动 | 隐藏区域、环境叙事、收集品 |
| 战斗 | 策略感与爽快感 | 克制链、连击系统、必杀演出 |
| 成长 | 获得感 | 技能树、装备升级、图鉴收集 |

### 2.4 Character Roster

每个 playable 角色填写一张 gameplay 卡：

| 角色 | 定位 | HP | ATK | DEF | SPD | 技能数 | 成长曲线 |
|------|------|-----|------|------|------|--------|----------|
| 战神 | DPS | 800 | 120 | 60 | 90 | 4 | linear |
| 圣骑 | Tank | 1500 | 60 | 150 | 50 | 3 | s-curve |

### 2.5 Level Flow

关卡流程图 + 逐关卡参数矩阵（详见 references/04-level-design.md）。

### 2.6 Economy

至少定义 3 种资源：软货币（金币）、硬货币（钻石）、特殊资源（体力/钥匙）。

| 资源 | 产出渠道 | 消耗渠道 | 单日产出上限 | 通胀控制 |
|------|----------|----------|-------------|----------|
| 金币 | 战斗/任务 | 装备强化 | N | 强化费用递增 |
| 钻石 | 成就/付费 | 抽卡/加速 | M | 固定兑换比 |

### 2.7 Progression

经验公式：`EXP_to_level(n) = baseEXP × (1 + curve × n)`
属性成长：`ATK(n) = baseATK × (1 + growthRate × (n - 1))`

### 2.8 UI/UX Mockup

ASCII 线框图，标注关键 UI 元素位置。不做美术——只标功能块。

```
┌──────────────────────────────┐
│ [HP 条]        [MP 条]       │  ← 状态栏
│                              │
│         [战斗画面]            │
│                              │
│ [技能1] [技能2] [技能3] [道具] │  ← 指令栏
└──────────────────────────────┘
```

### 2.9 Monetization

仅在有商业需求时填写。标注付费点 + 非付费玩家获取路径。

### 2.10 Tech Specs

```yaml
target_platform: PC / Mobile / Console
target_fps: 60
resolution: 1920x1080
engine: Godot 4.3
multiplayer: none / P2P / dedicated_server
```

## §3 GDD 版本管理

GDD 版本号与 story-design.md 对齐，同步递增。game-design.md 文件头部包含版本号：

```markdown
# Game Design — {游戏标题}
版本: v{N} | 最后变更: YYYY-MM-DD | 对齐 story-design v{N}

## 变更日志
| 版本 | 时间 | 变更内容 | 影响范围 |
|------|------|---------|---------|
```
