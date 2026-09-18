"""Parse raw JSON payloads from LLM APIs into typed objects.

设计要点：
1. ``parse_response`` —— 严格模式：成功返回强类型对象，失败抛 ``ParsingError``
2. ``safe_parse``     —— 宽松模式：永不抛异常，返回 ``(结果, 错误信息)`` 二元组

为什么要两种模式？
- 主流程（agent 循环里）通常要"要么成功要么立刻报错"→ 用 strict
- 批量处理（比如评测集里跑 1000 条）不想因为一条坏数据整体中断 → 用 safe

这是工程里常见的 API 设计模式：同一个能力，两种错误语义。
"""

import json

from pydantic import ValidationError

from alan_ai_sprint.models import BookShelfResponse


class ParsingError(Exception):
    """Raw payload cannot be parsed into a valid response.

    包装两类底层错误：
    - json.JSONDecodeError ：根本不是合法 JSON
    - ValidationError      ：是 JSON 但不符合 schema（字段缺失/类型错/约束违反）
    """

    def __init__(self, message: str, cause: Exception) -> None:
        super().__init__(message)
        self.cause = cause  # 保留原始异常，方便 debug 时看完整链路


def parse_response(raw: str) -> BookShelfResponse:
    """Parse a raw JSON string into a typed response. Raises ParsingError on failure.

    两步解析（重要的工程决策）：
    第 1 步用标准库 json.loads 检查**语法层**——JSON 本身坏没坏
    第 2 步用 pydantic 检查**schema 层**——JSON 合法但内容是否符合我们的结构

    为什么不直接一步 model_validate_json？
    因为 pydantic v2 内部用自己的 JSON 解析器，语法错误也会包装成
    ValidationError——两类错误混在一起，你就分不清"API 传输坏了"还是
    "模型输出跑偏了"。对 LLM 应用，这个区分直接影响 debug 方向。
    代价是 JSON 被解析两次——正确性优先，性能问题等真出现了再优化。
    """
    try:
        json.loads(raw)
    except json.JSONDecodeError as exc:
        msg = "payload is not valid JSON"
        raise ParsingError(msg, exc) from exc

    try:
        return BookShelfResponse.model_validate_json(raw)
    except ValidationError as exc:
        msg = f"payload failed schema validation: {exc}"
        raise ParsingError(msg, exc) from exc


def safe_parse(raw: str) -> tuple[BookShelfResponse | None, str | None]:
    """Parse without raising. Returns (response, None) on success, (None, error) on failure."""
    try:
        return parse_response(raw), None
    except ParsingError as exc:
        return None, str(exc)
