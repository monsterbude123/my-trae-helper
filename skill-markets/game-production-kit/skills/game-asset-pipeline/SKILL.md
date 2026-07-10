---
name: game-asset-pipeline
description: 游戏素材生成管线 — 引擎无关。覆盖素材预算规划、多后端 AI 图像生成（Gemini/Grok/Ark）、GLB 3D 模型生成（Tripo3D/Seed3D）、动画精灵管线、高级背景移除、BGM/SFX/语音、资产注册表与 5 层质量保证。引用 comfyui-api-skills 做图像/音频生成，voice-character-design 做音色设计，voice-acting-skill 做配音。触发词：游戏素材、立绘生成、背景生成、BGM生成、配音、TTS配音、3D模型、资产注册。
user-invocable: true
requires:
  skills: [comfyui-api-skills]
  optional: [voice-character-design, voice-acting-skill]
---

# 游戏素材生成管线

协调各类素材生成的**编排器**。引擎无关，不绑定 WebGAL / Ren'Py / Unity。

> 核心原则：**素材从角色宪法派生**，不独立设计。所有生成操作复用统一管线，禁止临时 ad-hoc 脚本。

## 核心铁律

```
1. 生成前先加载 comfyui-api-skills → 读对应模型族 yaml → 不要凭印象拼 workflow
2. TTS 配音前先加载 voice-character-design → 按 character-voice-card.md 走一遍
3. 先单张验证 → 小批量测流水线 → 再全量
4. 锚点先生成、审查后再衍生
5. 角色/道具用纯色背景（绝不 prompt "透明背景"），生成后用 BiRefNet 移除
6. 每个资产最多重试 3 次，第 3 次失败停下手动介入
7. 每个素材生成后在 ASSETS.md 中写入 source_version 和 Cost
```

## 素材类型与负责技能

| 素材类型 | 负责技能 | 说明 |
|----------|---------|------|
| 角色立绘 | `comfyui-api-skills`（首选）/ Gemini API（备用） | 图像生成 |
| 场景背景 | `comfyui-api-skills`（首选）/ Gemini API（备用） | 图像生成 |
| 标题图 | `comfyui-api-skills`（首选）/ Gemini API（备用） | 图像生成 |
| 3D 参考图 | Gemini API / Grok API | 用于 Tripo3D/Seed3D 输入 |
| GLB 3D 模型 | Tripo3D API / Seed3D API | 图像→3D 转换 |
| 动画精灵帧 | Gemini(参考+姿势) → Grok(视频) → ffmpeg → BiRefNet | 六步管线 |
| 纹理/道具 | Grok API | 低成本批量生成 |
| BGM | `comfyui-api-skills` | 音频生成，Stable Audio 3 |
| SFX / 环境音 | `comfyui-api-skills` | 音频生成 |
| 角色音色设计 | `voice-character-design` | 角色声线方法论 |
| 角色配音 | `voice-acting-skill` | TTS 配音管线 |

> **音频两个方向**：游戏音效/环境音（BGM/SFX/AMB）走素材管线；角色配音走 voice-character-design → voice-acting-skill。原则不同，不混用。

## 流程骨架

```
Phase 2 完整骨架（不可跳过）:
0.  视觉目标先行 → reference.png + art direction
1.  实体清单 → 从 story-design.md 扫描 → entity-inventory.md → 用户确认
2.  素材预算规划 → 锚点+衍生 → 成本估算 → 输出 ASSETS.md (含 Budget 段)
3.  风格确认 → 逐类型询问用户 → 参考图先行
4.  预算设置 → set_budget → 生成前 check_budget
5.  角色立绘生成 → 锚点 → rembg → 衍生
6.  背景/标题图生成
7.  纹理/道具 → Grok 批量
8.  BGM/SFX 生成 → ComfyUI 管线
9.  动画精灵生成 → 六步管线（需要时）
10. 3D 模型生成 → 参考图 → Tripo3D/Seed3D → GLB
11. 音色设计 → 加载 voice-character-design → 生成 voices.json
12. 配音合成 → 加载 voice-acting-skill → 生成语音文件
13. 质量保证链 → Layer 1 (prompt) → Layer 2 (style) → Layer 4 (registry)
14. 素材清洗 → 排除 QA 复合图、生成稿 → 产出最终素材目录
```

## 后端选择速查

| 后端 | 模型 | 成本/次 | 最佳用途 |
|------|------|---------|---------|
| Gemini (Google) | `gemini-3.1-flash-image-preview` | 5-15¢ | 参考图、角色设计、3D参考、精确构图 |
| Grok (xAI) | `grok-imagine-image` | 2¢ | 纹理、简单物体、道具、背景（精度不敏感） |
| Ark/Doubao (火山) | `doubao-seedream-4.5` | 3¢ | 替代方案 |
| Tripo3D/Seed3D | — | 40-57¢ | 图像→3D |

| 资产类型 | 推荐后端 | 成本/个 |
|----------|---------|---------|
| 视觉目标参考图 | Gemini 1K 16:9 | 7¢ |
| 角色立绘（锚点+衍生） | ComfyUI 本地 > Gemini 1K | 免费/7¢ |
| 3D 模型参考图 | Gemini 1K 1:1 | 7¢ |
| 背景/标题 | Gemini 2K 16:9 | 10¢ |
| 纹理/道具/UI 图标 | Grok 1K | 2¢ |
| 动画精灵参考+姿势 | Gemini 1K | 7¢ |
| 动画精灵视频 | Grok | 5¢/秒 |
| GLB 3D 模型 | Tripo3D P1 / Seed3D | 40-57¢ |

> 完整后端选择策略、锚点衍生模式、预算管理协议、超预算优先级 → `references/asset-generation-patterns.md`

## 预算管理协议

```
Step 1: 设置预算    set_budget 500
Step 2: 生成前检查   check_budget
Step 3: 生成后记录   record_spend → generation-log.json
Step 4: 超预算处理   按优先级排序（保留 > 切后端 > 降分辨率 > 推迟）
Step 5: 重试管理     每资产最多 3 次
Step 6: 日志持久化   assets/generation-log.json
```

> 成本速算表、ASSETS.md 完整模板、锚点+衍生协议 → `references/asset-generation-patterns.md`

## 质量保证链（5 层）

```
Layer 1: Prompt 质量检查（生成前）    → 关键词验证 + 负面词检测
Layer 2: 风格一致性检查（生成后）    → 0-1 评分，≥0.7 通过
Layer 3: 流水线就绪检查（资产规划前）→ 架构稳定性
Layer 4: 注册表完整性（门禁前）      → 文件存在 + 大小 + 格式
Layer 5: 视觉 QA（构建后）           → 截图 vs 参考图对比
```

> 各层详细阈值、必需关键词表、负面词清单（13 个）、3 种验证模式 → `references/asset-generation-patterns.md`

## 视觉目标先行

> 大量生成前先生成一张"游戏内截图风格"的参考图作为 art direction 锚点。

```
1. 描述最重要游戏时刻的画面
2. 用 Gemini 1K 16:9 生成 reference.png (7¢)
3. 审查确认 → 成为下游所有素材的视觉北极星
4. Art direction 写入 ASSETS.md 头部
```

> Prompt 规则、对象枚举、约束清单 → `references/asset-generation-patterns.md`

## 背景移除（rembg）

> **铁律**：NEVER prompt for "transparent background" — 生成器画 checkerboard。Always use solid color, then remove it.

| Regime | 触发条件 | 策略 |
|--------|---------|------|
| `trust` | BiRefNet 遮罩完整 | 直接使用 BiRefNet 输出 |
| `adapt` | 有背景残留 | BiRefNet + 颜色遮罩混合 |
| `color` | 背景颜色均匀 | 主要使用颜色遮罩 |

> BG 颜色策略（按场景选择）、批量模式、QA 验证 → `references/asset-generation-patterns.md`

## 动画精灵工作流

```
1. 参考图生成 (Gemini 1K, neutral pose, 一次性, 7¢)  → 仔细审查
2. 姿势帧 (Gemini 1K, image-to-image, 7¢/pose)        → 只 prompt 动作
3. 视频生成 (Grok, feed 姿势帧, 5¢/秒)               → 720p / 480p fallback
4. ffmpeg 提取帧
5. 循环裁剪 (find_loop_frame)
6. rembg 逐帧移除背景（批量模式）
```

> 链式动画约束、降尺度注意、详细六步协议 → `references/godogen-ark-pipeline.md`

## GLB 3D 模型生成

```
1. 生成 3D 参考图 (Gemini 1K, "3/4 front elevated, T-pose, plain BG, full body")
2. 上传 → Tripo3D/Seed3D API
3. 轮询任务状态 → 下载 GLB
4. Godot 导入（Scene Builder 模式）
5. 碰撞体用 BoxShape3D/SphereShape3D/CapsuleShape3D（禁止 create_convex_shape/trimesh）
```

## 素材规范速查

| 类别 | 规格 |
|------|------|
| 角色立绘 | RGBA PNG, 832x1216 |
| 背景 | 1216x832（或 1920x1080 标题级） |
| 标题 | 1920x1080 |
| 纹理 | 512²/1024² PNG/WebP，tileable |
| UI 图标 | 128x128 起步，2x 目标尺寸生成 |

> ANIMA 三件套、模型选择（运行时 `/object_info` 查询）、更多规范细节 → `references/asset-generation-patterns.md`

## 详细参考

- godogen-ark 全量 47 文件吸收 → `references/godogen-ark-pipeline.md`
- 资产生成模式（预算/锚点/成本/QA）：`references/asset-generation-patterns.md`
- 角色立绘/背景/标题细节 → `references/01-image-generation.md`
- BGM/SFX/AMB/FX 细节 → `references/02-audio-generation.md`
- TTS 配音集成 → `references/03-tts-integration.md`
- ComfyUI API 客户端：通过 `comfyui-api-skills` 技能提供
