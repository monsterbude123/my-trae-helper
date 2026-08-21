"""Layer 1: read-only docker probes for diagnostics.

Refactored 2026-08-20: the old one-shot script mixed ``docker inspect`` /
``docker logs`` / ``docker exec`` straight into deploy loops. These helpers
return structured data so callers can branch without re-parsing shell output.
"""
from __future__ import annotations

import shlex
import time
from dataclasses import dataclass, field
from typing import Optional

from publish.ssh.client import SshClient


@dataclass
class ContainerInfo:
    name: str
    status: str             # "Up 5 minutes" / "Restarting (1) 30 seconds ago"
    ports: str = ""         # raw from `docker ps`
    health: Optional[str] = None   # "healthy" / "starting" / "unhealthy" / None

    @property
    def is_running(self) -> bool:
        return self.status.startswith("Up")


@dataclass
class WaitResult:
    container: str
    reached: bool
    final_state: str
    elapsed_seconds: float
    attempts: int
    logs_tail: str = ""     # last few log lines captured on failure


def inspect_health(ssh: SshClient, container: str) -> Optional[str]:
    """Return ``Health.Status`` ("healthy"/"starting"/"unhealthy") or None
    if no healthcheck is configured.
    """
    cmd = (
        f"docker inspect --format='{{{{if .State.Health}}}}{{{{.State.Health.Status}}}}{{{{end}}}}' "
        f"{shlex.quote(container)} 2>/dev/null"
    )
    rc, out, _ = ssh.exec_command(cmd)
    if rc != 0:
        return None
    val = out.strip()
    return val or None


def list_containers(
    ssh: SshClient, *, name: Optional[str] = None, all_: bool = False
) -> list[ContainerInfo]:
    """Return structured container list, optionally filtered by name substring."""
    filter_arg = f'--filter name={shlex.quote(name)}' if name else ""
    all_flag = "-a " if all_ else ""
    fmt = "{{.Names}}\\t{{.Status}}\\t{{.Ports}}"
    rc, out, _ = ssh.exec_command(
        f"docker ps {filter_arg} {all_flag}--format '{fmt}'".replace("  ", " ")
    )
    if rc != 0:
        return []
    containers: list[ContainerInfo] = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t", 2)
        if len(parts) < 2:
            continue
        name_v = parts[0]
        status = parts[1]
        ports = parts[2] if len(parts) > 2 else ""
        containers.append(
            ContainerInfo(
                name=name_v,
                status=status,
                ports=ports,
                health=inspect_health(ssh, name_v),
            )
        )
    return containers


def tail_logs(ssh: SshClient, container: str, n: int = 60) -> str:
    """Fetch the last ``n`` log lines from a container."""
    rc, out, err = ssh.exec_command(
        f"docker logs --tail {n} {shlex.quote(container)} 2>&1"
    )
    return (out if rc == 0 else (out + err)).strip()


def exec_in(ssh: SshClient, container: str, command: str) -> tuple[int, str]:
    """Run a one-shot command inside a running container."""
    rc, out, err = ssh.exec_command(
        f"docker exec {shlex.quote(container)} sh -c {shlex.quote(command)} 2>&1"
    )
    return rc, out + err


def wait_healthy(
    ssh: SshClient,
    container: str,
    *,
    expected: str = "healthy",
    timeout_seconds: int = 60,
    poll_interval: float = 2.0,
) -> WaitResult:
    """Poll ``inspect_health`` until status matches ``expected`` or timeout.

    A 2026-08-20 zentao deploy actually needed ~30s for db healthy; we cap
    default at 60s for safety. Logs are captured on timeout for diagnosis.
    """
    t0 = time.monotonic()
    last_state = "(unknown)"
    attempts = 0
    while time.monotonic() - t0 < timeout_seconds:
        attempts += 1
        state = inspect_health(ssh, container)
        last_state = state or "(no-healthcheck)"
        if state == expected:
            return WaitResult(
                container=container,
                reached=True,
                final_state=state,
                elapsed_seconds=time.monotonic() - t0,
                attempts=attempts,
            )
        time.sleep(poll_interval)
    # timed out: grab diagnostics for the caller
    return WaitResult(
        container=container,
        reached=False,
        final_state=last_state,
        elapsed_seconds=time.monotonic() - t0,
        attempts=attempts,
        logs_tail=tail_logs(ssh, container, n=20),
    )
