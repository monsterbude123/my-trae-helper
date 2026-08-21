"""publish.pipeline — Layer 3: typed multi-step orchestration.

Refactored 2026-08-20 from nested try/except in ``cli.deploy``. Each step is
a callable returning a :class:`Step` (or raising) and the pipeline owns:

  * status aggregation (``ok`` / ``skipped`` / ``failed`` / ``partial``)
  * short-circuit on first hard failure
  * listener fan-out for stdout / audit / log / test
  * structured duration timing for each step

This is intentionally tiny (~120 lines) so :mod:`cli` can stay a thin router.

Example
-------
::

    from publish.pipeline import Pipeline, Step

    p = Pipeline("deploy:zentaopms.example.com")
    p.on_step(lambda s: typer.echo(_fmt(s)))

    @p.step
    def dns():
        try:
            dns.create_record("zentaopms.example.com", server_ip)
            return Step("dns", "ok")
        except ValueError as e:
            return Step("dns", "skipped" if "已存在" in str(e) else "failed", error=str(e))

    @p.step
    def nginx():
        with SshClient(ssh_cfg) as ssh:
            deploy_proxy(ssh, "zentaopms.example.com", "http://127.0.0.1:8088")
        return Step("nginx", "ok")

    success = p.run()
    typer.echo(p.summary())
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Iterable, Literal, Optional

# Step statuses
Status = Literal["pending", "ok", "skipped", "failed", "partial"]


@dataclass
class Step:
    """A single unit of work in a Pipeline."""

    name: str
    status: Status = "pending"
    output: str = ""
    error: str = ""
    duration_ms: int = 0

    @property
    def is_hard_failure(self) -> bool:
        """``True`` only for 'failed' — used by Pipeline to short-circuit."""
        return self.status == "failed"


@dataclass
class _RegisteredStep:
    """Pipeline-internal binding of name → callable."""

    name: str
    func: Callable[[], Step]


class Pipeline:
    """Collect steps, register listeners, run them in order with short-circuit.

    Listeners fire after each step finishes (regardless of status) and receive
    the :class:`Step` instance. Use them for typer output, audit logging, or
    per-step telemetry.
    """

    def __init__(self, name: str, *, short_circuit: bool = True):
        self.name = name
        self.short_circuit = short_circuit
        self._registered: list[_RegisteredStep] = []
        self.steps: list[Step] = []
        self.listeners: list[Callable[[Step], None]] = []

    # ── registration API (decorator-friendly) ──────────────────────────

    def step(self, func: Callable[[], Step]) -> Callable[[], Step]:
        """Decorator: ``@p.step`` registers the function under its __name__."""
        self._registered.append(_RegisteredStep(name=func.__name__, func=func))
        return func

    def add(self, func: Callable[[], Step], *, name: Optional[str] = None) -> None:
        """Imperative registration (no decorator)."""
        self._registered.append(
            _RegisteredStep(name=name or func.__name__, func=func)
        )

    # ── listener API ────────────────────────────────────────────────────

    def on_step(self, fn: Callable[[Step], None]) -> Callable[[Step], None]:
        """Register a listener fired after each step."""
        self.listeners.append(fn)
        return fn

    # ── execution ───────────────────────────────────────────────────────

    def run(self) -> bool:
        """Execute registered steps in order. Returns True on full success."""
        all_ok = True
        for registered in self._registered:
            step = Step(name=registered.name)
            t0 = time.monotonic()
            try:
                result = registered.func()
            except Exception as exc:  # noqa: BLE001 — actions may raise anything
                step.status = "failed"
                step.error = f"{type(exc).__name__}: {exc}"
            else:
                if isinstance(result, Step):
                    step = result
                elif result is None:
                    step.status = "ok"
                else:
                    # convenience: truthy → ok, falsy → skipped
                    step.status = "ok" if result else "skipped"
            step.duration_ms = int((time.monotonic() - t0) * 1000)
            self.steps.append(step)
            for listener in self.listeners:
                listener(step)
            if step.is_hard_failure:
                all_ok = False
                if self.short_circuit:
                    break
        return all_ok

    # ── reporting ───────────────────────────────────────────────────────

    def summary(self) -> str:
        """One-line summary suitable for final CLI output."""
        ok = sum(1 for s in self.steps if s.status == "ok")
        skipped = sum(1 for s in self.steps if s.status == "skipped")
        failed = sum(1 for s in self.steps if s.status == "failed")
        return (
            f"{self.name}: {ok} ok / {skipped} skipped / {failed} failed "
            f"out of {len(self.steps)} steps"
        )

    def failed_steps(self) -> Iterable[Step]:
        return (s for s in self.steps if s.status == "failed")


# ── Default formatter used by cli.py ────────────────────────────────────────

_STEP_ICONS = {
    "ok":      "✅",
    "skipped": "ℹ️ ",
    "failed":  "❌",
    "partial": "⚠️ ",
    "pending": "⏳",
}


def format_step(step: Step) -> str:
    """Compact one-line text used as default listener body."""
    icon = _STEP_ICONS.get(step.status, "?")
    base = f"{icon} {step.name:<30s} {step.status:<8s} {step.duration_ms}ms"
    if step.error:
        base += f"  err: {step.error[:60]}"
    return base
