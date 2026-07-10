---
name: game-hotfix
description: 游戏紧急修复流程 — S1/S2 分级审批 + 三方审批 + 回滚计划 + QA 重入门禁 + 事后复盘。适用于已上线游戏的紧急缺陷修复。触发词：游戏热修复、hotfix、紧急修复、线上bug、游戏回滚。
user-invocable: true
---

# 游戏紧急修复流程

> 吸收自 CC Studio hotfix 技能（7阶段流程 + S1/S2 分级 + 三方审批 + QA Re-Entry Gate + incident review）。

已上线游戏的紧急缺陷修复。非紧急修复走正常 Phase 4 门禁回退路径。

> 前置条件：游戏已上线（Phase 6 已完成）。
>
> 协作关系：独立技能，可在 kit 编排器路由下按需加载。不在正常 7 阶段流水线内。

## 核心铁律

```
1. 最小变更原则 — 只修 bug，不做重构或新功能
2. 必须有三方审批（程序员复查 + QA 回归测试 + 制作人批准部署）
3. 必须有回滚计划
4. 双分支合并：release branch + development branch
5. 4 小时内完成从发现到部署
6. 48 小时内完成 incident review
```

## S1 / S2 / S3 分级

| 级别 | 定义 | 响应时间 | 审批 |
|------|------|---------|------|
| **S1** | 不可玩 / 数据丢失 / 安全漏洞 | 紧急 (4h) | 三方审批 |
| **S2** | 重要功能损坏 | 紧急 (4h) | 三方审批 |
| **S3** | 视觉/UI 小问题 | 走正常 bug fix | 不需要 hotfix 流程 |

> S3 及以下不走 hotfix 流程。回到 Phase 4 门禁修复后重新构建。

## 7 阶段流程

```
1. Assess Severity → 定级 S1/S2/S3
     │
     ├── S3 → 回到正常 bug fix 流程
     │
     └── S1/S2 → 
2. Create Hotfix Record → hotfix-{date}-{编号}.md
3. Create Branch → hotfix/{issue-id} (基于 release branch)
4. Implement → 最小变更实施
5. Collect Approvals → 三方并行
     ├── lead-programmer: fix review
     ├── qa-tester: regression test
     └── producer: deployment approval
6. QA Re-Entry Gate → smoke / targeted / full 三级别
7. Deploy → 部署 + 监控
8. Post-Deploy Verification → 48h 内 incident review
```

## Hotfix 记录格式

```markdown
# Hotfix Record: {issue-id}
**日期**: 2024-07-08
**级别**: S1
**描述**: 进入第三场景后闪退
**根因**: 内存溢出 (null ref on dialog component)
**更改**: 1 个文件，3 行代码
**审批**: 
  - lead-programmer: APPROVED (2024-07-08 15:00)
  - qa-tester: APPROVED (2024-07-08 15:30)
  - producer: APPROVED (2024-07-08 15:45)
**回滚计划**: 回退到 build-{前一个版本号}
**部署时间**: 2024-07-08 16:00
**验证**: 正常 (2024-07-08 16:05)
```

## 三方审批

```
lead-programmer:  代码审查 — 变更是否正确？是否有副作用？
qa-tester:        回归测试 — 修复不引入新 bug？
producer:         部署审批 — 播放机影响范围？回滚准备就绪？
```

> 三方**并行**审批，不串行等待（节省时间）。

## QA Re-Entry Gate

根据受影响系统选择验证级别：

| 级别 | 范围 | 适用 |
|------|------|------|
| **smoke check** | 5 分钟关键路径 | 单系统、微小变更 |
| **targeted QA** | 受影响系统 + 邻接系统 | 中等影响 |
| **full QA** | 完整回归 | S1、多系统影响 |

**QA门禁输出**: `hotfix-qa-report.md`，含三态 verdict (PASS/CONCERNS/FAIL)。

## 回滚计划

```
1. 识别前一个生产版本 build tag
2. 确认回滚命令可用
3. 部署前测试回滚
4. 回滚触发条件: 部署后 15 分钟内监控告警 > 阈值
```

```bash
# 示例: 回滚 WebGAL 部署
publish rollback {game-key} -d {domain} --to {previous-build-tag}
```

## 变更约束

```
✅ 允许: 修复 bug 的单文件/单行变更
❌ 禁止: 重构代码、新功能、变更 API 接口、修改数据库 schema
```

> 违反任何一条禁止项 → 这不是 hotfix，回到正常开发流程。

## Incident Review（48小时内）

```markdown
# Incident Review: {issue-id}
**时间线**: 发现→诊断→修复→部署→验证 的时间戳
**影响范围**: 用户数 / 受影响功能
**根因分析**: 5 Why 追溯到根本原因
**预防措施**: 如何防止同类问题再次发生？
**流程改进**: hotfix 流程本身有什么可以优化的？
```
