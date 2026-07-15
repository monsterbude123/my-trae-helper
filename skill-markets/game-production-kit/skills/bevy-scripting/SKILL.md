---
name: bevy-scripting
description: Bevy 引擎脚本编写 — Rust ECS 架构，code-first 场景构建。AppState 状态机、WorldPlugin 世界构造、Bevy UI 覆盖层、GLTF 模型加载。触发词：Bevy、bevy scripting、Rust ECS、Bevy场景。
user-invocable: true
---

# Bevy 引擎脚本编写

> 吸收自 godogen bevy/ 模块（scaffold 15步 ECS 工作流 + scene-generation code-first + bevy-help API 参考 + quirks.md 已知坑）。

将 Phase 1 产出的 `story-design.md` 转化为 Bevy ECS 系统。

> 前置条件：Phase 1 story-design.md 完成，Phase 2 素材清单可用。
>
> 协作关系：在 kit 编排器路由下执行，已知 `game-story-design` + `game-asset-pipeline`。

## 核心铁律

```
1. Code-first — 场景通过代码 ECS spawning 构建，不使用序列化场景文件
2. DefaultPlugins + 按需添加子插件
3. OnEnter(AppState) 构造世界，Update 中按状态驱动
4. GlobalAmbientLight (Resource) 替代默认光照
5. load path 去 assets/ 前缀（Bevy AssetServer 约定）
6. 父锚点包含 visible children 时必须同时有 Transform 和 Visibility
7. rg glob "*.rs" 而非 type: "rust"
```

> Phase 3 统一产出契约: references/cross-engine-contract.md（scene-manifest.json / asset-references.json 格式）

## 代码质量（Phase 3 内建）

> H2 修复：lint/format 内建到 Phase 3，不推到 Phase 4。

- Lint: `cargo clippy -- -D warnings` — Rust 官方静态分析工具，750+ 条检查规则
- Formatter: `cargo fmt --check` — rustfmt，Rust 官方代码格式化器
- 提交前运行: `cargo fmt --check && cargo clippy -- -D warnings`
- 禁止跳过: clippy 警告 → 不进 Phase 4

## 项目骨架

```
project/
├── Cargo.toml
├── src/
│   ├── main.rs              # App 入口
│   ├── game/                # mod / state / world / ui
│   ├── characters/
│   ├── dialogue/
│   └── bin/capture.rs       # Offscreen 截图二进制
├── assets/                  # Phase 2 素材 (sprites/audio/fonts)
└── docs/engine-reference/bevy/VERSION.md
```

## 从 story-design.md 到 Bevy 的映射

| story-design.md 元素 | Bevy 对应 |
|----------------------|-----------|
| 角色宪法 → 角色属性 | Component (struct) + Bundle |
| 剧情树 → 分支逻辑 | AppState enum + OnEnter/OnExit |
| 场景列表 → 位置/背景 | WorldPlugin spawn_world() 函数 |
| 对话文本 → 演出 | UI Camera (order=1) + TextBundle |
| 立绘切换 → 表达式 | SpriteBundle 纹理替换 |
| BGM/SFX → 音频 | AudioBundle + AssetServer::load() |

## 核心模式索引

| 模式 | 文件 |
|------|------|
| AppState 状态机 | `references/bevy-patterns.md §1` |
| WorldPlugin 世界构造 | `references/bevy-patterns.md §2` |
| 光照（AmbientLight / DirectionalLight / PointLight） | `references/bevy-patterns.md §3` |
| 对话 UI 覆盖层 | `references/bevy-patterns.md §4` |
| GLTF 模型加载 | `references/bevy-gltf-guide.md` |

## 性能约束

- `#[derive(Component)]` + `#[require()]` 缓存组件组合
- `Commands` 批量 spawn（非逐次）
- Bevy UI 使用 `text_system` 非自定义
- 纹理: `bevy::prelude::Image` + `image` crate 压缩
- 更新频率: `Time<Virtual>` 固定时间步

## 开发环境

- Rust 1.80+
- Bevy 0.15+
- `cargo check` / `cargo build` / `cargo run`
- `docs/engine-reference/bevy/VERSION.md` 版本绑定

## 详细参考

- 完整 Rust 模式代码模板（AppState/WorldPlugin/光照/UI）→ `references/bevy-patterns.md`
- Bevy API 版本查找 → `references/bevy-api-guide.md`
- GLTF 3D 模型 → `references/bevy-gltf-guide.md`
- 已知坑 (B0004/offscreen/jpeg feature) → `references/bevy-quirks.md`
