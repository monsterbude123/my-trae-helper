# 资产生成模式

> 合成自 godogen-ark asset-planner + asset-gen + asset_manager + CC Studio asset-spec + art-bible。深度细节见 `references/godogen-ark-pipeline.md`。

---

## 预算规划模式

### 锚点与衍生 (Anchor & Derive)

来自 godogen-ark asset-planner。不逐个独立生成素材，而是先生成一个"英雄素材"作为风格锚点，再以此为 `--image` 参考生成同系列素材。

```
Step 1: 生成锚点素材 (Gemini 1K 高精度, 角色/场景各一个)
Step 2: 审查锚点 → 确认风格、色彩、细节
Step 3: 用锚点作为参考图 → 衍生同系列素材
```

**常见衍生模式**:
- **风格家族**: 所有立绘共享同一锚点参考
- **多视角**: 锚点正面 → 衍生侧面/背面
- **变体**: 锚点正常 → 衍生愤怒/笑/哭表情
- **场景一致性**: 场景 A 锚点 → 同建筑风格的场景 B/C
- **动画链式**: 第 1 动作末尾帧 → 第 2 动作起始帧（链深度 ≤ 2）

### 多后端选择策略

来自 godogen-ark asset-gen 三后端成本模型。详见 `references/godogen-ark-pipeline.md` §三。

| 后端 | 成本 | 精度 | 最佳用途 |
|------|------|------|---------|
| Gemini | 5-15¢ | 高 | 角色、参考图、3D参考、精确构图 |
| Grok (xAI) | 2¢ | 中 | 纹理、道具、背景（精度不敏感） |
| Ark/Doubao | 3¢ | 中 | 替代方案 |
| Tripo3D | 40-50¢ | — | 图像 → GLB 3D 模型 |
| Seed3D | ~40¢ | — | 图像 → GLB 3D 模型（替代） |

### 成本分级

| 用途 | 策略 | 原因 |
|------|------|------|
| 角色立绘（锚点） | Gemini 1K / ComfyUI 本地 | 一次生成，锚定全局 |
| 批量纹理/道具 | Grok 2¢/个 | 数量大，单个体积小 |
| 场景背景 | Gemini 2K 16:9 | 宽屏构图，细节多 |
| 动画精灵 | Gemini 参考+姿势 + Grok 视频 | 锚点保证帧间一致 |
| 标题图 | Gemini 2K | 第一印象，一次性 |
| 3D 模型 | Tripo3D P1 50¢ | 全 3D 资产 = 参考 7¢ + GLB 50¢ |

### 成本速算

- **完整 3D 资产** = Gemini 参考 7¢ + GLB 40-50¢ = **47-57¢**
- **动画精灵** = ref 7¢ + pose 7¢ + video 5¢×N秒 + 免费处理
- **角色立绘 10 表情** = 锚点 7¢ + 9 衍生 × 7¢ = **70¢**
- **场景背景 5 张** = 5 × 10¢ = **50¢**

### 预算管理协议

```
设置预算:     set_budget 500  # $5.00
生成前:       check_budget → 剩余足够？
生成后:       record_spend → generation-log.json
超预算:       保留 > 切后端 > 降分辨率 > 推迟
重试:         1 免费检测 + 2 付费重试 = 3 次上限
日志持久化:   assets/generation-log.json
```

---

## 资产注册表模式 (Asset Registry)

来自 godogen-ark asset_manager。详见 `references/godogen-ark-pipeline.md` §四。

### 资产类型 (10 种)

`texture` | `sprite` | `character` | `animated_sprite` | `three_d_model` | `background` | `ui_icon` | `ui_panel` | `game_logo` | `item_kit`

### 状态生命周期 (4 状态)

```
pending → generated → approved → (最终)
                   ↘ rejected → pending (重新生成)
```

### 质量保证链 (5 层)

```
Layer 1: Prompt 质量检查 (按资产类型必需关键词 + 13 负面关键词)
Layer 2: 风格一致性检查 (已批准资产关键词频次 → 评分 0-1)
Layer 3: 流水线就绪检查 (PLAN.md Risk Tasks 全完成)
Layer 4: 注册表完整性 (文件存在 + 大小 + 格式)
Layer 5: 视觉 QA (截图 vs 参考图, Static/Dynamic/Question)
```

### 风格一致性算法

```python
# 从已批准资产 prompt 提取风格关键词 → Counter.top_n
approved_keywords = registry.extract_style_keywords()

# 检查新 prompt 匹配度
found = sum(1 for w in approved_keywords if w.lower() in new_prompt.lower())
score = found / len(approved_keywords)

# 判定
>= 0.7 → PASS (通过)
0.4-0.7 → WARNING (警告，建议补充风格关键词)
< 0.4 → REJECT (拒绝，重新调整 prompt)
```

---

## 视觉目标先行 (Visual Target First)

来自 godogen-ark visual-target。在大量生成素材前，先生成一张"游戏内截图风格"的参考图。

**Prompt 规则**:
- 枚举每个游戏对象，标注位置和相对大小
- 反映真实技术约束（无体积光/运动模糊/景深）
- 排除不会构建的内容
- 展示 HUD/UI 元素
- **不要** prompt "placeholder"、"concept art"、"mockup"

**输出**: `reference.png` (Gemini 1K 16:9, 7¢) + art direction 写入 ASSETS.md 头部。

---

## 素材清单格式 (ASSETS.md)

来自 godogen-ark + CC Studio。每类素材独立表格，必须包含 `Size` + `Cost` + `Status` 列。

```markdown
# Assets
**Art direction:** <美术方向一句话描述>
**Budget:** $X.XX total | $X.XX spent | $X.XX remaining

## 角色立绘
| Name | Description | Size | Image | Source Ver | Cost | Status |
|------|-------------|------|-------|------------|------|--------|
| elise_normal | 红色长发少女 锚点 | 832x1216 | figure/elise_normal.png | v3 | 7¢ | approved |
| elise_smile | 微笑表情 衍生 | 832x1216 | figure/elise_smile.png | v3 | 7¢ | pending |

## 场景背景
| Name | Description | Size | Image | Source Ver | Cost | Status |
|------|-------------|------|-------|------------|------|--------|
| library_01 | 魔法图书馆全景 | 1216x832 | background/library_01.png | v3 | 10¢ | generated |

## BGM / SFX
| Name | Description | Duration | File | Source Ver | Cost | Status |
|------|-------------|----------|------|------------|------|--------|
| bgm_title | 标题画面主题 | 2:30 | bgm/s_Title.mp3 | v3 | — | generated |

## 角色配音
| Name | Character | Lines | Format | Source Ver | Status |
|------|-----------|-------|--------|------------|--------|
| elise_lines | elise | 42 条 | OGG | v3 | pending |
```

**字段说明**:
- `Source Ver`: story-design.md 的版本号，追踪素材漂移
- `Cost`: 生成成本（¢），ComfyUI 本地生成为 "—"
- `Status`: pending/generated/approved/rejected

---

## 实体清单模式 (Entity Inventory)

来自 CC Studio asset-spec Phase 0b。从所有源文档中扫描游戏实体，建立分类清单。

```
1. 从 story-design.md / character-card 扫描所有实体
2. 分类: Character, Environment, Item, UI, SFX, BGM
3. 输出 entity-inventory.md
4. 用户确认清单 → 作为预算规划输入
```

---

## 艺术圣经模式 (Art Bible)

9 sections 的视觉身份约束文档：

1. Visual Identity Statement — 一句话视觉身份
2. Mood & Atmosphere — 情绪与氛围
3. Shape Language — 形状语言（圆=友好/方=稳定/三角=危险）
4. Color System — 主色 + 辅色 + 强调色 + 禁用色
5. Character Design Direction — 角色设计方向
6. Environment Design Language — 环境设计语言
7. UI/HUD Visual Direction — UI 视觉方向
8. Asset Standards — 文件格式/命名/尺寸标准
9. Reference Direction — 参考方向（其他游戏/艺术风格）

---

## 背景移除策略

来自 godogen-ark rembg (BiRefNet 软遮罩 + 颜色遮罩混合)。详见 `references/godogen-ark-pipeline.md` §七。

### 铁律

**NEVER prompt for "transparent background"** → 生成器画 checkerboard 而非真透明

### 三种 Regime

| Regime | 触发 | 策略 |
|--------|------|------|
| `trust` | BiRefNet 遮罩完整 | 直接使用输出 |
| `adapt` | 有背景残留 | BiRefNet + 颜色遮罩混合 |
| `color` | 背景均匀 | 主要用颜色遮罩 |

### BG 颜色速查

- 森林/草地 → `dark-green` (#006400)
- 天空/水 → `steel-blue` (#4682B4)
- 地牢/室内 → `dark-gray` (#404040)
- 明亮室内 → `light-beige` (#F5F5DC)
- 通用 → `medium-gray` (#808080，避免 #00FF00 纯色键控色)

### QA 输出

生成 `_qa.png` 复合图在对比色背景（magenta/cyan/yellow）上检查背景残留/前景缺失/边缘光晕。

---

## 动画精灵完整管线

来自 godogen-ark 六步管线：

```
1. 参考图 → Gemini 1K, neutral pose, solid BG (7¢)
2. 姿势帧 → Gemini 1K, image-to-image from 参考图 (7¢/pose)
3. 视频   → Grok, feed 姿势帧, 5¢/秒
4. 帧提取 → ffmpeg -vsync 0
5. 循环裁剪 → find_loop_frame
6. 逐帧抠图 → rembg 批量模式 (共享 session+BG色)
```

---

## 3D 模型生成管线

来自 godogen-ark Tripo3D/Seed3D：

```
1. 3D 参考图 → Gemini 1K, 3/4 front elevated camera angle, T-pose (7¢)
2. 上传 → Tripo3D/Seed3D API
3. 轮询 → 下载 GLB
4. Godot 导入 → AABB 方向检查 → 旋转 → 缩放 → BoxShape3D 碰撞体
```

---

## 生成铁律

```
1. 永远不要 prompt "transparent background"
2. 锚点先生成、审查通过后再衍生
3. 架构不稳定时不花预算
4. 每个资产最多重试 3 次
5. ComfyUI 本地优先（免费），API 后端备用
6. 每个素材记录 source_version 和 cost
7. 3D 参考必须包含 "3/4 front elevated camera angle, T-pose, neutral expression"
8. 实体清单必须先出、用户确认后再做预算
```
