"""Day 4 · decorators.py 的契约测试。

这些测试是规格，不许改。对应规格：learning-paths/05-day4-decorators-generators.md 第 6 节。
"""

from __future__ import annotations

import types
from pathlib import Path

import pytest

from alan_ai_sprint.decorators import async_retry, read_urls_lazy, timed


def test_timed_prints_duration(capsys: pytest.CaptureFixture[str]) -> None:
    @timed
    def add(a: int, b: int) -> int:
        return a + b

    assert add(2, 3) == 5
    out = capsys.readouterr().out
    assert "add" in out
    assert "ms" in out


def test_timed_prints_duration_even_on_error(capsys: pytest.CaptureFixture[str]) -> None:
    @timed
    def boom() -> None:
        raise RuntimeError("kaput")

    with pytest.raises(RuntimeError, match="kaput"):
        boom()
    out = capsys.readouterr().out
    assert "boom" in out
    assert "ms" in out


async def test_async_retry_succeeds_after_failures() -> None:
    calls = {"n": 0}

    @async_retry(times=3, delay=0.01)
    async def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            msg = f"fail {calls['n']}"
            raise ValueError(msg)
        return "ok"

    assert await flaky() == "ok"
    assert calls["n"] == 3


async def test_async_retry_raises_after_exhausted() -> None:
    calls = {"n": 0}

    @async_retry(times=4, delay=0.01)
    async def always_fails() -> str:
        calls["n"] += 1
        raise ConnectionError("down")

    with pytest.raises(ConnectionError, match="down"):
        await always_fails()
    assert calls["n"] == 4  # 恰好 times 次——off-by-one 照妖镜


async def test_async_retry_preserves_function_name() -> None:
    @async_retry(times=2, delay=0.01)
    async def named_fn() -> int:
        return 1

    assert named_fn.__name__ == "named_fn"


def test_read_urls_lazy_skips_comments_and_blanks(tmp_path: Path) -> None:
    f = tmp_path / "urls.txt"
    f.write_text("# comment\n\nhttps://a.com\n   \n  https://b.com  \n", encoding="utf-8")
    assert list(read_urls_lazy(str(f))) == ["https://a.com", "https://b.com"]


def test_read_urls_lazy_is_lazy(tmp_path: Path) -> None:
    f = tmp_path / "urls.txt"
    f.write_text("https://a.com\n", encoding="utf-8")
    result = read_urls_lazy(str(f))
    assert isinstance(result, types.GeneratorType)  # 产出的是生成器，不是 list
    assert list(result) == ["https://a.com"]
