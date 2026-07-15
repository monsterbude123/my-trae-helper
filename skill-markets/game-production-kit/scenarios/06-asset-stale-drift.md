# 场景 6: 素材漂移：Story 更新后素材标记 stale

> 模拟目标: 验证 sync_version_tracking.py 版本对比 + gate-standards 影响范围匹配 + Phase 2 增量重生成协议。

---

## 用户视角

```
[背景: Phase 1-2 ✅]
story-design.md v3 — 角色: Elise, Lin, Boss (3人)
asset-manifest.md   — 12 素材，source_version 均为 v3

用户: "我想加一个新角色 Lisa，她是咖啡馆的熟客"

Agent: 🎭 game-story-design（增量更新）
       → Lisa 宪法追加: 28 岁自由插画师，Want=安静角落，Fear=被赶走
       → 变更日志: | v4 | 新增角色 Lisa | 立绘: lisa_*.png, TTS: lisa_*.wav |
       → story-design.md v3 → v4

[Cockpit 自检]
Agent: ⚠️ 素材漂移检测中...

       sync_version_tracking.py 原始输出:
       | character_elise_01.png | v3→v4 | 立绘: elise |
       | character_lin_01.png   | v3→v4 | 立绘: lin   |
       | character_boss_01.png  | v3→v4 | 立绘: boss  |
       | bg_cafe_01.png         | v3→v4 | 背景: cafe |

       Gate 版本一致性检查 (gate-standards §版本一致性检查):
       变更日志 v4 影响: "立绘: lisa_*.png, TTS: lisa_*.wav"
       逐项: elise≠lisa → APPROVE | lin≠lisa → APPROVE | boss≠lisa → APPROVE
       ✅ 已有素材无需重生成（变更仅影响 Lisa）

       缺口检测 (story-design 角色 vs asset-manifest):
       角色: Elise, Lin, Boss, Lisa → 立绘: elise, lin, boss → 缺失: lisa

Agent: 🔄 建议回退 Phase 2，为 Lisa 增成素材（已有素材不动）
       .project-cockpit.md: phase=2→2, status=🔄素材漂移

用户: "好，生成 Lisa 的素材"

Agent: [Phase 2 增量重跑]
       → 生成: character_lisa_01.png (v4) + voice_lisa_*.wav (v4)
       → asset-manifest.md 追加 Lisa entries
       → sync_version_tracking.py → ✅ 全部匹配 v4
       .project-cockpit.md: phase=2, status=✅
```

---

## 系统内部流程

```
Phase 1 增量更新 → story-design.md v3→v4（新增 Lisa）

Cockpit 自检
  ├── Step A: sync_version_tracking.py
  │     → 全部 v3 < v4 → 4 ⚠️ stale（不做影响匹配，全部标记）
  │
  ├── Step B: Gate 版本一致性检查
  │     → 变更 v4 影响范围: "lisa_*.png, lisa_*.wav"
  │     → 逐项匹配: elise/lin/boss/cafe ≠ lisa → 全部 APPROVE
  │
  ├── Step C: 缺口检测（ad-hoc）
  │     → story-design 角色 vs asset-manifest 前缀 → 差集: lisa
  │
  └── Step D: 决策 → 已有不动，缺失增量生成

Phase 2 增量重跑
  ├── 已有 12 素材 → 跳过
  ├── 新生成 Lisa 立绘 + TTS (source: v4)
  └── asset-manifest.md 追加 → 验证通过
```

---

## 关键决策点

### 1. sync_version_tracking.py 的局限
- ✅ 做版本号对比: source_version < 当前版本 → ⚠️ stale
- ❌ 不做影响范围匹配（全部标 stale，由 gate 过滤）
- ❌ 不做缺口检测（不发现"新角色缺素材"）
- 工作分工: 脚本 = 数据采集，gate = 判定过滤，cockpit = 缺口检测

### 2. 增量 vs 全量重生成
- 增量: 变更影响 ≤ 30% 已有素材（如新增角色）→ ✅ 本场景
- 全量: 变更影响 > 30%（如美术风格切换）
- 判断依据: 变更日志的 `影响范围` 字段精确匹配

### 3. 不自动回退 Phase 2
```
原则: 始终询问用户。原因:
  - 素材生成耗时（ComfyUI 30s-2min/张）
  - 用户可能先写脚本再补素材
  - 用户可能想手动选择哪些重新生成
```

---

## 发现的问题

### [ISSUE-06-01] sync_version_tracking.py 缺少"缺口检测"
- **描述**: 只做版本对比，不检测 story-design 新增需求在 asset-manifest 中无条目。场景中缺口检测是 cockpit ad-hoc 补做的。
- **建议**: 增加 `--gap-check` 模式，对比角色/场景列表 vs manifest 条目。

### [ISSUE-06-02] Gate 影响匹配依赖变更日志格式一致性
- **描述**: 影响范围匹配依赖 `{类别}: {pattern}` 格式（如 `立绘: lisa_*.png`）。格式不规范则匹配失败，已有素材被误标 CONCERNS。
- **建议**: game-story-design 变更日志模板强制结构化格式 + 校验正则。

### [ISSUE-06-03] 缺口检测无标准化实现
- **描述**: Lisa 缺口检测是 cockpit ad-hoc 逻辑，无独立脚本/规范，各 Agent 实现可能不同。
- **建议**: 整合到 sync_version_tracking.py `--gap-check` 或 check_assets.py。

### [ISSUE-06-04] 回退时 Phase 序号不变导致进度条模糊
- **描述**: `phase=2, status=🔄` 看不出是首次还是多次回退。多次 2→1→2→2→3 循环时进度条失效。
- **建议**: 增加 `retry_count` 字段或 `✅→🔄(r2)` 标记。
