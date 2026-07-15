---
name: game-operations
description: 游戏上线后运营 — 引擎无关。覆盖内容更新/DLC/赛季/本地化/数据埋点/玩家反馈/商店管理/法规合规。触发词：游戏运营、上线后、内容更新、DLC、赛季、本地化、localization、数据分析、商店发布。
user-invocable: true
---

# 游戏上线后运营

> 引擎无关的长期运营能力。Phase 6 构建完成 → Phase 7 进入运营生命周期。

## 前置条件

- Phase 6 Deploy 已成功（线上可访问产物）
- game-production-kit 编排器已加载
- .project-state-card.md 存在（含部署记录）

## 骨架流程

```
1. 上线检查清单 → ops-checklist.md
     │
2. 本地化管线
     文本提取 → 翻译注入 → 溢出检查
     │
3. 数据埋点
     事件定义 → Funnel 设计 → Dashboard 搭建
     │
4. 内容更新
     版本迭代 → 存档兼容 → 回归测试
     │
5. 玩家反馈
     收集 → 分类 → 设计回溯
     │
6. 持续循环（每版本/每赛季）
```

## 约束

- 本地化文本用 key-based 系统，不硬编码字符串
- 埋点事件定义在 game-design-doc 阶段预留
- 内容更新必须通过存档兼容性测试（读取 N-1 版本存档）

> 🛑 边界: game-operations 只做内容更新（活动/赛季/本地化/埋点）。Bug 修复走 game-hotfix 流程。不得将限时活动送入 hotfix 分级。

## 质量清单

- [ ] 上线检查清单 100% 通过
- [ ] 多语言溢出检查覆盖率 ≥ 目标语言数
- [ ] 核心 Funnel 埋点覆盖率 100%
- [ ] 存档跨版本兼容性测试通过（至少前 1 个版本）
- [ ] 商店页面必需素材齐全（截图/预告片/描述/分级）

## 铁律

```
1. 没有上线检查清单 → 不发布
2. 没有跨版本存档兼容测试 → 不发内容更新
3. 没有隐私合规自查 → 不开放数据采集
4. 法律合规未确认 → 不提交商店审核
5. 停服必须有离线模式或数据导出方案
```

## 详细参考

| 模块 | 文件 | 内容 |
|------|------|------|
| 上线检查清单 | `references/01-launch-checklist.md` | 技术/商店/内容/法律 4 维检查 |
| 本地化管线 | `references/02-localization.md` | Key-based 系统 / 翻译管线 / 溢出检查 / 字体回退 |
| 数据埋点与 Funnel | `references/03-analytics.md` | 事件定义 / 核心指标 / A/B 测试 / 隐私合规 |
| 内容更新与赛季 | `references/04-live-ops.md` | 版本迭代 / 赛季系统 / DLC / 活动模板 / 停服协议 |
| 商店发布与合规 | `references/05-store-compliance.md` | Steam/EGS/App Store/Google Play/itch.io + 年龄分级 |
