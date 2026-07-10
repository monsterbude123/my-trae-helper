---
name: unity-scripting
description: Unity 引擎脚本编写 — 将剧情设计转化为 Unity 场景和 C# 脚本。ScriptableObjects 数据驱动、Addressables 资产管理、Input System 新输入。触发词：Unity脚本、Unity场景、unity scripting、C# Unity。
user-invocable: true
---

# Unity 引擎脚本编写

> 吸收自 CC Studio unity-specialist + 4 子专家（DOTS/Shader/Addressables/UI）+ godogen bevy/babylon 架构分离模式。

将 Phase 1 产出的 `story-design.md` 转化为 Unity 可运行的场景和 C# 脚本。

> 前置条件：Phase 1 story-design.md 完成，Phase 2 素材清单可用。
>
> 协作关系：加载时已知 `game-story-design` + `game-asset-pipeline`，在 kit 编排器路由下执行。

## 核心铁律

```
1. C#: 禁止 Find/FindObjectOfType/SendMessage — 用引用或 DI
2. Awake() 中缓存组件引用，不在 Update() 中查找
3. [SerializeField] private 替代 public 字段
4. ScriptableObjects 做数据驱动（角色属性/对话数据）
5. asmdef 控制编译单元，减少编译时间
6. Addressables 替代 Resources.Load — 异步加载
7. 新 Input System (.inputactions) 替代旧 Input Manager
```

## 项目骨架

```
project/
├── Assets/
│   ├── _Project/
│   │   ├── Scenes/
│   │   ├── Scripts/                # Core / Characters / UI
│   │   ├── ScriptableObjects/      # 数据资源
│   │   ├── Prefabs/
│   │   ├── AddressableAssets/      # Addressables 资产
│   │   └── Input/                  # .inputactions
│   └── Settings/                   # URP/HDRP 配置
├── Packages/
└── ProjectSettings/
```

## 从 story-design.md 到 Unity 的映射

| story-design.md 元素 | Unity 对应 |
|----------------------|-----------|
| 角色宪法 → 角色属性 | ScriptableObject (CharacterData) |
| 剧情树 → 分支逻辑 | `UnityEvent` + State Machine |
| 场景列表 → 位置/背景 | Scene 文件 + `SceneManager.LoadSceneAsync()` |
| 对话文本 → 演出 | `DialogueSystem` + TextMeshPro |
| 立绘切换 → 表达式 | SpriteRenderer 纹理替换 + Animation |
| BGM/SFX → 音频 | AudioSource + AudioMixer |

## 核心脚本模式索引

| 模式 | 文件 |
|------|------|
| 角色数据 ScriptableObject | `references/unity-patterns.md §1` |
| 对话系统（UniTask 异步） | `references/unity-patterns.md §2` |
| 新 Input System | `references/unity-patterns.md §3` |
| Addressables 加载 | `references/unity-patterns.md §4` |

## Unity 版本策略

> 参照 CC Studio engine-programmer 知识缺口分析。

| Unity 版本 | API 稳定性 | 推荐场景 |
|-----------|-----------|---------|
| Unity 6 LTS | 长期支持 | 生产项目 |
| Unity 6000.x | 最新特性 | 体验新功能 |

**版本安全**: LLM 训练截止 2025.05，Unity 6+ API 可能不准确。使用前以 `[MAY BE OUTDATED]` 标记，提示用户验证。

## 性能约束

- `StringBuilder` 替代循环字符串拼接
- `ObjectPool<T>` — 频繁创建/销毁的对象
- Canvas Groups — UI 显隐管理（非 SetActive）
- `await UniTask` 替代协程（UniTask 库）
- 避免 `Update()` 轮询，用事件/coroutine 驱动
- Sprite Atlases (2D) / Texture Arrays (3D) 合批

## 开发环境

- Unity 6000.x+ (或 Unity 6 LTS)
- Visual Studio / Rider (C# 编辑)
- asmdef 管理：Core → Characters → UI（分层编译）

## 详细参考

- Addressables 使用指南 → `references/addressables-guide.md`
- Input System 配置 → `references/input-system-guide.md`
- UI Toolkit (运行时 UI) → `references/ui-toolkit-guide.md`
- 完整脚本模式代码模板 → `references/unity-patterns.md`
