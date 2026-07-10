# bevy-quirks.md

> 来源：godogen bevy/quirks.md（实战踩坑汇总）
> 关联：`bevy-engine-build/SKILL.md §已知坑` + `bevy-scripting/SKILL.md §核心铁律`

实战高频踩坑。遇到表内症状先查这一节。

## B0004 warning — 父锚点缺少 Visibility

**症状**：
```
warning[B0004]: bevy_transform: the `Visibility` component is missing
```

**根因**：父实体有 `Children` 但没有 `Visibility` 和 `Transform` 两个组件。

**修复**：给父实体加 `#[require(Transform, Visibility)]` 或手动添加：

```rust
commands.spawn((
    TransformBundle::default(),
    VisibilityBundle::default(),
    // children...
)).with_children(|p| { ... });
```

## GLTF texture 不显示

**症状**：模型出现在屏幕中但**全白/全黑/纯色**，无贴图。

**根因**：JPG 纹理未启用 jpeg feature，loader 静默跳过。

**修复**：

```toml
[dependencies]
bevy = { version = "0.15", features = ["jpeg"] }
```

> PNG / KTX2 不需要额外 feature。WebP 需要 `bevy = { features = ["webp"] }`。

## 程序化地形不可见

**症状**：手写 `Mesh` / 自定义 `MeshBuilder` 出来的 mesh 一面可见另一面不见。

**根因**：三角形顶点 winding 顺序（顺时针/逆时针）与背面剔除设置冲突。

**修复**：
- 默认 `CullMode::Back` → 顶点按**逆时针**（CCW）排列正面
- 如有大量反面可见 → 改 mesh 让 CCW 朝向相机，或临时设 `CullMode::None`

## Screenshot 未保存

**症状**：`cargo run --bin capture` 跑完无报错，但 `screenshots/` 目录为空。

**根因**：`Screenshot::image(...).observe(save_to_disk)` 是**异步**事件，主循环在保存完成前就退出了。

**修复**：用 latched state 等 save_to_disk 完成后再退出：

```rust
#[derive(Resource, Default)]
struct CaptureDone(bool);

fn after_save(mut done: ResMut<CaptureDone>, mut exit: EventWriter<AppExit>) {
    if done.0 { exit.send(AppExit); }
}
```

完整模板见 `references/bevy-capture.md`。

## BorderRadius 位置

**症状**：编译失败 `BorderRadius not found in prelude`。

**根因**：Bevy 0.15 中 `BorderRadius` 改为 `Node` 内部字段，**不是独立组件**。

**修复**：

```rust
// ❌ 错误
commands.spawn((NodeBundle::default(), BorderRadius::all(Val::Px(8.0))));

// ✅ 正确
commands.spawn(NodeBundle {
    style: Style {
        border: UiRect::all(Val::Px(2.0)),
        ..default()
    },
    border_radius: BorderRadius::all(Val::Px(8.0)),
    ..default()
});
```

## Offscreen capture panic（Linux）

**症状**：`xvfb-run cargo run` panic `failed to create window`。

**根因**：默认 `DefaultPlugins` 强制创建主窗口；headless X 下失败。

**修复**：使用专用 capture binary（见 `bevy-capture.md`），关键 wiring：

```rust
.add_plugins(DefaultPlugins.set(WindowPlugin {
    primary_window: None,
    ..default()
}))
.disable::<WinitPlugin>()
.add_plugins(ScheduleRunnerPlugin::run_loop(Duration::from_secs_f64(1.0/30.0)))
```

## Capture binary 找不到 asset

**症状**：`AssetServer::load("models/hero.gltf")` 返回 handle 但 spawn 时找不到。

**根因**：`cargo run --bin capture` 的 CWD 不是 crate root，assets 路径解析失败。

**修复**：在 crate root 运行：

```bash
cd /path/to/project
cargo run --bin capture
```

或者用 `--manifest-path`：

```bash
cargo run --bin capture --manifest-path /path/to/project/Cargo.toml
```

## 状态切换不触发 OnEnter

**症状**：调用 `next_state.set(NewState)` 后 `OnEnter(NewState)` 不执行。

**根因**：未注册状态 `app.add_state::<AppState>()`，或 `AppState` 没派生 `Default`。

**修复**：

```rust
#[derive(States, Debug, Clone, Copy, Default, Eq, PartialEq, Hash)]
pub enum AppState { #[default] Title, World }
```

## 调试技巧

```rust
fn debug(q: Query<Entity>, state: Res<State<AppState>>) {
    info!("[{}] entities = {}", state.get(), q.iter().count());
}
```