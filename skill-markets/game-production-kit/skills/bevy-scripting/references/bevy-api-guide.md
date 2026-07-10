# bevy-api-guide.md

> 来源：godogen bevy/bevy-help.md（API 速查表 + trait 签名）
> 关联：`bevy-scripting/SKILL.md §核心铁律` 中 `Bevy 0.15+` 锁定

Bevy 0.15+ 核心 API 速查。所有路径基于 `bevy::prelude::*` 与 `bevy::` 模块。

## App — 应用入口

```rust
fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugins(MyPlugin)
        .add_systems(Startup, setup)
        .add_systems(Update, tick)
        .run();
}
```

- `add_plugins(P)` 注册插件
- `add_systems(ScheduleLabel, system)` 注册系统
- `add_state::<T>()` 注册状态

## Plugin — 插件 trait

```rust
pub trait Plugin: Send + Sync + 'static {
    fn build(&self, app: &mut App);
    fn finish(&self, app: &mut App) { ... }
    fn cleanup(&self, app: &mut App) { ... }
}
```

最小插件：

```rust
pub struct MyPlugin;
impl Plugin for MyPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, setup);
    }
}
```

## Component — 组件

```rust
#[derive(Component)]
struct Health(pub f32);

#[derive(Component, Default)]
struct Player;

#[derive(Component)]
#[require(Transform, Visibility)]
struct Enemy;
```

- `#[require(...)]` 自动补齐依赖组件
- Bundle 是一组 Component 的集合（`SpatialBundle` 等）

## Resource — 全局数据

```rust
#[derive(Resource, Default)]
struct GameScore(pub u32);

// 注入
commands.insert_resource(GameScore::default());
// 读取
fn show(s: Res<GameScore>) { println!("{}", s.0); }
// 可变
fn add(mut s: ResMut<GameScore>) { s.0 += 1; }
```

## System — 系统函数

签名选项（可任意组合）：

```rust
fn sys(
    commands: Commands,           // 生成/销毁实体
    query: Query<...>,             // 查询
    res: Res<T>,                  // 不可变资源
    mut res_mut: ResMut<T>,       // 可变资源
    events: EventReader<E>,        // 事件读取
    time: Res<Time>,               // 时间
    keys: Res<ButtonInput<K>>,     // 输入
) { ... }
```

- 第一个参数前加 `mut` 修饰可变
- `Query<(&A, &mut B), With<C>>` 限定带 C 组件的实体
- 系统之间通过 `Resource`/`Event`/`Query` 解耦，**不直接传值**

## Query — 查询

```rust
fn move_players(
    mut q: Query<(&mut Transform, &Speed), With<Player>>,
    time: Res<Time>,
) {
    for (mut t, s) in &mut q {
        t.translation.x += s.0 * time.delta_seconds();
    }
}
```

常用过滤器：`With<T>` / `Without<T>` / `Added<T>` / `Changed<T>` / `Or<(T1, T2)>`。

## Event — 事件

```rust
#[derive(Event)]
struct Damage(pub f32);

// 注册
app.add_event::<Damage>();

// 发送
fn attack(mut ew: EventWriter<Damage>) {
    ew.send(Damage(10.0));
}

// 接收
fn take_damage(mut er: EventReader<Damage>, mut q: Query<&mut Health>) {
    for ev in er.read() {
        for mut h in &mut q { h.0 -= ev.0; }
    }
}
```

## 速查表

| 用途 | API | 模块 |
|------|-----|------|
| 3D 网格 | `Mesh3d(handle)` | `bevy::prelude` |
| 3D 材质 | `MeshMaterial3d(handle)` | `bevy::prelude` |
| 3D 场景 | `SceneRoot(handle)` | `bevy::prelude` |
| 3D 相机 | `Camera3d` | `bevy::prelude` |
| 2D 相机 | `Camera2d` | `bevy::prelude` |
| 加载资源 | `AssetServer::load("path")` | `bevy::prelude` |
| 方向光 | `DirectionalLight` | `bevy::prelude` |
| 环境光 | `GlobalAmbientLight` (Resource) | `bevy::prelude` |
| 输入 | `ButtonInput<KeyCode>` | `bevy::input` |

## 版本锁定

所有代码基于 Bevy 0.15+；如升级到 0.16 先查 [Bevy 迁移指南](https://bevyengine.org/learn/migration-guides/)。
