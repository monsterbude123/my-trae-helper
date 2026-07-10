# babylon-patterns.md

> 来源：godogen babylon/architecture.md（OOP-first 模式集，2026-06 提取）
> 关联：babylon-scripting/SKILL.md §核心模式索引
> 目的：4 个核心代码模式 — CreateScene 入口 / SceneBuilderBase / 对话系统 / HMR 循环。

## §1 CreateScene 入口

`CreateScene()` 必须是 async 函数，返回 `Promise<Scene>`。

```ts
// src/main.ts
import { Engine } from "@babylonjs/core/Engines/engine";
import { Scene } from "@babylonjs/core/scene";
import { TitleScene } from "@scenes/TitleScene";

export async function CreateScene(canvas: HTMLCanvasElement): Promise<Scene> {
  const engine = new Engine(canvas, true, { preserveDrawingBuffer: true });
  const scene = new Scene(engine);
  await new TitleScene(scene).build();
  engine.runRenderLoop(() => scene.render());
  window.addEventListener("resize", () => engine.resize());
  return scene;
}

const canvas = document.getElementById("app") as HTMLCanvasElement;
CreateScene(canvas);
```

要点：async 加载、保留 drawingBuffer（截图需要）、runRenderLoop 驱动帧。

## §2 SceneBuilderBase 继承

所有场景对象继承同一基类，统一生命周期方法。

```ts
// src/scenes/SceneBuilderBase.ts
import { Scene } from "@babylonjs/core/scene";

export abstract class SceneBuilderBase {
  constructor(protected scene: Scene) {}
  abstract build(): Promise<void> | void;
  onEnter?(): void;
  onExit?(): void;
  protected onReady(): void {}
}
```

```ts
// src/scenes/TitleScene.ts
import { SceneBuilderBase } from "./SceneBuilderBase";
import { ArcRotateCamera } from "@babylonjs/core/Cameras/arcRotateCamera";

export class TitleScene extends SceneBuilderBase {
  async build() {
    new ArcRotateCamera("cam", -Math.PI / 2, Math.PI / 2, 10, this.scene.activeCamera!.target, this.scene);
  }
}
```

继承链：`GameplayScene → SceneBuilderBase`；`TitleScene → SceneBuilderBase`；`DialogueScene → SceneBuilderBase`。

## §3 对话系统（Promise 包装）

对话 = 异步序列。每一句 await 用户点击。

```ts
// src/dialogue/DialogueRunner.ts
import { Scene } from "@babylonjs/core/scene";
import { AdvancedDynamicTexture } from "@babylonjs/gui/2D/advancedDynamicTexture";
import { TextBlock } from "@babylonjs/gui/2D/controls/textBlock";
import { Button } from "@babylonjs/gui/2D/controls/button";

export type Line = { speaker: string; text: string; sprite?: string };

export class DialogueRunner {
  private ui: AdvancedDynamicTexture;
  constructor(private scene: Scene) {
    this.ui = AdvancedDynamicTexture.CreateFullscreenUI("dlg", true, this.scene);
  }

  async play(lines: Line[]): Promise<void> {
    for (const line of lines) {
      await this.showLine(line);
    }
  }

  private showLine(line: Line): Promise<void> {
    return new Promise((resolve) => {
      const block = new TextBlock();
      block.text = `${line.speaker}: ${line.text}`;
      this.ui.addControl(block);
      const btn = Button.CreateSimpleButton("next", "▼");
      btn.onPointerUpObservable.addOnce(() => {
        this.ui.removeControl(block);
        this.ui.removeControl(btn);
        resolve();
      });
      this.ui.addControl(btn);
    });
  }
}
```

调用方 `await runner.play([...])`，剧情树 = Promise 链。

## §4 Vite HMR 循环

`import.meta.hot` 接受热重载，避免状态污染。

```ts
// src/main.ts 增强
if (import.meta.hot) {
  import.meta.hot.dispose(() => {
    engine.stopRenderLoop();
    scene.dispose();
    engine.dispose();
  });
}
```

Vite 6 默认行为：

| 触发 | 行为 |
|------|------|
| 修改 `.ts` 源文件 | 局部模块热替换 |
| 修改 `index.html` | 整页刷新 |
| 修改 `vite.config.ts` | 需重启 dev server |
| 修改 `package.json` | 需 `npm install` 后重启 |

> 配合 §1 的 `engine.stopRenderLoop()` 释放 GPU 资源；否则多次保存后 WebGL context 泄露 → 浏览器崩溃。
