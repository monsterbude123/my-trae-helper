# Godogen-Ark 资产管线深度参考

> 吸收自 `docs/references/ai-game/godogen-ark/` — 全量 47 个文件。godogen-ark 是从一句话到可玩游戏的全自动 AI 管线，基于 Godot 4.x，有成熟的资产生成经济模型和深度 Godot 领域知识。

---

## 一、核心管线架构

```
用户一句话描述
    ↓
[Visual Target] → reference.png (1K 16:9, 7¢ Gemini)
    ↓
[Decomposition] → PLAN.md (风险分类 + 验证标准)
    ↓
[Architecture] → STRUCTURE.md + project.godot + 脚本桩 + 场景构建器桩
    ↓
[Asset Planning] → ASSETS.md (预算规划 + 资产清单 + 尺寸规格)
    ↓
[Asset Gen] → PNG/GLB/精灵帧 (多后端, 成本追踪)
    ↓
[Task Execution] → GDScript + .tscn (风险任务先隔离→主构建)
    ↓
[Visual QA] → screenshots/ + VQA 报告 (Gemini/Claude 视觉)
    ↓
[Export] → Android APK / Steam / 抖音小游戏
```

**核心设计原则**：
1. **风险优先**：先验证最难的核心机制（白盒占位符），再花预算生成资产
2. **预算驱动决策**：每种操作有精确成本，资产规划是成本优化问题
3. **文件驱动状态**：所有关键状态在 Markdown 文件中，支持任意中断恢复
4. **渐进加载**：技能子文件按管线阶段渐进读取，Fork 大文档到独立上下文
5. **视觉验证闭环**：每次实现后截图→VQA 比较→修复

---

## 二、八文档协议 (Document Protocol)

| 文档 | 角色 | 写入者 | 读取者 |
|------|------|--------|--------|
| `PROJECT.md` | 游戏概念 + 需求（Origin of Truth） | 用户确认 | 所有阶段 |
| `reference.png` | 视觉北极星 | visual-target | 所有下游阶段 |
| `PLAN.md` | 风险分析 + 验证标准 + 任务分解 + 进度追踪 | decomposer | task-executor, orchestrator |
| `STRUCTURE.md` | 架构蓝图 + Asset Hints + Build Order | scaffold | asset-planner, task-executor |
| `ASSETS.md` | 资产清单 + 艺术方向 + 成本追踪 + 尺寸规格 | asset-planner | task-executor |
| `MEMORY.md` | 项目记忆（发现/解决方案/决策） | task-executor | task-executor |
| `CHANGELOG.md` | 增量修改记录（时间戳） | scaffold | resume |
| `CHECKPOINTS.md` | 阶段检查点 + 内容哈希 | orchestrator | resume |
| `STATUS.md` | 当前项目状态总览 | orchestrator | 用户 |

**game-production-kit 映射**：
- `PROJECT.md` → 合并到 `story-design.md`（Phase 1 产出）
- `PLAN.md` + `STRUCTURE.md` → 合并到 `.project-state-card.md`（驾驶舱）
- `ASSETS.md` → `asset-manifest.md`（Phase 2 产出）
- `MEMORY.md` → `quirks-{engine}.md`（引擎特定记忆）
- `CHECKPOINTS.md` + `STATUS.md` → `.project-state-card.md` 进度行

---

## 三、多后端资产生成经济模型

### 3.1 后端选择表

| 后端 | 模型/Flag | 单次成本 | 最佳用途 | 精度 |
|------|----------|---------|---------|------|
| Gemini | `gemini-3.1-flash-image-preview` | 5-15¢ (按尺寸) | 参考图、角色设计、3D参考、精确构图 | 高 |
| Grok | `grok-imagine-image` | 2¢ | 纹理、简单物体、道具、背景 | 中 |
| Ark/Doubao | `doubao-seedream-4.5` | 3¢ | 替代方案 | 中 |

### 3.2 Gemini 尺寸成本

| 尺寸 | 成本 | 用途 |
|------|------|------|
| `512` | 5¢ | 缩略图验证 |
| `1K` | 7¢ | 角色立绘、3D参考图、精灵参考 |
| `2K` | 10¢ | 背景、标题画面 |
| `4K` | 15¢ | 超高质量（极少需要） |

### 3.3 按资产类型的后端选择策略

| 资产类型 | 推荐后端 | 成本/个 | 备注 |
|----------|---------|--------|------|
| 视觉目标参考图 | Gemini 1K 16:9 | 7¢ | 整个项目的视觉北极星 |
| 角色立绘 | Gemini 1K | 7¢ | 精确 prompt 遵循 |
| 3D 模型参考图 | Gemini 1K 1:1 | 7¢ | front-facing, 3/4 elevated camera |
| 背景/标题 | Gemini 2K | 10¢ | 宽屏构图 |
| 纹理贴图 | Grok | 2¢ | 批量，单个体积小 |
| 道具/简单物体 | Grok | 2¢ | prompt 精确度不重要 |
| UI 图标 | Grok | 2¢ | 简单形状 |
| 动画精灵参考 | Gemini 1K | 7¢ | 一次性，锚定所有帧 |
| 动画精灵姿势 | Gemini 1K | 7¢ | 从参考图 image-to-image |
| 动画精灵视频 | Grok | 5¢/秒 | 从姿势图生成 |
| 3D 模型 GLB | Tripo3D/Seed3D | 40-57¢ | 图像→3D |

### 3.4 完整资产成本估算

- **完整 3D 资产** = Gemini 1K (7¢) + GLB (40-50¢) = 47-57¢
- **动画精灵** = ref (7¢) + pose (7¢) + video (5¢×N秒) + 免费处理
- **角色立绘** (10 表情) = ref 锚点 (7¢) + 9 衍生 (9×7¢) = 70¢
- **场景背景** (5 场景) = 5 × 10¢ = 50¢

### 3.5 预算管理协议

```
设置预算:   set_budget 500  # $5.00
生成前:     check_budget → 剩余是否够本次生成
生成后:     record_spend → 写入 generation-log.json
超预算:     按优先级排序（保留 > 先切后端 > 推迟）
重试:       每个资产最多 3 次（1 免费 + 2 付费 = 3 次）
日志:       assets/generation-log.json 持久化每条记录
```

**超预算优先级策略**：
1. 关键锚点资产 → 保留（不切后端）
2. 角色立绘 → 先从 Gemini 切 Grok
3. 批量纹理 → 降分辨率
4. 非关键道具 → 推迟到二期

---

## 四、资产注册表 (Asset Registry)

### 4.1 资产类型 (10 种)

| 类型 | 枚举值 | 说明 |
|------|--------|------|
| 纹理 | `texture` | 贴图、材质 |
| 精灵 | `sprite` | 2D 角色/物体 |
| 角色立绘 | `character` | 对话用立绘 |
| 动画精灵 | `animated_sprite` | 多帧动画 |
| 3D 模型 | `three_d_model` | GLB 文件 |
| 背景 | `background` | 场景背景 |
| UI 图标 | `ui_icon` | 界面元素 |
| UI 面板 | `ui_panel` | 界面容器 |
| 游戏标志 | `game_logo` | 标题 Logo |
| 物品套件 | `item_kit` | 网格切片生成的物品集 |

### 4.2 状态生命周期 (4 状态)

```
pending → generated → approved → (最终)
                   ↘ rejected → pending (重新生成)
```

### 4.3 CSV 格式

```csv
id,name,type,prompt,model,size,aspect_ratio,cost_cents,status,reference_image,output_path,created_at,updated_at,notes
1,elise_normal,character,"red-haired girl...",gemini,1K,9:16,7,approved,,assets/figure/elise_normal.png,2026-07-09T10:00:00,2026-07-09T10:05:00,
```

### 4.4 质量保证链 (5 层检查)

```
Layer 1: Prompt 质量检查
  → 按资产类型验证必需关键词
  → 检测负面关键词（"blurry", "low quality", "distorted"）
  → 验证推荐尺寸

Layer 2: 风格一致性检查
  → 从已批准资产提取风格关键词 (Counter.top_n)
  → 新 prompt 一致性评分 (0-1)
  → ≥0.7 通过 / 0.4-0.7 警告 / <0.4 拒绝

Layer 3: 流水线就绪检查
  → 验证 PLAN.md 中所有 Risk Tasks 已完成
  → 阻止架构不稳定时浪费预算生成资产

Layer 4: 注册表完整性
  → 验证所有 asset-manifest.md 中资产文件存在磁盘

Layer 5: 视觉 QA
  → 截图 vs 参考图对比
  → pass/fail/warning 判定
  → 3 次修复周期 + 重规划
```

### 4.5 Prompt 质量检查 - 按资产类型必需关键词

| 资产类型 | 必需关键词 |
|----------|-----------|
| 3D 参考 | "3/4 front elevated camera angle", "T-pose/A-pose", "neutral expression", "plain background", "well-lit", "full body" |
| 角色 | "full body", 角色描述 + 表情 + 光线 + 纯色背景色 |
| 背景 | 场景描述 + 构图 + 光照 + 风格 |
| 精灵 | "pixel art" (如果是像素), "sprite sheet" (如果是精灵表) |
| 纹理 | "seamless", "tileable", 材质描述 |
| UI | "flat design", "game UI", 功能描述 |
| Logo | "game logo", "title text readable", 风格 |

**负面关键词** (禁止出现): "blurry", "low quality", "distorted", "deformed", "bad anatomy", "extra limbs", "missing limbs", "fused", "watermark", "signature", "text", "jpeg artifacts", "poorly drawn"

---

## 五、Scaffold 脚手架生成

### 5.1 project.godot 关键配置

```ini
[application]
config/name="GameName"
config/features=PackedStringArray("4.5", "Forward Plus")

[rendering]
renderer/rendering_method="forward_plus"
textures/canvas_textures/default_texture_filter=0
anti_aliasing/quality/msaa_3d=2

[physics]
3d/physics_engine="GodotPhysics3D"
3d/run_on_separate_thread=true

[input]
move_forward={
    "deadzone": 0.2,
    "events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":87,"key_label":0,"unicode":119,"location":0,"echo":false,"script":null)]
}

[autoload]
GameState="*res://scripts/game_state.gd"
EventBus="*res://scripts/event_bus.gd"
```

### 5.2 STRUCTURE.md 格式

```markdown
# Architecture

## Scenes
### `scenes/game.tscn`
**Purpose:** Main game scene
**Root:** Node3D "Game"
**Scripts attached:**
- `res://scripts/player_controller.gd` → Player node (CharacterBody3D)
- `res://scripts/camera_rig.gd` → CameraPivot (Node3D)

## Asset Hints
- Character: young knight, blue armor, red cape -> `res://assets/figure/knight.png`
- Background: forest clearing with ancient ruins -> `res://assets/background/forest_01.png`

## Build Order
1. Main scene (no assets) — verify camera + movement
2. Player controller with whitebox placeholder
3. Enemy spawner
4. HUD overlay
5. Asset integration
```

---

## 六、Scene Builder 模式

Scene Builder 是 GDScript 脚本，在 Godot headless 模式运行一次产生 `.tscn`。

### 6.1 核心规则

- `extends SceneTree` — headless 执行必需
- 实现 `_initialize()` — 入口点
- 禁止在 Scene Builder 中使用：`@onready`、`preload()`、信号连接、`look_at()` 等空间方法
- Scene Tree 中 `_ready()` 不会触发 — 需要手动调用
- Owner Chain 是**致命模式** — 遗漏导致节点静默丢失

### 6.2 Owner Chain 协议

```gdscript
func set_owner_on_new_nodes(node: Node, scene_owner: Node) -> void:
    for child in node.get_children():
        child.owner = scene_owner
        if child.scene_file_path.is_empty():
            # Node created with .new() — recurse into children
            set_owner_on_new_nodes(child, scene_owner)
        # else: instantiated scene (GLB/TSCN) — don't recurse
```

**关键约束**：
- 所有节点必须设置 owner = scene root
- GLB 实例化场景**不能递归进去** — 会导致 100MB+ .tscn 文件，所有内部 mesh/material 序列化为文本
- 子场景实例只设置根节点 owner，内部已由子场景自己的 owner 维护

### 6.3 Post-Pack 验证

```gdscript
var count := _count_nodes(root)
var err := packed.pack(root)
if err != OK:
    push_error("Pack failed: " + str(err))
    quit(1); return
if not validate_packed_scene(packed, count, "res://{path}.tscn"):
    quit(1); return
err = ResourceSaver.save(packed, "res://{path}.tscn")
```

### 6.4 完整 Scene Builder 模板

见 [scene-generation.md 完整模板行 170-229](file:///D:/workspace/my-trae-helper/docs/references/ai-game/godogen-ark/sandbox/gen-rig-wasteland4/.claude/skills/godogen/scene-generation.md#L170-L229)

### 6.5 Scene Builder 与 Runtime Script 分离

| 特性 | Scene Builder | Runtime Script |
|------|-------------|----------------|
| extends | SceneTree | CharacterBody3D / Node3D / ... |
| 入口 | `_initialize()` | `_ready()` + `_process()` |
| 运行次数 | 一次（构建时） | 持续（运行时） |
| 可用 API | new(), add_child(), set_script() | 完整 API |
| 信号 | 不连接（脚本未实例化） | 在 `_ready()` 中连接 |
| 空间方法 | 不可用（不在场景树） | 全部可用 |
| `look_at()` | ❌ | ✅ |
| `preload()` | ❌ | ✅ |
| `@onready` | ❌ | ✅ |

---

## 七、高级背景移除 (rembg)

godogen-ark 使用 **BiRefNet 软遮罩 + 颜色遮罩混合方法**，远优于基础抠图。

### 7.1 三种 Regime

| Regime | 触发条件 | 策略 |
|--------|---------|------|
| `trust` | BiRefNet 遮罩完整（大面积连续透明） | 直接使用 BiRefNet 输出 |
| `adapt` | 有背景残留 | BiRefNet + 颜色遮罩混合 |
| `color` | 背景颜色均匀 | 主要使用颜色遮罩 |

### 7.2 BG 颜色策略

| 游戏环境 | 推荐 BG 色 | 原因 |
|----------|-----------|------|
| 森林/草地 | `dark-green` (#006400) | 接近预期背景 |
| 天空/水域 | `steel-blue` (#4682B4) | 接近天空色 |
| 地牢/室内 | `dark-gray` (#404040) | 接近暗环境 |
| 明亮室内 | `light-beige` (#F5F5DC) | 接近室内色调 |
| 通用 | `medium-gray` (#808080) | 中立，避免纯色键控色如 #00FF00 |

### 7.3 QA 验证

生成后合成 `_qa.png`：将抠出的主体放到对比色背景（magenta/cyan/yellow）上，视觉检查：
- 背景残留 → 选更对比的 BG 色重新生成
- 前景缺失 → 减小颜色遮罩阈值
- 边缘光晕 → 扩大遮罩膨胀
- 遮罩失败 → 切换到 color regime

---

## 八、Godot 深度陷阱知识 (补充)

以下陷阱是 godogen-ark quirks.md 中 game-production-kit 尚未完全覆盖的：

### 8.1 类型推断陷阱 (GDScript `:=`)

| # | 陷阱 | 示例 | 解决 |
|---|------|------|------|
| 1 | `:=` + `instantiate()` 返回 Variant | `var model = model_scene.instantiate()` | 明确类型：`var model_scene: PackedScene = load(...)` |
| 2 | `:=` + 多态数学函数 | `var d = Vector3().distance_to(...)` 推断为 Variant | 明确类型 |
| 3 | `:=` + 数组/字典索引 | `var v = dict["key"]` 推断为 Variant | 明确类型标注 |

### 8.2 动画静默失败

- 动画是 #1 静默失败源 — 无错误但"工作"不正确
- 检测方法：多帧截图 + VQA 对比
- AnimationPlayer 设置 `play("walk")` 后需要等到下一帧才生效
- 动画长度和循环模式在 `_ready()` 中设置

### 8.3 渲染/物理陷阱

| 陷阱 | 详情 |
|------|------|
| UV 平铺双倍缩放 | `uv1_scale = Vector3(10,10,1)` 在 20m 平面上产生 2m 瓷砖 |
| 碰撞层是位掩码 | Layer 3 = bitmask 4 (1<<2)，不是数值 3 |
| Camera lerp 原点抖动 | 需要初始化标志拍第一帧位置 |
| 帧率依赖的 drag | `speed *= (1-drag)` 在不同帧率效果差异大，用 `delta` 修正 |
| MultiMeshInstance3D 序列化 bug | pack+save 后丢失 mesh 引用，需用独立 GLB 实例 |

---

## 九、与 game-production-kit 的对应关系

| godogen-ark 概念 | game-production-kit 对应 | 状态 |
|-----------------|------------------------|------|
| Visual Target → reference.png | `game-asset-pipeline` → visual target first | **已吸收** |
| Decomposition → PLAN.md | `game-story-design` + `references/decomposer-patterns.md` | **已吸收** |
| Architecture → STRUCTURE.md + project.godot | `.project-state-card.md` + 引擎 scripting skills | **已吸收** |
| Asset Planning → ASSETS.md | `game-asset-pipeline` → asset-manifest.md | **已吸收** |
| Multi-backend Asset Gen | `game-asset-pipeline` → 多后端成本模型 | **本次吸收** |
| Asset Registry + QA | `game-asset-pipeline` → registry + 5层QA链 | **本次吸收** |
| Scene Builder | `godot-scripting` → Scene Builder 模式 | **本次吸收** |
| Task Execution | `references/task-execution-patterns.md` | **已吸收** |
| Visual QA | `game-quality-gate` → gate standards | **已吸收** |
| Quirks | `godot-scripting/references/godot-quirks.md` | **本次强化** |
| Platform Exports | 各引擎 `-engine-build` skills | **已吸收** |
| Publish | `references/publish-pipeline.md` | **已吸收** |
| Budget Management | `game-asset-pipeline` → 预算管理协议 | **本次吸收** |
| Context Hygiene | `references/context-hygiene.md` | **已吸收** |

---

## 十、godogen-manager 设计系统（仅供参考）

godogen-manager 是独立于核心管线的 Web 管理 UI：
- Next.js 14 全栈 (Thin Frontend / Thick Backend)
- Prisma ORM + SQLite
- WebSocket 实时日志推送
- 子进程编排 godogen-ark CLI
- 设计系统：紫色+橙色配色，Fira Code 字体

game-production-kit 当前阶段不需要此管理台——驾驶舱通过 `.project-state-card.md` 文件实现状态追踪。
