"""Layer 4 / cert — ``publish cert {status,renew}`` typer commands."""
from __future__ import annotations

import typer

from publish.certs.cert_manager import get_cert_status, renew_cert
from publish.cockpit.logger import log_publish
from publish.config.store import load_ssh_config
from publish.models import PublishOperation, PublishStatus
from publish.ssh.client import SshClient, SshConnectionError
from publish.utils.validators import validate_subdomain


def cert_status(subdomain: str) -> None:
    """查看 SSL 证书状态."""
    subdomain = validate_subdomain(subdomain)
    ssh_config = load_ssh_config()
    if not ssh_config:
        typer.echo("❌ 缺少 SSH 配置", err=True)
        raise typer.Exit(code=1)

    try:
        with SshClient(ssh_config) as ssh:
            info = get_cert_status(ssh, subdomain)
    except SshConnectionError as e:
        typer.echo(f"❌ SSH 连接失败: {e}", err=True)
        raise typer.Exit(code=1)

    if info.status == "absent":
        typer.echo(f"🔒 {subdomain}\n  状态: 无证书")
        return

    status_label = {"valid": "✅ 有效", "expiring": "⚠️ 即将过期", "expired": "❌ 已过期"}
    typer.echo(f"🔒 {subdomain}")
    typer.echo(f"  状态: {status_label.get(info.status, info.status)}")
    typer.echo(f"  颁发者: {info.issuer}")
    typer.echo(f"  有效期至: {info.not_after}")
    typer.echo(f"  剩余: {info.days_remaining} 天")
    typer.echo(f"  自动续期: ✅ 已启用")


def cert_renew(subdomain: str) -> None:
    """强制续期 SSL 证书."""
    subdomain = validate_subdomain(subdomain)
    ssh_config = load_ssh_config()
    if not ssh_config:
        typer.echo("❌ 缺少 SSH 配置", err=True)
        raise typer.Exit(code=1)

    try:
        with SshClient(ssh_config) as ssh:
            renew_cert(ssh, subdomain)
            info = get_cert_status(ssh, subdomain)
        typer.echo(f"♻️  证书已续期: {subdomain}")
        typer.echo(f"  新有效期至: {info.not_after}")
        log_publish(subdomain, PublishOperation.RENEW, PublishStatus.SUCCESS)
    except SshConnectionError as e:
        typer.echo(f"❌ SSH 连接失败: {e}", err=True)
        raise typer.Exit(code=1)
    except RuntimeError as e:
        typer.echo(f"❌ 续期失败: {e}", err=True)
        raise typer.Exit(code=1)
