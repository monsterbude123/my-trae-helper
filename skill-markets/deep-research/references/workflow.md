# Deep Research — 完整工作流

> 本文件是 SKILL.md §2 流程的展开版。详细步骤 + 工具签名 + 策略。

---

## Step 1: 理解目标

**澄清 1-2 问**（避免跑偏）：

- "您的目标是什么？学习 / 做决策 / 撰写内容？"
- "有特定角度或深度要求吗？"

**用户说"直接研究即可"** → 跳过澄清，使用合理默认（学术优先 + 12 月内来源 + 15-30 来源）。

---

## Step 2: 规划研究

**拆 3-5 个子问题**。每个子问题必须：

```
MUST:
  - 独立可搜索（不是"A 和 B 的关系"这种耦合问）
  - 可证伪（有反例 = 子问题有效）
  - 范围明确（"X 在 Y 市场的 Z 维度"而非"X 怎么样"）
```

**示例**（主题：AI 对医疗的影响）：

```
1. 目前医疗领域的主要 AI 应用有哪些？
2. 测得了哪些临床结果（疗效 / 误诊率 / 成本）？
3. 监管挑战（FDA / NMPA / GDPR-Health）？
4. 头部公司（产品 + 融资 + 落地医院数）？
5. 市场规模 + 5 年 CAGR 预测（来源？哪家公司测算）？
```

---

## Step 3: 执行多源搜索

### 工具调用签名

**firecrawl**：
```
firecrawl_search(query: "<子问题关键词>", limit: 8)
firecrawl_scrape(url: "<url>")
firecrawl_crawl(url: "<domain>", limit: 20)
```

**exa**：
```
web_search_exa(query: "<子问题关键词>", numResults: 8)
web_search_advanced_exa(query: "<关键词>", numResults: 5, startPublishedDate: "2025-01-01")
crawling_exa(url: "<url>", tokensNum: 5000)
```

### 搜索策略

| 维度 | 建议 |
|------|------|
| 关键词变体 | 每子问题 2-3 个（短词 / 长尾 / 学术化） |
| 时间窗口 | 默认 12 个月内，技术类放宽到 24 个月 |
| 来源类型 | 学术 > 官方 > 知名新闻 > 博客 > 论坛 |
| 总量目标 | 15-30 个 unique URL（去重） |
| 重复来源 | 同站点 ≤ 2 条（避免单点偏倚） |

---

## Step 4: 深度阅读关键来源

**选 3-5 个最相关 URL 抓全文**：

```
firecrawl_scrape(url)         # 适合单页
crawling_exa(url, 5000)       # 适合多 token 提取
```

**阅读原则**：

- ⚠ 不全信搜索片段（snippet 经常断章）
- ⚠ 同一事实多源对照（避免单源误差）
- ⚠ 数据来源链（"X 说 Y" → 找 X 引用的原始研究）

---

## Step 5: 综合并撰写报告

套 [report-template.md](report-template.md)。核心原则：

```
- 主题分章节（按子问题或主题聚类）
- 关键事实 inline 引用（[Source](url)）
- 区分"高置信" / "中置信" / "未验证"
- 末尾给可执行 takeaways（不是简单总结）
```

---

## Step 6: 交付

| 报告长度 | 交付方式 |
|---------|---------|
| < 1500 字 | 完整发聊天 |
| ≥ 1500 字 | 摘要 + 落盘到 `<workspace>/research-{topic}-{date}.md` |

**落盘路径建议**：

```
project-root/
  docs/
    research/
      {topic-slug}-{YYYYMMDD}.md
```

---

## 并行研究协议（加速广主题）

当子问题 ≥ 5 且彼此独立：

```
Task tool:
  Agent A: 子问题 1-2（独立上下文 + 独立 MCP 调用）
  Agent B: 子问题 3-4
  Agent C: 子问题 5 + 横向主题
  Agent D: 反向 fact-check（专项验证其他 agent 的争议声明）

主会话: 收集 4 份 findings → 综合 → 套报告模板
质量门禁: 每份 findings 必须 ≥ 5 引用 + 已交叉验证
```
