# Godot 引擎构建详解

> 来源：godogen godot/ + CC Studio godot-specialist
> 关联：godot-engine-build SKILL.md §构建流程 + §构建命令 + §Proof Bundle 验证

---

## §1 构建准备

### 目录结构检查

构建前必须确认以下目录存在且结构正确：

```
project/
├── project.godot          # Godot 项目文件
├── assets/                # 原始素材（纹理/音频/模型）
├── .import/               # 引擎生成的导入缓存
├── scenes/                # .tscn 场景文件
└── scripts/               # .gd / .cs 脚本文件
```

### assets/ 完整性

```bash
# 快速检查素材是否存在（与 ASSETS.md 对照）
godot --headless --path ./project --script res://tests/check_assets.gd
```

检查项：所有 `res://` 路径可解析 / 纹理非空 / 没有引用不存在的 UID。

### .import/ 清理时机

| 场景 | 操作 |
|------|------|
| 首次克隆项目 | `godot --headless --import` 生成 `.import/` |
| 素材文件变更后 | 重新运行 `--import`，旧缓存自动失效 |
| 构建失败白块 | 删除 `.import/` 后重跑 `--import` |
| CI 环境 | 每次构建前 `--import`，不缓存 `.import/` |

---

## §2 平台导出配置

### Editor Settings → Export 界面

在 Godot 编辑器中：`Project → Export`，添加各平台 Preset。配置后生成 `export_presets.cfg`。

### export_presets.cfg 示例

```ini
[preset.0]
name="Windows Desktop"
platform="Windows Desktop"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"

[preset.1]
name="Web"
platform="Web"
runnable=true
custom_template/debug=""
headless=false
vram_texture_compression/for_desktop=true
html/export_icon=true
```

每个 Preset 需配置：导出路径模板、资源过滤器、平台特有选项（如 Web 的 SharedArrayBuffer）。

---

## §3 命令行构建参数详解

```bash
# 基本形式
godot --headless --path <project_path> <export_action> "<preset_name>" <output_path>

# 关键参数
--headless          # 无 GUI 模式，CI 必须
--path <dir>        # 项目根目录（含 project.godot）
--import            # 导入素材（首次或素材变更后）
--export-release    # Release 构建（优化、去除调试）
--export-debug      # Debug 构建（含调试符号）
--write-movie       # 录制游戏画面视频
--fixed-fps <N>     # 固定帧率（确定性截图前提）
--script <path>     # 运行指定脚本
```

注意：
- `--export-release "Preset Name"` 中 Preset Name 必须与 `export_presets.cfg` 中 `name` 字段完全一致。
- `--path` 必须指向包含 `project.godot` 的目录。

---

## §4 各平台配置差异

### Windows
- 输出：`.exe` + `.pck`（或嵌入 exe 的单文件）
- 签名：使用 `signtool` 签名以避免 SmartScreen 警告
- 注意：`export_filter` 设为 `all_resources` 确保依赖库完整

### macOS
- 输出：`.app` bundle 或 `.zip`
- 签名 + Notarization：`codesign --deep -s "Developer ID" Game.app`
- Godot 4.x 导出为 `.dmg` 需外部工具（如 `create-dmg`）
- 注意：需 macOS 环境下构建（无交叉编译）

### Linux
- 输出：`.x86_64` 二进制
- 权限：`chmod +x game.x86_64`
- 依赖：确认目标系统有 `libgtk-3`、`libpulse` 等运行时库
- 注意：Godot 静态链接大部分依赖，基本无需额外安装

### Android
- 输出：`.apk` 或 `.aab`
- SDK 路径：`ANDROID_HOME` 指向 Android SDK 根目录
- keystore：debug 用 `debug.keystore`，release 需正式签名
- 详见 `references/android-build.md`

### Web (HTML5)
- 输出：`index.html` + `.wasm` + `.pck`
- SharedArrayBuffer：需要服务器返回以下头：
  ```
  Cross-Origin-Opener-Policy: same-origin
  Cross-Origin-Embedder-Policy: require-corp
  ```
- PWA：可选配置 `service-worker.js` 实现离线可用

---

## §5 Proof Bundle 截图自动化

### --write-movie 录制

```bash
# 录制确定性的 gameplay 视频
godot --path ./project --write-movie ./screenshots/video.avi --fixed-fps 60
```

### ffmpeg 提取关键帧

```bash
# 提取指定时间点的帧（每 5 秒一帧）
ffmpeg -i screenshots/video.avi -vf "fps=1/5" \
  screenshots/result/scene_%02d.png

# 转换为 mp4
ffmpeg -y -i screenshots/video.avi -c:v libx264 -pix_fmt yuv420p \
  screenshots/result/video.mp4
```

### 截图命名规范

```
screenshots/result/{build_tag}/
├── title.png          # 标题画面（第 1 帧）
├── scene_01.png       # 5s 快照
├── scene_02.png       # 10s 快照
├── scene_03.png       # 15s 快照（关键剧情节点）
├── video.mp4          # 完整 15s 录像
└── proof.md           # 验证说明
```

---

## §6 CI/CD 集成

### GitHub Actions runner 示例

```yaml
- name: Build Godot Project
  run: |
    godot --headless --path ./project --import
    godot --headless --path ./project \
      --export-release "Windows Desktop" ./build/win/game.exe
    godot --headless --path ./project \
      --export-release "Web" ./build/web/index.html

- name: Proof Bundle
  run: |
    godot --path ./project --write-movie ./screenshots/video.avi --fixed-fps 60
    ffmpeg -y -i screenshots/video.avi -c:v libx264 \
      screenshots/result/video.mp4
```

CI 要点：
- 使用 `godot-ci` Docker 镜像或裸机安装 Godot 二进制
- `--headless` 模式兼容所有 Godot 构建命令
- 将 `export_presets.cfg` 一并提交到仓库
- Proof Bundle 产物上传为 Artifact 供人工审查
