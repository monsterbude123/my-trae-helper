---
name: execution-control
description: Execution 控制核心技能 — 规范化高风险执行操作，提供可审计的执行轨迹。当操作涉及多系统组件、不可逆性、需回滚机制时触发。
requires:
  skills: []
  optional: []
---

# execution-control

> 📘 **这是 Skill 入口（精简版）。完整指南见 [`../../references/execution-skills-guide.md`](../../references/execution-skills-guide.md)**
>
> **职责划分**:
> - `SKILL.md`（本文件）→ Skill 加载入口，核心流程 + 控制点速览
> - `references/execution-skills-guide.md` → 完整参考指南（976 行，含 5 个核心 Execution Skills 的详细规范、模板、示例）
> - `references/execution-implementation.md` → 落地实现细节（脚本/模板引用）

## 定位

Execution 控制核心 — Agent 执行过程的控制层方法论，确保跨会话一致性。

## 核心流程

```
变更请求 → 影响评估 → 风险分级 → 备份/预演 → 执行 → 验证 → 清理/回滚
```

## 关键控制点

### CP-1 影响评估（必须）

| 风险等级 | 触发条件 | 强制措施 |
|:-------:|---------|---------|
| HIGH | 影响生产数据/跨表关联/无WHERE条件 | 备份+dry-run+审批 |
| MEDIUM | 单表变更/有明确范围 | 备份+dry-run |
| LOW | 新增测试数据/临时表 | 可选备份 |

### CP-2 备份当前状态（HIGH/MEDIUM 必须）

- 数据库：`mysqldump --single-transaction`
- 文件系统：`cp -r data/ data.bak.$(date +%Y%m%d_%H%M%S)`

### CP-3 dry-run 预演（HIGH 必须）

```sql
START TRANSACTION;
-- 执行变更
ROLLBACK; -- 预演完成，回滚
```

### CP-4 执行监控（必须）

- 记录开始时间、结束时间、影响行数
- 超过阈值自动告警

### CP-5 验证结果（必须）

- 数据一致性校验 / 业务功能冒烟测试 / 性能回归检查

## 适用与不适用

| 类别 | 说明 |
|------|------|
| ✅ 触发 | 涉及 ≥ 2 系统组件 / 不可逆 / 失败需回滚 |
| ❌ 不触发 | 单一文件纯新增 / 纯查询类 / 用户明确"快速执行" |

## 验收标准

1. HIGH/MEDIUM 操作必须有影响评估报告
2. HIGH 操作必须有 dry-run 预演记录
3. 失败操作必须有回滚记录
4. 执行轨迹可审计（who/when/what/result）

## 导航

| 内容 | 位置 |
|------|------|
| 5 个核心 Execution Skills 详细规范 | [`../../references/execution-skills-guide.md`](../../references/execution-skills-guide.md) |
| 落地实现细节 | [`references/execution-implementation.md`](references/execution-implementation.md) |
| 数据变更 / 文档同步 / 配置同步等模板 | [`templates/`](templates/) |