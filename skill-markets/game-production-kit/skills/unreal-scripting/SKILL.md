---
name: unreal-scripting
description: Unreal Engine 脚本编写 — 将剧情设计转化为 Unreal 的 C++ 类和 Blueprint 图。GAS 技能系统、Gameplay Tags 状态管理、网络复制。触发词：Unreal脚本、Unreal场景、unreal scripting、Blueprint、C++ Unreal。
user-invocable: true
---

# Unreal Engine 脚本编写

> 吸收自 CC Studio unreal-specialist + 4 子专家（GAS/Blueprint/Replication/UMG）+ godogen 架构分离模式。

将 Phase 1 产出的 `story-design.md` 转化为 Unreal 的 C++ 类和 Blueprint 图。

> 前置条件：Phase 1 story-design.md 完成，Phase 2 素材清单可用。
>
> 协作关系：加载时已知 `game-story-design` + `game-asset-pipeline`，在 kit 编排器路由下执行。

## 核心铁律

```
1. C++: UPROPERTY/UFUNCTION/UCLASS/USTRUCT 宏正确使用
2. TObjectPtr<> 替代裸 UObject 指针（UE5.1+）
3. Blueprint 图形 > 20 节点 → 转为 C++
4. Data Assets / Data Tables → 数据驱动（非硬编码）
5. Network: Server Authoritative + Client Prediction
6. 文件扩展: .uproject / .uplugin / .Build.cs / .Target.cs
```

## 项目骨架

```
project/
├── Game.uproject
├── Source/
│   └── Game/
│       ├── Game.Build.cs
│       ├── Game.h / Game.cpp
│       ├── Characters/
│       ├── Systems/
│       └── UI/
├── Content/
│   ├── Characters/       # Blueprint + 素材
│   ├── Maps/             # 关卡文件 (.umap)
│   ├── UI/               # UMG Widgets
│   ├── Audio/
│   └── Data/             # Data Tables / Data Assets
├── Config/
└── Plugins/
```

## 从 story-design.md 到 Unreal 的映射

| story-design.md 元素 | Unreal 对应 |
|----------------------|-----------|
| 角色宪法 → 角色属性 | DataAsset (UPrimaryDataAsset) |
| 剧情树 → 分支逻辑 | Blueprint 节点图 + Gameplay Tags |
| 场景列表 → 关卡 | Level (.umap) + Level Streaming |
| 对话文本 → 演出 | UMG RichTextBlock + Dialogue Component |
| 立绘切换 → 表达式 | UPaperSprite (2D) 或 SkeletalMesh (3D) |
| BGM/SFX → 音频 | AudioComponent + SoundCue |

## 核心模式索引

| 模式 | 文件 |
|------|------|
| 角色数据资产（UPrimaryDataAsset） | `references/unreal-patterns.md §1` |
| Gameplay Tags 状态标识 | `references/unreal-patterns.md §2` |
| 对话系统（Dialogue Component） | `references/unreal-patterns.md §3` |
| GAS 技能系统（GameplayAbility） | `references/unreal-patterns.md §4` |
| 网络复制（Replicated + RPC） | `references/unreal-patterns.md §5` |
| Blueprint ↔ C++ 决策 | `references/unreal-patterns.md §6` |

## Blueprint 使用原则

```
✅ 适合 Blueprint:
  - 数据变体（Data-only Blueprint）
  - 事件响应链（OnClick → 一系列视觉反馈）
  - 时间线动画（Timeline nodes）
  - 设计师调试（蓝图断点）

❌ 应转为 C++:
  - 图形 > 20 节点
  - 数学密集计算
  - 网络复制逻辑
  - Tick 中的重逻辑
```

## 性能约束

- `SCOPE_CYCLE_COUNTER` profiling 关键路径
- 对象池：Characters/Projectiles 频繁创建
- Level Streaming：大地图异步加载
- Nanite + Lumen：高画质但不适合移动端
- Animation Budget Allocator：大量角色时限制更新频率
- Distance Culling：远处角色降低更新频率

## 开发环境

- Unreal Engine 5.5+
- Visual Studio 2022 (C++ 编译)
- Rider (可选，C++ 编辑)
- `.uproject` 右键 → Generate Visual Studio project files

## 详细参考

- 完整 C++ 模式代码模板（DataAsset/GAS/网络复制）→ `references/unreal-patterns.md`
- GAS 系统深入 → `references/gas-guide.md`
- Blueprint 最佳实践 → `references/blueprint-guide.md`
- 网络复制 → `references/replication-guide.md`
