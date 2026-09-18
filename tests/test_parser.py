"""Tests for the LLM response parser.

测试设计原则：每个测试只验证**一个行为**，名字说清楚"测什么、期望什么"。

覆盖矩阵：
1. 合法 payload     → 成功解析，字段值正确
2. 非法 JSON        → ParsingError（JSONDecodeError 分支）
3. schema 违规      → ParsingError（ValidationError 分支）
4. safe_parse 失败  → 不抛异常，返回错误信息
5. Usage 计算逻辑   → total_tokens 正确
"""

import json

import pytest

from alan_ai_sprint.models import BookShelfResponse
from alan_ai_sprint.parser import ParsingError, parse_response, safe_parse

VALID_PAYLOAD = json.dumps(
    {
        "model": "gpt-4o-mini",
        "usage": {"prompt_tokens": 120, "completion_tokens": 80},
        "books": [
            {
                "title": "The Three-Body Problem",
                "author": "Liu Cixin",
                "year": 2008,
                "tags": ["science-fiction"],
                "stars": 4,
                "rating": 4.6,
            },
            {
                "title": "Meditations",
                "author": "Marcus Aurelius",
                "year": 180,
                "tags": [],
                "stars": 3,
                "rating": None,
            },
        ],
    }
)


def test_parse_valid_payload_returns_typed_response() -> None:
    response = parse_response(VALID_PAYLOAD)

    assert response.model == "gpt-4o-mini"
    assert response.usage.prompt_tokens == 120
    assert len(response.books) == 2
    assert response.books[0].title == "The Three-Body Problem"
    assert response.books[0].tags == ["science-fiction"]
    assert response.books[0].stars == 4
    assert response.books[1].rating is None  # null 在 JSON 里 → None


def test_parse_rejects_invalid_json() -> None:
    broken = '{"model": "gpt-4o", "usage": '  # 故意截断的 JSON

    with pytest.raises(ParsingError, match="not valid JSON"):
        parse_response(broken)


def test_parse_rejects_negative_year() -> None:
    bad_schema = json.dumps(
        {
            "model": "gpt-4o-mini",
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            "books": [{"title": "X", "author": "Y", "year": -5}],
        }
    )

    with pytest.raises(ParsingError, match="schema validation"):
        parse_response(bad_schema)


def test_parse_rejects_missing_required_title() -> None:
    missing_title = json.dumps(
        {
            "model": "gpt-4o-mini",
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            "books": [{"author": "Y", "year": 2020}],
        }
    )

    with pytest.raises(ParsingError, match="schema validation"):
        parse_response(missing_title)


def test_parse_rejects_missing_required_field() -> None:
    missing_usage = json.dumps(
        {
            "model": "gpt-4o-mini",
            "books": [],
        }
    )

    with pytest.raises(ParsingError, match="schema validation"):
        parse_response(missing_usage)


def test_parse_rejects_rating_with_too_many_decimals() -> None:
    dirty_rating = json.dumps(
        {
            "model": "gpt-4o-mini",
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            "books": [{"title": "X", "author": "Y", "year": 2020, "rating": 4.555}],
        }
    )

    with pytest.raises(ParsingError, match="1 decimal place"):
        parse_response(dirty_rating)
        # parse_response(VALID_PAYLOAD)


def test_parse_rejects_unconvertible_type() -> None:
    bad_type = json.dumps(
        {
            "model": "gpt-4o-mini",
            "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            "books": [{"title": "X", "author": "Y", "year": "abc"}],  # 字符串转不成 int
        }
    )

    with pytest.raises(ParsingError, match="schema validation"):
        parse_response(bad_type)


def test_safe_parse_returns_error_message_on_failure() -> None:
    response, error = safe_parse("this is not json at all")

    assert response is None
    assert error is not None
    assert "not valid JSON" in error


def test_safe_parse_returns_response_on_success() -> None:
    response, error = safe_parse(VALID_PAYLOAD)

    assert isinstance(response, BookShelfResponse)
    assert error is None


def test_usage_total_tokens_computed() -> None:
    response = parse_response(VALID_PAYLOAD)

    assert response.usage.total_tokens == 200
