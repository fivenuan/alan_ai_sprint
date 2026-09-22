"""Day 3 主任务的测试框架。

设计原则：**测试不打真网**（工程纪律，资料第 7 节）。
用 monkeypatch 把 fetcher._fetch_one 换成假实现，只测 fetch_urls 的并发编排逻辑。

当前状态（TDD 红灯）：
- test_fetch_result_* 绿（FetchResult 是给定的）
- test_fetch_urls_* 红（等你实现 TODO 1 / TODO 2）
- 你的任务：不改动这些测试，把 fetcher.py 实现到全绿
"""

from __future__ import annotations

import asyncio
import time

import httpx
import pytest

from alan_ai_sprint.fetcher import FetchResult, fetch_urls

# ---------------------------------------------------------------------------
# 第一组：FetchResult 模型（应全绿）
# ---------------------------------------------------------------------------


def test_fetch_result_success_shape() -> None:
    result = FetchResult(url="https://example.com", status_code=200, duration_ms=12.5)
    assert result.ok
    assert result.error is None


def test_fetch_result_failure_shape() -> None:
    result = FetchResult(url="https://example.com", error="boom")
    assert not result.ok
    assert result.status_code is None


def test_fetch_result_rejects_negative_duration() -> None:
    """duration_ms 不该是负数 —— 想加 Field(ge=0)？这是可选加餐。"""
    result = FetchResult(url="u", duration_ms=-1.0)
    assert result.duration_ms == -1.0  # 当前没约束，加了 ge=0 后这行会变 pytest.raises


# ---------------------------------------------------------------------------
# 第二组：fetch_urls 并发编排（红灯 —— 等你实现）
# 替身契约：_fetch_one(url, client) -> FetchResult
# ---------------------------------------------------------------------------


def _install_fake_fetch_one(
    monkeypatch: pytest.MonkeyPatch,
    *,
    delay: float = 0.01,
    fail_urls: set[str] | None = None,
) -> dict[str, int]:
    """把 fetcher._fetch_one 换成假实现，返回调用计数（供断言用）。

    替身行为：睡 delay 秒 -> fail_urls 里的 URL 抛异常 -> 其余返回 200。
    """
    calls: dict[str, int] = {}
    fail_urls = fail_urls or set()

    async def fake_fetch_one(url: str, client: httpx.AsyncClient) -> FetchResult:
        calls[url] = calls.get(url, 0) + 1
        await asyncio.sleep(delay)
        if url in fail_urls:
            msg = f"simulated failure for {url}"
            raise httpx.ConnectError(msg)
        return FetchResult(url=url, status_code=200, duration_ms=delay * 1000)

    monkeypatch.setattr("alan_ai_sprint.fetcher._fetch_one", fake_fetch_one)
    return calls


async def test_fetch_urls_returns_all_results(monkeypatch: pytest.MonkeyPatch) -> None:
    """20 个 URL 全部返回，顺序与输入一致。"""
    _install_fake_fetch_one(monkeypatch)
    urls = [f"u{i}" for i in range(20)]
    results = await fetch_urls(urls)
    assert len(results) == 20
    assert [r.url for r in results] == urls
    assert all(r.ok for r in results)


async def test_fetch_urls_one_failure_does_not_break_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """3 个 URL 里 1 个失败：整批不炸，失败的带 error，成功的带 status_code。"""
    _install_fake_fetch_one(monkeypatch, fail_urls={"bad"})
    results = await fetch_urls(["good1", "bad", "good2"])
    assert len(results) == 3
    by_url = {r.url: r for r in results}
    assert by_url["good1"].ok
    assert by_url["good2"].ok
    assert not by_url["bad"].ok
    assert by_url["bad"].error is not None
    assert by_url["bad"].status_code is None


async def test_fetch_urls_runs_concurrently(monkeypatch: pytest.MonkeyPatch) -> None:
    """20 个任务、每个 0.1s：串行要 2s，并发应远小于 2s。

    断言阈值 1.0s —— 如果你的实现是串行的，这个测试必挂。
    """
    _install_fake_fetch_one(monkeypatch, delay=0.1)
    start = time.perf_counter()
    results = await fetch_urls([f"u{i}" for i in range(20)])
    elapsed = time.perf_counter() - start
    assert len(results) == 20
    assert elapsed < 1.0, f"20 个 0.1s 任务耗时 {elapsed:.2f}s —— 疑似没并发？"


async def test_fetch_urls_empty_input(monkeypatch: pytest.MonkeyPatch) -> None:
    """空列表 -> 空结果，不炸。"""
    _install_fake_fetch_one(monkeypatch)
    assert await fetch_urls([]) == []
