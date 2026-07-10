---
name: godot-scripting
description: Godot 引擎脚本编写 — 将剧情设计转化为 Godot 场景脚本。程序化构建 .tscn、GDScript/C# 双语言参考、SceneBuilderBase 脚手架。触发词：Godot脚本、Godot场景、godot scripting、GDScript。
user-invocable: true
---

# Godot 引擎脚本编写

> 吸收自 godogen godot/ 模块（scaffold 16步工作流 + SceneBuilderBase + 双语言参考）+ CC Studio godot-specialist。

将 Phase 1 产出的 `story-design.md` 转化为 Godot 可运行的场景脚本。

> 前置条件：Phase 1 story-design.md 完成，Phase 2 素材清单可用。
>
> 协作关系：加载时已知 `game-story-design`（读角色宪法和剧情树）+ `game-asset-pipeline`（读 ASSETS.md 素材清单），在 kit 编排器路由下执行。

## 核心铁律

```
1. GDScript: 全局静态类型 + class_name 注册 + @export 暴露参数
2. Godot 4.x API 优先（避开 Godot 3.x 语法）
3. 组合优于继承 — 每个 scene 自包含
4. signals 解耦节点通信（不硬引用兄弟节点）
5. @onready 缓存节点引用，不在 _ready() 中做重计算
6. 脚本文件 glob: "*.gd" 而非 type: "gdscript"（rg 将 .gd 注册为 gap 类型）
```

## 项目骨架

```
project/
├── project.godot
├── scenes/                  # main / ui / game
├── scripts/
│   ├── autoload/            # 全局单例（音频/存档/事件总线）
│   ├── characters/          # 角色行为
│   └── systems/             # 游戏系统
├── assets/                  # 素材（从 Phase 2 产出拷贝）
├── resources/               # .tres 数据资源
└── docs/engine-reference/godot/VERSION.md
```

## 场景架构分离：Scene Builder vs Runtime Script

> Scene Builder 是构建时脚本（extends SceneTree，一次运行产出 .tscn），Runtime Script 是运行时脚本（extends 具体节点，持续执行）。两者 API 可用性完全不同，必须分离。

| 特性 | Scene Builder | Runtime Script |
|------|-------------|----------------|
| extends | `SceneTree` | `CharacterBody3D` / `Node3D` / `Control` |
| 入口 | `_initialize()` | `_ready()` + `_process()` |
| 运行次数 | 一次（构建时） | 持续（运行时） |
| `@onready` | ❌ | ✅ |
| `preload()` | ❌ 用 `load()` | ✅ |
| 信号连接 | ❌ | ✅ 在 `_ready()` 中 |
| `look_at()` 等空间方法 | ❌ | ✅ |
| `_ready()` 触发 | ❌ 需手动调用 | ✅ 自动触发 |

#### Scene Builder 核心规则

```
1. extends SceneTree → _initialize() 入口
2. 构建完整节点树 → set_script() 附加运行时脚本
3. Owner Chain: set_owner_on_new_nodes(root, root) 必须调用一次
4. Pack → Validate (节点数验证) → ResourceSaver.save → quit(0)
```

> 完整 Owner Chain 协议、模板、常见节点组合 → `references/scene-builder-pattern.md`

## 从 story-design.md 到 Godot 场景的映射

| story-design.md 元素 | Godot 对应 |
|----------------------|-----------|
| 角色宪法 → 角色属性 | `class_name` 注册 + `@export` 参数 |
| 剧情树 → 分支逻辑 | signals + scene transitions |
| 场景列表 → 位置/背景 | `PackedScene` + `change_scene_to_file()` |
| 对话文本 → 演出 | DialogueSystem + RichTextLabel |
| 立绘切换 → 表达式 | `set_expression()` + Sprite2D 纹理替换 |

## Godot 4.x 关键 API

> 触发词：需要特定 API 时加载 `godot-genre-visual-novel` 技能获取详细参考。

| 需求 | API | 注意事项 |
|------|-----|---------|
| 场景切换 | `SceneTree.change_scene_to_file()` | Godot 4.x 替代 `change_scene()` |
| 对话 UI | RichTextLabel + `visible_characters` | 打字机效果 |
| 音频 | AudioStreamPlayer / AudioStreamPlayer2D | 背景音乐 vs 音效 |
| TTS 配音 | AudioStreamPlayer + 文件路径 | 从 Phase 2 的 vocal/ 目录 |
| 动画 | AnimationPlayer + 关键帧 | 不是手动插值 |
| Tween | `create_tween()` | Godot 4.x 替代 `Tween.new()` |

## 性能约束

- `set_process(false)` — 不需要逐帧更新的节点禁用它
- 对象池 — 频繁创建/销毁的角色/粒子用对象池
- `VisibleOnScreenNotifier2D` — 离屏节点禁用处理
- 资源加载：`load()` 小资源，`ResourceLoader.load_threaded_request()` 大场景

## 开发环境

- Godot 4.4+ (C# 支持需要 mono 版)
- 编辑器或 `godot --headless` 模式均可
- VERSION.md 检查：`docs/engine-reference/godot/VERSION.md`

## 详细参考

- 完整 GDScript 最佳实践（角色/对话/动画代码模板）→ `references/gdscript-patterns.md`
- C# 对应方案 → `references/csharp-patterns.md`
- 常见坑 (80+ known quirks) → `references/godot-quirks.md`
- Scene Builder 完整模式（Owner Chain + 模板 + 常见节点组合）→ kit `references/scene-builder-pattern.md`
- godogen-ark 深度管线（8 文档协议 + 多后端生成 + 资产注册）→ kit `references/godogen-ark-pipeline.md`
