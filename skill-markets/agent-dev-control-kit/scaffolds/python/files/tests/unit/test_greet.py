"""Unit tests for greet utility."""

import pytest

from my_python_app.utils.greet import greet


def test_greet_returns_greeting():
    assert greet("Alice") == "Hello, Alice!"


def test_greet_rejects_empty():
    with pytest.raises(ValueError):
        greet("")


def test_greet_rejects_non_string():
    with pytest.raises(TypeError):
        greet(123)  # type: ignore[arg-type]