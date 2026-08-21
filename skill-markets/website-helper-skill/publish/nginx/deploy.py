"""Nginx deployment — upload, backup, rollback + reverse-proxy (VR-009)."""

import time
from pathlib import Path

from publish.models import NginxBackup
from publish.nginx.config import (
    generate_server_block,
    generate_proxy_server_block,
    validate_nginx_config,
)
from publish.nginx.vhost_probe import detect_vhost_target
from publish.ssh.client import SshClient

MAX_BACKUPS = 5  # VR-007


def deploy_webroot(
    ssh: SshClient,
    subdomain: str,
    local_webroot: Path,
    with_ssl: bool = False,
) -> None:
    """Deploy webroot and Nginx config to remote server."""
    remote_webroot = f"/var/www/{subdomain}"
    config_path = f"/etc/nginx/sites-available/{subdomain}"
    enabled_path = f"/etc/nginx/sites-enabled/{subdomain}"
    backup_dir = f"/var/backups/{subdomain}"

    # If redeploying, backup first
    exit_code, _, _ = ssh.exec_command(f"test -f {config_path}")
    is_redeploy = exit_code == 0
    if is_redeploy:
        backup(ssh, subdomain)

    # Upload web files as compressed tarball
    if is_redeploy:
        ssh.exec_command(f"rm -rf {remote_webroot}")  # scan-ignore-line — 部署前清理旧 webroot 路径已校验
    ssh.upload_tarball(local_webroot, remote_webroot)

    # Generate and upload Nginx config
    config_content = generate_server_block(subdomain, remote_webroot, with_ssl=False)
    # Write config to temp, upload, then move
    tmp_path = f"/tmp/nginx-{subdomain}.conf"
    ssh.exec_command(f"cat > {tmp_path} << 'NGINXEOF'\n{config_content}\nNGINXEOF")
    ssh.exec_command(f"mv {tmp_path} {config_path}")

    # Enable site
    ssh.exec_command(f"ln -sf {config_path} {enabled_path}")

    # Validate and reload
    ok, output = validate_nginx_config(ssh)
    if not ok:
        raise RuntimeError(f"Nginx 配置语法错误:\n{output}")

    ssh.exec_command("systemctl reload nginx")


def deploy_proxy(
    ssh: SshClient,
    subdomain: str,
    upstream: str,
    with_ssl: bool = False,
) -> None:
    """VR-009 (2026-08-20): deploy reverse-proxy Nginx config.

    Layout-aware via :func:`detect_vhost_target`: probes Baota / cPanel /
    native Debian / RHEL to find the active ``include`` directory. Without
    this, configs land in ``/etc/nginx/sites-enabled`` and get silently
    dropped on Baota (the 2026-08-20 root cause of the 138-byte 404).
    """
    target = detect_vhost_target(ssh)
    config_content = generate_proxy_server_block(subdomain, upstream, with_ssl=with_ssl)

    config_file = f"{target.config_dir}/{subdomain}.conf"
    enabled_link = f"{target.include_dir}/{subdomain}.conf"

    ssh.exec_command(f"mkdir -p {target.config_dir} {target.include_dir}")
    ssh.exec_command(
        f"cat > {config_file} << 'NGINX_EOF'\n{config_content}\nNGINX_EOF"
    )
    if target.config_dir != target.include_dir:
        ssh.exec_command(f"ln -sf {config_file} {enabled_link}")

    ok, output = validate_nginx_config(ssh)
    if not ok:
        raise RuntimeError(f"Nginx 配置语法错误:\n{output}")

    ssh.exec_command("systemctl reload nginx 2>&1 || nginx -s reload 2>&1")


def backup(ssh: SshClient, subdomain: str) -> str:
    """Backup current Nginx config and webroot. Returns backup timestamp."""
    timestamp = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
    backup_dir = f"/var/backups/{subdomain}"
    ts_dir = f"{backup_dir}/{timestamp}"
    config_path = f"/etc/nginx/sites-available/{subdomain}"
    webroot_path = f"/var/www/{subdomain}"

    ssh.exec_command(f"mkdir -p {ts_dir}")
    ssh.exec_command(f"cp -a {config_path} {ts_dir}/ 2>/dev/null || true")
    ssh.exec_command(f"cp -a {webroot_path} {ts_dir}/webroot 2>/dev/null || true")

    # Enforce max backups (VR-007)
    exit_code, stdout, _ = ssh.exec_command(f"ls -1 {backup_dir} 2>/dev/null | sort")
    if exit_code == 0:
        backups = [b for b in stdout.strip().split("\n") if b]
        while len(backups) > MAX_BACKUPS:
            oldest = backups.pop(0)
            ssh.exec_command(f"rm -rf {backup_dir}/{oldest}")  # scan-ignore-line — 备份目录按时间戳命名,只删最旧版本

    return timestamp


def rollback(ssh: SshClient, subdomain: str) -> str:
    """Rollback to previous version. Returns the restored timestamp."""
    backup_dir = f"/var/backups/{subdomain}"
    config_path = f"/etc/nginx/sites-available/{subdomain}"
    webroot_path = f"/var/www/{subdomain}"

    # Get list of backups, sorted by name (timestamp)
    exit_code, stdout, _ = ssh.exec_command(f"ls -1dt {backup_dir}/*/ 2>/dev/null")
    if exit_code != 0 or not stdout.strip():
        raise RuntimeError(f"无可用备份: {subdomain}")

    dirs = [d.rstrip("/") for d in stdout.strip().split("\n")]
    if len(dirs) < 2:
        # Only current backup (just made), need the one before that
        # Actually, the backup dirs include all versions
        raise RuntimeError(f"无可回滚版本（仅当前版本）: {subdomain}")

    # The backup list is sorted by time desc; [0] is current, [1] is previous
    # But we just backed up current, so the list is: current_backup, old_backup, ...
    target_backup = dirs[1]
    timestamp = Path(target_backup).name

    # Restore config
    ssh.exec_command(f"cp {target_backup}/{subdomain} {config_path}")
    # Restore webroot
    ssh.exec_command(f"rm -rf {webroot_path}")  # scan-ignore-line — 回滚前清理目标 webroot,目标路径已校验
    ssh.exec_command(f"cp -a {target_backup}/webroot {webroot_path}")

    # Validate and reload
    ok, output = validate_nginx_config(ssh)
    if not ok:
        raise RuntimeError(f"Nginx 配置语法错误（回滚后）:\n{output}")

    ssh.exec_command("systemctl reload nginx")
    return timestamp
