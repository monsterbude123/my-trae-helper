# babylon-quirks.md

> 来源：godogen babylon/quirks.md（已知坑 + 调优，2026-06 提取）
> 关联：babylon-scripting/SKILL.md §已知坑 / §性能约束
> 目的：8 类常见坑 — context lost / Audio / WebGLInspector / 性能 / 纹理 / 资源 / HMR / 移动端。

## §1 WebGL context lost

**症状**：切换浏览器标签页或长时间挂起后，画面卡死变黑。

**根因**：浏览器回收 GPU 资源，WebGL context 被销毁。

**处理**：

```ts
engine.onContextLostObservable.add(() => engine.stopRenderLoop());
engine.onContextRestoredObservable.add(() => {
  scene.restartRendering();
  engine.runRenderLoop(() => scene.render());
});
```

> 关键：必须停止再重启，否则只触发一次。

## §2 AudioContext 移动端限制

**症状**：iOS Safari / Android Chrome 上 BGM 自动播放无声音。

**根因**：浏览器自动播放策略 — 必须在用户首次交互后才能 `AudioContext.resume()`。

**处理**：

```ts
const audio = new AudioContext();
window.addEventListener("pointerdown", () => audio.resume(), { once: true });
```

> 移动端按设计需用户点击页面后才能播放音频。

## §3 WebGL Inspector（Chrome 扩展）

**用途**：检查 Babylon 场景图、DrawCall、GPU 状态。

```text
Chrome Web Store → 搜索 "Spector.js"（Babylon 官方推荐）
→ 启用后 DevTools 多出 "Spector" 标签
→ 录制帧 → 查看每条 draw call 的 shader / 纹理 / uniform
```

> 性能调优先于 Spector，再考虑 §4 的代码层优化。

## §4 性能调优清单

| 优化项 | 做法 | 收益 |
|--------|------|------|
| Sprite 批处理 | `SpriteManager` 复用 | 减少 draw call |
| 视锥剔除 | `mesh.cullingStrategy = AbstractMesh.CULLINGSTRATEGY_BOUNDINGSPHERE_ONLY` | 减少 CPU 计算 |
| 阴影分辨率 | `shadowGenerator.useBlurExponentialShadowMap` + `mapSize=1024` | GPU 平衡 |
| 材质共享 | 多 mesh 引用同一 StandardMaterial | 减少 shader 切换 |
| 帧率自适应 | `SceneOptimizer.OptimizeAsync(scene, { autoGeneratePriorities: true })` | 低端机自动降级 |
| 网格冻结 | `mesh.freezeWorldMatrix()`（静态物体） | 省 CPU |
| LOD | `mesh.addLODLevel(distance, lowMesh)` | 远距离用低模 |

## §5 纹理压缩

**原则**：PNG → WebP（无损 30%↓） / JPG（有损 70%↓）；大纹理走 KTX2/Basis。

```ts
import { Texture } from "@babylonjs/core/Materials/Textures/texture";

const tex = new Texture("/assets/bg.webp", scene, true, false);
tex.anisotropicFilteringLevel = 4;  // 斜视清晰度
```

| 类型 | 用途 |
|------|------|
| WebP | 通用位图（首选） |
| KTX2 | GPU 压缩（basis universal） |
| DDS | 老格式，慎用 |

> 移动端优先 KTX2 + `engine.setHardwareScalingLevel(devicePixelRatio)`。

## §6 资源 404

**症状**：控制台报 `Failed to load resource: 404`，但文件存在。

**根因**：路径写错或 vite `publicDir` 配置错误。

**修复**：

```ts
// 正确：放到 public/ 下
new Texture("/assets/bg.webp", scene);

// 错：相对 src/ 路径（vite build 后失效）
new Texture("./bg.webp", scene);
```

> 资源统一放 `public/`，引用以 `/` 开头。

## §7 HMR 资源泄露

**症状**：开发中编辑 .ts 文件后 FPS 骤降，最终崩溃。

**根因**：每次热重载都创建新 Engine，但旧 Engine 未释放 → GPU 资源耗尽。

**修复**：见 `babylon-patterns.md §4` 的 `import.meta.hot.dispose`。

## §8 移动端 60FPS 锁帧

**症状**：手机浏览器锁 30FPS，PC 端正常 60FPS。

**根因**：浏览器为了省电默认锁低帧率。

**处理**：

```ts
engine.setHardwareScalingLevel(1 / window.devicePixelRatio);
// 强制高刷
scene.getEngine().disablePerformanceMonitorInBackground = false;
```

> iOS Safari 强制 ≤60FPS，无解；Android Chrome 可用 `requestAnimationFrame` polyfill 优化。

## §9 坑登记

| 新坑 | 触发条件 | 临时方案 | 添加日期 |
|------|---------|---------|---------|
| -    | -       | -       | -       |

> 发现新坑 → 追加到上表 + 写复现 case。
