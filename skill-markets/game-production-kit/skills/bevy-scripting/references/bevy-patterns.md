# bevy-patterns.md

> 来源：godogen bevy/scaffold.md + scene-generation.md（code-first 模式族）
> 关联：`bevy-scripting/SKILL.md §核心模式索引` 4 个核心模式

4 个核心 ECS 模式：状态机、世界构造、光照、对话 UI 覆盖层。

## §1 AppState 状态机

用 `enum` 驱动 OnEnter/OnExit，避免巨型 main 循环。

```rust
use bevy::prelude::*;

#[derive(States, Debug, Clone, Copy, Default, Eq, PartialEq, Hash)]
pub enum AppState {
    #[default] Title, World, Dialogue, End,
}
```

注册与切换：

```rust
.add_systems(OnEnter(AppState::Title), spawn_title)
.add_systems(OnExit(AppState::Title), despawn_title)
.add_systems(Update, title_input.run_if(in_state(AppState::Title)))

fn start_game(keys: Res<ButtonInput<KeyCode>>, mut next: ResMut<NextState<AppState>>) {
    if keys.just_pressed(KeyCode::Space) { next.set(AppState::World); }
}
```

**铁律**：`#[derive(States, Default)]` 标记默认；切换用 `NextState<T>` 非 `State<T>`。

## §2 WorldPlugin 世界构造

每个场景一个 `Plugin`，把 spawn 逻辑封装为可复用 trait。

```rust
pub trait WorldPlugin {
    fn spawn_world(&mut self, commands: &mut Commands, assets: &AssetServer);
}

pub struct ForestWorld;
impl Plugin for ForestWorld {
    fn build(&self, app: &mut App) {
        app.add_systems(OnEnter(AppState::World), spawn_world_system);
    }
}
```

最小世界 spawn（地形 + 角色）：

```rust
fn spawn_world_system(mut c: Commands, a: Res<AssetServer>) {
    c.spawn((
        Mesh3d(a.load("models/ground.gltf#Mesh0/Primitive0")),
        MeshMaterial3d(a.load("materials/ground.mat")),
        Transform::from_translation(Vec3::ZERO),
    ));
    c.spawn((
        SceneRoot(a.load("models/hero.gltf#Scene0")),
        Transform::from_xyz(0.0, 0.0, 5.0),
        Visibility::default(),
    ));
}
```

## §3 光照

Bevy 0.15 默认全黑，必须显式设置环境光 + 方向光。

```rust
fn setup_lighting(mut commands: Commands) {
    commands.insert_resource(GlobalAmbientLight {
        color: Color::srgb(0.3, 0.3, 0.35),
        brightness: 800.0,
    });
    commands.spawn((
        DirectionalLight { illuminance: 15000.0, shadows_enabled: true, ..default() },
        Transform::from_rotation(Quat::from_euler(EulerRot::XYZ, -0.8, 0.4, 0.0)),
    ));
    commands.spawn((
        PointLight { intensity: 1_500_000.0, range: 30.0,
                     color: Color::srgb(1.0, 0.7, 0.4), ..default() },
        Transform::from_xyz(2.0, 3.0, 1.0),
    ));
}
```

**铁律**：不设 `GlobalAmbientLight` → 3D 物体全黑；不设 `DirectionalLight` → 无阴影。

## §4 对话 UI 覆盖层

UI 摄像机在 3D 之上，`order=1` 渲染于世界后。

```rust
fn setup_dialogue_ui(mut commands: Commands, assets: Res<AssetServer>) {
    // UI 相机覆盖在 3D 上方
    commands.spawn((
        Camera2d,
        Camera { order: 1, ..default() },
        Transform::from_xyz(0.0, 0.0, 1.0),
    ));
    // 对话框
    commands.spawn(NodeBundle {
        style: Style {
            width: Val::Percent(80.0),
            height: Val::Px(180.0),
            position_type: PositionType::Absolute,
            bottom: Val::Px(40.0),
            left: Val::Percent(10.0),
            ..default()
        },
        background_color: Color::srgba(0.0, 0.0, 0.0, 0.7).into(),
        ..default()
    }).with_children(|p| {
        p.spawn(TextBundle::from_section(
            "你好，旅人。",
            TextStyle {
                font: assets.load("fonts/main.ttf"),
                font_size: 32.0,
                color: Color::WHITE,
            },
        ));
    });
}
```

**要点**：
- `Camera::order = 1` 让 2D 渲染在 3D 之上
- `NodeBundle` 是 UI 容器；`TextBundle` 嵌套在 `with_children` 中
- 字体路径同 GLTF，**不要 `assets/` 前缀**（Bevy AssetServer 自动添加）
