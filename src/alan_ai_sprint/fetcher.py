"""Day 3 主任务：并发 URL 抓取器（asyncio + httpx + Semaphore）。

对外契约（这个文件是你的任务规格书）::

    fetch_urls(urls, concurrency=10) -> list[FetchResult]

- 并发上限：同一时刻最多 concurrency 个请求在飞（Semaphore）
- 单个失败不炸整体：失败的 URL 返回 error 字段非空的 FetchResult
- 每个结果都带 duration_ms（单次请求耗时）

实现分两层（为什么要拆，见《04-asyncio-day3.md》第 7 节）：
- ``_fetch_one``  —— 干活的：抓一个 URL
- ``fetch_urls``  —— 指挥的：并发编排 + 异常分类

YOUR JOB：把下面两个 ``TODO`` 补完，让 ``tests/test_fetcher.py`` 全绿。
"""

from __future__ import annotations

import asyncio  # noqa: F401  -- TODO 2 实现时要用的，先占位
import time  # noqa: F401  -- TODO 1 计时要用的，先占位

import httpx
from pydantic import BaseModel, Field


class FetchResult(BaseModel):
    """一次抓取的结果。成功时 status_code 非 None；失败时 error 非 None。"""

    url: str
    status_code: int | None = Field(default=None, description="HTTP 状态码；请求失败时为 None")
    error: str | None = Field(default=None, description="失败原因；成功时为 None")
    duration_ms: float = Field(default=0.0, description="本次请求耗时（毫秒）")

    @property
    def ok(self) -> bool:
        """成功 = 有状态码、无错误。"""
        return self.status_code is not None and self.error is None


async def _fetch_one(url: str, client: httpx.AsyncClient) -> FetchResult:
    """抓取单个 URL。

    TODO 1 —— 你来实现。步骤：
      1. 记下开始时间 time.perf_counter()
      2. ``resp = await client.get(url)`` 发请求
      3. 计算耗时（毫秒 = (结束 - 开始) * 1000）
      4. 返回 FetchResult(url=..., status_code=resp.status_code, duration_ms=...)

    注意：
      - 超时 / 网络错误会在这里抛异常（httpx.TimeoutException、httpx.HTTPError 等）
        —— 不要在这里 try/except！让异常抛给 fetch_urls 统一处理。
      - client 由调用方传入并复用（连接池），这里不要新建、也不要关闭。
    """
    raise NotImplementedError("TODO 1: 实现 _fetch_one")


async def fetch_urls(urls: list[str], concurrency: int = 10) -> list[FetchResult]:
    """并发抓取所有 URL，返回结果列表（顺序与 urls 一致）。

    TODO 2 —— 你来实现。步骤：
      1. ``sem = asyncio.Semaphore(concurrency)`` 造信号量
      2. 定义内部协程 ``limited(url)``：``async with sem:`` 后调 _fetch_one
      3. 用一个 ``async with httpx.AsyncClient(timeout=10) as client:``
         包住所有请求（整个函数复用这一个 client）
      4. ``results = await asyncio.gather(*tasks, return_exceptions=True)``
      5. 遍历 results：正常的直接收；是 Exception 的包成
         ``FetchResult(url=..., error=str(exc))``（status_code 留 None）
      6. 返回 list[FetchResult]，顺序与 urls 一致（gather 保证顺序）
    """
    raise NotImplementedError("TODO 2: 实现 fetch_urls")
