"""CLI entry point for my_python_app."""

from .utils.greet import greet


def main() -> int:
    """Print a greeting and return exit code."""
    print(greet("World"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())