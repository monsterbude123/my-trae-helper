# 跨引擎统一产出契约

> 来源：审计缺口 H1 + godogen 多引擎 capture 经验
> 关联：SKILL.md §1 相位门禁链 Phase 3

定义 Phase 3（脚本编写）完成后，所有引擎必须产出的通用产物。门禁不依赖引擎自我报告，而是机械检查这些产物是否存在。

## 通用产出物（6 引擎统一，Phase 4 门禁可检查）

| 产物 | 格式 | 检查方式 | 含义 |
|------|------|---------|------|
| scene-manifest.json | JSON | 文件存在 + JSON 可解析 | 场景列表（含对白/素材/分支） |
| asset-references.json | JSON | 文件存在 + 路径交叉比对 | 每个素材的引用次数和位置 |
| branch-coverage.txt | 纯文本 | 文件存在 + > 0 行 | 剧情分支已实现/未实现 |
| proof-screenshots/ | 目录 | 至少 3 张截图 | 关键场景视觉验证 |

## scene-manifest.json 通用格式

```json
{
  "engine": "godot|unity|unreal|bevy|babylon|webgal",
  "scenes": [
    {
      "id": "scene_01_intro",
      "source": "story-design.md §场景列表 #1",
      "dialogue_count": 12,
      "skipped_dialogues": 0,
      "assets_used": ["bg_library", "character_elise_01"],
      "branches": ["flag_courage > 0 → scene_02a", "else → scene_02b"],
      "voice_files": [],
      "skipped_voices": []
    }
  ],
  "branch_coverage": "8/10 implemented"
}
```
<!-- Phase 4 交叉验证: voice_files.length + skipped_voices.length == dialogue_count -->

## asset-references.json 通用格式

交叉验证素材引用完整性：

```json
{
  "engine": "godot|unity|unreal|bevy|babylon|webgal",
  "engine_version": "4.3",
  "assets": {
    "bg_library.png": {"used_in": ["scene_01_intro", "scene_03_clue"]},
    "character_elise_01.png": {"used_in": ["scene_01_intro", "scene_02a_confront"]}
  },
  "unreferenced": [],
  "missing": []
}
```

- `unreferenced` — 在磁盘但未被引用 → 警告
- `missing` — 被引用但磁盘不存在 → 阻断

## 门禁整合

Phase 4 game-quality-gate 加载本契约：

| 检查 | 条件 | 失败 verdict |
|------|------|-------------|
| scene-manifest.json 缺失 | 文件不存在 | REJECT |
| asset-references.json 缺失 | 文件不存在 | REJECT |
| asset-references.json missing 非空 | missing 数组 > 0 | REJECT |
| branch-coverage 不足 | 覆盖数 < story-design 分支数 | REJECT |
| proof-screenshots 不足 | < 3 张 | CONCERNS |

## 详细参考

- Phase 3 引擎脚本技能：`skills/*-scripting/SKILL.md`
- Phase 4 质量门禁：`skills/game-quality-gate/SKILL.md`
- 门禁标准：`references/gate-standards.md`

> 本契约被以下文件引用：SKILL.md §1 门禁链 Phase 3 / game-quality-gate SKILL.md §自动化检查项（已追加）

## 存档兼容测试唯一入口

- 测试文件: {game_key}/tests/test_save_compat.py ← 所有 phase 共用
- Phase 4 调用: 基础兼容（v{N} 存档 → v{N+1} 加载 + 核心字段不变）
- Phase 7 追加: 运营扩展兼容（道具/赛季/成就字段无覆盖）
- 原则: 一份测试文件，多 phase 追加 case

## asset-manifest 条目字段规范

| 字段 | AI 生成素材 | 外部导入素材 |
|------|:---:|:---:|
| source | "story-design" | "external" |
| source_version | ✅ 必填 | ❌ 不填 |
| source_detail | ❌ | ✅ 来源 + 许可 |
| generated_at | ✅ | ❌ |
| imported_at | ❌ | ✅ |
| status | pending/generated/approved | **imported** |
| 生成参数 | ✅ prompt/seed | ❌ |
| license | ❌ | ✅ 许可类型 |
