"""Day 4 · 可复用装饰器与生成器（横切关注点工具箱）。

契约：tests/test_decorators.py
"""

from __future__ import annotations

import asyncio
import functools
import time
from collections.abc import Callable, Coroutine, Iterator
from typing import Any


def timed[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """同步计时装饰器：正常返回和抛异常时都打印耗时。

    打印格式："took {X:.2f} ms"（契约见 tests/test_decorators.py）。
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            print(f"{func.__name__} took {duration_ms:.2f} ms")

    return wrapper


@timed
def slow_sum(a: int, b: int) -> int:
    time.sleep(0.1)  # 模拟慢操作
    return a + b


def async_retry[**P, R](
    times: int, delay: float
) -> Callable[[Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]]:
    """异步重试装饰器工厂。

    times: **总尝试次数**（不是重试次数——times=3 最多发 3 次请求）
    delay: 每次失败后的等待时间（秒）

    最后一次仍失败时，把最后一次的异常原样抛出（不吞）。
    """

    def decorator(
        func: Callable[P, Coroutine[Any, Any, R]],
    ) -> Callable[P, Coroutine[Any, Any, R]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(1, times + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    if attempt == times:
                        raise  # 最后一次失败：裸 raise 重抛当前异常，不吞
                    await asyncio.sleep(delay)
            raise AssertionError("unreachable: times >= 1 保证循环至少执行一次")

        return wrapper

    return decorator


def read_urls_lazy(path: str) -> Iterator[str]:
    """生成器：逐行产出 URL，跳过空行和 # 注释行。

    每行先 strip()；strip 后为空或以 # 开头的行跳过。
    with open 管理文件句柄；内存里永远只持有当前一行。
    """
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                yield stripped
