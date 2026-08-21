# 9 类素材角色分配协议

> REF2V 的核心难点 = 多份素材不会自动分配职责。每份素材必须显式标 `@Image<N>` / `@Video<N>` / `@Audio<N>` + 在 prompt 说**它做什么**。
>
> 本文给出 9 类素材角色 + 决策树 + 让位协议。

---

## §1 角色分类总览

```
R1 ~ R6 → 静态图片(@Image)
M1 ~ M3 → 视频片段(@Video)
A1 ~ A3 → 音频片段(@Audio)
```

## §2 角色详细定义

### §2.1 R1 — 主体身份(面部)

```
@Image1 → 主角面容
职责:锁定主角五官 / 发型 / 肤色 / 特征
数量:全场唯一(MUST 1 张)
优先级:最高
```

**反例**:
- ❌ 上传 2 张不同人的脸让模型选 — 模型无法判别
- ❌ 把 R1 当成"参考脸"而不是"主角脸" — R1 必为 is the protagonist

### §2.2 R2 — 主体侧面 / 背面

```
@Image2 → 主角侧面 / 背面参考
职责:补充角色其他角度(防止侧脸镜头与 R1 不一致)
数量:0 或 1 张
优先级:次主
```

**用法**:
- 拍摄主角侧脸 / 背影时引用 R2
- 不引用时 R2 自动降级为场景 / 美学补充(用户主动声明)

### §2.3 R3 — 服装 / 造型

```
@Image3 → 主角服装 / 配饰
职责:锁定服装颜色 / 款式 / 配饰细节
数量:0 或 1 张
优先级:中等
```

**误区**:
- ❌ 把 R3 当 R1 用(图是衣服不是人脸 → 模型会按主角穿模特的逻辑处理)
- ✅ "She wears the outfit from @Image3: ..."

### §2.4 R4 — 场景 / 背景

```
@Image4 → 场景参考
职责:空间 / 地形 / 光照方向
数量:0 或 1 张
优先级:中等
冲突:与 R6 美学风格时常打架
```

**让位规则**:`@Image4` 提供空间结构,色彩风格让位给 `@Image6`。

### §2.5 R5 — 道具特写

```
@Image5 → 道具 / 工具 / 物件特写
职责:锁定关键物件外观
数量:0 或 1 张
应用:特写镜头时(@Image5 的细节与主角互动)
```

### §2.6 R6 — 美学 / 调色

```
@Image6 → 美学 / 调色参考
职责:画风 / 色调 / 质感 / 颗粒 / 镜头光晕
数量:0 或 1 张
优先级:覆盖整片
冲突:与 R4 场景时常冲突 → R6 让位或优先于 R4
```

### §2.7 M1 — 动作节奏(视频)

```
@Video1 → 动作 / 表情节奏参考
职责:参考运动速度 / 表情变化频率
限制:≤ 15s(H3 上限)
优先级:动作执行时主参考
```

**用法**:
- 主角动作模式 → "@Video1's slow-motion release"
- 表情节奏 → "@Video1 shows the micro-expression cadence"

### §2.8 M2 — 镜头运动(视频)

```
@Video2 → 运镜参考
职责:机位 / 节奏 / 切镜时机
限制:≤ 15s
优先级:运镜主参考
```

### §2.9 A1 — BGM 底色(音频)

```
@Audio1 → 配乐参考
职责:旋律 / 节奏 / 调性
限制:≤ 15s
优先级:整片统一
```

### §2.10 A2 — 环境音(音频)

```
@Audio2 → 环境音参考
职责:背景噪声 / 空间感
限制:≤ 15s
冲突:与 A3 对白时常混淆 → A2 必然被 SFX 抢戏
```

### §2.11 A3 — 对白 / SFX(音频)

```
@Audio3 → 对白 / 关键音效参考
职责:台词节奏 / 关键音触发
限制:≤ 15s
应用:用 S1 标签引用 + verbatim 引号
```

---

## §3 决策树:用户上传 N 份素材时如何分配

```
输入 N 份素材 → 决策树:
│
├─ 只有 2 张图?→ 看是不是首尾关系
│    ├─ 是 → first_last_frame 模式
│    └─ 否 → reference 模式(1 张 R1 + 1 张 R4 / R6)
│
├─ 只有 1 张图 + 1 段视频?→ reference
│    ├─ 视频是动作 → 视频 = M1,图 = R1
│    └─ 视频是机位 → 视频 = M2,图 = R1
│
├─ 3~9 张图? → 按以下优先级填充角色(从 R1 开始):
│    1 张必给 R1,其余按内容分配 R2 ~ R6
│
└─ 多视频? → 多个 M1 / M2(各自独立角色)
```

## §4 让位协议(冲突素材)

### §4.1 何时触发让位

```
- 2 张图都"看起来像主角"
- R4 场景 + R6 美学色调打架
- A1 BGM 激昂 + A2 环境音极安静
- 视频之间运动风格冲突(M1 慢动作 + M2 急速推进)
```

### §4.2 让位语句模板(写入 prompt)

```
主角优先级:
  "@Image1 is the primary subject; @Image3 provides only the costume reference."

美学让位:
  "Ignore @Image4's background style; apply @Image6's color grading throughout."

场景让位:
  "@Image5 sets the location; ignore @Image4's setting."

镜头让位:
  "Camera work follows @Video2's pattern; @Video1 is for motion timing only."

音频让位:
  "Background score follows @Audio1; @Audio2's ambient sound is muted."
```

### §4.3 让位的禁忌

```
❌ 用"我更喜欢..."这类主观词(模型看不到情绪)
✅ 用"ignore / apply / use only / muted"这类可执行指令

❌ 让位语句埋在描述中部(模型可能跳过)
✅ 写在 integrated_multimodal_description 开头

❌ 三方都不让位(模型无法判别)
✅ 优先级链至少 3 层清晰
```

---

## §5 上传素材数量 vs 角色覆盖度

```
理想:每份素材都有 1 个角色,角色不重复
最低:每份素材在 prompt 出现 ≥ 1 次(可以是让位句)
容许:某些素材被显式让位(只上传但不参与决策)
反例:上传但完全不引用(浪费槽位且模型可能乱用)
```

## §6 完整示例(6 张图 + 2 视频 + 2 音频)

```yaml
素材清单:
  @Image1: 主角正面照(锁定面容)
  @Image2: 主角侧面照(多角度)
  @Image3: 主角服装特写(米色风衣)
  @Image4: 咖啡店门口(场景参考)
  @Image5: 复古相机(道具)
  @Image6: 1980s 胶片色调图(美学)
  @Video1: 走路动作视频(动作节奏)
  @Video2: 推镜头视频(机位运动)
  @Audio1: 钢琴配乐(BGM)
  @Audio2: 雨声环境音

角色分配:
  R1 = @Image1(必为 is the protagonist)
  R2 = @Image2(补充)
  R3 = @Image3(服装)
  R4 = @Image4(场景)
  R5 = @Image5(道具)
  R6 = @Image6(美学)
  M1 = @Video1(动作)
  M2 = @Video2(运镜)
  A1 = @Audio1(BGM)
  A2 = @Audio2(环境音)
  H3 上限:10(< 12 ✓)
```

---

## §7 来源

- 平台 API: <https://platform.minimax.io/docs/guides/video-generation>
- H3 多模态预算(蒸馏自官方文档):images ≤ 9, videos ≤ 3, audio ≤ 3, mixed ≤ 12
