# Kling 3.0 — 元素绑定(element reference)协议

> Kling 3.0 提供的 element reference(subject binding)是**身份一致性的核心机制**。本文档定义绑定时机、标注写法、三视图策略、一致性提升技巧。

## §1 何时开启(决策树)

```
主体在 prompt 中承担"身份锚"角色?
  ├─ 是(角色面部 / 品牌 logo / 服装 / 道具细节)
  │   → 必开 element reference
  │   → Subject 句加 KEEP IDENTITY LOCKED
  │
  └─ 否(抽象风景 / 静物 / 无主体特写)
      → 不必开,描述外观即可
```

### §1.1 强制开启场景

| 场景 | 风险 | 修复 |
|------|------|------|
| 真人面部 | 5s 后漂到他人 | element reference + LOCKED |
| 品牌 logo | 变形 / 字符糊 | LOCKED + 单独参考图 |
| 服装花纹 | 花纹变形 | LOCKED + 三视图 |
| 宠物 / IP 角色 | 脸 / 体型漂移 | LOCKED + 多角度 |

### §1.2 不必开启场景

| 场景 | 理由 |
|------|------|
| 风景延时(云 / 水流 / 树叶) | 无主体身份 |
| 静物特写(产品不动) | 状态稳定 |
| 抽象纹理 / 烟雾 | 无身份概念 |

## §2 prompt 标注规范

### §2.1 三种 LOCK 等级

```
L1 弱标注(默许漂移):
  Subject: a woman in a navy jacket

L2 中标注(声明意图,模型有概率遵守):
  Subject: the woman in the navy jacket (keep face consistent)

L3 强标注(强制开启 element reference):
  Subject: the woman in the navy jacket (KEEP IDENTITY LOCKED)
  Subject: the product (LOCKED, no drift)
  Subject: <主体> (bind via element reference)
```

> ⚠️ **推荐 L3 强标注** — Kling 对 `LOCKED` / `bind` 关键词识别稳定。

### §2.2 多主体时的标注

```
多主体 + 部分锁定:
  Subject A: the man in the navy jacket (KEEP IDENTITY LOCKED)
  Subject B: the woman at the table (no binding — 路人,不需一致)

完整 prompt:
  Subject A: the man in the navy jacket (KEEP IDENTITY LOCKED)
  Subject B: a woman walking past (no binding)
  Movement: A raises his glass; B crosses the frame left to right
  Camera: medium shot, static
```

## §3 三视图策略(身份一致性强化)

> 单张首帧难以覆盖所有角度 — 当 5 秒后角色转身 / 侧脸时,身份一致性会下降。**三视图策略 = 前 / 侧 / 后 三张参考图**。

```
参考图组合(数量 ≤ 7,模型上限):
  [Image 1] 正面 — 锁定面部特征
  [Image 2] 侧面 — 锁定发型 / 耳部 / 侧脸轮廓
  [Image 3] 背面 — 锁定服装 / 体型(可选)

使用方式(image_mode = reference):
  images: [<正面>, <侧面>, <背面>]
  Subject: <角色名> (KEEP IDENTITY LOCKED via element reference)
```

### §3.1 三视图使用守则

| 守则 | 说明 |
|------|------|
| 背景统一 | 同光线 / 同背景,避免杂讯 |
| 服装一致 | 同一套服装,否则身份锚失效 |
| 表情中性 | 闭口 / 微张嘴,避免笑容锁死 |
| 构图相近 | 同焦距 / 同景别 |

## §4 一致性提升 5 技巧

### §4.1 单图 + 锁定的边界

```
单图足够: 主体始终正面 / 3/4 侧; 5s 内; 镜头温和(push-in / 静态)
单图不足: 360° 旋转; 15s + 多角度; 复杂动作 + 服装变化
→ 此时必须三视图
```

### §4.2 锁定意图的强化短语

```
模型识别率高:
  - "KEEP IDENTITY LOCKED"
  - "LOCKED, no drift"
  - "bind via element reference"
  - "consistent character throughout"
  - "same face, same outfit, no morphing"

避免弱短语(模型忽略):
  ❌ "keep the same look"  ❌ "don't change the appearance"  ❌ "consistent"
```

### §4.3 主体分解(身份锚 × 动作)

```
把"主体"在 prompt 中拆为两层:
  身份锚: who (Subject 句,KEEP LOCKED)
  动作层: what they do (Movement 句)

❌ "The barista in a white apron pours coffee, smile unchanged" 
    → 模型可能为维持表情而牺牲动作
✅ Subject: the barista in a white apron (KEEP IDENTITY LOCKED)
✅ Movement: she reaches for a cup, pours slowly, slides it forward
✅ Camera: close-up on her hands
```

### §4.4 服装变化的处理

```
场景:主体需换装

策略 A:两段式(两次生成 + 拼接)
  镜头 1: 白色围裙 → 主动作
  镜头 2: 黑色外套 → 主动作
  后期拼接

策略 B:同一镜内不换装(推荐)
  prompt 只描述单一服装,镜头切换用 transition 处理

❌ "Subject in white apron, then changes to black jacket"
  → 模型会模糊处理,身份锚失效
```

### §4.5 多人场景的优先级

```
1. 锁定主体(主视觉焦点)— KEEP IDENTITY LOCKED
2. 次要人物(环境元素)— 无需 LOCKED
3. 背景群众 — 模糊处理("crowd in the background")
❌ 3 个人物都 LOCKED → 模型预算分散,3 个都漂
✅ 只锁定 1 个,其他不标
```

## §5 与首尾帧联用

```
组合用法(高级):
  element reference    → 锁定身份(同一张脸)
  first_last_frame     → 锁定动作轨迹(精确运动)
  + Subject LOCKED     → 意图明示

示例:
  Subject: the man (KEEP IDENTITY LOCKED via element reference)
  Movement: he walks from the door to the window
  images: [<首帧:站在门口>, <尾帧:站在窗前>]
  image_mode: first_last_frame

适用:商业广告(产品展示轨迹精确 + 模特身份一致)
```

## §6 调试清单(身份漂移时)

```
1. Subject 句含 KEEP IDENTITY LOCKED? 否 → 加 L3 标注
2. element reference 开关开启? 否 → 平台打开 subject binding
3. 时长过长(15s 漂移概率上升)? 是 → 缩短到 10s 或拆分
4. 主动作 >2 个? 是 → 砍到 1-2 个清晰动作
5. 360° 旋转? 是 → 加 3 张三视图
6. 服装 / 背景每张图一致? 否 → 统一背景与光线
```

## §7 来源

- [Kling 3.0 I2V 官方实战](https://kling3.app/blog/how-to-use-kling-3-0-image-to-video)
- [Kling AI I2V Quickstart](https://kling.ai/quickstart/image-to-video-guide) — element reference 协议
- 蒸馏自主 SKILL.md §3 元素锁定协议