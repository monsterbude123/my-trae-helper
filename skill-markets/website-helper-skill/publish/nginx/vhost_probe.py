"""VR-010: detect which nginx vhost include path is active on the remote host.

Different distros / panels install nginx in wildly different layouts. Before
we try to ``include`` or symlink a config we have to know where the active
``http { include }`` actually reads from. Falling back to /etc/nginx/sites-enabled
on a Baota install silently drops the config (returns 404 with a 138B body) — see
distill-2026-08-20.md §4 for the live failure mode.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from publish.ssh.client import SshClient


@dataclass
class VhostTarget:
    """Where to drop the per-subdomain nginx config on the remote."""

    include_dir: str        # e.g. "/etc/nginx/sites-enabled"
    config_dir: str         # e.g. "/etc/nginx/sites-available"
    family: str             # canonical name: "debian-native" / "baota" / "cpanel" / ...
    notes: str = ""         # free-form hint for the operator

    @property
    def config_path(self) -> str:
        return f"{self.config_dir}/$subdomain.conf"

    @property
    def enabled_path(self) -> str:
        return f"{self.include_dir}/$subdomain.conf"

    def paths_for(self, subdomain: str) -> tuple[str, str, str]:
        """Return (config_file, enabled_symlink, include_dir) for a given subdomain."""
        return (
            f"{self.config_dir}/{subdomain}.conf",
            f"{self.include_dir}/{subdomain}.conf",
            self.include_dir,
        )


# Ordered best-guess probes. The first match wins.
_PROBES: list[tuple[str, str]] = [
    # (family, marker_path)
    ("baota",      "/www/server/panel/vhost/nginx"),          # Baota / 宝塔
    ("cpanel",     "/etc/nginx/conf.d"),                       # cPanel
    ("directadmin","/usr/local/directadmin/data/users"),       # DirectAdmin (parent dir)
    ("openlitespeed", "/usr/local/lsws/conf"),                 # OpenLiteSpeed
    ("debian-native", "/etc/nginx/sites-enabled"),             # Vanilla Debian/Ubuntu
    ("rhel-native",   "/etc/nginx/conf.d"),                    # RHEL/CentOS
]


def detect_vhost_target(ssh: SshClient) -> VhostTarget:
    """Probe the remote to find the right nginx vhost path.

    Preference order: Baota > cPanel > DirectAdmin > OpenLiteSpeed > Debian > RHEL.
    Falls back to ``/etc/nginx/conf.d`` (RHEL-style) when nothing matches, since
    that always exists on a working nginx install.

    Detection strategy per probe:
      1. Confirm the path exists with ``test -d``.
      2. For Baota etc. confirm ``include`` directive in nginx.conf.
      3. If marker present and not yet certain, return as the candidate.
    """
    # Read nginx.conf once and probe existence in parallel-ish manner
    rc, conf, _ = ssh.exec_command("cat /www/server/nginx/conf/nginx.conf 2>&1 | head -200")
    baota_conf = rc == 0 and conf.strip()

    rc2, conf2, _ = ssh.exec_command("cat /etc/nginx/nginx.conf 2>&1 | head -200")
    std_conf = rc2 == 0 and conf2.strip()

    # Iterate probes
    for family, path in _PROBES:
        rc, _, _ = ssh.exec_command(f"test -d {path}")
        if rc != 0:
            continue
        notes = ""
        if family == "baota" and baota_conf and "include /www/server/panel/vhost/nginx" in conf:
            notes = "Baota nginx — site MUST be placed here, not sites-enabled."
        return VhostTarget(
            include_dir=path,
            config_dir=path,                 # Baota/cPanel flat directories
            family=family,
            notes=notes,
        )

    # Vanilla Debian: sites-available + sites-enabled
    rc_a, _, _ = ssh.exec_command("test -d /etc/nginx/sites-available")
    if rc_a == 0:
        return VhostTarget(
            include_dir="/etc/nginx/sites-enabled",
            config_dir="/etc/nginx/sites-available",
            family="debian-native",
            notes=std_conf or "vanilla sites-enabled layout",
        )

    # Final fallback: conf.d (RHEL)
    return VhostTarget(
        include_dir="/etc/nginx/conf.d",
        config_dir="/etc/nginx/conf.d",
        family="rhel-native",
        notes="fallback conf.d — vanilla deployment",
    )


def detect_ssl_cert_path(ssh: SshClient, subdomain: str) -> Optional[str]:
    """Return the live cert directory on the remote, or None."""
    standard = f"/etc/letsencrypt/live/{subdomain}"
    rc, _, _ = ssh.exec_command(f"test -d {standard}")
    if rc == 0:
        return standard
    # Some Baota configs use /www/server/panel/letsencrypt paths
    alt = "/www/server/letsencrypt/live"
    rc, _, _ = ssh.exec_command(f"test -d {alt}")
    if rc == 0:
        return alt
    return None
