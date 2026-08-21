"""Layer 2 / dns — DNS action returning :class:`Step`."""
from __future__ import annotations

from typing import Callable

from publish.dns.base import AbstractDnsProvider
from publish.pipeline import Step


def action_dns_create_record(
    domain: str,
    server_ip: str,
    *,
    dns_provider: AbstractDnsProvider,
    force: bool = False,
) -> Step:
    """Create an A record. Existing-record-without-force → skipped (not failed).

    Returns a :class:`Step` (never raises) so the pipeline keeps moving.
    """
    try:
        dns_provider.create_record(domain, server_ip)
        return Step(name=f"dns:{domain}", status="ok", output=f"A → {server_ip}")
    except ValueError as exc:
        if "已存在" in str(exc) and not force:
            return Step(
                name=f"dns:{domain}",
                status="skipped",
                output=str(exc),
                error=str(exc),
            )
        return Step(
            name=f"dns:{domain}",
            status="failed",
            error=f"{type(exc).__name__}: {exc}",
        )
    except Exception as exc:  # noqa: BLE001
        return Step(
            name=f"dns:{domain}",
            status="failed",
            error=f"{type(exc).__name__}: {exc}",
        )
