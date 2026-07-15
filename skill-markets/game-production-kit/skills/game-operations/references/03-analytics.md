# 数据埋点与 Funnel

> 来源：游戏数据分析行业标准
> 关联：game-operations SKILL.md §骨架流程.3

引擎无关的数据埋点框架。必须在 game-design-doc 阶段预留埋点定义。

## §1 核心 Funnel

```
启动 App
  → 完成新手引导 (FTUE Completion)
  → 首次付费 (First Purchase)
  → 第 2 次付费 (Repeat Purchase)
  → 第 7 日留存 (D7 Retention)
  → 第 14 日留存 (D14 Retention)
  → 第 30 日留存 (D30 Retention)
```

| 阶段 | 事件名 | 关键参数 |
|------|--------|---------|
| 启动 | `game_launch` | device_id, platform, version |
| 新手引导 | `tutorial_step` | step_id, duration_s, skip |
| 引导完成 | `ftue_complete` | total_duration_s |
| 首次付费 | `first_purchase` | item_id, price, currency |
| 重复付费 | `purchase` | item_id, price, is_first |
| 关卡完成 | `level_complete` | level_id, score, duration_s, deaths |
| 会话结束 | `session_end` | duration_s, actions_count |

## §2 事件定义模板

```yaml
event:
  name: "level_complete"          # 事件名（snake_case）
  trigger: "关卡结算界面出现"     # 触发时机
  params:
    - level_id: string            # 关卡 ID
    - score: int                  # 得分
    - duration_s: float           # 耗时（秒）
    - deaths: int                 # 死亡次数
    - stars: int                  # 星级评价 (1-3)
  sample_rate: 1.0                # 采样率 (0.0~1.0)
  privacy: "analytics"            # analytics / necessary / personal
```

**隐私分级**：

| 级别 | 范围 | 需 opt-out |
|------|------|-----------|
| `necessary` | 崩溃/性能/基础功能 | 否 |
| `analytics` | 玩法数据/Funnel | 是（GDPR） |
| `personal` | 可关联到个人身份 | 是（需显式同意） |

## §3 关键指标

| 指标 | 定义 | 基准 |
|------|------|------|
| **DAU** | 每日活跃用户 | — |
| **MAU** | 每月活跃用户 | — |
| **DAU/MAU** | 用户粘性 | >20% 健康 |
| **ARPU** | 每用户平均收入 | — |
| **ARPPU** | 每付费用户平均收入 | — |
| **LTV** | 用户生命周期价值 | LTV > 3×CAC |
| **Churn Rate** | 流失率（D7/D14/D30） | D7<60%, D30<80% |
| **Session Length** | 平均会话时长 | 视品类而定 |
| **FTUE Completion** | 新手引导完成率 | >80% |
| **Conversion Rate** | 免费转付费率 | 视品类 2-10% |

## §4 A/B 测试框架

```
1. 定义假设：改变 X → 影响 Y
2. 分流：控制组 50% / 实验组 50%
3. 最小样本量计算（power=0.8, α=0.05）
4. 运行 ≥ 最小时间（≥1 完整周期，通常 7-14 天）
5. 置信度 ≥ 95% → 结论有效
6. 回滚条件：指标恶化 >5% / 崩溃率上升 >1%
```

## §5 隐私合规

| 法规 | 关键要求 |
|------|---------|
| **GDPR** (EU) | 明确同意 + opt-out + 数据删除权 + 数据可携权 |
| **CCPA** (California) | 不出售个人信息权 + 删除权 |
| **PIPL** (中国) | 最小必要原则 + 单独同意 + 本地化存储 |
| **COPPA** (US) | 13 岁以下禁止数据采集 |

**数据存储**：

```
分析数据存储位置需在 Privacy Policy 中声明。
中国大陆运营 → 数据存储在中国境内服务器。
GDPR 区域 → 优先 EU 境内服务器或 EU-US DPF 认证。
```
