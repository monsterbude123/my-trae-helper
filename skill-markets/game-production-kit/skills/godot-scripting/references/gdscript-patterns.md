# Godot GDScript 最佳实践

> 吸收自 godogen gdscript.md (804行) + CC Studio godot-specialist。Godot 4.x GDScript 编码参考。

## 核心规则

```
1. 全局静态类型 — 所有变量和函数参数显式类型标注
2. class_name 注册 — 每个独立脚本用 class_name
3. @export 暴露参数 — 不在代码中硬编码
4. @onready 缓存节点引用 — var sprite: Sprite2D = $Sprite2D
5. signals 解耦 — 不硬引用兄弟节点
6. Godot 4.x API — 不用 3.x 语法
```

## 类型标注

```gdscript
# ✅ 正确
var speed: float = 100.0
var player_name: String = ""
var is_alive: bool = true
var enemies: Array[Node2D] = []

func take_damage(amount: float) -> void:
    health -= amount

# ❌ 错误
var speed = 100.0   # 失去类型安全
func take_damage(amount):   # 参数无类型
```

## class_name 注册

```gdscript
class_name CharacterDisplay
extends Node2D

@export var character_id: String
@export var default_expression: String = "normal"
```

> 每个独立功能脚本都有 `class_name`。只有场景专属的子脚本可以不注册。

## Signals 解耦

```gdscript
# 发送方
signal dialogue_finished(line_id: String)

func _on_end_animation() -> void:
    dialogue_finished.emit(line_id)

# 接收方
func _ready() -> void:
    dialogue_system.dialogue_finished.connect(_on_dialogue_finished)

func _on_dialogue_finished(line_id: String) -> void:
    # 不用知道发送方是谁
    next_line(line_id)
```

> 不用 `$"../Sibling/Node".method()` — 那是硬耦合。

## Godot 4.x vs 3.x API 差异

| 3.x | 4.x | 说明 |
|-----|-----|------|
| `change_scene()` | `change_scene_to_file()` | 场景切换 |
| `Tween.new()` | `create_tween()` | Tween 动画 |
| `get_node("Node")` | `$Node` | 节点引用 |
| `yield()` | `await` | 协程 |
| `export var` | `@export var` | 导出变量 |
| `onready var` | `@onready var` | 就绪变量 |
| `KinematicBody2D` | `CharacterBody2D` | 物理体 |
| `CanvasItem.update()` | `queue_redraw()` | 重绘 |

## 性能约束

```gdscript
# 禁用不需要的 process
func _ready() -> void:
    set_process(false)

# 只在需要的帧启用
func _on_player_entered() -> void:
    set_process(true)
```

- `set_process(false)` — 不需要逐帧更新的节点
- 对象池 — 频繁创建/销毁用 `preload()` + 缓存
- `VisibleOnScreenNotifier2D` — 离屏节点禁用

## 异步加载

```gdscript
# 小资源
var scene: PackedScene = load("res://scenes/gameplay.tscn")

# 大场景（异步）
ResourceLoader.load_threaded_request("res://scenes/level_02.tscn")
# ... 加载中做其他事 ...
var scene = ResourceLoader.load_threaded_get("res://scenes/level_02.tscn")
```

## 文件搜索

```bash
# rg 将 .gd 注册为 gap 类型，用 glob
rg "class_name" --glob "*.gd"
```

> 不用 `rg --type gdscript` — rg 不内置 .gd 类型。

## 测试

```bash
# Headless 运行测试
godot --headless --path ./project --script res://tests/run_tests.gd
```
