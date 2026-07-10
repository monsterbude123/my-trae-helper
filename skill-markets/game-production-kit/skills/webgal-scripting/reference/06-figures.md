# 六、立绘系统详解

## 6.1 位置

| 参数 | 位置 | 默认 id |
|:---|:---|:---|
| `-left` | 舞台左侧 | `fig-left` |
| 无参数 | 舞台中央 | `fig-center` |
| `-right` | 舞台右侧 | `fig-right` |
| `-id=xxx` | 自由立绘 | 自定义 id |

三个位置的立绘相互独立，需分别清除：
```webgal
changeFigure:none -left;
changeFigure:none;
changeFigure:none -right;
```

## 6.2 带 ID 的自由立绘

```webgal
changeFigure:test.png -left -id=test1;
changeFigure:none -id=test1;
```

## 6.3 立绘类型

- **图片立绘**：直接填图片路径（`.png` 等）
- **Live2D**：填 `.json` / `.model3.json` 模型路径
- **Spine**：填 `.skel` 路径，或 `.json?type=spine`

## 6.4 立绘嘴型同步

```webgal
; 1. 注册差分并上场
changeFigure:1/normal.png -id=charA -mouthOpen=1/mouth_open.png -mouthHalfOpen=1/mouth_half.png -mouthClose=1/normal.png;
; 2. 播放语音并驱动嘴型
角色A:你好，世界！ -vocal=charA_hello.wav -figureId=charA;
```

引擎根据语音实时音量在 `mouthOpen`/`mouthHalfOpen`/`mouthClose` 之间切换。`eyesOpen`/`eyesClose` 注册后自动触发随机眨眼。

## 6.5 变换与效果属性

完整效果属性参考：

| 类别 | 属性 | 默认值 | 范围 |
|:---|:---|:---|:---|
| 基础 | `position.x` | 0 | 画布像素 |
| 基础 | `position.y` | 0 | 画布像素 |
| 基础 | `rotation` | 0 | 弧度（顺时针正） |
| 基础 | `scale.x` | 1 | — |
| 基础 | `scale.y` | 1 | — |
| 效果 | `alpha` | 1 | 0-1 |
| 效果 | `blur` | 0 | 0-正无穷（像素） |
| 颜色 | `brightness` | 1 | — |
| 颜色 | `contrast` | 1 | — |
| 颜色 | `saturation` | 1 | — |
| 颜色 | `gamma` | 1 | — |
| 颜色 | `colorRed` | 255 | 0-255 |
| 颜色 | `colorGreen` | 255 | 0-255 |
| 颜色 | `colorBlue` | 255 | 0-255 |
| 泛光 | `bloom` | 0 | 0-正无穷 |
| 泛光 | `bloomBrightness` | 1 | — |
| 泛光 | `bloomBlur` | 0 | 0-正无穷（像素） |
| 泛光 | `bloomThreshold` | 0 | 0-1 |
| 倒角 | `bevel` | 0 | 0-1 |
| 倒角 | `bevelThickness` | 0 | 0-正无穷（像素） |
| 倒角 | `bevelRed/Green/Blue` | 255 | 0-255 |
| 滤镜 | `oldFilm` | 0 | 0-1（开关） |
| 滤镜 | `dotFilm` | 0 | 0-1（开关） |
| 滤镜 | `rgbFilm` | 0 | 0-1（开关） |
| 滤镜 | `glitchFilm` | 0 | 0-1（开关） |
| 滤镜 | `godrayFilm` | 0 | 0-1（开关） |
| 滤镜 | `reflectionFilm` | 0 | 0-1（开关） |
| 滤镜 | `shockwave` | 0 | — |
| 滤镜 | `radiusAlpha` | 0 | — |

## 6.6 缓动类型

| 值 | 说明 |
|:---|:---|
| `linear` | 线性 |
| `easeIn` | 缓入 |
| `easeOut` | 缓出 |
| `easeInOut` | 缓入缓出（默认） |
| `circIn` / `circOut` / `circInOut` | 圆形 |
| `backIn` / `backOut` / `backInOut` | 回弹 |
| `bounceIn` / `bounceOut` / `bounceInOut` | 弹跳 |
| `anticipate` | 预先反向 |

## 6.7 预置动画表

| 动画效果 | 动画名 | 持续时间(ms) |
|:---|:---|:---|
| 渐入 | `enter` | 300 |
| 渐出 | `exit` | 300 |
| 左右摇晃一次 | `shake` | 1000 |
| 从下侧进入 | `enter-from-bottom` | 500 |
| 从左侧进入 | `enter-from-left` | 500 |
| 从右侧进入 | `enter-from-right` | 500 |
| 前后移动一次 | `move-front-and-back` | 1000 |
| 模糊进入 | `blur` | 300 |
| 老电影滤镜 | `oldFilm` | 0 |
| 点状滤镜 | `dotFilm` | 0 |
| 反射滤镜 | `reflectionFilm` | 0 |
| 故障滤镜 | `glitchFilm` | 0 |
| RGB 分离滤镜 | `rgbFilm` | 0 |
| 光辉滤镜 | `godrayFilm` | 0 |
| 移除电影类滤镜 | `removeFilm` | 0 |
| 冲击波入场 | `shockwaveIn` | 2000 |
| 冲击波退场 | `shockwaveOut` | 2000 |
