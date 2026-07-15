# 场景 2: 引擎切换 — WebGAL → Godot（加交互玩法）

> **模拟**: Phase 1 故事设计完成后，用户想加入咖啡制作小游戏。WebGAL 无法支持交互玩法，切换到 Godot。Phase 1 产出保留，Phase 2-3 重做。

---

## 用户视角

```
用户: "刚才的《咖啡馆的猫》做完故事设计了，但我想加一个简单的咖啡制作小游戏
      （点击拖拽配料，做出不同咖啡），WebGAL 能做吗？"

Agent: WebGAL 是纯叙事引擎，不支持交互小游戏（点击拖拽、物品组合）。
      跨引擎对比:
        WebGAL — VN 纯叙事 ✅ 交互玩法 ❌
        Godot  — VN Dialogic 插件 + GDScript 交互 ✅

      切换影响评估:
        保留: Phase 1 story-design.md（角色宪法/剧情树/场景列表）
        重做: Phase 2 Asset（格式路径变更） + Phase 3 Scripting（GDScript 替代 .txt）
        不变: Phase 4 Quality Gate / Phase 5 Build（路由自动切换）

用户: "好，切换到 Godot"

Agent: Post-Phase 1 引擎切换 → cockpit 更新 engine=godot
      → 追加变更日志: "引擎 WebGAL→Godot | 影响: Phase 2 素材格式 + Phase 3 脚本全部"

Phase 2 Asset Pipeline（重做）:
  → 加载 game-asset-pipeline
  → 素材兼容: WebGAL PNG/OGG → Godot 可直接复用，仅路径变更
    character_elise_01.png: webgal figure/ → godot assets/characters/
    bg_cafe_morning.png:    webgal background/ → godot assets/backgrounds/
    bgm_main_theme.ogg:     webgal bgm/ → godot assets/audio/bgm/
  → 重新生成 asset-manifest.md（Godot 路径格式）

Phase 3 Scripting（重做）:
  → 加载 godot-scripting
  → VN 部分: 用 Dialogic 插件实现剧情播放
  → 小游戏部分: 新建 coffee_minigame.tscn + coffee_game.gd
    - 拖拽配料到杯子 → signals 触发配方判定
    - 3 种咖啡配方（美式/拿铁/摩卡）→ 影响角色好感度 flag
  → gdlint + gdformat 通过
  → 产出 scene-manifest.json + proof-screenshots/(5张: 含小游戏截图)

Phase 4-7: 后续阶段按 Godot 路由走，与 WebGAL 流程一致
```

---

## 系统内部流程

```
Phase 1 完成后
  │
  ├── 用户: "想加交互玩法"
  │
  ├── 引擎能力判定
  │     ├── WebGAL: 纯叙事引擎 → 交互 ❌
  │     └── 引擎决策指南: VN+轻度gameplay → Godot Dialogic
  │
  ├── [决策] 切换到 Godot
  │     ├── 时机判定: Phase 1 完成后 → ✅ 允许切换（Phase 3 之前）
  │     ├── Phase 1 产出保留: story-design.md（v1） 不变
  │     └── cockpit 变更:
  │           engine: webgal → godot
  │           变更日志追加引擎切换事件
  │           Phase 2 状态: ✅ → 🔄（需重做）
  │
  ├── Phase 2 素材重做
  │     ├── 素材兼容检查: PNG/OGG → Godot 直接复用
  │     ├── 仅变更: 目录结构 + asset-manifest.md 路径
  │     └── 无需重新生成（素材内容不变）
  │
  ├── Phase 3 脚本重做
  │     ├── 路由: webgal-scripting → godot-scripting
  │     ├── VN 部分: Dialogic timeline + 对话系统
  │     └── 小游戏: GDScript 交互逻辑
  │
  └── Phase 4-7: Godot 路由
        ├── game-quality-gate → 自动化检查（跨引擎契约）
        ├── godot-engine-build → headless + --export-release
        └── deploy → itch.io / GitHub Releases
```

---

## 关键决策点

| 决策点 | 判断条件 | 结果 |
|--------|---------|------|
| 切换准入 | Phase 3 之前可切，Phase 3 之后需评估 | Phase 1 后 → 准入 ✅ |
| 哪些产出保留 | Phase 1 engine-agnostic | story-design.md 保留 |
| 哪些产出重做 | Phase 2-3 engine-specific | asset-manifest 重写 + 脚本重写 |
| 素材兼容性 | PNG/OGG 通用格式 | 直接复用，仅路径变更 |
| 质量门禁 | 跨引擎统一契约 | scene-manifest.json 格式不变 |

---

## 发现的问题

1. **引擎切换的 cockpit 回退状态缺少显式协议**: cockpit.md 定义了"方向调整（Pivot）协议"，提到"引擎换型 → 更新状态卡引擎字段，Phase 3 从头开始"，但没说 Phase 2 的状态标记应该怎么处理。本场景中 Phase 2 素材需要重新走（路径变更），但 SKILL.md 和 cockpit.md 都没明确说 Phase 2 是否要重做、已生成的素材文件是否保留。

2. **cross-engine-contract.md 的 asset-references.json 没有引擎字段**: scene-manifest.json 有 `"engine"` 字段，但 asset-references.json 没有。引擎切换后素材路径会变化，如果 asset-references.json 不标引擎，Phase 4 门禁在交叉比对时可能找不到正确的路径格式基准。

3. **godot-scripting 没有引用 cross-engine-contract.md**: godot-scripting/SKILL.md 列出了产出要求，但没有明确引用 cross-engine-contract.md 中的统一产出契约（scene-manifest.json + asset-references.json + branch-coverage.txt + proof-screenshots/）。各引擎脚本技能应统一引用此契约以保证产出格式一致。
