# 发布后生命周期

> 触发: 项目 Phase 6 部署完成后的任何变更请求

## 场景 1: 内容更新（Content Update）

### 识别
用户意图包含 "更新内容" / "新章节" / "加角色" / "改对话" / "加结局"

### 路径
```
当前项目 → 维持引擎不变 → 从 Phase 1 增量开始
  ├── story-design.md 追加新章节/角色
  ├── Phase 2: 新素材生成
  ├── Phase 3: 新脚本编写
  ├── Phase 4: 重新跑门禁（增量 + solo 模式）
  ├── Phase 5: 重新构建
  └── Phase 6: 更新部署
```

### game_key 策略
复用原 game_key。版本号递增（v1.0 → v1.1）。
---

## 场景 2: 引擎升级（Engine Upgrade）

### 识别
用户意图包含 "升级引擎" / "Godot 4.3→4.4" / "换 Unity 版本"

### 验证清单
```
[ ] 更新 VERSION.md (引擎版本号)
[ ] 更新 cross-engine-contract asset-references engine_version 字段
[ ] 重新导入素材 (godot --headless --import)
[ ] 重跑 lint (gdlint/format → 对应引擎工具)
[ ] 重跑 Phase 4 质量门禁:
    [ ] 自动化检查项全量
    [ ] 性能基线重测（02-game-logic-checks.md §性能）
    [ ] 存档兼容性测试（test_save_compat.py）
    [ ] Proof bundle 新旧对比截图
[ ] Phase 5 重新构建
[ ] 烟雾测试（启动→核心循环→存档循环）
```

### game_key 策略
复用原 game_key。引擎版本号更新。
---
## 场景 3: 跨平台移植（Cross-Platform Port）

### 识别
用户意图包含 "移植到" / "上移动端" / "Switch 版" / "iOS" / "Android"

### 第一步: 可行性评估
```
当前引擎的发布平台支持:
  → 目标平台已支持 → 走「最小移植」路径
  → 目标平台不支持 → 🛑 展示选项:
      A) WebView 套壳（最小改动，性能可能下降）
      B) 引擎迁移→支持目标平台的引擎（重做 40-60%）
```

### 路径 A: WebView 套壳 (引擎不变)
```
├── 配置 WebView 容器 (react-native-webview / android-webview)
├── Phase 5: 调整构建配置
├── Phase 6: 更换部署目标 (App Store / Google Play)
└── Phase 4: 移动端性能基线 + 触控适配
```

### 路径 B: 引擎迁移
```
├── 新建 game_key: {原name}_{target_platform} (如 star_cafe_mobile)
├── 复用: Phase 1 story-design.md + Phase 2 通用素材(PNG/OGG)
├── 重做: Phase 3 脚本 → 目标引擎语法
├── 重做: Phase 5 构建 → 目标引擎导出
├── 重做: Phase 6 部署 → 新平台
└── 标注: project-cockpit 中 parent_project: {原game_key}
```

### game_key 策略
- 路径 A: 复用原 game_key
- 路径 B: 新建 game_key，标注 parent_project
---

## 场景 4: A/B 测试内容

### 识别
用户意图包含 "A/B" / "测试两个版本" / "对比"

### 内容管理
有 A/B 变体的场景用目录结构（单文件场景保持不变）:
```
{game_key}/scenes/
├── scene_01/
│   ├── variant_a.txt
│   ├── variant_b.txt
│   └── variant_config.json     # {"variants":["a","b"],"split_ratio":[50,50],"metric":"d2_retention","min_sample":200,"confidence":0.95,"max_days":14}
└── scene_02.txt
```

### asset-manifest 多版本标记
```yaml
assets/scene_01/bg_spaceship_crash.png:
  variant: "b"
  variant_parent: "scene_01"
```

### 分析闭环
- Phase 7 Operations 03-analytics.md §4 A/B 测试框架负责统计分析
- 结论: 置信度 ≥ 95% → 选优胜版本 → 删失败变体 → 更新 manifest
