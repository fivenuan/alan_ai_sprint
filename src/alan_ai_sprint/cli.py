"""Command-line entry point: validate an LLM JSON payload from a file.

用法（在项目根目录）::

    uv run parse-json data/sample_response.json

退出码约定（工程惯例）：
- 0 = 成功
- 1 = 文件不存在 / 读取失败
- 2 = payload 不合法（JSON 坏或 schema 违规）

退出码很重要：让这个 CLI 能被脚本 / CI / 其他 agent 编排调用，
调用方只需要看退出码，不用解析人类语言输出。
"""

import argparse
import sys
from pathlib import Path

from alan_ai_sprint.parser import ParsingError, parse_response


def build_arg_parser() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(
        prog="parse-json",
        description="Validate an LLM JSON payload against the book-shelf schema",
    )
    arg_parser.add_argument("path", help="Path to the JSON file to validate")
    return arg_parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    path = Path(args.path)

    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    raw = path.read_text(encoding="utf-8")

    try:
        response = parse_response(raw)
    except ParsingError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"model:  {response.model}")
    print(
        f"tokens: {response.usage.total_tokens} "
        f"(prompt={response.usage.prompt_tokens}, "
        f"completion={response.usage.completion_tokens})"
    )
    print(f"books:  {len(response.books)}")
    for book in response.books:
        rating = f"{book.rating:.1f}" if book.rating is not None else "n/a"
        print(f"  - {book.title} ({book.author}, {book.year}) [{rating}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
