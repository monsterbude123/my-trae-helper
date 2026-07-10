---
name: bevy-engine-build
description: Bevy 引擎构建与验证 — 编译 Rust 项目 + offscreen capture 确定性截图验证。包含 cargo build + capture binary + ffmpeg 视频 proof bundle。触发词：Bevy构建、bevy build、cargo build、bevy capture。
user-invocable: true
---

# Bevy 引擎构建与验证

> 吸收自 godogen bevy/ 模块（capture.md offscreen render target + quirks.md + task-execution.md 实现循环）。

将 Bevy Rust 项目编译为可运行产物，并进行视觉验证。

> 前置条件：`game-quality-gate` 门禁已通过，`bevy-scripting` ECS 系统已完成。
>
> 协作关系：在当前 kit 编排器路由下执行。

## 核心铁律

```
1. 信任截图，不信任代码 — cargo check 通过不代表游戏能玩
2. 构建后必须生成 proof bundle（offscreen capture screenshots + 视频）
3. 使用专用 capture binary (src/bin/capture.rs) + offscreen render target
4. TimeUpdateStrategy::ManualDuration 确保帧级确定性
5. cargo fmt -> cargo check -> cargo build -> cargo run — 标准 Rust 循环
```

## 构建流程

```
1. cargo fmt → cargo check → cargo build（标准 Rust 编译）
2. 构建 capture binary: cargo build --bin capture
3. 运行截图: cargo run --bin capture → screenshots/result/{tag}/
4. ffmpeg 编码: frame*.png → video.mp4
5. 人工确认 proof bundle
```

## 构建命令

```bash
# 编译
cargo build --release

# 生产产物在 target/release/
```

## Offscreen Capture 二进制

> 来自 godogen bevy capture.md。专用二进制 `src/bin/capture.rs`。

**关键 wiring**:
- `WindowPlugin { primary_window: None }` → 无窗口
- `disable::<WinitPlugin>()` → 无交互
- `ScheduleRunnerPlugin` → 自动帧循环
- `RenderTarget::Image(handle)` → 渲染到纹理
- `Screenshot::image(handle).observe(save_to_disk)` → 保存

> 完整 capture.rs 模板、save_to_disk 异步管理、latched state → `references/bevy-capture.md`

```bash
# 运行截图（必须在 crate root 运行，asset 路径相对 CWD）
cargo run --bin capture

# 帧序列 → 视频
ffmpeg -y -framerate 30 -i screenshots/result/{tag}/frame%d.png \
  -c:v libx264 -pix_fmt yuv420p screenshots/result/{tag}/video.mp4
```

## Proof Bundle 输出

```
screenshots/result/{build_tag}/
├── frame001.png       # 标题画面
├── frame150.png       # 游戏场景 1
├── frame300.png       # 游戏场景 2
├── frame450.png       # 关键剧情节点
├── video.mp4          # 15s 帧序列编码视频 (30fps × 15s = 450帧)
└── proof.md
```

**失败回退**: 证明帧序列后 → 拿到单帧截图 → 回到 editor loop 修复 → 重新运行 capture

## 实现循环

> 来自 godogen bevy task-execution.md。

```
cargo fmt → cargo check → cargo build → cargo run (桌面) 或 xvfb-run (无头)
→ 检查日志 + 更新 STRUCTURE.md → 循环
```

## 已知坑

> 来自 godogen bevy quirks.md。

| 错误 | 原因 | 解决 |
|------|------|------|
| B0004 warning | 父锚点无 Visibility 但有 visible children | 添加 Visibility 组件 |
| GLTF texture 不显示 | jpg 纹理未启用 jpeg feature | `bevy = { features = ["jpeg"] }` |
| 程序化地形不可见 | Triangle winding + 背面剔除 | 调整顶点顺序（逆时针） |
| offscreen capture panic (Linux) | 默认窗口模式在无头 X 下 panic | 使用 offscreen capture binary |
| Screenshot 未保存 | save_to_disk 是异步的 | 用 latched state 管理退出时机 |
| capture binary 找不到 asset | CWD 不是 crate root | `cargo run --bin capture` 从 crate root 运行 |
| Bevy UI `BorderRadius` | 放在 Node 内部 | 非独立组件 |

> 新发现的坑写入 `quirks-bevy.md`。

## 多平台构建

```bash
# Windows
cargo build --release --target x86_64-pc-windows-msvc

# Linux
cargo build --release --target x86_64-unknown-linux-gnu

# macOS
cargo build --release --target x86_64-apple-darwin

# Web (wasm)
cargo build --release --target wasm32-unknown-unknown
wasm-bindgen --out-dir web/pkg --target web target/wasm32-unknown-unknown/release/game.wasm
```
