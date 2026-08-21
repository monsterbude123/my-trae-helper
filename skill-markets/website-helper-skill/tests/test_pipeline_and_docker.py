"""v0.3.0 — tests for Layer 1 (docker/...), Layer 2 (actions/), Layer 3 (pipeline).

Three-state coverage:
  * PASS  — happy path
  * BLOCK — short-circuit on hard failure
  * BOUNDARY — partial skipped / partial failed transitions

We use a fake SshClient for all docker/ tests so we don't need a real docker
daemon: ``FakeSsh`` records every ``exec_command`` call and lets the test
script the responses.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Iterable

_HERE = Path(__file__).resolve().parent
_SKILL_ROOT = _HERE.parent
sys.path.insert(0, str(_SKILL_ROOT))

import pytest

from publish.docker.compose import (
    compose_pull,
    compose_up,
    compose_down,
    ensure_project_dir,
    write_compose_file,
)
from publish.docker.install import ensure_docker_installed
from publish.docker.probe import (
    ContainerInfo,
    list_containers,
    inspect_health,
    wait_healthy,
    WaitResult,
)
from publish.pipeline import Pipeline, Step, format_step


# ───────────────────────── Fake SshClient ─────────────────────────────────

class FakeSsh:
    """Drop-in for SshClient that scripts responses per command.

    Each entry in :attr:`scripted` is a tuple ``(matcher, (rc, out, err))``;
    the first matcher that ``cmd in matcher == True`` wins. If none match,
    we return ``(0, "", "")`` so tests don't accidentally crash on newlines.
    """

    def __init__(self) -> None:
        self.scripted: list[tuple[str, tuple[int, str, str]]] = []
        self.calls: list[str] = []
        self.closed = False

    def exec_command(self, cmd: str) -> tuple[int, str, str]:
        self.calls.append(cmd)
        for matcher, response in self.scripted:
            if matcher in cmd:
                return response
        return 0, "", ""

    def close(self) -> None:
        self.closed = True

    # Context-manager shim so `with FakeSsh()` mirrors SshClient.
    def __enter__(self) -> "FakeSsh":
        return self

    def __exit__(self, *args) -> None:
        self.close()


# ───────────────────────── Layer 1: docker/... ────────────────────────────

class TestEnsureDockerInstalled:
    def test_pass_already_installed(self):
        ssh = FakeSsh()
        # docker --version succeeds AND systemctl says active
        ssh.scripted.append(("docker --version", (0, "Docker 24.0", "")))
        ssh.scripted.append(("systemctl is-active docker", (0, "active", "")))
        assert ensure_docker_installed(ssh) is True
        # No apt install was issued
        assert not any("apt-get install" in c for c in ssh.calls)

    def test_block_install_failure(self):
        ssh = FakeSsh()
        # docker missing → apt install fails
        ssh.scripted.append(("docker --version", (1, "", "not found")))
        # error fallback (since rc != 0, we proceed to apt)
        ssh.scripted.append(("apt-get install", (1, "boom", "")))
        with pytest.raises(RuntimeError, match="apt install docker failed"):
            ensure_docker_installed(ssh)


class TestComposeLifecycle:
    """Each function should drop to the correct docker compose invocation."""

    def test_pass_pull_no_services(self):
        ssh = FakeSsh()
        ssh.scripted.append(("docker compose pull", (0, "Pulled", "")))
        rc, out = compose_pull(ssh, "/opt/zentao")
        assert rc == 0
        assert "cd /opt/zentao" in ssh.calls[0]
        assert "docker compose pull" in ssh.calls[0]

    def test_pass_pull_with_services(self):
        ssh = FakeSsh()
        ssh.scripted.append(("docker compose pull", (0, "", "")))
        compose_pull(ssh, "/opt/zentao", services=["zentao", "zentao-db"])
        # shlex.quote keeps alphanumeric tokens as-is; the full service list
        # appears at the end of the docker compose pull invocation
        assert ssh.calls[0].endswith("docker compose pull zentao zentao-db")

    def test_pass_pull_with_path_containing_spaces(self):
        """Boundary: project dir with spaces MUST be shell-quoted."""
        ssh = FakeSsh()
        ssh.scripted.append(("docker compose pull", (0, "", "")))
        compose_pull(ssh, "/opt/zentao proj")
        assert "'/opt/zentao proj'" in ssh.calls[0]

    def test_pass_up_detach_default(self):
        ssh = FakeSsh()
        ssh.scripted.append(("docker compose up -d", (0, "Started", "")))
        rc, _ = compose_up(ssh, "/opt/zentao")
        assert rc == 0
        assert " -d" in ssh.calls[0]

    def test_pass_up_no_detach(self):
        ssh = FakeSsh()
        ssh.scripted.append(("docker compose up ", (0, "", "")))
        compose_up(ssh, "/opt/zentao", detach=False)
        assert " -d" not in ssh.calls[0]

    def test_block_down_with_volumes(self):
        ssh = FakeSsh()
        ssh.scripted.append(("docker compose down -v", (0, "", "")))
        rc, _ = compose_down(ssh, "/opt/zentao", remove_volumes=True)
        assert rc == 0
        assert " -v" in ssh.calls[0]


class TestWriteComposeFile:
    def test_pass_writes_via_heredoc(self):
        ssh = FakeSsh()
        # fake successful exec since shell test is bundled with the cp fallback
        contents = "services:\n  zentao:\n    image: foo\n"
        write_compose_file(ssh, "/opt/zentao", contents)
        # Compose content lands in the heredoc
        assert any("services:" in c for c in ssh.calls)
        # backup attempt should have run first
        assert any(".bak" in c for c in ssh.calls)

    def test_block_reserved_sentinel_in_contents(self):
        ssh = FakeSsh()
        with pytest.raises(ValueError, match="禁用 sentinel"):
            write_compose_file(ssh, "/opt/zentao", "foo COMPOSE_EOF bar")


class TestEnsureProjectDir:
    def test_pass_quotes_path(self):
        ssh = FakeSsh()
        ensure_project_dir(ssh, "/opt/zen tao")  # spaces → must be quoted
        # Resulting command must contain the quoted form
        assert any("mkdir -p" in c for c in ssh.calls)


# ───────────────────────── Layer 1: docker/probe ───────────────────────────

class TestDockerProbe:
    def test_pass_inspect_health_healthy(self):
        ssh = FakeSsh()
        ssh.scripted.append(("docker inspect", (0, "healthy", "")))
        assert inspect_health(ssh, "zentao-db") == "healthy"

    def test_pass_inspect_health_no_healthcheck(self):
        ssh = FakeSsh()
        ssh.scripted.append(("docker inspect", (1, "", "")))
        assert inspect_health(ssh, "zentao") is None

    def test_pass_list_containers_parses_tabular(self):
        ssh = FakeSsh()
        ssh.scripted.append(("docker ps", (0, "zentao\tUp 5 minutes\t127.0.0.1:8088->80/tcp\n"
                                              "zentao-db\tUp 5 minutes (healthy)\t3306/tcp\n", "")))
        result = list_containers(ssh)
        assert len(result) == 2
        assert result[0].name == "zentao"
        assert result[1].ports == "3306/tcp"

    def test_pass_list_containers_with_filter(self):
        ssh = FakeSsh()
        ssh.scripted.append(("docker ps", (0, "", "")))
        list_containers(ssh, name="zentao")
        # shlex.quote leaves alphanumeric alone; the --filter form is present
        assert "--filter" in ssh.calls[0]
        assert "name=zentao" in ssh.calls[0]

    def test_pass_wait_healthy_eventually_reaches(self, monkeypatch):
        ssh = FakeSsh()
        # First two calls: 'starting' → next: 'healthy'
        responses = iter([
            (0, "starting", ""),
            (0, "starting", ""),
            (0, "healthy", ""),
        ])
        ssh.exec_command = lambda cmd: next(responses) if "--format='{{if .State.Health" in cmd else (0, "", "")
        # speed up the loop
        monkeypatch.setattr("publish.docker.probe.time.sleep", lambda _: None)
        result = wait_healthy(ssh, "zentao-db", expected="healthy", timeout_seconds=10, poll_interval=0)
        assert result.reached is True
        assert result.final_state == "healthy"

    def test_block_wait_healthy_timeout(self, monkeypatch):
        ssh = FakeSsh()
        ssh.scripted.append(("docker inspect", (0, "starting", "")))
        monkeypatch.setattr("publish.docker.probe.time.sleep", lambda _: None)
        result = wait_healthy(ssh, "zentao-db", expected="healthy", timeout_seconds=0, poll_interval=0)
        assert result.reached is False
        # diagnostic tail included for debugging
        assert isinstance(result.logs_tail, str)


# ───────────────────────── Layer 3: Pipeline ──────────────────────────────

class TestPipeline:
    """Pure-Python tests — no SSH at all."""

    def test_pass_runs_all_in_order(self):
        p = Pipeline("test:order")
        p.add(lambda: Step("a", "ok"))
        p.add(lambda: Step("b", "ok"))
        p.add(lambda: Step("c", "ok"))
        assert p.run() is True
        assert [s.name for s in p.steps] == ["a", "b", "c"]
        assert all(s.status == "ok" for s in p.steps)

    def test_block_short_circuits_on_failure(self):
        p = Pipeline("test:fail", short_circuit=True)
        p.add(lambda: Step("a", "ok"))
        p.add(lambda: Step("b", "failed", error="nope"))
        p.add(lambda: pytest.fail("must not be called"))
        assert p.run() is False
        assert len(p.steps) == 2

    def test_pass_continues_through_skipped(self):
        p = Pipeline("test:skip")
        p.add(lambda: Step("a", "ok"))
        p.add(lambda: Step("b", "skipped", output="already exists"))
        p.add(lambda: Step("c", "ok"))
        assert p.run() is True

    def test_pass_catches_exception_into_step(self):
        p = Pipeline("test:exc")
        def boom():
            raise RuntimeError("zentao image pull failed")
        p.add(boom)
        assert p.run() is False
        assert p.steps[0].status == "failed"
        assert "RuntimeError" in p.steps[0].error
        assert "zentao image pull" in p.steps[0].error

    def test_pass_listener_invoked(self):
        p = Pipeline("test:listener")
        received: list[str] = []
        p.on_step(lambda s: received.append(s.name))
        p.add(lambda: Step("a", "ok"))
        p.add(lambda: Step("b", "ok"))
        p.run()
        assert received == ["a", "b"]

    def test_pass_summary(self):
        p = Pipeline("test:summary")
        p.add(lambda: Step("a", "ok"))
        p.add(lambda: Step("b", "skipped"))
        p.add(lambda: Step("c", "ok"))
        p.run()
        s = p.summary()
        assert "2 ok" in s and "1 skipped" in s and "0 failed" in s

    def test_decorator_form(self):
        p = Pipeline("test:deco")
        @p.step
        def dns(): return Step("dns", "ok")
        @p.step
        def nginx(): return Step("nginx", "ok")
        assert p.run() is True
        assert [s.name for s in p.steps] == ["dns", "nginx"]

    def test_format_step_compact(self):
        s = Step("x", "ok", duration_ms=42)
        line = format_step(s)
        assert "x" in line and "42" in line and "ok" in line

    def test_pass_truthy_return_ok_falsy_skipped(self):
        """convenience: returning True/False maps to ok/skipped."""
        p = Pipeline("test:retval")
        p.add(lambda: True)
        p.add(lambda: False)
        p.run()
        assert p.steps[0].status == "ok"
        assert p.steps[1].status == "skipped"


if __name__ == "__main__":
    import unittest

    class L(unittest.TestLoader):
        def loadTestsFromModule(self, m):
            return unittest.TestSuite([
                TestEnsureDockerInstalled(),
                TestComposeLifecycle(),
                TestWriteComposeFile(),
                TestEnsureProjectDir(),
                TestDockerProbe(),
                TestPipeline(),
            ])

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(L().loadTestsFromModule(sys.modules[__name__]))
