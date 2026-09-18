"""Day 1 · 第一个有意义的代码单元。

这是一个最小但带类型注解、带测试、带文档字符串的模块——验证
pytest / ruff / mypy 全套工程纪律从 Day 1 起就接入。
"""


def greet(name: str = "alan") -> str:
    """Return a greeting message for the given name."""
    return f"Hello, {name}! Welcome to your AI sprint."


def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b


if __name__ == "__main__":
    print(greet())
