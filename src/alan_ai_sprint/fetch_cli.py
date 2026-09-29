"""fetch-urls 命令行入口：并发抓取一个 URL 列表文件。

用法（在项目根目录）::

    uv run fetch-urls data/urls.txt
    uv run fetch-urls data/urls.txt --concurrency 5

退出码约定（沿用 parse-json 的工程惯例）：
- 0 = 全部抓取成功
- 1 = 输入文件不存在 / 读取失败
- 2 = 有 URL 抓取失败（但整体流程跑完了）

这个文件已经写好——它调用的 fetch_urls 等你实现（fetcher.py 的 TODO 2）。
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

from alan_ai_sprint.decorators import read_urls_lazy
from alan_ai_sprint.fetcher import fetch_urls


def build_arg_parser() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(
        prog="fetch-urls",
        description="Fetch a list of URLs concurrently and report results",
    )
    arg_parser.add_argument("path", help="Path to a text file: one URL per line")
    arg_parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Max concurrent requests (default: 10)",
    )
    return arg_parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    path = Path(args.path)

    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    urls = list(read_urls_lazy(str(path)))
    print(f"loaded {len(urls)} urls, concurrency={args.concurrency}")

    start = time.perf_counter()
    results = asyncio.run(fetch_urls(urls, concurrency=args.concurrency))
    elapsed = time.perf_counter() - start

    failures = [r for r in results if not r.ok]
    for r in results:
        if r.ok:
            print(f"  [{r.status_code}] {r.url} ({r.duration_ms:.0f}ms)")
        else:
            print(f"  [ERR] {r.url} -> {r.error}")

    print(f"\ndone: {len(results) - len(failures)} ok, {len(failures)} failed ({elapsed:.2f}s)")
    return 2 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
