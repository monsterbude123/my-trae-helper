---
name: e2e-module-audit
status: deprecated
redirect_to: acceptance-discipline
description: [DEPRECATED → acceptance-discipline] E2E 双模式验证 — 批量验收（模块级回归 + 诊断报告）+ 即时诊断（单页面灵敏修复）。截图组织 → vision-audit → 日志关联 → 结构化诊断。
intent: [DEPRECATED → acceptance-discipline] E2E 双模式验证 — 批量验收（模块级...
category: gate
audience: [devops]
---
# e2e-module-audit

### 重要！！！！！！！！！！
- e2e的过程中即时的使用vision-audit 看界面内容，不要把问题堆积起来，如果你已经指导项目本身存在问题的情况下，跑全量e2e完全没意义，大部分时间是 e2e 的 Workflow B 在激活
- 只有你确定你知道没啥问题，就跑一跑e2e 全量，但是e2e全量太重，只能提醒用户主动触发，不要自己尝试。
### 两种工作流
> E2E 截图验证 + 后端日志关联诊断。**两种工作流，一个技能。**
>
> 文件索引：
> - [Workflow A — 批量验收](workflow-a-batch.md) · 模块级回归 / CI 门禁
> - [Workflow B — 即时诊断](workflow-b-instant.md) · 单页面灵敏修复
> - [共享基础设施](infra-shared.md) · helpers + 诊断推理引擎
> - [通用约定](conventions.md) · 命名规范 / vision-audit / 接入 / FAQ

---

## 两种工作流

| 维度 | Workflow A：批量验收 | Workflow B：即时诊断 |
|------|---------------------|---------------------|
| **目的** | 全量回归、模块级验收、CI 门禁 | 单页面 / 单交互的灵敏修复 |
| **触发词** | "跑 E2E""全量""回归""CI""发版" | "XX 有问题""帮我看看""修一下" |
| **粒度** | 整个模块的所有路由 + 交互 | 单个 bug 复现路径 |
| **产出** | `_diagnosis.md` + `_logs/` 归档 | 即时结论 → 修复代码 → 验证 |
| **日志策略** | Phase 0-4 全流程自动捕获 | 操作后即时 tail -f / API 查询 |
| **vision-audit** | `--dir` 目录扫描 | `--file` 单张分析 |
| **速度** | 分钟级 | 秒级（闭环 < 30s） |
| **异常处理** | recordAnomaly → 报告汇总 → 审阅 | 发现即修复，修复即验证 |

**共享核心理念**：截图是线索，日志是证据。两种工作流共享同一套 [诊断推理引擎](infra-shared.md#4-诊断推理引擎核心)，仅输出形式不同。

---

## 快速导航

### 我需要跑全量回归 / 模块验收
→ 读 [Workflow A — 批量验收](workflow-a-batch.md)
  - [工作流总览](workflow-a-batch.md#a1-工作流总览) (Phase 0→4)
  - [spec 模板](workflow-a-batch.md#a4-spec-模板)
  - [诊断报告格式](workflow-a-batch.md#a5-诊断报告格式)

### 用户说某个页面/按钮有问题，我要立刻定位 + 修复
→ 读 [Workflow B — 即时诊断](workflow-b-instant.md)
  - [即时诊断协议](workflow-b-instant.md#b2-即时诊断协议ai-必须逐步执行) (6 步闭环)
  - [硬约束](workflow-b-instant.md#b3-即时诊断的硬约束)
  - [示例对话](workflow-b-instant.md#b4-完整示例对话)

### 我要实现 helper / 了解推理引擎
→ 读 [共享基础设施](infra-shared.md)
  - [截图 helper](infra-shared.md#1-截图-helper)
  - [后端日志 helper](infra-shared.md#2-后端日志-helper)
  - [浏览器上下文捕获](infra-shared.md#3-浏览器上下文捕获-helper)
  - [诊断推理引擎](infra-shared.md#4-诊断推理引擎核心)

### 命名规范 / vision-audit / 接入 / FAQ
→ 读 [通用约定](conventions.md)

---

## 模式选择决策树

```
用户输入包含以下关键词？
  ├─ "跑一下 E2E" / "全量" / "回归" / "CI" / "发版"
  │   → Workflow A
  ├─ "XX 页面有问题" / "帮我看看" / "为什么" / "修一下"
  │   → Workflow B
  ├─ 用户贴了一张截图说有问题
  │   → Workflow B（先复现场景，再收集日志）
  └─ 不确定
      → 问用户："是全量跑模块 E2E 还是针对这个问题即时诊断？"
```
