"""Layer 2 / ssl — SSL action returning :class:`Step`."""
from __future__ import annotations

from publish.certs.cert_manager import get_cert_status, request_cert
from publish.models import SshConfig
from publish.pipeline import Step
from publish.ssh.client import SshClient


def action_ssl_request_cert(
    ssh_config: SshConfig,
    domain: str,
    *,
    skip_if_already_valid: bool = True,
) -> Step:
    """Request a Let's Encrypt cert. Honors the existing cert if it's still valid.

    Returns ``skipped`` if ``skip_if_already_valid`` and the cert is currently
    valid — useful for idempotent re-runs that re-deploy configs.
    """
    try:
        with SshClient(ssh_config) as ssh:
            existing = get_cert_status(ssh, domain)
            if (
                skip_if_already_valid
                and existing.status in ("valid", "expiring")
                and existing.days_remaining > 7
            ):
                return Step(
                    name=f"ssl:{domain}",
                    status="skipped",
                    output=f"valid until {existing.not_after} "
                           f"({existing.days_remaining}d remaining)",
                )
            output = request_cert(ssh, domain)
            cert_info = get_cert_status(ssh, domain)
        return Step(
            name=f"ssl:{domain}",
            status="ok",
            output=f"valid until {cert_info.not_after}",
        )
    except Exception as exc:  # noqa: BLE001
        return Step(
            name=f"ssl:{domain}",
            status="failed",
            error=f"{type(exc).__name__}: {exc}",
        )
