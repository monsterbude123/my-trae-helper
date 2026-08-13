# asset-management-control

资产管理控制子技能 — 与 `execution-control` 配合使用。

## 快速开始

参见 [SKILL.md](./SKILL.md) 了解完整规范；执行细节参考 [templates/asset-management-template.md](./templates/asset-management-template.md)。

## 适用对象

- 二进制、媒体、模型、压缩包、大文档等不可文本 diff 的资产
- 任何需要"上传/去重/引用追踪/清理"的场景

## 相关 Skill

- 上游：`execution-control`（风险评估/审计基线）
- 关联：`data-change-control`（结构化数据的去重可复用其流程）