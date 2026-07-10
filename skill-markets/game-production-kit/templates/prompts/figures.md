# 角色立绘提示词模板

## 模型选择

> **模型不在此硬编码。** 生成立绘前，必须通过 ComfyUI `/object_info` 接口运行时查询可用模型。

**查询方式：**
```python
from comfy_client import ComfyClient
c = ComfyClient()
c.check_connection()
models = c.available_checkpoints()  # 返回 CheckpointLoaderSimple.ckpt_name 可选值列表
# 从 models 中选择合适的 checkpoint（优先 SDXL 角色类模型）
```

**选择优先级：**
1. SDXL 角色类模型（速度 ~15s，角色设计表达好）→ 优先
2. SDXL 插画类模型（画风更精致）→ 备选
3. FLUX 写实类模型 → 不推荐（已验证产出褪色）

**禁止在此模板中硬编码任何模型文件名。**

## 提示词结构

```
[质量锚定], [角色类型], [具体特征], [姿势构图], [背景要求], [画质收尾]
```

### 质量锚定（必须放在最前面）
`masterpiece, best quality, highly detailed, sharp focus, professional`

### 角色类型
`game character design sheet, digital illustration of [性别] [年龄描述], standing`

### 具体特征（必须从 story-design.md 逐条提取）
- 发型：`shoulder-length dark hair` / `short bob cut` / `long flowing silver hair`
- 服装：`wearing an elegant cream white dress` / `dark tactical jacket`
- 五官：`soft gentle features, warm smile` / `sharp determined eyes`
- 气质：`elegant quiet demeanor` / `intense focused expression`

### 姿势构图
`full body standing pose, front facing, centered composition`

### 背景要求
`flat solid white background, product shot style, isolated, clean`

### 画质收尾
`professional art, clean lines, solo character`

## 完整模板示例

### 示例 1：年轻女性角色（温柔画家型）
```
masterpiece, best quality, highly detailed, sharp focus, professional,
game character design sheet, digital illustration of a young Chinese woman, 24 years old, standing,
shoulder-length dark hair, soft gentle features, warm elegant smile,
wearing an elegant cream white dress, quiet graceful demeanor,
full body standing pose, front facing, centered composition,
flat solid white background, product shot style, isolated, clean,
professional art, clean lines, solo character
```

### 示例 2：幽灵/空灵版本
```
masterpiece, best quality, highly detailed, sharp focus, professional,
game character illustration of a young Chinese woman, 24 years old, ethereal appearance, standing,
shoulder-length dark hair, melancholic expression, sad gentle smile,
wearing a flowing white dress, luminous silver rim light around silhouette,
pale desaturated color palette, dreamlike atmosphere,
full body standing pose, front facing, centered composition,
flat solid white background, product shot style, isolated,
professional art, clean lines, solo character
```

### 示例 3：中年男性角色（咖啡馆老板型）
```
masterpiece, best quality, highly detailed, sharp focus, professional,
game character design sheet, digital illustration of a middle-aged Chinese man, 50 years old, standing,
short gray hair, weathered wise face, calm knowing expression,
wearing a dark brown apron over a simple white shirt, steady reassuring presence,
full body standing pose, front facing, centered composition,
flat solid white background, product shot style, isolated, clean,
professional art, clean lines, solo character
```

## 负面提示词模板
```
nsfw, ugly, deformed, blurry, low quality, bad anatomy, extra limbs,
watermark, text, messy background, distorted face, fused fingers,
multiple people, complex background, grayscale, monochrome
```
