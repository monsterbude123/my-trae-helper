"""Layer 2 / nginx — nginx deploy action returning :class:`Step`.

Dispatches to ``deploy_webroot`` (static) or ``deploy_proxy`` (reverse) based
on which arguments are provided. Owns the SSH connection lifecycle so the
caller just hands over config.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from publish.models import SshConfig
from publish.nginx.deploy import deploy_webroot, deploy_proxy
from publish.nginx.vhost_probe import detect_vhost_target
from publish.pipeline import Step
from publish.ssh.client import SshClient


def action_nginx_deploy(
    ssh_config: SshConfig,
    domain: str,
    *,
    webroot: Optional[Path] = None,
    upstream: Optional[str] = None,
    with_ssl: bool = False,
) -> Step:
    """Mode is inferred: ``webroot`` → static; ``upstream`` → reverse-proxy.

    Returns a Step with `output` containing the detected vhost family for
    audit (e.g. ``"family=baota include=/www/server/panel/vhost/nginx"``).
    """
    if webroot is None and upstream is None:
        return Step(
            name=f"nginx:{domain}",
            status="failed",
            error="either webroot or upstream must be provided",
        )
    if webroot is not None and upstream is not None:
        return Step(
            name=f"nginx:{domain}",
            status="failed",
            error="webroot and upstream are mutually exclusive",
        )
    mode = "proxy" if upstream else "static"
    try:
        with SshClient(ssh_config) as ssh:
            vhost_note = ""
            if upstream:
                target = detect_vhost_target(ssh)
                vhost_note = f"family={target.family} include={target.include_dir}"
                deploy_proxy(ssh, domain, upstream, with_ssl=with_ssl)
            else:
                deploy_webroot(ssh, domain, Path(webroot), with_ssl=with_ssl)  # type: ignore[arg-type]
        return Step(
            name=f"nginx:{domain}",
            status="ok",
            output=f"mode={mode} {vhost_note}".strip(),
        )
    except Exception as exc:  # noqa: BLE001
        return Step(
            name=f"nginx:{domain}",
            status="failed",
            error=f"{type(exc).__name__}: {exc}",
        )
