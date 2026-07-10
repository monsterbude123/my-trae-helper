# Godot 常见坑 (Quirks)

> 吸收自 godogen godot/quirks.md (80+ 条目) + bevy/quirks.md + babylon/quirks.md。从实际构建中积累的已知问题。

## Godot 4.x 通用坑

| # | 问题 | 解决 |
|---|------|------|
| 1 | `.import/` 目录未生成导致素材空白 | `godot --headless --import` |
| 2 | 场景文件路径大小写错误 | Godot `res://` 大小写敏感 |
| 3 | `change_scene()` 已废弃 (3.x API) | 用 `change_scene_to_file()` |
| 4 | `Tween.new()` 已废弃 | 用 `create_tween()` |
| 5 | `yield()` 在 4.x 移除 | 用 `await` |
| 6 | `get_node("Node")` vs `$Node` | `$` 是语法糖，编译更快 |
| 7 | KinematicBody2D 移除 | 用 CharacterBody2D |
| 8 | CanvasItem.update() 移除 | 用 `queue_redraw()` |
| 9 | `export var` 语法废弃 | 用 `@export var` |
| 10 | Autoload 循环引用导致启动 crash | Autoload 不互相引用 |
| 11 | `_ready()` 中访问兄弟节点 | 用 `call_deferred()` 或 `@onready` |
| 12 | PackedScene 实例化后未 add_child | `instantiate()` 不自动加入场景树 |
| 13 | .tscn 文件编码非 UTF-8 | Godot 要求 UTF-8 |
| 14 | 资源格式 `.tres` vs `.res` | 文本格式用 `.tres`，二进制用 `.res` |
| 15 | `--write-movie` 在 Godot 3.x 不可用 | 升级到 4.x |
| 16 | 粒子 GPU 模式下项目设置未开启 | Project Settings → Rendering → GPU Particles |
| 17 | Font 变体缺失（粗体/斜体） | 导入时勾选对应的 OpenType 特性 |
| 18 | Camera2D 的 `current` 属性 | 多个 Camera2D 只有一个 `current = true` |
| 19 | `get_viewport().size` 在 `_ready()` 不可靠 | 在 `_process()` 第一帧检查 |
| 20 | ResourceLoader.load_threaded 无进度回调 | 轮询 `load_threaded_get_status()` |

## C# 特定坑

| # | 问题 | 解决 |
|---|------|------|
| 21 | .NET SDK 版本不匹配 | Godot 4.x 要求 .NET 8 |
| 22 | `dotnet build` vs `dotnet publish` | Godot 只需要 build |
| 23 | 泛型 `GetNode<T>()` | T 必须是 Node 子类 |
| 24 | C# 信号参数类型不匹配 | 严格匹配 `[Signal] delegate` 签名 |
| 25 | `GodotObject` 不自动 GC | Dispose 大资源 |

## 编辑器坑

| # | 问题 | 解决 |
|---|------|------|
| 26 | 编辑器打开后改外部文件不同步 | 手动 FileSystem dock → 右键 → Reimport |
| 27 | 插件安装后不生效 | 重启编辑器 |
| 28 | Asset Library 搜索超时 | 改 DNS 或用命令行 `godot --install-plugin` |

## Android 构建坑

| # | 问题 | 解决 |
|---|------|------|
| 29 | SDK 路径找不到 | `export ANDROID_HOME=/path/to/sdk` |
| 30 | debug.keystore 缺失 | `keytool -genkey -v -keystore debug.keystore -alias androiddebugkey` |
| 31 | 纹理压缩不支持 | 检查 Android 的 import 设置 |

## GDScript 类型推断陷阱 (:=)

> 来自 godogen-ark quirks.md。`:=` 在某些场景下推断为 Variant，导致后续类型错误。

| # | 陷阱 | 示例 | 解决 |
|---|------|------|------|
| 32 | `:=` + `instantiate()` 返回 Variant | `var model = model_scene.instantiate()` | 明确类型：`var model_scene: PackedScene = load(...)` |
| 33 | `:=` + 多态数学函数 | `var d = Vector3().distance_to(...)` 推断为 Variant | 明确类型标注 |
| 34 | `:=` + 数组/字典索引 | `var v = dict["key"]` 推断为 Variant | 明确类型标注 |

## 动画静默失败

> 来自 godogen-ark。动画是 **#1 静默失败源** — 代码无错误但动画"工作不正常"。

| # | 问题 | 解决 |
|---|------|------|
| 35 | 动画静默失败（无错误但不正常） | 多帧截图 + VQA 对比检测 |
| 36 | AnimationPlayer `play("walk")` 不立即生效 | 等到下一帧才生效，不要在 play() 后立即检查 |
| 37 | 动画长度/循环模式设置无效 | 在 `_ready()` 中设置，不在 `_initialize()` 中 |

## 渲染与场景构建陷阱

> 来自 godogen-ark.

| # | 问题 | 解决 |
|---|------|------|
| 38 | `--write-movie` frame 0 为空帧 | 跳过第一帧，从 frame 1 开始检查 |
| 39 | Camera lerp 原点抖动（第一帧从原点飞入） | 用初始化标志：if first_frame: snap_to_position(); return |
| 40 | 帧率依赖的 drag（`speed *= (1-drag)`） | 用 `delta` 修正：`speed *= pow(1-drag, delta*60)` |
| 41 | UV 平铺双倍缩放 | `uv1_scale = Vector3(10,10,1)` 在 20m 平面上产生 2m 瓷砖 |
| 42 | 碰撞层是位掩码不是 UI 编号 | Layer 3 = bitmask 4 (1<<2)，不是数值 3 |
| 43 | MultiMeshInstance3D pack+save 后丢失 mesh 引用 | 用独立 GLB 实例替代 |
| 44 | `_ready()` 在 SceneTree `_initialize()` 中不触发 | Headless 构建时需手动调用初始化方法 |
| 45 | GLB ownership 递归导致 100MB+ .tscn | 只设实例根节点 owner，用 `child.scene_file_path.is_empty()` 判断 |
| 46 | 遗漏 owner 导致节点静默丢失 | 所有 add_child() 后调用 `set_owner_on_new_nodes(root, root)` |
| 47 | `preload()` 在 headless 模式下失败 | 用 `load()` 替代 |
| 48 | `look_at()` / `to_global()` 在 SceneTree 中不可用 | 节点不在场景树，用 `rotation_degrees` 手动计算 |

## 3D 模型导入陷阱

| # | 问题 | 解决 |
|---|------|------|
| 49 | GLB 模型朝向错误（最长轴不是 forward） | 检查 AABB 最长维度，调整 rotation |
| 50 | `create_convex_shape()` 在高面数模型上 <1 FPS | 永远用 BoxShape3D/SphereShape3D/CapsuleShape3D |
| 51 | 动画角色移动方向与朝向不一致 | 截图验证：bounding box 或 silhouette 是否匹配移动方向 |

## Scene Builder 特定禁止项

| 禁止 | 原因 | 替代 |
|------|------|------|
| `@onready` | SceneTree 不执行 scene annotations | 在 `_initialize()` 中赋值 |
| 信号连接 | 脚本未实例化 | 在 Runtime `_ready()` 中连接 |
| `_ready()` 依赖 | SceneTree 不触发 | 显式调用初始化 |
| 2D/3D 节点混用 | 序列化不兼容 | 用 SubViewport 桥接 |

> 本文件定期从项目 `quirks-godot.md` 提升。发现新坑先写项目级文件。
