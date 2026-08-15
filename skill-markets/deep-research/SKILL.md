---
name: deep-research
version: 1.0.0
version: 1.0.0
description: Multi-source deep research with firecrawl/exa MCPs. Searches the web, synthesizes findings, delivers cited reports. Use when the user wants thorough research with evidence and citations.
intent: Multi-source deep research with firecrawl/exa MCPs
category: other
audience: [devops]
---
# Deep Research

> 精简骨架（§11 约束：≤10 铁律 + ≤150 行 + 详细内容按需 references/）。
> 起源：ECC `.agents/skills/deep-research`（v1.9.0），本版按 AGENTS.md §5 接入 skill-markets 治理。

## 0. 何时激活

```
MUST 激活: 用户说"研究 / 深入 / 调查 / 现状" + 任何主题
  - 竞品分析、技术评估、市场规模、尽调
  - 任何需要多源综合 + 引用 + 证据的问题
MUST NOT 激活: 单源查询（用 WebFetch） / 项目内代码检索（用 GitNexus）
```

## 1. MCP 要求（前置）

```
硬依赖: 至少 1 个 firecrawl 或 exa
  - firecrawl_search / firecrawl_scrape / firecrawl_crawl
  - web_search_exa / web_search_advanced_exa / crawling_exa
两者都启用 = 最佳覆盖
配置: ~/.claude.json 或 ~/.codex/config.toml
降级: 无 MCP → 降级 WebSearch + WebFetch（明示"工具降级，引用质量降低"）
```

## 2. 流程（6 步骨架，详细按需 references/）

```
Step 1: 澄清目标    → 1-2 问（"学习 / 决策 / 写文？"），用户说"直接研究"则跳
Step 2: 拆子问题    → 3-5 个子问题（参考 [references/workflow.md](references/workflow.md)）
Step 3: 多源搜索    → 每子问题 2-3 关键词变体 / 总计 15-30 来源 / 优先级：学术>官方>新闻>博客
Step 4: 深度阅读    → 选 3-5 个最相关 URL 抓全文（scrape/crawling），不全信搜索片段
Step 5: 综合成稿    → 套 [references/report-template.md](references/report-template.md)
Step 6: 交付        → 短报告直发 / 长报告摘要+落盘
```

## 3. 质量铁律（6 条）

1. **每条主张必有来源** — 无源 = 删除或标"未验证"
2. **交叉验证** — 单源声明必须标"⚠ unverified"
3. **时效性优先** — 默认 12 个月内，老资料明示日期
4. **承认空白** — 找不到 → 直说"insufficient data"，不编
5. **区分事实/推断** — 估算/预测/观点分别标注
6. **No hallucination** — 不知道 = "未找到足够数据"

## 4. 并行研究（可选加速）

```
广主题: 启 3 个 Task 子代理并行
  - Agent A: 子问题 1-2
  - Agent B: 子问题 3-4
  - Agent C: 子问题 5 + 横向主题
主会话: 收集 3 份发现 + 综合成稿（铁律 §3 全应用）
```

## 5. 反模式（避坑）

```
❌ 只看搜索摘要就写报告 → 必走 Step 4 抓全文
❌ 单源转述当事实 → 必走铁律 §2 交叉验证
❌ 强行编造找不到的子问题答案 → 必走铁律 §4 承认空白
❌ 长报告全塞聊天 → 必走 Step 6 落盘 + 摘要
```

## 6. 引用

- 完整工作流 + 工具签名：[references/workflow.md](references/workflow.md)
- 报告模板（结构 + 字段）：[references/report-template.md](references/report-template.md)
- 质量规则逐条 + 反例：[references/quality-rules.md](references/quality-rules.md)
- 上游来源：ECC `.agents/skills/deep-research` v1.9.0（已扫描 PASS，无执行面）
