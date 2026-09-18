"""Tests for the hello module — Day 1 sanity check.

pytest 风格 + type hints + descriptive names。这是工程纪律的最小闭环：
写代码 → 写测试 → 跑通 → 提交。
"""

from alan_ai_sprint.hello import add, greet


def test_greet_default() -> None:
    assert greet() == "Hello, alan! Welcome to your AI sprint."


def test_greet_custom_name() -> None:
    assert greet("world") == "Hello, world! Welcome to your AI sprint."


def test_add_positive() -> None:
    assert add(2, 3) == 5


def test_add_negative() -> None:
    assert add(-1, 1) == 0


def test_add_zero() -> None:
    assert add(0, 0) == 0
