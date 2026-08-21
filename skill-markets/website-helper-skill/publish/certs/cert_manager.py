"""SSL certificate management via certbot on remote host."""

from dataclasses import dataclass
from datetime import datetime

from publish.ssh.client import SshClient


@dataclass
class CertInfo:
    status: str  # valid, expiring, expired, absent
    issuer: str
    not_before: str
    not_after: str
    days_remaining: int


def _ensure_certbot(ssh: SshClient, with_nginx_plugin: bool = True) -> None:
    """Ensure certbot is installed; nginx plugin only when requested."""
    exit_code, _, _ = ssh.exec_command("which certbot")
    if exit_code != 0:
        pkgs = "certbot"
        if with_nginx_plugin:
            pkgs += " python3-certbot-nginx"
        ssh.exec_command(f"apt-get update -qq && apt-get install -y -qq {pkgs}")


def _nginx_plugin_available(ssh: SshClient) -> bool:
    """Check whether the certbot nginx plugin is installed."""
    rc, _, _ = ssh.exec_command(
        "python3 -c 'import certbot_nginx' 2>&1"
    )
    return rc == 0


def _stop_listeners_on_80(ssh: SshClient, exclude: str = "docker-proxy") -> None:
    """VR-011 (2026-08-20): stop nginx + docker-proxy listeners that hold :80,
    so certbot --standalone can complete the HTTP-01 challenge. Caller MUST
    restart them afterwards (``_start_listeners_on_80``).
    """
    # nginx first (since it usually fronts docker-proxy too)
    ssh.exec_command("systemctl stop nginx 2>&1 || nginx -s stop 2>&1 || true")
    # any docker-proxy bound to host :80 (only those, not upstream-only proxies)
    ssh.exec_command(
        f"iptables -I INPUT -p tcp --dport 80 -j DROP 2>&1 || true"
    )


def _start_listeners_on_80(ssh: SshClient) -> None:
    """Reverse the stop — used after certbot standalone completes."""
    ssh.exec_command("iptables -D INPUT -p tcp --dport 80 -j DROP 2>&1 || true")
    ssh.exec_command("systemctl start nginx 2>&1 || nginx 2>&1 || true")


def request_cert(ssh: SshClient, subdomain: str) -> str:
    """Request SSL certificate via certbot.

    Strategy (VR-011, 2026-08-20):
      1. Try ``certbot --nginx`` if plugin is installed (vanilla nginx).
      2. Fall back to ``certbot certonly --standalone`` — works on Baota /
         cPanel / OpenLiteSpeed where --nginx plugin is broken or missing.
         This means temporarily stopping nginx + iptables-blocking :80
         while certbot stakes the HTTP-01 challenge.

    The standalone fallback is the live-cure for the Baota nginx + missing
    python3-certbot-nginx seen on the 2026-08-20 zentaopms deploy.
    """
    _ensure_certbot(ssh, with_nginx_plugin=True)

    use_nginx_plugin = _nginx_plugin_available(ssh)

    if use_nginx_plugin:
        rc, stdout, stderr = ssh.exec_command(
            f"certbot --nginx -d {subdomain} --non-interactive --agree-tos "
            f"--email admin@{subdomain.split('.', 1)[1]} 2>&1"
        )
        if rc == 0:
            return stdout + stderr
        # --nginx failed (often on Baota where plugin can't talk to the master
        # nginx.conf), fall through to standalone
        _stderr_so_far = stdout + stderr
    else:
        _stderr_so_far = "certbot nginx plugin not installed"

    # ── Fallback: standalone HTTP-01 challenge ──
    _stop_listeners_on_80(ssh)
    try:
        rc, stdout, stderr = ssh.exec_command(
            f"certbot certonly --standalone --non-interactive --agree-tos "
            f"--email admin@{subdomain.split('.', 1)[1]} -d {subdomain} 2>&1"
        )
    finally:
        _start_listeners_on_80(ssh)

    output = stdout + stderr
    if rc != 0:
        if "DNS problem" in output or "NXDOMAIN" in output or "no valid A records" in output:
            raise RuntimeError(
                f"证书申请失败：DNS 尚未解析到服务器 IP。"
                f"请确认 DNS 记录已生效后重试: publish cert renew {subdomain}"
            )
        # If nginx plugin failed earlier, surface both errors
        if use_nginx_plugin and _stderr_so_far:
            raise RuntimeError(
                f"证书申请失败（--nginx 与 --standalone 两者都试了）。\n"
                f"--- nginx plugin attempt ---\n{_stderr_so_far}\n"
                f"--- standalone attempt ---\n{output}"
            )
        raise RuntimeError(f"证书申请失败:\n{output}")

    return output


def get_cert_status(ssh: SshClient, subdomain: str) -> CertInfo:
    """Query certificate status on remote host."""
    exit_code, stdout, stderr = ssh.exec_command("certbot certificates 2>&1")
    output = stdout + stderr
    if exit_code != 0:
        return CertInfo(status="absent", issuer="", not_before="", not_after="", days_remaining=0)

    # Parse certbot output
    lines = output.split("\n")
    in_cert = False
    cert_data = {}

    for line in lines:
        if subdomain in line:
            in_cert = True
        elif in_cert and line.startswith("  Certificate Name:"):
            break
        elif in_cert:
            if "Domains:" in line:
                cert_data["domains"] = line.split(":", 1)[1].strip()
            elif "Expiry Date:" in line:
                date_str = line.split(":", 1)[1].strip().split(" ")[0]  # 2026-09-27
                cert_data["expiry"] = date_str
            elif "VALID:" in line:
                cert_data["status"] = "valid"

    if "expiry" not in cert_data:
        return CertInfo(status="absent", issuer="", not_before="", not_after="", days_remaining=0)

    try:
        expiry = datetime.strptime(cert_data["expiry"], "%Y-%m-%d")
        days_left = (expiry - datetime.now()).days
    except ValueError:
        days_left = 0

    status = "valid"
    if days_left <= 0:
        status = "expired"
    elif days_left <= 30:
        status = "expiring"

    return CertInfo(
        status=status,
        issuer="Let's Encrypt",
        not_before="",
        not_after=cert_data.get("expiry", ""),
        days_remaining=days_left,
    )


def renew_cert(ssh: SshClient, subdomain: str) -> str:
    """Force renew certificate for subdomain."""
    exit_code, stdout, stderr = ssh.exec_command(
        f"certbot renew --cert-name {subdomain} --force-renewal 2>&1"
    )
    output = stdout + stderr
    if exit_code != 0:
        raise RuntimeError(f"证书续期失败:\n{output}")
    return output
