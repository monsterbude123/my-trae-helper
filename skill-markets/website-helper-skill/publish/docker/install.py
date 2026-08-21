"""Layer 1: install docker on a remote host (apt-based distros).

Refactored 2026-08-20: previously called as inline
``ssh.exec_command(\"apt-get install -y docker.io ...\")`` in a one-shot
deploy script — now reusable for any apt target.
"""
from __future__ import annotations

from publish.ssh.client import SshClient


def ensure_docker_installed(ssh: SshClient) -> bool:
    """Install docker engine + compose plugin if missing.

    Returns True if the engine is up after this call. Re-running on an
    already-installed host is a cheap no-op (systemctl enable --now is idempotent).
    """
    rc, out, _ = ssh.exec_command("docker --version")
    if rc == 0:
        # Service running?
        rc2, _, _ = ssh.exec_command("systemctl is-active docker")
        if rc2 == 0:
            return True

    # apt path (Debian / Ubuntu / Deepin / 同族)
    # shell-quoted heredoc to keep install idempotent
    cmd = (
        "bash -lc 'set -e; "
        "export DEBIAN_FRONTEND=noninteractive; "
        "apt-get update -qq >/dev/null && "
        "apt-get install -y -qq docker.io docker-compose-plugin 2>&1 | tail -3'"
    )
    rc, out, err = ssh.exec_command(cmd)
    if rc != 0:
        raise RuntimeError(f"apt install docker failed:\n{out}\n{err}")

    ssh.exec_command("systemctl enable --now docker 2>&1 || true")
    # wait for daemon to settle
    rc, _, _ = ssh.exec_command("systemctl is-active docker")
    return rc == 0
