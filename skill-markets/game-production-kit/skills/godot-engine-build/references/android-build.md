# Godot Android 构建详解

> 来源：godogen android-build.md
> 关联：godot-engine-build SKILL.md §Android 构建

---

## §1 环境准备

### 必需组件

```bash
# Android SDK (API 34+) — 含 build-tools + platform-tools
# NDK — Godot 4.x 需要 NDK r23 或更高
# JDK 17+ — 签名和构建工具链
# Godot Android Build Templates — 编辑器中安装
```

### 环境变量

```powershell
$env:ANDROID_HOME = "C:\Android\Sdk"
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
$env:Path += ";$env:ANDROID_HOME\platform-tools;$env:ANDROID_HOME\cmdline-tools\latest\bin"
```

```bash
export ANDROID_HOME=/opt/android/sdk
export JAVA_HOME=/usr/lib/jvm/java-17
export PATH=$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH
```

### Godot Android Build Templates

编辑器中：`Editor → Manage Export Templates → Install Android Build Template`。
或手动下载模板放到 `%APPDATA%/Godot/export_templates/<version>/`。

---

## §2 Keystore 配置

### Debug keystore（开发用）

```bash
keytool -genkey -v \
  -keystore debug.keystore \
  -alias androiddebugkey \
  -storepass android \
  -keypass android \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -dname "CN=Android Debug,O=Android,C=US"
```

### Release keystore（发布用）

```bash
keytool -genkey -v \
  -keystore release.keystore \
  -alias mygame \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -storepass <强密码> -keypass <强密码>
```

### Editor Settings 填写

`Editor → Editor Settings → Export → Android`：

| 字段 | 值 |
|------|-----|
| `adb` | `$ANDROID_HOME/platform-tools/adb` |
| `jarsigner` | JDK 自带 |
| `debug keystore` | `debug.keystore` 路径 |
| `debug keystore user` | `androiddebugkey` |
| `debug keystore pass` | `android` |

⚠️ **安全注意**：Release keystore 绝不提交到版本控制，使用 CI Secrets 存储密码。

---

## §3 APK 构建

```bash
# Debug APK（快速迭代）
godot --headless --path ./project --export-debug "Android" ./build/game-debug.apk

# Release APK（需 keystore 在 export_presets.cfg 中配置）
godot --headless --path ./project --export-release "Android" ./build/game-release.apk

# Release AAB（Google Play 要求）
godot --headless --path ./project --export-release "Android" ./build/game-release.aab
```

### export_presets.cfg Android 段关键字段

```ini
[preset.2]
name="Android"
platform="Android"
export_filter="all_resources"
custom_template/debug=""
custom_template/release=""
architectures/armeabi-v7a=true
architectures/arm64-v8a=true
architectures/x86_64=false
keystore/debug="debug.keystore"
keystore/debug_user="androiddebugkey"
keystore/debug_password="android"
package/unique_name="com.example.mygame"
version/code=1
version/name="1.0.0"
```

---

## §4 ABI 选择

| ABI | 目标设备 | Play Console 要求 |
|-----|---------| ------------------|
| `armeabi-v7a` | 旧 ARM 设备（32-bit） | 可选 |
| `arm64-v8a` | 现代 ARM 设备（64-bit） | **必须包含** |
| `x86_64` | 模拟器 / Chromebook | 可选 |

Play Console 2021 年起要求所有 APK/AAB 必须包含 `arm64-v8a` 原生库。建议勾选 `armeabi-v7a` + `arm64-v8a`，放弃 `x86_64`（减小包体）。

---

## §5 AAB vs APK

| 维度 | APK | AAB |
|------|-----|-----|
| 分发方式 | 手动安装 / 第三方商店 | Google Play 专用 |
| 包体 | 包含所有 ABI + 密度 | 动态分发（按设备裁剪） |
| Google Play 要求 | ❌ 新应用不可用 | ✅ 2021 年起强制 |
| 构建命令 | `--export-release "Android" game.apk` | 同上但输出 `.aab` |

生成 AAB：只需将输出路径后缀改为 `.aab`，Godot 自动生成 Android App Bundle 格式。

---

## §6 常见问题

### Build Templates 未安装

错误：`Android build template not found`
解决：`Editor → Manage Export Templates → Install Android Build Template`

### SDK 版本不匹配

错误：`Failed to find Build Tools revision 34.0.0`
解决：`sdkmanager "build-tools;34.0.0" "platforms;android-34"`

### 签名证书过期

错误：`jarsigner: certificate is not valid until...`
解决：删除旧 keystore，重新 `keytool -genkey` 生成（debug.keystore 有效期 10000 天通常够用）

### 包名冲突

错误：`INSTALL_FAILED_UPDATE_INCOMPATIBLE`
解决：修改 `export_presets.cfg` 中 `package/unique_name`，确保与已安装应用不冲突。不同 debug/release 构建用不同包名后缀（如 `.debug`）。
