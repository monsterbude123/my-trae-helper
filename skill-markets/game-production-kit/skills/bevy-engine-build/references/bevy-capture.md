# bevy-capture.md

> 来源：godogen bevy/capture.md（offscreen render target 完整模板）
> 关联：`bevy-engine-build/SKILL.md §Offscreen Capture 二进制`

专用 `src/bin/capture.rs` 模板：无窗口 → 渲染到 Image → 定时截图 → 保存到磁盘。

## 完整 capture.rs 模板

```rust
use bevy::prelude::*;
use bevy::render::view::RenderTarget;
use bevy::render::view::screenshot::{Screenshot, save_to_disk};
use std::time::Duration;

#[derive(Resource, Default)]
struct FrameCount(u32);

#[derive(Resource, Default)]
struct SavedCount(u32);

#[derive(Resource, Default)]
struct CaptureDone(bool);

fn main() {
    App::new()
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: None,        // 无主窗口
            ..default()
        }))
        .disable::<WinitPlugin>()        // 无交互
        .add_plugins(ScheduleRunnerPlugin::run_loop(
            Duration::from_secs_f64(1.0 / 30.0),  // 30fps 固定
        ))
        .insert_resource(TimeUpdateStrategy::ManualDuration(
            Duration::from_secs_f64(1.0 / 30.0),
        ))
        .init_resource::<FrameCount>()
        .init_resource::<SavedCount>()
        .init_resource::<CaptureDone>()
        .add_systems(Startup, setup_capture)
        .add_systems(Startup, setup_world)
        .add_systems(Update, tick_capture)
        .run();
}
```

## 设置 offscreen camera

```rust
fn setup_capture(
    mut commands: Commands,
    mut images: ResMut<Assets<Image>>,
) {
    // 创建渲染目标纹理
    let target = images.add(Image::new_fill(
        Extent3d { width: 1280, height: 720, depth_or_array_layers: 1 },
        TextureDimension::D2,
        &[0, 0, 0, 0],
        TextureFormat::Rgba8Unorm,
    ));

    // 渲染到该纹理的相机
    commands.spawn((
        Camera3dBundle {
            camera: Camera {
                target: RenderTarget::Image(target.clone()),
                ..default()
            },
            transform: Transform::from_xyz(0.0, 2.0, 8.0)
                .looking_at(Vec3::ZERO, Vec3::Y),
            ..default()
        },
    ));

    // 保存 handle 以便后续截图
    commands.insert_resource(CaptureTarget(target));
}

#[derive(Resource)]
struct CaptureTarget(Handle<Image>);
```

## 触发截图 + 异步保存

```rust
fn tick_capture(
    mut frame: ResMut<FrameCount>,
    mut saved: ResMut<SavedCount>,
    mut done: ResMut<CaptureDone>,
    target: Res<CaptureTarget>,
    mut commands: Commands,
    mut exit: EventWriter<AppExit>,
) {
    if done.0 { return; }
    frame.0 += 1;
    let trigger_frames = [1, 30, 60, 90, 150];
    if trigger_frames.contains(&frame.0) {
        let path = format!("screenshots/result/frame{:03}.png", saved.0 + 1);
        commands.spawn(Screenshot::image(target.0.clone())
            .observe(move |_: Trigger<Screenshot>, mut saved: ResMut<SavedCount>| {
                save_to_disk(path.clone());
                saved.0 += 1;
            }));
    }
    if saved.0 >= trigger_frames.len() as u32 {
        done.0 = true; exit.send(AppExit);
    }
}
```

## 关键 wiring 总览

| 步骤 | 关键点 | API |
|------|--------|-----|
| 无窗口 | `primary_window: None` | `WindowPlugin` |
| 无交互 | 关闭 Winit 插件 | `disable::<WinitPlugin>()` |
| 帧循环 | 30fps 固定步 | `ScheduleRunnerPlugin::run_loop` |
| 时间确定 | 手动推进 | `TimeUpdateStrategy::ManualDuration` |
| 渲染到纹理 | `RenderTarget::Image` | `bevy::render::view` |
| 触发截图 | `Screenshot::image(handle)` | `bevy::render::view::screenshot` |
| 异步保存 | `save_to_disk(path)` | observe 回调 |
| 退出时机 | latched state 计数 | `AppExit` event |

## ScheduleRunner vs Winit

`ScheduleRunnerPlugin` 在 headless 环境（CI/Docker/xvfb）下无需事件循环，靠 `Duration` 间隔推进帧。配合 `TimeUpdateStrategy::ManualDuration` 让时间完全可控 — 同一帧序号永远渲染同一画面。

## 常见错误

| 症状 | 原因 |
|------|------|
| `failed to create window` | 没关 `WinitPlugin` |
| 截图全黑 | 渲染目标尺寸为 0 或相机未指向纹理 |
| 截图 0 字节 | `save_to_disk` 路径相对 CWD |
| 主循环不退出 | latched state 未在 observe 中更新 |

## 与 game-quality-gate 协作

```bash
cargo run --bin capture
ls screenshots/result/*.png
ffmpeg -y -framerate 30 -i screenshots/result/frame%03d.png \
  -c:v libx264 -pix_fmt yuv420p screenshots/result/video.mp4
```

截图 + 视频 = proof bundle，传给 `game-quality-gate` 视觉验收。
