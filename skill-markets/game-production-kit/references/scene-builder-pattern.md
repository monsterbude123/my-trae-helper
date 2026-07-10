# Scene Builder 模式

> 吸收自 godogen-ark scene-generation.md + scaffold.md。Scene Builder 是 GDScript 脚本在 Godot headless 模式运行一次产生 `.tscn` 的程序化场景构建模式。这是 godogen-ark 的核心创新——用代码生成场景，而非手编序列化场景格式。

---

## 一、概念

**Scene Builder** 是**构建时**脚本（extends SceneTree, 运行一次产出 .tscn），与 **Runtime Script**（extends CharacterBody3D/Node3D, 运行时持续执行）完全分离。

| 特性 | Scene Builder | Runtime Script |
|------|-------------|----------------|
| extends | `SceneTree` | `CharacterBody3D` / `Node3D` / `Control` / ... |
| 入口 | `_initialize()` | `_ready()` + `_process()` |
| 运行次数 | 一次（构建时） | 持续（运行时） |
| `@onready` | ❌ 不可用 | ✅ |
| `preload()` | ❌ 不可用（headless 失败），用 `load()` | ✅ |
| 信号连接 | ❌ 脚本未实例化 | ✅ 在 `_ready()` 中 |
| 空间方法 (`look_at()`, `to_global()`) | ❌ 节点不在场景树 | ✅ |
| `_ready()` 触发 | ❌ SceneTree 中不触发，需手动调用 | ✅ 自动触发 |

**为什么分离两种模式**：
- Headless 执行的 SceneTree 环境与运行时编辑器/游戏环境 API 可用性不同
- 许多 GDScript 特性和 API 在 SceneTree headless 中不可用或无意义（信号、空间变换、preload）
- 混用会导致静默失败——代码能跑但场景节点丢失或功能异常

---

## 二、核心规则

```
1. extends SceneTree（headless 执行必需）
2. 实现 _initialize() 作为入口点
3. 构建完整节点层次结构，所有属性在 add_child() 后设置
4. 通过 set_script() 附加运行时脚本（从 STRUCTURE.md Attaches to 字段读取）
5. 设置 Owner Chain（所有节点的 owner = scene root）
6. Pack + Validate + ResourceSaver.save
7. quit(0) 退出
```

---

## 三、Owner Chain 协议 (CRITICAL)

Owner Chain 是 Scene Builder 的**致命模式**。遗漏 owner 设置会导致节点在序列化时静默丢失——.tscn 文件看起来正常但节点在实际加载时不出现。这是 #1 最常见的 bug 源。

```gdscript
# 在 _initialize() 末尾，所有 add_child() 调用之后调用一次:
set_owner_on_new_nodes(root, root)

func set_owner_on_new_nodes(node: Node, scene_owner: Node) -> void:
    for child in node.get_children():
        child.owner = scene_owner
        if child.scene_file_path.is_empty():
            # 用 .new() 创建的节点 — 递归设置子节点 owner
            set_owner_on_new_nodes(child, scene_owner)
        # else: 实例化场景（GLB/TSCN）— 不递归，保持为引用
```

**GLB Ownership Bug** (致命):
- 不能递归进入实例化 GLB 模型的内部节点树
- 如果无条件递归，所有 GLB 内部 mesh/material 节点被序列化为内联文本
- 导致 .tscn 文件膨胀到 100MB+

**常见错误模式**:

```gdscript
# WRONG: 只设置直接子节点的 owner
terrain.owner = root
# terrain 的 Mesh、Collision 子节点没有 owner → 静默丢失！

# WRONG: 对容器节点调用而不是 root
set_owner_on_new_nodes(track_container, root)
# track_container 本身没有 owner → 静默丢失！

# WRONG: 忘记子场景实例根节点
car.owner = root  # 只设这一行就够了，不要递归进内部
```

---

## 四、Post-Pack 验证

```gdscript
var count := _count_nodes(root)
var packed := PackedScene.new()
var err := packed.pack(root)
if err != OK:
    push_error("Pack failed: " + str(err))
    quit(1); return

if not validate_packed_scene(packed, count, "res://{path}.tscn"):
    quit(1); return

err = ResourceSaver.save(packed, "res://{path}.tscn")
if err != OK:
    push_error("Save failed: " + str(err))
    quit(1); return

print("BUILT: %d nodes" % count)
quit(0)

func _count_nodes(node: Node) -> int:
    var total := 1
    for child in node.get_children():
        total += _count_nodes(child)
    return total

func validate_packed_scene(packed: PackedScene, expected_count: int, scene_path: String) -> bool:
    var test_instance = packed.instantiate()
    var actual := _count_nodes(test_instance)
    test_instance.free()
    if actual < expected_count:
        push_error("Pack validation failed for %s: expected %d nodes, got %d" % [scene_path, expected_count, actual])
        return false
    return true
```

**验证门禁**: 只有验证通过（actual >= expected）才允许 `ResourceSaver.save()`。

---

## 五、完整 Scene Builder 模板

```gdscript
extends SceneTree

func _initialize() -> void:
    print("Generating: {scene_name}")

    var root := {RootNodeType}.new()
    root.name = "{SceneName}"

    # --- Build node hierarchy ---
    # var child := SomeNode.new()
    # child.some_property = value
    # root.add_child(child)

    # --- Attach runtime scripts ---
    # var script := load("res://scripts/player_controller.gd")
    # player_node.set_script(script)

    # --- Set ownership chain ---
    set_owner_on_new_nodes(root, root)

    # --- Validate node count ---
    var count := _count_nodes(root)

    # --- Pack and validate ---
    var packed := PackedScene.new()
    var err := packed.pack(root)
    if err != OK:
        push_error("Pack failed: " + str(err))
        quit(1); return
    if not validate_packed_scene(packed, count, "res://{output_path}.tscn"):
        quit(1); return

    # --- Save ---
    err = ResourceSaver.save(packed, "res://{output_path}.tscn")
    if err != OK:
        push_error("Save failed: " + str(err))
        quit(1); return

    print("BUILT: %d nodes" % count)
    print("Saved: res://{output_path}.tscn")
    quit(0)

func set_owner_on_new_nodes(node: Node, scene_owner: Node) -> void:
    for child in node.get_children():
        child.owner = scene_owner
        if child.scene_file_path.is_empty():
            set_owner_on_new_nodes(child, scene_owner)

func _count_nodes(node: Node) -> int:
    var total := 1
    for child in node.get_children():
        total += _count_nodes(child)
    return total

func validate_packed_scene(packed: PackedScene, expected_count: int, scene_path: String) -> bool:
    var test_instance = packed.instantiate()
    var actual := _count_nodes(test_instance)
    test_instance.free()
    if actual < expected_count:
        push_error("Pack validation failed for %s: expected %d nodes, got %d" % [scene_path, expected_count, actual])
        return false
    return true
```

---

## 六、常见节点组合模式

### 6.1 3D 物理对象

```gdscript
var body := RigidBody3D.new()
var collision := CollisionShape3D.new()
var mesh := MeshInstance3D.new()
var shape := BoxShape3D.new()
shape.size = Vector3(1, 1, 1)
collision.shape = shape
body.add_child(collision)
body.add_child(mesh)
```

### 6.2 相机 Rig

```gdscript
var pivot := Node3D.new()
var camera := Camera3D.new()
camera.position.z = 5
camera.current = true
pivot.add_child(camera)
```

### 6.3 环境与光照

```gdscript
var world_env := WorldEnvironment.new()
var env := Environment.new()
env.background_mode = Environment.BG_SKY
env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
env.ambient_light_color = Color.WHITE
env.ambient_light_sky_contribution = 0.5
var sky := Sky.new()
sky.sky_material = ProceduralSkyMaterial.new()
env.sky = sky
world_env.environment = env
root.add_child(world_env)

var sun := DirectionalLight3D.new()
sun.shadow_enabled = true
sun.shadow_bias = 0.05
sun.shadow_blur = 2.0
sun.directional_shadow_max_distance = 30.0
sun.sky_mode = DirectionalLight3D.SKY_MODE_LIGHT_AND_SKY
sun.rotation_degrees = Vector3(-45, -30, 0)
root.add_child(sun)
```

### 6.4 CSG 快速原型

CSG 节点自动生成碰撞体，适合白盒阶段快速验证：

```gdscript
var floor := CSGBox3D.new()
floor.size = Vector3(20, 0.5, 20)
floor.use_collision = true
floor.material = ground_mat
root.add_child(floor)

# 减法（挖洞）：子 CSG 操作在父 CSG 上
var hole := CSGCylinder3D.new()
hole.operation = CSGShape3D.OPERATION_SUBTRACTION
hole.radius = 1.0; hole.height = 1.0
floor.add_child(hole)
```

### 6.5 程序化噪声纹理

```gdscript
var noise := FastNoiseLite.new()
noise.noise_type = FastNoiseLite.TYPE_CELLULAR
noise.frequency = 0.02
noise.fractal_type = FastNoiseLite.FRACTAL_FBM
noise.fractal_octaves = 5

var tex := NoiseTexture2D.new()
tex.noise = noise
tex.width = 1024; tex.height = 1024
tex.seamless = true       # tileable
tex.as_normal_map = true  # for normal maps
tex.bump_strength = 2.0
```

---

## 七、GLB 3D 模型导入

```gdscript
# 必须明确类型：PackedScene，用 = 不是 :=
var model_scene: PackedScene = load("res://assets/glb/car.glb")
var model = model_scene.instantiate()
model.name = "CarModel"

# 查找 MeshInstance3D 获取 AABB
var mesh_inst: MeshInstance3D = find_mesh_instance(model)
var aabb: AABB = mesh_inst.get_aabb() if mesh_inst else AABB(Vector3.ZERO, Vector3.ONE)

# 缩放到目标尺寸
var target_length := 2.0
var scale_factor: float = target_length / aabb.size.x
model.scale = Vector3.ONE * scale_factor
model.position.y = -aabb.position.y * scale_factor  # 修正垂直对齐

parent_node.add_child(model)

func find_mesh_instance(node: Node) -> MeshInstance3D:
    if node is MeshInstance3D:
        return node
    for child in node.get_children():
        var found = find_mesh_instance(child)
        if found: return found
    return null
```

**GLB 朝向检查**: 导入后检查 AABB 最长维度。如果车的 AABB 最长在 Z 但游戏期望 forward = -Z，无需旋转；如最长在 X，rotate 90°。角色/动物的 forward-facing 轴必须与移动方向对齐。

**碰撞体铁律**: 永远用 BoxShape3D / SphereShape3D / CapsuleShape3D 简单图元。**禁止** `create_convex_shape()` 或 `create_trimesh_shape()` —— 高面数模型（100k+ 三角形）会导致 <1 FPS。

**纹理 UV Tiling**: `mat.uv1_scale = Vector3(N, N, 1)` 在 M 米平面上产生 M/N 米瓷砖。

---

## 八、子场景实例化

```gdscript
var car_scene: PackedScene = load("res://scenes/car.tscn")
var car = car_scene.instantiate()
car.name = "PlayerCar"
car.position = Vector3(0, 0, 5)
root.add_child(car)
car.owner = root  # 子场景内部节点已有自己的 owner — 只设实例根
```

---

## 九、Scene Builder 禁止项速查

| 禁止 | 原因 | 替代 |
|------|------|------|
| `@onready` | SceneTree 不执行 scene annotations | 在 `_initialize()` 中赋值 |
| `preload()` | Headless 中 `preload()` 失败 | 用 `load()` |
| 信号连接 | 脚本未实例化 | 在 Runtime Script `_ready()` 中连接 |
| `look_at()` | 节点不在场景树 | `rotation_degrees` 或手动计算（Runtime 中用 `look_at()`） |
| `to_global()` / `to_local()` | 节点不在场景树 | 手动坐标计算 |
| `_ready()` 依赖 | SceneTree 不触发 `_ready()` | 显式调用初始化方法 |
| 2D/3D 混用 | 同一场景层次中不可混用 | 用 SubViewport 桥接 |
| GLB 子节点递归 owner | 导致 100MB+ .tscn | 只设实例根 owner |

---

## 十、与 game-production-kit 的集成

- Phase 3 Godot scripting: 加载 `godot-scripting` skill → 读取本 reference → 按模板生成 Scene Builder GDScript
- Phase 5 Godot build: Scene Builder 在 headless Godot 中运行 → 产出 .tscn → 与 Runtime Script 一起构建验证
- STRUCTURE.md 的 Attaches to 字段驱动 Scene Builder 中的 `set_script()` 调用
