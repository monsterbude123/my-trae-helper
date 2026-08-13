"""Greeting utility."""


def greet(name: str) -> str:
    """Return a greeting for the given name.

    Args:
        name: Non-empty string.

    Returns:
        Greeting string.

    Raises:
        TypeError: If name is not a string.
        ValueError: If name is empty.
    """
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    if not name:
        raise ValueError("name must be non-empty")
    return f"Hello, {name}!"