# release-process-control

发布流程控制子技能 — 与 `execution-control` 配合使用。

## 快速开始

参见 [SKILL.md](./SKILL.md) 了解完整规范；执行细节参考 [templates/release-process-template.md](./templates/release-process-template.md)。

## 适用对象

- 业务服务、模型、前端资源、数据库迁移等所有线上变更
- 任何需要"灰度 / 监控 / 回滚 / 复盘"的发布场景

## 相关 Skill

- 上游：`execution-control`（风险评估/审计基线）
- 关联：`config-sync-control`（环境配置一致性）、`asset-management-control`（资源就绪）