---
name: guard-control
description: Guard 控制核心技能 — Agent 开发流程中的自动化门禁，在关键节点执行强制性检查，阻止不符合规范的代码/设计进入下一阶段。当 API 变更、测试覆盖率检查、代码审查前触发。
requires:
  skills: []
  optional: []
---

# guard-control

> 📘 **这是 Skill 入口（精简版）。完整指南见 [`../../references/guard-skills-guide.md`](../../references/guard-skills-guide.md)**
>
> **职责划分**:
> - `SKILL.md`（本文件）→ Skill 加载入口，核心流程 + 控制点速览
> - `references/guard-skills-guide.md` → 完整参考指南（696 行，含 5 个核心 Guard Skills 的检查项、配置示例、白名单机制）
> - `references/guard-implementation.md` → 落地实现细节（脚本/模板引用）

## 定位

Guard 控制核心 — Agent 开发流程中的自动化门禁，执行强制性检查，阻断不规范代码。

## 适用场景

- API 变更、契约校验触发 API Contract Guard
- PR 提交/合并前测试覆盖率检查
- 关键路径上的禁止性规则校验

## 执行流程

```
变更检测 → 规则匹配 → 检查执行 → 结果判定 → PASS/WARN/BLOCK
```

(亦称"核心流程")

## 关键控制点

### GP-1 禁止规则优先

```yaml
forbidden:
  - 添加无 Schema 的 API 端点
  - 修改已发布 API 的响应结构（破坏性变更）
  - 跳过版本号递增
  - 移除必需字段而不升级版本
  - 在生产端点使用 mock 数据
```

### GP-2 白名单机制兜底

```yaml
whitelist:
  - path: "/health"
    reason: "健康检查端点，无需认证"
    expires: "永久"
```

### GP-3 失败必须阻断

| 结果 | 处理 |
|------|------|
| PASS | 继续流程 |
| WARN | 输出警告，允许继续（需人工确认） |
| BLOCK | 终止流程，输出详细错误，要求修复 |

## 核心 Guard 类型

| Guard | 触发时机 | 检查内容 |
|-------|---------|---------|
| API 契约 Guard | API 定义变更/接口发布前 | 端点命名/Schema 完整性/版本管理 |
| 测试覆盖率 Guard | 提交前/合并前 | 覆盖率阈值/关键路径覆盖 |
| 依赖安全 Guard | 依赖更新后 | 已知漏洞/许可证合规 |
| 性能预算 Guard | 发布前 | 包体积/加载时间/内存占用 |

## 验收标准

1. BLOCK 结果必须终止流程，不允许绕过
2. 白名单项必须有过期时间（永久除外）
3. 检查失败必须输出修复建议
4. 所有检查必须有明确的通过/失败判定

## 导航

| 内容 | 位置 |
|------|------|
| 5 个核心 Guard Skills 详细规范 | [`../../references/guard-skills-guide.md`](../../references/guard-skills-guide.md) |
| 落地实现细节 | [`references/guard-implementation.md`](references/guard-implementation.md) |
| API 契约 / 覆盖率 Guard 配置模板 | [`templates/`](templates/) |