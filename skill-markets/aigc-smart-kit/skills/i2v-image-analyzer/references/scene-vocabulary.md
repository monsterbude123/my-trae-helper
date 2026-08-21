# 画面识别词表(Scene Vocabulary)

> vision 模型分析图像时使用的标准词表。确保下游 prompt 生成的词汇可控 + 跨 vision 模型一致。

## §0 词表用途

vision 模型看到图时,优先用本词表内的词,避免自由发挥造成 prompt 输出词不可控。

## §1 场景类型(scene.type)

| 词 | 中文 | 典型特征 |
|----|------|----------|
| `indoor` | 室内 | 房间 / 走廊 / 餐厅 / 办公室 / 室内空间 |
| `outdoor` | 室外 | 街道 / 公园 / 山林 / 海滩 |
| `studio` | 棚拍 | 纯色背景 / 摄影棚 / 极简布景 |
| `abstract` | 抽象 | 概念 / 几何 / AI 生成 / 非物理空间 |

### §1.1 细分(subtype)

```
indoor:
  cafe / restaurant / bedroom / bathroom / office / corridor / lobby / mall / subway / train / car-interior / kitchen / library / studio-room
outdoor:
  urban-street / park / forest / beach / desert / mountain / rooftop / garden / alley / square / stadium / market
abstract:
  geometric / gradient / particle / concept / dream
studio:
  product-shot / portrait-studio / minimalist
```

## §2 景别(cinematography.framing)

| 词 | 中文 | 视觉特征 |
|----|------|----------|
| `extreme-wide` | 大远景 | 主体极小,环境主导 |
| `wide` | 远景 | 主体可见,环境为主 |
| `medium-wide` | 全景 | 主体 + 周围环境 |
| `medium` | 中景 | 主体腰部以上 |
| `medium-close` | 中近 | 胸部以上 |
| `close-up` | 近景 / 特写 | 面部 / 主体细节 |
| `extreme-close-up` | 大特写 | 局部(眼 / 手 / 道具) |

## §3 视角(cinematography.angle)

| 词 | 中文 | 视觉特征 |
|----|------|----------|
| `eye-level` | 平视 | 摄像机与主体眼睛等高 |
| `low-angle` | 仰视 | 摄像机在主体下方,显得主体高大 |
| `high-angle` | 俯视 | 摄像机在主体上方 |
| `bird's-eye` | 鸟瞰 | 接近正上方 |
| `dutch-angle` | 荷兰角 | 镜头倾斜,营造不安 |
| `over-the-shoulder` | 越肩 | 过肩镜头 |

## §4 构图(cinematography.composition)

| 词 | 中文 | 视觉特征 |
|----|------|----------|
| `rule-of-thirds` | 三分法 | 主体在三等分线交叉点 |
| `centered` | 居中 | 主体在画面正中 |
| `symmetric` | 对称 | 左右 / 上下对称 |
| `diagonal` | 对角线 | 动态 / 能量感 |
| `minimal` | 极简 | 大量留白 |
| `frame-within-frame` | 框中框 | 门 / 窗 / 拱门构图 |
| `leading-lines` | 引线 | 道路 / 走廊引导视线 |

## §5 光照(aesthetic.lighting)

| 词 | 中文 | 视觉特征 |
|----|------|----------|
| `natural-light` | 自然光 | 太阳 / 窗光 |
| `golden-hour` | 黄金时刻 | 日出后 / 日落前 1 小时 |
| `blue-hour` | 蓝调时刻 | 日出前 / 日落后 |
| `studio-light` | 棚拍光 | 软光箱 / 反光板 |
| `hard-light` | 硬光 | 强对比 / 明显阴影 |
| `soft-light` | 软光 | 柔和过渡 |
| `volumetric` | 体积光 | 透过雾 / 烟 / 树的光柱 |
| `neon` | 霓虹 | 城市夜景 |
| `candlelight` | 烛光 | 暖色低照度 |
| `backlight` | 逆光 | 主体背后 |
| `rim-light` | 轮廓光 | 描边光 |

## §6 调色(aesthetic.color_grade)

| 词 | 中文 | 视觉特征 |
|----|------|----------|
| `warm` | 暖调 | 黄 / 橙 / 红主导 |
| `cool` | 冷调 | 蓝 / 紫主导 |
| `teal-and-orange` | 蓝橙 | 电影感经典 |
| `high-contrast` | 高对比 | 黑白分明 |
| `low-contrast` | 低对比 | 灰度接近 |
| `desaturated` | 低饱 | 褪色感 |
| `vintage` | 复古 | 偏黄 / 偏绿 |
| `modern` | 现代 | 干净 / 高清 |
| `monochrome` | 单色 | 黑 / 白 / 单色 |
| `pastel` | 粉彩 | 浅色柔色 |

## §7 风格(aesthetic.style)

| 词 | 中文 | 视觉特征 |
|----|------|----------|
| `cinematic` | 电影感 | 调色 + 构图专业 |
| `photographic` | 摄影 | 真实 / 写实 |
| `illustration` | 插画 | 平面化 |
| `anime` | 二次元 | 日式动画 |
| `3D-render` | 3D 渲染 | CG |
| `oil-painting` | 油画 | 笔触 / 厚涂 |
| `watercolor` | 水彩 | 透 / 渗 |
| `minimal` | 极简 | 少元素 |
| `surreal` | 超现实 | 梦境 |

## §8 情绪(aesthetic.mood)

| 情绪族 | 词 |
|--------|----|
| **平静** | calm, peaceful, serene, contemplative, meditative |
| **温暖** | warm, cozy, intimate, nostalgic, tender |
| **紧张** | tense, anxious, suspenseful, urgent, dramatic |
| **欢快** | joyful, playful, energetic, vibrant, festive |
| **忧伤** | melancholic, somber, wistful, lonely, sad |
| **史诗** | epic, grand, awe-inspiring, majestic, cinematic |
| **神秘** | mysterious, ethereal, dreamlike, otherworldly |
| **浪漫** | romantic, dreamy, soft, intimate, tender |

## §9 可动元素(dynamic.movable_subjects 候选)

```
人: hair / expression / breathing / blinking / clothing-flap / gesture
自然: leaves / clouds / water-flow / waves / smoke / steam / dust / fog
物体: fabric-flow / liquid-pour / fire-flicker / light-flicker / shadow
动物: tail / ears / wing / step
```

## §10 推荐运镜(dynamic.recommended_camera_motion)

| 视觉场景 | 推荐运镜 |
|----------|----------|
| 静物 / 产品 | `static` 或 `pull back` 缓慢揭示 |
| 人物肖像 | `push in small amplitude slow` 强调表情 |
| 风景 | `arc shot small amplitude slow` 360° 揭示 |
| 动态元素(风 / 流水) | `tracking shot` 跟拍运动元素 |
| 街头 / 城市 | `handheld pan` 纪实感 |
| 多层景深 | `dolly in` 利用景深变化 |
| 高反差光线 | `static` 让光线本身成为主角 |

## §11 反例(MUST 避免)

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
```

## §12 来源

- 蒸馏自 5 平台 I2V prompt 实战:
  - [MiniMax H3 提示词指南](https://minimaxh3.studio/zh/guide/minimax-h3)
  - [Seedance 2.5 官方](https://www.seeddance.io/zh/seedance-2-5)
  - [Veo 3.1 prompt guide](https://www.veo3gen.app/blog/veo-31-image-to-video-prompts-that-actually-animate-not-just-wiggle-a-beginner-g)
  - [Kling 3.0 I2V](https://kling3.app/blog/how-to-use-kling-3-0-image-to-video)
  - [Vidu Q3 指南](https://juejin.cn/post/7650347918663860270)
- 跨平台词表收敛,优先选多源印证词