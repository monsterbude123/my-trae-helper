"""Layer 4 / config — ``publish config {init,dns,ssh}`` typer commands."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from publish.config.store import (
    ENV_FILE,
    _get_env_value,
    load_dns_config,
    load_ssh_config,
    save_dns_config,
    save_ssh_config,
)
from publish.models import DnsConfig, DnsProvider, SshConfig
from publish.utils.validators import validate_dns_provider


def config_init() -> None:
    """从当前目录的 .env 文件自动生成 DNS + SSH 配置（无需交互）."""
    if not ENV_FILE.exists():
        typer.echo(
            f"❌ 未找到 {ENV_FILE}，请先复制 .env.example 为 .env 并填值",
            err=True,
        )
        raise typer.Exit(code=1)
    typer.echo(f"📄 读取 {ENV_FILE} ...")

    provider = _get_env_value("DNS_PROVIDER")
    if not provider:
        typer.echo("❌ .env 缺少 DNS_PROVIDER", err=True)
        raise typer.Exit(code=1)
    try:
        provider_enum = validate_dns_provider(provider)
    except ValueError as e:
        typer.echo(f"❌ {e}", err=True)
        raise typer.Exit(code=1)

    if provider_enum == DnsProvider.ALIYUN:
        dns_cfg = DnsConfig(
            provider=provider_enum, api_token="",
            domain=_get_env_value("ALIYUN_DOMAIN") or "",
            access_key_id=_get_env_value("ALIYUN_ACCESS_KEY_ID") or "",
            access_key_secret=_get_env_value("ALIYUN_ACCESS_KEY_SECRET") or "",
        )
        if not dns_cfg.domain or not dns_cfg.access_key_id or not dns_cfg.access_key_secret:
            typer.echo("❌ 阿里云需要 ALIYUN_DOMAIN / ALIYUN_ACCESS_KEY_ID / ALIYUN_ACCESS_KEY_SECRET", err=True)
            raise typer.Exit(code=1)
        save_dns_config(dns_cfg)
    elif provider_enum == DnsProvider.CLOUDFLARE:
        dns_cfg = DnsConfig(
            provider=provider_enum,
            api_token=_get_env_value("CLOUDFLARE_API_TOKEN") or "",
            zone_id=_get_env_value("CLOUDFLARE_ZONE_ID") or "",
        )
        if not dns_cfg.api_token or not dns_cfg.zone_id:
            typer.echo("❌ Cloudflare 需要 CLOUDFLARE_API_TOKEN / CLOUDFLARE_ZONE_ID", err=True)
            raise typer.Exit(code=1)
        save_dns_config(dns_cfg)
    elif provider_enum == DnsProvider.DNSPOD:
        dns_cfg = DnsConfig(
            provider=provider_enum, api_token="",
            domain=_get_env_value("DNSPOD_DOMAIN") or "",
            secret_id=_get_env_value("DNSPOD_SECRET_ID") or "",
            secret_key=_get_env_value("DNSPOD_SECRET_KEY") or "",
        )
        if not dns_cfg.domain or not dns_cfg.secret_id or not dns_cfg.secret_key:
            typer.echo("❌ DNSPod 需要 DNSPOD_DOMAIN / DNSPOD_SECRET_ID / DNSPOD_SECRET_KEY", err=True)
            raise typer.Exit(code=1)
        save_dns_config(dns_cfg)

    typer.echo(f"✅ DNS: {provider} 已配置")

    host = _get_env_value("SSH_HOST")
    user = _get_env_value("SSH_USER")
    if host and user:
        key_path = _get_env_value("SSH_KEY_PATH")
        ssh_cfg = SshConfig(
            host=host, user=user,
            port=int(_get_env_value("SSH_PORT") or "22"),
            key_path=Path(key_path) if key_path else None,
            password=_get_env_value("SSH_PASSWORD"),
        )
        save_ssh_config(ssh_cfg)
        typer.echo(f"✅ SSH: {user}@{host}")
    else:
        typer.echo("ℹ️  .env 未配置 SSH_HOST/SSH_USER，跳过 SSH 配置")

    typer.echo("\n🎉 初始化完成！可以运行:")
    typer.echo("  publish deploy app -d app.yourdomain.com -w ./dist")
    typer.echo("  publish deploy app -d app.yourdomain.com --proxy --upstream URL")


def config_dns(provider: str) -> None:
    """交互式配置 DNS 提供商凭据."""
    provider_enum = validate_dns_provider(provider)
    print(f"\n🔧 配置 {provider_enum.value} DNS\n")

    if provider_enum == DnsProvider.CLOUDFLARE:
        print("获取 Cloudflare API Token:")
        print("  1. 登录 https://dash.cloudflare.com")
        print("  2. 右上角头像 → My Profile → API Tokens")
        print('  3. Create Token → "Edit zone DNS" 模板')
        print("  4. Zone Resources 选择你的域名")
        print("  5. 复制生成的 Token\n")
        print("获取 Zone ID:")
        print("  1. 进入域名 Overview 页面")
        print("  2. 右侧 API 段复制 Zone ID\n")
        api_token = typer.prompt("API Token", hide_input=True)
        zone_id = typer.prompt("Zone ID")
        config = DnsConfig(provider=provider_enum, api_token=api_token, zone_id=zone_id)
    elif provider_enum == DnsProvider.ALIYUN:
        print("获取阿里云 AccessKey:")
        print("  1. 登录 https://ram.console.aliyun.com")
        print("  2. 用户 → 创建用户 → 编程访问")
        print("  3. 添加 AliyunDNSFullAccess 权限")
        print("  4. 复制 AccessKey ID 和 Secret\n")
        access_key_id = typer.prompt("AccessKey ID", hide_input=True)
        access_key_secret = typer.prompt("AccessKey Secret", hide_input=True)
        domain = typer.prompt("域名（如 example.com）")
        config = DnsConfig(
            provider=provider_enum, api_token="", domain=domain,  # scan-ignore-line — DnsConfig dataclass 必填字段占位
            access_key_id=access_key_id, access_key_secret=access_key_secret,
        )
    elif provider_enum == DnsProvider.DNSPOD:
        print("获取 DNSPod SecretId/SecretKey:")
        print("  1. 登录 https://console.dnspod.cn")
        print("  2. 账号中心 → API 密钥管理")
        print("  3. 创建密钥 → 复制 SecretId 和 SecretKey\n")
        secret_id = typer.prompt("SecretId", hide_input=True)
        secret_key = typer.prompt("SecretKey", hide_input=True)
        domain = typer.prompt("域名（如 example.com）")
        config = DnsConfig(
            provider=provider_enum, api_token="", domain=domain,  # scan-ignore-line — DnsConfig dataclass 必填字段占位
            secret_id=secret_id, secret_key=secret_key,
        )
    save_dns_config(config)
    print(f"✅ DNS 配置已保存 ({provider_enum.value})")


def config_ssh(host: str, user: str, port: int, key: Optional[Path]) -> None:
    """交互式/参数式配置 SSH."""
    config = SshConfig(host=host, user=user, port=port, key_path=key)
    if not key:
        password = typer.prompt(
            "SSH 密码（留空使用密钥）", default="",
            hide_input=True, show_default=False,
        )
        if password:
            config.password = password
    save_ssh_config(config)
    print(f"\n✅ SSH 配置已保存")
    print(f"  主机: {host}")
    print(f"  用户: {user}")
    print(f"  认证: {'密钥' if key else '密码'}")
