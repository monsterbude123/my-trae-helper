#!/usr/bin/env python3
"""Browser Use Cloud — 结构化数据提取模板

展示如何使用 Pydantic 模型搭配 client.run() 实现类型安全的结构化提取。

用法（直接运行示例）:
    python structured_extract.py

用法（作为模板复制）:
    cp structured_extract.py my_extractor.py && 编辑 my_extractor.py

依赖:
    pip install browser-use-sdk pydantic
    export BROWSER_USE_API_KEY=bu_your_key
"""

import asyncio
from typing import Optional
from pydantic import BaseModel, Field
from browser_use_sdk.v3 import AsyncBrowserUse


# ============================================================
# 定义你的输出 Schema（修改这里适配业务需求）
# ============================================================

class Product(BaseModel):
    """单个产品信息"""
    name: str = Field(description="产品名称")
    price: float = Field(description="当前价格（美元）")
    currency: str = Field(default="USD", description="货币代码")
    url: Optional[str] = Field(default=None, description="产品页面链接")
    rating: Optional[float] = Field(default=None, description="评分（1-5）")
    availability: Optional[str] = Field(default=None, description="库存状态")


class ProductList(BaseModel):
    """产品列表提取结果"""
    products: list[Product] = Field(description="提取的产品列表")
    source_url: Optional[str] = Field(default=None, description="数据来源 URL")
    total_count: Optional[int] = Field(default=None, description="总产品数")


class Article(BaseModel):
    """单篇文章信息"""
    title: str
    url: Optional[str] = None
    author: Optional[str] = None
    points: Optional[int] = None
    comment_count: Optional[int] = None


class ArticleList(BaseModel):
    """文章列表提取结果"""
    articles: list[Article]
    source: Optional[str] = None


# ============================================================
# 提取函数
# ============================================================

async def extract_products(task_description: str, model: str = "claude-sonnet-4.6") -> ProductList:
    """通用产品提取。

    Args:
        task_description: 自然语言任务描述，如 "搜索 Amazon 上的 MacBook Pro，提取前 5 个结果"
        model: 模型选择

    Returns:
        ProductList: 类型安全的产品列表

    示例:
        result = await extract_products("Search amazon.com for 'wireless headphones' and extract top 10 results with prices")
        for p in result.products:
            print(f"{p.name}: ${p.price}")
    """
    client = AsyncBrowserUse()
    result = await client.run(
        task_description,
        output_schema=ProductList,
        model=model,
    )
    return result.output


async def extract_articles(task_description: str, model: str = "claude-sonnet-4.6") -> ArticleList:
    """通用文章/帖子提取。

    示例:
        result = await extract_articles("List the top 20 posts on Hacker News with points")
        for a in result.articles:
            print(f"{a.title}: {a.points} pts")
    """
    client = AsyncBrowserUse()
    result = await client.run(
        task_description,
        output_schema=ArticleList,
        model=model,
    )
    return result.output


# ============================================================
# 高级模式：批量提取 + 成本优化
# ============================================================

async def extract_with_cache(
    workspace_name: str,
    task_template: str,
    params: list[dict],
) -> list:
    """使用 Deterministic Rerun 批量提取。

    首次运行全 agent，后续 $0 LLM 成本。

    Args:
        workspace_name: workspace 名称
        task_template: 任务模板，用 @{{}} 标记可变参数
        params: 参数列表，每个元素是一个 dict

    示例:
        results = await extract_with_cache(
            "hn-scraper",
            "Get the top @{{count}} stories from Hacker News",
            [{"count": 5}, {"count": 10}, {"count": 20}],
        )
    """
    client = AsyncBrowserUse()
    workspace = await client.workspaces.create(name=workspace_name)
    results = []

    for i, p in enumerate(params):
        task = task_template
        for key, value in p.items():
            # 替换 @{{key}} → @{{value}}
            task = task.replace(f"@{{{{{key}}}}}", f"@{{{{{value}}}}}")

        result = await client.run(task, workspace_id=str(workspace.id))
        results.append(result.output)
        print(f"  [{i+1}/{len(params)}] params={p} → done (LLM: ${result.llm_cost_usd if hasattr(result, 'llm_cost_usd') else 'N/A'})")

    return results


# ============================================================
# 演示
# ============================================================

async def demo():
    """运行演示（需要有效的 API Key）。"""
    print("=" * 60)
    print("Browser Use Cloud — 结构化提取模板演示")
    print("=" * 60)

    # 演示 1：提取 Hacker News 文章
    print("\n📰 演示 1: 提取 Hacker News Top 5\n")
    try:
        result = await extract_articles(
            "Go to https://news.ycombinator.com and extract the top 5 posts with title, url, and points"
        )
        for i, a in enumerate(result.articles, 1):
            print(f"  {i}. {a.title}")
            print(f"     {a.points} pts | {a.url}")
        print(f"\n  ✅ 提取成功: {len(result.articles)} 篇文章")
    except Exception as e:
        print(f"  ❌ 提取失败: {e}")

    # 演示 2：提取产品信息
    print("\n🛒 演示 2: 提取产品价格\n")
    try:
        result = await extract_products(
            "Search amazon.com for 'mechanical keyboard' and extract the top 3 results with name and price"
        )
        for p in result.products:
            print(f"  {p.name}: ${p.price} ({p.availability or 'unknown'})")
        print(f"\n  ✅ 提取成功: {len(result.products)} 个产品")
    except Exception as e:
        print(f"  ❌ 提取失败: {e}")


if __name__ == "__main__":
    print("提示: 直接运行将执行演示任务（会消耗 API 额度）")
    print("建议: 复制此文件作为模板，修改 Schema 和 task 后使用\n")
    asyncio.run(demo())
