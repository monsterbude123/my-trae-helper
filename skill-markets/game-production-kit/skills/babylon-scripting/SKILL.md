---
name: babylon-scripting
description: Babylon.js 引擎脚本编写 — TypeScript 浏览器游戏，Vite HMR 热重载开发。OOP-first 架构、SceneBuilderBase 类继承、Playwright 浏览器截图。触发词：Babylon、babylon scripting、babylonjs、TypeScript 浏览器游戏。
user-invocable: true
---

# Babylon.js 引擎脚本编写

> 吸收自 godogen babylon/ 模块（architecture.md OOP-first + scaffold Vite/TS + scene-generation + quirks.md）。

将 Phase 1 产出的 `story-design.md` 转化为 Babylon.js TypeScript 游戏。

> 前置条件：Phase 1 story-design.md 完成，Phase 2 素材清单可用。
>
> 协作关系：在当前 kit 编排器路由下执行。

## 核心铁律

```
1. OOP-first — 所有场景对象继承 SceneBuilderBase
2. TypeScript strict mode + noImplicitAny
3. Vite HMR 开发循环 — 编辑代码即见即所得
4. @babylonjs/core + @babylonjs/gui + @babylonjs/loaders
5. CreateScene() 函数返回 Scene 对象
6. 浏览器原生 Web Audio API（非 Babylon 侧 Sound 仅简单播放）
7. rg glob "*.ts" + "*.tsx"
```

## 项目骨架

```
project/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
├── src/
│   ├── main.ts              # CreateScene() 入口
│   ├── scenes/              # title / gameplay / dialogue
│   ├── characters/          # 角色类
│   ├── dialogue/            # 对话系统
│   └── ui/                  # HUD
├── public/                  # Phase 2 素材 (sprites/audio/fonts)
└── docs/engine-reference/babylon/VERSION.md
```

> 完整 `package.json` + `tsconfig.json` 模板 → `references/babylon-scaffold.md`

## 从 story-design.md 到 Babylon 的映射

| story-design.md 元素 | Babylon 对应 |
|----------------------|-------------|
| 角色宪法 → 角色属性 | Character 类 (extends SceneBuilderBase) |
| 剧情树 → 分支逻辑 | async/await + Promise chain |
| 场景列表 → 位置/背景 | CreateScene() 返回 Scene 对象 |
| 对话文本 → 演出 | `@babylonjs/gui` + TextBlock |
| 立绘切换 → 表达式 | Sprite 纹理替换 + Animation |
| BGM/SFX → 音频 | Web Audio API (AudioContext) |

## 核心模式索引

| 模式 | 文件 |
|------|------|
| CreateScene 入口 | `references/babylon-patterns.md §1` |
| SceneBuilderBase 继承 | `references/babylon-patterns.md §2` |
| 对话系统（Promise 包装） | `references/babylon-patterns.md §3` |
| Vite HMR 循环 | `references/babylon-patterns.md §4` |

## 性能约束

- Sprite 批处理（spriteManager 复用）
- Scene Optimizer 自动降帧（`BABYLON.SceneOptimizer`）
- AudioContext 限制：移动端需用户交互后才能播放
- WebGL context lost/restore 处理
- 纹理压缩：PNG → WebP/JPG

## 开发环境

- Node.js 20+ / Vite 6+ / Babylon.js 7+
- Chrome DevTools (WebGL Inspector)

## 详细参考

- Babylon.js API 参考 → `references/babylon-api-guide.md`
- 完整代码模式（CreateScene/SceneBuilderBase/对话系统）→ `references/babylon-patterns.md`
- 已知坑 (Web Audio/context lost) → `references/babylon-quirks.md`
