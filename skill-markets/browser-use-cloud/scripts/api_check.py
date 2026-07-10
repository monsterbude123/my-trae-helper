#!/usr/bin/env python3
"""Browser Use Cloud — API 自检脚本

检查 API Key 有效性、账户余额、最近 session 列表。

用法:
    python api_check.py                        # 检查 API Key + 余额 + 最近 sessions
    python api_check.py --sessions 20          # 列出最近 20 个 sessions
    python api_check.py --verbose              # 详细输出

依赖:
    pip install browser-use-sdk
    export BROWSER_USE_API_KEY=bu_your_key
"""

import asyncio
import argparse
import os
import sys
from datetime import datetime


async def check_api() -> dict:
    """运行所有 API 自检并返回结果。"""
    from browser_use_sdk.v3 import AsyncBrowserUse

    results = {}

    # 检查 API Key
    api_key = os.environ.get("BROWSER_USE_API_KEY", "")
    if not api_key:
        print("❌ BROWSER_USE_API_KEY 未设置")
        sys.exit(1)
    if not api_key.startswith("bu_"):
        print("⚠️  API Key 不以 'bu_' 开头，可能无效")
    else:
        key_preview = api_key[:20] + "..." if len(api_key) > 20 else api_key
        print(f"✅ API Key: {key_preview}")
    results["api_key_configured"] = True

    client = AsyncBrowserUse()

    # 检查连接（列出 sessions 作为连通性测试）
    print("\n📡 检查 API 连通性...")
    try:
        sessions_response = await client.sessions.list(limit=5)
        print(f"✅ API 连通正常（最近 {len(sessions_response.items) if hasattr(sessions_response, 'items') else '?'} 个 sessions）")
        results["api_connected"] = True
    except Exception as e:
        print(f"❌ API 连接失败: {e}")
        results["api_connected"] = False
        return results

    # 检查 billing（如果可用）
    print("\n💰 检查账户信息...")
    try:
        billing = await client.billing.get()
        if hasattr(billing, 'balance') and billing.balance is not None:
            print(f"   余额: ${billing.balance:.2f}")
            results["balance"] = billing.balance
        if hasattr(billing, 'usage_this_month') and billing.usage_this_month is not None:
            print(f"   本月用量: ${billing.usage_this_month:.2f}")
            results["usage_this_month"] = billing.usage_this_month
        results["billing_available"] = True
    except Exception as e:
        print(f"⚠️  无法获取账单信息: {e}")
        results["billing_available"] = False

    # 列出 profiles
    print("\n👤 检查 Profiles...")
    try:
        profiles_response = await client.profiles.list()
        if hasattr(profiles_response, 'items'):
            count = len(profiles_response.items)
            print(f"   共 {count} 个 profiles")
            results["profile_count"] = count
        results["profiles_available"] = True
    except Exception as e:
        print(f"⚠️  无法获取 profiles: {e}")
        results["profiles_available"] = False

    return results


async def list_recent_sessions(limit: int = 10, verbose: bool = False):
    """列出最近的 sessions。"""
    from browser_use_sdk.v3 import AsyncBrowserUse

    client = AsyncBrowserUse()
    print(f"\n📋 最近 {limit} 个 Sessions:\n")
    print(f"{'Session ID':<40} {'Status':<12} {'Created':<20}")
    print("-" * 72)

    try:
        response = await client.sessions.list(limit=limit)
        items = response.items if hasattr(response, 'items') else []
        if not items:
            print("   (无 sessions)")
            return

        for s in items:
            sid = s.id if hasattr(s, 'id') else str(s)
            status = s.status.value if hasattr(s, 'status') and hasattr(s.status, 'value') else str(s.status)
            created = str(s.created_at)[:19] if hasattr(s, 'created_at') else "N/A"
            print(f"{sid:<40} {status:<12} {created:<20}")

            if verbose and hasattr(s, 'output'):
                output = str(s.output)[:200]
                print(f"  Output: {output}")
                if hasattr(s, 'task'):
                    print(f"  Task: {s.task[:120]}")
    except Exception as e:
        print(f"❌ 获取 sessions 失败: {e}")


async def main():
    parser = argparse.ArgumentParser(description="Browser Use Cloud API 自检工具")
    parser.add_argument("--sessions", type=int, default=10, help="列出最近 N 个 sessions（默认 10）")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()

    print("=" * 60)
    print("Browser Use Cloud — API 自检")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = await check_api()
    await list_recent_sessions(limit=args.sessions, verbose=args.verbose)

    # 汇总
    print("\n" + "=" * 60)
    print("自检汇总")
    print("=" * 60)
    all_ok = all(v for v in results.values() if isinstance(v, bool))
    if all_ok:
        print("✅ 所有检查通过")
    else:
        failed = [k for k, v in results.items() if isinstance(v, bool) and not v]
        print(f"⚠️  以下检查未通过: {', '.join(failed)}")
    print(f"完整结果: {results}")


if __name__ == "__main__":
    asyncio.run(main())
