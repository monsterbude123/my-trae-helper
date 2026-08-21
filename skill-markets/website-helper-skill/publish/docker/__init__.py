"""publish.docker — Layer 1: remote docker operations.

Refactored 2026-08-20 from inline ``ssh.exec_command("docker ...")`` calls
in one-off deploy scripts. Each function here owns exactly one concern so
that any subsequent pipeline / action layer can compose them.
"""

from publish.docker.compose import (
    compose_pull,
    compose_up,
    compose_down,
    ensure_project_dir,
    write_compose_file,
)
from publish.docker.install import ensure_docker_installed
from publish.docker.probe import (
    inspect_health,
    list_containers,
    tail_logs,
    exec_in,
    wait_healthy,
)

__all__ = [
    "compose_pull",
    "compose_up",
    "compose_down",
    "ensure_project_dir",
    "write_compose_file",
    "ensure_docker_installed",
    "inspect_health",
    "list_containers",
    "tail_logs",
    "exec_in",
    "wait_healthy",
]
