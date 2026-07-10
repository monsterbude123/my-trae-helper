#!/usr/bin/env python3
"""Browser Use Cloud — 批量会话管理器

并发运行多个 session，收集结果。支持 asyncio.gather 并行模式。

用法:
    python batch_sessions.py --tasks tasks.json            # 从 JSON 文件加载任务
    python batch_sessions.py --tasks "task1||task2||task3"  # 用 || 分隔多个任务
    python batch_sessions.py --concurrency 5               # 最大并发数（默认 3）

tasks.json 格式:
[
    {"task": "Find the top HN story", "model": "claude-sonnet-4.6"},
    {"task": "Get Bitcoin price from coinbase.com"},
    {"task": "Search amazon for best laptops under $500"}
]

依赖:
    pip install browser-use-sdk
    export BROWSER_USE_API_KEY=bu_your_key
"""

import asyncio
import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TaskResult:
    task: str
    status: str  # success / error / timeout
    output: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    session_id: Optional[str] = None
    model: Optional[str] = None


async def run_single_task(client, task_spec: dict, timeout: int = 300) -> TaskResult:
    """运行单个任务并返回结果。"""
    task_desc = task_spec.get("task", "")
    model = task_spec.get("model", "claude-sonnet-4.6")
    start = time.time()

    try:
        result = await asyncio.wait_for(
            client.run(task_desc, model=model),
            timeout=timeout,
        )
        elapsed = time.time() - start
        return TaskResult(
            task=task_desc,
            status="success",
            output=str(result.output)[:500],
            duration_seconds=elapsed,
            session_id=result.id if hasattr(result, 'id') else None,
            model=model,
        )
    except asyncio.TimeoutError:
        elapsed = time.time() - start
        return TaskResult(
            task=task_desc, status="timeout",
            error=f"任务超时（{timeout}s）", duration_seconds=elapsed,
        )
    except Exception as e:
        elapsed = time.time() - start
        return TaskResult(
            task=task_desc, status="error",
            error=str(e), duration_seconds=elapsed,
        )


async def run_batch(
    tasks: list[dict],
    concurrency: int = 3,
    timeout: int = 300,
) -> list[TaskResult]:
    """并发运行批量任务。

    Args:
        tasks: 任务规范列表
        concurrency: 最大并发数
        timeout: 单个任务超时时间（秒）

    Returns:
        按输入顺序排列的结果列表
    """
    from browser_use_sdk.v3 import AsyncBrowserUse

    client = AsyncBrowserUse()
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded_run(task_spec):
        async with semaphore:
            idx = task_spec.get("_index", 0)
            total = len(tasks)
            print(f"[{idx+1}/{total}] 开始: {task_spec['task'][:80]}...")
            result = await run_single_task(client, task_spec, timeout)
            icon = {"success": "✅", "error": "❌", "timeout": "⏱️"}.get(result.status, "❓")
            print(f"  {icon} [{idx+1}/{total}] {result.status} ({result.duration_seconds:.1f}s)")
            if result.error:
                print(f"     错误: {result.error[:200]}")
            return result

    # 添加索引以保持顺序
    for i, t in enumerate(tasks):
        t["_index"] = i

    print(f"\n🚀 启动 {len(tasks)} 个任务（并发: {concurrency}）\n")
    start = time.time()

    results = await asyncio.gather(*[bounded_run(t) for t in tasks])

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"批量完成: {len(tasks)} 任务 / {elapsed:.1f}s / 并发 {concurrency}")
    success = sum(1 for r in results if r.status == "success")
    print(f"成功: {success}/{len(tasks)}")

    return results


def load_tasks(args) -> list[dict]:
    """从命令行参数加载任务列表。"""
    if args.tasks and os.path.isfile(args.tasks):
        # JSON 文件
        with open(args.tasks, "r", encoding="utf-8") as f:
            tasks = json.load(f)
        if not isinstance(tasks, list):
            print("❌ JSON 文件应为任务数组")
            sys.exit(1)
        return tasks
    elif args.tasks:
        # || 分隔的字符串
        task_strings = [t.strip() for t in args.tasks.split("||") if t.strip()]
        return [{"task": t} for t in task_strings]
    else:
        # 默认演示任务
        return [
            {"task": "Find the top story on Hacker News today", "model": "claude-sonnet-4.6"},
            {"task": "Go to wikipedia.org and tell me the featured article title"},
            {"task": "What is the current featured article on techcrunch.com?"},
        ]


def save_results(results: list[TaskResult], output_path: str = "batch_results.json"):
    """保存结果到 JSON 文件。"""
    data = [
        {
            "task": r.task[:200],
            "status": r.status,
            "output": r.output,
            "error": r.error,
            "duration_seconds": round(r.duration_seconds, 1),
            "session_id": r.session_id,
            "model": r.model,
        }
        for r in results
    ]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"📄 结果已保存到 {output_path}")


async def main():
    parser = argparse.ArgumentParser(description="Browser Use Cloud 批量会话管理器")
    parser.add_argument("--tasks", type=str, help="JSON 文件路径 或 || 分隔的任务字符串")
    parser.add_argument("--concurrency", "-c", type=int, default=3, help="最大并发数（默认 3）")
    parser.add_argument("--timeout", "-t", type=int, default=300, help="单个任务超时秒数（默认 300）")
    parser.add_argument("--output", "-o", type=str, default="batch_results.json", help="结果输出文件")
    args = parser.parse_args()

    tasks = load_tasks(args)
    results = await run_batch(tasks, concurrency=args.concurrency, timeout=args.timeout)
    save_results(results, args.output)


if __name__ == "__main__":
    asyncio.run(main())
