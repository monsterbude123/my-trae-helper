# product-teardown — 双层产品/技术拆解技能包（正式）

> **定位**：对目标产品做「P/T 双层隔离」拆解，产出两份独立交付物 —— 《产品 PRD》与《技术拆解文档》。
> **治理状态**：正式 SKILL 包，已注册于 `registry/skills.yaml`，受 structure guard 校验。

---

## 能力概述

把目标产品拆解为**两个完全隔离的层**：

| 层 | 子 Agent | 交付物 | 消费视角 |
|----|----------|--------|----------|
| **P 层（产品层）** | `product-teardown-analyze` | 5 产品维度分析 → 功能菜单 → 《产品 PRD》 | 产品策划经理，**零技术噪音** |
| **T 层（技术层）** | `product-teardown.tech` | 《技术拆解文档》（技术→模块映射） | 研发 / 技术评估 |

核心诉求：**产品文档不被技术描述污染**。技术实现（技术栈/架构/第三方依赖）只存在于《技术拆解文档》，PRD 仅做尾注引用。

---

## 结构

- `SKILL.md` — 编排器（唯一入口，协调全流程，P/T 双层）
- `skills/product-teardown-analyze/` — 产品拆解器（P 层，5 维度）
- `skills/product-teardown-tech/` — 技术拆解器（T 层，技术→模块映射）
- `skills/product-teardown-prd/` — PRD 文档生成器（P 层纯产品 PRD）
- `templates/` — menu / prd-lite / prd-full / tech-doc 模板

## 依赖

- 无外部 skill 硬依赖；重活委派经 `Task` 工具调用子 Agent（`general_purpose_task`）

## 触发

- 用户说"分析 / 复刻 / 竞品拆解 [产品名]"等 → 本 skill 自动加载

## 产出落盘

所有中间产物 + 最终交付物落盘到 `docs/product-analysis/<产品名>/`，命名 `<产品名>-{product|tech|menu|prd-完整|prd-精简}-<时间戳>.md`。聊天回复只回路径 + 摘要，不全文打印。详见 `SKILL.md` §一.5。