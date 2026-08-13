"""Integration tests for CLI entry point."""

from my_python_app.cli import main


def test_main_runs():
    assert main() == 0