# Unity BuildScript.cs 模板与构建详解

> 来源：CC Studio release-checklist + launch-checklist
> 关联：unity-engine-build SKILL.md §构建命令 > `references/unity-build-script.md`

---

## §1 BuildScript.cs 完整模板

```csharp
#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.AddressableAssets.Settings;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class BuildScript
{
    private const string BuildDir = "Build";

    [MenuItem("Build/Windows")]
    public static void BuildWindows()
        => Build(BuildTarget.StandaloneWindows64, BuildOptions.None, ".exe");

    private static void Build(BuildTarget target, BuildOptions options, string ext)
    {
        IncrementVersion();
        AddressableAssetSettings.BuildPlayerContent();
        string path = $"{BuildDir}/{target}/{PlayerSettings.productName}{ext}";
        var bp = new BuildPlayerOptions
        {
            scenes = EditorBuildSettingsScene.GetActiveSceneList(EditorBuildSettings.scenes),
            locationPathName = path, target = target, options = options
        };
        BuildReport report = BuildPipeline.BuildPlayer(bp);
        BuildResult(report, path);
    }
}
#endif
```

---

## §2 平台枚举映射

| 平台参数 | `BuildTarget` 枚举 | 输出扩展名 |
|---------|-------------------|-----------|
| Win64 | `StandaloneWindows64` | `.exe` |
| MacOS | `StandaloneOSX` | `.app` |
| Linux64 | `StandaloneLinux64` | 无扩展（二进制） |
| Android | `Android` | `.apk` / `.aab` |
| iOS | `iOS` | Xcode 项目目录 |
| WebGL | `WebGL` | 输出目录 |
| DedicatedServer | `StandaloneWindows64` + `EnableHeadlessMode` | `.exe` |

CI 入口按 `-buildTarget` 参数分发：

```csharp
switch (GetArg("-buildTarget"))
{
    case "Win64": BuildWindows(); break;
    case "MacOS": BuildMac(); break;
    case "Linux64": BuildLinux(); break;
    case "Android": BuildAndroid(); break;
    case "iOS": BuildIOS(); break;
    case "WebGL": BuildWebGL(); break;
    default: EditorApplication.Exit(1); break;
}
```

---

## §3 BuildOptions 参数

| 选项 | 含义 | 适用场景 |
|------|------|---------|
| `None` | 标准 Release 构建 | 正式发布 |
| `Development` | 启用 Profiler + 开发控制台 | 内部测试 |
| `AllowDebugging` | 允许脚本调试器连接 | Development 构建 |
| `CompressWithLz4` | LZ4 压缩（快速加载） | 桌面端默认 |
| `CompressWithLz4HC` | LZ4HC 压缩（高压缩率） | 移动端推荐 |
| `EnableHeadlessMode` | 无头模式（服务器） | Dedicated Server |

```csharp
var options = BuildOptions.Development | BuildOptions.AllowDebugging | BuildOptions.CompressWithLz4;
```

---

## §4 Addressables 构建集成

```csharp
private static void BuildAddressables()
{
    var settings = AddressableAssetSettingsDefaultObject.Settings;
    if (settings == null) { Debug.LogWarning("Addressables 未配置"); return; }
    AddressableAssetSettings.CleanPlayerContent(settings.ActivePlayerDataBuilder);
    AddressableAssetSettings.BuildPlayerContent();
}
```

**调用时机**：`BuildPipeline.BuildPlayer()` 之前。跳过将导致 `Exception: Unable to load asset`。

---

## §5 版本号自动递增

```csharp
private static void IncrementVersion()
{
    string today = DateTime.Now.ToString("yy.MM.dd");
    string[] parts = PlayerSettings.bundleVersion.Split('.');
    int buildNum = 1;
    if (parts.Length == 4 && parts[0] + "." + parts[1] + "." + parts[2] == today)
        buildNum = int.Parse(parts[3]) + 1;
    PlayerSettings.bundleVersion = $"{today}.{buildNum}";
    System.IO.File.WriteAllText($"{BuildDir}/build-version.txt",
        $"{PlayerSettings.bundleVersion}\n{DateTime.Now:yyyy-MM-dd HH:mm:ss}");
}
```

---

## §6 CI/CD 命令行模式

```bash
# 通用模板
unity -quit -batchmode -projectPath ./MyProject \
  -buildTarget <Win64|MacOS|Linux64|Android|iOS|WebGL> \
  -executeMethod BuildScript.Build<Platform> \
  -logFile ./build.log
```

| 参数 | 说明 |
|------|------|
| `-quit` | 构建完成后退出 |
| `-batchmode` | 无 GUI 模式 |
| `-projectPath` | 项目根目录（含 `Assets/`） |
| `-executeMethod` | 静态方法全限定名 |
| `-logFile` | 指定日志输出路径（推荐） |

---

## §7 常见构建失败处理

| 错误 | 原因 | 解决 |
|------|------|------|
| `No active license found` | CI 环境许可证未激活 | 使用 `.ulf` 许可证文件（路径：`~/.local/share/unity3d/Unity/Unity_lic.ulf`）|
| IL2CPP 构建卡住 | 大型项目编译超时 | 降低 `Stripping Level` 为 `Minimal`，增加 CI timeout |
| 条件编译代码未生效 | Missing scripting symbol | 检查 `PlayerSettings → Scripting Define Symbols` |
| `Scene couldn't be loaded` | Scene 未加入列表 | `File → Build Settings → Add Open Scenes` |
