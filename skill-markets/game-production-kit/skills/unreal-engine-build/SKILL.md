---
name: unreal-engine-build
description: Unreal Engine 构建与打包 — Unreal 项目构建为多平台产物（Windows/Mac/Linux/Android/iOS）。包含确定性截图验证 proof bundle + 多平台打包配置。触发词：Unreal构建、Unreal打包、unreal build、unreal package、ue5 build。
user-invocable: true
---

# Unreal Engine 构建与打包

> 吸收自 CC Studio release-checklist + launch-checklist 发布管线模式 + devops-engineer CI/CD 模式 + godogen 多引擎 capture 模式。

将 Unreal 项目构建为可运行产物，并进行视觉验证。

> 前置条件：`game-quality-gate` 门禁已通过，`unreal-scripting` 脚本已完成。
>
> 协作关系：在当前 kit 编排器路由下执行，已知 `unreal-scripting` + `game-quality-gate` 产出。

## 核心铁律

```
1. Cook + Build + Stage + Package = 完整打包流程 (UBT + UAT)
2. 构建后必须生成 proof bundle（截图 + 视频）
3. Development 用于测试，Shipping 用于发布
4. Shipping 构建剥离所有调试符号和控制台命令
5. 移动端构建需要对应的 SDK/NDK (Android) 或 Xcode (iOS)
```

## 构建流程

```
1. 素材验证 → 确认 Content/ 下资源引用完整
2. UBT Compile → 编译所有 C++ 模块
3. UAT Cook → 资源烹饪（转换格式 + 剔除未引用）
4. UAT Stage → 资源分阶段部署
5. UAT Package → 最终打包
6. 截图验证 proof bundle → 人工确认
```

## 构建命令

```bash
# 通用语法
RunUAT.bat BuildCookRun \
    -project="path/to/Game.uproject" \
    -platform={Win64|Mac|Linux|Android|IOS} \
    -clientconfig={Development|Shipping} \
    -cook -stage -pak -archive \
    -archivedirectory="path/to/Build"

# Windows
RunUAT.bat BuildCookRun -project="Game.uproject" -platform=Win64 -clientconfig=Development -cook -stage -pak -archive -archivedirectory="./Build/Windows"

# Android
RunUAT.bat BuildCookRun -project="Game.uproject" -platform=Android -clientconfig=Development -cook -stage -pak -archive -archivedirectory="./Build/Android"

# iOS (需要 Mac)
RunUAT.sh BuildCookRun -project="Game.uproject" -platform=IOS -clientconfig=Development -cook -stage -pak -archive -archivedirectory="./Build/IOS"
```

## 编辑器内打包

```
File → Package Project → {Platform}
```

生成的包在项目目录的 `Build/` 或指定 `-archivedirectory` 路径。

## Proof Bundle 验证

```
screenshots/result/{build_tag}/
├── title.png          # 标题画面
├── gameplay_01.png    # 游戏场景 1
├── gameplay_02.png    # 游戏场景 2
├── gameplay_03.png    # 关键剧情节点
├── video.mp4          # 15s 游戏流程录像
└── proof.md
```

**截图**: 使用 HighResShot 控制台命令（Development 构建）或外部工具。
**视频**: OBS Studio / NVIDIA ShadowPlay / Unreal Insights 录制。

## 构建配置检查

### Project Settings

- **Project → Description**: 项目名称/版本/公司信息
- **Project → Maps & Modes**: 默认地图 + GameMode
- **Project → Packaging**: 需要打包的地图列表
- **Platforms → {Platform}**: 平台特定设置（图标/签名/SDK）

### 发布前检查

- Shipping 配置下无 Crash
- 所有 Content 引用有效（无 Missing Reference）
- 包体大小 < 目标平台限制
- 图标和启动画面已设置
- 版本号已递增
- `Config/DefaultGame.ini` 包含生产配置

## 多平台打包策略

| 平台 | 额外要求 | 包体约束 |
|------|---------|---------|
| Windows | 无 | < 50GB (典型) |
| macOS | Mac 构建机 | < 50GB |
| Linux | Linux 构建机 | < 50GB |
| Android | Android SDK + NDK | < 2GB (APK) / < 4GB (AAB) |
| iOS | Mac + Xcode | < 4GB |

> 移动端构建建议 iOS 和 Android 分开处理，不同时在本地构建。

## 常见构建错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `UBT ERROR: Missing precompiled manifest` | Intermediate/ 损坏 | 删除 Intermediate/ 和 Binaries/ 后重新 Generate |
| `UAT ERROR: Cook failed` | 资源引用错误 | 检查 Output Log → Missing Reference |
| `Black textures after cooking` | 纹理压缩设置 | 检查 Texture → Compression Settings |
| `Android SDK not found` | SDK/NDK 未安装 | Epic Games Launcher → Options → Android |
| `Package exceeds size limit` | 未剥离未用资源 | 使用 Asset Audit + `-prereqs` 检查依赖 |
| `Shipping build crashes on startup` | C++ 断言未处理 | 确保无 `check()` / `ensure()` 在生产路径中 |
