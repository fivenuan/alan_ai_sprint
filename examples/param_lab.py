"""param_lab.py — 推理参数实验台（Day 8）

对同一 prompt 在不同 temperature 下各跑 N 次，输出 markdown 对比表，
供 param_notes.md 记录观察结论。

用法：
    uv run --env-file .env python examples/param_lab.py
    uv run --env-file .env python examples/param_lab.py --temps 0 0.7 1.5 --runs 3
    uv run --env-file .env python examples/param_lab.py --prompt "写一句关于海的比喻"

成本意识：每次运行都在花 token。默认 3 个温度 × 2 次 = 6 次小请求。
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from openai import OpenAI


def build_arg_parser() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(
        prog="param-lab",
        description="同一 prompt 在不同推理参数下的行为对比实验台",
    )
    arg_parser.add_argument(
        "--prompt",
        default="用一句话解释什么是 temperature（大模型推理参数）",
        help="实验用的用户消息",
    )
    arg_parser.add_argument(
        "--system",
        default="你是一个简洁的技术助手。",
        help="system 消息",
    )
    arg_parser.add_argument(
        "--temps",
        type=float,
        nargs="+",
        default=[0.0, 0.7, 1.5],
        help="要对比的 temperature 列表",
    )
    arg_parser.add_argument("--runs", type=int, default=2, help="每个温度重复次数")
    arg_parser.add_argument("--max-tokens", type=int, default=100, help="补全上限")
    arg_parser.add_argument(
        "--out",
        default="examples/param_results.md",
        help="结果 markdown 输出路径",
    )
    return arg_parser


def run_one(
    client: OpenAI,
    model: str,
    system: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
) -> tuple[str, int, float]:
    """发一次请求，返回 (回复文本, 总 token 数, 耗时秒)。"""
    start = time.perf_counter()
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    elapsed = time.perf_counter() - start
    text = resp.choices[0].message.content or ""
    return text, resp.usage.total_tokens if resp.usage else 0, elapsed


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    api_key = os.environ.get("LLM_API_KEY")
    base_url = os.environ.get("LLM_BASE_URL")
    model = os.environ.get("LLM_MODEL", "qwen-plus")
    if not api_key or not base_url:
        print(
            "error: 缺少 LLM_API_KEY / LLM_BASE_URL，用 uv run --env-file .env 运行",
            file=sys.stderr,
        )
        return 1

    client = OpenAI(api_key=api_key, base_url=base_url)

    lines: list[str] = []
    lines.append(f"# param_lab 结果 · {time.strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append(f"- model: `{model}`")
    lines.append(f"- system: {args.system}")
    lines.append(f"- prompt: {args.prompt}")
    lines.append(f"- max_tokens: {args.max_tokens}")
    lines.append("")
    lines.append("| temp | run | total_tokens | 耗时s | 回复 |")
    lines.append("|---|---|---|---|---|")

    total_requests = 0
    total_tokens = 0
    for temp in args.temps:
        for run in range(1, args.runs + 1):
            try:
                text, tokens, elapsed = run_one(
                    client, model, args.system, args.prompt, temp, args.max_tokens
                )
            except Exception as exc:
                detail = f"{type(exc).__name__}: {str(exc)[:80]}"
                lines.append(f"| {temp} | {run} | - | - | ERROR: {detail} |")
                continue
            total_requests += 1
            total_tokens += tokens
            compact = text.replace("\n", " ").replace("|", "\\|")
            lines.append(f"| {temp} | {run} | {tokens} | {elapsed:.2f} | {compact} |")

    lines.append("")
    lines.append(f"共 {total_requests} 次请求，{total_tokens} tokens。")
    lines.append("")
    lines.append("## 观察（由我填写）")
    lines.append("")
    lines.append("- temperature=0.0 时三次输出是否一致？")
    lines.append("- temperature 升高后，输出出现了什么变化？")
    lines.append("- 耗时和 token 数随温度有明显变化吗？")

    out_path = Path(args.out)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"done: {total_requests} requests, {total_tokens} tokens -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
