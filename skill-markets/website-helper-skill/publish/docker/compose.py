"""Layer 1: docker compose lifecycle on a remote host.

Refactored 2026-08-20 from a long inline script that hard-coded Zentao paths.
These functions now take ``project_dir`` explicitly so any compose project
(zentao / wordpress / nextcloud / gitlab) can be deployed.
"""
from __future__ import annotations

import shlex
from pathlib import Path

from publish.ssh.client import SshClient


def ensure_project_dir(ssh: SshClient, project_dir: str) -> None:
    """mkdir -p the project directory on the remote."""
    ssh.exec_command(f"mkdir -p {shlex.quote(project_dir)}")


def write_compose_file(
    ssh: SshClient,
    project_dir: str,
    compose_contents: str,
    filename: str = "docker-compose.yml",
) -> None:
    """Atomically write a docker-compose file to ``project_dir/<filename>``.

    The ``compose_contents`` is uploaded via stdin heredoc; any prior file is
    preserved as ``<name>.bak`` so a failed write is recoverable.
    """
    safe_path = shlex.quote(project_dir)
    safe_name = shlex.quote(filename)
    # preserve prior version
    ssh.exec_command(
        f"test -f {safe_path}/{safe_name} && "
        f"cp -f {safe_path}/{safe_name} {safe_path}/{safe_name}.bak 2>/dev/null || true"
    )
    # write via heredoc — caller must ensure no '\nNGINX_EOF\n' in content
    sentinel = "COMPOSE_EOF"
    if sentinel in compose_contents:
        raise ValueError(
            f"compose_contents 包含禁用 sentinel ({sentinel!r}), "
            f"改文件名或换 sentinel"
        )
    ssh.exec_command(
        f"cat > {safe_path}/{safe_name} << '{sentinel}'\n{compose_contents}\n{sentinel}"
    )


def compose_pull(
    ssh: SshClient, project_dir: str, services: list[str] | None = None
) -> tuple[int, str]:
    """``docker compose pull`` the whole project or a subset of services."""
    svc = " ".join(shlex.quote(s) for s in services) if services else ""
    cmd = f"cd {shlex.quote(project_dir)} && docker compose pull {svc}".strip()
    rc, out, err = ssh.exec_command(cmd)
    return rc, out + err


def compose_up(
    ssh: SshClient,
    project_dir: str,
    services: list[str] | None = None,
    detach: bool = True,
) -> tuple[int, str]:
    """``docker compose up`` (default ``-d``). Empty services list = whole project."""
    args = " ".join(shlex.quote(s) for s in services) if services else ""
    flags = "-d " if detach else ""
    cmd = f"cd {shlex.quote(project_dir)} && docker compose up {flags}{args}".strip()
    rc, out, err = ssh.exec_command(cmd)
    return rc, out + err


def compose_down(
    ssh: SshClient,
    project_dir: str,
    *,
    remove_volumes: bool = False,
    remove_images: bool = False,
) -> tuple[int, str]:
    """``docker compose down`` (optionally ``-v`` to wipe named volumes)."""
    flags = []
    if remove_volumes:
        flags.append("-v")
    if remove_images:
        flags.append("--rmi all")
    cmd = (
        f"cd {shlex.quote(project_dir)} && "
        f"docker compose down {' '.join(flags)}".strip()
    )
    rc, out, err = ssh.exec_command(cmd)
    return rc, out + err
