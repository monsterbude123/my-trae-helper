# Game Production Kit — 项目脚手架

使用方法: 复制 `scaffold/` 到你的游戏项目目录，重命名为 `{game_key}/`。

## 结构

```
{game_key}/
├── .project-cockpit.md       ← Cockpit 状态卡（Agent 自动填充）
├── .checkpoint-phase3.json   ← Phase 3 子 checkpoint
├── story-design.md           ← 故事设计文档
├── game-design-doc.md        ← GDD（非 VN 游戏必填）
├── asset-manifest.md         ← 素材清单（Agent 自动填充）
├── scene-manifest.json       ← 场景清单（Agent 自动填充）
├── assets/
│   └── _placeholder/         ← 降级占位素材
├── scripts/                  ← 引擎脚本（Phase 3 产出）
├── build/                    ← 构建产物（Phase 5 产出）
├── tests/
│   └── test_save_compat.py   ← 存档兼容测试统一入口
└── reports/                  ← Report Growth 报告
```
