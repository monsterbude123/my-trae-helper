# 冲突解决 4 步法

> REF2V 的最大风险 ≠ 单图 I2V 的主体漂移,而是**多素材打架**。本文给出 4 步识别 + 解决协议。

---

## §1 为什么冲突必然出现

```
只要上传 ≥ 2 份素材,冲突概率 ≥ 50%:
  - 2 张图都有"主角脸"特征 → 模型无法判定谁是 is the protagonist
  - 场景图美学色调 vs 美学参考图色调 → 整体色彩两套规则
  - BGM 节奏 ≠ 实际动作速度 → 音画分裂
  - 视频 1 慢动作 vs 视频 2 急速推镜 → 机位运动不确定
```

不解决冲突 = 模型只能用 1 份 + 自己猜其余。

## §2 4 步法总览

```
Step 1:识别冲突(谁 / 美学 / 动作 / 镜头 / 声音 5 维度任一冲突)
Step 2:优先级排序(身份 > 美学 > 动作 > 镜头 > 声音)
Step 3:让位(写明"低优先级素材如何让位")
Step 4:标注让位关系(写入 prompt 开头)
```

## §3 Step 1 — 5 维度冲突识别

### §3.1 主角多个?

```
触发:2+ 张图 R1 角色(都"像主角")
识别:用户上传的人脸图 ≥ 2 张
```

### §3.2 风格打架?

```
触发:R4(场景)与 R6(美学)色调不一致
识别:写实场景 + 赛博朋克调色 / 室内 + 室外光线
```

### §3.3 动作混乱?

```
触发:多视频素材动作风格不一致
识别:@Video1 慢动作 + @Video2 急速推进 / 多视频主角不一致
```

### §3.4 镜头打架?

```
触发:多视频运镜方式冲突
识别:@Video1 推镜 + @Video2 拉镜 + 主角行为不一致
```

### §3.5 声音混乱?

```
触发:A1 BGM 与 A2 环境音冲突
识别:BGM 激昂 + 环境音极安静 / 多音频类型重复
```

## §4 Step 2 — 优先级排序

```
身份(谁)        — R1 必为最高
  ↓
美学(长什么样)  — R6 美学覆盖全片
  ↓
动作(做什么)    — M1 动作节奏
  ↓
镜头(怎么看)    — M2 运镜参考
  ↓
声音(听起来怎样) — A1 / A2 / A3
```

**铁律**:高优先级永远不让位,低优先级主动声明让位。

## §5 Step 3 — 让位模板

### §5.1 主角优先级让位

```
"@Image1 is the primary subject; @Image3 provides only the costume reference."
```

### §5.2 美学让位

```
"Ignore @Image4's background palette; apply @Image6's color grading throughout."
```

### §5.3 场景让位

```
"@Image5 sets the location; ignore @Image4's setting."
```

### §5.4 镜头让位

```
"Camera work follows @Video2's pattern; @Video1 is for motion timing only."
```

### §5.5 音频让位

```
"Background score follows @Audio1; @Audio2's ambient sound is muted."
```

### §5.6 多维让位(完整示例)

```
"@Image1 is the primary subject (@Image3 provides costume only).
Color grading follows @Image6, ignoring @Image4's palette.
Camera work follows @Video2; @Video1 governs motion timing only.
Background score follows @Audio1; @Audio2 is muted."
```

## §6 Step 4 — 让位语句的写作位置

```
MUST 写:integrated_multimodal_description 开头(最前 3 句话内)
NOT 写:藏在描述中段 / 写在 soundscape / 写在 music

原因:模型先读 description → 让位语句早于动作描述 = 优先级意识贯穿全片
```

## §7 完整冲突示例 + 让位 prompt

### §7.1 场景:主角面部冲突

```yaml
素材:
  @Image1: 女生 A 的正面照(红色长发)
  @Image2: 女生 B 的侧面照(黑色短发)
  @Image3: 巴黎街景

冲突:2 张不同人脸,谁是主角?
让位 prompt:
  "@Image1 is the primary subject (red hair, front-facing).
  @Image2 is referenced only for side-profile continuity.
  She walks through @Image3's Parisian street."
```

### §7.2 场景:美学冲突

```yaml
素材:
  @Image1: 主角正面
  @Image4: 暗色调哥特建筑
  @Image6: 日落暖色胶片调

冲突:暗色调 vs 暖色调 = 2 套风格
让位 prompt:
  "@Image1 is the protagonist. The scene's color palette follows @Image6
  (warm Kodak Gold tones). Lighting follows @Image4's direction but in
  warm, not cold tones."
```

### §7.3 场景:镜头 + 音频冲突

```yaml
素材:
  @Video1: 主角快速奔跑
  @Video2: 缓慢推镜头
  @Audio1: 快节奏电子 BGM
  @Audio2: 安静雨声

冲突:快动作 + 慢镜头 + 快 BGM + 安静雨声 = 4 重矛盾
让位 prompt(优先级链):
  "Subject (from @Image1) runs at @Video1's fast pace.
  Camera follows @Video2's slow push-in (creates dramatic deceleration feel).
  Background score follows @Audio1 (electronic tempo).
  @Audio2 rain ambience is muted (not zero — soft whispers only)."
```

## §8 冲突未解决 = 失败预测

| 现象 | 根因 | 修复 |
|------|------|------|
| 主角脸在两帧间换人 | 没有"R1 唯一"声明 | 加 §5.1 让位句 |
| 色调在镜头中突变 | R4 vs R6 没让位 | 加 §5.2 让位句 |
| 推镜 + 拉镜穿插 | M2 没让位 | 加 §5.4 让位句 |
| BGM 听不见 | A1 / A2 音量冲突 | 加 §5.5 让位句 |
| 模型乱用上传素材 | 某些素材不引用 | 用 §5 让位明确弃用 |

---

## §9 来源

- 蒸馏自 MiniMax H3 官方多模态参考指南 + 实战案例
- 与 [material-role-binding.md](material-role-binding.md) §4 让位协议对应
