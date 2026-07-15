# 游戏逻辑测试维度

> 来源：CC Studio director-gate + godogen test-harness 经验
> 关联：game-quality-gate SKILL.md §自动化检查项（补充） / gate-standards.md §6 跨引擎差异

> 背景：素材属性检查（12 项）覆盖视觉/音频素材质量，但**不覆盖游戏逻辑正确性**。
> 以下 6 个维度补齐剧情/状态/交互/性能/存档/资源完整性覆盖。

## §1 分支完整性

| 项 | 说明 |
|----|------|
| 检查目标 | 剧情树所有分支可达，无死路径，无孤立节点 |
| 检查方法 | 解析 `story-design.md` 中剧情树定义 → 拓扑排序 → BFS 可达性分析 |
| 通过标准 | 可达节点数 = 总节点数；每个 END 节点至少 1 条路径可达 |
| 失败影响 | 玩家卡关 / 剧情断裂 / 测试覆盖率盲区 |

```
# WebGAL: 解析 scene/*.txt 的 choose 分支
# Godot:  解析 .tres/.gd 的 DialogueResource 跳转
# Unity:  解析 YarnSpinner .yarn 或 Ink .ink 的 divert
```

## §2 状态机正确性

| 项 | 说明 |
|----|------|
| 检查目标 | 存档状态 vs 新游戏状态的关键 flag 比对，读档后正确恢复 |
| 检查方法 | 新游戏 → 推进到关键 flag 点 → 存档 → 读档 → 比对 flag 快照 |
| 通过标准 | 所有关键 flag 读档后值与存档前一致；不存在未定义 flag 污染 |
| 失败影响 | 读档后剧情错乱 / NPC 消失 / 物品丢失 |

关键 flag 示例：`affection_level`, `route_flag`, `item_inventory[]`, `scene_cleared[]`

## §3 UI 交互序列

| 项 | 说明 |
|----|------|
| 检查目标 | 对话选项 → 分支跳转 → 场景切换 的 E2E 序列正确 |
| 检查方法 | 按引擎选择验证方式（见下表） |
| 通过标准 | 每个选项产生的分支跳转与 story-design.md 一致；场景切换无崩溃 |
| 失败影响 | 选项无响应 / 跳转错误分支 / 场景切换黑屏 |

| 引擎 | 验证方法 | 实现 |
|------|---------|------|
| WebGAL | 解析 scene 文件 → 提取 `choose` → 比对 `targetScene` | `scripts/verify_webgal_flow.py` |
| Godot | `--headless` test-harness → 模拟点击 → 断言场景路径 | `res://tests/gate_ui_flow.gd` |
| Unity | EditMode TestRunner → 模拟选项选择 → 断言 SceneManager 状态 | `[UnityTest] IEnumerator` |
| Unreal | Automation Spec → 模拟输入 → 断言 Level 切换 | `.spec.cpp` |
| Bevy | `cargo test` → `App::new()` 注入测试 state → 断言 `NextState` | `#[test] fn gate_ui_flow()` |

## §4 性能基线

| 项 | 说明 |
|----|------|
| 检查目标 | 帧率 / 冷启动 / 内存在各引擎目标范围内 |
| 检查方法 | 引擎内置 profiler + 脚本采样（见下表） |
| 通过标准 | FPS ≥ 目标帧率 95% 帧达标 / 冷启动 ≤ 目标值 / 内存 ≤ 目标值 |

| 引擎 | 帧率目标 | 冷启动目标 | 内存目标 | 测量方式 |
|------|---------|----------|---------|---------|
| WebGAL | 60 FPS | ≤ 3s | ≤ 256 MB | Chrome DevTools Performance |
| Godot | 60 FPS | ≤ 2s | ≤ 512 MB | `--headless` + `Performance.get_monitor()` |
| Unity | 60 FPS | ≤ 3s | ≤ 512 MB | ProfilerRecorder API |
| Unreal | 60 FPS | ≤ 5s | ≤ 1 GB | `stat fps` / `stat memory` |
| Bevy | 60 FPS | ≤ 1s | ≤ 256 MB | `bevy::diagnostic::FrameTimeDiagnosticsPlugin` |
| Babylon | 60 FPS | ≤ 3s | ≤ 256 MB | `engine.getCaps()` + `performance.now()` |

> 失败影响：低于 30 FPS → REJECT；30~目标帧率 → CONCERNS。

## §5 存档兼容性

| 项 | 说明 |
|----|------|
| 检查目标 | 旧版本存档在新版本中可读 + 反序列化不崩溃 + 缺失字段用默认值 |
| 检查方法 | 保留 N-1 版本存档文件 → 新版本加载 → 断言无 crash + key fields 非 null |
| 通过标准 | `load("save_v1.json")` 不抛异常；所有关键字段可访问；缺失字段回填默认值 |
| 失败影响 | 玩家存档损坏 / 版本更新丢失进度 |

```
# 各引擎存档格式：
# WebGAL:  JSON (globalData + sceneData)
# Godot:   .save (ConfigFile) 或自定义 JSON
# Unity:   PlayerPrefs / BinaryFormatter / JSON
# Bevy:    save.ron (RON format) 或 JSON
```

存档版本号规范：每次修改存档结构 → `save_version` +1，旧版本兼容逻辑独立模块。

## §6 资源完整性

| 项 | 说明 |
|----|------|
| 检查目标 | asset-manifest.md 引用计数 vs 实际加载，无悬垂引用 / 无 404 |
| 检查方法 | 解析 asset-manifest.md → 扫描代码中所有资源引用 → 交叉比对 |
| 通过标准 | manifest 中每条资源在代码中有 ≥1 引用；代码中每条资源路径在 manifest 中存在 / 文件实际存在 |
| 失败影响 | 运行时崩溃 / 占位纹理 / 静默缺失音频 |

| 引用类型 | 扫描目标 | 工具 |
|---------|---------|------|
| 纹理/立绘/背景 | 代码中 `show` / `Texture2D` / `Sprite` / `Image` 路径 | grep pattern 按引擎 |
| 音频 | `playBgm` / `AudioStreamPlayer` / `AudioClip` 路径 | grep pattern 按引擎 |
| 字体 | `font` / `FontFile` / `DynamicFontData` 路径 | grep pattern 按引擎 |

> engine-agnostic 兜底：`scripts/check_asset_refs.py --manifest asset-manifest.md --scan-dir src/`
