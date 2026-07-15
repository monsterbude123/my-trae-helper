---
name: game-quality-gate
description: 游戏素材质量门禁 — 引擎无关。自动化检查立绘/背景/标题/BGM/TTS的质量，阻断不合格素材进入构建。支持 full/lean/solo 三档审查模式。触发词：质量门禁、素材检查、质量审查、asset check。
user-invocable: true
---

# 游戏素材质量门禁

引擎无关的素材质量自动化检查。任何检查不通过 → 阻断构建，回到素材管线重新生成。

> Gate 机制参照 Claude-Code-Game-Studios Director Gates：每项检查返回 APPROVE / CONCERNS / REJECT 三态 verdict，按最严格结果决定整体状态。

## 审查模式

> 参照 CC Studio review-mode。通过参数 `--review [full|lean|solo]` 控制。

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| `full` | 自动化 + 人工确认 → 逐项 verdict | 正式发布、团队协作 |
| `lean` | 自动化 + 人工确认 → 整体 PASS/FAIL | **默认** — 个人项目、快速迭代 |
| `solo` | 仅自动化检查 → 跳过人工确认 | 原型验证、极速构建 |

## 铁律

- Gate verrict 为 REJECT → **阻断**，不得跳过，回退 Phase 2 改正
- Gate verdict 为 CONCERNS → 向用户展示问题列表，用户决定"修复"或"接受并继续"
- 门禁是构建的前置条件，不是建议

## 自动化检查项

| 类别 | 检查项 | 阈值 | 失败含义 | 失败动作 |
|------|--------|------|----------|----------|
| 立绘 | RGBA 模式 | 必须是 RGBA | BiRefNet 抠图失败 | 阻断 |
| 立绘 | 832x1216 | 精确匹配 | 生成参数错误 | 阻断 |
| 立绘 | 30KB~2MB | 范围内 | 过小=空白图，过大=伪影 | 阻断 |
| 立绘 | HSV 饱和度 | > 5% | 过灰=生成失败 | 阻断 |
| 立绘 | 主体像素占比 | > 30% | 大面积空白/伪影 | 阻断 |
| 背景 | 1216x832 | 精确匹配 | 生成参数错误 | 阻断 |
| 背景 | >=15KB | 最小值 | 过小=单色填充 | 阻断 |
| 标题 | 1920x1080 | 精确匹配 | 生成参数错误 | 阻断 |
| 标题 | >=30KB | 最小值 | 过小=空白 | 阻断 |
| BGM | >=500KB | 最小值 | 可能为静默文件 | 阻断 |
| BGM | RMS/peaks 互异 | 所有文件不相同时 | seed 固定/重复 | 阻断 |
| TTS 配音 | 后 30% RMS | < max_amp × 0.01 | 过长静音 | 阻断 |

## 跨引擎脚本检查

> 来自 cross-engine-contract.md 统一产出契约。

| 检查项 | 阈值 | 失败含义 | 失败动作 |
|--------|------|----------|----------|
| scene-manifest.json | 存在且 JSON 可解析 | 脚本阶段未完成或格式错误 | 阻断 |
| asset-references.json | 存在且 missing 数组为空 | 素材引用断裂 | 阻断 |
| branch_coverage | ≥ story-design 分支数 | 剧情分支未全部实现 | 阻断 |
| proof-screenshots/ | ≥ 3 张 | 关键场景未验证 | 询问用户 |
| 游戏逻辑 | [02-game-logic-checks.md](references/02-game-logic-checks.md) | 分支覆盖 / 存档兼容 / 性能基线 | — |

## Chain-of-Verification

> 参照 CC Studio gate-check；每个 Gate 验证后自我挑战 5 个问题。

```
1. 自动化检查通过
2. 自问 5 个反例问题：
   a) 是否有素材刚过阈值但肉眼明显不合格？
   b) 是否有素材漏检（新增文件未在 asset-manifest.md 中）？
   c) 是否有设计文档更新但素材未同步（source_version 不一致）？
   d) 是否有 BGM/SFX 字节大小正常但实际为静音？
   e) 是否有配音正常但文本与字幕不匹配？
3. 任一问题答案为"是" → 降 verdict（APPROVE → CONCERNS 或 CONCERNS → REJECT）
4. 人工确认 5 个自问的结果
```

## Gate 判定逻辑

> 参照 CC Studio Director Gates：按最严格结果决定整体状态。

```
全部 APPROVE → 通过，进入 Phase 5
任一 CONCERNS → 展示问题清单，用户决定：
  - "修复" → 回退 Phase 2 改正具体项
  - "接受并继续" → 记录风险到 .project-state-card.md，继续
任一 REJECT → 阻断，必须回退 Phase 2 改正，不得跳过
```

## QA 证据分级

> 参照 CC Studio qa-lead 故事类型 → 测试证据矩阵。

| 素材类别 | 自动化检查 | 人工确认 | 说明 |
|---------|-----------|---------|------|
| 角色立绘 | **阻断** (尺寸/格式/RGBA/饱和度/主体) | 必须 (五官/颜色/设计) | 影响全线视觉 |
| 场景背景 | **阻断** (尺寸/格式/文件大小) | 建议 (氛围/无畸变) | 游戏可玩性核心 |
| 标题图 | **阻断** (尺寸/格式) | 建议 (清晰度) | 第一印象 |
| BGM | 探测 (文件大小/RMS) | 必须 (试听) | 无法自动化判断氛围 |
| TTS 配音 | **阻断** (静音检测) | 必须 (同步/音色) | 无法自动化判断匹配度 |
| 动画精灵 | **阻断** (逐帧 RGBA/尺寸) | 必须 (循环/连续性) | 多帧复杂性高 |

## 流程

```
1. 加载 asset-manifest.md → 定位所有素材路径
2. 运行自动化检查 → 逐项判定 APPROVE/CONCERNS/REJECT
3. Chain-of-Verification → 5 个自问 → 调整 verdict
4. 输出 quality-report.md → 含每项 verdict + 自问结论
5. 人工确认 → 五官正常？氛围匹配？设计一致？自问到位的？
6. 用户确认 → "确认无误后继续构建？(Y/n)"
```

## 人工确认点

```
全部自动化检查通过。建议人工核查：
1. 立绘：五官正常？服装颜色与设计稿一致？透明背景纯净无白边？
2. 背景：场景氛围正确？无畸变？与设计文档描述一致？
3. BGM/SFX：试听后确认氛围匹配？无静音/杂音？
4. TTS 配音：与字幕同步？音色与角色设计匹配？
5. 标题图：文字清晰？设计符合预期？
6. 动画精灵：逐帧连贯？动作自然？循环无跳帧？
```

## 详细参考

- 完整检查项与执行方式：`references/01-check-items.md`
- Gate verdict 阈值定义：`references/gate-standards.md`
