"""first_llm_call.py — 你的第一次 LLM 调用（Day 8）

用法：
    uv run --env-file .env python examples/first_llm_call.py
    uv run --env-file .env python examples/first_llm_call.py --probe   # 探测 base_url 正确后缀

key / base_url / model 全部从环境变量读取，绝不写进代码。
"""

from __future__ import annotations

import os
import sys

from openai import OpenAI

CANDIDATE_SUFFIXES = ["", "/v1", "/compatible-mode/v1"]


def make_call(client: OpenAI, model: str) -> str:
    """发一次最小对话请求，返回模型回复文本。"""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个简洁的技术助手，回答不超过三句话。"},
            {"role": "user", "content": "用一句话解释什么是 API 密钥"},
        ],
    )
    usage = resp.usage
    print(f"model: {resp.model}")
    print(f"reply: {resp.choices[0].message.content}")
    print(
        f"usage: prompt={usage.prompt_tokens} tokens, "
        f"completion={usage.completion_tokens} tokens, total={usage.total_tokens} tokens"
    )
    return resp.choices[0].message.content or ""


def probe(client: OpenAI, base_url: str, model: str) -> str | None:
    """依次尝试 base_url 的候选后缀，返回第一个能跑通的。"""
    for suffix in CANDIDATE_SUFFIXES:
        candidate = base_url + suffix
        print(f"try: {candidate} ...", flush=True)
        try:
            make_call(OpenAI(api_key=client.api_key, base_url=candidate), model)
        except Exception as exc:
            print(f"    failed: {type(exc).__name__}: {str(exc)[:120]}\n", flush=True)
        else:
            print(f"\nOK -> base_url = {candidate}")
            return candidate
    return None


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv

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

    if "--probe" in args:
        found = probe(client, base_url, model)
        return 0 if found else 2

    make_call(client, model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
