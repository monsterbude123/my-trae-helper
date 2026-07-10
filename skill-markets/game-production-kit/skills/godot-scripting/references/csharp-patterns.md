# Godot C# 编码参考

> 吸收自 godogen csharp.md (621行)。Godot 4.x C# (Godot .NET) 编码参考。

## 核心规则

```csharp
// 1. 使用 Godot 集合类型 (非 System.Collections.Generic)
Godot.Collections.Array<Node> nodes = new();
Godot.Collections.Dictionary<string, int> dict = new();

// 2. [Export] 替代 [SerializeField]
[Export] public float Speed { get; set; } = 100.0f;

// 3. 信号用 [Signal] delegate
[Signal] public delegate void DialogueFinishedEventHandler(string lineId);
```

## 项目结构

```
project/
├── project.godot
├── Game.csproj
├── Game.sln
├── scripts/
│   ├── Core/
│   ├── Characters/
│   └── Systems/
└── scenes/
```

## 常用 API 对照

| GDScript | C# | 说明 |
|----------|-----|------|
| `$Node` | `GetNode<T>("Node")` | 节点引用 |
| `$"%UniqueNode"` | `GetNode<T>("%UniqueNode")` | 唯一节点 |
| `@onready var` | `GetNode<>()` in `_Ready()` | 就绪变量 |
| `load(path)` | `GD.Load<PackedScene>(path)` | 加载资源 |
| `preload(path)` | 用 `[Export]` 替代 | 编译期加载 |
| `signal name(args)` | `[Signal] delegate Name(args)` | 信号声明 |
| `name.emit(args)` | `EmitSignal(SignalName.Name, args)` | 信号触发 |
| `name.connect(callable)` | `Name += handler` | 信号连接 |
| `create_tween()` | `CreateTween()` | Tween |
| `tween.tween_property()` | `tween.TweenProperty()` | Tween 属性 |
| `await condition` | `await ToSignal(...)` | 异步等待 |
| `queue_free()` | `QueueFree()` | 销毁节点 |

## 编译与运行

```bash
# 编译
dotnet build

# 修复编译错误
dotnet build --no-incremental

# 运行
godot --headless --path ./project --quit

# 带脚本运行
godot --headless --path ./project --script res://tests/run_tests.cs
```

## Godot 命名空间

```csharp
using Godot;  // 主命名空间
using Godot.Collections;  // Godot 集合
```

## 性能注意事项

- `[GlobalClass]` 替代 `class_name` — C# 类默认可引用
- `GodotObject` 不自动垃圾回收 — 手动 `Dispose()` 大资源
- `Transform3D` 和 `Transform2D` 是值类型，赋值 = 复制
- `CallDeferred()` 延迟调用（避免执行顺序问题）

## 版本兼容

- Godot 4.x + .NET 8 SDK
- `Game.csproj` 中 `TargetFramework` = `net8.0`
- 不使用 `Godot 3.x` 的 `Object.Connect()` 和 `Object.Disconnect()`
