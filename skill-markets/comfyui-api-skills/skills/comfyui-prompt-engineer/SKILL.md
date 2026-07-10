---
name: comfyui-prompt-engineer
description: 针对 FLUX、SDXL、SD1.5、Wan 等不同模型优化提示词。处理身份保持方法（InstantID、PuLID、IP-Adapter、LoRA），给出各模型推荐的 CFG 缩放、负面提示词模板。结合角色档案提供上下文。用于提示词工程或提示词优化。
user-invocable: true
metadata: {"openclaw":{"emoji":"✍️","os":["darwin","linux","win32"]}}
---

# ComfyUI 提示词工程技能

为不同模型定制最优提示词，涵盖身份保持与负面提示词。

## 模型特定策略

### FLUX.2 / FLUX.1-dev

**特征**：
- 自然语言理解强
- 简洁提示词表现更佳
- 无需负面提示词（内置引导）

**正面提示词模板**：
```
{Sage}，{场景}，写实人像，{光线描述}，50mm 镜头，浅景深，
高细节，专业摄影
```

**参数建议**：
| 参数 | 范围 | 推荐 |
|------|------|------|
| 步数 | 20-50 | 28-35 |
| CFG | 1-5 | 3.0-3.5 |
| 采样器 | euler, uni_pc | uni_pc |
| 调度 | normal, sgm_uniform | sgm_uniform |
| 分辨率 | 1024-2048 | 1024x1024 |

**提示词示例**：
```
Sage 半身像，身穿棕色皮夹克，森林背景，金色阳光透过树叶，
写实风格，自然光，50mm 镜头，浅景深，专业摄影
```

### SDXL（RealVisXL、CyberRealistic 等）

**特征**：
- 需要短标签 + 详细描述
- 负面提示词关键
- 自然语言 + 标签混合

**正面提示词模板**：
```
{主体}, {详细特征}, {场景}, {光线}, {风格}
(masterpiece, best quality, photorealistic:1.4)
```

**负面提示词模板**：
```
(cartoon, painting, illustration, anime:1.3), (deformed, distorted:1.2),
(extra limbs, extra fingers, mutated hands:1.4), (blurry, low quality:1.3),
(watermark, text, signature:1.4)
```

**参数建议**：
| 参数 | 范围 | 推荐 |
|------|------|------|
| 步数 | 25-40 | 30 |
| CFG | 5-9 | 7.0 |
| 采样器 | dpmpp_2m, euler_ancestral | dpmpp_2m |
| 调度 | karras | karras |
| 分辨率 | 1024x1024 | 1024x1024 |

### SD1.5（已较少使用）

**特征**：
- 严重依赖标签
- 必用负面提示词
- 提示词长度受限（77 token）

**提示词示例**：
```
(masterpiece:1.3), (best quality:1.3), photorealistic, 1girl, auburn hair,
green eyes, freckles, leather jacket, forest, sunlight
Negative: (cartoon:1.3), (deformed:1.2), (extra fingers:1.4), blurry
```

### Wan 2.6 / Wan 2.2（图生视频）

**特征**：
- 视频提示词要描述**运动**
- 写明镜头运动
- 控制提示词长度（避免模型"忘记"主体）

**提示词模板**：
```
{主体}，{动作}，{场景}，{镜头运动}，{风格}
```

**提示词示例**：
```
Sage 慢慢转头微笑，森林中阳光斑驳，背景树叶轻微飘动，
电影感，特写镜头，稳定
```

### HunyuanVideo 1.5

**特征**：
- 中文支持好
- 详细场景描述
- 强调摄影术语

**提示词示例**：
```
一位 28 岁女性，赤褐色波浪长发，绿色眼睛，雀斑，
森林中金色阳光，半身像，专业人像摄影，85mm 镜头
```

## 身份保持方法

### InstantID

**适用**：SDXL 人脸一致性

**正面提示词结构**：
```
{角色名}, {稳定面部特征}, {场景}, {风格}
```

**技巧**：
- 描述人脸特征时**只写稳定特征**（脸型、眼距、痣的位置）
- 不写动态特征（表情、动作）
- 配合 IP-Adapter 增强相似度

### PuLID Flux II

**适用**：FLUX.1 双角色

**技巧**：
- 提示词中明确"two people"或"two characters"
- 为每个角色编号
- 使用 `character_1: Sage, character_2: Mike` 写法

**示例**：
```
两位人物并排站立，左侧 Sage 穿皮夹克，右侧 Mike 穿衬衫，
城市街道背景，街头摄影，浅景深
```

### IP-Adapter / IP-Adapter Plus

**适用**：通用风格/构图参考

**技巧**：
- IP-Adapter 强度 0.5-0.8
- 提示词描述**内容**，IP-Adapter 处理**风格/构图**
- 提示词与参考互补

### LoRA 角色

**提示词结构**：
```
{LoRA 触发词}, {场景}, {动态描述}
```

**强度范围**：
- 写实：0.7-0.9
- 风格化：0.5-0.7
- 过高会出现"过拟合"伪影

## 负面提示词模板库

### 通用负面

```
ugly, deformed, noisy, blurry, low contrast, low quality,
oversaturated, cropped, extra limbs, extra fingers, watermark
```

### 人像专用

```
(deformed face:1.3), (cross-eyed:1.2), (poor facial details:1.2),
(skin blemishes:1.1), (asymmetric eyes:1.3)
```

### 写实专用

```
(cartoon, anime, painting, illustration:1.4), (3d render:1.2),
(unrealistic lighting:1.2)
```

### 视频专用

```
(morphing, flickering:1.3), (temporal inconsistency:1.2),
(motion blur:1.1)
```

## 与角色档案协同

读取 `projects/{项目}/角色/{名}.yaml` 后：

- 把档案中的 `正面提示词模板` 套用
- 套用 `服装默认`
- 提示词结尾追加档案中的负面提示词

## 产出

输出应包含：

1. **正面提示词**（带权重标注）
2. **负面提示词**（如适用）
3. **推荐参数**（步数、CFG、采样器、调度）
4. **预期显存**（基于模型 + 分辨率）
5. **下游移交建议**（转给 workflow-builder 即可直接执行）

## 注意事项

- **不要过度堆砌**标签——FLUX 等模型更看重语义
- 提示词**具体化**——"绿眼睛"胜过"漂亮"
- **光线和镜头**描述显著提升写实感
- 多次实验后**记录成功组合**到 `有效组合`
