# 引擎决策指南

> Phase 0 引擎确认阶段的决策参考。参照 CC Studio setup-engine 决策矩阵。

## 决策原则

```
游戏需求 → 匹配引擎特征 → 推荐 → 用户确认
```

不根据单一维度（如"流行度"）推荐，而是综合**游戏类型、2D/3D、目标平台、技术栈、团队规模**五个维度匹配。

## 引擎决策矩阵

> 参照 CC Studio 20+ 决策点矩阵。每个引擎包含 honest tradeoffs。

### 视觉小说（VN / Visual Novel）

| 引擎 | 维度 | 状态 |
|------|------|------|
| **WebGAL** | Web 发布、零代码 DSL、中文原生支持 | ✅ 已集成 |
| **Ren'Py** | 桌面/移动端、Python 生态、最大社区 | ⏳ 待建 |
| **Godot (Dialogic)** | 自定义 UI、混合 gameplay、开源 | ⏳ 待建 |

**推荐逻辑**: 
- 纯粹 VN + Web 发布 → WebGAL
- 纯粹 VN + 桌面/移动端 → Ren'Py
- VN + 轻度 gameplay（探索/解谜）→ Godot Dialogic

### 2D 游戏

| 引擎 | 维度 | 状态 |
|------|------|------|
| **Godot** | GDScript/C#、开源、2D 专用引擎层 | 🔗 外部 (godogen) |
| **Unity** | C#、2D 工具链成熟、最大生态 | 🔗 外部 |

### 3D 游戏

| 引擎 | 维度 | 状态 |
|------|------|------|
| **Godot 4** | 开源 3D、轻量、Jolt Physics | 🔗 外部 (godogen) |
| **Unity** | 通用 3D、资产商店丰富 | 🔗 外部 |
| **Unreal** | 高画质 3A、蓝图系统、C++ | 🔗 外部 |

### 浏览器游戏

| 引擎 | 维度 | 状态 |
|------|------|------|
| **Babylon.js** | TypeScript、Vite、WebGL2、Playwright 截图 | 🔗 外部 (godogen) |

## 引导对话脚本

> 参照 CC Studio Path C "I know the game but not the engine" + godogen publish.sh --engine。

```text
Q1: 游戏类型？
    A) 视觉小说/Galgame/VN — 推荐 WebGAL（Web）或 Ren'Py（桌面）
    B) 2D 横版/平台/弹幕/解谜 — 推荐 Godot
    C) 3D 动作/射击/开放世界 — 推荐 Unity 或 Unreal
    D) 网页小游戏/H5 — 推荐 WebGAL 或 Babylon.js
    E) 其他 → 用户描述

Q2: 2D 还是 3D？
    A) 2D — 缩小范围到 Godot / Unity / WebGAL
    B) 3D — 缩小范围到 Godot 4 / Unity / Unreal / Babylon.js
    C) 都行 — 按游戏类型推荐

Q3: 目标平台？
    A) Web 浏览器 — WebGAL / Babylon.js
    B) Windows/Mac/Linux 桌面 — Ren'Py / Godot / Unity
    C) iOS/Android 移动端 — Godot / Unity / Ren'Py
    D) 全平台 — Godot / Unity

Q4: 技术偏好？
    A) 零代码 / DSL 脚本 — WebGAL / Ren'Py (Ren'Py Script)
    B) GDScript — Godot
    C) C# — Godot (.NET) / Unity
    D) Python — Ren'Py
    E) Rust — Bevy
    F) TypeScript — Babylon.js
    G) 不关心 → 推荐最适合游戏类型的引擎

→ 综合四个回答推荐一个引擎，给用户最终确认
```

## 知识缺口分析

> 参照 CC Studio engine-programmer 版本安全机制。LLM 训练截止 2025 年 5 月。

| 风险级别 | 说明 | 处理 |
|---------|------|------|
| **LOW** | API 在 cutoff 前已稳定 ≥1 年 | 正常使用 |
| **MEDIUM** | API 在 cutoff 附近发布/变更 | 使用前显式告知用户可能过时 |
| **HIGH** | API 在 cutoff 后发布 | 必须查最新文档后使用 |

**引擎文档查找策略**:
- Godot: 先读 `docs/engine-reference/godot/VERSION.md` → 检查 deprecated-apis.md 和 breaking-changes.md
- WebGAL: 运行 `npm view webgal-parser versions` → 检查最新版 CHANGELOG
- 外部引擎: 提示用户提供引擎版本，标记未知 API 为 MEDIUM 风险

## File Extension Routing

> 参照 CC Studio 三引擎文件扩展路由表。引擎特定文件不混用。

| 引擎 | 场景文件 | 脚本文件 | 素材路径 | 构建产物 |
|------|---------|---------|---------|---------|
| WebGAL | `.txt` (DSL) | `.txt` | `public/game/{type}/` | `dist/` |
| Godot | `.tscn` | `.gd` / `.cs` | `res://assets/` | `build/` |
| Ren'Py | `.rpy` | `.rpy` | `game/images/` | `dist/` |
| Unity | `.unity` / `.prefab` | `.cs` | `Assets/` | `Builds/` |
| Unreal | `.umap` | `.cpp` / Blueprint | `Content/` | `Build/` |

## 默认策略

如果用户拒绝选择（"随便""你推荐""不想选"）：
- VN 类型 → 默认 **WebGAL**（Web 零部署，最轻量）
- 非 VN → 告知"需要选定引擎才能继续"，不替用户决定

## 引擎×功能列式对比

| 功能 | WebGAL | Godot | Unity | Unreal | Bevy | Babylon |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| 视觉小说/对话系统 | ⭐ | ✅ | ✅ | ✅ | ❌ | ❌ |
| 2D 精灵/像素 | ❌ | ⭐ | ✅ | ✅ | ⭐ | ❌ |
| 3D 渲染 | ❌ | ✅ | ⭐ | ⭐ | ❌ | ⭐ |
| 回合制战斗 | ❌ | ⭐ | ⭐ | ✅ | ⭐ | ✅ |
| 模拟经营 | ❌ | ⭐ | ⭐ | ⭐ | ✅ | ✅ |
| 物理引擎 | ❌ | ✅ | ✅ | ⭐ | ✅ | ✅ |
| 多人联机 | ❌ | ✅ | ⭐ | ⭐ | ❌ | ✅ |
| 发布平台 | Web | 桌面+移动+Web | 桌面+移动+主机+Web ⭐ | 桌面+主机 | 桌面+Web | Web |
| 移动端 | ❌ | ✅ | ⭐ | ✅ | ❌ | ✅ |
| 学习曲线 | 低 | 中 | 高 | 高 | 高 | 中 |

⭐ = 最佳 / ✅ = 支持 / ❌ = 不适用
