# babylon-api-guide.md

> 来源：godogen babylon/api-guide.md（Babylon 7+ API 速查，2026-06 提取）
> 关联：babylon-scripting/SKILL.md §详细参考
> 目的：核心 API 速查 — Scene / Engine / Camera / Light / SceneLoader / Animation。

## §1 Engine

`Engine` 是 WebGL 上下文封装。所有 Scene 共享一个 Engine。

```ts
import { Engine } from "@babylonjs/core/Engines/engine";

const engine = new Engine(canvas, true, {
  preserveDrawingBuffer: true,  // Playwright 截图需要
  stencil: true,                // GUI 蒙层需要
  antialias: true,
});
```

关键方法：

| 方法 | 作用 |
|------|------|
| `runRenderLoop(cb)` | 启动帧循环 |
| `stopRenderLoop()` | 停止帧循环（HMR 释放） |
| `resize()` | canvas resize 同步 |
| `dispose()` | 销毁 WebGL context |
| `getFps()` | 当前 FPS（性能调优） |

## §2 Scene

`Scene` 是场景图根节点。包含相机、灯光、网格、动画。

```ts
import { Scene } from "@babylonjs/core/scene";

const scene = new Scene(engine);
await scene.whenReadyAsync();  // Playwright 等待渲染就绪
```

场景控制：

| API | 作用 |
|-----|------|
| `scene.activeCamera` | 当前相机 |
| `scene.lights` | 灯光列表 |
| `scene.meshes` | 网格列表 |
| `scene.beginAnimation / stopAnimation` | 动画控制 |
| `scene.onBeforeRenderObservable` | 每帧钩子 |
| `SceneOptimizer.OptimizeAsync(scene)` | 自动降帧 |

## §3 ArcRotateCamera

第三人称环绕相机，最常用。

```ts
import { ArcRotateCamera } from "@babylonjs/core/Cameras/arcRotateCamera";
import { Vector3 } from "@babylonjs/core/Maths/math.vector";

const cam = new ArcRotateCamera(
  "cam",
  -Math.PI / 2,   // alpha: 水平角
  Math.PI / 2.5,  // beta:  垂直角
  10,             // radius: 距离
  Vector3.Zero(), // target: 注视点
  scene
);
cam.attachControl(canvas, true);
cam.lowerRadiusLimit = 3;
cam.upperRadiusLimit = 20;
```

> 鼠标拖拽 = 旋转；滚轮 = 缩放；右键 = 平移。

## §4 HemisphericLight

半球光，模拟环境光（无阴影）。

```ts
import { HemisphericLight } from "@babylonjs/core/Lights/hemisphericLight";

const light = new HemisphericLight("hemi", new Vector3(0, 1, 0), scene);
light.intensity = 0.7;
light.groundColor = new Color3(0.2, 0.2, 0.3);
```

需要阴影时改用 `DirectionalLight` + `ShadowGenerator`。

## §5 SceneLoader（资源加载）

加载 `.glb` / `.gltf` / `.obj` 资源到场景。

```ts
import { SceneLoader } from "@babylonjs/core/Loading/sceneLoader";

await SceneLoader.ImportMeshAsync(
  "",                              // 父目录（gltf 内嵌用）
  "character.glb",                 // 文件名
  "/assets/models/",               // 路径
  scene,
  undefined,                       // onSuccess
  ".glb"                           // 扩展名
);
```

异步加载完毕 → `await scene.whenReadyAsync()` → 渲染稳定。

## §6 Animation

`Animation` 关键帧 + 缓动函数。

```ts
import { Animation } from "@babylonjs/core/Animations/animation";
import { CubicEase, EasingFunction } from "@babylonjs/core/Animations/easing";

const anim = new Animation(
  "fadeIn", "scaling", 60,
  Animation.ANIMATIONTYPE_VECTOR3,
  Animation.ANIMATIONLOOPMODE_CONSTANT
);
anim.setKeys([
  { frame: 0, value: new Vector3(0, 0, 0) },
  { frame: 30, value: new Vector3(1, 1, 1) },
]);
const ease = new CubicEase();
ease.setEasingMode(EasingFunction.EASINGMODE_EASEOUT);
anim.setEasingFunction(ease);

scene.beginDirectAnimation(mesh, [anim], 0, 30, false);
```

类型：`ANIMATIONTYPE_FLOAT` / `ANIMATIONTYPE_VECTOR3` / `ANIMATIONTYPE_QUATERNION` / `ANIMATIONTYPE_COLOR3`。

## §7 速查速查表

| 类 | import 路径 | 触发场景 |
|----|------------|---------|
| Engine | `@babylonjs/core/Engines/engine` | 入口 |
| Scene | `@babylonjs/core/scene` | 场景根 |
| ArcRotateCamera | `@babylonjs/core/Cameras/arcRotateCamera` | 3D 角色 |
| HemisphericLight | `@babylonjs/core/Lights/hemisphericLight` | 环境光 |
| SceneLoader | `@babylonjs/core/Loading/sceneLoader` | 加载模型 |
| Animation | `@babylonjs/core/Animations/animation` | 关键帧动画 |
| AdvancedDynamicTexture | `@babylonjs/gui/2D/advancedDynamicTexture` | UI 蒙层 |
| Vector3 | `@babylonjs/core/Maths/math.vector` | 三维向量 |
