# 场景 1: 新建 VN 完整链 — 《咖啡馆的猫》

> **模拟**: 用户第一次使用 game-production-kit，从头做一个短篇视觉小说。走完整 8 Phase 流水线。

---

## 用户视角

```
用户: "帮我做一个视觉小说《咖啡馆的猫》，3个角色，8个场景，有立绘和配音"

Agent: 🎮 Phase 0 Cockpit 启动...
      检测: .project-cockpit.md 不存在 → 新游戏
      → 初始化 cockpit（game_key=cafe-cat, 引擎待确认）
      
      引擎选择引导:
      Q: 游戏类型？ → VN/视觉小说
      Q: 目标平台？ → Web
      Q: 技术偏好？ → 零代码/低门槛
      → 推荐: WebGAL（Web 原生、零代码 DSL、免费开源）
      用户确认 → 引擎锁定 WebGAL

Phase 0.5 Engine: WebGAL ✅ → cockpit 更新

Phase 1 Story+Design:
  → 加载 game-story-design → 逐节面试 10 节
  → 产出 story-design.md（v1）：3 角色宪法 + 8 场景 + 剧情树（1真结局+2坏结局）
  → GDD 判定: VN 纯叙事 → 标记 N/A（跳过 game-design-doc）

Phase 2 Asset Pipeline:
  → 加载 game-asset-pipeline → 实体清单 → 素材预算
  → 生成顺序: 立绘(6张) → 背景(8张) → BGM(2首) → TTS配音(约80行对话)
  → 产出 asset-manifest.md + 全部素材文件

Phase 3 Scripting:
  → 加载 webgal-scripting → 按 story-design.md 场景列表写 .txt 脚本
  → 产出 scene-manifest.json + asset-references.json + proof-screenshots/(3张)

Phase 4 Quality Gate:
  → 加载 game-quality-gate → 自动化检查全部 APPROVE
  → 立绘 RGBA/尺寸 ✅ 背景尺寸 ✅ BGM 互异 ✅ TTS 静音检测通过
  → 安全审查 PASS（无外部脚本执行、无敏感信息泄露）
  → 产出 quality-report.md

Phase 5 Build:
  → 加载 webgal-engine-build → 素材导入验证 → vite build
  → 产出 dist/ → proof bundle 截图验证 ✅

Phase 6 Deploy:
  → 部署到 itch.io → 线上可访问 → cockpit 标记 Phase 6 ✅

Phase 7 Operations:
  → 跳过（短篇 VN，无持续运营需求）

Agent: 🎉 《咖啡馆的猫》制作完成！线上地址: https://xxx.itch.io/cafe-cat
```

---

## 系统内部流程

```
用户输入
  │
  ├── Phase 0 Cockpit
  │     ├── 检测 .project-cockpit.md → 不存在 → 初始化
  │     ├── 引擎选择引导 → WebGAL
  │     └── 写入 cockpit（game_key=cafe-cat, engine=webgal, phase=1 ⏳）
  │
  ├── Phase 1 Story+Design
  │     ├── 加载 game-story-design → 10节面试
  │     ├── 落盘 story-design.md（v1）+ 角色宪法
  │     ├── GDD 判定: VN → N/A
  │     └── cockpit: phase=2 ⏳
  │
  ├── Phase 2 Asset Pipeline
  │     ├── 加载 game-asset-pipeline + comfyui-api-skills
  │     ├── 立绘(6) → 背景(8) → BGM(2) → TTS(80行)
  │     ├── 落盘 asset-manifest.md + 素材文件
  │     └── cockpit: phase=3 ⏳
  │
  ├── Phase 3 Scripting
  │     ├── 加载 webgal-scripting
  │     ├── 逐场景写 .txt 脚本（8 场景 + 分支）
  │     ├── 产出 scene-manifest.json + asset-references.json
  │     ├── 截图 proof-screenshots/ (≥3张)
  │     └── cockpit: phase=4 ⏳
  │
  ├── Phase 4 Quality Gate
  │     ├── 加载 game-quality-gate
  │     ├── 自动化检查 → 全部 APPROVE
  │     ├── Chain-of-Verification 5问 → 无异常
  │     ├── 安全审查 PASS
  │     ├── 落盘 quality-report.md
  │     └── cockpit: phase=5 ⏳
  │
  ├── Phase 5 Build
  │     ├── 加载 webgal-engine-build
  │     ├── 素材验证 → vite build → dist/
  │     ├── proof bundle 截图 ✅
  │     └── cockpit: phase=6 ⏳
  │
  ├── Phase 6 Deploy
  │     ├── 部署 itch.io → 线上可访问
  │     └── cockpit: phase=7 ✅
  │
  └── Phase 7 Operations（跳过）
```

---

## 关键决策点

| 决策点 | 判断条件 | 结果 |
|--------|---------|------|
| 引擎选择 | VN + Web + 零代码 → 引擎决策指南 | WebGAL |
| GDD 是否生成 | VN 纯叙事 | 跳过（标记 N/A） |
| 素材生成顺序 | 立绘（核心视觉）优先 → 背景 → 音频 | 立绘→BG→BGM→TTS |
| Phase 7 是否执行 | 短篇 VN 无持续运营需求 | 跳过 |
| Cockpit 更新时机 | 每个 Phase 门禁通过后 | 写入 phase 状态 + 最后产出时间 |

---

## 发现的问题

1. **cockpit 状态卡命名不一致**: SKILL.md §6 使用 `.project-state-card.md`，但 §2.5 和 cockpit.md 使用 `.project-cockpit.md`。同一个文件两个名字，Agent 自检时可能找错文件。建议统一为 `.project-cockpit.md`。

2. **Phase 0 引擎确认无独立 skill**: Phase 0.5 引擎确认决策树内嵌在 SKILL.md 中，没有对应的 `engine-selector` 子技能。主 Agent 直接处理，可能超出主上下文边界（协调器不该直接执行决策逻辑）。

3. **Phase 1 门禁描述模糊**: SKILL.md §1 表写 `story-design.md + 用户确认（非 VN 游戏加 game-design-doc）`，但 §4 委派速查写 `game-story-design + game-design-doc`。两个表对 VN 场景的 GDD 预期不一致——§1 说 VN 可跳过，§4 没标注条件。
