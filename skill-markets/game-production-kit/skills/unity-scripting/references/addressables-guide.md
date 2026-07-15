# Addressables 资源管理指南

> 来源：CC Studio unity-specialist
> 关联：unity-scripting SKILL.md §详细参考

Unity Addressables 是资源系统的替代方案，替代 `Resources.Load` 提供异步加载、远程分发、内存管理。

## vs Resources.Load

| 特性 | Resources.Load | Addressables |
|------|---------------|-------------|
| 加载方式 | 同步阻塞 | 异步 |
| 打包粒度 | 全在 `Resources/` | 按 Group 分包 |
| 远程更新 | 不支持 | CDN 增量更新 |
| 内存控制 | 手动 Unload | Release 引用计数 |
| 适用场景 | 原型快速验证 | 生产项目 |

> 🛑 生产项目禁 `Resources.Load`，用 Addressables。

## 设置步骤

1. **安装**: Package Manager → `Addressables`
2. **初始化**: `Window → Asset Management → Addressables → Groups` → 点击 `Create Addressables Settings`
3. **标记资产**: 选中资源 → Inspector 勾选 `Addressable`，填写 Key（如 `portrait_alice_happy`）
4. **建 Group**: Groups 窗口右键 `Create New Group`，命名如 `Characters`、`UI`
5. **加 Label**: 对 Group 内资源加 Label（如 `preload_characters`），用于批量操作

## 加载 API

```csharp
// 单资源异步加载
var handle = Addressables.LoadAssetAsync<Sprite>("portrait_alice");
Sprite sprite = await handle.Task;

// 场景加载
var sceneHandle = Addressables.LoadSceneAsync("VN_Chapter1");

// 实例化 Prefab
var goHandle = Addressables.InstantiateAsync("dialogue_box", parent);
GameObject obj = await goHandle.Task;
```

## 内存管理

```csharp
// 释放资产引用
Addressables.Release(handle);

// 释放实例化对象（同时 Destroy + Release）
Addressables.ReleaseInstance(goHandle);

// 预加载后手动控制释放
Addressables.Release(preloadHandle);
```

**规则**: 每次 `LoadAssetAsync` 对应一次 `Release`。`InstantiateAsync` 对应 `ReleaseInstance`。不释放 → 内存泄漏。

## 预加载策略

```csharp
using UnityEngine.AddressableAssets;

public class Preloader : MonoBehaviour
{
    public async UniTask PreloadChapter(string label)
    {
        var handle = Addressables.DownloadDependenciesAsync(label);
        await handle.Task;

        float sizeMB = handle.GetDownloadStatus().TotalBytes / 1024f / 1024f;
        Debug.Log($"预加载完成: {label}, {sizeMB:F1} MB");
        Addressables.Release(handle);
    }
}
```

**策略**: 章节切换时预加载下一章 Label，Loading 界面显示进度条。已下载的资源存在于本地缓存，再次加载立即完成。

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `Exception: InvalidKey` | Key 拼写错误或 Group 未 Build | 检查 Addressables Groups 窗口 → Build |
| 资源路径变化后加载失败 | 未重新 Build | `Build → New Build → Default Build Script` |
| 内存持续增长 | 未 Release | 每个 Load 配 Release，用 Profiler 查泄漏 |
| Remote 加载失败 | CDN 地址错误或未上传 | 检查 `AddressableAssetSettings → Build & Load Paths` |
| Editor 正常 Build 后异常 | Editor 用 AssetDatabase 模式 | `Addressables.InitializeAsync()` 确保运行时初始化 |
