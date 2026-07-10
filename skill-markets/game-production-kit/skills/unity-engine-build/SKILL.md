---
name: unity-engine-build
description: Unity 引擎构建与验证 — Unity 项目构建为多平台产物（Windows/Mac/Linux/Android/iOS/WebGL）。包含确定性截图验证 proof bundle。触发词：Unity构建、Unity导出、unity build、unity deploy、unity打包。
user-invocable: true
---

# Unity 引擎构建与验证

> 吸收自 CC Studio release-checklist + launch-checklist 发布管线模式 + godogen 多引擎 capture 模式。

将 Unity 项目构建为可运行产物，并进行视觉验证。

> 前置条件：`game-quality-gate` 门禁已通过，`unity-scripting` 脚本已完成。
>
> 协作关系：在当前 kit 编排器路由下执行，已知 `unity-scripting` + `game-quality-gate` 产出。

## 核心铁律

```
1. 构建后必须生成 proof bundle（截图 + 视频）
2. 多平台构建用 CI pipeline，不同时在本地构建所有目标
3. IL2CPP 用于移动端/WebGL，Mono 用于桌面端
4. Addressables 构建前运行 Addressables.BuildPlayerContent()
5. Player Settings 检查：Bundle Identifier、Version、Icon
```

## 构建流程

```
1. 素材验证 → 确认 AddressableAssets 组配置
2. Build Settings 检查 → Scenes In Build + Platform + Player Settings
3. Addressables.BuildPlayerContent() → 资产包构建
4. BuildPipeline.BuildPlayer() → 目标平台产物
5. 截图验证 proof bundle → 人工确认
```

## 构建命令

```bash
# 命令行构建（各平台）
# Windows
unity -quit -batchmode -buildTarget Win64 -projectPath ./project -executeMethod BuildScript.BuildWindows

# macOS
unity -quit -batchmode -buildTarget MacOS -projectPath ./project -executeMethod BuildScript.BuildMac

# Linux
unity -quit -batchmode -buildTarget Linux64 -projectPath ./project -executeMethod BuildScript.BuildLinux

# Android
unity -quit -batchmode -buildTarget Android -projectPath ./project -executeMethod BuildScript.BuildAndroid

# iOS (Xcode 项目)
unity -quit -batchmode -buildTarget iOS -projectPath ./project -executeMethod BuildScript.BuildIOS

# WebGL
unity -quit -batchmode -buildTarget WebGL -projectPath ./project -executeMethod BuildScript.BuildWebGL
```

> BuildScript.cs 完整模板 → `references/unity-build-script.md`

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

**视频录制**: 使用 Unity Recorder Package 或第三方工具（OBS/FFmpeg 屏幕录制）。

## 构建前检查

- `PlayerSettings.productName` 已设置
- `PlayerSettings.bundleVersion` 已递增
- Scenes In Build 列表完整（无遗漏/多余）
- Addressables groups 配置正确
- IL2CPP Code Generation 设为 `Faster (smaller) builds`（非调试构建）
- Strip Engine Code 开启（减小包体）
- 图标已设置（多分辨率）

## 常见构建错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `Scene couldn't be loaded` | Scene 未加入 Build Settings | 添加 Scene 到 Scenes In Build |
| Addressables 加载失败 | 未运行 Build Content | `Addressables.BuildPlayerContent()` |
| IL2CPP build 超慢 | 未配置增量构建 | 使用 `BuildOptions.AcceptExternalModificationsToPlayer` |
| Android SDK not found | Android 模块未安装 | Unity Hub → 安装 Android Build Support |
| WebGL 内存溢出 | 素材未优化 | 压缩纹理、减少 Addressables 包大小 |
| missing asmdef reference | 编译单元未关联 | 检查 .asmdef 文件的引用列表 |
