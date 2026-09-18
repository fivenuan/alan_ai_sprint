"""Typed models describing an LLM book-extraction response.

这是 Day 2 的核心：用 pydantic 定义"LLM 返回的 JSON 必须长什么样"。
LLM 的输出是概率性的——同一句话它可能这次返回合法 JSON，下次漏字段、
类型跑偏。所以每条 LLM 调用链都需要一层 schema 验证，pydantic 干的就是这个。

pydantic v2 核心概念（今天的重点）：
- BaseModel   ：继承它 = 声明一个带验证的数据结构
- Field(...)  ：给字段加约束（范围、长度、默认值）
- field_validator：自定义验证逻辑（约束表达不了的时候用）
"""

from pydantic import BaseModel, Field, field_validator


class Usage(BaseModel):
    """Token 用量统计——每次 LLM 调用都会返回这个。"""

    prompt_tokens: int = Field(ge=0)  # ge = greater than or equal
    completion_tokens: int = Field(ge=0)

    @property
    def total_tokens(self) -> int:
        """总 token 数——之后做 cost tracking 的基础。"""
        return self.prompt_tokens + self.completion_tokens


class Book(BaseModel):
    """一本书的抽取结果。

    注意 rating 的类型：``float | None``——Python 3.10+ 的联合类型写法，
    表示"可以是 float，也可以缺失（None）"。JSON 里对应 null 或字段缺失。
    """

    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    year: int = Field(ge=0, le=2100)  # 出版年份：0（如古代作品）到 2100
    tags: list[str] = Field(default_factory=list)  # 可选字段，默认空列表
    stars: int = Field(ge=0, le=5)
    rating: float | None = Field(default=None, ge=0, le=5)

    @field_validator("rating")
    @classmethod
    def rating_precision(cls, value: float | None) -> float | None:
        """自定义验证：rating 最多一位小数（避免 4.55555 这种脏数据）。"""
        if value is not None and round(value, 1) != value:
            msg = f"rating must have at most 1 decimal place, got {value}"
            raise ValueError(msg)
        return value


class BookShelfResponse(BaseModel):
    """整个 LLM 响应的顶层结构。"""

    model: str = Field(min_length=1)  # 哪个模型生成的，如 "gpt-4o-mini"
    usage: Usage
    books: list[Book]
