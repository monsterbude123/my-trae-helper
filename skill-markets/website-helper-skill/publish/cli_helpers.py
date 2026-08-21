"""Layer 4 helpers — pure functions used by typer commands but not in actions.

Things here are CLI-shape utilities (formatting, dispatch tables) that don't
fit the Pipeline/Action layer. They stay separate from ``cli.py`` to keep the
router file readable.

This module is intentionally thin (~40 lines).
"""
from __future__ import annotations

from publish.dns.base import (
    AbstractDnsProvider,
    AliyunProvider,
    CloudflareProvider,
    DnspodProvider,
)
from publish.models import DnsConfig, DnsProvider


def get_dns_provider(config: DnsConfig) -> AbstractDnsProvider:
    """Dispatch table from DnsConfig to concrete provider instance.

    Was a private function ``_get_dns_provider`` inside cli.py — promoted
    here so actions/ can also resolve providers in tests.
    """
    if config.provider == DnsProvider.CLOUDFLARE:
        if not config.zone_id:
            raise ValueError("Cloudflare 需要 zone_id")
        return CloudflareProvider(api_token=config.api_token, zone_id=config.zone_id)
    if config.provider == DnsProvider.ALIYUN:
        return AliyunProvider(
            access_key_id=config.access_key_id or "",
            access_key_secret=config.access_key_secret or "",
            domain=config.domain or "",
        )
    if config.provider == DnsProvider.DNSPOD:
        return DnspodProvider(
            secret_id=config.secret_id or "",
            secret_key=config.secret_key or "",
            domain=config.domain or "",
        )
    raise ValueError(f"未知 DNS 提供商: {config.provider}")
