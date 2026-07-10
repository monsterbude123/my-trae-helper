---
name: godot-engine-build
description: Godot 引擎构建与验证 — 将 Godot 项目构建为可运行产物（Windows/Linux/macOS/Android/Web）。包含 --write-movie 确定性截图验证 + APK 导出 + Android 构建。触发词：Godot构建、Godot导出、godot build、godot deploy、APK导出。
user-invocable: true
---

# Godot 引擎构建与验证

> 吸收自 godogen godot/ 模块（capture.md 确定性截图管线 + test-harness + android-build.md APK导出 + quirks.md 80+ 坑收集）+ CC Studio godot-specialist 子专家体系。

将 Godot 项目构建为可运行产物，并进行视觉验证。

> 前置条件：`game-quality-gate` 门禁已通过，`godot-scripting` 脚本已完成。
>
> 协作关系：在当前 kit 编排器路由下执行，已知 `godot-scripting` + `game-quality-gate` 产出。

## 核心铁律

```
1. 信任截图，不信任代码 — 代码编译通过不代表游戏能玩
2. 构建后必须生成 proof bundle（关键场景截图 + 视频录像）
3. proof bundle 通过确认后才能部署
4. --fixed-fps 确保帧级确定性（同一输入 → 同一截图）
5. --headless 模式用于 CI 构建和批量验证
```

## 构建流程

```
1. 素材导入验证 → 确认 assets/ 下文件结构与 ASSETS.md 一致
2. godot --headless --import → 导入素材到 .import/
3. godot --headless --export-release → 导出目标平台
4. 截图验证 proof bundle → 人工确认
5. 部署（按平台分发）
```

## 构建命令

```bash
# 导入素材（首次构建）
godot --headless --path ./project --import

# 导出 Windows
godot --headless --path ./project --export-release "Windows Desktop" ./build/game.exe

# 导出 Linux
godot --headless --path ./project --export-release "Linux/X11" ./build/game.x86_64

# 导出 macOS
godot --headless --path ./project --export-release "macOS" ./build/game.zip

# 导出 Web (HTML5)
godot --headless --path ./project --export-release "Web" ./build/web/index.html

# 导出 Android APK
godot --headless --path ./project --export-release "Android" ./build/game.apk
```

## Proof Bundle 验证

> 来自 godogen capture.md 确定性截图管线。

```bash
# 录制 game play 视频 (15s, 固定帧率)
godot --path ./project --write-movie ./screenshots/video.avi --fixed-fps 60

# ffmpeg 转换
ffmpeg -y -i video.avi -c:v libx264 -pix_fmt yuv420p screenshots/result/video.mp4
```

**Proof bundle 输出**:

```
screenshots/result/{build_tag}/
├── title.png          # 标题画面
├── scene_01.png       # 第一场景
├── scene_02.png       # 立绘场景
├── scene_03.png       # 关键剧情节点
├── video.mp4          # 15s 游戏流程视频
└── proof.md           # 证据说明
```

**人工确认点**: 标题/立绘位置/字幕配音同步/BGM 正常/场景切换无闪烁。详见 `references/01-build.md`。

## Android 构建

> 来自 godogen android-build.md。

**前置条件**:
- Android SDK (API 34+) / NDK / JDK 17+
- `debug.keystore` 或 release keystore
- Godot Android build templates 已安装

```bash
# 设置 Android SDK 路径
export ANDROID_HOME=/path/to/android/sdk

# 导出 debug APK
godot --headless --path ./project --export-debug "Android" ./build/game-debug.apk

# 导出 release APK (需 keystore)
godot --headless --path ./project --export-release "Android" ./build/game-release.apk
```

> 详细 Android 配置（keystore/签名/ABI） → `references/android-build.md`

## Test Harness

> 来自 godogen test-harness。SceneTree 遍历验证游戏状态。

```bash
# 运行测试套件
godot --headless --path ./project --script res://tests/run_tests.gd
```

验证项目：
- 所有 scene 文件可被 `PackedScene` 加载
- 所有脚本编译通过（`GDScript.parse()` 或 `CSharpScript`）
- 所有素材路径在 `res://assets/` 下存在
- 无循环引用（Autoloads 检查）
- 资源文件（.tres/.res）格式正确

## 常见构建错误

> 来自 godogen quirks.md + MEMORY.md 反馈环。

| 错误 | 原因 | 解决 |
|------|------|------|
| `.import/` 缺失 | 首次构建未导入 | `godot --headless --import` |
| `scene file not found` | 路径大小写错误 | Godot 大小写敏感，检查 .tscn 中 `path` 字段 |
| Android build failed | SDK/NDK 未配置 | 检查 `ANDROID_HOME` 环境变量 |
| `--write-movie` not available | Godot 版本 < 4.0 | 升级到 Godot 4.x |
| 素材白块/缺失 | .import 未触发 | 确认 `res://` 路径正确 |
| GDScript parse error | Godot 3.x 语法混入 | 检查 `@onready` / `create_tween()` 等 4.x API |
| APK 签名失败 | keystore 未提供 | debug 模式用 debug.keystore |

> 新发现的坑写入 `quirks-godot.md`（项目级），kit 维护者定期审查提升到本文件。

## 详细参考

- 引擎构建详解 → `references/01-build.md`
- Android 构建详解 → `references/android-build.md`
