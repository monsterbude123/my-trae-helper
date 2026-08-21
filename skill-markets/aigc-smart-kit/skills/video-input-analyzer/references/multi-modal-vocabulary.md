# 多模态视觉词表(Multi-Modal Vocabulary)

> **定位**:`video-input-analyzer` 在 vision 模型分析时使用的标准词表(v2.0)。
> **不重复**:v1.0 词表 → [../i2v-image-analyzer/references/scene-vocabulary.md](../../i2v-image-analyzer/references/scene-vocabulary.md);本文扩展多模态场景 / 视频关键帧 / 音频节奏 / ref2v 角色分配的词表。

## §0 词表用途

vision 模型分析多模态输入时,优先用本词表内的词,确保下游 prompt 生成的词汇可控 + 跨 vision 模型一致。

## §1 视频关键帧描述词

### §1.1 镜头状态

| 词 | 中文 | 含义 |
|----|------|------|
| `static` | 静止 | 机位不动 |
| `pan-left` / `pan-right` | 左 / 右摇 | 机位水平旋转 |
| `tilt-up` / `tilt-down` | 上 / 下倾 | 机位垂直旋转 |
| `zoom-in` / `zoom-out` | 推 / 拉 | 焦距变化 |
| `push-in` / `pull-out` | 推进 / 拉远 | 机位物理移动 |
| `tracking` | 跟拍 | 跟随主体 |
| `handheld` | 手持 | 不稳定感 |
| `orbit` | 环绕 | 围绕主体旋转 |

### §1.2 主体状态

| 词 | 中文 | 含义 |
|----|------|------|
| `entering-frame` | 入画 | 主体刚出现 |
| `leaving-frame` | 出画 | 主体离开 |
| `mid-action` | 动作中 | 主动作进行中 |
| `paused` | 静止 | 主体不动 |
| `turning` | 转身 | 旋转动作 |
| `facing-camera` | 对镜 | 面向镜头 |

## §2 音频特征词

### §2.1 节奏类别

| 词 | 中文 | 含义 |
|----|------|------|
| `steady-rhythm` | 稳定节奏 | 节拍规律 |
| `syncopated` | 切分 | 不规则重音 |
| `accelerating` | 渐快 | 节奏渐快 |
| `decelerating` | 渐慢 | 节奏渐慢 |
| `silence` | 静音 | 无声音 |
| `ambient-only` | 仅环境音 | 无音乐 |

### §2.2 乐器 / 风格

| 词 | 中文 | 典型用途 |
|----|------|----------|
| `piano` | 钢琴 | 抒情 / 温暖 |
| `strings` | 弦乐 | 史诗 / 浪漫 |
| `guitar-acoustic` | 木吉他 | 温暖 / 民谣 |
| `brass` | 铜管 | 史诗 / 力量 |
| `drums` | 鼓 | 紧张 / 节奏 |
| `synth` | 合成器 | 现代 / 科幻 |
| `percussion` | 打击乐 | 节奏 / 紧张 |
| `vocal-hum` | 人声哼鸣 | 神秘 / 抒情 |

### §2.3 情绪词(音频视角)

```
warm / cool / bright / dark / uplifting / melancholic / tense / playful / mysterious / epic
```

## §3 ref2v 角色分配词表(供 vision 提示)

### §3.1 角色 → 视觉特征

| 角色 | vision 应该识别的视觉特征 |
|------|-------------------------|
| `character_identity` | 高清人脸特写 / 产品三视图 / 主体面部清晰 |
| `scene_aesthetic` | 场景主导 / 色调统一 / 美学风格明确 |
| `motion_reference` | 多角度 / 视频 / 连续动作 |
| `rhythm_ambient` | 节拍清晰 / 旋律明显 |
| `first_last_frame` | 2 张图(可对比首尾状态变化) |
| `style_transfer` | 单图(目标风格清晰) |
| `extension_prior` | 单视频(末帧可衔接) |

### §3.2 分配原则提示词(给 vision)

```
vision prompt 强制要求:
  - 对每张图 / 视频 / 音频,先识别"主导信息"(subject / scene / motion / rhythm)
  - 然后匹配到角色候选(character_identity / scene_aesthetic / motion_reference / rhythm_ambient)
  - 输出 rationale(为什么是这个角色)
```

## §4 跨模态一致性词表

### §4.1 视觉 → 视觉一致性

```
多图分析时:
  SAME ART STYLE       跨图风格锚
  SAME CHARACTER       主体身份一致
  SAME COLOR PALETTE   色调一致
  SAME LIGHTING        光线一致
```

### §4.2 视觉 → 音频一致性

```
视频 + 音频分析时:
  MOTION-RHYTHM MATCH  主体运动节拍与音频节拍一致
  AUDIO-MOOD MATCH     音频情绪与视觉情绪一致
  SCENE-AUDIO MATCH    场景环境音与视觉场景一致
```

### §4.3 多图角色锚定

```
跨图角色锚定:
  PRIMARY_CHARACTER   主体(锁定身份)
  SECONDARY_CHARACTER 配角
  BACKGROUND          背景元素
  PROP                道具(可被多个主体引用)
```

## §5 速查 — 反例(MUST 避免)

```
❌ 自由发挥词:"看起来很高级" / "氛围感拉满"
   → vision 输出下游包装 prompt 时不可控

✅ 标准词:"cinematic, warm teal-and-orange, contemplative"
   → 严格用词表内词

❌ 多义混淆:"close-up of a person"
   → close-up 是景别,不是位置

✅ 区分清晰:
   framing = close-up (景别)
   position = center-frame, eye-level (位置)
   angle = eye level (视角)

❌ 角色分配模糊:"这张图很重要" 
   → 必须从 §3.1 候选值选一个

✅ 角色清晰:"role=character_identity, 主体脸部特写"
```

## §6 来源

- 蒸馏自 `i2v-image-analyzer/references/scene-vocabulary.md`(v1.0 词表)
- 扩展:视频关键帧描述 / 音频特征 / ref2v 角色分配 / 跨模态一致性
- 跨平台实战:MiniMax H3 / Seedance 2.5 / 可灵 3.0 / Vidu Q3 / 万相 2.7
- 创建日期:2026-08-20
