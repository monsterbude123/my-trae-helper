---
name: gate-control
description: Gate 控制核心技能 — 代码生命周期的分层门禁机制，在 commit/push/merge/release 关键节点自动执行检查，确保代码质量、安全性和可维护性。当 git 操作、PR 合并、发布前触发。
requires:
  skills: []
  optional: []
---

# gate-control

> 📘 **这是 Skill 入口（精简版）。完整指南见 [`../../references/gate-skills-guide.md`](../../references/gate-skills-guide.md)**
>
> **职责划分**:
> - `SKILL.md`（本文件）→ Skill 加载入口，四层门禁概览 + 核心控制点速览
> - `references/gate-skills-guide.md` → 完整参考指南（355 行，含 L1~L4 详细检查项、配置示例、Hook 集成）
> - `references/gate-implementation.md` → 落地实现细节（脚本/模板引用）

## 定位

Gate 控制核心 — 代码生命周期的分层门禁机制，确保代码质量和安全性。

## 适用场景

- Git commit / push / merge / release 各阶段的质量门禁
- 多层级流水线(L1~L4)的"检查点"阻断
- 与 CI/CD(GitHub Actions / GitLab CI)集成的自动化关卡

## 四层门禁机制

```
L4 发布前门禁 (Release Gate)
L3 合并前门禁 (Merge Gate)
L2 推送前门禁 (Push Gate)
L1 提交前门禁 (Commit Gate)
```

> 越靠近底层 → 检查越快越轻；越靠近顶层 → 检查越深越重。

## 执行流程

```
代码变更 → 门禁匹配 → 检查执行 → 结果判定 → PASS/BLOCK
```

(亦称"核心流程")

## 各层概览

| 层级 | 触发时机 | 核心检查项 |
|:----:|---------|-----------|
| L1 | `git commit` | Lint + TypeCheck + 单元测试 + 格式化 |
| L2 | `git push` | L1 + 集成测试 + 覆盖率检查 + 构建 |
| L3 | PR merge | L2 + 代码审查 + E2E 测试 |
| L4 | Release | 全量测试 + 性能基准 + 安全扫描 + 验收测试 |

## 关键控制点

### GP-1 每层必须全过

- L_n 失败 → 直接 BLOCK，不允许"先提交后修复"

### GP-2 配置可定制

- 检查项 / 阈值 / 白名单 均可配置
- 见 `templates/gate-config-template.json`

### GP-3 执行时间预算

- L1 ≤ 30s / L2 ≤ 5min / L3 ≤ 15min / L4 ≤ 60min（参考阈值）

## 验收标准

1. 每层级检查全部通过才允许进入下一阶段
2. 失败必须有明确的错误信息
3. 门禁配置可定制（检查项、阈值、白名单）
4. 执行时间在可接受范围内

## 导航

| 内容 | 位置 |
|------|------|
| L1~L4 详细检查项与 Hook 集成 | [`../../references/gate-skills-guide.md`](../../references/gate-skills-guide.md) |
| 落地实现细节 | [`references/gate-implementation.md`](references/gate-implementation.md) |
| 门禁配置 / pre-commit / pre-push 模板 | [`templates/`](templates/) |