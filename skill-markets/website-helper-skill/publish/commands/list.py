"""Layer 4 / list — ``publish list`` typer command."""
from __future__ import annotations

import typer

from publish.cockpit.logger import list_published


def list_published_cmd() -> None:
    """查看所有已发布子域名."""
    records = list_published()
    if not records:
        typer.echo("暂无发布记录")
        return
    typer.echo("\n📋 已发布子域名:")
    typer.echo("| 子域名 | 最后部署时间 | 操作 | 状态 |")
    typer.echo("|--------|-------------|------|------|")
    seen = set()
    for r in records:
        if r.subdomain in seen:
            continue
        seen.add(r.subdomain)
        status_icon = {"success": "✅", "partial": "⚠️", "failed": "❌"}
        icon = status_icon.get(r.status.value, "?")
        typer.echo(
            f"| {r.subdomain} | {r.timestamp} | {r.operation.value} | {icon} {r.status.value} |"
        )
    typer.echo("")
