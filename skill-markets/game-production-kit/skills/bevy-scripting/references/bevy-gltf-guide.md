# bevy-gltf-guide.md

> 来源：godogen bevy/scene-generation.md（GLTF 加载 + jpeg feature 坑）
> 关联：`bevy-scripting/SKILL.md §核心模式索引` GLTF 加载

GLTF 模型加载走 `AssetServer::load` + 资源句柄 + `SceneRoot` 组件。

## 最小加载示例

```rust
fn spawn_hero(mut commands: Commands, assets: Res<AssetServer>) {
    commands.spawn((
        SceneRoot(assets.load("models/hero.gltf#Scene0")),
        Transform::from_xyz(0.0, 0.0, 5.0),
        Visibility::default(),
    ));
}
```

- 路径相对 `assets/` 目录（**不要带 `assets/` 前缀**）
- `#Scene0` 选取场景节点；`#Node0` 选节点；`#Mesh0/Primitive0` 选网格

## AssetServer::load 返回值

`load` 返回 `Handle<T>`，**立即可用**（不阻塞）。首次渲染时资源未就绪则该实体不可见，需配合下面 `visibility` 处理。

## 加载状态监听

```rust
#[derive(Component)]
struct ModelReady(bool);

fn check_ready(
    mut q: Query<(&mut ModelReady, &SceneRoot)>,
    scenes: Res<Assets<Scene>>,
) {
    for (mut ready, root) in &mut q {
        if scenes.get(root.0.id()).is_some() {
            ready.0 = true;
        }
    }
}
```

## 子节点 / 网格单独加载

```rust
// 只取网格
commands.spawn((
    Mesh3d(assets.load("models/hero.gltf#Mesh0/Primitive0")),
    MeshMaterial3d(assets.load("materials/hero.mat")),
));

// 只取节点（带动画）
commands.spawn((
    SceneRoot(assets.load("models/hero.gltf#Node0")),
    Transform::IDENTITY,
));
```

## 动画播放

GLTF 内含的 `AnimationClip` 通过 `AnimationPlayer` 组件驱动：

```rust
fn play_idle(
    mut q: Query<&mut AnimationPlayer>,
    animations: Res<Assets<AnimationClip>>,
) {
    let mut player = q.single_mut();
    player.play(animations.iter().next().unwrap().0);
}
```

## jpeg feature 坑

JPG 纹理默认未启用，需在 `Cargo.toml` 显式打开：

```toml
[dependencies]
bevy = { version = "0.15", features = ["jpeg"] }
```

不开启 → GLTF 材质引用 jpg 时**静默失败**（无错误但纹理不显示）。PNG 无此问题。

## glTF 文件放置

```
project/
├── assets/
│   ├── models/hero.gltf        # 入口
│   ├── models/hero.bin         # 二进制缓冲
│   └── models/hero-texture.png
└── src/main.rs
```

> 路径中**不要**用绝对路径或 `..`。

## 性能提示

- 多个同模型实例复用 `Handle<Scene>`，**不要**每次 spawn 重新 load
- 大模型用 `bevy_scene::SceneInstanceReady` 等异步事件触发后续逻辑
- 远距离实体用 `Visibility::Hidden` 提前剔除

## 与代码生成 mesh 混用

```rust
commands.spawn((
    Mesh3d(meshes.add(Plane3d::default().mesh().size(50.0, 50.0))),
    MeshMaterial3d(materials.add(Color::srgb(0.3, 0.5, 0.3))),
));
```

代码生成 + GLTF 加载可混用，前者用于地形/简单几何，后者用于角色/复杂模型。
