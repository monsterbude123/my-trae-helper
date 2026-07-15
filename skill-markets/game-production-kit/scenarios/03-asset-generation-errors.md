# 场景 3: 素材生成异常处理 — ComfyUI 超时 + TTS 部分失败

> **模拟**: Phase 2 素材生成中，ComfyUI 后端超时导致部分立绘/背景失败，TTS 部分对话行超时。触发 L1 异常处理协议和降级策略。

---

## 用户视角

```
Agent: Phase 2 Asset Pipeline 启动...
       加载 game-asset-pipeline + comfyui-api-skills

  [1/4] 立绘生成（ComfyUI 本地管线）:
         character_elise_01.png ✅（832x1216 RGBA, 锚点图）
         character_elise_02.png ✅（衍生表情）
         character_lin_01.png  ⏳ ComfyUI 超时 → retry 1/2...
         character_lin_01.png  ✅（retry 2 成功）
         character_lin_02.png  ✅

  [2/4] 背景生成:
         bg_cafe_morning.png ✅
         bg_cafe_evening.png ❌ ComfyUI 持续超时（retry 2/2 失败）
           → 降级: 复用 bg_cafe_morning.png + 色温偏移 作为占位
           → 写入 placeholder: bg_cafe_evening → bg_cafe_morning_dusk_fallback.png

  [3/4] BGM 生成（Stable Audio 3）:
         bgm_main_theme.ogg ✅（1.2MB, RMS 正常）
         bgm_ending.ogg     ✅（互异检测通过）

  [4/4] TTS 配音（voice-acting-skill）:
         voice_scene_01_001.wav ✅
         voice_scene_01_002.wav ❌ API 超时 → retry 1/1 失败 → 跳过
         voice_scene_01_003.wav ✅
         ... (共 80 行，2 行失败)

Agent: [L1] 素材降级报告 → 写入 report-01.md
      影响范围:
        bg_cafe_evening → fallback（功能可用，视觉需后续修复）
        voice_scene_01_002 → skipped（该行对话无声，显示字幕）

      asset-manifest.md 标记:
        bg_cafe_evening.png:          status=placeholder, source=bg_cafe_morning_dusk_fallback
        voice_scene_01_002.wav:       status=skipped

      质量预估: ⚠️ 2 项异常
        - 1 个背景降级 → 不阻断（故事可推进，视觉有瑕疵）
        - 1 个配音缺失 → 不阻断（字幕可见，音频需补录）
      → Phase 4 质量门禁预期: CONCERNS（可接受继续）

Agent: 素材管线完成。2 项异常已记录，可继续 Phase 3 Scripting。
      建议: Phase 4 前重新尝试 bg_cafe_evening 和 voice_scene_01_002。
```

---

## 系统内部流程

```
Phase 2 启动
  │
  ├── 立绘生成循环
  │     ├── char_01 ✅ → char_02 ✅
  │     ├── char_03 ⏳ → retry 2/2 ✅
  │     └── 全部成功 → 无降级
  │
  ├── 背景生成循环
  │     ├── bg_01 ✅
  │     ├── bg_02 ❌ → retry 2/2 仍失败
  │     │     └── [降级] 占位素材（复用 + 色温偏移）
  │     └── 1 项降级
  │
  ├── BGM 生成循环
  │     ├── bgm_01 ✅
  │     └── bgm_02 ✅ → 全部成功
  │
  ├── TTS 配音循环
  │     ├── voice_001 ✅
  │     ├── voice_002 ❌ → retry 1/1 失败 → 跳过
  │     ├── voice_003 ✅
  │     └── 2 行失败 → 1 项跳过
  │
  └── 异常处理
        ├── 判定等级: L1（资产/文件异常）
        ├── 原则: NEVER SILENT FAIL → retry 后 report
        ├── 写入 report-01.md（L1 格式）
        ├── 更新 asset-manifest.md（status=placeholder/skipped）
        └── 同步 cockpit 阻塞项区
```

---

## 关键决策点

| 决策点 | 判断条件 | 结果 |
|--------|---------|------|
| 立绘失败 | 立绘是核心视觉，缺失不可玩 | 必须 retry（2次），失败阻断 |
| 背景失败 | 背景可降级为占位 | retry 2次后降级，不阻断 |
| TTS 失败 | 配音是辅助，字幕可见 | retry 1次后跳过，不阻断 |
| BGM 失败 | 可选氛围增强 | retry 1次后跳过，不阻断 |
| 重试次数 | 资产类 2次 / 语音类 1次 | ComfyUI 2次 / TTS API 1次 |
| Report 写入时机 | 异常发生时实时记录 | 每次降级/跳过立即写入 report |

---

## 发现的问题

1. **retry 次数缺少资产类型区分声明**: report-growth.md 说 `RETRY TWICE, STOP`（最多 2 次），game-asset-pipeline 说每个资产最多 3 次。两个文件不一致——report-growth 统一 2 次，game-asset-pipeline 说 3 次。TTS 只重试 1 次的规则也没有在 report-growth 中显式区分。

2. **降级占位素材的路径规范缺失**: game-asset-pipeline 没有定义占位素材（placeholder）的命名约定和存放位置。本场景中 `bg_cafe_morning_dusk_fallback.png` 是模拟者推导的，实际执行时 Agent 可能把占位素材放到任意位置，Phase 4 门禁检查时可能因找不到预期路径而误报。

3. **TTS 跳过后 scene-manifest 的对话行一致性**: 当某个 voice 文件被跳过时，cross-engine-contract 中 scene-manifest.json 的 `dialogue_count` 是应该减去跳过的行还是保留原数？如果保留原数，Phase 4 验证时会发现 voice 文件数 < dialogue_count；如果减去，与 story-design 的场景对白数对不上。没有定义这个边界行为。

4. **cockpit 阻塞项与 report 联动未实现**: report-growth.md 说"每个 report 产出时在 cockpit 阻塞项区追加一条"，但 cockpit.md 的阻塞字段只是单值文本（`阻塞: {原因 / NULL}`），不支持多条阻塞项列表。新 report 会覆盖旧阻塞记录。
